import os
import sys
import re
import time

import requests
import fake_useragent as fu
import bs4
import queue as q
import threading as t
import csv


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


rand = Randomizer()

# if result is None, then insert empty row with id

URLS = q.Queue()
PRODUCTS = q.Queue()
URLS_PROC, PROD_PROC = t.Event(), t.Event()

PROD_ID = 1

def run_collector(brands):
    procth = t.Thread(target=__proc_urls_que)
    procth.start()
    for b in brands:
        match b:
            case "rossmann":
                details = __get_source_details("https://rossmann.pl/kategoria/makijaz-i-paznokcie,12000")
                source = Source(
                    "rossmann", "https://rossmann.pl",
                    "https://rossmann.pl/kategoria/makijaz-i-paznokcie,12000",
                    int(details[0][:-10]), int(details[1])
                )
                __collect_urls(source)
            case _:
                pass


def __proc_urls_que():
    cdir = os.path.dirname(__file__)
    while not URLS_PROC.is_set():
        with open(os.path.join(cdir, "resources/urls.txt"), "a") as f:
            for i in range(URLS.qsize()): f.write(URLS.get() + "\n")
        time.sleep(20)


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


def __collect_urls(source):
    from random import randint
    headers = {
        "User-agent": rand.get_user_agent(),
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": rand.get_referer()
    }
    for i in range(source.pages_k):
        res = requests.get(source.prod_url + "?page=" + str(i), headers=headers, proxies=rand.get_proxies())
        soup = bs4.BeautifulSoup(res.content, "html.parser")
        elems = soup.find_all(class_=re.compile("^RowProductTiles"))
        for j in range(len(elems)):
            imgcs = elems[j].find_all(class_=re.compile("^ImageSection-module_imageSection"))
            for img in imgcs: URLS.put(source.base_url + img.find("a").get("href"))
            sys.stdout.write(f"\r\033[K")
            sys.stdout.write(f"\r(script) {j + 1}/{len(elems)} url")
            sys.stdout.flush()
        sys.stdout.write(f"\r\033[K")
        sys.stdout.write(f"\r(script) {i + 1}/{source.pages_k} page")
        sys.stdout.flush()
        time.sleep(randint(5, 10))
    while URLS.qsize() != 0: continue;
    URLS_PROC.set()
    sys.stdout.write(f"\r(script) urls read completed")
    sys.stdout.flush()


def run_proc():
    procth = t.Thread(target=__proc_prod_que)
    procth.start()
    __proc_prod()


def __proc_prod_que():
    cdir = os.path.dirname(__file__)
    while not PROD_PROC.is_set():
        with open(os.path.join(cdir, "resources/products.csv"), "a", newline="") as f:
            writer = csv.writer(f, delimiter=";")
            for i in range(PRODUCTS.qsize()): writer.writerow(PRODUCTS.get())
        time.sleep(10)


def __proc_prod():
    from random import randint
    cdir = os.path.dirname(__file__)
    prod_k = __get_products_k()
    k, d = prod_k // 10, prod_k % 10
    for i in range(k + 1):
        sys.stdout.write(f"\r\033[K")
        sys.stdout.write(f"\r(script) {i + 1}/{k + 1} operation")
        sys.stdout.flush()
        with open(os.path.join(cdir, "resources/urls.txt"), "r") as f:
            for j, ln in enumerate(f):
                if i == k and j >= i * 10:
                    __collect_prod(ln)
                    time.sleep(randint(5, 10))
                else:
                    if j < i * 10 or j >= (i * 10) + 10: continue
                    __collect_prod(ln)
                    time.sleep(randint(5, 10))
    while PRODUCTS.qsize() != 0: continue
    PROD_PROC.set()
    sys.stdout.write(f"\r(script) prod read completed")
    sys.stdout.flush()


def __get_products_k():
    cdir = os.path.dirname(__file__)
    with open(os.path.join(cdir, "resources/urls.txt"), "r") as f:
        return sum(1 for _ in f)


def __collect_prod(url):
    headers = {
        "User-agent": rand.get_user_agent(),
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": rand.get_referer()
    }
    res = requests.get(url, headers=headers, proxies=rand.get_proxies())
    soup = bs4.BeautifulSoup(res.content, "html.parser")
    global PROD_ID
    info = str(PROD_ID)
    title = soup.find(class_=re.compile("^styles-module_titleBrand")).text
    elems = soup.find_all(class_=re.compile("^styles-module_productDescriptionContent"))
    PRODUCTS.put([PROD_ID, elems[2].text[(elems[2].text.find("EAN") + 3):], title, url.split("/")[4], elems[0].text, elems[1].text])
    PROD_ID += 1


# coins system (rubins)
    # collect them from watching an ad or other activities
    # unlock additional analyses, item price monitor
# lifetime pass
    # everything is available

if __name__ == "__main__":
    match len(sys.argv):
        case 1:
            try:
                run_proc()
            except KeyboardInterrupt: pass
        case 2:
            if sys.argv[1] != "--collect-urls":
                print(f"script: usage: python3 collectd.py [--collect-urls]")
            else:
                try:
                    brands = ["rossmann", "hebe"]
                    run_collector(brands)
                    run_proc()
                except KeyboardInterrupt: pass
        case _:
            print(f"script: usage: python3 collectd.py [--collect-urls]")