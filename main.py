from src.ClassParser import ContestParser
from json import dump, load
from getpass import getpass
import click
from timeit import default_timer


@click.command()
@click.option('--save', is_flag=True, default=False, help='Сохраняет логин и пароль plain textom в config.json')
def main(save):
    with open('config.json', 'r') as file:
        config = load(file)

    if not config['login']:
        config['login'] = input('login: ')
    if not config['password']:
        config['password'] = getpass('password: ')
    if save:
        with open('config.json', 'w') as write_file:
            dump(config, write_file, indent=0)

    person = ContestParser(config['login'], config['password'])
    ContestParser.mask = config['mask']
    Time = default_timer()
    with open('links.txt', 'r') as file:
        for URL in file:
            if 'official.contest.yandex.ru' not in URL:
                continue
            if config['save_solutions']:
                person.saveTasks(URL, config['tasks_in_txt'], config['tasks_in_html'])
            if config['save_result_table']:
                person.saveTable(URL)
    print(f'Скачали за {round((default_timer() - Time)/60, 2)} минут')


if __name__ == '__main__':
    main()
