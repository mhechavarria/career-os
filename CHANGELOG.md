# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
See [CONTRIBUTING.md](CONTRIBUTING.md#versioning) for what MAJOR / MINOR / PATCH
mean for a template repo.

## [Unreleased]

## [1.7.0] — 2026-08-10

### Added
- **`flywheel/skills/save-memory/SKILL.md` — index-discipline parity.** Step 4 now states a hard
  160-char cap per `MEMORY.md` index line, a rewrite-in-place rule (an updated entry replaces its
  existing line, never appends), GREEN/AMBER/RED byte bands (`< 16,000` / `16,000–19,999` /
  `>= 20,000`) with an archive-sweep procedure, and the
  `grep '^- \[' MEMORY.md | awk 'length($0)>160'` verification command run before a save reports
  done. Step 4 also states the `<type>_<slug>.md` file-name convention that the
  archive-eligibility rules key on, and clarifies that the `name:` frontmatter field stays the
  bare slug because it is the `[[link]]` target. Adds a new step 7, "Back up the store, if it
  is one" — a reminder-only step that prints the exact `git add`/`commit`/`push` commands only
  when the memory directory is already its own git repo, and stays a silent no-op otherwise;
  the flywheel itself still never runs a commit or a push. Step 6 (`lessons.md` promotion) is
  unchanged. Also ships an opt-in **durability tier**: `flywheel/check_memory.sh`, a read-only
  integrity check (index-size band, the 160-char line cap, index-to-body resolution, tracked-file
  linkage for both the bodies and the index files themselves, and frontmatter shape) and `flywheel/hooks/pre-push`, a thin caller that blocks a push
  on any `FAIL`, both documented in a new `flywheel/README.md` § "Advanced (optional): a durable,
  checked memory store" section. Both scripts are read-only, and both install into the memory
  directory (`check_memory.sh` at its root, the hook in its `.git/hooks/`), still outside this
  repo; the README's "What this never does" bullet is precision-fixed to say so.

### Changed
- **The dev toolchain and ruff's rule set are now pinned explicitly.** `requirements-dev.txt`
  pins `ruff==0.16.2`, `pytest==9.1.1` and `pymarkdownlnt==0.9.39` instead of resolving to
  whatever was newest at CI time, and `ruff.toml` selects `["E4", "E7", "E9", "F"]` rather than
  inheriting ruff's implicit default. That default is not stable across releases: ruff 0.16
  dropped `E4` and added isort, refurb, pylint and several flake8 rule sets, which turned CI red
  on code that had not changed. Pinning one dimension without the other leaves the same trap, so
  both are pinned — and a fork's first CI run now fails only on rules the fork opted into.
  Dependabot already covers pip weekly, so upgrades arrive as a reviewable PR instead of as a
  surprise on an unrelated branch. (#39)
- Bumped CI GitHub Actions: `actions/setup-python` v7. (#37)

### Fixed
- **`flywheel/skills/save-memory/SKILL.md` — the repo-root check no longer false-negatives on a
  trailing slash.** Step 7 gates the backup reminder on `git -C <memory-dir> rev-parse
  --show-toplevel` printing the memory directory itself, but that comparison was literal, and
  `--show-toplevel` never emits a trailing slash while a memory directory is very often written
  with one. A correctly configured store could therefore read as a mismatch. Because the step is
  a deliberate silent no-op when the check fails, the symptom was no output at all: the backup
  reminder simply never appeared, with nothing to indicate why. The check now strips a trailing
  `/` from both sides before comparing.

## [1.6.0] — 2026-07-02

### Added
- **The Judgment Flywheel — full-momentum upgrade** (`flywheel/`): an optional, opt-in
  layer for **Claude Code** users that adds session-to-session momentum on top of the
  v1.5.0 retro loop. Ships a tracked `flywheel/` directory with a `save-memory` skill
  (the capture engine — reviews a session and persists user / feedback / project /
  reference facts, and promotes durable job-search lessons back into `lessons.md`) and a
  `flywheel/README.md` that doubles as the **agent-executed install runbook**: tell Claude
  Code "set up the flywheel" and it installs the skill into the gitignored `.claude/`
  (skipping if a global `save-memory` already exists). No script, no new dependency, and
  nothing installed is ever committed. The harness auto-loads the memory index natively;
  an index-first manifest hook is documented as an **advanced, optional** extra, not part
  of the default install. Other editors stay on the editor-agnostic `lessons.md` loop and
  lose nothing.

## [1.5.0] — 2026-07-02

### Added
- **Company research folders** (`companies/<slug>/`) as a first-class part of the
  framework. `AGENT.md` gains **Phase 7 — Company Research**: a triage gate that
  hard-filters location / comp / role-type fit *before* any research or tailored-CV
  investment (so a full build is never sunk into a role the user can't take), then a
  research pass that separates confirmed facts from inferred ones, does "Why I Fit"
  honestly (names gaps with adjacent experience instead of inflating), and stops when
  the user can answer five questions about the company. Ships three coaching templates
  (`company-research`, `interview-prep`, `people`) whose section headers teach the
  quality bar inline, a `companies/README.md`, a rooted `.gitignore` entry (research is
  gitignored by default — it can hold interviewer names and comp figures), a **Company
  Research** view on `applications/pipeline.md`, and a fully worked example under
  `examples/sample-candidate/companies/quasar/`.
- **Interview prep** as `AGENT.md` **Phase 8 — Interview Prep**: map already-documented
  STAR stories to the role's themes (select, don't invent — one vivid specific, name the
  mechanism, land a company-tied punchline), read `people.md` first so a known interviewer
  reorders which story leads, pre-write the honest answer to the role's weakest gap, and
  handle the recruiter screen and any take-home as their own beats. Adds the in-interview
  anonymization discipline (tell stories without naming real customers or internal IDs).
- **Optional `architecture.md`** technical deep-dive — a seniority-gated template plus a
  worked example (`examples/sample-candidate/companies/quasar/architecture.md`) that
  doubles as system-design prep and models marking confirmed vs. inferred facts.
- `AGENT.md` **Phase 5** gains an explicit **honest-framing** rule: never inflate scope
  (used/extended ≠ built/owned), reframe grey-area work as the business outcome, and never
  imply employment at a vendor whose product you only integrated.
- **The Judgment Flywheel** — a repo-native `lessons.md` playbook that makes judgment
  compound across runs. `AGENT.md` **Phase 9 — Retro & the Judgment Flywheel** captures a
  short retro on **any** terminal outcome (including wins — offer/placed, the most valuable
  retro), and Phases 7.0 / 7 / 8 read `lessons.md` first so past lessons sharpen the next
  run before effort is spent. Ships an empty, instructional root `lessons.md` and a seeded
  example (`examples/sample-candidate/lessons.md`); the `AGENT.md` intro and README are
  refreshed for the full research → interview → retro scope.

### Changed
- `AGENT.md` Phase 0 no longer references a "planned" automated DOCX/PDF extraction
  script. After evaluation it was decided against: the agent reads PDFs directly and
  DOCX sources should be exported to PDF or pasted, so the doc-first intake needs no
  extra tooling — the dangling promise is removed rather than left unbuilt.

## [1.4.0] — 2026-06-05

### Changed
- `AGENT.md` Phase 3 experience schema adds a dedicated **`employer:`** frontmatter field for
  contractor / agency placements, so the staffing agency is recorded there instead of being
  overloaded into `role:` (the job-title field). `company:` stays the host/client, `role:` the
  title; `employer:` is optional and omitted for direct employment.
- `AGENT.md` Phase 3 documents a **contract-to-hire at the same host** pattern: keep one
  experience file spanning the whole tenure with both phases dated in Context, rather than
  splitting a continuous tenure into two jobs or laundering the contract phase into apparent
  direct employment.
- `AGENT.md` Phase 3 gives a **non-engineering prior career** (teaching, military, a trade) a
  home in the IC-centric experience schema via a `Prior-Career Impact` section that keeps
  outcomes in that domain's own terms — never relabeled as engineering metrics or promoted into
  the engineering impact library.
- `AGENT.md` Phase 5 documents an **employment-gap** pattern: let a multi-year break stay
  visible through honest non-overlapping dates (never a fabricated "Freelance" job or a
  stretched end date); optionally explain it in `profile/` or as a clearly-labeled `Career
  Break` line that is never dressed up as employment.
- `jd_gap.py` now detects the bare language / tool names **`python`**, **`java`**, **`ruby`**,
  and **`docker`**, which the CamelCase token regex missed — so a JD requiring any of them is
  no longer invisible in the gap report. Unlike `go`/`rust` these need no capitalization guard
  (they don't occur as ordinary English in a software JD/CV); `java` won't match `javascript`
  (word boundary) and `docker compose` is still counted as its own phrase first.

## [1.3.0] — 2026-06-04

### Changed
- `AGENT.md` Phase 0 now treats **quantitative self-claims** imported from an old CV /
  LinkedIn (years of experience, "millions of users", "10x faster") as unverified — confirm
  them against the role dates and the interview or drop them, never copy a tenure or scale
  claim straight into the CV summary.
- `AGENT.md` Phase 5 tailored-CV guidance now keeps roles in **reverse-chronological order**
  when tailoring (tailor by bullet selection and the summary, not by reordering roles — an
  out-of-order work history reads as an error to recruiters and ATS parsers).
- `AGENT.md` Phase 5 documents an **`Earlier Experience`** condensation pattern for long
  careers (more than ~5–6 roles): full bullets for the recent 3–4 roles, one line each for
  the rest, so the CV stays within the 2-page cap without reordering or padding.
- `AGENT.md` Phase 3 experience schema now covers **management / lead roles** via an optional
  `Leadership & Management` section, giving leadership impact a home in the IC-centric schema.
- `AGENT.md` adds an optional **`Open (unquantified)`** impact-library holding section for
  achievements that aren't CV-ready yet, and the bullet-quality rule now prefers the user's
  literal before/after over a derived multiplier ("weekly → daily", not "~5×").
- `jd_gap.py` now detects **Go / Golang** as a keyword. "go" is two lowercase letters
  the token regex couldn't see, so a Go requirement in a JD was previously invisible in
  the gap report. Detection is scoped to the capitalized `Go` language token plus
  `golang`, so ordinary English ("go to market", "go deep", "Go-getter") isn't miscounted.
- `jd_gap.py` now also detects **Rust** (a capitalized standalone token, the same
  treatment as `Go`), so a "Rust" requirement in a JD is no longer invisible in the gap
  report. Both common-English-word language names now live in one extensible
  `CAPITALIZED_LANG_TOKENS` map; lowercase prose ("trust", "rusty", "Rust Belt") still
  isn't miscounted.
- `jd_gap.py` now applies that same guarded matcher when checking whether the **CV**
  covers a `Go`/`Rust` requirement, not just when reading the JD. Previously a CV that
  merely mentioned "Rust Belt" (or "go to market") was counted as covering the language,
  so a genuinely missing requirement was silently dropped from the gap report instead of
  flagged as MISSING.
- `new_application.py` now reuses a `--jd` file that already lives in `jds/` instead of
  copying it to a second `jds/<company>-<role>.txt` — so a saved JD whose slug differs
  from `<company>-<role>` no longer produces a duplicate, and the application's `jd_file`
  points at the file you actually saved.
- `new_application.py` slugs (and the matching `AGENT.md` filename rule) now transliterate
  accents to ASCII (`José → jose`) instead of stripping them to a stray hyphen (`jos-…`),
  keeping generated PDF and JD filenames clean for non-ASCII names.
- `AGENT.md` impact-library guidance now lists the aggregate theme headings, scopes the
  full inline-field set (`tags::`/`company::`/`category::`) to the per-company files while
  the aggregate carries only `[company:: ]`, and clarifies that `category::` is an
  orthogonal per-bullet tag, not a section heading.

### Fixed
- `jd_gap.py` no longer crashes with a raw `FileNotFoundError` traceback when the JD or
  CV path is missing — it prints a clear error and exits 1, matching `generate_cv.py`.
- `pipeline_report.py` now warns (on stderr) when an application references a missing
  `jd_file`/`cv_version` instead of silently dropping it from the gap aggregation;
  `new_application.py`'s missing-JD warning also moved to stderr for consistency.
- `pipeline_report.py`'s missing-keyword section is now titled "MASTER-CV GAP SUGGESTIONS
  — keywords missing across applications" (was "MASTER CV GAPS"), making clear it
  aggregates each application's *tailored* `cv_version` rather than scanning `cv/master.md`.
- `AGENT.md` now defines the `experience/<year>-<company>.md` filename rules (start year;
  lowercase, hyphenated, accent-transliterated company slug; contractor-via-agency
  handling), and adds an explicit "never fabricate a metric — prefer a `- [ ] TODO:`"
  rule to the bullet-quality standard.
- `AGENT.md` / `cv/master.md` summary guidance reconciled (both now describe a short
  2–4-sentence paragraph), the experience `status` enum is glossed, the CV **Skills**
  block is documented as a condensed view of `profile/skills.md`, and the CV
  bullet-count guidance is clarified as a ceiling (`generate_cv.py` warns above 5).

## [1.2.0] — 2026-06-02

### Added
- **Source intake (Phase 0)** — an optional first intake phase in `AGENT.md` plus a
  `sources/` folder: drop an old CV (`.md` / `.txt` / `.pdf`) or pasted LinkedIn text
  and the agent seeds your profile and role skeletons from it, so the interview can
  focus on the metrics and evidence those documents lack. Imported bullets without a
  number land as `- [ ] TODO:` items, and raw sources are gitignored by default to
  keep PII out of Git.

## [1.1.0] — 2026-06-02

### Added
- **Worked example** — `examples/sample-candidate/`, a complete, filled-in Career OS
  instance for a fictional engineer (profile, five roles, per-company impact
  libraries, project writeups, a master CV, and three tailored CV variants targeting
  three job descriptions), so new users can see what a finished instance looks like. (#8)
- **End-to-end pipeline runner** — `examples/run_pipeline.py` drives every script
  (CV render → keyword gap → application bootstrap → pipeline report) against the
  sample data on a throwaway working copy, plus a CI job that runs it on every push
  and PR. (#8)
- README **Table of contents**, a **Why Career OS exists** section, a **Tests**
  section documenting the CI suite, and an **Acknowledgements** section crediting the
  [Tech Interview Handbook resume guide](https://www.techinterviewhandbook.org/resume/)
  by Yangshun Tay. (#9, #10)

### Changed
- Revamped the README following common README best practices; it now documents the
  worked example and the local test commands. (#9)
- Raised dependency floors: `weasyprint>=68.1`, `pyyaml>=6.0.3`, `markdown2>=2.5.5`.
- Bumped CI/release GitHub Actions: `actions/checkout` v6, `actions/setup-python` v6,
  `actions/upload-artifact` v7, `softprops/action-gh-release` v3.

### Fixed
- Smoothed out the new-user developer experience: hardened setup instructions, made
  the impact library the default, and made the application pipeline stage-driven.

## [1.0.0] — 2026-05-29

### Added
- Initial public release of the Career OS template.
- `AGENT.md` — phased AI intake guide (profile → experience → impacts → CV → applications).
- Toolchain: `generate_cv.py` (ATS PDF generator with validator + page-count guard),
  `jd_gap.py` (keyword-coverage analyzer with synonym map), `new_application.py`,
  `pipeline_report.py`, `cv_style.css`.
- Blank skeletons for `profile/`, `cv/master.md`, `impacts/`, and the
  `experience/` · `applications/` · `jds/` workflows.
- Templates for role, project, and STAR-story capture.
- Unit tests for the gap analyzer (`tests/test_jd_gap.py`).
- Project governance: MIT license, contribution guide, code of conduct, security
  policy, PR/issue templates, Dependabot, and CI (lint · test · PDF render).

[Unreleased]: https://github.com/mhechavarria/career-os/compare/v1.7.0...HEAD
[1.7.0]: https://github.com/mhechavarria/career-os/compare/v1.6.0...v1.7.0
[1.6.0]: https://github.com/mhechavarria/career-os/compare/v1.5.0...v1.6.0
[1.5.0]: https://github.com/mhechavarria/career-os/compare/v1.4.0...v1.5.0
[1.4.0]: https://github.com/mhechavarria/career-os/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/mhechavarria/career-os/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/mhechavarria/career-os/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/mhechavarria/career-os/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/mhechavarria/career-os/releases/tag/v1.0.0
