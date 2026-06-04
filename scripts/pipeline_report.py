#!/usr/bin/env python3
"""
pipeline_report.py — aggregate job application data into CV improvement suggestions

Usage: python3 scripts/pipeline_report.py
"""

import re
import sys
from collections import Counter
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent))
import jd_gap as jd_gap_module

REPO_ROOT = Path(__file__).parent.parent

STAGES_ORDER = [
    "applied",
    "phone-screen",
    "technical",
    "system-design",
    "take-home",
    "onsite",
    "offer",
]
CLOSED_STAGES = {"rejected", "ghosted", "withdrawn"}

SECTION_MAP = {
    "observability": "Summary or Skills",
    "platform engineering": "Summary or Skills",
    "system design": "Summary or Skills",
    "distributed systems": "Summary or Skills",
    "datadog": "Skills → Core",
    "prometheus": "Skills → Core",
    "grafana": "Skills → Core",
    "sentry": "Skills → Core",
    "opentelemetry": "Skills → Core",
    "open telemetry": "Skills → Core",
    "terraform": "Skills → Core",
    "helm": "Skills → Core",
    "ansible": "Skills → Core",
}


def parse_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n([\s\S]*?)\n---", text)
    if not match:
        return {}
    try:
        return yaml.safe_load(match.group(1)) or {}
    except Exception:
        return {}


def get_missing_terms(jd_file: str, cv_file: str) -> list:
    jd_path = REPO_ROOT / jd_file
    cv_path = REPO_ROOT / cv_file
    if not jd_path.exists() or not cv_path.exists():
        return []
    jd_text = jd_path.read_text(encoding="utf-8")
    cv_text = jd_gap_module.strip_markdown(cv_path.read_text(encoding="utf-8"))
    jd_counts = jd_gap_module.extract_tech_tokens(jd_text)
    return [
        term for term in jd_counts if jd_gap_module.count_in_text(term, cv_text) == 0
    ]


def pct(n: int, d: int) -> str:
    return f"({n / d * 100:.0f}%)" if d > 0 else ""


def main():
    apps_dir = REPO_ROOT / "applications"
    if not apps_dir.exists():
        print("applications/ directory not found.")
        return

    apps = []
    for f in sorted(apps_dir.glob("*.md")):
        if f.name == "pipeline.md":
            continue
        fm = parse_frontmatter(f)
        if fm.get("type") == "application":
            apps.append(fm)

    if not apps:
        print("No application files found. Run new_application.py to add one.")
        return

    total = len(apps)

    # Missing keyword aggregation
    missing_counter: Counter = Counter()
    for app in apps:
        jd_file = str(app.get("jd_file") or "")
        cv_file = str(app.get("cv_version") or "")
        if jd_file and jd_file != "null" and cv_file:
            if not (REPO_ROOT / jd_file).exists() or not (REPO_ROOT / cv_file).exists():
                # Surface dangling references instead of silently dropping the
                # application from gap analysis (finding D1).
                print(
                    f"Warning: application references a missing file "
                    f"(jd_file={jd_file}, cv_version={cv_file}) "
                    f"— excluded from gap analysis",
                    file=sys.stderr,
                )
                continue
            for term in get_missing_terms(jd_file, cv_file):
                missing_counter[term] += 1

    # Outcome signals
    stage_counts: Counter = Counter(str(a.get("stage", "applied")) for a in apps)
    screened = sum(stage_counts.get(s, 0) for s in STAGES_ORDER[1:])
    technical = sum(stage_counts.get(s, 0) for s in STAGES_ORDER[2:])
    offers = stage_counts.get("offer", 0)

    # CV version performance
    cv_perf: dict = {}
    for app in apps:
        cv = str(app.get("cv_version", "unknown"))
        cv_perf.setdefault(cv, {"apps": 0, "screens": 0})
        cv_perf[cv]["apps"] += 1
        if str(app.get("stage", "applied")) not in {"applied"} | CLOSED_STAGES:
            cv_perf[cv]["screens"] += 1

    # Print report. The missing-keyword aggregate below is computed across each
    # application's *tailored* cv_version (not a scan of cv/master.md); a keyword
    # missing from many applications is a strong candidate to add to the master CV.
    print("\n=== MASTER-CV GAP SUGGESTIONS — keywords missing across applications ===")
    if missing_counter:
        for term, count in missing_counter.most_common(20):
            priority = "!!" if count >= 3 else " !"
            section = SECTION_MAP.get(term, "Skills section")
            print(f"  {priority} [{count:2d}/{total} apps]  {term:<32} → {section}")
    else:
        print("  No JD files linked yet — add jd_file paths to application frontmatter")

    print("\n=== OUTCOME SIGNALS ===")
    print(f"  Applications:     {total}")
    print(f"  Phone screen:     {screened:3d}  {pct(screened, total)}")
    print(
        f"  Technical round:  {technical:3d}  {pct(technical, screened) if screened else ''}"
    )
    print(f"  Offer:            {offers:3d}  {pct(offers, total)}")

    print("\n=== CV VERSION PERFORMANCE ===")
    for cv, data in sorted(cv_perf.items(), key=lambda x: -x[1]["apps"]):
        label = cv.replace("cv/versions/", "").replace(".md", "")
        n, screens = data["apps"], data["screens"]
        print(
            f"  {label:<38} {n} app{'s' if n != 1 else ''}  → {screens} screen{'s' if screens != 1 else ''}  {pct(screens, n)}"
        )

    print("\n=== CONCRETE SUGGESTIONS ===")
    high = [(t, c) for t, c in missing_counter.most_common() if c >= 5]
    mid = [(t, c) for t, c in missing_counter.most_common() if 3 <= c < 5]
    low = [(t, c) for t, c in missing_counter.most_common() if 1 <= c < 3]

    if high:
        print("  HIGH (missing in 5+ apps):")
        for t, _ in high:
            print(f'    → Add "{t}" to {SECTION_MAP.get(t, "Skills section")}')
    if mid:
        print("  MEDIUM (missing in 3-4 apps):")
        for t, _ in mid:
            print(f'    → Add "{t}" to {SECTION_MAP.get(t, "Skills section")}')
    if low:
        print("  LOW (missing in 1-2 apps):")
        for t, _ in low[:5]:
            print(f'    → Consider adding "{t}"')
    if not (high or mid or low):
        print(
            "  (not enough data yet — link jd_file in application frontmatter to get suggestions)"
        )

    print()


if __name__ == "__main__":
    main()
