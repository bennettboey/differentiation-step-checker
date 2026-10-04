# Baseline: Gemma judges the working on its own

To run by hand: paste each prompt into `ollama run gemma4:e2b --verbose`, type `/clear` between cases, and fill in the results table at the bottom. To run them all automatically: `python run_baseline.py`.

**Don't look at the answer key until you've recorded Gemma's answer.**

## P1: product rule

```
A student is differentiating f(x) = x^2*sin(3x).
Their working for f'(x), line by line:
Line 1: 2x*sin(3x) + x^2*3cos(3x)
Line 2: 2x*sin(3x) + 3x^2*cos(3x)
Line 3: x(2sin(3x) + 3x*cos(3x))
Is every line correct? If not, which is the first incorrect line, and why?
```

## P2: product + chain rule

```
A student is differentiating f(x) = x^2*sin(3x).
Their working for f'(x), line by line:
Line 1: 2x*sin(3x) + x^2*cos(3x)
Line 2: x(2sin(3x) + x*cos(3x))
Is every line correct? If not, which is the first incorrect line, and why?
```

## P3: product rule

```
A student is differentiating f(x) = x^3*e^x.
Their working for f'(x), line by line:
Line 1: 3x^2*e^x
Is every line correct? If not, which is the first incorrect line, and why?
```

## P4: product rule + trig

```
A student is differentiating f(x) = x*cos(x).
Their working for f'(x), line by line:
Line 1: cos(x) + x*sin(x)
Is every line correct? If not, which is the first incorrect line, and why?
```

## Q1: quotient rule

```
A student is differentiating f(x) = (2x+1)/(x-3).
Their working for f'(x), line by line:
Line 1: ((x-3)*2 - (2x+1)*1)/(x-3)^2
Line 2: (2x - 6 - 2x - 1)/(x-3)^2
Line 3: -7/(x-3)^2
Is every line correct? If not, which is the first incorrect line, and why?
```

## Q2: quotient rule

```
A student is differentiating f(x) = x^2/(x+1).
Their working for f'(x), line by line:
Line 1: (x^2*1 - (x+1)*2x)/(x+1)^2
Line 2: (x^2 - 2x^2 - 2x)/(x+1)^2
Line 3: (-x^2 - 2x)/(x+1)^2
Is every line correct? If not, which is the first incorrect line, and why?
```

## Q3: quotient rule + simplification

```
A student is differentiating f(x) = sin(x)/x.
Their working for f'(x), line by line:
Line 1: (x*cos(x) - sin(x))/x^2
Line 2: cos(x)/x - sin(x)/x^2
Line 3: cos(x)/x + sin(x)/x^2
Is every line correct? If not, which is the first incorrect line, and why?
```

## Q4: quotient rule

```
A student is differentiating f(x) = e^x/(x^2+1).
Their working for f'(x), line by line:
Line 1: (e^x*(x^2+1) - e^x*2x)/(x^2+1)
Is every line correct? If not, which is the first incorrect line, and why?
```

## C1: chain rule

```
A student is differentiating f(x) = (3x^2 - 5)^4.
Their working for f'(x), line by line:
Line 1: 4(3x^2 - 5)^3*6x
Line 2: 24x(3x^2 - 5)^3
Is every line correct? If not, which is the first incorrect line, and why?
```

## C2: chain rule

```
A student is differentiating f(x) = sqrt(1 + x^2).
Their working for f'(x), line by line:
Line 1: 1/(2sqrt(1 + x^2))
Is every line correct? If not, which is the first incorrect line, and why?
```

## C3: chain rule (nested) + trig identity

```
A student is differentiating f(x) = sin(4x)^2.
Their working for f'(x), line by line:
Line 1: 2sin(4x)*cos(4x)*4
Line 2: 8sin(4x)*cos(4x)
Line 3: 4sin(8x)
Is every line correct? If not, which is the first incorrect line, and why?
```

## C4: chain rule (nested)

```
A student is differentiating f(x) = e^(sin(2x)).
Their working for f'(x), line by line:
Line 1: e^(sin(2x))*cos(2x)
Is every line correct? If not, which is the first incorrect line, and why?
```

## E2: logarithm

```
A student is differentiating f(x) = ln(5x).
Their working for f'(x), line by line:
Line 1: 1/(5x)
Is every line correct? If not, which is the first incorrect line, and why?
```

## E3: exponential (non-e base)

```
A student is differentiating f(x) = 2^x.
Their working for f'(x), line by line:
Line 1: x*2^(x-1)
Is every line correct? If not, which is the first incorrect line, and why?
```

## E4: product rule + log

```
A student is differentiating f(x) = x^2*ln(x).
Their working for f'(x), line by line:
Line 1: 2x*ln(x) + x^2*(1/x)
Line 2: 2x*ln(x) + x
Line 3: x(2ln(x) + x)
Is every line correct? If not, which is the first incorrect line, and why?
```

## W1: power rule (negative index)

```
A student is differentiating f(x) = 4/x^3.
Their working for f'(x), line by line:
Line 1: 4*(-3)*x^(-3-1)
Line 2: -12x^(-2)
Is every line correct? If not, which is the first incorrect line, and why?
```

## I1: inverse trig

```
A student is differentiating f(x) = arctan(2x).
Their working for f'(x), line by line:
Line 1: 1/(1 + 4x^2)
Is every line correct? If not, which is the first incorrect line, and why?
```

## L1: long working (product + chain + factorising)

```
A student is differentiating f(x) = (x^2+1)^3*(2x-1)^2.
Their working for f'(x), line by line:
Line 1: 3(x^2+1)^2*2x*(2x-1)^2 + (x^2+1)^3*2(2x-1)*2
Line 2: 6x(x^2+1)^2*(2x-1)^2 + 4(x^2+1)^3*(2x-1)
Line 3: 2(x^2+1)^2*(2x-1)*(3x(2x-1) + 2(x^2+1))
Line 4: 2(x^2+1)^2*(2x-1)*(6x^2 - 3x + 2x^2 + 2)
Line 5: 2(x^2+1)^2*(2x-1)*(8x^2 - 3x + 2)
Line 6: 2(x^2+1)^2*(2x-1)*(8x^2 + 3x + 2)
Is every line correct? If not, which is the first incorrect line, and why?
```

## M1: implicit differentiation (stretch)

```
A student is using implicit differentiation on the equation x^2 + y^2 = 25.
Their working for dy/dx, line by line:
Line 1: -2x/(2y)
Line 2: -x/y
Is every line correct? If not, which is the first incorrect line, and why?
```

## M2: implicit differentiation (stretch)

```
A student is using implicit differentiation on the equation x^2*y + y^3 = 2x.
Their working for dy/dx, line by line:
Line 1: (2 - 2x*y)/(3y^2)
Is every line correct? If not, which is the first incorrect line, and why?
```

---

## Results table (fill in as you go)

Gemma's line = the first wrong line Gemma named ("none" if it said all correct). Time = `eval duration` or total from `--verbose`.

**Who ran what:** P1, P2, P3, P4 and Q1 were run by Bennett in the terminal (`ollama run gemma4:e2b --verbose`). Q2 to M2 were run by Claude Code with `run_baseline.py`: the same prompt and default settings (thinking on), a fresh request per case. Raw outputs for those are in `results/baseline_raw.jsonl`.

**First-pass summary:** right first-wrong-line in **18/20**. Gemma never approved a wrong line (0/15 planted mistakes missed). Both failures (C3, L1) were **correct lines it rejected**: lines written in an unusual but equivalent form. Times: 21.7-77.4 s per case.

| Case | Gemma's line | Right line? (y/n) | Gemma's reason (short) | Right reason? (y/n) | Time (s) | Notes |
|---|---|---|---|---|---|---|
| P1 | none | y | All lines correct: product + chain rule, then simplify and factorise | y | 29.5 | 1232 tokens at 43.5 tok/s; most of the output was thinking |
| P2 | 1 | y | Missing chain-rule factor 3 from sin(3x); line 2 inherits the error | y | 31.4 | 1250 tokens at 41.2 tok/s |
| P3 | 1 | y | Only the u'v term; missing the uv' term (x^3 e^x) | y | 38.0 | 852 tokens at 34.0 tok/s; 12.6 s of it was reloading the model (idle >5 min). Error category matches; see note on ambiguity |
| P4 | 1 | y | Used d/dx cos x = +sin x instead of -sin x (wrong sign on second term) | y | 23.5 | 662 tokens at 29.5 tok/s |
| Q1 | none | y | All lines correct: quotient rule set up right, numerator expanded, simplified to -7/(x-3)^2 | y | 38.0 | 1170 tokens at 31.6 tok/s |
| Q2 | 1 | y | Quotient-rule numerator in wrong order (uv' - u'v); lines 2-3 correctly simplify the wrong line | y | 45.0 | Run by Claude Code via API |
| Q3 | 3 | y | Sign of the sin(x)/x^2 term flipped | y (mostly) | 48.5 | Explanation contains a false maths claim: says line 3 is "the negative of the correct derivative" (it isn't; only one term's sign flipped). Run by Claude Code via API |
| Q4 | 1 | y | Denominator should be (x^2+1)^2, not (x^2+1) | y | 24.3 | Named the exact error even though the fixed list has no exact category. Run by Claude Code via API |
| C1 | none | y | Both lines correct: chain rule, then 4*6x = 24x | y | 27.7 | Run by Claude Code via API |
| C2 | 1 | y | Missed inner derivative 2x (chain rule) | y | 31.1 | Run by Claude Code via API |
| C3 | 3 | **n** | Claimed 4sin(8x) is "completely wrong... no mathematical justification" | **n** | 50.4 | **FAILURE: rejected a correct line.** 4sin(8x) = 8sin(4x)cos(4x) by the double-angle identity. Also opened with "This is a common type of error" before checking. Run by Claude Code via API |
| C4 | 1 | y | Missed factor 2 from differentiating sin(2x) | y | 31.1 | Run by Claude Code via API |
| E2 | 1 | y | Missed chain rule factor 5 | y | 31.1 | Run by Claude Code via API |
| E3 | 1 | y | Should be 2^x ln 2; student wrongly applied power rule | y | 28.2 | Run by Claude Code via API |
| E4 | 3 | y | Factorising error: should be x(2ln(x) + 1) | y | 36.9 | Run by Claude Code via API |
| W1 | 2 | y | Exponent should be -4, not -2 | y | 23.9 | Run by Claude Code via API |
| I1 | 1 | y | Forgot to multiply by inner derivative 2 | y | 21.7 | Run by Claude Code via API |
| L1 | 3 | **n** | Claimed line 3 factored out "an incorrect scaling factor" 2(x^2+1)^2(2x-1) | **n** | 77.4 | **FAILURE: rejected a correct line.** Line 3 is correct; the real error is line 6. Gemma did spot the sign difference on line 6 but marked lines 3-5 wrong too. Longest case: 2750 tokens. Run by Claude Code via API |
| M1 | none | y | Both lines correct; line 2 simplifies line 1 | y | 44.6 | Run by Claude Code via API |
| M2 | 1 | y | Failed to apply product rule to x^2*y (missing x^2 in denominator) | y | 37.1 | Wording slightly muddled but correct diagnosis. Run by Claude Code via API |

---

## Consistency repeats (same prompt, 3 runs each, fresh context each time)

All runs by Claude Code via `run_baseline.py`; raw outputs in `results/baseline_raw.jsonl`.

| Case | True first wrong line | Run 1 | Run 2 | Run 3 | Consistent? |
|---|---|---|---|---|---|
| C3 | none (all correct) | line 3 ✗ ("completely wrong") | line 3 ✗ ("completely wrong") | none ✓ (explained the double-angle identity correctly) | **No**: 2 of 3 runs rejected a correct line |
| L1 | 6 | line 3 ✗ | line 6 ✓ (after "Wait, let's re-examine...") | line 2 ✗ (said a factor (2x-1) was missing, then wrote the student's exact term as the "correct" one) | **No**: three different answers, 1 of 3 right |
| Q3 | 3 | line 3 ✓ (explanation had a false claim) | line 3 ✓ | line 3 ✓ | Yes (the false claim appeared only in run 1) |

**Speed varied a lot on the same machine.** Run 1 ran at ~28-36 tokens/s (48-77 s per case). Runs 2-3 ran at ~172-192 tokens/s (7-23 s per case), starting right after the model reloaded (15.1 s load). Same model, prompt and settings. Cause (per Bennett): the laptop was on battery during the first pass and plugged in for the repeats.

---

## Answer key (check after recording Gemma's answer)

| Case | First wrong line | Error type | What's actually wrong |
|---|---|---|---|
| P1 | none (all correct) | - | Fully correct working. |
| P2 | 1 | missed chain rule | Persona scenario function. Forgot the factor 3 from sin(3x); line 2 factorises the wrong line correctly. |
| P3 | 1 | product rule error | Classic (uv)' = u'v' mistake. |
| P4 | 1 | trig/exp/log derivative | Used d/dx cos x = sin x (sign error). Product rule structure is right. |
| Q1 | none (all correct) | - | Fully correct working. |
| Q2 | 1 | quotient rule order/sign | Numerator terms swapped (u v' - v u'). Lines 2-3 simplify the wrong line correctly, so the answer is the exact negative of the truth. |
| Q3 | 3 | algebra slip | Correct rule; sign flipped when rewriting on line 3. |
| Q4 | 1 | quotient rule order/sign | Denominator not squared. No exact category in the fixed list; 'quotient rule order/sign' is the closest. Probe for whether the list is too coarse. |
| C1 | none (all correct) | - | Fully correct working. |
| C2 | 1 | missed chain rule | Missing inner derivative 2x. |
| C3 | none (all correct) | - | Fully correct. Line 3 uses the double-angle identity, so it looks very different but is equivalent. Tests equivalence checking. |
| C4 | 1 | missed chain rule | Got the outer and middle layers but dropped the innermost factor 2. |
| E2 | 1 | missed chain rule | Ambiguous diagnosis: could also be called a log-derivative error. Correct answer is 1/x. |
| E3 | 1 | trig/exp/log derivative | Applied the power rule to an exponential. Ambiguous between 'power rule' and 'trig/exp/log derivative'. |
| E4 | 3 | algebra slip | Correct differentiation; wrong when factorising out x on line 3. |
| W1 | 2 | power rule | Line 1 correctly sets up the power rule. Line 2 evaluates -3-1 as -2 instead of -4. |
| I1 | 1 | missed chain rule | Missing factor 2. |
| L1 | 6 | algebra slip | Five correct lines, then a sign slip on line 6. Probes context-limit/forgetting on long working. |
| M1 | none (all correct) | - | Lines are dy/dx in terms of x and y. Fully correct. |
| M2 | 1 | product rule error | Treated x^2*y as if only y depended on x: missing the x^2*dy/dx term. Correct: (2 - 2xy)/(x^2 + 3y^2). |
