from requests_futures.sessions import FuturesSession
from concurrent.futures import as_completed
from bs4 import BeautifulSoup
from os import makedirs, path
import requests
import sys
import re


class ContestParser:
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
            s = session.get(URL, headers=ContestParser.headers)
            soup = BeautifulSoup(s.text, 'html.parser')
            if 'авторизоваться' in soup.text:
                URL = self.__const + soup.find('a', attrs={'class': "link link_access_login"}).attrs['href']
                s = session.get(URL, headers=ContestParser.headers)
            if 'Войти' in soup.text:
                soup = BeautifulSoup(s.text, 'html.parser')
                form['retpath'] = soup.find('input', attrs={'name': "retpath"}).attrs['value']
                form['sk'] = soup.find('input', attrs={'name': "sk"}).attrs['value']
                s = session.post(URL, data=form, headers=ContestParser.headers)
                if 'error' in s.url:
                    raise ValueError('Incorrect login or password')
                print('Авторизовались')
            return s.text

    @staticmethod
    def __print_bar(char):
        sys.stdout.write(char)
        sys.stdout.flush()

    @staticmethod
    def __fixDir(name):
        for i in ['?', ':', '*', '/', '\\', '<', '>', '|', '"']:
            name = name.replace(i, '_')
        return name

    @staticmethod
    def __createDir(*args):
        way = [ContestParser.__fixDir(arg) for arg in args]
        dir = '/'.join(way)
        if not path.exists(dir):
            makedirs(dir)
        return dir

    def saveTable(self, URL):
        with self.session as session:
            soup = BeautifulSoup(self.__try_connect(URL), 'html.parser')
            if 'У вас нет прав просматривать это соревнование' in soup.text:
                print('Нет прав на просмотр')
                return
            name = soup.find('a', attrs={'class': "link", 'href': re.compile('/enter/')}).contents[0]
            try:
                temp = self.__const + soup.find('a', attrs={'class': "link", 'href': re.compile('/standings/')}).attrs['href']
            except AttributeError:
                print(f'В {name} нет положения участников')
                return
            s = session.get(temp, headers=ContestParser.headers)
            soup = BeautifulSoup(s.text, 'html.parser')
            try:
                pages = len(soup.find('div', attrs={'class': "pager i-bem"}).contents)
            except AttributeError:
                pages = 1

            print(f'Скачиваем {pages} страниц результатов {name}')
            result = soup.find('table')
            self.__print_bar('O')
            future_session = FuturesSession(session=session)
            futures = [future_session.get(temp + f'?p={i}') for i in range(2, pages + 1)]
            for future in as_completed(futures):
                data = BeautifulSoup(future.result().text, 'html.parser').find('tbody', attrs={'class': "table__body"})
                result.contents.append(data)
                self.__print_bar('O')
            print()

            dir = self.__createDir(self.login, name)
            with open(f'{dir}/{self.__fixDir(name)}.html', 'w') as file:
                file.write(str(result))

    def saveTasks(self, URL, txt=False, html=True):
        tasks = {}
        with self.session as session:
            soup = BeautifulSoup(self.__try_connect(URL), 'html.parser')
            if 'У вас нет прав просматривать это соревнование' in soup.text:
                print('Нет прав на просмотр')
                return
            name = soup.find('a', attrs={'class': "link", 'href': re.compile('/enter/')}).contents[0]
            try:
                temp = self.__const + soup.find('a', attrs={'class': "link", 'href': re.compile('/problems/')}).attrs['href']
            except AttributeError:
                print(f'Не начато виртуальное участие в {name}?')
                return
            s = session.get(temp, headers=ContestParser.headers)
            soup = BeautifulSoup(s.text, 'html.parser')
            temp = soup.find_all('span', attrs={'class': 'tabs-menu__tab-content-text'})
            for data in temp:
                tasks[self.__const + data.parent.attrs['href']] = data.text

            print(f'Скачиваем задачи ({len(tasks)}) {name}')
            name = self.__fixDir(name)
            future_session = FuturesSession(session=session)
            fut_tasks = [future_session.get(link) for link in tasks.keys()]
            fut_solution, info = [], []
            for res, task in zip(fut_tasks, tasks.values()):
                soup = BeautifulSoup(res.result().text, 'html.parser')
                if 'Посылок нет' not in soup.text:
                    temp = soup.find('tbody', attrs={'class': 'table__body'})
                    temp = temp.find_all('a', attrs={'class': 'link', 'href': re.compile('/run-report/')})
                    for num, i in enumerate(temp[:-1][::-2]):
                        if i.text in ContestParser.mask:
                            link = self.__const + i.attrs['href']
                            fut_solution.append(future_session.get(link))
                            info.append({'res': i.text, 'task': self.__fixDir(task), 'n': num + 1})
                self.__print_bar('O')
                dir = self.__createDir(self.login, name, task)
                temp = soup.find('div', attrs={'class': 'problem-statement'})
                if txt:
                    with open(f'{dir}/task.txt', 'w', encoding='utf-8') as file:
                        file.write(temp.text)
                if html:
                    with open(f'{dir}/task.html', 'w', encoding='utf-8') as file:
                        file.write(str(temp))
            get_code = []
            for f in as_completed(fut_solution):
                soup = BeautifulSoup(f.result().text, 'html.parser')
                url_for_code = self.__const + soup.find('a', attrs={'title': 'Скачать исходный код'}).attrs['href']
                get_code.append(future_session.get(url_for_code, allow_redirects=True))
            for code, data in zip(as_completed(get_code), info):
                headers = code.result()
                ext = headers.raw.headers._container['content-disposition'][1].split('.')[-1]
                code = headers.content
                try:
                    with open(f'{self.login}/{name}/{data["task"]}/{data["n"]}. {data["res"]}.{ext}', 'wb') as file:
                        file.write(code)
                except OSError:
                    with open(f'{self.login}/{name}/{data["task"]}/{data["n"]}. {data["res"]}.txt', 'wb') as file:
                        file.write(code)
                self.__print_bar('-')
            print()
