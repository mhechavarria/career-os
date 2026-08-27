"""Tests for the stage vocabulary and reach accounting in pipeline_report.

`stage` records where an application IS; `furthest_stage` records how far it
GOT. These pull in opposite directions exactly when an application screened and
then closed, which is the case that used to be counted inconsistently.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import pipeline_report as pr  # noqa: E402


class TestFurthestStage:
    def test_declared_reach_survives_a_closed_stage(self):
        """An application that screened, then closed on an eligibility gap."""
        assert (
            pr.furthest_stage({"stage": "rejected", "furthest_stage": "phone-screen"})
            == "phone-screen"
        )

    def test_a_stale_declared_value_never_holds_back_a_live_stage(self):
        """The regression that made the funnel report no progression at all.

        `new_application.py` writes `furthest_stage: applied` into every file it
        creates, and its own closing instruction used to tell the user to update
        `stage` only. Trusting the declared value blindly meant an application
        that reached an onsite still counted as never screened. It is a
        high-water mark: the further of the two wins, whichever field holds it.
        """
        assert (
            pr.furthest_stage({"stage": "technical", "furthest_stage": "applied"})
            == "technical"
        )
        assert (
            pr.furthest_stage({"stage": "onsite", "furthest_stage": "phone-screen"})
            == "onsite"
        )
        assert (
            pr.furthest_stage({"stage": "placed", "furthest_stage": "applied"})
            == "placed"
        )

    def test_parked_application_keeps_its_reach(self):
        """An application that screened before the employer froze the requisition."""
        assert (
            pr.furthest_stage({"stage": "on-hold", "furthest_stage": "phone-screen"})
            == "phone-screen"
        )

    def test_draft_has_no_reach(self):
        """An unsent application must not inherit `applied` from the fallback."""
        assert pr.furthest_stage({"stage": "draft", "furthest_stage": "null"}) == ""
        assert pr.furthest_stage({"stage": "draft"}) == ""

    def test_falls_back_to_stage_when_field_absent(self):
        assert pr.furthest_stage({"stage": "onsite"}) == "onsite"

    def test_fallback_refuses_to_credit_a_non_lifecycle_stage(self):
        """Without the field, `on-hold` proves only that it was applied to."""
        assert pr.furthest_stage({"stage": "on-hold"}) == "applied"
        assert pr.furthest_stage({"stage": "rejected"}) == "applied"

    def test_null_and_empty_are_treated_as_absent(self):
        assert (
            pr.furthest_stage({"stage": "applied", "furthest_stage": "null"})
            == "applied"
        )
        assert (
            pr.furthest_stage({"stage": "applied", "furthest_stage": ""}) == "applied"
        )


class TestStageVocabulary:
    def test_screened_stages_excludes_applied(self):
        assert "applied" not in pr.SCREENED_STAGES
        assert "phone-screen" in pr.SCREENED_STAGES
        assert "placed" in pr.SCREENED_STAGES

    def test_known_stages_covers_the_whole_vocabulary(self):
        """Anything outside the vocabulary silently skews the rates.

        Derived from the sets rather than retyped: the hand-written list this
        replaces omitted `technical`, `system-design`, `take-home`, `onsite`
        and `offer` while its name promised every stage.
        """
        for group in (
            pr.STAGES_ORDER,
            pr.CLOSED_STAGES,
            pr.PRE_SUBMISSION_STAGES,
            pr.PARKED_STAGES,
        ):
            for stage in group:
                assert stage in pr.KNOWN_STAGES

    def test_a_rejected_screen_still_counts_as_a_screen(self):
        """The regression this file exists for."""
        apps = [
            {"stage": "rejected", "furthest_stage": "phone-screen"},
            {"stage": "on-hold", "furthest_stage": "phone-screen"},
            {"stage": "rejected", "furthest_stage": "applied"},
        ]
        screened = sum(1 for a in apps if pr.furthest_stage(a) in pr.SCREENED_STAGES)
        assert screened == 2


class TestUnrecognisedStageWarning:
    """The warning is the thing under test, so the report has to actually run.

    An earlier version of this file asserted only `furthest_stage()` and the
    stage sets. Both were already correct, so it passed against the very
    warning text it was written to pin, and would have kept passing while the
    message said anything at all.
    """

    def _report(self, tmp_path, monkeypatch, capsys, frontmatter: str):
        apps = tmp_path / "applications"
        apps.mkdir()
        (apps / "a.md").write_text(f"---\n{frontmatter}\n---\n", encoding="utf-8")
        monkeypatch.setattr(pr, "REPO_ROOT", tmp_path)
        pr.main()
        return capsys.readouterr()

    @staticmethod
    def _count(report: str, label: str) -> int:
        """The counted value on one funnel line, not a substring of the line.

        `"Phone screen:       1" in out` is a substring test: it survives a
        changed column width and reads as satisfied by anything that happens to
        contain those characters. Split the real line instead.
        """
        line = next(ln for ln in report.splitlines() if ln.strip().startswith(label))
        return int(
            line.split()[-2] if line.rstrip().endswith(")") else line.split()[-1]
        )

    def test_it_warns_and_still_counts_the_application(
        self, tmp_path, monkeypatch, capsys
    ):
        out = self._report(
            tmp_path,
            monkeypatch,
            capsys,
            "type: application\ncompany: Acme\nstage: phone-scren",
        )
        assert "unrecognised stage 'phone-scren'" in out.err
        assert self._count(out.out, "Applications:") == 1
        assert self._count(out.out, "Phone screen:") == 0

    # Distinct reaches, most of them not derivable from "is the field set?".
    # A message that hardcodes the answer instead of asking `furthest_stage()`
    # would have to enumerate the whole lifecycle to pass, at which point it IS
    # the function. The earlier version asserted two, and a conditional
    # hardcode that consulted nothing satisfied both.
    @pytest.mark.parametrize(
        "declared,expected_reach,expected_screens",
        [
            (None, "applied", 0),
            ("phone-screen", "phone-screen", 1),
            ("onsite", "onsite", 1),
            ("placed", "placed", 1),
            # Both fields misspelled. The only case in this branch where the
            # raw `furthest_stage` field and the computed reach disagree, so
            # it is the only one that catches a message echoing the field
            # instead of asking for the high-water mark.
            ("onsit", "applied", 0),
        ],
    )
    def test_the_warning_names_the_reach_the_funnel_actually_counted(
        self,
        tmp_path,
        monkeypatch,
        capsys,
        declared,
        expected_reach,
        expected_screens,
    ):
        """The warning and the rate below it have to tell the same story.

        The first two wordings each denied, in prose, a screen the funnel went
        on to count, leaving the reader to pick which half of one report to
        believe. Asserting both together is the only thing that pins that.
        """
        frontmatter = "type: application\ncompany: Acme\nstage: phone-scren"
        if declared:
            frontmatter += f"\nfurthest_stage: {declared}"
        out = self._report(tmp_path, monkeypatch, capsys, frontmatter)

        assert f"reach reads as '{expected_reach}'" in out.err
        assert self._count(out.out, "Phone screen:") == expected_screens
        assert "never count as a screen" not in out.err
        assert "will not count toward any rate" not in out.err

    def test_a_recognised_stage_warns_about_nothing(
        self, tmp_path, monkeypatch, capsys
    ):
        out = self._report(
            tmp_path,
            monkeypatch,
            capsys,
            "type: application\ncompany: Acme\nstage: phone-screen",
        )
        assert "unrecognised stage" not in out.err
