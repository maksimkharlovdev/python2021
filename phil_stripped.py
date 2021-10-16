#!/usr/bin/env python3
import requests
from urllib.parse import quote
from urllib.parse import unquote
from urllib.error import URLError, HTTPError
from collections import deque
import re


def get_content(name):
    """
    Функция возвращает содержимое вики-страницы name из русской Википедии.
    В случае ошибки загрузки или отсутствия страницы возвращается None.
    """
    try:
        with requests.get('http://ru.wikipedia.org/wiki/' + quote(name)) as page:
            content = page.text
    except (URLError, HTTPError):
        return None

    return content


def extract_content(page):
    """
    Функция принимает на вход содержимое страницы и возвращает 2-элементный
    tuple, первый элемент которого — номер позиции, с которой начинается
    содержимое статьи, второй элемент — номер позиции, на котором заканчивается
    содержимое статьи.
    Если содержимое отсутствует, возвращается (0, 0).
    """
    if page is None:
        return 0, 0

    for i in re.finditer(r'<body.*>', page):
        start = i.end()

    for i in re.finditer(r'</body.*>', page):
        end = i.start()

    return start, end - 1


def extract_links(page, begin, end):
    """
    Функция принимает на вход содержимое страницы и начало и конец интервала,
    задающего позицию содержимого статьи на странице и возвращает все имеющиеся
    ссылки на другие вики-страницы без повторений и с учётом регистра.
    """
    list_links = re.findall(
        r'<(?:a|A)\s+?(?:h|H)ref=(?:"|\')/wiki/([_%\w\d-]*?)(?:"|\')',
        page[begin:end], re.I | re.S)
    list_links = list(set(list_links))

    for i in range(0, len(list_links)):
        list_links[i] = unquote(list_links[i])

    return list_links


def find_chain(start, finish):
    """
    Функция принимает на вход название начальной и конечной статьи и возвращает
    список переходов, позволяющий добраться из начальной статьи в конечную.
    Первым элементом результата должен быть start, последним — finish.
    Если построить переходы невозможно, возвращается None.
    """
    queue = deque()
    visited = dict()
    queue.append(start)
    visited[start] = True
    steps = []
    if start == finish:
        return [start]
    while len(queue) != 0:
        node = queue.popleft()
        page = get_content(node)
        if page is None:
            return None
        else:
            steps.append(node)
        begin, end = extract_content(page)
        links = extract_links(page, begin, end)
        if finish in links:
            steps.append(finish)
            return steps
        else:
            for i in range(len(links)):
                if (links[i] in visited) is False:
                    queue.append(links[i])
                    visited[links[i]] = True
                    break


def main():
    start = input()
    final = input()
    print(find_chain(start, final))


if __name__ == '__main__':
    main()
