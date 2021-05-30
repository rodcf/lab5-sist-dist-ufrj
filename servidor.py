import grpc
import server_pb2
import server_pb2_grpc
import node_pb2
import node_pb2_grpc
import hashlib
import multiprocessing
from concurrent import futures

NUMBER_OF_NODES = 16
ID_BIT_LENGTH = 160

IP = 'localhost'
SERVER_PORT = 5000
INITIAL_NODE_PORT = 5001

THREAD_CONCURRENCY = multiprocessing.cpu_count()

seq_num_to_node_address = {}
address_to_seq_num = {}
address_to_finger_table = {}

value = None

def hashing(key):

    hash = hashlib.sha1(key.encode()).hexdigest()
    node_id = int(hash, 16)

    return node_id

def createFingerTables(node_id_list, id_to_node_address):

    _address_to_finger_table = {}

    for node_id in node_id_list:

        finger_table = {}

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

def initialize():

    port_list = [INITIAL_NODE_PORT + i for i in range(NUMBER_OF_NODES)]
    node_id_list = []
    id_to_node_address = {}
    _node_id_to_seq_num = {}
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

class ServerServicer(server_pb2_grpc.ServerServicer):

    def getNodeList(self, request, context):
        node_list = server_pb2.NodeList()

        for k, v in seq_num_to_node_address.items():
            node = server_pb2.Node(seq_num=k, ip=v[0], port=v[1])
            node_list.nodeList.append(node)

        return node_list

class NodeServicer(node_pb2_grpc.NodeServicer):

    def retrieveValue(self, request, context):

        return node_pb2.Value(value=value)

    def storeValue(self, request, context):

        global value
        value = request.value

        return node_pb2.StoreResponse()

    def search(self, request, context):

        if request.seq_num not in seq_num_to_node_address.keys():
            return node_pb2.SearchResponse(success=False)

        address = seq_num_to_node_address[request.seq_num]

        finger_table = address_to_finger_table[address]

        key_id = hashing(request.key)

        nodes = sorted(list(finger_table.items()), key=lambda x: x[0])

        successor = nodes[0]
        sucessor_id = hashing(f'{successor[1][0]}:{successor[1][1]}')

        if successor[0] <= key_id <= sucessor_id:
            channel = grpc.insecure_channel(f'{successor[1][0]}:{successor[1][1]}')
            stub = node_pb2_grpc.NodeStub(channel)

            retrieved_value = stub.retrieveValue(node_pb2.Value()).value

            print('retrieved_value:', retrieved_value)

            if not retrieved_value:
                return node_pb2.SearchResponse(success=False)

            return node_pb2.SearchResponse(success=True, seq_num_node_stored=address_to_seq_num[successor[1]],
                                           value=retrieved_value)

        # predecessors
        # candidates = [node for node in list(nodes) if node[0] < node_id]

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

        # print('retrieved_value:', value)
        #
        # if not value:
        #     return node_pb2.SearchResponse(success=False)
        #
        # return node_pb2.SearchResponse(success=True, seq_num_node_stored=request.seq_num, value=value)

    def insert(self, request, context):

        if request.seq_num not in seq_num_to_node_address.keys():
            return node_pb2.InsertResponse(success=False)

        address = seq_num_to_node_address[request.seq_num]

        finger_table = address_to_finger_table[address]

        key_id = hashing(request.key)

        nodes = sorted(list(finger_table.items()), key=lambda x: x[0])

        successor = nodes[0]
        successor_id = hashing(f'{successor[1][0]}:{successor[1][1]}')

        if successor[0] <= key_id <= successor_id:
            channel = grpc.insecure_channel(f'{successor[1][0]}:{successor[1][1]}')
            stub = node_pb2_grpc.NodeStub(channel)

            value_to_store = node_pb2.Value(value=request.value)

            stub.storeValue(value_to_store)

            return node_pb2.InsertResponse(success=True, seq_num_node_stored=address_to_seq_num[successor[1]])

        # predecessors
        # candidates = [node for node in list(nodes) if node[0] < node_id]

        for node in reversed(nodes):

            node_id = hashing(f'{node[1][0]}:{node[1][1]}')
            if successor[0] <= node_id < key_id:

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

        # global value
        # value = request.value
        # return node_pb2.InsertResponse(success=True, seq_num_node_stored=request.seq_num)

def main():
    global seq_num_to_node_address
    global address_to_seq_num
    global address_to_finger_table

    processes = []

    seq_num_to_node_address, address_to_seq_num, address_to_finger_table = initialize()

    for node in seq_num_to_node_address.items():
        seq_num = node[0]
        bind_address = f'{node[1][0]}:{node[1][1]}'

        process = multiprocessing.Process(target=runNode, args=(seq_num, bind_address))

        process.start()
        processes.append(process)

    runServer(f'{IP}:{SERVER_PORT}')

    for process in processes:
        process.join()


if __name__ == '__main__':
    main()
