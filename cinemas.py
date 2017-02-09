import requests
import requests.exceptions as reqexc

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
    afisha_soup = BeautifulSoup(raw_afisha_html, "lxml")
    movie_class = "object s-votes-hover-area collapsed"
    all_movies = afisha_soup.findAll('div', movie_class)
    for movie in all_movies[:movies_number]:
        movie_title = movie.find('h3', "usetags").find('a').text
        theaters_number = len(movie.findAll('td', "b-td-item"))
        yield (movie_title, theaters_number)


def fetch_movie_info(movie_title, proxy):
    search_url = "https://www.kinopoisk.ru/search/handler-chromium-extensions"\
                 "?query={movie}&go=1".format(movie=movie_title)
    while True:
        try:
            movie_page = requests.get(search_url, timeout=5,
                                      proxies={'https': proxy.current})
            movie_soup = BeautifulSoup(movie_page.content, "lxml")
            rating_elem = movie_soup.find('span', "rating_ball")
            return float(rating_elem.text) if rating_elem else None
        except (reqexc.ProxyError, requests.ConnectionError,
                reqexc.ConnectTimeout, reqexc.ReadTimeout):
            next(proxy)


def sort_movies(movies_list):
    sorted_movies = list(sorted(movies_list, key=lambda x: x[1]))
    return sorted_movies


def output_movies_to_console(movies):
    for movie in movies:
        print(movie)


if __name__ == '__main__':
    movie_list = []
    proxy = Proxy()
    print("Proxies are collected!")
    raw_afisha_page = fetch_afisha_page()
    print("Parsing... Stand by. ")
    for title, theaters_number in parse_afisha_list(raw_afisha_page):
        rate = fetch_movie_info(title, proxy)
        movie_list.append((title, rate, theaters_number))
    sorted_movies = sort_movies(movie_list)
    output_movies_to_console(sorted_movies)
