"""
2. Каждое из слов «class», «function», «method» записать в байтовом формате
без преобразования в последовательность кодов
не используя методы encode и decode)
и определить тип, содержимое и длину соответствующих переменных.

"""

word_1 = b'class'
word_2= b'function'
word_3 = b'method'

list_word = [word_1, word_2, word_3]

for i in list_word:
    print(type(i))
    print(i)
    print(len(i))