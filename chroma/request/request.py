from urllib.request import Request, ProxyHandler, build_opener
from headers import Randomizer


RANDOMIZER = Randomizer()

def get(url: str) -> "response obj":
    handler = ProxyHandler(RANDOMIZER.get_proxies())
    opener = build_opener(handler)
    request = Request(url, headers=RANDOMIZER.get_headers()) # get_headers returns str