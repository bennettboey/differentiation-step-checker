"""Gemma explanation layer: explains a mistake that SymPy has already found.

Gemma never decides correctness. It is told which line is wrong and what the
correct derivative is, must pick one error type from a fixed list, and writes
a one-sentence hint plus a corrected version of the wrong line (which SymPy
checks before it is ever shown). Output is forced into a JSON schema; if the reply is still
unusable it retries once, then falls back to a fixed non-AI message.
A non-AI clean-up step turns any LaTeX in the hint into plain text before it is shown.
Every call is logged to results/pipeline_log.jsonl.
"""
import json
import os
import re
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

MODEL = os.environ.get("STEPCHECK_MODEL", "gemma4:e2b")
# On by default: task 5 showed thinking doubles correct diagnoses (15/45 -> 29/45) for ~3 s more.
THINK = os.environ.get("STEPCHECK_THINK", "true").lower() == "true"
URL = "http://localhost:11434/api/chat"
LOG = Path(__file__).parent / "results" / "pipeline_log.jsonl"
MAX_HINT_CHARS = 300
PROMPT_VERSION = 3  # v2: plain-text maths, not LaTeX; v3: also returns a corrected line (checked by SymPy)

ERROR_TYPES = [
    "missed chain rule",
    "product rule error",
    "quotient rule order/sign",
    "power rule",
    "trig/exp/log derivative",
    "algebra slip",
]
SCHEMA = {
    "type": "object",
    "properties": {
        "error_type": {"type": "string", "enum": ERROR_TYPES},
        "hint": {"type": "string"},
        "corrected_line": {"type": "string"},
    },
    "required": ["error_type", "hint", "corrected_line"],
}
FALLBACK_HINT = "Compare this line with the line before it and re-check each rule you applied."

SYSTEM = (
    "You help an IB Math HL student find a mistake in their differentiation working. "
    "A computer algebra system has already checked the working, and its verdict is certain: "
    "the line marked INCORRECT really is incorrect. Do not re-check or question that verdict.\n"
    "Your job:\n"
    "1. Choose the single most likely error type from this list: " + "; ".join(ERROR_TYPES) + ".\n"
    "2. Write ONE short sentence (at most 25 words) to the student that points to the mistake. "
    "The hint must not contain the corrected line; let the student try to fix it first.\n"
    "3. Write the corrected version of the INCORRECT line: what that line should have been, "
    "in the same style as the student's working (e.g. 2x*sin(3x) + x^2*3cos(3x)). "
    "It is shown only if the student asks for it.\n"
    "Write any maths as plain text (e.g. x^2, sin(3x), 1/x), never LaTeX.\n"
    'Reply only with JSON: {"error_type": "...", "hint": "...", "corrected_line": "..."}'
)


STEP_SCHEMA = {
    "type": "object",
    "properties": {"corrected_line": {"type": "string"}},
    "required": ["corrected_line"],
}
STEP_SYSTEM = (
    "You help an IB Math HL student who made a mistake in their differentiation working. "
    "Write the corrected version of the INCORRECT line: what that line should have been, "
    "in the same style as the student's working (e.g. 2x*sin(3x) + x^2*3cos(3x)). "
    "A computer algebra system will check that it equals the correct derivative. "
    "Use brackets carefully. Write maths as plain text, never LaTeX.\n"
    'Reply only with JSON: {"corrected_line": "..."}'
)


LATEX_WORDS = [
    (r"\times", "×"), (r"\cdot", "·"), (r"\left", ""), (r"\right", ""), (r"\,", " "),
    (r"\sqrt", "sqrt"), (r"\sin", "sin"), (r"\cos", "cos"), (r"\tan", "tan"),
    (r"\ln", "ln"), (r"\log", "log"), (r"\pi", "π"),
]


def clean_hint(text):
    r"""Turn LaTeX in Gemma's hint into plain text (non-AI). The page can't render LaTeX,
    and JSON decodes the "\t" in \text, "\r" in \right, "\f" in \frac and "\b" in \beta
    into control characters, losing letters."""
    for char, escape in (("\t", "\\t"), ("\r", "\\r"), ("\f", "\\f"), ("\b", "\\b")):
        text = text.replace(char, escape)  # put back the backslash JSON turned into a control character
    text = re.sub(r"\\(?:text|mathrm|operatorname)\{([^}]*)\}", r"\1", text)
    text = re.sub(r"\\frac\{([^}]*)\}\{([^}]*)\}", r"(\1)/(\2)", text)
    text = re.sub(r"\^\{([^}]*)\}", lambda m: "^" + (m.group(1) if len(m.group(1)) == 1 else f"({m.group(1)})"), text)
    for latex, plain in LATEX_WORDS:
        text = text.replace(latex, plain)
    text = re.sub(r"\\([a-zA-Z]+)", r"\1", text)  # any other LaTeX command, e.g. \beta -> beta
    text = re.sub(r"[${}]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def build_user_message(function_text, implicit, previous_line, wrong_line, correct_derivative):
    what = "dy/dx for the implicit equation" if implicit else "f'(x) for f(x) ="
    previous = previous_line if previous_line else "(none: the incorrect line is the first line)"
    return (
        f"The student is finding {what} {function_text}\n"
        f"Last correct line: {previous}\n"
        f"INCORRECT line: {wrong_line}\n"
        f"A correct expression for the derivative: {correct_derivative}"
    )


def _call(messages, schema=SCHEMA):
    body = json.dumps({
        "model": MODEL, "messages": messages, "format": schema,
        "think": THINK, "stream": False,
    }).encode()
    req = urllib.request.Request(URL, data=body, headers={"Content-Type": "application/json"})
    start = time.time()
    with urllib.request.urlopen(req, timeout=300) as resp:
        data = json.loads(resp.read())
    return data["message"]["content"], round(time.time() - start, 1)


def _validate(raw):
    """Return (error_type, hint, corrected_line) if Gemma's reply is usable, else None.
    The corrected line is not judged here; SymPy checks it before it is ever shown."""
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return None
    if not isinstance(data, dict):
        return None
    error_type, hint = data.get("error_type"), data.get("hint")
    if error_type not in ERROR_TYPES or not isinstance(hint, str):
        return None
    hint = clean_hint(hint)
    if not hint or len(hint) > MAX_HINT_CHARS:
        return None
    corrected = data.get("corrected_line")
    corrected = clean_hint(corrected)[:MAX_HINT_CHARS] if isinstance(corrected, str) else ""
    return error_type, hint, corrected


def _log(record):
    LOG.parent.mkdir(exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def explain(function_text, implicit, previous_line, wrong_line, correct_derivative):
    """Ask Gemma for a hint. Returns a dict with status ok | fallback | unavailable."""
    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": build_user_message(function_text, implicit, previous_line, wrong_line, correct_derivative)},
    ]
    attempts = []
    result = {"status": "fallback", "error_type": None, "hint": FALLBACK_HINT}
    for _ in range(2):  # first try + one retry
        try:
            raw, seconds = _call(messages)
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            attempts.append({"error": str(e)})
            result = {"status": "unavailable", "error_type": None, "hint": None}
            break
        attempts.append({"raw": raw, "seconds": seconds})
        valid = _validate(raw)
        if valid:
            result = {"status": "ok", "error_type": valid[0], "hint": valid[1], "corrected_line": valid[2],
                      "raw_hint": json.loads(raw).get("hint")}  # before clean-up, for evaluation
            break
    result["seconds"] = round(sum(a.get("seconds", 0) for a in attempts), 1)
    result["attempts"] = len(attempts)
    _log({
        "time": datetime.now().isoformat(timespec="seconds"), "event": "hint",
        "model": MODEL, "think": THINK, "function": function_text,
        "previous_line": previous_line, "wrong_line": wrong_line,
        "correct_derivative": correct_derivative, "attempts": attempts, "result": result,
    })
    return result


def retry_step(function_text, implicit, previous_line, wrong_line, correct_derivative, rejected):
    """Ask Gemma (again) for just the corrected line, telling it which earlier attempts
    SymPy rejected. Returns (corrected_line, seconds); corrected_line is "" if unusable."""
    message = build_user_message(function_text, implicit, previous_line, wrong_line, correct_derivative)
    if rejected:
        message += ("\nThese earlier attempts at the corrected line were checked by a computer algebra "
                    "system and are NOT equal to the correct derivative, so do not repeat them:\n"
                    + "\n".join(f"- {line}" for line in rejected))
    messages = [{"role": "system", "content": STEP_SYSTEM}, {"role": "user", "content": message}]
    try:
        raw, seconds = _call(messages, STEP_SCHEMA)
    except (urllib.error.URLError, TimeoutError, OSError):
        return "", 0
    try:
        line = json.loads(raw).get("corrected_line")
    except (json.JSONDecodeError, AttributeError):
        line = None
    return (clean_hint(line)[:MAX_HINT_CHARS] if isinstance(line, str) else ""), seconds


def log_step_check(function_text, corrected_line, step, attempt):
    """Record whether SymPy accepted one of Gemma's corrected lines."""
    _log({
        "time": datetime.now().isoformat(timespec="seconds"), "event": "step_check",
        "function": function_text, "attempt": attempt,
        "corrected_line": corrected_line, "verified": step["verified"],
    })
