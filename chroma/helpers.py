from __future__ import annotations
import os, functools, contextlib
from typing import Any, ClassVar, Dict


@functools.cache
def getenv(key, default=0): return type(default) (os.getenv(key, default))

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