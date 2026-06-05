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


def _stub_git(monkeypatch, *, latest="v1.3.0", existing_tags=(), dirty=False):
    monkeypatch.setattr(pr, "latest_tag", lambda: latest)
    monkeypatch.setattr(pr, "tag_exists", lambda v: f"v{v}" in existing_tags)
    monkeypatch.setattr(pr, "working_tree_dirty", lambda pathspec=None: dirty)
    monkeypatch.setattr(pr, "current_branch", lambda: "main")


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


def test_main_blocks_tag_without_commit(tmp_path, monkeypatch, capsys):
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text(SAMPLE, encoding="utf-8")
    monkeypatch.setattr(pr, "CHANGELOG", changelog)
    _stub_git(monkeypatch)

    rc = pr.main(["--version", "1.4.0", "--tag"])

    assert rc == 1
    assert "--tag requires --commit" in capsys.readouterr().err
