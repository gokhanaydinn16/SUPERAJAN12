from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Callable


class _Mark:
    def asyncio(self, func):
        return func


def fixture(func: Callable[..., Any] | None = None, *, scope: str = "function"):
    if func is None:
        return lambda inner: fixture(inner, scope=scope)
    setattr(func, "_pytest_fixture", {"scope": scope})
    return func


mark = _Mark()


@contextmanager
def raises(expected_exception):
    try:
        yield
    except expected_exception:
        return
    except Exception as exc:
        raise AssertionError(f"Expected {expected_exception.__name__}, got {type(exc).__name__}") from exc
    raise AssertionError(f"Expected {expected_exception.__name__} to be raised")
