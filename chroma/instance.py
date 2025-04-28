from enum import Enum, auto
from multiprocessing import Process, cpu_count
from typing import ClassVar
from worker import AtomicInteger, Dispatcher

# *************** Exception ***************

class InstanceException(Exception):
    """Raised when there is a problem with Instance"""

# *************** Ops ***************

class Ops(Enum):
    FETCH_PAGE_COUNT = auto(); FETCH_PROD_COUNT = auto();
    FETCH_PROD_URLS = auto(); FETCH_PROD_DATA = auto();
    PROCESS_PROD_DATA = auto(); SAVE_PROD_DATA = auto(); # saving in other thread???

# *************** Instance ***************

class _Instance(Process):
    INSTANCE_ID: ClassVar[AtomicInteger] = AtomicInteger()
    def __init__(self) -> None:
        super().__init__(name=f"Instance-{_Instance.INSTANCE_ID.get_and_increment()}", daemon=True)
        self._dispatcher = Dispatcher()

# instance with prod/page data fetch
# instance with prod analyze
# instance with api server

# data
# id-{first letter of type (uppercase)}
#
# priority:
# clearance:
#
# status:
# classification:

# SECURITY OVERRIDE  SYNCING
#
# {PRODUCTS} {NUMBER} LOG TRANSFER
# ------------------------------------------------
# |# UPLOAD COMPLETE ############################| 100%
# ------------------------------------------------

# http errors handle