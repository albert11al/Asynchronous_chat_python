# Программа сервера

import socket
import json
import sys
import log.config_log_server
from client import send_message, get_response
import logging
import argparse
from errors import IncorrectDataRecivedError
from decos import log

# Инициализация логирования сервера.
LOGGER = logging.getLogger('server')

@log
def process_client_message(message):
    
    LOGGER.debug(f'Разбор сообщения от клиента : {message}')

    if 'action' in message and message['action'] == 'presence' and \
        'time' in message and \
        'user' in message and message['user']['account_name'] == 'Guest':
        return {'response': 200}
    return {
        'response': 400,
        'error': 'Bad Request'
    }

@log
def create_arg_parser():
    """
    Парсер аргументов коммандной строки
    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=7777, type=int, nargs='?')
    parser.add_argument('-a', default='', nargs='?')
    return parser

# параметры командной строки:
def main():

    parser = create_arg_parser()
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p

    if not 1023 < listen_port < 65536:
        LOGGER.critical(f'Попытка запуска сервера с указанием неподходящего порта '
                               f'{listen_port}. Допустимы адреса с 1024 до 65535.')
        sys.exit(1)
    LOGGER.info(f'Запущен сервер, порт для подключений: {listen_port}, '
                       f'адрес с которого принимаются подключения: {listen_address}. '
                       f'Если адрес не указан, принимаются соединения с любых адресов.')

    # Готовим сокет

    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.bind((listen_address, listen_port))

    # Слушаем порт

    transport.listen(5)

    while True:
        client, client_address = transport.accept()
        LOGGER.info(f'Установлено соедение с ПК {client_address}')
        try:
            message_from_cient = get_response(client)
            LOGGER.debug(f'Получено сообщение {message_from_cient}')
            print(message_from_cient)
            response = process_client_message(message_from_cient)
            LOGGER.info(f'Cформирован ответ клиенту {response}')

            send_message(client, response)
            LOGGER.debug(f'Соединение с клиентом {client_address} закрывается.')

            client.close()
        except json.JSONDecodeError:
            LOGGER.error(f'Не удалось декодировать JSON строку, полученную от '
                                f'клиента {client_address}. Соединение закрывается.')
            client.close()
        except IncorrectDataRecivedError:
            LOGGER.error(f'От клиента {client_address} приняты некорректные данные. '
                                f'Соединение закрывается.')
            client.close()

if __name__ == '__main__':
    main()