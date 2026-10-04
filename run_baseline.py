"""Baseline: ask Gemma alone (no SymPy) to judge each test case's working.

Sends the same prompt as baseline_prompts.md to the local Ollama API, one fresh
request per case (no shared context), default settings (thinking on), and saves
every raw response with timings to results/baseline_raw.jsonl.

Run:  python run_baseline.py            (all cases)
      python run_baseline.py Q2 Q3 C1   (only these cases)
"""
import json
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
MODEL = "gemma4:e2b"
URL = "http://localhost:11434/api/generate"


def build_prompt(case):
    if case.get("kind") == "implicit":
        head = f"A student is using implicit differentiation on the equation {case['equation']}.\nTheir working for dy/dx, line by line:"
    else:
        head = f"A student is differentiating f(x) = {case['f']}.\nTheir working for f'(x), line by line:"
    lines = "\n".join(f"Line {i}: {line}" for i, line in enumerate(case["working"], 1))
    return f"{head}\n{lines}\nIs every line correct? If not, which is the first incorrect line, and why?"


def ask(prompt):
    body = json.dumps({"model": MODEL, "prompt": prompt, "stream": False}).encode()
    req = urllib.request.Request(URL, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as resp:
        return json.loads(resp.read())


def main():
    cases = json.loads((HERE / "data" / "test_cases.json").read_text(encoding="utf-8"))["cases"]
    wanted = set(sys.argv[1:])
    out_path = HERE / "results" / "baseline_raw.jsonl"
    out_path.parent.mkdir(exist_ok=True)
    with out_path.open("a", encoding="utf-8") as out:
        for case in cases:
            if wanted and case["id"] not in wanted:
                continue
            prompt = build_prompt(case)
            data = ask(prompt)
            record = {
                "id": case["id"],
                "model": MODEL,
                "prompt": prompt,
                "response": data.get("response", ""),
                "thinking": data.get("thinking", ""),
                "total_seconds": round(data["total_duration"] / 1e9, 1),
                "load_seconds": round(data["load_duration"] / 1e9, 1),
                "eval_count": data.get("eval_count"),
                "tokens_per_second": round(data["eval_count"] / (data["eval_duration"] / 1e9), 1),
            }
            out.write(json.dumps(record, ensure_ascii=False) + "\n")
            out.flush()
            print(f"{case['id']}: {record['total_seconds']} s, {record['eval_count']} tokens", flush=True)


if __name__ == "__main__":
    main()
