"""Entry point. Double-click (exe) -> GUI.  `--cli` -> headless run (used for tests / CI / Docker)."""
import argparse
import os
import sys


def cli(argv):
    from code_agent.agent import CodeAgent
    from code_agent.llm import DEFAULT_BASE_URL, DEFAULT_MODEL, DeepSeekClient
    ap = argparse.ArgumentParser(prog="CodeAgent --cli")
    ap.add_argument("--cli", action="store_true")
    ap.add_argument("--doc", required=True, help="Architecture_Documentation.md")
    ap.add_argument("--views", required=True, help="Architecture_View.md")
    ap.add_argument("--out", required=True, help="output directory")
    ap.add_argument("--api-key", default=os.environ.get("DEEPSEEK_API_KEY", ""))
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--base-url", default=DEFAULT_BASE_URL)
    ap.add_argument("--max-turns", type=int, default=80)
    a = ap.parse_args(argv)
    client = DeepSeekClient(a.api_key, a.model, a.base_url)
    res = CodeAgent(client, a.out, on_event=lambda k, t: print(f"[{k}] {t}", flush=True),
                    max_turns=a.max_turns).run(a.doc, a.views)
    print(res["status"], res["output_dir"])
    return 0 if res["status"] == "finished" else 1


if __name__ == "__main__":
    if "--cli" in sys.argv:
        sys.exit(cli(sys.argv[1:]))
    from code_agent.gui import main
    main()
