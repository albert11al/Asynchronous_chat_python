# Программа клиента

import socket
import time
import json
import sys
import logging
import argparse
from errors import ReqFieldMissingError, IncorrectDataRecivedError, NonDictInputError
from decos import log

LOGGER = logging.getLogger('client')

#s = socket(AF_INET,SOCK_STREAM)     # Создать сокет TCP
#s.connect(('localhost', 10000))     # Соединиться с сервером

# cli_log = logging.getLogger('client')
@log
def presence(account_name='Guest'):  # сформировать presence-сообщение;
    LOGGER.debug(f'Сформировано {"presence"} сообщение для пользователя {account_name}')
    return {
        "action": "presence",
        "time": time.time(),
        "user": {
            "account_name": account_name
        }
    }

@log
def send_message(sock, message):  # отправить сообщение серверу
    if not isinstance(message, dict):
        raise NonDictInputError
    js_msg = json.dumps(message)
    sock.send(js_msg.encode('utf-8'))

@log
def get_response(client):  # получить ответ сервера;
    encoded_response = client.recv(1024)
    if isinstance(encoded_response, bytes):
        json_response = encoded_response.decode('utf-8')
        response = json.loads(json_response)
        if isinstance(response, dict):
            return response
        raise IncorrectDataRecivedError
    raise IncorrectDataRecivedError

@log
def parse_message(message):  # разобрать сообщение сервера;
    #serv_message = {}
    #serv_message = json.loads(str1.decode('utf-8'))
    # if serv_message["response"] in (100, 101, 102, 200, 201, 202):
    LOGGER.debug(f'Разбор сообщения от сервера: {message}')
    if 'response' in message:
        if message['response'] == 200:
            return '200 : OK'
        return f'400 : {message["error"]}'
    raise ReqFieldMissingError('response')

@log
def create_arg_parser():
    """Создаём парсер аргументов коммандной строки"""
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default='127.0.0.1', nargs='?')
    parser.add_argument('port', default=7777, type=int, nargs='?')
    return parser

# получить и обработать параметры командной строки

def main():
    """Загружаем параметы коммандной строки"""
    parser = create_arg_parser()
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port

    # проверим подходящий номер порта
    if not 1023 < server_port < 65536:
        LOGGER.critical(
            f'Попытка запуска клиента с неподходящим номером порта: {server_port}. '
            f'Допустимы адреса с 1024 до 65535. Клиент завершается.')
        sys.exit(1)

    LOGGER.info(f'Запущен клиент с парамертами: адрес сервера: '
                f'{server_address}, порт: {server_port}')

    # Инициализация сокета и обмен
  
    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((server_address, server_port))
        message_to_server = presence()
        send_message(transport, message_to_server)
        answer =  parse_message(get_response(transport))
        LOGGER.info(f'Принят ответ от сервера {answer}')
    except json.JSONDecodeError:
        LOGGER.error('Не удалось декодировать полученную Json строку.')
    except ReqFieldMissingError as missing_error:
        LOGGER.error(f'В ответе сервера отсутствует необходимое поле {missing_error.missing_field}')
    except ConnectionRefusedError:
        LOGGER.critical(f'Не удалось подключиться к серверу {server_address}:{server_port}, '
                        f'конечный компьютер отверг запрос на подключение.')


if __name__ == '__main__':
    main()