# Программа клиента

import socket
import time
import json
import sys

#s = socket(AF_INET,SOCK_STREAM)     # Создать сокет TCP
#s.connect(('localhost', 10000))     # Соединиться с сервером

# cli_log = logging.getLogger('client')

def presence(account_name='Guest'):  # сформировать presence-сообщение;
    return {
        "action": "presence",
        "time": time.time(),
        "user": {
            "account_name": account_name
        }
    }


def send_message(sock, message):  # отправить сообщение серверу
    js_msg = json.dumps(message)
    sock.send(js_msg.encode('utf-8'))


def get_response(client):  # получить ответ сервера;
    encoded_response = client.recv(1024)
    if isinstance(encoded_response, bytes):
        json_response = encoded_response.decode('utf-8')
        response = json.loads(json_response)
        if isinstance(response, dict):
            return response
        raise ValueError
    raise ValueError


def parse_message(message):  # разобрать сообщение сервера;
    #serv_message = {}
    #serv_message = json.loads(str1.decode('utf-8'))
    # if serv_message["response"] in (100, 101, 102, 200, 201, 202):
    if 'response' in message:
        if message['response'] == 200:
            return '200 : OK'
        return f'400 : {message["error"]}'
    raise ValueError

# получить и обработать параметры командной строки

def main():

    try:
        server_address = sys.argv[1]
        server_port = int(sys.argv[2])
        if server_port < 1024 or server_port > 65535:
            raise ValueError
    except IndexError:
        server_address = '127.0.0.1'
        server_port = 7777
    except ValueError:
        print('В качестве порта может быть указано только число в диапазоне от 1024 до 65535.')
        sys.exit(1)

    # Инициализация сокета и обмен

    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.connect((server_address, server_port))
    message_to_server = presence()
    send_message(transport, message_to_server)
    try:
        answer =  parse_message(get_response(transport))
        print(answer)
    except (ValueError, json.JSONDecodeError):
        print('Не удалось декодировать сообщение сервера.')


if __name__ == '__main__':
    main()