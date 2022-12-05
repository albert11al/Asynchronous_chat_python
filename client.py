# Программа клиента

import socket
import time
import json
import sys
import logging
import argparse
from errors import ReqFieldMissingError, IncorrectDataRecivedError, NonDictInputError, ServerError
from decos import log

LOGGER = logging.getLogger('client')

#s = socket(AF_INET,SOCK_STREAM)     # Создать сокет TCP
#s.connect(('localhost', 10000))     # Соединиться с сервером

# cli_log = logging.getLogger('client')
@log
def message_from_server(message):
    
    if 'action' in message and message['action'] == 'message' and \
            'sender' in message and 'mess_text' in message:
        print(f'Получено сообщение от пользователя '
              f'{message["sender"]}:\n{message["mess_text"]}')
        LOGGER.info(f'Получено сообщение от пользователя '
                    f'{message["sender"]}:\n{message["mess_text"]}')
    else:
        LOGGER.error(f'Получено некорректное сообщение с сервера: {message}')


@log
def create_message(sock, account_name='Guest'):

    message = input('Введите сообщение для отправки или \'!!!\' для завершения работы: ')
    if message == '!!!':
        sock.close()
        LOGGER.info('Завершение работы по команде пользователя.')
        print('Спасибо за использование нашего сервиса!')
        sys.exit(0)
    message_dict = {
        'action': 'message',
        'time': time.time(),
        'account_name': account_name,
        'mess_text': message
    }
    LOGGER.debug(f'Сформирован словарь сообщения: {message_dict}')
    return message_dict

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
        elif message['response'] == 400:
            raise ServerError(f'400 : {message["error"]}')
    raise ReqFieldMissingError('response')

@log
def create_arg_parser():
    """Создаём парсер аргументов коммандной строки"""
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default='127.0.0.1', nargs='?')
    parser.add_argument('port', default=7777, type=int, nargs='?')
    parser.add_argument('-m', '--mode', default='listen', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_mode = namespace.mode

    # проверим подходящий номер порта
    if not 1023 < server_port < 65536:
        LOGGER.critical(
            f'Попытка запуска клиента с неподходящим номером порта: {server_port}. '
            f'Допустимы адреса с 1024 до 65535. Клиент завершается.')
        sys.exit(1)

    # Проверим допустим ли выбранный режим работы клиента
    if client_mode not in ('listen', 'send'):
        LOGGER.critical(f'Указан недопустимый режим работы {client_mode}, '
                        f'допустимые режимы: listen , send')
        sys.exit(1)

    return server_address, server_port, client_mode

# получить и обработать параметры командной строки

def main():
    """Загружаем параметы коммандной строки"""
    server_address, server_port, client_mode = create_arg_parser()

    LOGGER.info(f'Запущен клиент с парамертами: адрес сервера: '
                f'{server_address}, порт: {server_port}, режим работы: {client_mode}')

    # Инициализация сокета и обмен
  
    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((server_address, server_port))
        send_message(transport, presence())
        answer =  parse_message(get_response(transport))
        LOGGER.info(f'Установлено соединение с сервером. Ответ сервера: {answer}')
        print(f'Установлено соединение с сервером.')
    except json.JSONDecodeError:
        LOGGER.error('Не удалось декодировать полученную Json строку.')
        sys.exit(1)
    except ServerError as error:
        LOGGER.error(f'При установке соединения сервер вернул ошибку: {error.text}')
        sys.exit(1)
    except ReqFieldMissingError as missing_error:
        LOGGER.error(f'В ответе сервера отсутствует необходимое поле {missing_error.missing_field}')
        sys.exit(1)
    except ConnectionRefusedError:
        LOGGER.critical(f'Не удалось подключиться к серверу {server_address}:{server_port}, '
                        f'конечный компьютер отверг запрос на подключение.')
        sys.exit(1)
    else:

        if client_mode == 'send':
            print('Режим работы - отправка сообщений.')
        else:
            print('Режим работы - приём сообщений.')
        while True:
            # режим работы - отправка сообщений
            if client_mode == 'send':
                try:
                    send_message(transport, create_message(transport))
                except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                    LOGGER.error(f'Соединение с сервером {server_address} было потеряно.')
                    sys.exit(1)

            # Режим работы приём:
            if client_mode == 'listen':
                try:
                    message_from_server(get_response(transport))
                except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                    LOGGER.error(f'Соединение с сервером {server_address} было потеряно.')
                    sys.exit(1)



if __name__ == '__main__':
    main()