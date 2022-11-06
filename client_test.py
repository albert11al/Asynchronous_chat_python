import unittest
import json
from client import presence, parse_message, send_message, get_response

class TestClass(unittest.TestCase):

    def test_def_presense(self):        #Tест коректного запроса
        test = presence()
        test['time'] = 1.1  # время необходимо приравнять принудительно иначе тест никогда не будет пройден
        self.assertEqual(test, {'action': 'presence', 'time': 1.1, 'user': {'account_name': 'Guest'}})
    
    test_dict_send = {
        'action': 'presence',
        'time': 111111.111111,
        'user': {
            'account_name': 'test_test'
        }
    }
    test_dict_recv_ok = {'response': 200}
    test_dict_recv_err = {
        'response': 400,
        'error': 'Bad Request'
    }

    def test_send_message(self):        #Тестируем корректность работы фукции отправки
        """
        создадим тестовый сокет и проверим корректность отправки словаря
        """
        # экземпляр тестового словаря, хранит собственно тестовый словарь
        test_socket = TestSocket(self.test_dict_send)
        # вызов тестируемой функции, результаты будут сохранены в тестовом сокете
        send_message(test_socket, self.test_dict_send)
        # проверка корретности кодирования словаря.
        # сравниваем результат довренного кодирования и результат от тестируемой функции
        self.assertEqual(test_socket.encoded_message, test_socket.receved_message)
        # дополнительно, проверим генерацию исключения, при не словаре на входе.
        with self.assertRaises(Exception):
            send_message(test_socket, test_socket)

    def test_get_response(self):        #Тест функции приёма сообщения
        test_sock_ok = TestSocket(self.test_dict_recv_ok)
        test_sock_err = TestSocket(self.test_dict_recv_err)
        # тест корректной расшифровки корректного словаря
        self.assertEqual(get_response(test_sock_ok), self.test_dict_recv_ok)
        # тест корректной расшифровки ошибочного словаря
        self.assertEqual(get_response(test_sock_err), self.test_dict_recv_err)

    def test_200_ans(self):     #Тест корректтного разбора ответа 200
        self.assertEqual(parse_message({'response': 200}), '200 : OK')

    def test_400_ans(self):     #Тест корректного разбора 400
        self.assertEqual(parse_message({'response': 400, 'error': 'Bad Request'}), '400 : Bad Request')

    def test_no_response(self):     #Тест исключения без поля RESPONSE
        self.assertRaises(ValueError, parse_message, {'error': 'Bad Request'})

class TestSocket:       #Тестовый класс для тестирования отправки и получения
    '''
    Тестовый класс для тестирования отправки и получения,
    при создании требует словарь, который будет прогонятся
    через тестовую функцию
    '''
    def __init__(self, test_dict):
        self.test_dict = test_dict
        self.encoded_message = None
        self.receved_message = None

    def send(self, message_to_send):        #Тестовая функция отправки
        """
        Тестовая функция отправки, корретно  кодирует сообщение,
        так-же сохраняет что должно было отправлено в сокет.
        message_to_send - то, что отправляем в сокет
        :param message_to_send:
        :return:
        """
        json_test_message = json.dumps(self.test_dict)
        # кодирует сообщение
        self.encoded_message = json_test_message.encode('utf-8')
        # сохраняем что должно было отправлено в сокет
        self.receved_message = message_to_send

    def recv(self, max_len):        #Получаем данные из сокета (:param max_len 1024)
        json_test_message = json.dumps(self.test_dict)
        return json_test_message.encode('utf-8')


if __name__ == '__main__':
    unittest.main()