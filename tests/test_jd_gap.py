"""Unit tests for scripts/jd_gap.py — keyword extraction, synonyms, and scoring."""

import sys
from pathlib import Path

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
