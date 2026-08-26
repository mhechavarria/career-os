#!/usr/bin/env python3
"""
new_application.py — bootstrap a new job application file

Usage:
    python3 scripts/new_application.py \
      --company "Acme" \
      --role "Staff Backend Engineer" \
      --cv cv/versions/acme-staff-backend.md \
      --level Staff \
      --source LinkedIn \
      [--jd jds/acme-staff-backend.txt] \
      [--url "https://..."] \
      [--remote] \
      [--no-pdf]

A PDF is generated automatically alongside the application file, named the same
way generate_cv.py names it: <your-name>-<cv-stem>.pdf, e.g.
cv/versions/<your-name>-acme-staff-backend.pdf. Pass --no-pdf to skip.
"""

import argparse
import contextlib
import io
import re
import subprocess
import sys
import unicodedata
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import jd_gap

REPO_ROOT = Path(__file__).parent.parent


def slugify(text: str) -> str:
    # NFKD-normalize and drop combining marks so accented characters
    # transliterate to ASCII (José → jose) instead of being stripped to
    # hyphens (jos-) and mangling the resulting filename.
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def main():
    parser = argparse.ArgumentParser(
        description="Bootstrap a new job application file."
    )
    parser.add_argument("--company", required=True, help="Company name")
    parser.add_argument("--role", required=True, help="Role title")
    parser.add_argument(
        "--cv",
        required=True,
        help="Path to tailored CV markdown (e.g. cv/versions/foo.md)",
    )
    parser.add_argument(
        "--level",
        default="Senior",
        choices=["Junior", "Mid", "Senior", "Staff", "Principal"],
    )
    parser.add_argument(
        "--source",
        default="LinkedIn",
        choices=[
            "LinkedIn",
            "Greenhouse",
            "Lever",
            "Ashby",
            "Referral",
            "Direct",
            "Other",
        ],
    )
    parser.add_argument("--jd", default=None, help="Path to JD text file (optional)")
    parser.add_argument("--url", default="", help="Job posting URL")
    parser.add_argument("--remote", action="store_true", help="Flag if role is remote")
    parser.add_argument(
        "--location", default="Remote", help="Location (default: Remote)"
    )
    parser.add_argument("--no-pdf", action="store_true", help="Skip PDF generation")
    args = parser.parse_args()

    today = date.today()
    month_str = today.strftime("%Y-%m")
    company_slug = slugify(args.company)
    role_slug = slugify(args.role)
    slug = f"{company_slug}-{role_slug}"
    out_path = REPO_ROOT / "applications" / f"{slug}-{month_str}.md"

    if out_path.exists():
        print(f"File already exists: {out_path.relative_to(REPO_ROOT)}")
        sys.exit(1)

    # Handle JD file
    jd_file_ref = "null"
    gap_section = (
        "<!-- Run: python3 scripts/jd_gap.py <jd.txt> cv/versions/<slug>.md -->"
    )

    coverage = None
    if args.jd:
        jd_src = Path(args.jd)
        jds_dir = REPO_ROOT / "jds"
        jds_dir.mkdir(parents=True, exist_ok=True)

        # If the JD already lives in jds/, reuse it in place. Copying it to a
        # second jds/<company>-<role>.txt produced two byte-identical JDs
        # whenever the user's slug differed from <company>-<role> (finding C1).
        src_in_jds = jd_src.exists() and jds_dir.resolve() in jd_src.resolve().parents
        if src_in_jds:
            jd_path_to_use = jd_src
            jd_ref_path = jd_src.resolve().relative_to(REPO_ROOT.resolve())
        else:
            jd_dst = jds_dir / f"{slug}.txt"
            if jd_src.exists() and jd_src.resolve() != jd_dst.resolve():
                jd_dst.write_text(jd_src.read_text(encoding="utf-8"), encoding="utf-8")
            jd_path_to_use = jd_dst if jd_dst.exists() else jd_src
            jd_ref_path = Path("jds") / f"{slug}.txt"

        cv_path = REPO_ROOT / args.cv

        if jd_path_to_use.exists() and cv_path.exists():
            jd_file_ref = jd_ref_path.as_posix()
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                try:
                    coverage = jd_gap.run(str(jd_path_to_use), str(cv_path))
                except Exception as e:
                    buf.write(f"[Gap analysis error: {e}]\n")
            # Strip the machine-specific repo path so the committed application
            # file shows portable, repo-relative JD/CV references.
            report = buf.getvalue().strip().replace(f"{REPO_ROOT}/", "")
            gap_section = f"```\n{report}\n```"
        else:
            print(
                f"Warning: JD file not found at {jd_path_to_use} — skipping gap analysis",
                file=sys.stderr,
            )

    location = "Remote" if args.remote else args.location

    # Generate company-named PDF
    cv_pdf_ref = "null"
    if not args.no_pdf:
        cv_path = REPO_ROOT / args.cv
        if cv_path.exists():
            # Let generate_cv.py name the file and report where it put it, rather
            # than predicting the name here. Predicting it means a second copy of
            # the naming rule, and the two drifted once already — this built
            # <name>-<company>.pdf while the generator defaulted to
            # <name>-<cv-stem>.pdf, so every application produced two PDFs of the
            # same CV. One owner of the rule is the only version that cannot drift.
            result = subprocess.run(
                [
                    sys.executable,
                    str(REPO_ROOT / "scripts" / "generate_cv.py"),
                    str(cv_path),
                ],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                done = re.search(r"Done →\s+(\S.*?)\s+\(\d+ pages?\)", result.stdout)
                if done:
                    pdf_path = Path(done.group(1))
                    with contextlib.suppress(ValueError):
                        cv_pdf_ref = str(pdf_path.relative_to(REPO_ROOT).as_posix())
                if cv_pdf_ref == "null":
                    print(
                        "Warning: could not read the rendered PDF path from "
                        "generate_cv.py output",
                        file=sys.stderr,
                    )
                if result.stderr.strip():
                    print(result.stderr.strip(), file=sys.stderr)
            else:
                print(
                    f"Warning: PDF generation failed — {result.stderr.strip()}",
                    file=sys.stderr,
                )
        else:
            print(
                f"Warning: CV file not found at {cv_path} — skipping PDF generation",
                file=sys.stderr,
            )

    content = f"""---
type: application
company: {args.company}
role: {args.role}
level: {args.level}
source: {args.source}
url: {args.url}
jd_file: {jd_file_ref}
cv_version: {args.cv}
cv_pdf: {cv_pdf_ref}
applied_date: {today.isoformat()}
status: active
stage: applied
furthest_stage: applied
tech_keyword_coverage: {coverage if coverage is not None else "null"}
resume_worded_score: null
salary_min: null
salary_max: null
currency: USD
remote: {str(args.remote).lower()}
location: {location}
tags: []
---

## Gap Analysis

{gap_section}

## Pipeline Timeline

- {today.isoformat()} · Applied

## Interview Notes

<!-- One subsection per round, e.g.: -->
<!--
### Round 1 — Phone Screen (date)
- Interviewer:
- Topics covered:
- My answers:
- Questions I asked:
-->

## Outcome

- Result: <!-- advanced | rejected | offer | withdrawn | ghosted -->
- Stage reached:
- Reason given:
- Closed date:

## Learnings

## Feedback Loop

- [ ]
- [ ]
"""

    out_path.write_text(content, encoding="utf-8")

    rel = out_path.relative_to(REPO_ROOT)
    print(f"\nCreated: {rel}")
    if coverage is not None:
        print(f"    Tech keyword coverage: {coverage}%")
    if cv_pdf_ref != "null":
        print(f"    PDF: {cv_pdf_ref}")
    if jd_file_ref == "null":
        print(f"\n  Add JD to jds/{slug}.txt then run:")
        print(f"    python3 scripts/jd_gap.py jds/{slug}.txt {args.cv}")
    print("\n  Update 'stage' in frontmatter as the application progresses.")
    print("  Run python3 scripts/pipeline_report.py for aggregate insights.\n")


if __name__ == "__main__":
    main()
