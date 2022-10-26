"""
3. Задание на закрепление знаний по модулю yaml.
Написать скрипт, автоматизирующий сохранение данных
в файле YAML-формата.
Для этого:

Подготовить данные для записи в виде словаря, в котором
первому ключу соответствует список, второму — целое число,
третьему — вложенный словарь, где значение каждого ключа —
это целое число с юникод-символом, отсутствующим в кодировке
ASCII(например, €);

Реализовать сохранение данных в файл формата YAML — например,
в файл file.yaml. При этом обеспечить стилизацию файла с помощью
параметра default_flow_style, а также установить возможность работы
с юникодом: allow_unicode = True;

Реализовать считывание данных из созданного файла и проверить,
совпадают ли они с исходными.
"""

import yaml

data_yaml = {
    'color': ['black', 'white', 'blue'], 
    'availability': 5, 
    'car_price': {
        'Audi': '20000€',
        'Mercedes': '30000€',
        'BMW': '27000€',
        'Porsche': '70000€',
        'Volkswagen': '18000€'
    }
}

with open('file.yaml', 'w', encoding='utf-8') as f_n:
    yaml.dump(data_yaml, f_n, default_flow_style=False, allow_unicode = True, sort_keys=False)

with open('file.yaml', 'r', encoding='utf-8') as f_n:
    f_n_content = yaml.load(f_n, Loader=yaml.SafeLoader)
print(f_n_content == data_yaml)

#TypeError: load() missing 1 required positional argument: 'Loader'









