"""Tests for the stage vocabulary and reach accounting in pipeline_report.

`stage` records where an application IS; `furthest_stage` records how far it
GOT. These pull in opposite directions exactly when an application screened and
then closed, which is the case that used to be counted inconsistently.
"""

import sys
from pathlib import Path

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
        assert "Applications:     1" in out.out
        assert "Phone screen:       0" in out.out

    def test_the_warning_never_contradicts_the_rate_printed_below_it(
        self, tmp_path, monkeypatch, capsys
    ):
        """A typo'd `stage` next to a valid `furthest_stage` DOES screen.

        The warning used to deny that in the same breath as the funnel counted
        it, so the reader had to pick which half of one report to believe.
        """
        out = self._report(
            tmp_path,
            monkeypatch,
            capsys,
            "type: application\ncompany: Acme\n"
            "stage: phone-scren\nfurthest_stage: phone-screen",
        )
        assert "Phone screen:       1" in out.out
        assert "never count as a screen" not in out.err
        assert "falls back to 'applied'" not in out.err
        # It names the reach that was actually used, so it cannot drift.
        assert "'phone-screen'" in out.err

    def test_it_names_the_fallback_when_there_is_no_declared_reach(
        self, tmp_path, monkeypatch, capsys
    ):
        out = self._report(
            tmp_path,
            monkeypatch,
            capsys,
            "type: application\ncompany: Acme\nstage: phone-scren",
        )
        assert "reach reads as 'applied'" in out.err

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
