import unittest
from server import process_client_message

class TestServer(unittest.TestCase):
    '''
    В сервере только 1 функция для тестирования
    '''
    err_dict = {
        'response': 400,
        'error': 'Bad Request'
    }
    ok_dict = {'response': 200}

    def test_no_action(self):       #Тест на oшибку если нет действия
        self.assertEqual(process_client_message(
            {'time': '1.1', 'user': {'account_name': 'Guest'}}), self.err_dict)

    def test_wrong_action(self):        #Тест на oшибку если неизвестное действие
        self.assertEqual(process_client_message(
            {'action': 'Wrong', 'time': '1.1', 'user': {'account_name': 'Guest'}}), self.err_dict)

    def test_no_time(self):     #Тест на oшибку, если  запрос не содержит штампа времени
        self.assertEqual(process_client_message(
            {'action': 'presence', 'user': {'account_name': 'Guest'}}), self.err_dict)

    def test_no_user(self):     #Тест на oшибку - нет пользователя
        self.assertEqual(process_client_message(
            {'action': 'presence', 'time': '1.1'}), self.err_dict)

    def test_unknown_user(self):#Тест на oшибку - не Guest
        self.assertEqual(process_client_message(
            {'action': 'presence', 'time': 1.1, 'user': {'account_name': 'Guest1'}}), self.err_dict)

    def test_ok_check(self):#Тест на kорректный запрос
        self.assertEqual(process_client_message(
            {'action': 'presence', 'time': 1.1, 'user': {'account_name': 'Guest'}}), self.ok_dict)


if __name__ == '__main__':
    unittest.main()