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


def prepare(version: str, latest: str | None, date: str | None, commit: bool) -> int:
    """Phase 1: rewrite CHANGELOG.md (and optionally commit) on a release branch."""
    assert_increasing(version, latest)
    if tag_exists(version):
        raise ReleaseError(f"tag v{version} already exists")
    text = CHANGELOG.read_text(encoding="utf-8")
    if not has_release_notes(unreleased_body(text)):
        raise ReleaseError("the [Unreleased] section is empty — nothing to release")
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
        return prepare(version, latest, args.date, args.commit)
    except ReleaseError as err:
        print(f"error: {err}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
