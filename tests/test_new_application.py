"""Unit tests for scripts/new_application.py — slug + JD-handling behavior."""

import sys
from pathlib import Path

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
