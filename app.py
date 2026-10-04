"""Differentiation step-checker: local web app (Python standard library only).

Run:  python app.py      then open http://localhost:8000
Needs Ollama running with gemma4:e2b pulled (only for hints; checking works without it).
"""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pipeline
import verifier

HERE = Path(__file__).parent
PORT = 8000


def api_preview(body):
    function_text = body.get("function", "")
    try:
        problem = verifier.setup(function_text)
    except verifier.ParseError as e:
        return {"function": {"ok": False, "error": str(e)}, "lines": []}
    symbols = problem.symbols
    if problem.implicit:
        sides = [verifier.parse(side, symbols) for side in verifier.FUNCTION_PREFIX.sub("", function_text).split("=")]
        function = {"ok": True, "mathml": verifier.mathml(verifier.sp.Eq(*sides, evaluate=False))}
    else:
        function = verifier.preview(function_text, symbols)
    return {
        "function": function,
        "implicit": problem.implicit,
        "lines": [verifier.preview(line, symbols) for line in body.get("lines", [])],
    }


def api_check(body):
    try:
        return verifier.check_working(body.get("function", ""), body.get("lines", []))
    except verifier.ParseError as e:
        return {"error": str(e), "line": getattr(e, "line", None)}


def api_hint(body):
    # The verdict is recomputed server-side, so the hint is always about SymPy's verdict.
    return pipeline.hint_with_step(body["function"], body["lines"])


def api_step(body):
    return pipeline.more_tries(body["function"], body["lines"])


def api_examples():
    cases = json.loads((HERE / "data" / "test_cases.json").read_text(encoding="utf-8"))["cases"]
    return [{"id": c["id"], "topic": c["topic"], "function": c.get("equation") or c["f"], "lines": c["working"]} for c in cases]


ROUTES = {"/api/preview": api_preview, "/api/check": api_check, "/api/hint": api_hint,
          "/api/step": api_step}


class Handler(BaseHTTPRequestHandler):
    def _send(self, status, content_type, payload):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._send(200, "text/html; charset=utf-8", (HERE / "static" / "index.html").read_bytes())
        elif self.path == "/api/examples":
            self._send(200, "application/json", json.dumps(api_examples()).encode())
        else:
            self._send(404, "text/plain", b"Not found")

    def do_POST(self):
        route = ROUTES.get(self.path)
        if not route:
            return self._send(404, "text/plain", b"Not found")
        length = int(self.headers.get("Content-Length", 0))
        try:
            body = json.loads(self.rfile.read(length) or b"{}")
            payload = json.dumps(route(body), ensure_ascii=False).encode()
            self._send(200, "application/json; charset=utf-8", payload)
        except Exception as e:  # keep the app alive and show the problem
            self._send(500, "application/json", json.dumps({"error": f"Server error: {e}"}).encode())

    def log_message(self, *args):
        pass  # keep the terminal quiet


if __name__ == "__main__":
    print(f"Step-checker running at http://localhost:{PORT}  (Ctrl+C to stop)")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
