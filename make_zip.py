"""Build the submission zip (for Bennett; not included in the zip itself).

Run:  python make_zip.py   ->  dist/differentiation-step-checker.zip
"""
import zipfile
from pathlib import Path

HERE = Path(__file__).parent
NAME = "differentiation-step-checker"
INCLUDE = [
    "README.md", "requirements.txt", "app.py", "pipeline.py", "verifier.py", "explainer.py",
    "check_test_cases.py", "run_baseline.py", "run_pipeline.py",
    "static/index.html", "data/test_cases.json",
    "baseline_prompts.md", "pipeline_results.md", "limits_log.md", "ai_use_log.md",
]
INCLUDE_DIRS = ["results"]  # every file inside


def main():
    files = [HERE / f for f in INCLUDE]
    for d in INCLUDE_DIRS:
        files += sorted(p for p in (HERE / d).rglob("*") if p.is_file())
    missing = [str(f) for f in files if not f.exists()]
    if missing:
        raise SystemExit(f"Missing files: {missing}")
    out = HERE / "dist" / f"{NAME}.zip"
    out.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for f in files:
            z.write(f, f"{NAME}/{f.relative_to(HERE).as_posix()}")
    print(f"Wrote {out} ({len(files)} files, {out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
