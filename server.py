# Программа сервера

import socket
import sys
import log.config_log_server
from client import send_message, get_response
import logging
import argparse
from decos import log
import select
import time

# Инициализация логирования сервера.
LOGGER = logging.getLogger('server')

@log
def process_client_message(message, messages_list, client):
    
    LOGGER.debug(f'Разбор сообщения от клиента : {message}')

    if 'action' in message and message['action'] == 'presence' and \
        'time' in message and \
        'user' in message and message['user']['account_name'] == 'Guest':
        send_message(client, {'response': 200})
        return
    elif 'action' in message and message['action'] == 'message' and \
        'time' in message and \
        'mess_text' in message:
        messages_list.append((message['account_name'], message['mess_text']))
        return
    else:
        send_message(client, {
            'response': 400,
            'error': 'Bad Request'
        })
        return

@log
def create_arg_parser():
    """
    Парсер аргументов коммандной строки
    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=7777, type=int, nargs='?')
    parser.add_argument('-a', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p

    if not 1023 < listen_port < 65536:
        LOGGER.critical(
            f'Попытка запуска сервера с указанием неподходящего порта '
            f'{listen_port}. Допустимы адреса с 1024 до 65535.')
        sys.exit(1)

    return listen_address, listen_port

# параметры командной строки:
def main():

    listen_address, listen_port = create_arg_parser()
    
    LOGGER.info(
        f'Запущен сервер, порт для подключений: {listen_port}, '
        f'адрес с которого принимаются подключения: {listen_address}. '
        f'Если адрес не указан, принимаются соединения с любых адресов.')


    # Готовим сокет

    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.bind((listen_address, listen_port))
    transport.settimeout(0.5)

    # список клиентов , очередь сообщений
    clients = []
    messages = []

    # Слушаем порт

    transport.listen(5)
    # Основной цикл программы сервера
    while True:
        
        
        try:
            client, client_address = transport.accept()
        except OSError:
            pass
        else:
            LOGGER.info(f'Установлено соедение с ПК {client_address}')
            clients.append(client)

        recv_data_lst = []
        send_data_lst = []
        err_lst = []

        try:
            if clients:
                recv_data_lst, send_data_lst, err_lst = select.select(clients, clients, [], 0)
        except OSError:
            pass

        if recv_data_lst:
            for client_with_message in recv_data_lst:
                try:
                    process_client_message(get_response(client_with_message),
                                           messages, client_with_message)
                except:
                    LOGGER.info(f'Клиент {client_with_message.getpeername()} '
                                f'отключился от сервера.')
                    clients.remove(client_with_message)

        # Если есть сообщения для отправки и ожидающие клиенты, отправляем им сообщение.
        if messages and send_data_lst:
            message = {
                'action': 'message',
                'sender': messages[0][0],
                'time': time.time(),
                'mess_text': messages[0][1]
            }
            del messages[0]
            for waiting_client in send_data_lst:
                try:
                    send_message(waiting_client, message)
                except:
                    LOGGER.info(f'Клиент {waiting_client.getpeername()} отключился от сервера.')
                    clients.remove(waiting_client)



if __name__ == '__main__':
    main()