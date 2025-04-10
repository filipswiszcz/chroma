import sys
import re
import time

import requests
import fake_useragent as fu
import bs4


class Randomizer():
    def __init__(self):
        self.__referers = self.__init_referers()

    def __init_referers(self):
        return [
            "https://www.google.com",
            "https://www.yahoo.com",
            "https://www.bing.com",
            "https://youtube.com"
        ]

    def get_referer(self):
        from random import randint
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
source = Source(
    "rossmann",
    "https://www.rossmann.pl",
    "https://www.rossmann.pl/kategoria/makijaz-i-paznokcie,12000",
    7487, # find those on website
    312
)

# ?page=

agent = fu.UserAgent(os="Ubuntu")

headers = {
    "User-agent": agent.random,
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/"
}
response = requests.get(source.prod_url, headers=headers)
soup = bs4.BeautifulSoup(response.content, "html.parser")
# product = re.search('<div class="RowProductTiles[^"]*".*?</div>', response.text)
elems = soup.find_all(class_=re.compile("^RowProductTiles"))
urls = []
for e in elems:
    imgcs = e.find_all(class_=re.compile("^ImageSection-module_imageSection"))
    for i in imgcs:
        urls.append(i.find("a").get("href"))

# print(urls)


def init_source(brand):
    match brand:
        case "rossmann":
            products, pages = __get_source_details("https://rossmann.pl/kategoria/makijaz-i-paznokcie,12000")
            print(products, pages)
        case _:
            pass


def __get_source_details(url):
    headers = {
        "User-agent": agent.random,
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": rand.get_referer()
    }
    res = requests.get(url, headers=headers)
    soup = bs4.BeautifulSoup(res.content, "html.parser")
    products = soup.find(class_=re.compile("^styles-module_productListCount")).text
    pages = soup.find(class_=re.compile("^pages layout-2024")).find("span").text
    return products, pages


def get_urls():
    for _ in range(source.prod_k):
        continue

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
    init_source("rossmann")