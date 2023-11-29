from bs4 import BeautifulSoup
from pick import pick
from os import system, getcwd
from time import sleep
import requests

DATA = dict()


def clear_and_status():
    system("cls")
    print("Собрано:", len(DATA))


def create_session():
    """Создает сессию для хранения пользовательских данных.
    :return: Созданная сессия.
    """
    session = requests.Session()
    session.verify = False
    return session


def auth(session, domain, login, password):
    """Отправляет логин и пароль для базовой аутентификации.
    :param session: Cессия для хранения пользовательских данных.
    :param domain: Домен, с которым работает скрипт.
    :param login: Логин для аутентификации.
    :param password: Пароль для аутентификации.
    :return: Сессия с пройденной аутентификацией.
    """
    session.auth = (login, password)
    session.post(domain)
    return session


def parsed_path(document):
    """Просматривает html-документ из ответа и собирает все пути в список.
    :param document: Полученный html-документ.
    :return: Список путей.
    """
    path_list = list()
    for data in document.find_all('a'):
        try:
            path_link = data["href"]
            if path_link.startswith("/") and path_link not in path_list:
                path_list.append(path_link)
        except KeyError:
            pass
    return path_list


def parsed_text(document):
    """Ищет указанный текст на странице.
    :param document: Полученный html-документ.
    :return: True, если есть .php на странице. Иначе False.
    """
    return True if '.php' in document.get_text() else False


def collect(session, domain, path_list=None, i=0):
    """Рекурсивно перебирает все внутренние ссылки.
    :param session: Cессия для хранения пользовательских данных.
    :param domain: Домен, с которым работает скрипт.
    :param path_list: Список путей.
    :param i: Индекс path_list для выхода из рекурсии.
    :return: Словарь со ссылками, статус кодами, флагом наличия ошибок.
    """
    if path_list is None:
        path_list = [""]

    if i == len(path_list):
        return DATA

    # clear_and_status()

    url = domain + path_list[i]
    if url not in DATA:
        response = session.get(url)
        if response.status_code == 401:
            login = input("Введите логин:")
            password = input("Введите логин:")
            session = auth(session, domain, login, password)
            response = session.get(url)
        document = BeautifulSoup(response.text, "html.parser")
        DATA[url] = [response.status_code, parsed_text(document)]
        return collect(session, domain, parsed_path(document))
    else:
        return collect(session, domain, path_list, i + 1)


def output_csv(data):
    """Записывает данные в csv.
    :param data: Данные.
    """
    with open(getcwd()+"/"+'result.csv', 'w') as csv:
        csv.write("url, status_code, php_error\n")
        for key, value in data.items():
            status, php_error = value[0], value[1]
            csv.write(f"{str(key)}, {str(status)}, {str(php_error)}\n")


def interface():
    """Интерфейс для управления.
    """
    domain = input("Введите URL в формате http(s)://example.ru/:")
    collect(create_session(), domain)

    output_csv(DATA)
    print(f"Собрано: {len(DATA)}. Данные выведены в {getcwd()}")
    sleep(10)


if __name__ == "__main__":
    interface()
