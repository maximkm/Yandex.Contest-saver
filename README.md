# Yandex.Contest-saver
Программа для скачивания: всех посылок, условий задач и положений участников из Яндекс.Контеста.
### Установка из исходников:
```
git clone https://github.com/maximkm/Yandex.Contest-saver.git
cd Yandex.Contest-saver
pip install -r requirements.txt
```
### Использование:
1. Написать все ссылки на контесты в файл ```links.txt```.
2. Зайти в ```config.json``` и поставить желаемые настройки скачивания.
3. Запустить программу: ```python main.py```.
4. Ввести логин и пароль, если не ввели их в ```config.json```.

Все поссылки будут сохранены в папке с названием вашего логина в дирректории main.py.

#### Про пароль
Пароль не обязательно записывать в ```config.json```, его можно вводить при каждом запуске программы.

Также можно запустить программу с флагом: ```python main.py --save```, чтобы введёный логин и пароль сохранился в **plaintext** в ```config.json```.

### Бенчмарки
В версии **v2.0** реализован асинхронный парсинг, благодаря чему скачивание происходит более чем в 4 раза быстрее по сравнению с версией **v1.0**. 50 контестов полностью скачиваются примерно за 7 минут.