"""Unit tests for scripts/new_application.py — slug + JD-handling behavior."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import new_application  # noqa: E402


# --- slugify ----------------------------------------------------------------


def test_slugify_basic():
    assert new_application.slugify("Staff Backend Engineer") == "staff-backend-engineer"


def test_slugify_transliterates_accents():
    # NFKD transliteration, not accent-stripping-to-hyphens (finding C3):
    # "José" must become "jose", never "jos-". Covers combining diacritics
    # (acute, circumflex, tilde, cedilla, umlaut).
    assert new_application.slugify("José Antônio Nóbrega") == "jose-antonio-nobrega"
    assert new_application.slugify("François Núñez") == "francois-nunez"
    assert new_application.slugify("Müller") == "muller"


def test_slugify_trims_and_collapses_separators():
    assert new_application.slugify("  Acme   Corp!!  ") == "acme-corp"


# --- JD handling (findings C1 / C2) -----------------------------------------


def _write_min_repo(tmp_path: Path) -> Path:
    (tmp_path / "jds").mkdir()
    (tmp_path / "cv" / "versions").mkdir(parents=True)
    (tmp_path / "applications").mkdir()
    cv = tmp_path / "cv" / "versions" / "cardume.md"
    cv.write_text(
        "# Jane Roe\njane@example.com | +1 555 000 0000\nGo and PostgreSQL.\n",
        encoding="utf-8",
    )
    return cv


def test_reuses_jd_already_in_jds_dir(monkeypatch, tmp_path):
    # A JD already saved under jds/ with a name that differs from the
    # <company>-<role> slug must be reused in place, not duplicated (C1).
    _write_min_repo(tmp_path)
    jd = tmp_path / "jds" / "cardume-staff-backend.txt"
    jd.write_text("We need Go, Kubernetes, and PostgreSQL.\n", encoding="utf-8")

    monkeypatch.setattr(new_application, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "new_application.py",
            "--company",
            "Cardume",
            "--role",
            "Staff Backend Engineer",
            "--jd",
            str(jd),
            "--cv",
            "cv/versions/cardume.md",
            "--no-pdf",
        ],
    )
    new_application.main()

    # No duplicate JD created under a <company>-<role> name.
    jd_files = sorted(p.name for p in (tmp_path / "jds").glob("*.txt"))
    assert jd_files == ["cardume-staff-backend.txt"]

    # The application points at the existing JD, not a copy.
    app = next((tmp_path / "applications").glob("*.md"))
    assert "jd_file: jds/cardume-staff-backend.txt" in app.read_text(encoding="utf-8")


def test_copies_jd_from_outside_jds_dir(monkeypatch, tmp_path):
    # A JD passed from outside jds/ is still archived to jds/<slug>.txt.
    _write_min_repo(tmp_path)
    external = tmp_path / "external.txt"
    external.write_text("Go, Kubernetes, PostgreSQL.\n", encoding="utf-8")

    monkeypatch.setattr(new_application, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "new_application.py",
            "--company",
            "Cardume",
            "--role",
            "Staff Backend Engineer",
            "--jd",
            str(external),
            "--cv",
            "cv/versions/cardume.md",
            "--no-pdf",
        ],
    )
    new_application.main()

    jd_files = sorted(p.name for p in (tmp_path / "jds").glob("*.txt"))
    assert jd_files == ["cardume-staff-backend-engineer.txt"]
    app = next((tmp_path / "applications").glob("*.md"))
    assert "jd_file: jds/cardume-staff-backend-engineer.txt" in app.read_text(
        encoding="utf-8"
    )


# --- yaml_scalar: the frontmatter this script writes must survive being read -


import yaml  # noqa: E402

import pipeline_report  # noqa: E402


HOSTILE_VALUES = [
    "Acme: Europe",  # a colon ended the mapping and voided the whole document
    "Engineer #2",  # `#2` was eaten as a comment, silently
    "No",  # would come back as the boolean False
    "null",  # would come back as None
    "true",
    "2026",  # would come back as an int
    "2026-08-27",  # would come back as a date
    "R&D",
    "Straße GmbH",
    "- leading dash",
    "@handle",
    "*star",
    'say "hi"',
    "it's",
    "trailing space ",
    "line\nbreak",
]


@pytest.mark.parametrize("value", HOSTILE_VALUES)
def test_yaml_scalar_round_trips_as_a_string(value):
    """Every one of these used to corrupt or void the generated file.

    The two that mattered in practice: a colon made
    `parse_frontmatter` return `{}`, so the application disappeared from every
    report with no error, and a `#` truncated the value while leaving a record
    that still looked fine.
    """
    document = f"key: {new_application.yaml_scalar(value)}"
    loaded = yaml.safe_load(document)["key"]
    assert isinstance(loaded, str)
    assert loaded == " ".join(value.split())


def test_yaml_scalar_emits_a_real_null_for_none():
    """The `jd_file`/`cv_pdf` sentinel has to stay YAML null, not the text."""
    assert new_application.yaml_scalar(None) == "null"
    assert yaml.safe_load(f"key: {new_application.yaml_scalar(None)}")["key"] is None


def test_yaml_scalar_leaves_ordinary_values_unquoted():
    """Quoting everything would churn every generated file for no reason."""
    assert new_application.yaml_scalar("Cleanco") == "Cleanco"
    assert new_application.yaml_scalar("Senior Backend Engineer") == (
        "Senior Backend Engineer"
    )


def test_a_generated_file_is_readable_by_the_report(tmp_path, monkeypatch):
    """The contract that actually matters, exercised end to end.

    `new_application.py` writes the file and `pipeline_report.py` reads it;
    nothing tested that the two agreed on the format.
    """
    body = "\n".join(
        f"{key}: {new_application.yaml_scalar(value)}"
        for key, value in (
            ("company", "Acme: Europe"),
            ("role", "Engineer #2"),
            ("cv_version", "cv/versions/backend.md"),
        )
    )
    path = tmp_path / "app.md"
    path.write_text(
        f"---\ntype: application\n{body}\nstage: applied\nfurthest_stage: applied\n---\n",
        encoding="utf-8",
    )

    frontmatter = pipeline_report.parse_frontmatter(path)
    assert frontmatter.get("type") == "application"
    assert frontmatter["company"] == "Acme: Europe"
    assert frontmatter["role"] == "Engineer #2"
    assert pipeline_report.furthest_stage(frontmatter) == "applied"


# --- the generate_cv contract ------------------------------------------------


import generate_cv  # noqa: E402


class TestGeneratedPdfPathContract:
    """`new_application` reads the PDF's location out of `generate_cv`'s stdout.

    That is a contract between two files dressed as a human-readable message,
    and it had no test on either side. Rewording the line is a one-word edit
    that looks cosmetic and costs every new application its `cv_pdf` reference.
    """

    @pytest.mark.parametrize("pages", [1, 2, 11])
    def test_it_reads_the_line_generate_cv_actually_prints(self, pages):
        """Built from `generate_cv.done_line`, so rewording one side fails here."""
        stdout = generate_cv.done_line("cv/versions/jane-acme.pdf", pages)
        assert new_application.parse_generated_pdf_path(stdout) == Path(
            "cv/versions/jane-acme.pdf"
        )

    def test_it_survives_a_path_containing_spaces(self):
        stdout = generate_cv.done_line("cv/versions/jane doe acme.pdf", 2)
        assert new_application.parse_generated_pdf_path(stdout) == Path(
            "cv/versions/jane doe acme.pdf"
        )

    def test_it_finds_the_line_among_other_output(self):
        stdout = "\n".join(
            [
                "Rendering...",
                generate_cv.done_line("cv/versions/x.pdf", 1),
                "trailing chatter",
            ]
        )
        assert new_application.parse_generated_pdf_path(stdout) == Path(
            "cv/versions/x.pdf"
        )

    def test_unrecognised_output_returns_none_rather_than_guessing(self):
        """The caller warns on None; a wrong path would be recorded as fact."""
        assert new_application.parse_generated_pdf_path("Done: x.pdf [1p]") is None
        assert new_application.parse_generated_pdf_path("") is None

    def test_the_format_still_carries_what_the_parser_needs(self):
        """Names the coupling outright, so a reword fails with an explanation.

        `DONE_LINE` is the single owner of this format; the parser depends on
        its arrow and its trailing page count.
        """
        assert "{path}" in generate_cv.DONE_LINE
        assert "{pages}" in generate_cv.DONE_LINE
        assert "→" in generate_cv.DONE_LINE
