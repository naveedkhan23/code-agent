import pytest

from code_agent.tools import Workspace


@pytest.fixture
def ws(tmp_path):
    return Workspace(tmp_path)


def test_write_read_edit(ws):
    assert ws.call("write_file", {"path": "src/a.py", "content": "x = 1\ny = 2\n"}).startswith("OK")
    assert "2\ty = 2" in ws.call("read_file", {"path": "src/a.py"})
    assert ws.call("edit_file", {"path": "src/a.py", "old": "x = 1", "new": "x = 5"}).startswith("OK")
    assert "x = 5" in ws.call("read_file", {"path": "src/a.py"})
    assert "not found" in ws.call("edit_file", {"path": "src/a.py", "old": "zzz", "new": "q"})


def test_sandbox_blocks_escape(ws):
    assert "escapes" in ws.call("write_file", {"path": "../evil.txt", "content": "x"})
    assert "escapes" in ws.call("read_file", {"path": "/etc/passwd"})


def test_syntax_check(ws):
    ws.call("write_file", {"path": "bad.py", "content": "def f(:\n"})
    assert ws.call("check_syntax", {}).startswith("SYNTAX PROBLEMS")
    ws.call("write_file", {"path": "bad.py", "content": "def f():\n    pass\n"})
    assert ws.call("check_syntax", {}).startswith("OK")


def test_finish_gate_rejects_until_complete(ws):
    assert ws.call("finish", {"summary": "s"}).startswith("REJECTED")
    for p, c in {"a.py": "x=1", "b.py": "y=1", "c.py": "z=1", "README.md": "# r",
                 "requirements.txt": "", "Dockerfile": "FROM python:3.12",
                 "tests/test_a.py": "def test_a():\n    assert True\n"}.items():
        ws.call("write_file", {"path": p, "content": c})
    assert ws.call("finish", {"summary": "done"}).startswith("OK")
    assert ws.finished


def test_unknown_tool_and_bad_args(ws):
    assert "unknown tool" in ws.call("rm_rf", {})
    assert "bad arguments" in ws.call("write_file", {"oops": 1})


def test_run_tests(ws):
    ws.call("write_file", {"path": "tests/test_ok.py", "content": "def test_ok():\n    assert 1 + 1 == 2\n"})
    out = ws.call("run_tests", {})
    assert "exit code 0" in out or out.startswith("UNAVAILABLE")
