from __future__ import annotations
from queue import Queue, Empty
from threading import Thread, Lock as TLock, Event
from multiprocessing import Lock as PLock
from ctypes import c_int
from typing import Union, ClassVar
from helpers import Context, WORKERS

# *************** Exception ***************

class DispatcherException(Exception):
    """Raised when there is a problem with Dispatcher"""

# *************** Dispatcher ***************

class Dispatcher:
    def __init__(self) -> None:
        self._workers, self.ops, self.shutdown = [], Queue(), Event()
        for _ in range(WORKERS.value):
            self._workers.append(_Worker())
    def start(self) -> None:
        for worker in self._workers: worker.start()
        _Worker(target=self.__runnable).start()
    def __runnable(self) -> None:
        while not self.shutdown.is_set():
            try:
                op = self.ops.get(timeout=0.1)
                worker = self.__find_worker()
                # find worker, send op
            except Empty: continue
    def stop(self) -> None:
        for worker in self._workers: worker.join()
        self.shutdown.set()
    def __find_worker(self) -> _Worker:
        for worker in self._workers:
            if not worker.is_busy(): return worker
    def submit(self, op) -> None:
        if self.shutdown.is_set():
            raise RuntimeError("Dispatcher is offline")
        self.tasks.put(op) # operation (type, data)
        
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
    def __enter__(self) -> AtomicInteger: return self
    def __exit__(self) -> None:
        if hasattr(self.__lock, "close"): self.__lock.close()
        return None

# *************** Worker ***************

class _Worker(Thread):
    WORKER_ID: ClassVar[AtomicInteger] = AtomicInteger()
    def __init__(self, target=None) -> None:
        super().__init__(name=f"Worker-{_Worker.WORKER_ID.get_and_increment()}", target=target, daemon=True)
        self.is_busy = Event()