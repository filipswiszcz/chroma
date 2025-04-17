from enum import Enum
from random import choice, choices, randint

# ********** Exception **********

class UserAgentException(Exception):
    """Raised when there is a problem with UserAgent"""

# ********** Agent **********

class _Device:
    WIN10_X64 = "Windows NT 10.0; Win64; x64";  WIN10_ARM = "Windows NT 10.0; ARM64"; WIN7_X86 = "Windows NT 6.1; WOW64";
    MAC_INT = "Macintosh; Intel Mac OS X 10_15_7"; MAC_SIL = "Macintosh; ARM Mac OS X 10_15_7";
    UBUNTU_X64 = "X11; Ubuntu; Linux x86_64"; UBUNTU_ARM = "X11; Ubuntu; Linux aarch64";

class UserAgent():
    def __init__(self) -> None:
        self._engines = {
            "Blink": {"token": "AppleWebKit/537.36 (KHTML, like Gecko)"},
            "Gecko": {"token": "Gecko/20100101"},
            "WebKit": {"token": "AppleWebKit/605.1.15 (KHTML, like Gecko)"}
        }
        self._browsers = {
            "Chrome": {"token": "Chrome/{version}", "engine": "Blink", "platforms": [_Device.WIN10_X64, _Device.WIN10_ARM, _Device.UBUNTU_X64, _Device.UBUNTU_ARM], "versions": (120, 125)},
            "Firefox": {"token": "Firefox/{version}", "engine": "Gecko", "platforms": [_Device.WIN10_X64, _Device.WIN7_X86, _Device.MAC_INT, _Device.UBUNTU_X64], "versions": (115, 120)},
            "Safari": {"token": "Safari/{version}", "engine": "WebKit", "platforms": [_Device.MAC_INT, _Device.MAC_SIL], "versions": (605, 605)},
        }
    def get(self) -> str:
        browser = self._browsers[choices(list(self._browsers.keys()), weights=[0.7, 0.2, 0.1], k=1)[0]]
        parts = ["Mozilla/5.0", f"({choice(browser["platforms"])})", self._engines[browser["engine"]]["token"], browser["token"].format(version=f"{randint(*browser["versions"])}.0.0.0")]
        if browser["engine"] == "Blink": parts.append("Safari/537.36")
        return " ".join(parts)

# windows
    # edge
        # Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.3179.73
    # internet explorer
        # Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko
    # chrome
        # Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36
        # Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36
    # firefox
        # Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:137.0) Gecko/20100101 Firefox/137.0
# linux
    # chrome
        # Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36
    # firefox
        # Mozilla/5.0 (X11; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0
        # Mozilla/5.0 (X11; Linux i686; rv:137.0) Gecko/20100101 Firefox/137.0
# macos
    # safari
        # Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.3 Safari/605.1.15
    # chrome
        # Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36
    # firefox
        # Mozilla/5.0 (Macintosh; Intel Mac OS X 14.7; rv:137.0) Gecko/20100101 Firefox/137.0