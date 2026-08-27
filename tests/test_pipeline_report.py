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


class ReportHarness:
    """Runs the real `main()` over a throwaway repo and reads what it printed.

    Asserting on the report itself is the point. Checking the helper functions
    in isolation is what let two earlier versions of these tests pass against
    the very defects they were written to pin.
    """

    def _report(self, tmp_path, monkeypatch, capsys, *frontmatters: str):
        apps = tmp_path / "applications"
        apps.mkdir()
        for i, frontmatter in enumerate(frontmatters):
            (apps / f"app{i}.md").write_text(
                f"---\n{frontmatter}\n---\n", encoding="utf-8"
            )
        monkeypatch.setattr(pr, "REPO_ROOT", tmp_path)
        pr.main()
        return capsys.readouterr()

    @staticmethod
    def _line(report: str, label: str) -> str:
        return next(ln for ln in report.splitlines() if ln.strip().startswith(label))

    @classmethod
    def _count(cls, report: str, label: str) -> int:
        """The counted value on one funnel line, not a substring of the line.

        `"Phone screen:       1" in out` is a substring test: it survives a
        changed column width and reads as satisfied by anything that happens to
        contain those characters. Split the real line instead.
        """
        line = cls._line(report, label)
        return int(
            line.split()[-2] if line.rstrip().endswith(")") else line.split()[-1]
        )

    @classmethod
    def _percent(cls, report: str, label: str) -> str:
        """The rate, which is where a wrong denominator shows and a count does not."""
        line = cls._line(report, label).rstrip()
        return line.split()[-1] if line.endswith(")") else ""


class TestUnrecognisedStageWarning(ReportHarness):
    """The warning is the thing under test, so the report has to actually run.

    An earlier version of this file asserted only `furthest_stage()` and the
    stage sets. Both were already correct, so it passed against the very
    warning text it was written to pin, and would have kept passing while the
    message said anything at all.
    """

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


class TestFunnelArithmetic(ReportHarness):
    """The conversion rates are the reason this tool exists, and three of the
    rules behind them survived every mutation the review threw at them.

    Each test below names the mutant it kills, because a rate test that only
    asserts a count passes against a wrong denominator: the count is right in
    both, and only the percentage moves.
    """

    APPLIED = "type: application\ncompany: Alfa\nstage: applied"
    DRAFT = "type: application\ncompany: Bravo\nstage: draft\nrole: Backend"

    def test_a_draft_stays_out_of_every_denominator(
        self, tmp_path, monkeypatch, capsys
    ):
        """Kills `submitted = list(apps)`.

        A draft is tailored work that was never sent, so it has no outcome to
        measure. Counting it would silently deflate every rate in the report,
        and this line is the whole reason the stage exists.
        """
        out = self._report(
            tmp_path,
            monkeypatch,
            capsys,
            "type: application\ncompany: Alfa\nstage: phone-screen"
            "\nfurthest_stage: phone-screen",
            self.DRAFT,
        )
        assert self._count(out.out, "Applications:") == 1
        assert self._percent(out.out, "Phone screen:") == "(100%)"
        assert "NOT SUBMITTED" in out.out
        assert "Bravo" in out.out

    def test_the_technical_rate_is_out_of_screens_not_applications(
        self, tmp_path, monkeypatch, capsys
    ):
        """Kills `pct(technical, total)`.

        "How many of the screens reached a technical round" is the question
        worth asking; dividing by every application answers a different one.
        Both denominators print `Technical round: 1`, so only the rate catches
        it.
        """
        out = self._report(
            tmp_path,
            monkeypatch,
            capsys,
            self.APPLIED,
            "type: application\ncompany: Charlie\nstage: technical"
            "\nfurthest_stage: technical",
        )
        assert self._count(out.out, "Applications:") == 2
        assert self._count(out.out, "Phone screen:") == 1
        assert self._count(out.out, "Technical round:") == 1
        assert self._percent(out.out, "Technical round:") == "(100%)"

    def test_a_placement_counts_as_an_offer_too(self, tmp_path, monkeypatch, capsys):
        """Kills `offers = reach_counts.get("offer", 0)`.

        Nobody is placed without being offered first, so a placement that did
        not increment offers would report a funnel narrower at the offer step
        than at the step after it.
        """
        out = self._report(
            tmp_path,
            monkeypatch,
            capsys,
            "type: application\ncompany: Delta\nstage: placed\nfurthest_stage: placed",
        )
        assert self._count(out.out, "Placed:") == 1
        assert self._count(out.out, "Offer:") == 1

    def test_no_rate_exceeds_the_step_above_it(self, tmp_path, monkeypatch, capsys):
        """A funnel that widens as it narrows is arithmetically impossible."""
        out = self._report(
            tmp_path,
            monkeypatch,
            capsys,
            self.APPLIED,
            "type: application\ncompany: Charlie\nstage: technical"
            "\nfurthest_stage: technical",
            "type: application\ncompany: Delta\nstage: placed\nfurthest_stage: placed",
        )
        total = self._count(out.out, "Applications:")
        screened = self._count(out.out, "Phone screen:")
        technical = self._count(out.out, "Technical round:")
        offers = self._count(out.out, "Offer:")
        placed = self._count(out.out, "Placed:")
        assert total >= screened >= technical >= offers >= placed


class TestCvPerformanceTable(ReportHarness):
    """The per-CV table is where the `on-hold` behaviour actually changed, and
    it had no end-to-end test at all: its screen rule could be replaced with
    `if True` without failing anything."""

    def test_only_a_reach_past_applied_counts_as_a_screen(
        self, tmp_path, monkeypatch, capsys
    ):
        """Kills `if True` and `in STAGES_ORDER` in the cv_perf screen rule.

        `applied` is in STAGES_ORDER but is not a screen, so a rule using the
        wrong set credits every submitted application with one.
        """
        out = self._report(
            tmp_path,
            monkeypatch,
            capsys,
            "type: application\ncompany: Alfa\nstage: applied"
            "\ncv_version: cv/versions/backend.md",
            "type: application\ncompany: Bravo\nstage: rejected"
            "\nfurthest_stage: phone-screen\ncv_version: cv/versions/backend.md",
        )
        line = self._line(out.out, "backend")
        assert "2 apps" in line
        assert "1 screen" in line and "1 screens" not in line
        assert line.rstrip().endswith("(50%)")

    def test_a_parked_application_without_a_declared_reach_is_not_a_screen(
        self, tmp_path, monkeypatch, capsys
    ):
        """The exact case this change fixed: `on-hold` used to count here and
        not in the funnel, so one report disagreed with itself."""
        out = self._report(
            tmp_path,
            monkeypatch,
            capsys,
            "type: application\ncompany: Alfa\nstage: on-hold"
            "\ncv_version: cv/versions/backend.md",
        )
        assert "0 screens" in self._line(out.out, "backend")
        assert self._count(out.out, "Phone screen:") == 0


class TestGapAggregation(ReportHarness):
    """Keyword aggregation across applications, untested end to end until now."""

    @staticmethod
    def _link(tmp_path, slug: str, jd_terms: str, cv_body: str = "Nothing here"):
        (tmp_path / "jds").mkdir(exist_ok=True)
        (tmp_path / "cv" / "versions").mkdir(parents=True, exist_ok=True)
        (tmp_path / "jds" / f"{slug}.txt").write_text(jd_terms, encoding="utf-8")
        (tmp_path / "cv" / "versions" / f"{slug}.md").write_text(
            cv_body, encoding="utf-8"
        )
        return (
            f"type: application\ncompany: {slug.title()}\nstage: applied"
            f"\njd_file: jds/{slug}.txt\ncv_version: cv/versions/{slug}.md"
        )

    def test_a_term_missing_from_two_applications_is_counted_twice(
        self, tmp_path, monkeypatch, capsys
    ):
        """Kills `missing_counter[term] = 1`.

        The count IS the signal: a keyword missing once is noise, and one
        missing across many applications is what earns a place on the master
        CV. Collapsing it to 1 silences the ranking without changing anything
        visible about which terms appear.
        """
        out = self._report(
            tmp_path,
            monkeypatch,
            capsys,
            self._link(tmp_path, "alfa", "We need Kubernetes experience."),
            self._link(tmp_path, "bravo", "Kubernetes, mostly."),
        )
        assert "[ 2/2 apps]" in out.out
        assert "kubernetes" in out.out

    def test_a_dangling_file_reference_is_reported_and_excluded(
        self, tmp_path, monkeypatch, capsys
    ):
        """Kills replacing the `continue` with `pass`.

        A typo'd path must not vanish from the analysis silently; it is the
        difference between "this JD has no gaps" and "this JD was never read".
        """
        out = self._report(
            tmp_path,
            monkeypatch,
            capsys,
            "type: application\ncompany: Alfa\nstage: applied"
            "\njd_file: jds/missing.txt\ncv_version: cv/versions/gone.md",
        )
        assert "missing file" in out.err
        assert "No JD files linked yet" in out.out

    def test_the_keyword_denominator_includes_drafts(
        self, tmp_path, monkeypatch, capsys
    ):
        """Kills `tailored = len(submitted)`.

        A draft is excluded from every OUTCOME rate because it has no outcome,
        but its tailoring is real CV work and belongs in the gap denominator.
        The two counts are deliberately different populations.
        """
        draft = self._link(tmp_path, "bravo", "Kubernetes again.").replace(
            "stage: applied", "stage: draft"
        )
        out = self._report(
            tmp_path,
            monkeypatch,
            capsys,
            self._link(tmp_path, "alfa", "We need Kubernetes experience."),
            draft,
        )
        assert self._count(out.out, "Applications:") == 1
        assert "[ 2/2 apps]" in out.out


class TestDeclaredReachWarning(ReportHarness):
    def test_a_valid_furthest_stage_is_not_warned_about(
        self, tmp_path, monkeypatch, capsys
    ):
        """Kills inverting the `reach not in STAGES_ORDER` condition."""
        out = self._report(
            tmp_path,
            monkeypatch,
            capsys,
            "type: application\ncompany: Alfa\nstage: rejected\nfurthest_stage: onsite",
        )
        assert "unrecognised furthest_stage" not in out.err

    def test_a_misspelled_furthest_stage_is_warned_about(
        self, tmp_path, monkeypatch, capsys
    ):
        out = self._report(
            tmp_path,
            monkeypatch,
            capsys,
            "type: application\ncompany: Alfa\nstage: rejected\nfurthest_stage: onsit",
        )
        assert "unrecognised furthest_stage 'onsit'" in out.err


class TestDraftOnlyInstance(ReportHarness):
    def test_a_repo_holding_only_drafts_reports_without_dividing_by_zero(
        self, tmp_path, monkeypatch, capsys
    ):
        """Kills relaxing `pct`'s `d > 0` guard to `d >= 0`.

        Nothing has been submitted, so every outcome denominator is zero. This
        is the state a fresh instance is in, which makes it the first thing a
        new user would hit.
        """
        out = self._report(
            tmp_path,
            monkeypatch,
            capsys,
            "type: application\ncompany: Alfa\nstage: draft\nrole: Backend",
        )
        assert self._count(out.out, "Applications:") == 0
        assert self._percent(out.out, "Phone screen:") == ""
        assert "NOT SUBMITTED" in out.out

    def test_pct_guards_a_zero_denominator_directly(self):
        assert pr.pct(0, 0) == ""
        assert pr.pct(1, 2) == "(50%)"
