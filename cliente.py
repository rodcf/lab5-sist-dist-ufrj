import grpc
import server_pb2
import server_pb2_grpc
import node_pb2
import node_pb2_grpc

IP = 'localhost'
SERVER_PORT = 5000

NUMBER_OF_NODES = 16

node_list = {}

def initialize():
    _node_list = {}

    channel = grpc.insecure_channel(f'{IP}:{SERVER_PORT}')
    stub = server_pb2_grpc.ServerStub(channel)

    response = stub.getNodeList(server_pb2.Request())

    for node in response.nodeList:
        _node_list[node.seq_num] = (node.ip, node.port)

    return _node_list

def handleInsert():

    seq_num = input(f'A partir de qual nó deseja inserir? Digite um número de 1 a {NUMBER_OF_NODES}:\nR: ')

    try:
        seq_num = int(seq_num)
    except ValueError:
        print(f'ERRO: O valor deve ser um número inteiro entre 1 e {NUMBER_OF_NODES}')
        return

    if seq_num not in range(1, NUMBER_OF_NODES + 1):
        print(f'ERRO: Nó {seq_num} não existe!')
        return

    key = input('Qual será a chave?\nR: ')

    value = input('Qual será o valor a ser inserido nessa chave?\nR: ')

    address = node_list[seq_num]

    channel = grpc.insecure_channel(f'{address[0]}:{address[1]}')
    stub = node_pb2_grpc.NodeStub(channel)

    insert_request = node_pb2.InsertRequest(seq_num=seq_num, key=key, value=value)

    insert_response = stub.insert(insert_request)

    print(insert_response)

    print('inserted in:', node_list[insert_response.seq_num_node_stored])

def handleSearch():

    seq_num = input(f'A partir de qual nó deseja buscar? Digite um número de 1 a {NUMBER_OF_NODES}:\nR: ')

    try:
        seq_num = int(seq_num)
    except ValueError:
        print(f'ERRO: O valor deve ser um número inteiro entre 1 e {NUMBER_OF_NODES}')
        return

    if seq_num not in range(1, NUMBER_OF_NODES + 1):
        print(f'ERRO: Nó {seq_num} não existe!')
        return

    key = input('Qual a chave que deseja buscar?\nR: ')

    address = node_list[seq_num]

    channel = grpc.insecure_channel(f'{address[0]}:{address[1]}')
    stub = node_pb2_grpc.NodeStub(channel)

    search_request = node_pb2.SearchRequest(seq_num=seq_num, key=key)

    search_response = stub.search(search_request)

    if not search_response.success:
        print(f'Valor para a chave "{key}" não encontrado nos nós.')

    else:
        print(f'Valor para a chave "{key}" encontrada no nó {search_response.seq_num_node_stored}: "{search_response.value}".')

def main():

    print('Iniciando cliente...')

    global node_list

    node_list = initialize()

    print('Lista de nós com seus respectivos endereços:', node_list)

    while True:

        option = input(
            'O que deseja fazer? Digite um número de 1 a 3:\n1 - Inserir par chave/valor\n2 - Buscar por chave\n3 - Encerrar aplicação\nR: ')

        if option == '1':
            handleInsert()

        elif option == '2':
            handleSearch()

        elif option == '3':
            print('Encerrando cliente...')
            break

        else:
            print('Opção inválida! Escolha uma opção de 1 a 3.')
            continue


if __name__ == '__main__':
    main()
