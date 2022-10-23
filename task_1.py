"""
1. Каждое из слов «разработка», «сокет», «декоратор» представить
в строковом формате и проверить тип и содержание соответствующих переменных.
Затем с помощью онлайн-конвертера преобразовать строковые представление
в набор кодовых точек Unicode и также проверить тип и содержимое переменных.

"""

word_1 = 'разработка'
word_2 = 'сокет'
word_3 = 'декоратор'

list_word = [word_1, word_2, word_3]

for i in list_word:
    print(type(i))
    print(i)

print()

unicode_word_1 = '\u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0430'
unicode_word_2 = '\u0441\u043e\u043a\u0435\u0442'
unicode_word_3 = '\u0434\u0435\u043a\u043e\u0440\u0430\u0442\u043e\u0440'

list_unicode_word = [unicode_word_1, unicode_word_2, unicode_word_3]

for n in list_unicode_word:
    print(type(n))
    print(n)

