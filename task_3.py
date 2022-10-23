"""
3. Определить, какие из слов «attribute», «класс», «функция», «type»
невозможно записать в байтовом типе с помощью маркировки b''.

"""

word_1 = 'attribute'
word_2 = 'класс'
word_3 = 'функция'
word_4 = 'type'

list_word = [word_1, word_2, word_3, word_4]

for i in list_word:
    try:
        print(i.encode('ascii'))
    except:
        print(f'слово "{i}" невозможно записать в байтовом типе')