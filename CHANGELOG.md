# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
See [CONTRIBUTING.md](CONTRIBUTING.md#versioning) for what MAJOR / MINOR / PATCH
mean for a template repo.

## [Unreleased]

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

[Unreleased]: https://github.com/mhechavarria/career-os/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/mhechavarria/career-os/releases/tag/v1.0.0
