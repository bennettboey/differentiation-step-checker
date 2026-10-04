# Differentiation Step-Checker

**HCI Mini Project · Theme: Learning**

A local tool for IB Mathematics HL students: you enter a function and your line-by-line working for its derivative, and it finds the **first incorrect line** and explains the likely mistake.

- **SymPy** (a non-AI computer algebra library) is the only judge of correctness.
- **Gemma 4 (`gemma4:e2b`)**, running locally through Ollama, only explains a mistake SymPy has already found. Its explanation is shown as a hint that may not be 100% accurate.
- No cloud APIs. Everything runs on your computer, and it works offline.

**Model:** gemma4:e2b · **Approach:** Pipeline (LLM + symbolic verifier) · **Tested on:** Windows 11 Home, Intel i7-13620H, NVIDIA RTX 4060 Laptop (8 GB VRAM), 16 GB RAM, Python 3.11.5

---

## 1. Setup

You need **Python 3.9 or newer** and about **5 GB of free disk space** for the model.

**Step 1: Install Ollama**

- **Windows** (PowerShell):
  ```
  irm https://ollama.com/install.ps1 | iex
  ```
- **macOS / Linux:**
  ```
  curl -fsSL https://ollama.com/install.sh | sh
  ```

Then open a **new** terminal so the `ollama` command is found. Installers for all systems are also at https://ollama.com/download.

**Step 2: Download the model** (about 4.6 GB, one time)
```
ollama pull gemma4:e2b
```

**Step 3: Install the Python dependency** (SymPy, about 7 MB)

From this folder, run:
```
python -m pip install -r requirements.txt
```
On macOS / Linux, use `python3` instead of `python` here and in every command below.

**Step 4: Check the install**
```
python check_test_cases.py
```
This should end with `20 cases, 0 mismatches`.

---

## 2. Run the step-checker

```
python app.py
```
Open **http://localhost:8000** in a browser. Press `Ctrl+C` in the terminal to stop.

Ollama must be running for hints. It starts automatically after installing on Windows and macOS; on Linux, run `ollama serve` in another terminal if needed. Checking works even without Ollama.

### Using it
1. Type f(x), or choose one of the 20 test cases from **Load a test case**. For implicit differentiation, type an equation such as `x^2 + y^2 = 25`.
2. Type your working for f'(x), **one line per row**.
   - Write powers with `^`, and functions with brackets: `x^2`, `sin(3x)^2`, `ln(x)`, `e^(2x)`, `sqrt(x)`, `arctan(x)`.
3. Check the **"This is what your working looks like."** preview. Typos such as `sinx` are flagged there, and **Check** stays disabled until they're fixed.
4. Click **Check my working**. SymPy's verdict appears immediately for each line:
   - ✓ **Correct**
   - ✗ **Incorrect** (the first one is where the mistake happened)
   - ↳ **Carries the mistake** (it follows correctly from the wrong line, so only the first error needs fixing)
   - ? **Couldn't confirm** (SymPy couldn't decide, so it says so instead of guessing)
5. A few seconds later, Gemma's hint appears: a one-sentence explanation with a small "Possible type" label, marked **"may not be 100% accurate"**.
   - **Show the correct step** shows the corrected version of the wrong line. Gemma writes it, and it is shown **only if SymPy confirms it is correct**. If SymPy rejects it, Gemma is asked again (up to 3 tries, told which attempts failed); if all fail, a **Try again** button asks for more. An unverified step is never shown.

Hints and step checks are logged to `results/pipeline_log.jsonl`.

### Optional settings

Set these before running `python app.py`:

| Setting | Effect | Windows (PowerShell) | macOS / Linux |
|---|---|---|---|
| `STEPCHECK_THINK` | `false` turns Gemma's thinking off for hints. It's on by default: it doubled correct diagnoses in testing, for ~3 s more. | `$env:STEPCHECK_THINK="false"` | `export STEPCHECK_THINK=false` |
| `STEPCHECK_MODEL` | Use another model tag, e.g. `gemma4:e4b` | `$env:STEPCHECK_MODEL="gemma4:e4b"` | `export STEPCHECK_MODEL=gemma4:e4b` |

---

## 3. Reproduce the evaluation

All three scripts use only the local model. Results are **appended** to the files in `results/`, so the original runs stay in place. Timings depend heavily on hardware and power: on the test laptop, Gemma was about 6x slower on battery.

| Command | What it does | Time on the test laptop (plugged in) |
|---|---|---|
| `python check_test_cases.py` | Confirms every label in `data/test_cases.json` with SymPy | a few seconds |
| `python run_baseline.py` | **Baseline:** asks Gemma *alone* (no SymPy) to judge each case's working, saving raw answers to `results/baseline_raw.jsonl`. Add case IDs to run only those, e.g. `python run_baseline.py C3 L1`. | ~3-8 min |
| `python run_pipeline.py` | **Pipeline:** SymPy verdict, then Gemma hint, for the 15 cases with a mistake (3 runs each, thinking off and on). Saves to `results/pipeline_eval.jsonl` and prints a summary. Options: `--runs 1`, `--think on`. | ~5-10 min |

### Results summary

| | Gemma alone (baseline) | Pipeline |
|---|---|---|
| Found the right first incorrect line | 18/20 cases on the first pass; inconsistent on repeats (L1: 3 different answers in 3 runs) | 15/15 cases, every run (SymPy) |
| Rejected a correct line | C3 and L1 | never |
| Named the error type correctly | – | 33% (thinking off), 62–69% (thinking on) |
| Verified next step found | – | 45/45 runs (43 first try, 2 after a retry); an unverified step is never shown |
| Time to verdict | 22–77 s on battery, 7–23 s plugged in | under 0.4 s (hint after ~5 s) |

Details: `baseline_prompts.md`, `pipeline_results.md`, and the Model Limits Log in `limits_log.md`.

---

## 4. How it works

```
student input ──► verifier.py (SymPy, no AI)
                    • computes the true derivative
                    • checks each line: symbolic → numeric spot-check → "couldn't confirm"
                    • marks the first incorrect line ──► shown immediately
                              │
                              ▼
                  explainer.py (Gemma 4 via Ollama)
                    • told SymPy's verdict is certain; given the wrong line + correct derivative
                    • picks an error type from a fixed list + writes one sentence + a corrected line (JSON schema)
                    • one retry, then a fixed fallback message; LaTeX cleaned to plain text
                              │
                              ▼
                  pipeline.py: SymPy checks Gemma's corrected line; if wrong, Gemma retries (up to 3)
                    ──► shown only once SymPy confirms it
                              │
                              ▼
                  hint shown as "may not be 100% accurate" ──► student can ask for the correct step
```

## 5. Files

| File | Purpose |
|---|---|
| `app.py`, `static/index.html` | The local web app (Python standard library only) |
| `pipeline.py` | Runs the pipeline: SymPy verdict → Gemma hint → corrected step, retried until SymPy verifies it |
| `verifier.py` | SymPy verifier: parsing, true derivative, line-by-line equivalence checks. No AI. |
| `explainer.py` | Gemma layer: prompt, JSON schema, retry/fallback, LaTeX clean-up, logging |
| `data/test_cases.json` | 20 differentiation cases (5 correct, 15 with one planted mistake), labelled |
| `check_test_cases.py` | Verifies the test labels with SymPy |
| `run_baseline.py`, `run_pipeline.py` | Evaluation scripts (section 3) |
| `baseline_prompts.md` | Baseline prompts, results table, consistency repeats and answer key |
| `pipeline_results.md` | Pipeline evaluation results and observations |
| `limits_log.md` | Model Limits Log, with every row from a real run |
| `ai_use_log.md` | Record of what AI tools (Claude Code) did in this project |
| `results/` | Raw logs: `baseline_raw.jsonl`, `pipeline_eval.jsonl`, `pipeline_eval_calls.jsonl`, `smoke_test_log.jsonl`, `pipeline_log.jsonl` |
| `requirements.txt` | Python dependency (SymPy) |
