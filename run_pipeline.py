"""Task 5: evaluate the pipeline (SymPy verdict -> Gemma hint) on the test cases.

For every test case, SymPy finds the first incorrect line (compared with the label),
then Gemma is asked for an error type + hint, several times, with thinking off and on.
Every result is saved to results/pipeline_eval.jsonl; a summary is printed at the end.

Run:  python run_pipeline.py              (3 runs per case, thinking off and on)
      python run_pipeline.py --runs 1     (quicker)
      python run_pipeline.py --think off  (only one setting)
"""
import argparse
import json
import statistics
from collections import defaultdict
from pathlib import Path

import explainer
import pipeline
from verifier import check_working

HERE = Path(__file__).parent
OUT = HERE / "results" / "pipeline_eval.jsonl"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--think", choices=["off", "on", "both"], default="both")
    args = parser.parse_args()
    settings = {"off": [False], "on": [True], "both": [False, True]}[args.think]

    cases = json.loads((HERE / "data" / "test_cases.json").read_text(encoding="utf-8"))["cases"]
    explainer.LOG = HERE / "results" / "pipeline_eval_calls.jsonl"  # keep the app's own log separate
    OUT.parent.mkdir(exist_ok=True)

    # Warm-up so the first timed call doesn't include loading the model.
    explainer._call([{"role": "user", "content": "Reply with JSON."}])

    rows = []
    with OUT.open("a", encoding="utf-8") as out:
        for think in settings:
            explainer.THINK = think
            for case in cases:
                fn = case.get("equation") or case["f"]
                verdict = check_working(fn, case["working"])
                row_base = {
                    "id": case["id"], "think": think,
                    "label_first_error": case["first_error_line"],
                    "sympy_first_error": verdict["first_error"],
                    "sympy_correct": verdict["first_error"] == case["first_error_line"],
                    "label_error_type": case["error_type"],
                }
                if not verdict["first_error"]:
                    continue  # no mistake -> Gemma is never asked
                wrong = case["working"][verdict["first_error"] - 1]
                for run in range(1, args.runs + 1):
                    hint = pipeline.hint_with_step(fn, case["working"])
                    step = hint.get("step", {"verified": False, "tries": 0, "rejected": []})
                    row = {**row_base, "run": run, "prompt_version": explainer.PROMPT_VERSION,
                           "status": hint["status"], "error_type": hint["error_type"],
                           "hint": hint["hint"], "raw_hint": hint.get("raw_hint"),
                           "corrected_line": hint.get("corrected_line"), "step_verified": step["verified"],
                           "step_tries": step["tries"], "step_rejected": step["rejected"],
                           "attempts": hint["attempts"], "seconds": hint["seconds"],
                           "type_correct": hint["error_type"] == case["error_type"]}
                    rows.append(row)
                    out.write(json.dumps(row, ensure_ascii=False) + "\n")
                    out.flush()
                    print(f"think={'on ' if think else 'off'} {case['id']:3} run {run}: {hint['status']:8} "
                          f"{str(hint['error_type']):26} {'OK ' if row['type_correct'] else 'X  '} "
                          f"step {'verified' if step['verified'] else 'NOT FOUND'} in {step['tries']} tries, {hint['seconds']} s", flush=True)

    print("\n=== Summary ===")
    for think in settings:
        rs = [r for r in rows if r["think"] == think]
        if not rs:
            continue
        by_case = defaultdict(list)
        for r in rs:
            by_case[r["id"]].append(r["error_type"])
        consistent = sum(len(set(v)) == 1 for v in by_case.values())
        secs = [r["seconds"] for r in rs]
        print(f"thinking {'on' if think else 'off'}: error type right in {sum(r['type_correct'] for r in rs)}/{len(rs)} hints; "
              f"same label on every run in {consistent}/{len(by_case)} cases; "
              f"retries {sum(r['attempts'] > 1 for r in rs)}, fallbacks {sum(r['status'] == 'fallback' for r in rs)}, "
              f"unavailable {sum(r['status'] == 'unavailable' for r in rs)}; "
              f"verified step found {sum(r['step_verified'] for r in rs)}/{len(rs)} "
              f"(first try {sum(r['step_verified'] and r['step_tries'] == 1 for r in rs)}, after retries {sum(r['step_verified'] and r['step_tries'] > 1 for r in rs)}); "
              f"seconds median {statistics.median(secs)}, max {max(secs)}; "
              f"raw hints with LaTeX ($ or backslash or tab) {sum(any(c in (r['raw_hint'] or '') for c in '$' + chr(92) + chr(9)) for r in rs)}")


if __name__ == "__main__":
    main()
