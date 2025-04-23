from queue import Queue
from threading import Thread , Lock as TLock
from multiprocessing import Lock as PLock
from ctypes import c_int
from typing import Union, ClassVar
from helpers import Context, WORKERS

# *************** Exception ***************

class DispatcherException(Exception):
    """Raised when there is problem with Dispatcher"""

# *************** Dispatcher ***************

class Dispatcher:
    def __init__(self) -> None:
        self._workers, self.tasks = [], Queue()
        for _ in range(WORKERS):
            self._workers.append(_Worker(daemon=True))

# *************** Atomic ***************

LockType = Union[TLock, PLock]

class AtomicInteger:
    def __init__(self, default=0, multiprocessing=False) -> None:
        self._value, self.__lock = c_int(default), TLock() if not multiprocessing else PLock()
    def get_and_increment(self) -> int:
        while True:
            current = self._value
            if self.__compare_and_set(current.value, current.value + 1): return current.value
    def __compare_and_set(self, expected, updated) -> bool:
        with self.__lock:
            if self._value.value == expected:
                self._value.value = updated; return True
            return False
    def __enter__(self): return self
    def __exit__(self) -> None:
        if hasattr(self.__lock, "close"): self.__lock.close()
        return None

# *************** Worker ***************

class _Worker(Thread):
    WORKER_ID: ClassVar[AtomicInteger] = AtomicInteger()
    def __init__(self) -> None:
        super().__init__(name=f"Worker-{_Worker.WORKER_ID.get_and_increment()}", daemon=True)