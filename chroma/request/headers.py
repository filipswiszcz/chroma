from enum import Enum
from random import choice, choices, randint
from queue import Queue
from threading import Thread # other class should handle this
from typing import Iterator

# *************** Exception ***************

class UserAgentException(Exception):
    """Raised when there is a problem with UserAgent"""

class ProxyException(Exception):
    """Raised when there is a problem with Proxy"""

# *************** Randomizer ***************

class Randomizer():
    def __init(self) -> None:
        self.user_agents, self.proxies, self.referers = Queue(), Queue(), Queue()
    def run() -> None:
        Thread(target=__write_user_agents).start()
    def __write_user_agents(self) -> None:
        user_agent = UserAgent()
        while True:
            if len(self.user_agents) < 10: self.user_agents.put(user_agent.get())
    def get_header(self) -> str: # use contextvar
        return {"UserAgent": self.user_agents.get(), "Accept-Language": "en-US,en;q=0.9", "Referer": self.referers.get()}

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
            for line in file:
                parts = line.split(" ")
                self.addresses.append(_Address(parts[0], parts[1].upper()))
    def _check_address_state(self) -> bool:
        pass
    def _add_address(self, address) -> None:
        pass # add address live. everything should be live all the time
    def _get_available_addresses(self) -> Iterator[str]:
        for address in self.addresses:
            if address.state == _AddressState.IDLE: yield address.label

# *************** Referer ***************

class Referer:
    def __init__(self) -> None:
        self._hosts = ["https://google.com", "https://youtube.com", "https://yahoo.com", "https://bing.com"]
    def __collect_random_urls(self) -> None: pass
    def get_url(self) -> str:
        return choice(self._hosts)