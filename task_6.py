"""
6. Создать текстовый файл test_file.txt, заполнить его тремя строками:
«сетевое программирование», «сокет», «декоратор».
Проверить кодировку файла по умолчанию.
Принудительно открыть файл в формате Unicode и вывести его содержимое.

"""
from chardet.universaldetector import UniversalDetector

detector = UniversalDetector()
with open('test_file.txt', 'rb') as fh:
    for line in fh:
        # скармливаем детектору строки
        detector.feed(line)
        if detector.done:
            # если детектор определил 
            # кодировку, то прерываем цикл
            break
    # закрываем детектор
    detector.close()
print(detector.result['encoding'])


with open('test_file.txt', 'r', encoding=detector.result['encoding']) as f_n:
    content = f_n.read()
print(content)