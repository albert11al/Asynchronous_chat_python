import logging
import logging.handlers
import sys
import os

# Создание именованного логгера;
LOG = logging.getLogger('app.server')

# Сообщения лога, формат: "<дата-время> <уровень_важности> <имя_модуля> <сообщение>";
server_format = logging.Formatter("%(asctime)s %(levelname)-10s %(module)s: %(message)s")

# На стороне сервера необходимо настроить ежедневную ротацию лог-файлов.
# Подготовка имени файла для логирования
curr_dir = os.path.dirname(os.path.abspath(__file__))
logging_file = os.path.join(curr_dir, 'server.log')
# Ротация
rotation_logging_handler = logging.handlers.TimedRotatingFileHandler(logging_file, encoding='utf-8', when='D', interval=1)

rotation_logging_handler.setFormatter(server_format)

# # Создать обработчик, который выводит сообщения с уровнем
# # CRITICAL в поток stderr
crit_hand = logging.StreamHandler(sys.stderr)
crit_hand.setLevel(logging.DEBUG)
crit_hand.setFormatter(server_format)

# Добавить несколько обработчиков в регистратор 'app.server'
LOG.addHandler(rotation_logging_handler)
LOG.addHandler(crit_hand)
LOG.setLevel(logging.DEBUG)

# отладка
if __name__ == '__main__':
    LOG.critical('Критическая ошибка')
    LOG.error('Ошибка')
    LOG.debug('Отладочная информация')
    LOG.info('Информационное сообщение')
