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

    def test_known_stages_covers_every_stage_in_the_repo(self):
        """Anything outside the vocabulary silently skews the rates."""
        for stage in (
            "draft",
            "applied",
            "phone-screen",
            "on-hold",
            "rejected",
            "ghosted",
            "withdrawn",
            "placed",
        ):
            assert stage in pr.KNOWN_STAGES

    def test_an_unrecognised_stage_still_counts_as_an_application(self):
        """The warning used to promise the opposite of what the code does.

        An unrecognised `stage` is not a draft, so the record stays in the
        submitted set and sits in every denominator, while its reach falls
        back to `applied` and never reaches SCREENED_STAGES. That is a typo
        deflating the rates, not a record being skipped, and the warning has
        to say so or it sends the reader looking for a missing application.
        """
        typo = {"stage": "phone-scren"}
        assert typo["stage"] not in pr.KNOWN_STAGES
        assert typo["stage"] not in pr.PRE_SUBMISSION_STAGES
        assert pr.furthest_stage(typo) == "applied"
        assert pr.furthest_stage(typo) not in pr.SCREENED_STAGES

    def test_a_rejected_screen_still_counts_as_a_screen(self):
        """The regression this file exists for."""
        apps = [
            {"stage": "rejected", "furthest_stage": "phone-screen"},
            {"stage": "on-hold", "furthest_stage": "phone-screen"},
            {"stage": "rejected", "furthest_stage": "applied"},
        ]
        screened = sum(1 for a in apps if pr.furthest_stage(a) in pr.SCREENED_STAGES)
        assert screened == 2
