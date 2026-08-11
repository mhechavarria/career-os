"""Unit tests for maintainers/prepare_release.py — version math + CHANGELOG surgery."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "maintainers"))

import prepare_release as pr  # noqa: E402


# A miniature CHANGELOG that mirrors the real file's shape: an [Unreleased]
# section with notes, a prior release, and Keep-a-Changelog link references.
SAMPLE = """\
# Changelog

## [Unreleased]

### Changed
- A real change worth releasing.

## [1.3.0] — 2026-06-04

### Changed
- Something shipped earlier.

[Unreleased]: https://github.com/acme/career-os/compare/v1.3.0...HEAD
[1.3.0]: https://github.com/acme/career-os/compare/v1.2.0...v1.3.0
"""

# SAMPLE after a v1.4.0 cut has been prepared and merged to main — the shape the
# phase-2 `--tag` step sees (CHANGELOG already carries the [1.4.0] section).
CUT = SAMPLE.replace(
    "## [Unreleased]\n",
    "## [Unreleased]\n\n## [1.4.0] — 2026-06-05\n",
    1,
)


# --- version helpers --------------------------------------------------------


def test_parse_version_accepts_plain_and_v_prefixed():
    assert pr.parse_version("1.4.0") == (1, 4, 0)
    assert pr.parse_version("v2.0.1") == (2, 0, 1)


def test_parse_version_rejects_garbage():
    for bad in ["1.4", "1.4.x", "v1", "", "1.2.3.4"]:
        with pytest.raises(pr.ReleaseError):
            pr.parse_version(bad)


def test_bump_version_each_part():
    assert pr.bump_version((1, 3, 2), "major") == (2, 0, 0)
    assert pr.bump_version((1, 3, 2), "minor") == (1, 4, 0)
    assert pr.bump_version((1, 3, 2), "patch") == (1, 3, 3)


def test_resolve_version_prefers_explicit():
    assert pr.resolve_version("v1.3.0", "1.9.0", None) == "1.9.0"


def test_resolve_version_bumps_from_latest_tag():
    assert pr.resolve_version("v1.3.0", None, "minor") == "1.4.0"


def test_resolve_version_bump_without_tag_errors():
    with pytest.raises(pr.ReleaseError):
        pr.resolve_version(None, None, "patch")


def test_assert_increasing_blocks_downgrade_and_equal():
    with pytest.raises(pr.ReleaseError):
        pr.assert_increasing("1.3.0", "v1.3.0")  # equal
    with pytest.raises(pr.ReleaseError):
        pr.assert_increasing("1.2.5", "v1.3.0")  # older
    pr.assert_increasing("1.4.0", "v1.3.0")  # newer is fine
    pr.assert_increasing("1.0.0", None)  # no prior tag is fine


# --- [Unreleased] content detection -----------------------------------------


def test_has_release_notes_true_for_real_content():
    assert pr.has_release_notes(pr.unreleased_body(SAMPLE)) is True


def test_has_release_notes_false_for_empty_and_header_only():
    assert pr.has_release_notes("\n\n") is False
    # only an empty category header, no bullets → nothing to release
    assert pr.has_release_notes("\n### Changed\n\n") is False


def test_unreleased_body_without_a_following_section():
    # first-ever release: [Unreleased] has notes but no prior '## [' section.
    # The body must still be detected (stop at EOF), not reported as empty.
    first = "# Changelog\n\n## [Unreleased]\n\n### Added\n- Initial release.\n"
    assert pr.has_release_notes(pr.unreleased_body(first)) is True


def test_unreleased_body_stops_before_link_references():
    # link-ref definitions below an empty [Unreleased] are not release notes
    only_refs = (
        "# Changelog\n\n## [Unreleased]\n\n"
        "[Unreleased]: https://example.com/compare/v1.0.0...HEAD\n"
    )
    assert pr.has_release_notes(pr.unreleased_body(only_refs)) is False


# --- changelog completeness (every merged PR must be mentioned) --------------


def test_merged_pr_numbers_reads_squash_subjects(monkeypatch):
    log = "\n".join(
        [
            "feat(flywheel): ship an opt-in durability tier (#41)",
            "chore(ci): pin the dev toolchain (#39)",
            "a direct push with no PR number",
            "Revert 'something (#12)' (#40)",  # only the trailing number counts
        ]
    )
    monkeypatch.setattr(pr, "git", lambda *a, **k: log)
    assert pr.merged_pr_numbers("v1.6.0") == [41, 39, 40]


def test_merged_pr_numbers_reads_pre_squash_merge_commits(monkeypatch):
    # history from before the repo went squash-only leads with the number instead
    log = "Merge pull request #28 from mhechavarria/sync/panda-os-abc123"
    monkeypatch.setattr(pr, "git", lambda *a, **k: log)
    assert pr.merged_pr_numbers("v1.2.0") == [28]


def test_unnumbered_subjects_surfaces_what_cannot_be_checked(monkeypatch):
    # `squash_merge_commit_title: COMMIT_OR_PR_TITLE` means a single-commit PR —
    # dependabot's usual shape — can land with no "(#N)" at all
    log = "\n".join(
        [
            "chore(deps): bump actions/setup-python from 5 to 6",
            "feat(flywheel): ship an opt-in durability tier (#41)",
            "Merge pull request #28 from mhechavarria/sync",
        ]
    )
    monkeypatch.setattr(pr, "git", lambda *a, **k: log)
    assert pr.unnumbered_subjects("v1.6.0") == [
        "chore(deps): bump actions/setup-python from 5 to 6"
    ]


def test_unnumbered_subjects_skips_git_without_a_prior_tag(monkeypatch):
    def boom(*a, **k):
        raise AssertionError("git must not run when there is no tag to diff from")

    monkeypatch.setattr(pr, "git", boom)
    assert pr.unnumbered_subjects(None) == []


def test_main_warns_about_commits_it_cannot_check(tmp_path, monkeypatch, capsys):
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text(SAMPLE, encoding="utf-8")
    monkeypatch.setattr(pr, "CHANGELOG", changelog)
    _stub_git(
        monkeypatch, unnumbered=("chore(deps): bump actions/checkout from 4 to 6",)
    )

    rc = pr.main(["--bump", "minor", "--date", "2026-06-05"])

    # a warning, not a block: a direct push is legitimate
    assert rc == 0
    err = capsys.readouterr().err
    assert "no PR number in: chore(deps): bump actions/checkout from 4 to 6" in err
    assert "lost its '(#N)'" in err


def test_merged_pr_numbers_skips_git_without_a_prior_tag(monkeypatch):
    def boom(*a, **k):
        raise AssertionError("git must not run when there is no tag to diff from")

    monkeypatch.setattr(pr, "git", boom)
    assert pr.merged_pr_numbers(None) == []


def test_unreferenced_prs_reports_only_the_gap():
    body = "\n### Changed\n- Pinned the toolchain. (#39)\n"
    assert pr.unreferenced_prs(body, [39, 41]) == [41]


def test_unreferenced_prs_credits_every_number_in_a_shared_entry():
    # one bullet can close several PRs: "(#9, #10)" must credit both
    body = "\n### Added\n- README revamp and the acknowledgements. (#9, #10)\n"
    assert pr.unreferenced_prs(body, [9, 10]) == []


def test_main_blocks_when_a_merged_pr_has_no_entry(tmp_path, monkeypatch, capsys):
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text(SAMPLE, encoding="utf-8")
    monkeypatch.setattr(pr, "CHANGELOG", changelog)
    _stub_git(monkeypatch, merged=(39, 41))

    rc = pr.main(["--bump", "minor", "--date", "2026-06-05"])

    assert rc == 1
    err = capsys.readouterr().err
    assert "#39, #41" in err
    assert "--allow-missing-entries" in err
    # a failed guard must leave the file untouched
    assert changelog.read_text(encoding="utf-8") == SAMPLE


def test_main_allow_missing_entries_overrides_the_guard(tmp_path, monkeypatch):
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text(SAMPLE, encoding="utf-8")
    monkeypatch.setattr(pr, "CHANGELOG", changelog)
    _stub_git(monkeypatch, merged=(39,))

    rc = pr.main(["--bump", "minor", "--date", "2026-06-05", "--allow-missing-entries"])

    assert rc == 0
    assert "## [1.4.0] — 2026-06-05" in changelog.read_text(encoding="utf-8")


def test_main_passes_when_every_merged_pr_is_credited(tmp_path, monkeypatch):
    credited = SAMPLE.replace(
        "- A real change worth releasing.",
        "- A real change worth releasing. (#39)",
    )
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text(credited, encoding="utf-8")
    monkeypatch.setattr(pr, "CHANGELOG", changelog)
    _stub_git(monkeypatch, merged=(39,))

    assert pr.main(["--bump", "minor", "--date", "2026-06-05"]) == 0


def test_tag_phase_ignores_the_completeness_guard(tmp_path, monkeypatch):
    # phase 2 runs after the notes already moved into their dated section, so
    # [Unreleased] is empty by design and the guard must not fire there
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text(CUT, encoding="utf-8")
    monkeypatch.setattr(pr, "CHANGELOG", changelog)
    _stub_git(monkeypatch, merged=(39, 41))
    monkeypatch.setattr(pr, "git", lambda *a, **k: "")

    assert pr.main(["--version", "1.4.0", "--tag"]) == 0


# --- CHANGELOG surgery ------------------------------------------------------


def test_rewrite_inserts_dated_version_and_empties_unreleased():
    out = pr.rewrite_changelog(SAMPLE, "1.4.0", "2026-06-05")
    # the dated heading now exists, directly under an emptied [Unreleased]
    assert "## [1.4.0] — 2026-06-05" in out
    assert "## [Unreleased]\n\n## [1.4.0] — 2026-06-05\n" in out
    # the notes moved under the new version, not left under [Unreleased]
    assert pr.has_release_notes(pr.unreleased_body(out)) is False
    assert "A real change worth releasing." in out


def test_rewrite_refreshes_link_references():
    out = pr.rewrite_changelog(SAMPLE, "1.4.0", "2026-06-05")
    base = "https://github.com/acme/career-os/compare"
    assert f"[Unreleased]: {base}/v1.4.0...HEAD" in out
    assert f"[1.4.0]: {base}/v1.3.0...v1.4.0" in out
    # the old [Unreleased] compare base must be gone
    assert f"[Unreleased]: {base}/v1.3.0...HEAD" not in out
    # the prior release's link reference is untouched
    assert f"[1.3.0]: {base}/v1.2.0...v1.3.0" in out


def test_rewrite_rejects_existing_version_section():
    with pytest.raises(pr.ReleaseError):
        pr.rewrite_changelog(SAMPLE, "1.3.0", "2026-06-05")


def test_rewrite_warns_when_no_link_refs(capsys):
    minimal = "# Changelog\n\n## [Unreleased]\n\n### Changed\n- A change.\n"
    out = pr.rewrite_changelog(minimal, "1.4.0", "2026-06-05")
    assert "## [1.4.0] — 2026-06-05" in out
    assert "no '[Unreleased]" in capsys.readouterr().err


# --- end-to-end main(), with git stubbed ------------------------------------


def _stub_git(
    monkeypatch,
    *,
    latest="v1.3.0",
    existing_tags=(),
    dirty=False,
    merged=(),
    unnumbered=(),
):
    monkeypatch.setattr(pr, "latest_tag", lambda: latest)
    monkeypatch.setattr(pr, "tag_exists", lambda v: f"v{v}" in existing_tags)
    monkeypatch.setattr(pr, "working_tree_dirty", lambda pathspec=None: dirty)
    monkeypatch.setattr(pr, "current_branch", lambda: "main")
    # Default to "no PRs merged since the tag" so the completeness guard is inert
    # unless a test opts into it; otherwise every CLI test would depend on the
    # real git history of whatever checkout the suite runs in.
    monkeypatch.setattr(pr, "merged_pr_numbers", lambda since: list(merged))
    monkeypatch.setattr(pr, "unnumbered_subjects", lambda since: list(unnumbered))


def test_main_rewrites_changelog_file(tmp_path, monkeypatch, capsys):
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text(SAMPLE, encoding="utf-8")
    monkeypatch.setattr(pr, "CHANGELOG", changelog)
    _stub_git(monkeypatch)

    rc = pr.main(["--bump", "minor", "--date", "2026-06-05"])

    assert rc == 0
    assert "## [1.4.0] — 2026-06-05" in changelog.read_text(encoding="utf-8")
    assert "[Unreleased] → [1.4.0]" in capsys.readouterr().out


def test_main_cuts_first_release_with_no_prior_section(tmp_path, monkeypatch, capsys):
    # CLI path for a first release: no prior tag, CHANGELOG has only [Unreleased].
    first = "# Changelog\n\n## [Unreleased]\n\n### Added\n- Initial release.\n"
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text(first, encoding="utf-8")
    monkeypatch.setattr(pr, "CHANGELOG", changelog)
    _stub_git(monkeypatch, latest=None)

    rc = pr.main(["--version", "1.0.0", "--date", "2026-06-05"])

    assert rc == 0  # must not falsely report "nothing to release"
    assert "## [1.0.0] — 2026-06-05" in changelog.read_text(encoding="utf-8")


def test_main_blocks_when_tag_exists(tmp_path, monkeypatch, capsys):
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text(SAMPLE, encoding="utf-8")
    monkeypatch.setattr(pr, "CHANGELOG", changelog)
    _stub_git(monkeypatch, existing_tags=("v1.4.0",))

    rc = pr.main(["--version", "1.4.0"])

    assert rc == 1
    assert "already exists" in capsys.readouterr().err
    # the file must be left untouched when a guard fails
    assert changelog.read_text(encoding="utf-8") == SAMPLE


def test_main_blocks_empty_unreleased(tmp_path, monkeypatch, capsys):
    empty = "# Changelog\n\n## [Unreleased]\n\n## [1.3.0] — 2026-06-04\n- old\n"
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text(empty, encoding="utf-8")
    monkeypatch.setattr(pr, "CHANGELOG", changelog)
    _stub_git(monkeypatch)

    rc = pr.main(["--bump", "minor"])

    assert rc == 1
    assert "nothing to release" in capsys.readouterr().err


def test_main_commit_phase_makes_release_commit(tmp_path, monkeypatch, capsys):
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text(SAMPLE, encoding="utf-8")
    monkeypatch.setattr(pr, "CHANGELOG", changelog)
    _stub_git(monkeypatch)
    calls = []
    monkeypatch.setattr(pr, "git", lambda *a, **k: calls.append(a) or "")

    rc = pr.main(["--bump", "minor", "--date", "2026-06-05", "--commit"])

    assert rc == 0
    assert "## [1.4.0] — 2026-06-05" in changelog.read_text(encoding="utf-8")
    assert ("add", "CHANGELOG.md") in calls
    assert ("commit", "-m", "release: v1.4.0 changelog") in calls


def test_main_commit_and_tag_are_mutually_exclusive():
    # argparse rejects the combination before any work happens
    with pytest.raises(SystemExit):
        pr.main(["--version", "1.4.0", "--commit", "--tag"])


# --- phase 2: tagging the merged release commit on main ---------------------


def test_main_tag_phase_tags_merged_release(tmp_path, monkeypatch, capsys):
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text(CUT, encoding="utf-8")
    monkeypatch.setattr(pr, "CHANGELOG", changelog)
    _stub_git(monkeypatch)  # on main, clean, latest v1.3.0, tag absent
    calls = []
    monkeypatch.setattr(pr, "git", lambda *a, **k: calls.append(a) or "")

    rc = pr.main(["--version", "1.4.0", "--tag"])

    assert rc == 0
    assert ("tag", "-a", "v1.4.0", "-m", "v1.4.0") in calls
    assert changelog.read_text(encoding="utf-8") == CUT  # CHANGELOG untouched
    assert "git push origin v1.4.0" in capsys.readouterr().out


def test_main_tag_phase_requires_cut_changelog(tmp_path, monkeypatch, capsys):
    # SAMPLE still has the notes under [Unreleased] — the cut isn't merged yet
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text(SAMPLE, encoding="utf-8")
    monkeypatch.setattr(pr, "CHANGELOG", changelog)
    _stub_git(monkeypatch)

    rc = pr.main(["--version", "1.4.0", "--tag"])

    assert rc == 1
    assert "no [1.4.0] section yet" in capsys.readouterr().err


def test_main_tag_phase_must_run_on_main(tmp_path, monkeypatch, capsys):
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text(CUT, encoding="utf-8")
    monkeypatch.setattr(pr, "CHANGELOG", changelog)
    _stub_git(monkeypatch)
    monkeypatch.setattr(pr, "current_branch", lambda: "release/v1.4.0")

    rc = pr.main(["--version", "1.4.0", "--tag"])

    assert rc == 1
    assert "not 'main'" in capsys.readouterr().err
