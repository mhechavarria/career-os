#!/usr/bin/env python3
"""End-to-end pipeline runner for the `sample-candidate` worked example.

This drives the *real* Career OS scripts against the fictional "Jordan Rivera"
example data and asserts that every stage of the pipeline works:

    generate_cv  ->  jd_gap  ->  new_application  ->  pipeline_report

How it works
------------
`new_application.py` and `pipeline_report.py` resolve all paths against
`REPO_ROOT = scripts/..`, so they only see data in the *top level* of the repo
that owns the scripts. To exercise them against the example data without
polluting the repository's real top-level folders, this runner assembles a
throwaway working copy in a temp directory:

    <tmp>/profile, experience, impacts, projects, cv, jds, applications   (example data)
    <tmp>/scripts/*.py + cv_style.css                                     (fresh copies)

Every script is then run with `cwd=<tmp>` and repo-relative path arguments, so
`REPO_ROOT` resolves to the temp dir. The framework scripts are copied verbatim
and never modified.

Usage
-----
    python3 examples/run_pipeline.py          # run all stages, print PASS/FAIL
    python3 examples/run_pipeline.py --keep    # keep the temp work dir for inspection
"""

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EXAMPLE_DIR = REPO_ROOT / "examples" / "sample-candidate"
SCRIPTS_DIR = REPO_ROOT / "scripts"

DATA_DIRS = ["profile", "experience", "impacts", "projects", "cv", "jds", "applications"]

# (company, role, level, source, jd, cv) — one per tailored CV.
TARGETS = [
    (
        "Orbital Systems",
        "Senior Go Backend Engineer",
        "Senior",
        "LinkedIn",
        "jds/senior-go-backend.txt",
        "cv/versions/senior-go-backend.md",
    ),
    (
        "Quasar",
        "Staff Backend Engineer",
        "Staff",
        "Greenhouse",
        "jds/staff-distributed-systems.txt",
        "cv/versions/staff-distributed-systems.md",
    ),
    (
        "Lumen Cloud",
        "Platform Engineer Observability",
        "Senior",
        "Referral",
        "jds/platform-observability.txt",
        "cv/versions/platform-observability.md",
    ),
]

TAILORED_CVS = [t[5] for t in TARGETS]


def banner(text: str) -> None:
    print(f"\n{'=' * 72}\n{text}\n{'=' * 72}")


def build_workdir() -> Path:
    """Copy example data + fresh script copies into a temp working repo."""
    work = Path(tempfile.mkdtemp(prefix="career-os-e2e-"))
    for name in DATA_DIRS:
        src = EXAMPLE_DIR / name
        if src.exists():
            shutil.copytree(src, work / name)
    scripts_dst = work / "scripts"
    scripts_dst.mkdir(parents=True, exist_ok=True)
    for f in SCRIPTS_DIR.glob("*.py"):
        shutil.copy2(f, scripts_dst / f.name)
    css = SCRIPTS_DIR / "cv_style.css"
    if css.exists():
        shutil.copy2(css, scripts_dst / css.name)
    return work


def run(work: Path, argv: list) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, *argv], cwd=work, capture_output=True, text=True
    )


def extract_coverage(output: str):
    m = re.search(r"[Kk]eyword coverage\s*:\s*(\d+)", output)
    return int(m.group(1)) if m else None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--keep", action="store_true", help="Keep the temp work dir and print its path"
    )
    args = parser.parse_args()

    if not EXAMPLE_DIR.exists():
        print(f"Example data not found at {EXAMPLE_DIR}", file=sys.stderr)
        return 1

    work = build_workdir()
    print(f"Work dir: {work}")
    results = []  # (stage, ok, detail)

    # --- Stage 1: generate_cv (master + each tailored CV) --------------------
    banner("STAGE 1 — generate_cv.py (render ATS PDFs)")
    for cv in ["cv/master.md", *TAILORED_CVS]:
        proc = run(work, ["scripts/generate_cv.py", cv])
        pdf = work / Path(cv).with_suffix(".pdf")
        ok = proc.returncode == 0 and pdf.exists() and pdf.stat().st_size > 0
        warn = "ATS WARNINGS" in proc.stderr
        page = re.search(r"\((\d+) pages?\)", proc.stdout)
        detail = f"{page.group(0) if page else '?'}{'  [ATS warnings]' if warn else ''}"
        print(f"  {'OK ' if ok else 'FAIL'}  {cv:<42} {detail}")
        if proc.stderr.strip():
            print("        " + proc.stderr.strip().replace("\n", "\n        "))
        results.append((f"generate_cv {cv}", ok, detail))

    # --- Stage 2: jd_gap (each JD vs its tailored CV) ------------------------
    banner("STAGE 2 — jd_gap.py (JD vs CV keyword coverage)")
    for company, _role, _level, _source, jd, cv in TARGETS:
        proc = run(work, ["scripts/jd_gap.py", jd, cv])
        cov = extract_coverage(proc.stdout)
        ok = proc.returncode == 0 and cov is not None
        print(f"  {'OK ' if ok else 'FAIL'}  {company:<18} coverage={cov}%   ({jd})")
        results.append((f"jd_gap {company}", ok, f"coverage={cov}%"))

    # --- Stage 3: new_application (bootstrap + auto gap + auto PDF) ----------
    banner("STAGE 3 — new_application.py (bootstrap application files)")
    for company, role, level, source, jd, cv in TARGETS:
        proc = run(
            work,
            [
                "scripts/new_application.py",
                "--company", company,
                "--role", role,
                "--level", level,
                "--source", source,
                "--jd", jd,
                "--cv", cv,
                "--remote",
            ],
        )
        cov = extract_coverage(proc.stdout)
        ok = proc.returncode == 0
        print(f"  {'OK ' if ok else 'FAIL'}  {company:<18} {proc.stdout.strip().splitlines()[0] if proc.stdout.strip() else ''}")
        if proc.stderr.strip():
            print("        " + proc.stderr.strip().replace("\n", "\n        "))
        results.append((f"new_application {company}", ok, f"coverage={cov}%"))

    app_files = [p for p in (work / "applications").glob("*.md") if p.name != "pipeline.md"]
    apps_ok = len(app_files) == len(TARGETS)
    print(f"\n  {'OK ' if apps_ok else 'FAIL'}  {len(app_files)} application file(s) created (expected {len(TARGETS)})")
    results.append(("application files created", apps_ok, f"{len(app_files)}/{len(TARGETS)}"))

    # --- Stage 4: pipeline_report (aggregate across all applications) -------
    banner("STAGE 4 — pipeline_report.py (aggregate gaps + funnel)")
    proc = run(work, ["scripts/pipeline_report.py"])
    report_ok = proc.returncode == 0 and "OUTCOME SIGNALS" in proc.stdout
    print(proc.stdout.rstrip())
    if proc.stderr.strip():
        print(proc.stderr.strip(), file=sys.stderr)
    results.append(("pipeline_report", report_ok, "ok" if report_ok else "no report"))

    # --- Summary -------------------------------------------------------------
    banner("SUMMARY")
    passed = sum(1 for _, ok, _ in results if ok)
    for stage, ok, detail in results:
        print(f"  [{'PASS' if ok else 'FAIL'}]  {stage:<34} {detail}")
    all_ok = passed == len(results)
    print(f"\n  {passed}/{len(results)} stages passed — {'ALL STAGES PASSED' if all_ok else 'FAILURES PRESENT'}")

    if args.keep:
        print(f"\nWork dir kept at: {work}")
    else:
        shutil.rmtree(work, ignore_errors=True)

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
