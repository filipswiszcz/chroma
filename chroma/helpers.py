from __future__ import annotations
import os, functools, contextlib, time, datetime, traceback
from typing import Any, ClassVar, Dict
from collections import defaultdict, deque


@functools.cache
def getenv(key, default=0): return type(default) (os.getenv(key, default))

# *************** Watchdog ***************

class Watchdog:
    def __init__(self) -> None:
        self._metrics = defaultdict(lambda: deque(maxlen=256))
        self._errors = deque(maxlen=256)
        self.alert = None
    def monitor(self, function) -> "func":
        def wrapped(*args, **kwargs) -> "func":
            start = time.time()
            try:
                result = function(*args, **kwargs)
                duration = time.time() - start
                self._record_metric(function.__name__, duration, "success")
                return result
            except Exception:
                duration = time.time() - start
        return wrapped
    def _record_metric(self, name: str, value: int, state: str) -> None:
        timestamp = datetime.datetime.now()
        self._metrics[name].append({"timestamp": timestamp, "value": value, "state": state})
        if value > 5 and self.alert: self.alert(f"Performance drop: {name} took {value:.2f}s", "performance")
    def _record_error(self, context: str, error: Any) -> None:
        error_data = {"context": context, "type": type(error).__name__, "message": str(error), "stack_trace": traceback.format_exc(), "timestamp": datetime.datetime.now()}
        self._errors.append(error_data)
        if self.alert: self.alert(f"Error in {context}: {str(error)}", "error", error_data)

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

DEBUG, INSTANCES, WORKERS = ContextVar("DEBUG", 0), ContextVar("INSTANCES", 1), ContextVar("WORKERS", 5)

# *************** Cache ***************