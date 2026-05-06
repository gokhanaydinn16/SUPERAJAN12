from __future__ import annotations

from pathlib import Path

from pytest import _runner


def test_runner_supports_scoped_and_yield_fixtures(tmp_path, monkeypatch) -> None:
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    events_path = tmp_path / "events.log"

    (tests_dir / "conftest.py").write_text(
        "\n".join(
            [
                "from pathlib import Path",
                "import pytest",
                "",
                f"EVENTS = Path({str(events_path)!r})",
                "",
                "def record(value: str) -> None:",
                "    with EVENTS.open('a', encoding='utf-8') as handle:",
                "        handle.write(value + '\\n')",
                "",
                "@pytest.fixture(scope='session')",
                "def shared_session_fixture():",
                "    record('session_setup')",
                "    yield 'session-token'",
                "    record('session_teardown')",
            ]
        ),
        encoding="utf-8",
    )
    (tests_dir / "test_alpha.py").write_text(
        "\n".join(
            [
                "from pathlib import Path",
                "import os",
                "import pytest",
                "",
                f"EVENTS = Path({str(events_path)!r})",
                "",
                "def record(value: str) -> None:",
                "    with EVENTS.open('a', encoding='utf-8') as handle:",
                "        handle.write(value + '\\n')",
                "",
                "@pytest.fixture(scope='module')",
                "def shared_module_fixture():",
                "    record('module_setup')",
                "    yield 'module-token'",
                "    record('module_teardown')",
                "",
                "@pytest.fixture()",
                "def function_fixture(monkeypatch, tmp_path):",
                "    record('function_setup')",
                "    monkeypatch.setenv('RUNNER_TMP', tmp_path.name)",
                "    yield tmp_path.name",
                "    record('function_teardown')",
                "",
                "def test_first(shared_session_fixture, shared_module_fixture, function_fixture):",
                "    record('test_first')",
                "    assert shared_session_fixture == 'session-token'",
                "    assert shared_module_fixture == 'module-token'",
                "    assert os.environ['RUNNER_TMP'] == function_fixture",
                "",
                "def test_second(shared_session_fixture, shared_module_fixture):",
                "    record('test_second')",
                "    assert shared_session_fixture == 'session-token'",
                "    assert shared_module_fixture == 'module-token'",
                "    assert 'RUNNER_TMP' not in os.environ",
            ]
        ),
        encoding="utf-8",
    )
    (tests_dir / "test_beta.py").write_text(
        "\n".join(
            [
                "from pathlib import Path",
                f"EVENTS = Path({str(events_path)!r})",
                "",
                "def record(value: str) -> None:",
                "    with EVENTS.open('a', encoding='utf-8') as handle:",
                "        handle.write(value + '\\n')",
                "",
                "def test_third(shared_session_fixture):",
                "    record('test_third')",
                "    assert shared_session_fixture == 'session-token'",
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.chdir(tmp_path)
    result = _runner.main()

    assert result == 0
    events = events_path.read_text(encoding="utf-8").splitlines()
    assert events == [
        "session_setup",
        "module_setup",
        "function_setup",
        "test_first",
        "function_teardown",
        "test_second",
        "module_teardown",
        "test_third",
        "session_teardown",
    ]
