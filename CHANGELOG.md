# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
See [CONTRIBUTING.md](CONTRIBUTING.md#versioning) for what MAJOR / MINOR / PATCH
mean for a template repo.

## [Unreleased]

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

[Unreleased]: https://github.com/mhechavarria/career-os/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/mhechavarria/career-os/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/mhechavarria/career-os/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/mhechavarria/career-os/releases/tag/v1.0.0
