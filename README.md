# Career OS

[![CI](https://github.com/mhechavarria/career-os/actions/workflows/ci.yml/badge.svg)](https://github.com/mhechavarria/career-os/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/mhechavarria/career-os)](https://github.com/mhechavarria/career-os/releases)

A markdown-first, Git-tracked, AI-driven system for managing your professional
narrative, impact history, and CV tailoring — so you never have to reconstruct
your achievements from scratch during a job search again.

> **This is a template.** It ships with blank skeletons and an AI intake guide.
> Click **"Use this template"** (or fork), then let an AI agent interview you and
> fill it in.

## What you get

- A single source of truth for your profile, experience, and impact evidence.
- Continuous impact capture — log wins as they happen, not during a panic.
- On-demand, **ATS-compliant PDF CVs** generated from plain markdown.
- Keyword **gap analysis** between any job description and your CV.
- Application tracking with a pipeline dashboard.
- Fully portable: plain markdown + Git, no vendor lock-in.

## What this is not

- Not a hosted service — everything runs locally in your own clone.
- Not an AI resume "writer" — it structures *your* real evidence; you stay honest.

## Quick start

### 1. Create your own copy

Click **Use this template → Create a new repository** (recommended), or clone:

```bash
git clone https://github.com/mhechavarria/career-os.git my-career-os
cd my-career-os
```

### 2. Open it in an AI-enabled editor

Works with Claude Code, Cursor, or any editor whose AI assistant can read and
write files in the repo.

### 3. Run the intake

Tell the agent:

> Read `AGENT.md` and follow it to set up my Career OS. Start with Phase 1.

It asks one topic at a time and writes files as it goes. A full intake takes
roughly 60–90 minutes, naturally split across sessions (one role per session is a
good pace).

| Phase | Files produced |
| --- | --- |
| Profile intake | `profile/*.md` |
| Per-role deep-dive | `experience/<year>-<company>.md` + `impacts/impact-library-<company>.md` |
| Brag doc | `impacts/brag-doc.md` |
| CV assembly | `cv/master.md` + `cv/versions/<target>.md` |
| Applications | `applications/<company>-YYYY-MM.md` + `jds/<slug>.txt` |

## Repository structure

```text
career-os/
├── AGENT.md             # AI intake instructions — start here
├── profile/             # Identity and positioning (about, headline, skills, ...)
├── experience/          # One file per role
├── impacts/             # Impact library + quarterly brag doc
├── cv/                  # master.md, ats-checklist.md, versions/
├── applications/        # One file per application + pipeline.md dashboard
├── jds/                 # Archived job descriptions (for gap analysis)
├── scripts/             # Tooling (PDF generation, gap analysis, tracking)
├── templates/           # Blank templates for manual use
└── tests/               # Unit tests for the tooling
```

## Generate an ATS-compliant PDF

Install dependencies once:

```bash
pip install -r requirements.txt
```

On Linux, WeasyPrint also needs a few system libraries:

```bash
sudo apt-get install -y libpango-1.0-0 libpangocairo-1.0-0 \
  libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
```

Then render any CV file:

```bash
python3 scripts/generate_cv.py cv/master.md
# → cv/master.pdf
```

The generator strips Obsidian syntax, warns on ATS violations (tables, images,
more than 5 bullets per role, bullets without metrics, more than 2 pages), and
renders selectable-text output with no headers or footers.

## Tooling

| Script | Purpose |
| --- | --- |
| `generate_cv.py` | ATS-compliant PDF from a CV markdown file |
| `jd_gap.py` | Keyword-coverage analysis (JD vs CV) with a synonym map |
| `new_application.py` | Bootstrap an application file with gap analysis + PDF |
| `pipeline_report.py` | Aggregate gaps + conversion funnel across applications |

## Tool compatibility

- **Obsidian** — open as a vault; inline `[field:: value]` tags drive Dataview queries.
- **Any markdown editor** — plain markdown with YAML frontmatter.
- **Git** — full version history of your career documentation.

## Contributing

Issues and PRs are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md) and the
[Code of Conduct](CODE_OF_CONDUCT.md). Releases follow
[Semantic Versioning](https://semver.org) and are tracked in
[CHANGELOG.md](CHANGELOG.md).

## License

Released under the [MIT License](LICENSE).
