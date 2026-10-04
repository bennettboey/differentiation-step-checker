# Model Limits Log

Every row comes from a real run. Copy the strongest 5–8 rows into the report.

**Failure type codes:** hallucination · instruction-miss · refusal/over-caution · inconsistency · context-limit/forgetting · format-break · latency
**Mitigation codes:** narrow the task · verification step · human-in-the-loop · prompt/framing · retrieval/grounding · retry/ensemble · fall back to non-AI

Sources: baseline = Gemma alone judging the working (`baseline_prompts.md`, `results/baseline_raw.jsonl`); pipeline = SymPy verdict + Gemma hint (`pipeline_results.md`, `results/pipeline_eval.jsonl`).

## From the baseline (Gemma alone), with the mitigation tested in the pipeline

| Input (case) | What failed (what Gemma actually said) | Failure type | Mitigation tried | Helped? (y/n) |
|---|---|---|---|---|
| C3: f = sin(4x)^2, line 3 = 4sin(8x) (correct, double-angle form) | Gemma alone said line 3 is "completely wrong... no mathematical justification". It rejected a correct line. | hallucination | verification step + fall back to non-AI: SymPy alone decides correctness | y: SymPy marks all 3 lines correct, every time (95 ms) |
| L1: 6-line working, real error on line 6 | Gemma alone said line 3 (correct) used "an incorrect scaling factor" and marked lines 3-6 wrong. 77.4 s, 2750 tokens. | hallucination (on the longest input) | verification step: SymPy decides correctness | y: SymPy found line 6 in all runs; Gemma's hint then pointed to the sign error in 5/6 hints |
| C3 and L1, same prompt run 3 times each | C3: rejected the correct line in 2 of 3 runs, accepted it in 1. L1: a different first-wrong line every run (3, 6, 2). | inconsistency | verification step: SymPy with a fixed random seed, so the same input always gives the same verdict | y: the verdict was identical on every run (90/90 pipeline runs found the right line) |
| Q3: f = sin(x)/x, sign flipped on line 3 | Right line and right reason, but the explanation also claimed line 3 is "the negative of the correct derivative", which is false. | hallucination (wrong maths inside an explanation) | narrow the task (one short sentence) + retrieval/grounding (Gemma is given the correct derivative) | n: wrong maths still appeared in the pipeline (C4, I1 hints said the inner derivative "is 2x" when it is 2; once more in the prompt-v2 re-run) |
| All 20 baseline cases (thinking on) | Every verdict took 21.7-77.4 s (median ~31 s) on battery; plugged in, 7-23 s. | latency | fall back to non-AI for the verdict (instant) + narrow the task (one-sentence hint, loaded after the verdict) + thinking off | y: verdict in 95-344 ms; hint median 2.5 s (thinking off) or 5.3 s (thinking on), plugged in |

## From the pipeline (Gemma explaining SymPy's verdict)

| Input (case) | What failed (what Gemma actually said) | Failure type | Mitigation tried | Helped? (y/n) |
|---|---|---|---|---|
| 15 error cases × 3 runs, thinking off | Gemma picked the right error type in only 15/45 hints (33%), e.g. P2 (missed chain rule) labelled "product rule error" in all 3 runs, even though it was given the wrong line and the correct derivative. | hallucination | narrow the task (fixed list of 6 types) + retrieval/grounding (correct derivative given) | n: only 33% right |
| Same 15 cases × 3 runs | Same as above. | hallucination | prompt/framing: turn Gemma's thinking on | y (partly): 29/45 (64%) right, at the cost of median 5.3 s instead of 2.5 s |
| Same 15 cases, thinking off | The same label on all 3 runs in 13/15 cases, but mostly the wrong one (only 33% right). | hallucination (consistently wrong) | retry/ensemble (considered) | n: retrying would repeat the same wrong label, so it was not adopted |
| E2, I1, P4, M2 (both settings) | The label contradicted its own sentence, e.g. E2: "algebra slip" + "apply the chain rule to the inside function"; P4 (thinking on): "product rule error" + "the derivative of cos(x) is negative sine(x)". The sentence was right; the label was wrong. | inconsistency | human-in-the-loop: hint shown as "Likely mistake… may be wrong", with "This isn't my mistake" revealing SymPy's correct derivative | not yet tested with users |
| 5/45 hints, thinking off (P2, P4, E3, E4) | Gemma wrote LaTeX like `\text{sin}(3x)` inside the JSON; `\t` becomes a tab, so the page showed `<tab>ext{sin}(3x)`. 15/90 hints contained raw `$...$` LaTeX the page doesn't render. | format-break | JSON schema + one retry + fixed fallback message | partly: JSON never broke (0 retries in 90 calls), but the schema doesn't control the text inside the hint |
| Same LaTeX problem (follow-up) | As above. | format-break | prompt/framing ("write maths as plain text, never LaTeX") + fall back to non-AI (clean-up step converts LaTeX to plain text) | y: 0/45 raw hints had LaTeX with the new prompt (was 6/45); the clean-up fixed 16/16 affected hints from the earlier run |
| Q2, prompt v3 run 1 (Gemma asked for the corrected line) | Gemma's corrected line `(2*x)*(x+1) - (x^2)*1 / (x+1)^2` was missing outer brackets, so it meant something different from the correct derivative. | hallucination | verification step + fall back to non-AI: SymPy checks every corrected line before it is shown; if it fails, it is hidden and SymPy's derivative is shown | y: 44/45 steps passed; the 1 wrong step was caught and never shown |
| E2 and Q2 (Gemma's corrected line rejected by SymPy) | E2: `5/5x` (meant 5/(5x), but reads as x). Q2: missing outer brackets. | format-break (ambiguous notation) | retry/ensemble: ask Gemma again, telling it which attempts SymPy rejected; verification step on every attempt | y: a verified step was found in 45/45 runs (2 needed one retry); the real Q2 wrong step was fixed on the 2nd try |
| W1, thinking on, run 2 | Told not to give the full answer, Gemma still wrote "it should be -4, not -2". | instruction-miss | prompt/framing ("do not write out the full corrected answer") | n (1/45 hints) |

*Baseline context (not failures):* Gemma alone found the right first incorrect line in 18/20 cases on the first pass and never approved a wrong line. Across all 26 baseline runs (20 first-pass + 6 repeats), it named the wrong first line in 4 runs (C3 twice, L1 twice).
