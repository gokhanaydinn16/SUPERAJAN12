from __future__ import annotations

import asyncio
import importlib.util
import inspect
import os
import sys
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from tempfile import TemporaryDirectory
from types import GeneratorType
from typing import Any


@dataclass
class _FixtureDef:
    name: str
    scope: str
    func: Any


@dataclass
class _ScopeState:
    cache: dict[str, Any] = field(default_factory=dict)
    finalizers: list[Any] = field(default_factory=list)


def main() -> int:
    root = Path.cwd() / "tests"
    quiet = "-q" in sys.argv[1:]
    failures: list[tuple[str, BaseException]] = []
    count = 0
    session_state = _ScopeState()
    conftest_module = _load_optional_module(root / "conftest.py", module_name="tests.conftest")
    conftest_fixtures = _collect_fixture_defs(conftest_module) if conftest_module is not None else {}

    try:
        for path in sorted(root.glob("test_*.py")):
            module = _load_module(path)
            fixture_defs = {**conftest_fixtures, **_collect_fixture_defs(module)}
            module_state = _ScopeState()
            try:
                for name in sorted(dir(module)):
                    if not name.startswith("test_"):
                        continue
                    candidate = getattr(module, name)
                    if not callable(candidate):
                        continue
                    count += 1
                    function_state = _ScopeState()
                    fixtures = _build_fixtures(
                        candidate,
                        fixture_defs=fixture_defs,
                        session_state=session_state,
                        module_state=module_state,
                        function_state=function_state,
                    )
                    try:
                        if inspect.iscoroutinefunction(candidate):
                            asyncio.run(candidate(**fixtures))
                        else:
                            candidate(**fixtures)
                    except BaseException as exc:
                        failures.append((f"{path.name}::{name}", exc))
                        if not quiet:
                            traceback.print_exc()
                    finally:
                        _teardown_scope(function_state)
            finally:
                _teardown_scope(module_state)
    finally:
        _teardown_scope(session_state)

    if failures:
        for label, exc in failures:
            print(f"FAILED {label}: {exc}")
        print(f"{len(failures)} failed, {count - len(failures)} passed")
        return 1

    print(f"{count} passed")
    return 0


def _load_optional_module(path: Path, *, module_name: str):
    if not path.exists():
        return None
    return _load_module(path, module_name=module_name)


def _load_module(path: Path, *, module_name: str | None = None):
    resolved_name = module_name or f"tests.{path.stem}"
    spec = importlib.util.spec_from_file_location(resolved_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _collect_fixture_defs(module) -> dict[str, _FixtureDef]:
    fixtures: dict[str, _FixtureDef] = {}
    if module is None:
        return fixtures
    for name in dir(module):
        candidate = getattr(module, name)
        metadata = getattr(candidate, "_pytest_fixture", None)
        if metadata is None:
            continue
        fixtures[name] = _FixtureDef(name=name, scope=str(metadata.get("scope") or "function"), func=candidate)
    return fixtures


def _build_fixtures(
    func,
    *,
    fixture_defs: dict[str, _FixtureDef],
    session_state: _ScopeState,
    module_state: _ScopeState,
    function_state: _ScopeState,
) -> dict[str, object]:
    fixtures: dict[str, object] = {}
    for name in inspect.signature(func).parameters:
        fixtures[name] = _resolve_fixture(
            name,
            fixture_defs=fixture_defs,
            session_state=session_state,
            module_state=module_state,
            function_state=function_state,
        )
    return fixtures


def _resolve_fixture(
    name: str,
    *,
    fixture_defs: dict[str, _FixtureDef],
    session_state: _ScopeState,
    module_state: _ScopeState,
    function_state: _ScopeState,
) -> object:
    builtin_value = _build_builtin_fixture(name, function_state=function_state)
    if builtin_value is not None:
        return builtin_value

    fixture_def = fixture_defs.get(name)
    if fixture_def is None:
        raise TypeError(f"Unknown fixture: {name}")

    scope_state = _scope_state_for(
        fixture_def.scope,
        session_state=session_state,
        module_state=module_state,
        function_state=function_state,
    )
    if name in scope_state.cache:
        return scope_state.cache[name]

    dependencies = {
        dep_name: _resolve_fixture(
            dep_name,
            fixture_defs=fixture_defs,
            session_state=session_state,
            module_state=module_state,
            function_state=function_state,
        )
        for dep_name in inspect.signature(fixture_def.func).parameters
    }
    value = _invoke_fixture(fixture_def.func, dependencies, scope_state)
    scope_state.cache[name] = value
    return value


def _build_builtin_fixture(name: str, *, function_state: _ScopeState) -> object | None:
    if name == "tmp_path":
        tempdir = TemporaryDirectory()
        function_state.finalizers.append(tempdir.cleanup)
        return Path(tempdir.name)
    if name == "monkeypatch":
        monkeypatch = _MonkeyPatch()
        function_state.finalizers.append(monkeypatch.undo)
        return monkeypatch
    return None


def _invoke_fixture(func, dependencies: dict[str, Any], scope_state: _ScopeState) -> Any:
    if inspect.isasyncgenfunction(func):
        async_gen = func(**dependencies)
        value = asyncio.run(async_gen.__anext__())

        def finalize_async_gen() -> None:
            try:
                asyncio.run(async_gen.__anext__())
            except StopAsyncIteration:
                return
            raise RuntimeError(f"Async fixture {func.__name__} yielded more than once")

        scope_state.finalizers.append(finalize_async_gen)
        return value

    result = func(**dependencies)
    if inspect.isawaitable(result):
        return asyncio.run(result)
    if isinstance(result, GeneratorType):
        value = next(result)

        def finalize_generator() -> None:
            try:
                next(result)
            except StopIteration:
                return
            raise RuntimeError(f"Fixture {func.__name__} yielded more than once")

        scope_state.finalizers.append(finalize_generator)
        return value
    return result


def _scope_state_for(
    scope: str,
    *,
    session_state: _ScopeState,
    module_state: _ScopeState,
    function_state: _ScopeState,
) -> _ScopeState:
    if scope == "function":
        return function_state
    if scope == "module":
        return module_state
    if scope == "session":
        return session_state
    raise TypeError(f"Unsupported fixture scope: {scope}")


def _teardown_scope(scope_state: _ScopeState) -> None:
    errors: list[BaseException] = []
    while scope_state.finalizers:
        finalizer = scope_state.finalizers.pop()
        try:
            finalizer()
        except BaseException as exc:  # noqa: BLE001
            errors.append(exc)
    scope_state.cache.clear()
    if errors:
        raise errors[0]


class _MonkeyPatch:
    def __init__(self) -> None:
        self._env_changes: list[tuple[str, str | None, bool]] = []
        self._cwd_changes: list[Path] = []

    def setenv(self, name: str, value: str) -> None:
        existed = name in os.environ
        previous = os.environ.get(name)
        self._env_changes.append((name, previous, existed))
        os.environ[name] = value

    def chdir(self, path: Path | str) -> None:
        self._cwd_changes.append(Path.cwd())
        os.chdir(path)

    def undo(self) -> None:
        while self._cwd_changes:
            os.chdir(self._cwd_changes.pop())
        while self._env_changes:
            name, previous, existed = self._env_changes.pop()
            if existed:
                assert previous is not None
                os.environ[name] = previous
            else:
                os.environ.pop(name, None)
