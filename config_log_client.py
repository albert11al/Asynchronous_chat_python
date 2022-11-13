import logging
import logging.handlers
import sys
import os

# Создание именованного логгера;
LOG = logging.getLogger('app.client')

# Сообщения лога, формат: "<дата-время> <уровень_важности> <имя_модуля> <сообщение>";
client_format = logging.Formatter("%(asctime)s %(levelname)-10s %(module)s: %(message)s")

# Подготовка имени файла для логирования
curr_dir = os.path.dirname(os.path.abspath(__file__))
logging_file = os.path.join(curr_dir, 'client.log')

# создаём потоки вывода логов
crit_hand = logging.StreamHandler(sys.stderr)
crit_hand.setLevel(logging.DEBUG)
crit_hand.setFormatter(client_format)
logging_handler = logging.FileHandler(logging_file, encoding='utf-8')
logging_handler.setFormatter(client_format)

# Добавить несколько обработчиков в регистратор 'app.client'
LOG.addHandler(crit_hand)
LOG.addHandler(logging_handler)
LOG.setLevel(logging.DEBUG)

# отладка
if __name__ == '__main__':
    LOG.critical('Критическая ошибка')
    LOG.error('Ошибка')
    LOG.debug('Отладочная информация')
    LOG.info('Информационное сообщение')