"""
1. Задание на закрепление знаний по модулю CSV. Написать скрипт,
осуществляющий выборку определенных данных из файлов info_1.txt, info_2.txt,
info_3.txt и формирующий новый «отчетный» файл в формате CSV.

Для этого:

Создать функцию get_data(), в которой в цикле осуществляется перебор файлов
с данными, их открытие и считывание данных. В этой функции из считанных данных
необходимо с помощью регулярных выражений извлечь значения параметров
«Изготовитель системы», «Название ОС», «Код продукта», «Тип системы».
Значения каждого параметра поместить в соответствующий список. Должно
получиться четыре списка — например, os_prod_list, os_name_list,
os_code_list, os_type_list. В этой же функции создать главный список
для хранения данных отчета — например, main_data — и поместить в него
названия столбцов отчета в виде списка: «Изготовитель системы»,
«Название ОС», «Код продукта», «Тип системы». Значения для этих
столбцов также оформить в виде списка и поместить в файл main_data
(также для каждого файла);

Создать функцию write_to_csv(), в которую передавать ссылку на CSV-файл.
В этой функции реализовать получение данных через вызов функции get_data(),
а также сохранение подготовленных данных в соответствующий CSV-файл;

Проверить работу программы через вызов функции write_to_csv().

"""

import csv
import re

def get_data():

    os_prod_list = []
    os_name_list = []
    os_code_list = []
    os_type_list = []
    main_list = []
    
    for i in range(1, 4):
        file_text = open(f'info_{i}.txt')
        text = file_text.read()

        pattern_prod = re.compile(r'Изготовитель системы:\s*\S*')
        os_prod_list.append(pattern_prod.findall(text)[0].split()[2])

        pattern_name = re.compile(r'Windows\s\S*')
        os_name_list.append(pattern_name.findall(text)[0])

        pattern_code = re.compile(r'Код продукта:\s*\S*')
        os_code_list.append(pattern_code.findall(text)[0].split()[2])

        pattern_type = re.compile(r'Тип системы:\s*\S*')
        os_type_list.append(pattern_type.findall(text)[0].split()[2])
            
    pattern = ['Изготовитель системы', 'Название ОС', 'Код продукта', 'Тип системы']
    main_list.append(pattern)

    a = 1
    for i in range(0, 3):
        row_list = []
        row_list.append(a)
        row_list.append(os_prod_list[i])
        row_list.append(os_name_list[i])
        row_list.append(os_code_list[i])
        row_list.append(os_type_list[i])
        main_list.append(row_list)
        a += 1
    #for x in main_list:
     #   print(x)
    return main_list

def write_to_csv(file_csv):

    main_list = get_data()

    with open(file_csv, 'w', encoding='utf-8') as f_n:
        f_n_writer = csv.writer(f_n)
        for row in main_list:
            f_n_writer.writerow(row)

          
write_to_csv('task_1.csv')            

    
    

