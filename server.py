# Программа сервера

import socket
import sys
import select
from client import send_message, get_response
import logging
import argparse
from decos import log
from metaclasses import ServerMaker
import threading
from server_database import ServerStorage

# Инициализация логирования сервера.
LOGGER = logging.getLogger('server')
class Port:
    def __set__(self, instance, value):

        if not 1023 < value < 65536:
            LOGGER.critical(
                f'Попытка запуска сервера с указанием неподходящего порта {value}. Допустимы адреса с 1024 до 65535.')
            exit(1)
        # Если порт прошел проверку, добавляем его в список атрибутов экземпляра
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name

@log
def create_arg_parser():
    """
    Парсер аргументов коммандной строки
    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=7777, type=int, nargs='?') #70000 (7777)
    parser.add_argument('-a', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p
    return listen_address, listen_port

# Основной класс сервера
class Server(threading.Thread, metaclass=ServerMaker):
    port = Port()

    def __init__(self, listen_address, listen_port, database):
        # Параментры подключения
        super().__init__()
        self.addr = listen_address
        self.port = listen_port

        # База данных сервера
        self.database = database

        # Список подключённых клиентов.
        self.clients = []

        # Список сообщений на отправку.
        self.messages = []

        # Словарь содержащий сопоставленные имена и соответствующие им сокеты.
        self.names = dict()

    def init_socket(self):
        LOGGER.info(f'Запущен сервер, порт для подключений: {self.port}, '
                    f'адрес с которого принимаются подключения: {self.addr}. '
                    f'Если адрес не указан, принимаются соединения с любых адресов.')

    # Готовим сокет

        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.bind((self.addr, self.port))
        transport.settimeout(0.5)

        self.sock = transport
        self.sock.listen()

    def main_loop(self):
        # Инициализация Сокета
        self.init_socket()

        while True:
                
            try:
                client, client_address = self.sock.accept()
            except OSError:
                pass
            else:
                LOGGER.info(f'Установлено соедение с ПК {client_address}')
                self.clients.append(client)

            recv_data_lst = []
            send_data_lst = []
            err_lst = []

            try:
                if self.clients:
                    recv_data_lst, send_data_lst, err_lst = select.select(self.clients, self.clients, [], 0)
            except OSError:
                pass

            if recv_data_lst:
                for client_with_message in recv_data_lst:
                    try:
                        self.process_client_message(get_response(client_with_message), client_with_message)
                    except:
                        LOGGER.info(f'Клиент {client_with_message.getpeername()} отключился от сервера.')
                        self.clients.remove(client_with_message)

        # Если есть сообщения для отправки и ожидающие клиенты, отправляем им сообщение.
            for message in self.messages:
                try:
                    self.process_message(message, send_data_lst)
                except:
                    LOGGER.info(f'Связь с клиентом с именем {message["to"]} была потеряна')
                    self.clients.remove(self.names[message['to']])
                    del self.names[message['to']]
            self.messages.clear()

    def process_message(self, message, listen_socks):
        if message['to'] in self.names and self.names[message['to']] in listen_socks:
            send_message(self.names[message['to']], message)
            LOGGER.info(f'Отправлено сообщение пользователю {message["to"]} от пользователя {message["from"]}.')
        elif message['to'] in self.names and self.names[message['to']] not in listen_socks:
            raise ConnectionError
        else:
            LOGGER.error(
                f'Пользователь {message["to"]} не зарегистрирован на сервере, отправка сообщения невозможна.')

    def process_client_message(self, message, client):
    
        LOGGER.debug(f'Разбор сообщения от клиента : {message}')

        if 'action' in message and message['action'] == 'presence' and 'time' in message and 'user' in message:
            if message['user']['account_name'] not in self.names.keys():
                self.names[message['user']['account_name']] = client
                client_ip, client_port = client.getpeername()
                self.database.user_login(message['user']['account_name'], client_ip, client_port)
                send_message(client, {'response': 200})
            else:
                response = {'response': 400, 'error': None}
                response['error'] = 'Имя пользователя уже занято.'
                send_message(client, response)
                self.clients.remove(client)
                client.close()
            return
        elif 'action' in message and message['action'] == 'message' and 'to' in message and 'time' in message \
                and 'from' in message and 'mess_text' in message:
            self.messages.append(message)
            return
        elif 'action' in message and message['action'] == 'exit' and 'account_name' in message:
            self.database.user_logout(message['account_name'])
            self.clients.remove(self.names['account_name'])
            self.names['account_name'].close()
            del self.names['account_name']
            return
    # Иначе отдаём Bad request
        else:
            response = {'response': 400, 'error': None}
            response['error'] = 'Запрос некорректен.'
            send_message(client, response)
            return

def print_help():
    print('Поддерживаемые комманды:')
    print('users - список известных пользователей')
    print('connected - список подключенных пользователей')
    print('loghist - история входов пользователя')
    print('exit - завершение работы сервера.')
    print('help - вывод справки по поддерживаемым командам')
# параметры командной строки:
def main():

    listen_address, listen_port = create_arg_parser()

    # Инициализация базы данных
    database = ServerStorage()

    # Создание экземпляра класса - сервера и его запуск:
    server = Server(listen_address, listen_port, database)
    server.daemon = True
    server.start()

if __name__ == '__main__':
    main()