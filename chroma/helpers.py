import contextlib
from typing import Any, ClassVar, Dict

# *************** Context ***************

class Context(contextlib.ContextDecorator):
    def __init__(self, **kwargs) -> None:
        self.kwargs = kwargs
    def __enter__(self) -> None:
        self.old_context: dict = {k: v.value for k, v in ContextVar._cache.items()}
        for k, v in self.kwargs.items():
            ContextVar._cache[k].value = v
    def __exit__(self, *args) -> None:
        for k, v in self.old_context.items():
            ContextVar._cache[k].value = v

class ContextVar:
    _cache: ClassVar[dict[str, "ContextVar"]] = {}
    def __init__(self, key, default_value) -> None:
        if key in ContextVar._cache:
            raise RuntimeError(f"attempt to recreate ContextVar {key}")
        ContextVar._cache[key] = self
        self.key, self.value = key, default_value
    def set(self, value) -> None:
        self.value = value
    def get(self) -> Any:
        return self.value
    def __bool__(self) -> bool:
        return bool(self.value)
    def __ge__(self, other) -> bool:
        return self.value >= other
    def __gt__(self, other) -> bool:
        return self.value > other
    def __le__(self, other) -> bool:
        return self.value <= other
    def __lt__(self, other) -> bool:
        return self.value < other

DEBUG = ContextVar("DEBUG", 0)

# *************** Cache ***************