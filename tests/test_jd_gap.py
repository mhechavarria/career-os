"""Unit tests for scripts/jd_gap.py — keyword extraction, synonyms, and scoring."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import jd_gap  # noqa: E402


# --- strip_markdown ---------------------------------------------------------


def test_strip_markdown_removes_frontmatter_and_links():
    raw = (
        "---\n"
        "type: cv\n"
        "---\n"
        "# Title\n"
        "Use [[wiki link]] and [a link](http://example.com).\n"
    )
    out = jd_gap.strip_markdown(raw)
    assert "type: cv" not in out  # frontmatter stripped
    assert "[[" not in out  # wiki link syntax stripped
    assert "wiki link" in out  # display text kept
    assert "a link" in out  # markdown link text kept
    assert "http" not in out  # url dropped


# --- extract_tech_tokens ----------------------------------------------------


def test_extract_detects_multiword_phrase():
    counts = jd_gap.extract_tech_tokens("Built an event-driven architecture at scale")
    assert counts["event-driven architecture"] == 1


def test_extract_detects_single_camelcase_token():
    counts = jd_gap.extract_tech_tokens("We use TypeScript heavily")
    assert counts["typescript"] == 1


# --- synonyms ---------------------------------------------------------------


def test_synonym_folding_on_jd_side():
    # "k8s" should be counted under its canonical term "kubernetes"
    counts = jd_gap.extract_tech_tokens("Deploy with k8s, scale with k8s")
    assert counts["kubernetes"] == 2
    assert "k8s" not in counts


def test_count_in_text_matches_variant_spelling():
    # Looking for canonical "kubernetes" should find the variant "k8s" in text
    assert jd_gap.count_in_text("kubernetes", "we deploy on k8s") == 1
    # And "postgres" should satisfy "postgresql"
    assert jd_gap.count_in_text("postgresql", "backed by postgres") == 1


def test_tech_phrases_have_no_duplicates():
    assert len(jd_gap.TECH_PHRASES) == len(set(jd_gap.TECH_PHRASES))


# --- score ------------------------------------------------------------------


def test_score_full_coverage_is_100():
    assert jd_gap.score([], [], [("a", 3, 3)]) == 100


def test_score_no_coverage_is_0():
    assert jd_gap.score([("a", 3)], [], []) == 0


def test_score_partial_and_weak_are_in_range():
    assert jd_gap.score([("a", 2)], [], [("b", 2, 2)]) == 50  # half present
    assert jd_gap.score([], [("a", 2, 1)], []) == 50  # weak = half weight


def test_score_empty_is_0():
    assert jd_gap.score([], [], []) == 0


# --- "go" / short lowercase language detection ------------------------------


def test_extract_detects_go_and_golang_fold():
    # capitalized "Go" + "golang" both fold to the canonical "go"
    counts = jd_gap.extract_tech_tokens("We build in Go; some services use golang too")
    assert counts["go"] == 2
    assert "golang" not in counts


def test_extract_go_ignores_substrings():
    # word-boundary + capitalized-only: going / good / google must not count
    counts = jd_gap.extract_tech_tokens("Going to do good work on Google Cloud daily")
    assert counts.get("go", 0) == 0


def test_extract_go_ignores_english_phrases():
    # ordinary English "go" phrases must not be miscounted as the language
    counts = jd_gap.extract_tech_tokens(
        "Candidates should go to market fast, go deep, and be a Go-getter"
    )
    assert counts.get("go", 0) == 0


def test_extract_detects_go_in_tech_list():
    counts = jd_gap.extract_tech_tokens("Backend services in Python, Go, and Rust")
    assert counts["go"] == 1


def test_count_in_text_go_matches_golang_variant():
    assert jd_gap.count_in_text("go", "primarily written in golang") == 1
    assert jd_gap.count_in_text("go", "we ship Go services") == 1


# --- "rust" capitalized-token detection -------------------------------------


def test_extract_detects_rust_capitalized_token():
    # capitalized "Rust" is the language, counted like "Go"
    counts = jd_gap.extract_tech_tokens("Backend in Go and Rust")
    assert counts["rust"] == 1


def test_extract_rust_ignores_english_and_rust_belt():
    # lowercase prose (trust, rusty) and "Rust Belt" must not count as the language
    counts = jd_gap.extract_tech_tokens(
        "We trust the process, no rusty code, hiring across the Rust Belt"
    )
    assert counts.get("rust", 0) == 0


# --- CLI: graceful missing-file handling ------------------------------------


def test_main_exits_cleanly_on_missing_file(monkeypatch, tmp_path, capsys):
    cv = tmp_path / "cv.md"
    cv.write_text("# CV\nGo and Python.\n", encoding="utf-8")
    missing_jd = tmp_path / "nope.txt"
    monkeypatch.setattr(sys, "argv", ["jd_gap.py", str(missing_jd), str(cv)])
    with pytest.raises(SystemExit) as exc:
        jd_gap.main()
    assert exc.value.code == 1
    assert "not found" in capsys.readouterr().err
