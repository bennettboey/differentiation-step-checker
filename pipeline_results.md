# Pipeline results (task 5)

Run by Claude Code with `run_pipeline.py` on 4 Oct 2026, laptop plugged in. Every case with a planted mistake (15) went through the real pipeline: SymPy finds the first incorrect line, then Gemma is asked for an error type + one-sentence hint. 3 runs per case, with Gemma's thinking **off** and then **on**. Raw rows: `results/pipeline_eval.jsonl`; full Gemma calls: `results/pipeline_eval_calls.jsonl`.

## Summary

| Measure | Thinking off | Thinking on |
|---|---|---|
| SymPy found the right first incorrect line | 15/15 cases (every run) | 15/15 cases (every run) |
| Gemma's error type matched the label (strict) | **15/45 (33%)** | **29/45 (64%)** |
| ...also accepting 'power rule' for E3 (ambiguous case) | 18/45 (40%) | 30/45 (67%) |
| Same label on all 3 runs | 13/15 cases | 10/15 cases |
| Invalid JSON / retries / fallback messages | 0 / 0 / 0 | 0 / 0 / 0 |
| Hint text garbled by LaTeX (Gemma wrote `\text{sin}(3x)`; JSON turns `\t` into a tab, so the page shows `<tab>ext{sin}(3x)`) | 5/45 | 0/45 |
| Hints containing raw LaTeX `$...$` (unrendered on the page) | 9/45 | 6/45 |
| Hint time, median (max) | 2.5 s (20.4 s, first call) | 5.3 s (9.9 s) |

## Per case (label given by Gemma on runs 1 / 2 / 3; ✓ = matches label)

| Case | Correct type | Thinking off | Thinking on |
|---|---|---|---|
| P2 | missed chain rule | product / product / product | chain ✓ / chain ✓ / chain ✓ |
| P3 | product rule error | product ✓ / product ✓ / product ✓ | product ✓ / product ✓ / product ✓ |
| P4 | trig/exp/log derivative | product / product / product | product / product / product |
| Q2 | quotient rule order/sign | product / algebra / algebra | product / product / quotient ✓ |
| Q3 | algebra slip | algebra ✓ / algebra ✓ / algebra ✓ | algebra ✓ / quotient / algebra ✓ |
| Q4 | quotient rule order/sign | product / product / product | quotient ✓ / quotient ✓ / quotient ✓ |
| C2 | missed chain rule | quotient / power / power | chain ✓ / chain ✓ / chain ✓ |
| C4 | missed chain rule | chain ✓ / chain ✓ / chain ✓ | chain ✓ / chain ✓ / chain ✓ |
| E2 | missed chain rule | algebra / algebra / algebra | chain ✓ / chain ✓ / chain ✓ |
| E3 | trig/exp/log derivative | power / power / power | product / power / trig/exp/log ✓ |
| E4 | algebra slip | product / product / product | product / product / product |
| W1 | power rule | power ✓ / power ✓ / power ✓ | power ✓ / power ✓ / algebra |
| I1 | missed chain rule | algebra / algebra / algebra | chain ✓ / chain ✓ / chain ✓ |
| L1 | algebra slip | algebra ✓ / algebra ✓ / algebra ✓ | algebra ✓ / product / algebra ✓ |
| M2 | product rule error | quotient / quotient / quotient | algebra / algebra / algebra |

## What reading the hints showed

- **The label is often wrong while the sentence is right.** Examples: thinking off, E2 and I1 were labelled *algebra slip* but the hint said to apply the chain rule (correct); thinking on, P4 was labelled *product rule error* but the hint said "the derivative of cos(x) is negative sine(x)" (correct); M2 was labelled *algebra slip* but the hint said "you missed the x² term from differentiating x²y" (correct).
- **Thinking off is consistent but consistently wrong:** the same label on all 3 runs in 13/15 cases, yet only 33% right. Retrying would just repeat the wrong answer.
- **Wrong maths inside hints (thinking on):** C4 runs 2-3 and I1 run 3 said the derivative of the inside function "is 2x" (it is 2).
- **Misleading pointers (thinking off):** C4: "apply the chain rule to the outer exponential function" (the missing factor comes from the inner 2x); L1: "when differentiating (2x-1)^2" (the error is a sign slip while expanding, not differentiating).
- **One hint gave the answer away** despite the instruction: W1 (thinking on) run 2, "it should be -4, not -2".
- **Scoring caveat:** each case has one hand-written label. Some cases fit two labels (E3: power rule vs exp derivative; P3, see the baseline notes), so strict accuracy is a slight underestimate.

## Follow-up: plain-text prompt + LaTeX clean-up (prompt v2, thinking on)

After the results above, two changes were made: Gemma's instructions now say "Write any maths as plain text (e.g. x^2, sin(3x), 1/x), never LaTeX", and a non-AI clean-up step (`clean_hint` in `explainer.py`) converts any remaining LaTeX to plain text before the hint is shown. The thinking-on evaluation was then re-run (15 cases × 3 runs, plugged in). Rows have `"prompt_version": 2` in `results/pipeline_eval.jsonl`.

| Measure | Prompt v1, thinking on | Prompt v2, thinking on |
|---|---|---|
| Raw hints containing LaTeX (before clean-up) | 6/45 | **0/45** |
| Error type right | 29/45 (64%) | 28/45 (62%) |
| Same label on all 3 runs | 10/15 cases | 7/15 cases |
| Hint time, median (max) | 5.3 s (9.9 s) | 5.2 s (8.9 s) |

- The clean-up step, applied to the 90 hints from the first evaluation, fixed all 16 that contained LaTeX (e.g. `$	ext{sin}(3x)$` became `sin(3x)`).
- Accuracy and speed were about the same; the 1-hint difference is within run-to-run variation.
- The label still often contradicts a correct sentence: Q4 was labelled *algebra slip* on all 3 runs while every sentence correctly said the denominator must be squared.
- Wrong maths still appeared once: C4 run 2, "the derivative of the inner function, which is 2x" (it is 2).

## Follow-up: corrected step, written by Gemma and checked by SymPy (prompt v3, thinking on)

Gemma now also writes the corrected version of the wrong line. The page shows it (via **Show the correct step**, or after **This isn't my mistake**) only if SymPy confirms it equals the true derivative; otherwise it is hidden and SymPy's own derivative is shown. Re-run: 15 cases × 3 runs, plugged in. Rows have `"prompt_version": 3`.

| Measure | Prompt v2 | Prompt v3 |
|---|---|---|
| Corrected step passed SymPy's check | – | **44/45** |
| Error type right | 28/45 | 29/45 |
| Raw hints containing LaTeX (cleaned before display) | 0/45 | 2/45 |
| Hint time, median (max) | 5.2 s (8.9 s) | 5.9 s (9.3 s) |

- **The one rejected step was really wrong:** Q2 run 1, `(2*x)*(x+1) - (x^2)*1 / (x+1)^2`. Without outer brackets, only the last term is divided by (x+1)^2. SymPy hid it, so a student would never see it.
- **"Same style as the student" is not always followed:** for E4 (error on line 3, a factorising step) Gemma gave `2x*ln(x) + x`, which is correct but is line 2's form, not the factorised form. For P2 the step matched the student's style exactly (`2x*sin(3x) + x^2*3*cos(3x)`).
- **Wrong maths can still appear in the hint sentence** (not the step): C2 run 1 said the inside derivative is "x" (it is 2x); C4 run 1 said "2x" (it is 2).

## Follow-up: retry the step until SymPy verifies it (no final-answer fallback)

Bennett's decision: the student needs the next step, not the final answer, so if SymPy rejects Gemma's corrected line, Gemma is asked again (told which attempts were rejected) instead of falling back to SymPy's derivative. Up to 3 tries per request; if all fail, the page offers **Try again** (3 more) and shows nothing unverified. Re-run: 15 cases × 3 runs, thinking on, plugged in (rows have `step_tries`).

| Measure | Result |
|---|---|
| Verified next step found | **45/45** (43 on the first try, 2 after one retry) |
| Times the student would see nothing / an unverified step | 0 / 0 |
| Error type right | 31/45 (69%) |
| Hint + step time, median (max) | 5.9 s (15.0 s, with a retry) |

- **Both retries were E2:** Gemma first wrote `5/5x`, meaning 5/(5x), but without brackets it reads as (5/5)·x = x, so SymPy rejected it. The retry wrote an unambiguous version that passed.
- **The same ambiguity affects students:** typing `1/2x` is read as (1/2)·x. The "This is what your working looks like" preview shows how the line was read, so the student can spot this before checking.
- **Testing the retry with real Gemma:** starting from the wrong Q2 step it wrote earlier (missing brackets), Gemma fixed the brackets on the 2nd try and SymPy verified it.
