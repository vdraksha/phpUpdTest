from bs4 import BeautifulSoup
import requests

DATA = dict()


def authentication(domain, login, password):
    session = requests.Session()
    session.auth = (login, password)
    session.post(domain)
    return session


def get_endpoint(response):
    path_list = []
    document = BeautifulSoup(response.text, "html.parser")
    for data in document.find_all('a'):
        if data["href"].startswith("/"):
            path_list.append(data["href"])
    return path_list


def collect(session, domain, lt=None, i=0):
    if lt is None:
        lt = ["/"]

    if i > len(lt):
        return DATA

    if domain + lt[i] not in DATA:
        response = session.get(domain + lt[i])
        DATA[domain + lt[i]] = response.status_code
        lt = get_endpoint(response)
        print(True)
        return collect(session, domain, lt, i+1)
    else:
        print(False)
        return collect(session, domain, lt, i+1)


if __name__ == "__main__":
    u = "http://utoy-test.2204535.ru"
    s = authentication(u, "utoy", "utoy")
    i = 0
    for key, value in collect(s, u).items():
        i += 1
        print(i, key, value)

