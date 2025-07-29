"""main.py

Модуль для получения данных из таблицы users базы
данных testDB с источника http://185.244.219.162/phpmyadmin/.

url_auth - адрес для авторизации,
url_get - адрес таблицы users,
username - логин для авторизации,
password - пароль для авторизации.

get_page() - функция для получения html страницы,
parsing() - функция для парсинга страницы и извлечения данных из таблицы,
create_df() - функция для преобразования данных в DataFrame.
"""


import requests
import pandas
from bs4 import BeautifulSoup


url_auth = 'http://185.244.219.162/phpmyadmin/'
url_get = 'http://185.244.219.162/phpmyadmin/index.php?route=/sql&server=1&db=testDB&table=users&pos=0'
username = 'test'
password = 'JHFBdsyf2eg8*'


def get_page(url_auth, pma_username, pma_password, url_get):
    """Функция для авторизации на url_auth и получения html страницы url_get.

    В качестве параметров принимает:
    url_auth - страница для авторизации,
    pma_username - логин,
    pma_password - пароль,
    url_get - страница для отправки GET запроса.

    Возвращает answer - ответ на GET запрос к странице url_get.
    """
    with requests.Session() as session:
        answer = session.get(url_auth).text

        soup = BeautifulSoup(answer, 'html.parser')
        token = soup.find("input", {"name": "token"})["value"]
        data = {'pma_username': pma_username,
                'pma_password': pma_password,
                'token': token}

        session.post(url=url_auth, data=data)

        answer = session.get(url_get)
    return answer


def parsing(html_page):
    """Функция для парсинга страницы и извлечения данных из таблицы users.

    В качестве параметра принимает html_page - страницу для парсинга.

    Возвращает:
    names - список с названиями столбцов таблицы,
    table - список со списками данных таблицы (данные каждой строки
    хранятся в отдельном вложенном списке), пример:
    [
     ['1', 'Имя1'],
     ['2', 'Имя2'],
     ['3', 'Имя3'],
     ...
    ]
    """
    soup = BeautifulSoup(html_page, 'html.parser')

    table = soup.find('table', {'class':'table table-light table-striped '
                                                    'table-hover table-sm table_results '
                                                    'data ajax w-auto'})
    thead = table.find('thead', {"class":"thead-light"})
    # Поиск всех ячеек шапки таблицы кроме первой (пустой ячейки).
    thead = thead.find_all('th')[1:]

    names = list()
    for name in thead:
        small = name.find('small')
        name = name.find('a').text
        # Удаление индексов из текста в ячейке, если они есть.
        if small and small.text in name:
            name = name.replace(small.text, '')

        name = name.strip()
        names.append(name)

    tbody = table.find('tbody')
    tbody = tbody.find_all('tr')

    table =list()
    for line in tbody:
        # Поиск всех ячеек в строке таблицы, кроме первых 4 (пустых).
        line = line.find_all('td')[4:]

        elems = list()
        for elem in line:
            elem = elem.text.strip()
            elems.append(elem)

        table.append(elems)

    return names, table


def create_df(table, names):
    """Функция для преобразования данных в DataFrame.

    В качестве параметров принимает:
    table - список со списками данных,
    names - список с заголовками столбцов.

    Возвращает df - DataFrame отсортированный по первому столбцу.
    """
    df = pandas.DataFrame(data=table, columns=names).sort_values(names[0])
    return df


if __name__ == '__main__':
    html_page = get_page(url_auth, username, password, url_get).text
    names, table = parsing(html_page)
    df = create_df(table, names)
    print(df.to_string(index=False))

