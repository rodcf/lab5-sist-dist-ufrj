import grpc
import server_pb2
import server_pb2_grpc
import node_pb2
import node_pb2_grpc
import hashlib
import multiprocessing
from concurrent import futures
from collections import OrderedDict

# número de nós no anel
NUMBER_OF_NODES = 16

# número de bits nos ids
ID_BIT_LENGTH = 160

# localizacao do servidor
IP = 'localhost'
SERVER_PORT = 5000

# porta do primeiro nó no anel
INITIAL_NODE_PORT = 5001

# número de threads a serem usadas em cada processo
THREAD_CONCURRENCY = multiprocessing.cpu_count()

# dicionário de id sequencial para endereço de cada nó
seq_num_to_node_address = {}

# dicionário de endereço para id sequencial de cada nó
address_to_seq_num = {}

# dicionário de endereço para a tabela de apontamentos de cada nó
address_to_finger_table = {}

# dicionário para armazenar os pares chave/valor de cada nó
key_value = {}

# gera uma hash (SHA1) a partir de uma chave
def hashing(key):

    hash = hashlib.sha1(key.encode()).hexdigest()
    node_id = int(hash, 16)

    return node_id

# cria as tabelas de apontamentos para todos os nós do anel
def createFingerTables(node_id_list, id_to_node_address):

    _address_to_finger_table = {}

    for node_id in node_id_list:

        finger_table = OrderedDict()

        for i in range(ID_BIT_LENGTH):
            _value = (node_id + (2 ** i)) % (2 ** ID_BIT_LENGTH)
            candidate_nodes_ids = [j for j in node_id_list if j > _value]
            if not candidate_nodes_ids:
                successor_id = min(node_id_list)
            else:
                successor_id = min(candidate_nodes_ids)
            finger_table[_value] = id_to_node_address[successor_id]

        node_address = id_to_node_address[node_id]
        _address_to_finger_table[node_address] = finger_table

    return _address_to_finger_table

# inicializa os nós e atribui uma porta para cada um (portas sequenciais)
def initialize():

    port_list = [INITIAL_NODE_PORT + i for i in range(NUMBER_OF_NODES)]
    node_id_list = []
    id_to_node_address = {}
    _seq_num_to_node_address = {}

    for i in range(NUMBER_OF_NODES):
        address_string = f'{IP}:{port_list[i]}'
        node_id = hashing(address_string)
        node_id_list.append(node_id)
        id_to_node_address[node_id] = (IP, port_list[i])

    node_id_list.sort()

    _seq_num_to_node_address = {k + 1: id_to_node_address[v] for k, v in enumerate(node_id_list)}

    _address_to_seq_num = dict(zip(_seq_num_to_node_address.values(), _seq_num_to_node_address.keys()))

    _address_to_finger_table = createFingerTables(node_id_list, id_to_node_address)

    return _seq_num_to_node_address, _address_to_seq_num, _address_to_finger_table

# inicia o servidor (processo pai)
def runServer(bind_address):

    options = (('grpc.so_reuseport', 1),)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=THREAD_CONCURRENCY, ), options=options)

    server_pb2_grpc.add_ServerServicer_to_server(ServerServicer(), server)
    server.add_insecure_port(bind_address)
    server.start()

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        server.stop(None)

# inicia os nós (processos filhos)
def runNode(seq_num, bind_address):

    options = (('grpc.so_reuseport', 1),)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=THREAD_CONCURRENCY, ), options=options)

    node_pb2_grpc.add_NodeServicer_to_server(NodeServicer(), server)
    server.add_insecure_port(bind_address)
    server.start()

    print(f'Nó {seq_num} iniciado com endereço {bind_address}')

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        server.stop(None)

# classe do serviço RPC para o servidor (processo pai)
class ServerServicer(server_pb2_grpc.ServerServicer):

    # retorna o dicionário contendo os ids sequenciais e o endereço de cada nó do anel
    def getNodeList(self, request, context):

        node_list = server_pb2.NodeList()

        for k, v in seq_num_to_node_address.items():
            node = server_pb2.Node(seq_num=k, ip=v[0], port=v[1])
            node_list.nodeList.append(node)

        return node_list

# classe do serviço RPC para os nós (processos filhos) 
class NodeServicer(node_pb2_grpc.NodeServicer):

    # retorna o valor atribuído à chave passada na requisição
    def retrieveValue(self, request, context):

        return node_pb2.RetrieveResponse(value=key_value[request.key])

    # armazena o par chave/valor passado na requisição
    def storeValue(self, request, context):

        global key_value
        key_value[request.key] = request.value

        return node_pb2.StoreResponse()

    # busca nos nós do anel o valor atribuído à chave passada na requisição
    def search(self, request, context):

        address = seq_num_to_node_address[request.seq_num]

        finger_table = address_to_finger_table[address]

        key_id = hashing(request.key)

        nodes = list(finger_table.items())

        current_id = hashing(f'{address[0]}:{address[1]}')

        successor = nodes[0]
        successor_id = hashing(f'{successor[1][0]}:{successor[1][1]}')

        if current_id < key_id <= successor_id:
            channel = grpc.insecure_channel(f'{successor[1][0]}:{successor[1][1]}')
            stub = node_pb2_grpc.NodeStub(channel)

            retrieved_value = stub.retrieveValue(node_pb2.RetrieveRequest(key=request.key)).value

            print('retrieved_value:', retrieved_value)

            return node_pb2.SearchResponse(seq_num_node_stored=address_to_seq_num[successor[1]], value=retrieved_value)

        for node in reversed(nodes):

            node_id = hashing(f'{node[1][0]}:{node[1][1]}')
            if successor[0] <= node_id < key_id:

                channel = grpc.insecure_channel(f'{node[1][0]}:{node[1][1]}')
                stub = node_pb2_grpc.NodeStub(channel)

                search_request = node_pb2.SearchRequest(seq_num=address_to_seq_num[node[1]], key=request.key)

                return stub.search(search_request)

        max_node = nodes[-1]

        channel = grpc.insecure_channel(f'{max_node[1][0]}:{max_node[1][1]}')
        stub = node_pb2_grpc.NodeStub(channel)

        search_request = node_pb2.SearchRequest(seq_num=address_to_seq_num[max_node[1]], key=request.key)

        return stub.search(search_request)

    # insere em um dos nós do anel o par chave/valor passado na requisição
    def insert(self, request, context):

        address = seq_num_to_node_address[request.seq_num]

        finger_table = address_to_finger_table[address]

        key_id = hashing(request.key)

        nodes = list(finger_table.items())

        current_id = hashing(f'{address[0]}:{address[1]}')

        successor = nodes[0]
        successor_id = hashing(f'{successor[1][0]}:{successor[1][1]}')

        if current_id < key_id <= successor_id:
            channel = grpc.insecure_channel(f'{successor[1][0]}:{successor[1][1]}')
            stub = node_pb2_grpc.NodeStub(channel)

            value_to_store = node_pb2.StoreRequest(key=request.key, value=request.value)

            stub.storeValue(value_to_store)

            return node_pb2.InsertResponse(seq_num_node_stored=address_to_seq_num[successor[1]])

        for node in reversed(nodes):

            node_id = hashing(f'{node[1][0]}:{node[1][1]}')
            if current_id < node_id < key_id:

                channel = grpc.insecure_channel(f'{node[1][0]}:{node[1][1]}')
                stub = node_pb2_grpc.NodeStub(channel)

                insert_request = node_pb2.InsertRequest(seq_num=address_to_seq_num[node[1]], key=request.key,
                                                        value=request.value)

                return stub.insert(insert_request)

        max_node = nodes[-1]

        channel = grpc.insecure_channel(f'{max_node[1][0]}:{max_node[1][1]}')
        stub = node_pb2_grpc.NodeStub(channel)

        insert_request = node_pb2.InsertRequest(seq_num=address_to_seq_num[max_node[1]], key=request.key,
                                                value=request.value)

        return stub.insert(insert_request)

def main():

    # variáveis globais
    global seq_num_to_node_address
    global address_to_seq_num
    global address_to_finger_table

    # lista para armazenar os processos filhos
    processes = []

    # inicializa os nós e cria os dicionários globais
    seq_num_to_node_address, address_to_seq_num, address_to_finger_table = initialize()

    # inicia os processos filhos, que rodarão o serviço RPC dos nós
    for node in seq_num_to_node_address.items():
        seq_num = node[0]
        bind_address = f'{node[1][0]}:{node[1][1]}'

        process = multiprocessing.Process(target=runNode, args=(seq_num, bind_address))

        process.start()
        processes.append(process)

    # inicia o serviço RPC do servidor, para atender as requisições do cliente
    runServer(f'{IP}:{SERVER_PORT}')

    # aguarda todos os processos filhos finalizarem
    for process in processes:
        process.join()


if __name__ == '__main__':
    main()
