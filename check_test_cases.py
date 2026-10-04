"""Sanity-check data/test_cases.json with the SymPy verifier.

For each case, finds the first working line that is not equivalent to the true
derivative and compares it with the hand-written label.
Run: python check_test_cases.py
"""
import json
from pathlib import Path

from verifier import check_working


def main():
    cases = json.loads((Path(__file__).parent / "data" / "test_cases.json").read_text(encoding="utf-8"))["cases"]
    mismatches = 0
    for case in cases:
        result = check_working(case.get("equation") or case["f"], case["working"])
        found = result["first_error"]
        ok = found == case["first_error_line"]
        mismatches += not ok
        print(f"{case['id']:3} {'OK ' if ok else 'BAD'} label={case['first_error_line']} sympy={found}  f'={result['derivative']}")
    print(f"\n{len(cases)} cases, {mismatches} mismatches")


if __name__ == "__main__":
    main()
