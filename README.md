# Simple Code Agent

A small **Windows desktop app** that works like a simple version of Claude Code.
You give it two Markdown files:

1. `Architecture_Documentation.md` - the written design of a system
2. `Architecture_View.md` - UML diagrams (PlantUML / Mermaid)

The agent reads them and writes a complete project into a folder you choose:
source code, tests, `requirements.txt`, `Dockerfile` and a `README.md`.

- **AI model:** `deepseek-v4-pro`, used through the official DeepSeek API
  (`https://api.deepseek.com`). No local model is needed.
- **App type:** a desktop window made with Python and Tkinter.
- **Windows .exe:** one file, no Python needed on the user's PC.

## Links

- **Download the .exe:** `https://github.com/naveedkhan23/code-agent/releases/download/v1.0.0/CodeAgent.exe`
- **Demo video:** `PASTE YOUR YOUTUBE LINK HERE`
- **Example output (Space Fractions game):** see the `output_example/` folder

## How to use the app

1. Double-click `CodeAgent.exe`.
2. Paste your DeepSeek API key and click **Test connection**.
   Leave "Model" as `deepseek-v4-pro` and "Base URL" as `https://api.deepseek.com`.
3. Choose your `Architecture_Documentation.md` and `Architecture_View.md`.
4. Choose an **empty** output folder.
5. Click **Generate project** and watch the log. Wait for `status=finished`.
6. Open the output folder. To run the generated game:
   ```
   pip install -r requirements.txt
   python main.py
   python -m pytest -q
   ```

Your API key is saved on your own PC in `%APPDATA%\SimpleCodeAgent\config.json`.
It is never stored in this repository.

Note: the DeepSeek API is prepaid. If you see `HTTP 402 Insufficient Balance`,
add credit on platform.deepseek.com.

## How it works

```
Input files  ->  Pre-processing  ->  Agent loop  <->  DeepSeek V4 Pro
                 (Markdown to JSON)       |
                                          v
                                  Tools write files into the output folder
```

1. **Pre-processing** (`code_agent/preprocess.py`)
   - The documentation becomes JSON: sections, tables, code blocks, requirement
     IDs (FR / NFR / ASR) and the traceability table.
   - The diagrams become JSON: classes and relations, sequence messages, state
     changes, use cases, packages, nodes. The raw diagram text is also kept.
   - The JSON is saved in `<output>/.agent/architecture.json`.
2. **Agent loop** (`code_agent/agent.py`)
   - We send the JSON and a system prompt to the model.
   - The model answers with tool calls. The program runs them and sends the
     results back. This repeats until the model calls `finish`.
3. **Tools** (`code_agent/tools.py`)

   | Tool | What it does |
   |---|---|
   | `write_file` | Create or replace a file |
   | `read_file` | Read a file |
   | `edit_file` | Change one exact piece of text in a file |
   | `list_dir` | Show the files in the output folder |
   | `check_syntax` | Check all `.py` and `.json` files for errors |
   | `run_tests` | Run the generated tests (needs Python on the PC) |
   | `update_todos` | Keep a visible to-do plan |
   | `finish` | End the run (only allowed when everything is ready) |

4. **Safety checks**
   - **Sandbox:** the agent can only write inside the output folder.
   - **Finish check:** the run is rejected until the project has a README,
     `requirements.txt`, tests, a Dockerfile, at least 3 source files, and no
     syntax errors.
   - **Context shrinking:** in long runs, old tool results are shortened so the
     conversation stays small.
   - **Retries:** if the API fails, the app tries again with a delay.
5. **Desktop rule:** the system prompt says the final product must be a
   desktop app. If the documentation describes a web or microservice design,
   the agent builds one desktop app instead, and keeps the design files
   (OpenAPI, proto, SQL, etc.) in `docs/`.

## Ideas taken from Claude Code

I studied public descriptions of how Claude Code works, including the
*How Claude Code Works* project. These are the main ideas I used, in a much
smaller form:

| Idea in Claude Code | What I did here |
|---|---|
| One main loop: call the model, run tools, repeat until the model stops asking for tools | `CodeAgent.run()` in `agent.py` |
| Tools share one simple format, and the model chooses which to call | `TOOL_SCHEMAS` and `Workspace.call()` in `tools.py` |
| The model plans with a to-do list | `update_todos`, shown live in the log |
| Permissions: the agent cannot do whatever it wants | Sandbox: paths must stay inside the output folder |
| The context window is limited, so old content is compressed | `compact()` shortens old tool results |
| Check the work before stopping | `finish` is rejected until all checks pass |

**Left out on purpose** (to keep the project small): sub-agents, MCP servers,
hooks, long-term memory, shell commands, and streaming output.

## Project layout

```
main.py                 start the app (GUI by default, --cli for no window)
code_agent/
  gui.py                Tkinter window
  agent.py              the agent loop
  llm.py                DeepSeek API client
  tools.py              tools and sandbox
  preprocess.py         Markdown to JSON
  prompts.py            system prompt and rules
  config.py             saves settings
tests/                  automatic tests
examples/               small sample inputs
build_exe.bat           builds the .exe
Dockerfile              run the agent without a window
```

## Run from source

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
python main.py
```

No window (command line):
```
set DEEPSEEK_API_KEY=your_key
python main.py --cli --doc Architecture_Documentation.md --views Architecture_View.md --out out
```

## Build the .exe

```
pip install requests pyinstaller
pyinstaller --onefile --windowed --name CodeAgent --collect-all certifi main.py
```
The file is created at `dist\CodeAgent.exe`. You can also run `build_exe.bat`.

## Tests

```
python -m pytest -q
```
The tests need no API key. They check the pre-processing, the tools and the
sandbox, the whole agent loop with a fake model, and the API client with a
fake local server.

## Known limits

- The quality of the generated project depends on the AI model. If a result
  has bugs, you can run the agent again.
- `run_tests` only works when Python is installed on the user's PC. Without
  it, the agent only checks syntax.
- Very large input files are cut to about 120,000 characters each.
- The generated game may need `pip install -r requirements.txt` before it runs.
