#!/usr/bin/env python3
"""
prepare_release.py — finalize a Career OS release safely (maintainers only).

This is the "prepare" half of a release. It runs the same guards as
``.github/workflows/release.yml`` *locally*, before any tag is pushed, and does
the error-prone CHANGELOG surgery for you:

  * move the accumulated ``## [Unreleased]`` notes into a dated ``## [X.Y.Z]``
    section, leaving a fresh empty ``[Unreleased]`` heading above it;
  * refresh the Keep-a-Changelog link references at the foot of the file (point
    ``[Unreleased]`` at the new tag and add the ``[X.Y.Z]`` compare link).

It also adds one guard of its own: every PR squash-merged since the last tag must
be mentioned in ``[Unreleased]``. The release notes are generated from that
section, so a PR that merged without an entry ships invisible — which is exactly
how the toolchain pins of #39 nearly went out unannounced. The check runs here
rather than in CI because it is the only place that catches **dependabot** PRs,
which will never write an entry for themselves. Override it deliberately with
``--allow-missing-entries``.

It never pushes and never creates the GitHub Release — ``release.yml`` does that
from the CHANGELOG when the tag is pushed.

Usage:
    # phase 1 — on a release branch: rewrite CHANGELOG.md and commit
    python3 maintainers/prepare_release.py --bump minor --commit
    #   ...push, open a PR, and squash-merge it...
    # phase 2 — on an up-to-date main: tag the merged release commit
    python3 maintainers/prepare_release.py --version 1.4.0 --tag

By default it only rewrites CHANGELOG.md and prints the remaining steps.
``--commit`` and ``--tag`` are deliberately *separate phases*: under a
squash-merge the branch commit's SHA changes when the PR lands, so a tag made
on the branch would not be an ancestor of main (``release.yml`` would reject
it). ``--commit`` makes the release commit on the current branch; ``--tag``
runs later, on main, and tags the already-merged commit. Neither pushes.
"""

import argparse
import datetime as dt
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CHANGELOG = REPO_ROOT / "CHANGELOG.md"

VERSION_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


class ReleaseError(Exception):
    """A guard failed — abort the release with a clear message."""


# --- version helpers --------------------------------------------------------


def parse_version(text: str) -> tuple[int, int, int]:
    """Parse 'X.Y.Z' (or 'vX.Y.Z') into a (major, minor, patch) tuple."""
    m = VERSION_RE.match(text.strip().lstrip("v"))
    if not m:
        raise ReleaseError(f"'{text}' is not a valid X.Y.Z version")
    return (int(m[1]), int(m[2]), int(m[3]))


def format_version(parts: tuple[int, int, int]) -> str:
    return "{}.{}.{}".format(*parts)


def bump_version(parts: tuple[int, int, int], part: str) -> tuple[int, int, int]:
    major, minor, patch = parts
    if part == "major":
        return (major + 1, 0, 0)
    if part == "minor":
        return (major, minor + 1, 0)
    if part == "patch":
        return (major, minor, patch + 1)
    raise ReleaseError(f"unknown bump part: {part}")


def resolve_version(latest: str | None, version: str | None, bump: str | None) -> str:
    """Resolve the target version from --version, or --bump + the latest tag."""
    if version:
        return format_version(parse_version(version))
    if not latest:
        raise ReleaseError("no existing tag to --bump from; pass --version X.Y.Z")
    return format_version(bump_version(parse_version(latest), bump))


def assert_increasing(version: str, latest: str | None) -> None:
    if latest and parse_version(version) <= parse_version(latest):
        raise ReleaseError(
            f"version {version} is not greater than the latest tag {latest}"
        )


# --- changelog surgery ------------------------------------------------------


def unreleased_body(text: str) -> str:
    """Return the notes under [Unreleased], stopping at the next version
    section, the link-reference block, or EOF — so a first release whose
    CHANGELOG has no prior section is still detected as having notes."""
    m = re.search(
        r"^## \[Unreleased\]\n(.*?)(?=^## \[|^\[[^\]]+\]:|\Z)",
        text,
        re.S | re.M,
    )
    return m.group(1) if m else ""


def has_release_notes(body: str) -> bool:
    """True if the section has real content (not just blanks / ### headers)."""
    for line in body.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("###"):
            return True
    return False


# A squash-merge subject carries the PR number GitHub appends to it, e.g.
# "feat(flywheel): ship an opt-in durability tier (#41)". Commits from before this
# repo went squash-only carry it up front instead: "Merge pull request #28 from …".
SQUASH_PR_RE = re.compile(r"\(#(\d+)\)$")
MERGE_PR_RE = re.compile(r"^Merge pull request #(\d+)\b")
# Any PR reference in the notes counts, so a shared entry like "(#9, #10)" credits both.
NOTES_PR_RE = re.compile(r"#(\d+)\b")


def subject_pr_number(subject: str) -> int | None:
    """The PR number a commit subject advertises, if it advertises one."""
    for pattern in (SQUASH_PR_RE, MERGE_PR_RE):
        m = pattern.search(subject.strip())
        if m:
            return int(m[1])
    return None


def merged_pr_numbers(since: str | None) -> list[int]:
    """PR numbers merged since `since` (a tag), oldest first."""
    if not since:
        return []
    subjects = git("log", f"{since}..HEAD", "--pretty=%s").splitlines()
    return [n for s in subjects if (n := subject_pr_number(s)) is not None]


def unnumbered_subjects(since: str | None) -> list[str]:
    """Subjects since `since` that name no PR, so nothing can be checked for them.

    Most are legitimate: a direct push, or the release commit before its own PR
    lands. But this repo's `squash_merge_commit_title` is `COMMIT_OR_PR_TITLE`,
    and GitHub uses the *commit* subject verbatim when a PR holds a single
    commit — dependabot's usual shape. Such a merge lands with no `(#N)` at all,
    which would make the completeness guard pass it in silence. Surfacing these
    keeps that failure visible instead of silent.
    """
    if not since:
        return []
    subjects = git("log", f"{since}..HEAD", "--pretty=%s").splitlines()
    return [s.strip() for s in subjects if s.strip() and subject_pr_number(s) is None]


def unreferenced_prs(body: str, merged: list[int]) -> list[int]:
    """Merged PR numbers that the [Unreleased] notes never mention."""
    referenced = {int(n) for n in NOTES_PR_RE.findall(body)}
    return sorted(set(merged) - referenced)


def rewrite_changelog(text: str, version: str, date: str) -> str:
    """Move [Unreleased] into a dated [version] section and refresh link refs."""
    if re.search(rf"^## \[{re.escape(version)}\]", text, re.M):
        raise ReleaseError(f"CHANGELOG.md already has a [{version}] section")

    # 1. Insert the dated version heading just below [Unreleased], keeping the
    #    accumulated notes under it and leaving [Unreleased] empty above.
    new_text, n = re.subn(
        r"^## \[Unreleased\]\n",
        f"## [Unreleased]\n\n## [{version}] — {date}\n",
        text,
        count=1,
        flags=re.M,
    )
    if n != 1:
        raise ReleaseError("could not find the '## [Unreleased]' heading")

    # 2. Refresh the Keep-a-Changelog link references at the foot of the file:
    #    point [Unreleased] at the new tag and add the [version] compare link.
    ref_re = re.compile(
        r"^\[Unreleased\]:\s*(?P<base>\S+/compare/)"
        r"v(?P<prev>\d+\.\d+\.\d+)\.\.\.HEAD$",
        re.M,
    )
    m = ref_re.search(new_text)
    if m:
        base, prev = m["base"], m["prev"]
        replacement = (
            f"[Unreleased]: {base}v{version}...HEAD\n"
            f"[{version}]: {base}v{prev}...v{version}"
        )
        new_text = ref_re.sub(replacement, new_text, count=1)
    else:
        print(
            "  ! no '[Unreleased]: …/compare/…HEAD' link reference found — "
            "skipped link-ref refresh (update it by hand if you use them)",
            file=sys.stderr,
        )
    return new_text


# --- git helpers ------------------------------------------------------------


def git(*args: str, check: bool = True) -> str:
    result = subprocess.run(
        ["git", *args], capture_output=True, text=True, cwd=REPO_ROOT
    )
    if check and result.returncode != 0:
        raise ReleaseError(f"`git {' '.join(args)}` failed: {result.stderr.strip()}")
    return result.stdout.strip()


def latest_tag() -> str | None:
    out = git("tag", "--list", "v*", "--sort=-v:refname")
    for tag in out.splitlines():
        if VERSION_RE.match(tag.strip().lstrip("v")):
            return tag.strip()
    return None


def tag_exists(version: str) -> bool:
    return bool(git("tag", "--list", f"v{version}"))


def working_tree_dirty(pathspec: str | None = None) -> bool:
    args = ["status", "--porcelain"]
    if pathspec:
        args.append(pathspec)
    return bool(git(*args))


def current_branch() -> str:
    return git("rev-parse", "--abbrev-ref", "HEAD")


# --- CLI --------------------------------------------------------------------


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Finalize a Career OS release (maintainers only)."
    )
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--version", help="explicit target version, e.g. 1.4.0")
    target.add_argument(
        "--bump",
        choices=["major", "minor", "patch"],
        help="compute the next version from the latest git tag",
    )
    parser.add_argument(
        "--date", default=None, help="release date YYYY-MM-DD (default: today)"
    )
    parser.add_argument(
        "--allow-missing-entries",
        action="store_true",
        help="cut the release even if a PR merged since the last tag has no "
        "[Unreleased] entry (deliberate override, not a default)",
    )
    # --commit and --tag are separate release phases — never both at once.
    phase = parser.add_mutually_exclusive_group()
    phase.add_argument(
        "--commit",
        action="store_true",
        help="phase 1: make the release commit on the current branch",
    )
    phase.add_argument(
        "--tag",
        action="store_true",
        help="phase 2: tag the merged release commit on main (after the PR merges)",
    )
    return parser.parse_args(argv)


def print_prepare_steps(version: str, commit: bool) -> None:
    print("\nNext steps:")
    step = 1
    if not commit:
        print(f"  {step}. Review:  git diff CHANGELOG.md")
        step += 1
        print(
            f"  {step}. Commit:  git add CHANGELOG.md && "
            f'git commit -m "release: v{version} changelog"'
        )
        step += 1
    print(f"  {step}. PR:      push the release branch, open a PR, and merge it")
    step += 1
    print(
        f"  {step}. Tag:     once merged, from an up-to-date main run "
        f"`prepare_release.py --version {version} --tag`"
    )
    print(
        "\nThe --tag step tags the merged commit on main; pushing that tag makes "
        "release.yml publish the Release — do NOT create it in the UI."
    )


def prepare(
    version: str,
    latest: str | None,
    date: str | None,
    commit: bool,
    allow_missing_entries: bool = False,
) -> int:
    """Phase 1: rewrite CHANGELOG.md (and optionally commit) on a release branch."""
    assert_increasing(version, latest)
    if tag_exists(version):
        raise ReleaseError(f"tag v{version} already exists")
    text = CHANGELOG.read_text(encoding="utf-8")
    if not has_release_notes(unreleased_body(text)):
        raise ReleaseError("the [Unreleased] section is empty — nothing to release")
    missing = unreferenced_prs(unreleased_body(text), merged_pr_numbers(latest))
    if missing and not allow_missing_entries:
        listed = ", ".join(f"#{n}" for n in missing)
        raise ReleaseError(
            f"merged since {latest} but absent from [Unreleased]: {listed}\n"
            "  The release notes are generated from that section, so whatever is\n"
            "  missing from it ships invisible. Add an entry for each (dependabot\n"
            "  PRs included — they never write their own), or re-run with\n"
            "  --allow-missing-entries to cut the release without them."
        )
    unnumbered = unnumbered_subjects(latest)
    if unnumbered:
        for subject in unnumbered:
            print(f"  ! no PR number in: {subject}", file=sys.stderr)
        print(
            "  ! nothing above could be checked against [Unreleased]. A direct push\n"
            "    is fine; a squash-merge that lost its '(#N)' is not — confirm those\n"
            "    are covered before publishing.",
            file=sys.stderr,
        )
    if working_tree_dirty("CHANGELOG.md"):
        raise ReleaseError(
            "CHANGELOG.md has uncommitted changes — commit or stash first"
        )
    if commit and working_tree_dirty():
        raise ReleaseError(
            "working tree is not clean — the release commit must contain "
            "only the CHANGELOG change"
        )

    resolved_date = date or dt.date.today().isoformat()
    CHANGELOG.write_text(
        rewrite_changelog(text, version, resolved_date), encoding="utf-8"
    )
    print(f"✓ CHANGELOG.md: [Unreleased] → [{version}] — {resolved_date}")

    if commit:
        git("add", "CHANGELOG.md")
        git("commit", "-m", f"release: v{version} changelog")
        print(f"✓ committed: release: v{version} changelog")

    print_prepare_steps(version, commit)
    return 0


def tag_release(version: str, latest: str | None) -> int:
    """Phase 2: tag the merged release commit on main (run after the PR merges)."""
    assert_increasing(version, latest)
    if tag_exists(version):
        raise ReleaseError(f"tag v{version} already exists")
    branch = current_branch()
    if branch != "main":
        raise ReleaseError(
            f"on branch '{branch}', not 'main' — the tag must sit on main, which "
            "release.yml requires (it rejects tags that aren't ancestors of main)"
        )
    if working_tree_dirty():
        raise ReleaseError("working tree is not clean — sync main before tagging")
    text = CHANGELOG.read_text(encoding="utf-8")
    if not re.search(rf"^## \[{re.escape(version)}\]", text, re.M):
        raise ReleaseError(
            f"CHANGELOG.md has no [{version}] section yet — run --commit on a "
            "release branch and merge that PR before tagging"
        )

    git("tag", "-a", f"v{version}", "-m", f"v{version}")
    print(f"✓ tagged: v{version} on main (local only — not pushed)")
    print(f"\nNext step:\n  Push:  git push origin v{version}")
    print(
        "\nrelease.yml publishes the GitHub Release from the CHANGELOG when the "
        "tag lands — do NOT create the release in the UI."
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        latest = latest_tag()
        version = resolve_version(latest, args.version, args.bump)
        if args.tag:
            return tag_release(version, latest)
        return prepare(
            version, latest, args.date, args.commit, args.allow_missing_entries
        )
    except ReleaseError as err:
        print(f"error: {err}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
