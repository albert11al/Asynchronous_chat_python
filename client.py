# Программа клиента

import socket
import time
import json
import sys
import logging
import argparse
from errors import ReqFieldMissingError, IncorrectDataRecivedError, NonDictInputError, ServerError
from decos import log
import threading

LOGGER = logging.getLogger('client')

#s = socket(AF_INET,SOCK_STREAM)     # Создать сокет TCP
#s.connect(('localhost', 10000))     # Соединиться с сервером

# cli_log = logging.getLogger('client')

@log
def create_exit_message(account_name):
    """Функция создаёт словарь с сообщением о выходе"""
    return {
        'action': 'exit',
        'time': time.time(),
        'account_name': account_name
    }

@log
def message_from_server(sock, my_username):
    
    while True:
        try:
            message = get_response(sock)
            if 'action' in message and message['action'] == 'message' and \
                    'from' in message and 'to' in message \
                    and 'mess_text' in message and message['to'] == my_username:
                print(f'\nПолучено сообщение от пользователя {message["from"]}:'
                      f'\n{message["mess_text"]}')
                LOGGER.info(f'Получено сообщение от пользователя {message["from"]}:'
                            f'\n{message["mess_text"]}')
            else:
                LOGGER.error(f'Получено некорректное сообщение с сервера: {message}')
        except IncorrectDataRecivedError:
            LOGGER.error(f'Не удалось декодировать полученное сообщение.')
        except (OSError, ConnectionError, ConnectionAbortedError,
                ConnectionResetError, json.JSONDecodeError):
            LOGGER.critical(f'Потеряно соединение с сервером.')
            break

@log
def create_message(sock, account_name='Guest'):

    to_user = input('Введите получателя сообщения: ')
    message = input('Введите сообщение для отправкиершения: ')
    message_dict = {
        'action': 'message',
        'from': account_name,
        'to': to_user,
        'time': time.time(),
        'mess_text': message
    }
    LOGGER.debug(f'Сформирован словарь сообщения: {message_dict}')
    try:
        send_message(sock, message_dict)
        LOGGER.info(f'Отправлено сообщение для пользователя {to_user}')
    except:
        LOGGER.critical('Потеряно соединение с сервером.')
        sys.exit(1)

@log
def user_interactive(sock, username):
    """Функция взаимодействия с пользователем, запрашивает команды, отправляет сообщения"""
    print_help()
    while True:
        command = input('Введите команду: ')
        if command == 'message':
            create_message(sock, username)
        elif command == 'help':
            print_help()
        elif command == 'exit':
            send_message(sock, create_exit_message(username))
            print('Завершение соединения.')
            LOGGER.info('Завершение работы по команде пользователя.')
            # Задержка неоходима, чтобы успело уйти сообщение о выходе
            time.sleep(0.5)
            break
        else:
            print('Команда не распознана, попробойте снова. help - вывести поддерживаемые команды.')


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

def print_help():
    """Функция выводящяя справку по использованию"""
    print('Поддерживаемые команды:')
    print('message - отправить сообщение. Кому и текст будет запрошены отдельно.')
    print('help - вывести подсказки по командам')
    print('exit - выход из программы')

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
        else:
            raise IncorrectDataRecivedError
    else:
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
    parser.add_argument('-n', '--name', default='None', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_name = namespace.name

    # проверим подходящий номер порта
    if not 1023 < server_port < 65536:
        LOGGER.critical(
            f'Попытка запуска клиента с неподходящим номером порта: {server_port}. '
            f'Допустимы адреса с 1024 до 65535. Клиент завершается.')
        sys.exit(1)

    return server_address, server_port, client_name

# получить и обработать параметры командной строки

def main():

    print('Консольный месседжер. Клиентский модуль.')

    # Загружаем параметы коммандной строки
    server_address, server_port, client_name = create_arg_parser()

    # Если имя пользователя не было задано, необходимо запросить пользователя.
    if not client_name:
        client_name = input('Введите имя пользователя: ')

    LOGGER.info(
        f'Запущен клиент с парамертами: адрес сервера: {server_address}, '
        f'порт: {server_port}, имя пользователя: {client_name}')

    # Инициализация сокета и сообщение серверу о нашем появлении
    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((server_address, server_port))
        send_message(transport, presence(client_name))
        answer = parse_message(get_response(transport))
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
    except (ConnectionRefusedError, ConnectionError):
        LOGGER.critical(f'Не удалось подключиться к серверу {server_address}:{server_port}, '
                        f'конечный компьютер отверг запрос на подключение.')
        sys.exit(1)
    else:

        receiver = threading.Thread(target=message_from_server, args=(transport, client_name))
        receiver.daemon = True
        receiver.start()

        user_interface = threading.Thread(target=user_interactive, args=(transport, client_name))
        user_interface.daemon = True
        user_interface.start()
        LOGGER.debug('Запущены процессы')

        while True:
            time.sleep(1)
            if receiver.is_alive() and user_interface.is_alive():
                continue
            break


if __name__ == '__main__':
    main()