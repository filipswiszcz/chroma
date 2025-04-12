import os
import sys
import re
import time

import requests
import fake_useragent as fu
import bs4
import queue as q
import threading as t


class Randomizer():
    def __init__(self):
        self.__agent = fu.UserAgent(os="Ubuntu")
        self.__proxies = self.__load_proxies()
        self.__referers = self.__init_referers()

    def __load_proxies(self):
        cdir = os.path.dirname(__file__)
        proxies = {}
        with open(os.path.join(cdir, "resources/proxies.txt"), "r") as f:
            for ln in f:
                proxies["http"] = "http://" + ln
                proxies["https"] = "http://" + ln
        return proxies

    def __init_referers(self):
        return [
            "https://www.google.com",
            "https://www.yahoo.com",
            "https://www.bing.com",
            "https://www.youtube.com"
        ]

    def get_user_agent(self):
        return self.__agent.random

    def get_proxies(self):
        return self.__proxies

    def get_referer(self):
        from random import randint # it should not be here
        return self.__referers[randint(0, len(self.__referers) - 1)]

class Source:
    def __init__(self, name, base_url, prod_url, prod_k, pages_k):
        self.name = name
        self.base_url = base_url
        self.prod_url = prod_url
        self.prod_k = prod_k
        self.pages_k = pages_k


# id | name | type | desc | ingredients

rand = Randomizer()


# source = Source(
#     "rossmann",
#     "https://www.rossmann.pl",
#     "https://www.rossmann.pl/kategoria/makijaz-i-paznokcie,12000",
#     7487, # find those on website
#     312
# )

# ?page=

# headers = {
#     "User-agent": rand.get_user_agent(),
#     "Accept-Language": "en-US,en;q=0.9",
#     "Referer": rand.get_referer()
# }
# proxies = rand.get_proxies()

# response = requests.get(source.prod_url, headers=headers, proxies=proxies)
# soup = bs4.BeautifulSoup(response.content, "html.parser")
# elems = soup.find_all(class_=re.compile("^RowProductTiles"))
# urls = []
# for e in elems:
#     imgcs = e.find_all(class_=re.compile("^ImageSection-module_imageSection"))
#     for i in imgcs:
#         urls.append(i.find("a").get("href"))

# print(urls[0])

# if result is None, then insert empty row with id

URLS = q.Queue()
PROC = True

def run_source(brand):
    match brand:
        case "rossmann":
            details = __get_source_details("https://rossmann.pl/kategoria/makijaz-i-paznokcie,12000")
            source = Source(
                "rossmann", "https://rossmann.pl",
                "https://rossmann.pl/kategoria/makijaz-i-paznokcie,12000",
                int(details[0][:-10]), int(details[1])
            )
            th = t.Thread(target=__proc_que)
            th.start()
            __collect_urls(source)
        case _:
            pass


def __get_source_details(url):
    headers = {
        "User-agent": rand.get_user_agent(),
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": rand.get_referer()
    }
    res = requests.get(url, headers=headers, proxies=rand.get_proxies())
    soup = bs4.BeautifulSoup(res.content, "html.parser")
    products = soup.find(class_=re.compile("^styles-module_productListCount")).text
    pages = soup.find(class_=re.compile("^pages layout-2024")).find("span").text
    return products, pages


def __proc_que():
    cdir = os.path.dirname(__file__)
    while PROC:
        with open(os.path.join(cdir, "resources/urls.txt"), "a") as f:
            for i in range(URLS.qsize()): f.write(URLS.get() + "\n")
        sys.stdout.write(f"\r[COLLECTD] urls write")
        sys.stdout.flush()
        time.sleep(20)


def __collect_urls(source):
    from random import randint
    for i in range(source.pages_k):
        res = requests.get(source.prod_url + "?page=" + str(i))
        soup = bs4.BeautifulSoup(res.content, "html.parser")
        elems = soup.find_all(class_=re.compile("^RowProductTiles"))
        for j in range(len(elems)):
            imgcs = elems[j].find_all(class_=re.compile("^ImageSection-module_imageSection"))
            for img in imgcs: URLS.put(img.find("a").get("href"))
            sys.stdout.write(f"\r[COLLECTD] {j}/{len(elems)} urls")
            sys.stdout.flush()
        sys.stdout.write(f"\r[COLLECTD] {i}/{source.pages_k} pages")
        sys.stdout.flush()
        time.sleep(randint(5, 10))
    PROC = False

# try:
#     for i in range(100):
#         sys.stdout.write(f"\rcollected: {i}/100")
#         sys.stdout.flush()
#         time.sleep(1)
# except KeyboardInterrupt: pass


# coins system (rubins)
    # collect them from watching an ad or other activities
    # unlock additional analyses, item price monitor
# lifetime pass
    # everything is available

if __name__ == "__main__":
    run_source("rossmann")