from urllib.request import Request, ProxyHandler, build_opener
from headers import Randomizer

# *************** Pool ***************

class _HTTPConnectionPool(__ConnectionPool):
    def __init__(self, host: str, port: int = None, timeout: int = 5, maxsize: int = 1,
        headers: str = None, retries: int = None) -> None:
            pass

# _HTTPSConnectionPool

class __ConnectionPool:
    def __init__(self, host: str, port: int = None) -> None:
        pass


RANDOMIZER = Randomizer()

def get(url: str) -> "response obj":
    handler = ProxyHandler(RANDOMIZER.get_proxies())
    opener = build_opener(handler)
    request = Request(url, headers=RANDOMIZER.get_headers()) # get_headers returns str
    try: response = opener.open(request)
    except: pass