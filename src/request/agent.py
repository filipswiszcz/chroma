from enum import Enum

# ********** Exception **********

class UserAgentException(Exception):
    """Raised when there is a problem with UserAgent"""

# ********** Agent **********

class _Device:
    MOBILE = 1; DESKTOP = 2

class UserAgent():
    def __init__(self) -> None:
        self._browsers = {"Chrome": _Device.DESKTOP, "Chrome Mobile": _Device.MOBILE, "Chrome Mobile iOS": _Device.MOBILE, "Edge": _Device.DESKTOP, "Edge Mobile": _Device.MOBILE, "Safari": _Device.DESKTOP, "Mobile Safari": _Device.MOBILE, "Mobile Safari UI/WKWebView": _Device.MOBILE, "Firefox": _Device.DESKTOP, "Firefox Mobile": _Device.MOBILE, "Firefox iOS": _Device.MOBILE, "Opera": _Device.DESKTOP}
        self._operating_systems = [""]