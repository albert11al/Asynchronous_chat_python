# Программа сервера

import socket
import sys
import log.config_log_server
from client import send_message, get_response
import logging
import argparse
from decos import log
import select

# Инициализация логирования сервера.
LOGGER = logging.getLogger('server')

@log
def process_client_message(message, messages_list, client, clients, names):
    
    LOGGER.debug(f'Разбор сообщения от клиента : {message}')

    if 'action' in message and message['action'] == 'presence' and \
        'time' in message and 'user' in message:
        if message['user']['account_name'] not in names.keys():
            names[message['user']['account_name']] = client
            send_message(client, {'response': 200})
   
        else:
            response = {'response': 400, 'error': None}
            response['error'] = 'Имя пользователя уже занято.'
            send_message(client, response)
            clients.remove(client)
            client.close()
        return
    elif 'action' in message and message['action'] == 'message' and \
            'to' in message and 'time' in message and 'from' in message and \
            'mess_text' in message:
        messages_list.append(message)
        return
    elif 'action' in message and message['action'] == 'exit' and 'account_name' in message:
        clients.remove(names[message['account_name']])
        names[message['account_name']].close()
        del names[message['account_name']]
        return
    # Иначе отдаём Bad request
    else:
        response = {'response': 400, 'error': None}
        response['error'] = 'Запрос некорректен.'
        send_message(client, response)
        return

@log
def process_message(message, names, listen_socks):

    if message['to'] in names and names[message['to']] in listen_socks:
        send_message(names[message['to']], message)
        LOGGER.info(f'Отправлено сообщение пользователю {message["to"]} '
                    f'от пользователя {message["from"]}.')
    elif message['to'] in names and names[message['to']] not in listen_socks:
        raise ConnectionError
    else:
        LOGGER.error(
            f'Пользователь {message["to"]} не зарегистрирован на сервере, '
            f'отправка сообщения невозможна.')

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

    names = dict()
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
                                           messages, client_with_message, clients, names)
                except Exception:
                    LOGGER.info(f'Клиент {client_with_message.getpeername()} '
                                f'отключился от сервера.')
                    clients.remove(client_with_message)

        # Если есть сообщения для отправки и ожидающие клиенты, отправляем им сообщение.
        for i in messages:
            try:
                process_message(i, names, send_data_lst)
            except Exception:
                LOGGER.info(f'Связь с клиентом с именем {i["to"]} была потеряна')
                clients.remove(names[i['to']])
                del names[i['to']]
        messages.clear()

if __name__ == '__main__':
    main()