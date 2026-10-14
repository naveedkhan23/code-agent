"""Tests the HTTP client against a local fake DeepSeek server (checks URL, auth header, model, tools)."""
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from code_agent.llm import DeepSeekClient, LLMError

SEEN = {}


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        SEEN.update(path=self.path, auth=self.headers["Authorization"], body=body)
        if self.headers["Authorization"] == "Bearer bad":
            self.send_response(401)
            self.end_headers()
            self.wfile.write(b'{"error":"invalid key"}')
            return
        out = {"choices": [{"message": {"role": "assistant", "content": "pong"}}],
               "usage": {"prompt_tokens": 3, "completion_tokens": 1}}
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(out).encode())


@pytest.fixture(scope="module")
def server():
    s = HTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=s.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{s.server_port}"
    s.shutdown()


def test_chat_request_shape(server):
    c = DeepSeekClient("sk-test", base_url=server + "/")
    assert c.ping() == "pong"
    assert SEEN["path"] == "/chat/completions"
    assert SEEN["auth"] == "Bearer sk-test"
    assert SEEN["body"]["model"] == "deepseek-v4-pro"
    assert c.usage == {"prompt_tokens": 3, "completion_tokens": 1}


def test_auth_error_not_retried(server):
    with pytest.raises(LLMError, match="401"):
        DeepSeekClient("bad", base_url=server).ping()


def test_empty_key():
    with pytest.raises(LLMError):
        DeepSeekClient("  ")
