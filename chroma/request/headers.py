from enum import Enum
from random import choice, choices, randint
from queue import Queue
from time import sleep
from threading import Event, Lock
from typing import Iterator
from helpers import Context, DEBUG
from worker import _Worker

# *************** Exception ***************

class UserAgentException(Exception):
    """Raised when there is a problem with UserAgent"""

class ProxyException(Exception):
    """Raised when there is a problem with Proxy"""

# *************** Randomizer ***************

class Randomizer():
    def __init__(self) -> None:
        self.proxies, self.user_agent, self.referrers, self.shutdown = Queue(), UserAgent(), ["https://google.com/", "https://bing.com/", "https://l.facebook.com/", "https://www.reddit.com/", "https://old.reddit.com/", "https://youtube.com/"], Event()
    def start(self) -> None: _Worker(target=self.__get_idle_proxies).start()
    def stop(self) -> None: self.shutdown.set()
    def __get_idle_proxies(self) -> None:
        proxy = Proxy()
        proxy._check_address_state()
        while not self.shutdown.is_set(): # it will be better in future
            for address in proxy._get_available_addresses():
                if address not in list(self.proxies.queue): self.proxies.put(address)
            sleep(3)
    def get_proxies(self) -> dict:
        address = self.proxies.get(); address.state = _AddressState.ACTIVE
        return {"http": "http://" + address.label, "https": "https://" + address.label}
    def get_headers(self) -> str:
        return " ".join(f"{k}: {v}" for k, v in {"UserAgent": self.user_agent.get(), "Accept-Language": "en-US,en;q=0.9", "Referer": choice(self.referrers)}.items())

# *************** Agent ***************

class _Device:
    WIN10_x64 = "Windows NT 10.0"; WIN10_x32 = "Windows NT 10.0"; LINUX_x64 = "X11"; LINUX_x32 = "X11"; MAC = "Macintosh";

class UserAgent():
    def __init__(self) -> None:
        self._engines = {
            "Blink": {"token": "AppleWebKit/537.36 (KHTML, like Gecko)"},
            "Gecko": {"token": "Gecko/20100101"},
            "WebKit": {"token": "AppleWebKit/605.1.15 (KHTML, like Gecko)"}
        }
        self._browsers = {
            "Edge": {"platforms": [_Device.WIN10_x64], "suffixes": {_Device.WIN10_x64: "Win64; x64"}, "engine": "Blink", "version": "Chrome/135.0.0.0 Safari/537.36 Edg/135.0.3179.73"},
            "Safari": {"platforms": [_Device.MAC], "suffixes": {_Device.MAC: "Intel Mac OS X 10_15_7"}, "engine": "WebKit", "version": "Version/18.3.1 Safari/605.1.15"},
            "Chrome": {"platforms": [_Device.WIN10_x64, _Device.WIN10_x32, _Device.LINUX_x64, _Device.MAC], "suffixes": {_Device.WIN10_x64: "Win64; x64", _Device.WIN10_x32: "WOW64", _Device.LINUX_x64: "Linux x86_64", _Device.MAC: "Intel Mac OS X 10_15_7"}, "engine": "Blink", "version": "Chrome/137.0.0.0 Safari/537.36"},
            "Firefox": {"platforms": [_Device.WIN10_x64, _Device.LINUX_x64, _Device.LINUX_x32, _Device.MAC], "suffixes": {_Device.WIN10_x64: "Win64; x64; rv:137.0", _Device.LINUX_x64: "Linux x86_64; rv:137.0", _Device.LINUX_x32: "Linux i686; rv:137.0", _Device.MAC: "Intel Mac OS X 14.7; rv:137.0"}, "engine": "Gecko", "version": "Gecko/20100101 Firefox/137.0"}
        }
    def get(self) -> str:
        browser = self._browsers[choices(list(self._browsers.keys()), weights=[0.05, 0.2, 0.6, 0.15], k=1)[0]]
        platform = choice(browser["platforms"])
        parts = ["Mozilla/5.0", f"({platform}" + ")" if browser["suffixes"][platform] == "" else f"({platform}; {browser["suffixes"][platform]})", self._engines[browser["engine"]]["token"], browser["version"]]
        return " ".join(parts)

# *************** Proxy ***************

class _AddressState(Enum):
    INACTIVE = 0; IDLE = 1; ACTIVE = 2;

class _Address:
    def __init__(self, label, state=_AddressState.INACTIVE) -> None:
        self.label = label
        self.state = state

class Proxy:
    def __init__(self) -> None:
        self.addresses = []
        self.__load_items("resources/proxies.txt")
    def __load_items(self, filepath) -> None:
        with open(filepath, "r") as file:
            for line in file: self.addresses.append(_Address(line, _AddressState.INACTIVE))
    def _check_address_state(self) -> bool:
        # temporary check
        for address in self.addresses: address.state = _AddressState.IDLE
    def _add_address(self, address) -> None:
        pass # add address live. everything should be live all the time
    def _get_available_addresses(self) -> Iterator[_Address]:
        for address in self.addresses:
            if address.state == _AddressState.IDLE: yield address