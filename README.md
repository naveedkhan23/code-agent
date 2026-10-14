# Simple Code Agent (Windows desktop app, DeepSeek V4 Pro)

A simplified, Claude-Code-style coding agent. Give it **Architecture_Documentation.md** and
**Architecture_View.md** (PlantUML / Mermaid UML) and it generates a complete project
(source, `requirements.txt`, `Dockerfile`, `README.md`, tests) in the output directory you choose.

* LLM: **`deepseek-v4-pro`** through the official API (`https://api.deepseek.com`, OpenAI-compatible, function calling). No local weights.
* Deliverable: single-file **`CodeAgent.exe`** (PyInstaller) - double-click, no Python needed on the target PC.
* GUI: API key, model/base URL, two input files, output directory, Run / Stop, live log.

## Using the app
1. Double-click `CodeAgent.exe`.
2. Paste your DeepSeek API key -> **Test connection**.
3. Select `Architecture_Documentation.md`, `Architecture_View.md` and an output folder
   (try `examples/` for a ready-made Tetris spec).
4. **Generate project**. Watch the plan (todo list), tool calls and results in the log. **Open output folder** when done.

The key is stored in `%APPDATA%\SimpleCodeAgent\config.json` (plain text, local only).

## Get the .exe
**Option A - GitHub Actions (no local setup):** push this repo to GitHub -> *Actions* -> *build-windows-exe* -> download the
`CodeAgent-windows-exe` artifact (tag `v1.0.0` to also attach it to a Release).

**Option B - on a Windows machine with Python 3.10+:** double-click `build_exe.bat` -> `dist\CodeAgent.exe`.

## How it works (mapping to Claude Code)
| Claude Code concept | Here |
|---|---|
| Query loop (model <-> tools until done) | `code_agent/agent.py` `CodeAgent.run` |
| Tool system (Read/Write/Edit/Bash/TodoWrite) | `code_agent/tools.py`: `read_file`, `write_file`, `edit_file`, `list_dir`, `check_syntax`, `run_tests`, `update_todos`, `finish` |
| Permission / sandbox | all paths resolved inside the output dir; escapes rejected |
| System prompt + workflow rules | `code_agent/prompts.py` (plan -> implement -> verify -> finish) |
| Context compaction | `compact()` shrinks old tool results / written file bodies when the conversation grows |
| Todo planning | `update_todos`, shown live in the GUI |
| Verification / stop hooks | `finish` is **rejected** until README, requirements, tests, Dockerfile, >=3 source files exist and all `.py`/`.json` parse |
| Error recovery | tool errors are returned to the model as results; API retries with backoff; bad JSON arguments are bounced back |

**Input preprocessing** (`code_agent/preprocess.py`): Markdown -> JSON. Documentation becomes a section tree with bullets,
tables, requirement sentences and tech mentions. Views become typed diagrams: class diagrams -> classes/members/relations,
sequence -> participants/messages, state/flow -> nodes/edges. The JSON is saved to `<output>/.agent/architecture.json`.
Raw diagram source is always kept, so unknown syntax is still visible to the model.

DeepSeek V4 thinking mode: `reasoning_content` of tool-call turns is sent back to the API as required.

## CLI / Docker (headless)
```
set DEEPSEEK_API_KEY=sk-...
python main.py --cli --doc examples\Architecture_Documentation.md --views examples\Architecture_View.md --out out
docker build -t simple-code-agent . && docker run -e DEEPSEEK_API_KEY=sk-... -v %cd%/examples:/in -v %cd%/out:/out simple-code-agent
```

## Tests
`pip install -r requirements-dev.txt && python -m pytest -q` - 17 tests: preprocessing, tools/sandbox/finish-gate,
the whole agent loop with a scripted fake LLM, and the HTTP client against a local fake DeepSeek server (no key needed).

## Limitations
* `run_tests` needs a Python on the user's machine; without it the agent falls back to `check_syntax` (the exe itself never needs Python).
* Output quality depends on the model; very large specs are truncated to ~120k chars per input.
* The generated app may need `pip install -r requirements.txt` on the machine where you run it.
