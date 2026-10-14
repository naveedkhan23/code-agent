"""End-to-end agent test with a scripted fake LLM (no network / no API key needed)."""
import json
from pathlib import Path

from code_agent.agent import CodeAgent, compact

EX = Path(__file__).parent.parent / "examples"


def call(i, name, **args):
    return {"id": f"c{i}", "type": "function", "function": {"name": name, "arguments": json.dumps(args)}}


class FakeLLM:
    usage = {"prompt_tokens": 1, "completion_tokens": 1}

    def __init__(self, script):
        self.script, self.i, self.seen = script, 0, []

    def chat(self, messages, tools=None, max_tokens=0):
        self.seen.append(len(messages))
        m = self.script[min(self.i, len(self.script) - 1)]
        self.i += 1
        return m


def test_full_run_with_gate(tmp_path):
    files = {"main.py": "print('hi')\n", "game.py": "x = 1\n", "ui.py": "y = 2\n",
             "README.md": "# Game\n", "requirements.txt": "\n", "Dockerfile": "FROM python:3.12\n",
             "tests/test_game.py": "def test_x():\n    assert True\n"}
    script = [{"content": "plan", "tool_calls": [call(0, "update_todos", todos=[{"task": "t", "status": "pending"}])]},
              {"content": "", "tool_calls": [call(1, "finish", summary="too early")]},  # gate must reject
              {"content": "", "reasoning_content": "thinking", "tool_calls": [
                  call(10 + i, "write_file", path=p, content=c) for i, (p, c) in enumerate(files.items())]},
              {"content": "", "tool_calls": [call(2, "check_syntax"), call(3, "finish", summary="done")]}]
    events = []
    llm = FakeLLM(script)
    res = CodeAgent(llm, str(tmp_path / "out"), on_event=lambda k, t: events.append((k, t))).run(
        str(EX / "Architecture_Documentation.md"), str(EX / "Architecture_View.md"))
    assert res["status"] == "finished" and res["missing"] == []
    assert (tmp_path / "out" / "tests" / "test_game.py").is_file()
    assert (tmp_path / "out" / ".agent" / "architecture.json").is_file()
    assert any("REJECTED" in t for k, t in events if k == "result")


def test_stall_and_max_turns(tmp_path):
    llm = FakeLLM([{"content": "thinking only"}])
    res = CodeAgent(llm, str(tmp_path), max_turns=10).run(str(EX / "Architecture_Documentation.md"),
                                                          str(EX / "Architecture_View.md"))
    assert res["status"] == "stalled"


def test_compaction_shrinks_old_output():
    msgs = [{"role": "system", "content": "s"}, {"role": "user", "content": "u"}]
    for i in range(20):
        msgs.append({"role": "assistant", "content": "", "tool_calls": [call(i, "write_file", path="a", content="x" * 1000)]})
        msgs.append({"role": "tool", "tool_call_id": f"c{i}", "content": "y" * 1000})
    assert compact(msgs) > 10000
    assert "compacted" in msgs[3]["content"]
