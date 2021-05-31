import grpc
import server_pb2
import server_pb2_grpc
import node_pb2
import node_pb2_grpc

# localização do servidor
IP = 'localhost'
SERVER_PORT = 5000

# número de nós no anel
NUMBER_OF_NODES = 16

# dicionário contendo os ids sequenciais e o endereço de cada nó do anel
node_list = {}

# inicializa a conexão com o servidor via RPC
# e recupera, do servidor, o dicionário contendo os ids sequenciais e o endereço de cada nó do anel
def initialize():
    _node_list = {}

    channel = grpc.insecure_channel(f'{IP}:{SERVER_PORT}')
    stub = server_pb2_grpc.ServerStub(channel)

    response = stub.getNodeList(server_pb2.Request())

    for node in response.nodeList:
        _node_list[node.seq_num] = (node.ip, node.port)

    return _node_list

# trata os inputs do usuário relacionados à inserção de pares chave/valor e
# faz chamada ao servidor para inserir os pares passados pelo usuário em um dos nós do anel
def handleInsert():

    while True:
        seq_num = input(f'A partir de qual nó deseja inserir? Digite um número de 1 a {NUMBER_OF_NODES}:\nR: ')

        try:
            seq_num = int(seq_num)
        except ValueError:
            print(f'ERRO: O valor deve ser um número inteiro entre 1 e {NUMBER_OF_NODES}')
            continue

        if seq_num not in range(1, NUMBER_OF_NODES + 1):
            print(f'ERRO: Nó {seq_num} não existe!')
            continue

        break

    while True:
        key = input('Qual será a chave?\nR: ')

        if not key:
            print(f'ERRO: A chave não pode ser vazia!')
            continue

        break

    while True:
        value = input('Qual será o valor a ser inserido nessa chave?\nR: ')

        if not value:
            print(f'ERRO: O valor não pode ser vazio!')
            continue

        break

    address = node_list[seq_num]

    channel = grpc.insecure_channel(f'{address[0]}:{address[1]}')
    stub = node_pb2_grpc.NodeStub(channel)

    insert_request = node_pb2.InsertRequest(seq_num=seq_num, key=key, value=value)

    insert_response = stub.insert(insert_request)

    print(f'Valor armazenado para a chave "{key}" no nó {insert_response.seq_num_node_stored}: "{value}".')

# trata os inputs do usuário relacionados à busca de um valor associado à uma determinada chave e
# faz chamada ao servidor para buscar o valor da chave passada pelo usuário em um dos nós do anel
def handleSearch():

    while True:
        seq_num = input(f'A partir de qual nó deseja buscar? Digite um número de 1 a {NUMBER_OF_NODES}:\nR: ')

        try:
            seq_num = int(seq_num)
        except ValueError:
            print(f'ERRO: O valor deve ser um número inteiro entre 1 e {NUMBER_OF_NODES}')
            continue

        if seq_num not in range(1, NUMBER_OF_NODES + 1):
            print(f'ERRO: Nó {seq_num} não existe!')
            continue

        break

    while True:
        key = input('Qual a chave que deseja buscar?\nR: ')

        if not key:
            print(f'ERRO: A chave não pode ser vazia!')
            continue

        break

    address = node_list[seq_num]

    channel = grpc.insecure_channel(f'{address[0]}:{address[1]}')
    stub = node_pb2_grpc.NodeStub(channel)

    search_request = node_pb2.SearchRequest(seq_num=seq_num, key=key)

    search_response = stub.search(search_request)

    if not search_response.value:
        print(f'Valor para a chave "{key}" não encontrado nos nós.')

    else:
        print(f'Valor para a chave "{key}" encontrada no nó {search_response.seq_num_node_stored}: "{search_response.value}".')

# loop principal do programa
def main():

    print('Iniciando cliente...')

    # variável global
    global node_list

    # inicializa o serviço RPC cliente e recebe o valor do dicionário global de endereços dos nós
    node_list = initialize()

    # loop para tratamento de inputs do usuário
    while True:

        option = input(
            'O que deseja fazer? Digite um número de 1 a 4:\n1 - Inserir par chave/valor\n2 - Buscar por chave\n'
            '3 - Listar endereços dos nós\n4 - Encerrar aplicação\nR: ')

        if option == '1':
            handleInsert()

        elif option == '2':
            handleSearch()

        elif option == '3':
            print('Lista de nós com seus respectivos endereços:', node_list)

        elif option == '4':
            print('Encerrando cliente...')
            break

        else:
            print('Opção inválida! Escolha uma opção de 1 a 3.')
            continue


if __name__ == '__main__':
    main()
