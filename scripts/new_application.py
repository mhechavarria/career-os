#!/usr/bin/env python3
"""
new_application.py — bootstrap a new job application file

Usage:
    python3 scripts/new_application.py \
      --company "Nango" \
      --role "Staff Backend Engineer" \
      --cv cv/versions/nango-staff-backend.md \
      --level Staff \
      --source LinkedIn \
      [--jd jds/nango-staff-backend.txt] \
      [--url "https://..."] \
      [--remote] \
      [--no-pdf]

A company-named PDF is generated automatically alongside the application file,
e.g. cv/versions/mariano-echavarria-nango.pdf. Pass --no-pdf to skip.
"""

import argparse
import contextlib
import io
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import jd_gap

REPO_ROOT = Path(__file__).parent.parent


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def extract_name_slug(cv_path: Path) -> str:
    """Extract candidate name from the CV's first H1 heading and slugify it."""
    try:
        text = cv_path.read_text(encoding="utf-8")
        match = re.search(r"^# (.+)$", text, re.MULTILINE)
        if match:
            return slugify(match.group(1).strip())
    except Exception:
        pass
    return "cv"


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
        jd_dst = jds_dir / f"{slug}.txt"

        if jd_src.resolve() != jd_dst.resolve() and jd_src.exists():
            jd_dst.write_text(jd_src.read_text(encoding="utf-8"), encoding="utf-8")

        jd_path_to_use = jd_dst if jd_dst.exists() else jd_src
        cv_path = REPO_ROOT / args.cv

        if jd_path_to_use.exists() and cv_path.exists():
            jd_file_ref = f"jds/{slug}.txt"
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                try:
                    coverage = jd_gap.run(str(jd_path_to_use), str(cv_path))
                except Exception as e:
                    buf.write(f"[Gap analysis error: {e}]\n")
            gap_section = f"```\n{buf.getvalue().strip()}\n```"
        else:
            print(
                f"Warning: JD file not found at {jd_path_to_use} — skipping gap analysis"
            )

    location = "Remote" if args.remote else args.location

    # Generate company-named PDF
    cv_pdf_ref = "null"
    if not args.no_pdf:
        cv_path = REPO_ROOT / args.cv
        if cv_path.exists():
            name_slug = extract_name_slug(cv_path)
            pdf_name = f"{name_slug}-{company_slug}.pdf"
            pdf_path = cv_path.parent / pdf_name
            result = subprocess.run(
                [
                    sys.executable,
                    str(REPO_ROOT / "scripts" / "generate_cv.py"),
                    str(cv_path),
                    "--output",
                    str(pdf_path),
                ],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                cv_pdf_ref = f"{Path(args.cv).parent}/{pdf_name}"
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
keyword_coverage: {coverage if coverage is not None else "null"}
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
        print(f"    Keyword coverage: {coverage}%")
    if cv_pdf_ref != "null":
        print(f"    PDF: {cv_pdf_ref}")
    if jd_file_ref == "null":
        print(f"\n  Add JD to jds/{slug}.txt then run:")
        print(f"    python3 scripts/jd_gap.py jds/{slug}.txt {args.cv}")
    print("\n  Update 'stage' in frontmatter as the application progresses.")
    print("  Run python3 scripts/pipeline_report.py for aggregate insights.\n")


if __name__ == "__main__":
    main()
