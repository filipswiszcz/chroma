from __future__ import annotations
import os, functools, contextlib, time, traceback
from typing import Any, ClassVar, TypeVar, Dict, Generic, MutableMapping, OrderedDict, Callable
from collections import defaultdict, deque, OrderedDict
from datetime import datetime
from psutil import cpu_percent, virtual_memory, disk_usage # temporary lib
from threading import Thread, Event, RLock


@functools.cache
def getenv(key, default=0): return type(default) (os.getenv(key, default))

def interval(seconds): time.sleep(seconds)

# *************** Watchdog ***************

class Watchdog:
    def __init__(self, callback=None) -> None:
        self._func_metrics, self._errors, self._sys_metrics, self.callback, self.shutdown = defaultdict(lambda: deque(maxlen=256)), deque(maxlen=256), deque(maxlen=16), callback, Event()
    def start(self) -> None: Thread(target=self.__read_sys_metrics, daemon=True).start()
    def stop(self) -> None: self.shutdown.set()
    def __read_sys_metrics(self) -> None:
        while not self.shutdown.is_set():
            self._sys_metrics.append({"timestamp": datetime.now(), "cpu": cpu_percent(), "mem": virtual_memory().percent, "disk": disk_usage("/").percent}), interval(SYS_INFO_INTERVAL.value)
    def monitor(self, function) -> "func":
        def wrapped(*args, **kwargs) -> "func":
            start = time.time()
            try:
                result = function(*args, **kwargs)
                duration = time.time() - start
                self._record_metric(function.__name__, duration, "success")
                return result
            except Exception as exc:
                duration = time.time() - start
                self._record_metric(function.__name__, duration, "error")
                self._record_error(function.__name__, exc)
                raise
        return wrapped
    def _record_metric(self, name: str, value: int, state: str) -> None:
        timestamp = datetime.now()
        self._func_metrics[name].append({"timestamp": timestamp, "value": value, "state": state})
        if value > 5 and self.callback: self.callback(f"Performance drop: {name} took {value:.2f}s", "performance")
    def _record_error(self, context: str, error: Any) -> None:
        error_data = {"context": context, "type": type(error).__name__, "message": str(error), "stack_trace": traceback.format_exc(), "timestamp": datetime.now()}
        self._errors.append(error_data)
        if self.callback: self.callback(f"Error in {context}: {str(error)}", "error")
    def get_sys_metrics(self) -> list: return list(self._sys_metrics)
    def get_func_metrics(self, name=None) -> list:
        if name: return list(self._func_metrics.get(name, []))
        return {k: list(v) for k, v in self._func_metrics.items()}

# structure
#   exec time
#       func exec duration
#       db query times
#   request err detection
#       http error codes
#   resource monitoring
#       mem usage
#       cpu util
#       disk i/o
#       network bandwidth

# *************** Context ***************

class Context(contextlib.ContextDecorator):
    def __init__(self, **kwargs) -> None:
        self.kwargs = kwargs
    def __enter__(self) -> None:
        self.old_context: dict = {k: v.value for k, v in ContextVar._cache.items()}
        for k, v in self.kwargs.items(): ContextVar._cache[k].value = v
    def __exit__(self, *args) -> None:
        for k, v in self.old_context.items(): ContextVar._cache[k].value = v

class ContextVar:
    _cache: ClassVar[dict[str, ContextVar]] = {}
    key: str
    value: int
    def __init__(self, key, default) -> None:
        if key in ContextVar._cache: raise RuntimeError(f"Attempt to recreate ContextVar {key}")
        ContextVar._cache[key] = self
        self.key, self.value = key, getenv(key, default)
    def __bool__(self) -> bool: return bool(self.value)
    def __ge__(self, other) -> bool: return self.value >= other
    def __gt__(self, other) -> bool: return self.value > other
    def __le__(self, other) -> bool: return self.value <= other
    def __lt__(self, other) -> bool: return self.value < other

DEBUG, CAPTURING = ContextVar("DEBUG", 0), ContextVar("CAPTURING", 1)
INSTANCES, WORKERS = ContextVar("INSTANCES", 1), ContextVar("WORKERS", 5)
HTTP_TIMEOUT, HTTP_RETRIES, HTTP_REDIRECTS = ContextVar("HTTP_TIMEOUT", 5), ContextVar("HTTP_RETRIES", 1), ContextVar("HTTP_REDIRECTS", 10)
SYS_INFO_INTERVAL = ContextVar("SYS_INFO_INTERVAL", 1)

# *************** Cache ***************

_KeyType = TypeVar("_KeyType")
_ValueType = TypeVar("_ValueType")
_DefaultType = TypeVar("_DefaultType")

class RecentlyUsedDict(Generic[_KeyType, _ValueType], MutableMapping[_KeyType, _ValueType]):
    _dict: OrderedDict[_KeyType, _ValueType]
    _maxsize: int
    lock: RLock
    def __init__(self, maxsize: int = 10, disposer: Callable[[_ValueType], None] | None = None) -> None:
        super().__init__()
        self._maxsize, self.disposer, self._dict, self.lock = maxsize, disposer, OrderedDict(), RLock()
    def __getitem__(self, key: _KeyType) -> _ValueType:
        with self.lock:
            item = self._dict.pop(key)
            self._dict[key] = item
            return item
    def __setitem__(self, key: _KeyType, value: _ValueType) -> None:
        evicted_item = None
        with self.lock:
            try:
                evicted_item = key, self._dict.pop(key)
                self._dict[key] = value
            except KeyError:
                self._dict[key] = value
                if len(self._dict) > self._maxsize: evicted_item = self._dict.popitem(last=False)
        if evicted_item is not None and self.disposer:
            _, evicted_value = evicted_item
            self.disposer(evicted_value)
    def __delitem__(self, key: _KeyType) -> None:
        with self.lock: value = self._dict.pop(key)
        if self.disposer: self.disposer(value)
    def __iter__(self) -> None:
        raise NotImplementationError("Unlikely to be thread safe")
    def __len__(self) -> int:
        with self.lock: return len(self._dict)
    def keys(self) -> set[_KeyType]:
        with self.lock: return set(self._dict.keys())
    def clear(self) -> None:
        with self.lock:
            values = list(self._dict.values())
            self._dict.clear()
        if self.disposer:
            for value in values:
                self.disposer(value)