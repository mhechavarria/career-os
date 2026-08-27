"""Unit tests for scripts/generate_cv.py — output naming and the Done contract.

The PDF leaves the repo, so its filename is the only thing telling the person
who opens it whose CV it is. Getting that wrong is not cosmetic.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import generate_cv  # noqa: E402


def cv_for(name: str) -> str:
    """A CV document opening with the candidate's name as its H1.

    `default_output_path` takes the document, not a name: the owner is read
    from the file so a fork gets its own name with nothing to configure.
    """
    return f"# {name}\n\nSenior Backend Engineer\n"


# --- default_output_path ----------------------------------------------------


def test_the_candidate_name_is_prefixed_to_the_pdf():
    out = generate_cv.default_output_path(Path("acme-staff.md"), cv_for("Jane Roe"))
    assert out.name == "jane-roe-acme-staff.pdf"


def test_an_already_prefixed_stem_is_not_prefixed_twice():
    out = generate_cv.default_output_path(Path("jane-roe-acme.md"), cv_for("Jane Roe"))
    assert out.name == "jane-roe-acme.pdf"


def test_a_stem_equal_to_the_name_is_left_alone():
    out = generate_cv.default_output_path(Path("jane-roe.md"), cv_for("Jane Roe"))
    assert out.name == "jane-roe.pdf"


def test_a_partial_name_match_is_still_prefixed():
    """`ann` is a prefix of the stem `anna-staff`, but it is not that name.

    A bare `startswith` read the stem as already prefixed, so Ann's CV kept a
    filename built from someone else's name and never gained her own. The PDF
    is the artefact that leaves the repo, so it carried the wrong person.
    """
    out = generate_cv.default_output_path(Path("anna-staff.md"), cv_for("Ann"))
    assert out.name == "ann-anna-staff.pdf"


def test_two_names_sharing_a_prefix_do_not_produce_one_filename():
    anna = generate_cv.default_output_path(Path("anna-staff.md"), cv_for("Anna"))
    ann = generate_cv.default_output_path(Path("anna-staff.md"), cv_for("Ann"))
    assert anna.name == "anna-staff.pdf"  # genuinely already prefixed
    assert ann.name == "ann-anna-staff.pdf"
    assert anna.name != ann.name


def test_the_directory_is_preserved():
    out = generate_cv.default_output_path(
        Path("cv/versions/acme.md"), cv_for("Jane Roe")
    )
    assert out.parent == Path("cv/versions")


def test_an_unreadable_name_leaves_the_stem_alone():
    """`name_slug` returns empty when it cannot find a name to use."""
    out = generate_cv.default_output_path(Path("acme-staff.md"), "")
    assert out.name == "acme-staff.pdf"


# --- the line new_application.py parses -------------------------------------


def test_done_line_singular_and_plural():
    assert generate_cv.done_line("x.pdf", 1).endswith("(1 page)")
    assert generate_cv.done_line("x.pdf", 2).endswith("(2 pages)")


def test_done_line_carries_the_path_verbatim():
    assert "cv/versions/jane-acme.pdf" in generate_cv.done_line(
        "cv/versions/jane-acme.pdf", 1
    )
