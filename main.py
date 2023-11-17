from bs4 import BeautifulSoup
from pick import pick
from os import system, getcwd
from time import sleep
import requests

DATA = dict()


def authentication(domain, login=None, password=None):
    """Создает сессию и выполняет аутентификацию, если потребуется.
    :param domain: ...
    :param login: None, если аутентификация не требуется.
    :param password: None, если аутентификация не требуется.
    :return: Возвращает сессию.
    """
    session = requests.Session()
    session.verify = False
    if password is None:
        return session
    else:
        session.auth = (login, password)
        session.post(domain)
        return session


def parsed_endpoint(response):
    """Собирает ендпоинты для внутренних ссылок.
    :param response: Ответ на запрос, из которого парсим документ.
    :return: Возвращает список эндпоинтов.
    """
    path_list = list()
    document = BeautifulSoup(response.text, "html.parser")
    for data in document.find_all('a'):
        if data["href"].startswith("/"):
            path_list.append(data["href"])
    return path_list


def parsed_text(response):
    """Ищет на странице текст с окончание .php.
    :param response: ...
    :return: True, если есть .php на странице. Иначе False.
    """
    document = BeautifulSoup(response.text, "html.parser")
    return True if '.php' in document.get_text() else False


def collect(session, domain, lt=None, i=0):
    """Рекурсивно перебирает все внутренние ссылки.
    :param session: ...
    :param domain: ...
    :param lt: Список ендпоинтов.
    :param i: Индекс для lt.
    :return: Вовзращает словарь со ссылками, статус кодами, флагом наличия ошибок.
    """
    if lt is None:
        lt = [""]

    system("cls")
    print("Собрано:", len(DATA))

    if i > len(lt):
        return DATA

    if domain + lt[i] not in DATA:
        response = session.get(domain + lt[i])
        DATA[domain + lt[i]] = [response.status_code]
        DATA[domain + lt[i]].append(parsed_text(response))
        lt = parsed_endpoint(response)
        return collect(session, domain, lt, i + 1)
    else:
        return collect(session, domain, lt, i + 1)


def output_csv(data):
    """Записывает данные в csv.
    :param data: Данные.
    :return: ...потому что хочу.
    """
    with open(getcwd()+"/"+'result.csv', 'w') as csv:
        csv.write("url, status_code, php_error\n")
        for key, value in data.items():
            status, php_error = value[0], value[1]
            csv.write(f"{str(key)}, {str(status)}, {str(php_error)}\n")
    return True


def interface():
    """Интерфейс для управления.
    :return: ...
    """
    domain = input("Введите URL (http(s)://example.ru/):")

    title = "Нужна аутентификация?"
    options = ["Да", "Нет"]
    option, index = pick(options, title)

    if index == 0:
        login = input("login:")
        password = input("password:")
        session = authentication(domain, login, password)
    else:
        session = authentication(domain)

    collect(session, domain)

    output_csv(DATA)
    print(f"Собрано: {len(DATA)}. Данные выведены в {getcwd()}")
    sleep(10)


if __name__ == "__main__":
    interface()
