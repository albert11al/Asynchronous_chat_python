"""
4. Преобразовать слова «разработка», «администрирование», «protocol»,
«standard» из строкового представления в байтовое и выполнить
обратное преобразование (используя методы encode и decode).

"""

word_1 = 'разработка'
word_2= 'администрирование'
word_3 = 'protocol'
word_4 = 'standard'

list_word = [word_1, word_2, word_3, word_4]

list_encode = []
list_decode = []
for i in list_word:
    list_str = i.encode('utf-8')
    list_encode.append(list_str)
for w, e in zip(list_word, list_encode):
    print(w, '-', e)

print()

for n in list_encode:
    list_bayt = n.decode('utf-8')
    list_decode.append(list_bayt)
for e, d in zip(list_encode, list_decode):
    print(e, '-', d)

