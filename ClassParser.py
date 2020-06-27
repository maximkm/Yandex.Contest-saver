import requests
import re
from bs4 import BeautifulSoup
from os import makedirs
import sys


class ParserOIMP:
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36'}
    mask = ['OK', 'WA', 'RE', 'TL', 'CE']
    __const = 'https://official.contest.yandex.ru'

    def __init__(self, login, password):
        self.login = login
        self.password = password
        self.session = requests.Session()
        self.__try_connect(self.__const + '/login')

    def __try_connect(self, URL):
        form = {'login': self.login, 'password': self.password}
        URL = URL.replace('\n', '')
        with self.session as session:
            s = session.get(URL, headers=ParserOIMP.headers)
            soup = BeautifulSoup(s.text, 'html.parser')
            if 'авторизоваться' in soup.text:
                URL = self.__const + soup.find('a', attrs={'class': "link link_access_login"}).attrs['href']
                s = session.get(URL, headers=ParserOIMP.headers)
            if 'Войти' in soup.text:
                soup = BeautifulSoup(s.text, 'html.parser')
                form['retpath'] = soup.find('input', attrs={'name': "retpath"}).attrs['value']
                form['sk'] = soup.find('input', attrs={'name': "sk"}).attrs['value']
                s = session.post(URL, data=form, headers=ParserOIMP.headers)
                print('Авторизовались')
            return s.text

    @staticmethod
    def __print_bar(char):
        sys.stdout.write(char)
        sys.stdout.flush()

    def SaveTable(self, URL):
        with self.session as session:
            soup = BeautifulSoup(self.__try_connect(URL), 'html.parser')
            name = soup.find('a', attrs={'class': "link", 'href': re.compile('/enter/')}).contents[0]
            try:
                temp = self.__const + soup.find('a', attrs={'class': "link", 'href': re.compile('/standings/')}).attrs['href']
            except AttributeError:
                print(f'В {name} нет положения участников')
                return
            s = session.get(temp, headers=ParserOIMP.headers)
            soup = BeautifulSoup(s.text, 'html.parser')
            try:
                pages = len(soup.find('div', attrs={'class': "pager i-bem"}).contents)
            except AttributeError:
                pages = 1

            print(f'Начинаем парсить {pages} страниц, {name}')
            result = soup.find('table')
            self.__print_bar('O')
            for i in range(2, pages + 1):
                s = session.get(temp + f'?p={i}', headers=ParserOIMP.headers)
                data = BeautifulSoup(s.text, 'html.parser').find('tbody', attrs={'class': "table__body"})
                result.contents.append(data)
                self.__print_bar('O')
            print()
            try:
                makedirs(f'{self.login}\\{name}')
            except FileExistsError:
                pass  # директория уже создана
            with open(f'{self.login}\\{name}\\{name}.html', 'w') as file:
                file.write(str(result))
            print(f'Файл {name}.html сохранён')

    def SaveTasks(self, URL):
        def pars(soup, name, task):
            for i in ['?', ':', '*', '/', '\\', '<', '>', '|', '"']:
                task = task.replace(i, '_')
            try:
                makedirs(f'{self.login}\\{name}\\{task}')
            except FileExistsError:
                pass  # директория уже создана

            self.__print_bar('O')
            temp = soup.find('div', attrs={'class': 'problem-statement'})
            with open(f'{self.login}\\{name}\\{task}\\task.html', 'w', encoding='utf-8') as file:  # записываем условие
                file.write(str(temp))
            if 'Посылок нет' not in soup.text:
                temp = soup.find('tbody', attrs={'class': 'table__body'}).find_all('a', attrs={'class': 'link', 'href': re.compile('/run-report/')})
                num = 1
                for i in temp[::-1]:
                    if i.text in ParserOIMP.mask:
                        link = self.__const + i.attrs['href']
                        s = session.get(link, headers=ParserOIMP.headers)
                        soup = BeautifulSoup(s.text, 'html.parser')
                        URL_downdload = self.__const + soup.find('a', attrs={'title': 'Скачать исходный код'}).attrs['href']
                        headers = self.session.get(URL_downdload, allow_redirects=True)
                        ext = headers.raw.headers._container['content-disposition'][1].split('.')[-1]
                        code = headers.content
                        try:
                            with open(f'{self.login}\\{name}\\{task}\\{num}. {i.text}.{ext}', 'wb') as file:
                                file.write(code)
                        except OSError:  # прилетел тест
                            with open(f'{self.login}\\{name}\\{task}\\{num}. {i.text}.txt', 'wb') as file:
                                file.write(code)
                        self.__print_bar('.')
                        num += 1

        tasks = {}
        with self.session as session:
            soup = BeautifulSoup(self.__try_connect(URL), 'html.parser')
            name = soup.find('a', attrs={'class': "link", 'href': re.compile('/enter/')}).contents[0]
            try:
                temp = self.__const + soup.find('a', attrs={'class': "link", 'href': re.compile('/problems/')}).attrs['href']
            except AttributeError:
                print(f'Не начато виртуальное участие в {name}?')
                return
            s = session.get(temp, headers=ParserOIMP.headers)
            soup = BeautifulSoup(s.text, 'html.parser')
            temp = soup.find_all('span', attrs={'class': 'tabs-menu__tab-content-text'})
            for data in temp:
                tasks[self.__const + data.parent.attrs['href']] = data.text

            print(f'Начинаем парсить задачи ({len(tasks)}) {name}')
            for link, task in tasks.items():
                s = session.get(link, headers=ParserOIMP.headers)
                pars(BeautifulSoup(s.text, 'html.parser'), name, task)
            print()
