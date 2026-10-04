# AI-Use Log (for the report's AI-Use Acknowledgment)

Running record of what Claude Code (Anthropic) did in this project. Bennett reviews and edits everything.

| Date | What Claude Code did |
|---|---|
| 2026-10-04 | Installed Ollama and pulled `gemma4:e2b`; checked hardware against Ollama's GPU docs; measured first-call and warm latency. |
| 2026-10-04 | Drafted the 20 test cases in `data/test_cases.json` (functions, working lines, labels). |
| 2026-10-04 | Wrote `check_test_cases.py`, which verifies the labels with SymPy. It caught one wrong label that Claude had written (case W1, line 1); that line was fixed. |
| 2026-10-04 | Wrote `README.md`: setup, how to operate Gemma manually, and the video-making guide. |
| 2026-10-04 | Generated `baseline_prompts.md` (prompts, results table and answer key from the test cases) and a blank `limits_log.md` template; wrote the manual baseline steps in the README. Bennett runs the baseline himself. |
| 2026-10-04 | Wrote `run_baseline.py` and ran baseline cases Q2-M2 through local Gemma at Bennett's request (Bennett ran P1-Q1 himself). Checked each Gemma verdict against the answer key and filled in the results table and Limits Log rows. **The report's AI-Use Acknowledgment must say that Claude Code ran 15 of the 20 baseline cases.** |
| 2026-10-04 | Ran the 3x consistency repeats (C3, L1, Q3) at Bennett's request and recorded the results. |
| 2026-10-04 | Built the pipeline: `verifier.py` (SymPy checker), `explainer.py` (Gemma hint layer), `app.py` + `static/index.html` (local web app); refactored `check_test_cases.py` to use the verifier. Tested it in the browser and ran 3 real Gemma hint calls (logged). Design choices made by Claude Code for Bennett to review: thinking off for hints, hint must not give the full answer, a stdlib web app instead of Streamlit (to avoid a ~100 MB download and work offline). |
| 2026-10-04 | Wrote the Scenario section (persona Ben) at Bennett's request, based on the built app and a real Gemma hint from testing. |
| 2026-10-04 | Wrote and ran `run_pipeline.py` (task 5: 90 Gemma hint calls), read all 90 hints, wrote `pipeline_results.md`, and filled in the Limits Log's mitigation and helped columns. |
| 2026-10-04 | At Bennett's request: thinking on by default, hint sentence as headline with a small "Possible type" label, plain-text prompt line + `clean_hint` LaTeX clean-up; re-ran the thinking-on evaluation (45 calls) to measure it. |
| 2026-10-04 | Submission prep: code review (fixed the LaTeX clean-up for `\right`, `\frac` and `\beta`, blocked Python built-ins in student input, accepted `f(x) =` and `abs()`, removed unused code), rewrote README.md for markers, moved the video notes to VIDEO_GUIDE.md, wrote make_zip.py, and tested the zip from a clean folder. |
| 2026-10-04 | At Bennett's request: added the correct-next-step feature (Gemma writes the corrected line, SymPy verifies it before it is shown; prompt v3), switched the preview to MathML, fixed the test-case dropdown, renamed the preview heading; re-ran the thinking-on evaluation (45 calls). |
| 2026-10-04 | At Bennett's request: replaced the final-answer fallback with retries (`pipeline.py`: Gemma retries the corrected step, up to 3 per request, until SymPy verifies it; page Try again button); re-ran the thinking-on evaluation (45 runs). |
| 2026-10-04 | At Bennett's request: removed the Got it / This isn't my mistake buttons and the click logging behind them, and changed the hint label to "may not be 100% accurate". |
