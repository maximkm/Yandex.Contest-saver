from ClassParser import ParserOIMP

person = ParserOIMP('login', 'password')  # авторизация
ParserOIMP.mask = ['OK', 'WA', 'RE', 'TL', 'CE']  # какие посылки сохранять
with open('Links.txt', 'r') as file:  # проходимся по контестам
    for URL in file:
        if 'official.contest.yandex.ru' not in URL:
            continue
        person.SaveTable(URL)  # сохраняем таблицу положения участников
        person.SaveTasks(URL)  # сохраняем все посылки
