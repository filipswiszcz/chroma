from queue import Queue
from threading import Thread
from helpers import Context, WORKERS

# *************** Exception ***************

class DispatcherException(Exception):
    """Raised when there is problem with Dispatcher"""

# *************** Dispatcher ***************

class Dispatcher:
    def __init__(self) -> None:
        self.tasks = Queue()
        self._workers = []
    def start_workers(self) -> None:
        pass