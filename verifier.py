"""SymPy verifier: the only judge of correctness in the step-checker.

Given f(x) (or an implicit equation in x and y) and the student's working lines,
it computes the true derivative once and checks every line for equivalence:
  1. symbolic:  simplify(line - truth) == 0
  2. numeric:   if symbolic is inconclusive, compare values at random points
  3. unsure:    if neither can decide, say so instead of guessing
No AI is involved anywhere in this file.
"""
import random
import re
from dataclasses import asdict, dataclass

import sympy as sp
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

x, y = sp.symbols("x y")
TRANSFORMS = standard_transformations + (implicit_multiplication_application, convert_xor)
NAMES = {
    "x": x, "y": y, "e": sp.E, "pi": sp.pi, "ln": sp.log, "abs": sp.Abs,
    "arctan": sp.atan, "arcsin": sp.asin, "arccos": sp.acos,
}
SYMPY_ONLY = {}  # parse with SymPy names only, so input can't call Python built-ins
exec("from sympy import *", SYMPY_ONLY)
SYMPY_ONLY["__builtins__"] = {}
ALLOWED_CHARS = re.compile(r"^[0-9a-zA-Z\s.+\-*/^()]*$")
LINE_PREFIX = re.compile(r"^\s*(f'\(x\)|f'|dy/dx|y')?\s*=\s*")  # tolerate "f'(x) = ..." or "= ..."
FUNCTION_PREFIX = re.compile(r"^\s*f\(x\)\s*=")  # tolerate "f(x) = ..." in the function box
NUMERIC_POINTS = 6
TOLERANCE = 1e-7


class ParseError(ValueError):
    pass


def parse(text, allowed_symbols, evaluate=True):
    text = LINE_PREFIX.sub("", text).strip()
    if not text:
        raise ParseError("This line is empty.")
    if not ALLOWED_CHARS.match(text) or "__" in text:
        raise ParseError("Use only letters, numbers, + - * / ^ and round brackets.")
    try:
        expr = parse_expr(text, local_dict=NAMES, global_dict=SYMPY_ONLY, transformations=TRANSFORMS, evaluate=evaluate)
    except Exception:
        raise ParseError("Couldn't read this line. Check the brackets, and write powers with ^ (e.g. x^2, sin(x)^2).")
    unknown = expr.free_symbols - allowed_symbols
    if unknown:
        names = ", ".join(sorted(str(s) for s in unknown))
        raise ParseError(f"Unknown letter(s): {names}. Write functions with brackets, e.g. sin(x), ln(x).")
    return expr


def caret(expr):
    """SymPy expression -> plain text a student would type (x^2, not x**2)."""
    return sp.sstr(expr).replace("**", "^")


def mathml(expr):
    """Expression as MathML, which browsers draw as real maths (offline, no libraries)."""
    markup = sp.printing.mathml(expr, printer="presentation", order="none")  # keep the typed term order
    # Show a dot between adjacent numbers, so 4*6x doesn't read as "46x".
    markup = markup.replace("</mn><mo>&InvisibleTimes;</mo><mn>", "</mn><mo>·</mo><mn>")
    markup = markup.replace("<mo>-</mo>", "<mo>−</mo>")  # a real minus sign, not a short hyphen
    return f'<math display="inline">{markup}</math>'


@dataclass
class Problem:
    implicit: bool
    expr: object        # f(x), or lhs - rhs of the implicit equation
    derivative: object  # f'(x), or dy/dx in terms of x and y

    @property
    def symbols(self):
        return {x, y} if self.implicit else {x}


def setup(function_text):
    """Parse the function (or implicit equation) and compute the true derivative."""
    function_text = FUNCTION_PREFIX.sub("", function_text)
    if function_text.count("=") > 1:
        raise ParseError("Use at most one '=' (for an implicit equation like x^2 + y^2 = 25).")
    if "=" in function_text:
        lhs, rhs = function_text.split("=")
        eq = parse(lhs, {x, y}) - parse(rhs, {x, y})
        if y not in eq.free_symbols:
            raise ParseError("An implicit equation needs y in it.")
        return Problem(True, eq, sp.simplify(sp.idiff(eq, y, x)))
    f = parse(function_text, {x})
    return Problem(False, f, sp.diff(f, x))


def _value(expr, point):
    v = complex(sp.N(expr.subs(point)))
    return v if abs(v.imag) < 1e-9 and abs(v.real) < 1e12 else None


def _sample_points(problem, rng):
    """Random points where the derivative can be evaluated. For implicit
    problems the points lie on the curve, since dy/dx forms may only agree there."""
    for _ in range(60):
        x0 = sp.Rational(rng.randint(-300, 300), 100)
        if not problem.implicit:
            yield {x: x0}
            continue
        try:
            roots = sp.Poly(problem.expr.subs(x, x0), y).nroots()
        except Exception:
            continue
        for r in roots:
            if abs(sp.im(r)) < 1e-9:
                yield {x: x0, y: sp.re(r)}


def compare(line_expr, target, problem):
    """Return (status, method): status is 'equal', 'different' or 'unsure'."""
    try:
        if sp.simplify(line_expr - target) == 0:
            return "equal", "symbolic"
    except Exception:
        pass
    rng = random.Random(0)  # fixed seed: same input always gives the same verdict
    agreed = 0
    for point in _sample_points(problem, rng):
        try:
            a, b = _value(line_expr, point), _value(target, point)
        except Exception:
            continue
        if a is None or b is None:
            continue
        if abs(a - b) > TOLERANCE * max(1.0, abs(b)):
            return "different", "numeric"
        agreed += 1
        if agreed >= NUMERIC_POINTS:
            return "equal", "numeric"
    return "unsure", "none"


@dataclass
class LineResult:
    number: int
    text: str
    status: str   # correct | incorrect | carries_error | unsure
    method: str   # symbolic | numeric | none
    message: str


def check_working(function_text, lines):
    """Check every working line. Raises ParseError (with .line set) on bad input."""
    problem = setup(function_text)
    parsed = []
    for i, text in enumerate(lines, start=1):
        try:
            parsed.append(parse(text, problem.symbols))
        except ParseError as e:
            e.line = i
            raise
    results, first_error, first_error_expr = [], None, None
    for i, (text, expr) in enumerate(zip(lines, parsed), start=1):
        status, method = compare(expr, problem.derivative, problem)
        if status == "equal":
            results.append(LineResult(i, text, "correct", method, "Correct."))
        elif status == "unsure":
            results.append(LineResult(i, text, "unsure", method, "Couldn't confirm this line either way."))
        elif first_error is None:
            first_error, first_error_expr = i, expr
            results.append(LineResult(i, text, "incorrect", method, "First incorrect line."))
        elif compare(expr, first_error_expr, problem)[0] == "equal":
            results.append(LineResult(i, text, "carries_error", method,
                                      f"Follows correctly from line {first_error}, so it carries that mistake forward."))
        else:
            results.append(LineResult(i, text, "incorrect", method, "Also incorrect."))
    previous_correct = None
    if first_error:
        earlier = [r for r in results[: first_error - 1] if r.status == "correct"]
        previous_correct = earlier[-1].text if earlier else None
    return {
        "implicit": problem.implicit,
        "derivative": caret(problem.derivative),
        "derivative_mathml": mathml(problem.derivative),
        "lines": [asdict(r) for r in results],
        "first_error": first_error,
        "previous_correct": previous_correct,
    }


def check_step(function_text, step_text):
    """Check a corrected line written by Gemma. It is shown to the student only if
    SymPy confirms it equals the true derivative; otherwise the caller falls back
    to SymPy's own derivative."""
    problem = setup(function_text)
    step_text = step_text or ""
    for symbol, plain in (("·", "*"), ("×", "*"), ("−", "-"), ("²", "^2"), ("³", "^3")):
        step_text = step_text.replace(symbol, plain)
    try:
        expr = parse(step_text, problem.symbols)
    except ParseError:
        return {"verified": False, "reason": "unreadable"}
    if compare(expr, problem.derivative, problem)[0] != "equal":
        return {"verified": False, "reason": "not equal to the true derivative"}
    try:
        shown = parse(step_text, problem.symbols, evaluate=False)
    except ParseError:
        shown = expr
    return {"verified": True, "text": step_text, "mathml": mathml(shown)}


def preview(text, allowed_symbols):
    """Render one line as the checker reads it, so the student can spot typos."""
    try:
        expr = parse(text, allowed_symbols)
    except ParseError as e:
        return {"ok": False, "error": str(e)}
    try:  # unevaluated form stays closer to what the student typed, e.g. x^2*3cos(3x)
        return {"ok": True, "mathml": mathml(parse(text, allowed_symbols, evaluate=False))}
    except Exception:
        return {"ok": True, "mathml": mathml(expr)}
