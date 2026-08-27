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


# --- CV-coverage side: bare-word languages use the same guarded matcher -------
# count_in_text() checks whether the CV covers a JD term; for "Go"/"Rust" it must
# apply the capitalized, context-guarded pattern (not a lowercased \bword\b), or a
# CV that merely says "Rust Belt" / "go to market" would be scored as covering the
# language and the real gap would be dropped from the report.


def test_count_in_text_rust_ignores_rust_belt_in_cv():
    assert jd_gap.count_in_text("rust", "Engineers based in the Rust Belt") == 0
    assert jd_gap.count_in_text("rust", "We trust the process; nothing rusty") == 0
    # genuine coverage still counts
    assert jd_gap.count_in_text("rust", "Shipped a Rust service") == 1


def test_count_in_text_go_ignores_english_prose_in_cv():
    assert jd_gap.count_in_text("go", "We go to market fast and go deep") == 0
    # genuine coverage (capitalized Go and the golang variant) still counts
    assert jd_gap.count_in_text("go", "Built backend services in Go using golang") == 2


# --- common bare-word language / tool names ---------------------------------
# python / java / ruby / docker are lowercase words the CamelCase regex misses.
# Unlike go/rust they need no capitalization guard — they don't occur as ordinary
# English in a software JD/CV, so case-insensitive whole-word matching is safe.


def test_extract_detects_common_language_names():
    counts = jd_gap.extract_tech_tokens(
        "Backend in Python and Java; tooling scripts in Ruby"
    )
    assert counts["python"] == 1
    assert counts["java"] == 1
    assert counts["ruby"] == 1


def test_extract_java_does_not_match_javascript():
    # word boundary: "java" must not be found inside "JavaScript"
    counts = jd_gap.extract_tech_tokens("Frontend in JavaScript")
    assert counts.get("java", 0) == 0


def test_extract_docker_counted_separately_from_compose():
    # "docker compose" is matched (and blanked) first, then bare "docker" once
    counts = jd_gap.extract_tech_tokens("We run Docker locally via docker compose")
    assert counts["docker compose"] == 1
    assert counts["docker"] == 1


def test_count_in_text_matches_bare_language_names():
    assert jd_gap.count_in_text("python", "Primarily a Python shop") == 1
    assert jd_gap.count_in_text("docker", "Everything ships in Docker") == 1
    # absence is a real gap (zero), not a false hit
    assert jd_gap.count_in_text("ruby", "We use Go and Python") == 0


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


# --- a JD with nothing to measure -------------------------------------------


def test_an_empty_jd_does_not_claim_full_coverage(tmp_path, capsys):
    """It used to print `0%` and `full coverage!` on the same screen.

    Both cannot be true, and neither was: an empty JD yields no terms, so there
    was nothing to cover. A reader had to pick which half to believe, which is
    the same defect class as a warning contradicting the rate beneath it.
    """
    jd = tmp_path / "empty.txt"
    jd.write_text("", encoding="utf-8")
    cv = tmp_path / "cv.md"
    cv.write_text("# CV\n\nSome prose.\n", encoding="utf-8")

    coverage = jd_gap.run(str(jd), str(cv))
    out = capsys.readouterr().out

    # Not 0. Zero is a real measurement meaning the CV echoed nothing; None
    # means there was nothing to measure, and the callers already write
    # `null` and print no figure for it.
    assert coverage is None
    assert "full coverage" not in out
    assert "nothing to measure" in out
    assert "n/a" in out


def test_a_jd_with_no_recognised_keywords_is_reported_as_unmeasurable(tmp_path, capsys):
    jd = tmp_path / "prose.txt"
    jd.write_text("We are looking for a wonderful person who likes people.\n", "utf-8")
    cv = tmp_path / "cv.md"
    cv.write_text("# CV\n", encoding="utf-8")

    jd_gap.run(str(jd), str(cv))
    out = capsys.readouterr().out
    assert "full coverage" not in out


def test_a_real_gap_still_reports_the_missing_term(tmp_path, capsys):
    """The unmeasurable path must not swallow the ordinary one."""
    jd = tmp_path / "jd.txt"
    jd.write_text("We need Kubernetes and Terraform.\n", encoding="utf-8")
    cv = tmp_path / "cv.md"
    cv.write_text("# CV\n\nI know Terraform.\n", encoding="utf-8")

    jd_gap.run(str(jd), str(cv))
    out = capsys.readouterr().out
    assert "MISSING" in out
    assert "kubernetes" in out
    assert "nothing to measure" not in out


def test_a_real_zero_coverage_is_still_reported_as_zero(tmp_path, capsys):
    """`None` must not swallow a genuine measurement of nothing matching."""
    jd = tmp_path / "jd.txt"
    jd.write_text("We need Kubernetes and Terraform.\n", encoding="utf-8")
    cv = tmp_path / "cv.md"
    cv.write_text("# CV\n\nI have opinions about wine.\n", encoding="utf-8")

    assert jd_gap.run(str(jd), str(cv)) == 0


def test_the_generated_application_agrees_with_its_own_gap_report(tmp_path):
    """The contradiction that returning 0 for an unmeasurable JD produced.

    `new_application.py` writes `tech_keyword_coverage` into the frontmatter
    and embeds the gap report in the same file. Returning 0 while the report
    said `n/a` put both answers in one document, which is the defect the
    report's own wording was fixed to avoid.
    """
    import new_application

    jd = tmp_path / "empty.txt"
    jd.write_text("", encoding="utf-8")
    cv = tmp_path / "cv.md"
    cv.write_text("# CV\n", encoding="utf-8")

    coverage = jd_gap.run(str(jd), str(cv))
    rendered = f"tech_keyword_coverage: {new_application.yaml_scalar(coverage)}"
    assert rendered == "tech_keyword_coverage: null"
