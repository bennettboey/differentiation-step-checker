"""The step-checker pipeline: SymPy's verdict -> Gemma's hint -> a verified next step.

Used by both the web app (app.py) and the evaluation (run_pipeline.py), so they behave the same.
"""
import explainer
import verifier

MAX_STEP_TRIES = 3  # per request; the page offers "Try again" for 3 more


def find_verified_step(function_text, verdict, wrong_line, first_candidate=None, tries=MAX_STEP_TRIES):
    """Ask Gemma for the corrected line until SymPy confirms one, up to `tries` attempts.
    Each retry is told which earlier attempts SymPy rejected. Never falls back to the final answer."""
    args = (function_text, verdict["implicit"], verdict["previous_correct"], wrong_line, verdict["derivative"])
    rejected, seconds, candidate = [], 0.0, first_candidate
    for attempt in range(1, tries + 1):
        if candidate is None:
            candidate, took = explainer.retry_step(*args, rejected=rejected)
            seconds += took
        step = verifier.check_step(function_text, candidate)
        explainer.log_step_check(function_text, candidate, step, attempt)
        if step["verified"]:
            break
        if candidate:
            rejected.append(candidate)
        candidate = None
    step["tries"], step["seconds"], step["rejected"] = attempt, round(seconds, 1), rejected
    return step


def hint_with_step(function_text, lines):
    """Full pipeline for one piece of working. Returns the hint dict, with a verified step if found."""
    verdict = verifier.check_working(function_text, lines)
    if not verdict["first_error"]:
        return {"status": "no_error"}
    wrong = lines[verdict["first_error"] - 1]
    hint = explainer.explain(function_text, verdict["implicit"], verdict["previous_correct"], wrong, verdict["derivative"])
    if hint["status"] == "ok":
        hint["step"] = find_verified_step(function_text, verdict, wrong, first_candidate=hint["corrected_line"])
        hint["seconds"] = round(hint["seconds"] + hint["step"]["seconds"], 1)
    return hint


def more_tries(function_text, lines):
    """The page's "Try again" button: up to MAX_STEP_TRIES fresh attempts at the step."""
    verdict = verifier.check_working(function_text, lines)
    if not verdict["first_error"]:
        return {"verified": False, "tries": 0}
    return find_verified_step(function_text, verdict, lines[verdict["first_error"] - 1])
