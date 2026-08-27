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
    "placed",
]
# Negative terminal stages (used to exclude non-progress outcomes from screen
# counts). The positive terminal `placed` is intentionally NOT here — a placed
# application advanced all the way through, so it counts as progress.
CLOSED_STAGES = {"rejected", "ghosted", "withdrawn"}

# Pre-submission stages. A file in one of these is tailored work in progress
# that was never sent, so it has no outcome to measure: counting it as an
# application would depress every conversion rate and counting it as a screen
# would inflate CV performance. It stays out of both and is reported separately.
PRE_SUBMISSION_STAGES = {"draft"}

# Current-state stages that are not positions in the lifecycle: the application
# is parked by the employer, not advancing and not closed. `furthest_stage` is
# what records how far it had got before it stopped.
PARKED_STAGES = {"on-hold"}

# The whole vocabulary. Anything outside it is a typo or an invented stage, and
# an unrecognised stage silently skews the rates below — which is exactly how
# `on-hold` came to be counted as a screen in one table and not the other.
KNOWN_STAGES = set(STAGES_ORDER) | CLOSED_STAGES | PRE_SUBMISSION_STAGES | PARKED_STAGES

# Every stage at or past a first conversation. One definition, used by both the
# outcome signals and the CV performance table — they used to disagree.
SCREENED_STAGES = set(STAGES_ORDER[1:])


def furthest_stage(app: dict) -> str:
    """How far an application GOT, independent of where it now IS.

    `stage` records current state, so a rejection, a freeze or a withdrawal
    overwrites the high-water mark. An application that reached a recruiter
    screen and then closed on an eligibility gap, and one that screened before
    the employer froze the requisition, both look under `stage` alone as though
    they never got past the application. The reach is therefore recorded
    separately in `furthest_stage`.

    It is a HIGH-WATER MARK, so it is whichever of the two fields is further
    along the lifecycle, never the declared one on its own. Every file the
    generator creates starts at `furthest_stage: applied`, and an application
    that advances only ever has `stage` moved by hand; trusting the declared
    value blindly would report no progression at all for anyone who does not
    maintain a second field.
    """
    # A pre-submission file has no reach at all, and must never inherit one
    # from the fallbacks below.
    stage = str(app.get("stage", "applied"))
    if stage in PRE_SUBMISSION_STAGES:
        return ""
    declared = str(app.get("furthest_stage") or "").strip()
    if declared == "null":
        declared = ""
    # Compare only values that are positions in the lifecycle: a closed or
    # parked `stage` proves nothing about reach, and neither does a typo.
    positions = [s for s in (declared, stage) if s in STAGES_ORDER]
    if positions:
        return max(positions, key=STAGES_ORDER.index)
    # Nothing usable on either side: a file predating the field and parked or
    # closed is credited only with having been applied to.
    return "applied"


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

    # Drafts were tailored but never submitted. Keep them in the gap analysis
    # (the CV work is real) and out of every outcome rate (the outcome is not).
    drafts = [
        a for a in apps if str(a.get("stage", "applied")) in PRE_SUBMISSION_STAGES
    ]
    submitted = [a for a in apps if a not in drafts]

    tailored = len(apps)
    total = len(submitted)

    for app in apps:
        company = app.get("company", "unknown")
        stage = str(app.get("stage", "applied"))
        if stage not in KNOWN_STAGES:
            # Report the reach that was actually computed, never a claim about
            # what it will be. The first wording said the record would not count
            # toward any rate, which was false. The second said its reach falls
            # back to `applied` and so can never be a screen, which is false
            # whenever `furthest_stage` holds a valid value — the rate printed
            # a few lines below then contradicted the warning on the same
            # screen. An interpolated value cannot disagree with itself.
            print(
                f"Warning: {company} has an unrecognised stage '{stage}' "
                f"— it still counts as an application, and its reach reads as "
                f"'{furthest_stage(app)}'; set furthest_stage if that is wrong",
                file=sys.stderr,
            )
        reach = str(app.get("furthest_stage") or "").strip()
        if reach and reach != "null" and reach not in STAGES_ORDER:
            print(
                f"Warning: {company} has an unrecognised furthest_stage "
                f"'{reach}' — expected one of {', '.join(STAGES_ORDER)}",
                file=sys.stderr,
            )

    # Missing keyword aggregation
    missing_counter: Counter = Counter()
    for app in apps:
        jd_file = str(app.get("jd_file") or "")
        cv_file = str(app.get("cv_version") or "")
        if jd_file and jd_file != "null" and cv_file:
            if not (REPO_ROOT / jd_file).exists() or not (REPO_ROOT / cv_file).exists():
                # Surface dangling references instead of silently dropping the
                # application from gap analysis (finding D1).
                #
                # `get_missing_terms` guards the same two paths and returns []
                # for them, so this `continue` is belt-and-braces: replacing it
                # with `pass` produces byte-identical output. It stays because
                # the intent is not to rely on that, and because the check that
                # produces the warning should also be the one that acts on it.
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
    # Counted on reach, not on current state: an application that screened and
    # was then rejected still screened.
    reach_counts: Counter = Counter(furthest_stage(a) for a in submitted)
    screened = sum(reach_counts.get(s, 0) for s in STAGES_ORDER[1:])
    technical = sum(reach_counts.get(s, 0) for s in STAGES_ORDER[2:])
    placed = reach_counts.get("placed", 0)
    # A placement implies an offer, so count it toward offers too.
    offers = reach_counts.get("offer", 0) + placed

    # CV version performance
    cv_perf: dict = {}
    for app in submitted:
        cv = str(app.get("cv_version", "unknown"))
        cv_perf.setdefault(cv, {"apps": 0, "screens": 0})
        cv_perf[cv]["apps"] += 1
        if furthest_stage(app) in SCREENED_STAGES:
            cv_perf[cv]["screens"] += 1

    # Print report. The missing-keyword aggregate below is computed across each
    # application's *tailored* cv_version (not a scan of cv/master.md); a keyword
    # missing from many applications is a strong candidate to add to the master CV.
    print("\n=== MASTER-CV GAP SUGGESTIONS — keywords missing across applications ===")
    if missing_counter:
        for term, count in missing_counter.most_common(20):
            priority = "!!" if count >= 3 else " !"
            section = SECTION_MAP.get(term, "Skills section")
            print(f"  {priority} [{count:2d}/{tailored} apps]  {term:<32} → {section}")
    else:
        print("  No JD files linked yet — add jd_file paths to application frontmatter")

    print("\n=== OUTCOME SIGNALS ===")
    print(f"  Applications:     {total}")
    for draft in drafts:
        print(
            f"  ! NOT SUBMITTED:  {draft.get('company', 'unknown')}"
            f" — {draft.get('role', 'unknown')} (stage: draft, excluded from rates)"
        )
    print(f"  Phone screen:     {screened:3d}  {pct(screened, total)}")
    print(
        f"  Technical round:  {technical:3d}  {pct(technical, screened) if screened else ''}"
    )
    print(f"  Offer:            {offers:3d}  {pct(offers, total)}")
    print(f"  Placed:           {placed:3d}  {pct(placed, total)}")

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
