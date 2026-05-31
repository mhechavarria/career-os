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

### 4. Make it yours

The template ships with **genericized sample content** (a placeholder profile,
`cv/master.md`, and impact files) so the shape of each file is clear. The intake in
step 3 overwrites these with your real information — you don't need to delete anything
first. Folders like `applications/`, `cv/versions/`, `experience/`, and `jds/` start
empty (kept by `.gitkeep`) and fill up as you go.

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

Set up a virtual environment and install the Python dependencies once:

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

> **Fresh Debian/Ubuntu?** If `python3 -m venv .venv` fails with
> `ensurepip is not available`, install the venv/pip packages first:
> `sudo apt-get install -y python3-venv python3-pip`.

PDF rendering uses **WeasyPrint**, which needs a few native libraries — this is the
single most common setup snag. Install them for your OS:

- **Linux (Debian/Ubuntu):**

  ```bash
  sudo apt-get install -y python3-venv python3-pip \
    libpango-1.0-0 libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
  ```

- **macOS (Homebrew):**

  ```bash
  brew install pango gdk-pixbuf libffi
  ```

- **Windows:** use **WSL** and follow the Linux steps above — WeasyPrint's native
  deps are painful on bare Windows. See the
  [WeasyPrint install docs](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html)
  if you hit a missing-library error.

Then render any CV file:

```bash
python3 scripts/generate_cv.py cv/master.md
# → cv/master.pdf
```

The generator strips Obsidian syntax, warns on ATS violations (tables, images,
more than 5 bullets per role, bullets without metrics, more than 2 pages), and
renders selectable-text output with no headers or footers.

## From evidence to CV — a 60-second example

The system turns one logged win into a tailored CV line you can defend in an interview:

**1. Capture** a quantified bullet in `impacts/impact-library-acme.md`:

```text
- Cut p99 checkout latency 320ms → 90ms with read-through caching and by collapsing
  N+1 queries. [tags:: backend, performance] [company:: Acme] [category:: performance]
```

**2. Tailor** — the agent pulls it into `cv/versions/<role>.md`, reworded for the target JD:

```text
- Reduced checkout latency 72% (320ms → 90ms p99) via read-through caching and query optimization.
```

**3. Render** an ATS-safe PDF:

```bash
python3 scripts/generate_cv.py cv/versions/<role>.md
```

**4. Check** that your CV covers the job description's keywords:

```bash
python3 scripts/jd_gap.py jds/<role>.txt cv/versions/<role>.md
```

`jd_gap.py` flags any JD keywords your CV is missing, so you close real gaps before applying.

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
