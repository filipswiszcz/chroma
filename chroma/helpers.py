from __future__ import annotations
import os, functools, contextlib, time, traceback
from typing import Any, ClassVar, Dict
from collections import defaultdict, deque
from datetime import datetime
from psutil import cpu_percent, virtual_memory, disk_usage # temporary lib
from threading import Thread, Event


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
HTTP_TIMEOUT, HTTP_RETRIES, HTTP_REDIRECTS = ContextVar("HTTP_TIMEOUT", 5), ContextVar("HTTP_RETRIES", 1), ContextVar("HTTP_REDIRECTS", 3)
SYS_INFO_INTERVAL = ContextVar("SYS_INFO_INTERVAL", 1)

# *************** Cache ***************