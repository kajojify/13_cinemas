import requests
import requests.exceptions as reqexc
import progressbar
import time

from bs4 import BeautifulSoup


class Proxy:
    proxy_url = "https://hidemy.name/ru/proxy-list/?maxtime=1500&type=s"
    proxy_list = []

    def __init__(self):
        self.proxy_list = self.get_all_proxies()
        self._proxy_gen = self.get_valid_proxy_iter()
        self.current = next(self._proxy_gen)

    def __iter__(self):
        return self

    def __next__(self):
        self.current = next(self._proxy_gen)
        return self.current

    def get_all_proxies(self):
        all_proxies = []
        proxy_page = requests.get(self.proxy_url)
        proxy_soup = BeautifulSoup(proxy_page.content, "lxml")
        all_proxy_tags = proxy_soup.findAll('td', "tdl")
        for proxy_tag in all_proxy_tags:
            ip = proxy_tag.text
            port = proxy_tag.findNext().text
            proxy_address = "http://{}:{}".format(ip, port)
            all_proxies.append(proxy_address)
        return all_proxies

    def get_valid_proxy_iter(self):
        for proxy in self.proxy_list:
            if self.is_valid(proxy):
                yield proxy

    def is_valid(self, proxy_address):
        test_url = "https://ya.ru"
        page = requests.get(test_url, timeout=5,
                            proxies={'http': proxy_address})
        if page.status_code == 200:
            return True
        else:
            return False


def fetch_afisha_page():
    afisha_url = "http://www.afisha.ru/msk/schedule_cinema/"
    afisha_page = requests.get(afisha_url)
    return afisha_page.content


def parse_afisha_list(raw_afisha_html, movies_number=10):
    afisha_list = []
    afisha_soup = BeautifulSoup(raw_afisha_html, "lxml")
    movie_class = "object s-votes-hover-area collapsed"
    all_movie_tags = afisha_soup.findAll('div', movie_class)
    for movie_tag in all_movie_tags[:movies_number]:
        movie_title = movie_tag.find('h3', "usetags").find('a').text
        theaters_number = len(movie_tag.findAll('td', "b-td-item"))
        afisha_list.append((movie_title, theaters_number))
    return afisha_list


def fetch_movie_info(movie_title, proxy):
    search_url = "https://www.kinopoisk.ru/search/handler-chromium-extensions"\
                 "?query={movie}&go=1".format(movie=movie_title)
    while True:
        try:
            movie_page = requests.get(search_url, timeout=5,
                                      proxies={'https': proxy.current})
            movie_soup = BeautifulSoup(movie_page.content, "lxml")
            rating_elem = movie_soup.find('span', "rating_ball")
            return float(rating_elem.text) if rating_elem else 0
        except (reqexc.ProxyError, requests.ConnectionError,
                reqexc.ConnectTimeout, reqexc.ReadTimeout):
            next(proxy)


def sort_movies(movies_list):
    sorted_movies = sorted(movies_list, key=lambda x: x[1], reverse=True)
    return list(sorted_movies)


def output_movies_to_console(movies):
    print("{:<5}{:<30}{:<20}{:<30}\n".format("№", "Title",
                                             "Kinopoisk rating",
                                             "Theaters number"))
    for movie_number, (title, rate, theaters_number) in enumerate(movies, 1):
        rate = rate if rate else "No info"
        print("{:<5}{:<30}{:<20}{:<30}".format(movie_number, title,
                                               rate, theaters_number))

if __name__ == '__main__':
    movie_list = []
    proxy = Proxy()
    print("Proxies are collected!")

    print("Parsing... Stand by.")
    raw_afisha_page = fetch_afisha_page()
    afisha_list = parse_afisha_list(raw_afisha_page)
    with progressbar.ProgressBar(max_value=len(afisha_list)) as bar:
        for number, (title, theaters_number) in enumerate(afisha_list, 1):
            try:
                rate = fetch_movie_info(title, proxy)
            except StopIteration:
                exit("Proxies are over! Restart the script.")
            movie_list.append((title, rate, theaters_number))
            bar.update(number)
    time.sleep(0.5)
    sorted_movies = sort_movies(movie_list)
    output_movies_to_console(sorted_movies)
