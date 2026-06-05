# Contributing to Career OS

Thanks for your interest in improving Career OS! This repository is the
**framework** — scripts, templates, and the `AGENT.md` intake guide. Your own
filled-in career data lives in *your* copy, never here.

## Ways to contribute

- Improve the `AGENT.md` intake flow or the templates.
- Fix or extend the scripts (`generate_cv.py`, `jd_gap.py`, ...).
- Improve the documentation.
- Report bugs or request features via [issues](../../issues).

## Development setup

```bash
pip install -r requirements-dev.txt
```

On Linux, WeasyPrint needs system libraries for PDF rendering:

```bash
sudo apt-get install -y libpango-1.0-0 libpangocairo-1.0-0 \
  libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
```

## Branch strategy

This project uses a simple trunk-based / GitHub Flow model:

- `main` is always releasable and protected.
- Do work on short-lived branches off `main`, named by type:
  `feat/...`, `fix/...`, `docs/...`, `chore/...`.
- External contributors: fork, branch, then open a PR against `main`.
- PRs are **squash-merged** to keep history linear.
- No direct pushes to `main`.

## Before opening a PR

Run the same checks CI runs:

```bash
ruff check scripts/ tests/
ruff format --check scripts/ tests/
pytest
pymarkdown --config .pymarkdown.json scan .
python3 scripts/generate_cv.py cv/master.md   # must render with no ATS warnings
```

Then:

- Add a `CHANGELOG.md` entry under `[Unreleased]` for any user-facing change.
- Never commit personal data, secrets, or generated PDFs (`*.pdf` is git-ignored).

## Commit messages

Conventional-Commit prefixes (`feat:`, `fix:`, `docs:`, `chore:`) are encouraged
for a readable history, but not enforced.

## Versioning

This project follows [Semantic Versioning](https://semver.org). For a template
repo that means:

- **MAJOR** — a breaking change to the file schema, the `AGENT.md` phase
  structure, or a script's CLI (existing users would have to migrate).
- **MINOR** — a new backward-compatible capability (new script, template, or phase).
- **PATCH** — fixes, documentation, and small tweaks.

## Releasing (maintainers)

[`maintainers/prepare_release.py`](maintainers/README.md) does the CHANGELOG
surgery and runs the release guards locally. Because the repo squash-merges,
releasing has **two phases**: the release commit goes in via a PR, and the tag
is created on `main` only *after* that PR merges (a tag made on the branch would
point at a soon-to-be-squashed commit, which `release.yml` rejects).

**Phase 1 — on a release branch**, rewrite the CHANGELOG and commit:

```bash
git switch -c release/vX.Y.Z origin/main
python3 maintainers/prepare_release.py --bump minor --commit
git push -u origin release/vX.Y.Z
```

Use `--bump major|minor|patch` (computed from the latest tag) or `--version X.Y.Z`;
drop `--commit` to only rewrite the CHANGELOG and review the diff first. The script
moves `[Unreleased]` into a dated `[X.Y.Z]` section, refreshes the compare links,
and refuses to proceed on a dirty tree, a duplicate/older version, or an empty
`[Unreleased]`. Open a PR and squash-merge it.

**Phase 2 — once merged, from an up-to-date `main`**, tag and push:

```bash
git switch main && git pull
python3 maintainers/prepare_release.py --version X.Y.Z --tag
git push origin vX.Y.Z
```

The `--tag` step only runs on a clean `main` whose CHANGELOG already carries the
`[X.Y.Z]` section. The `release.yml` workflow then publishes the GitHub Release
from that section — **do not** create the Release in the GitHub UI yourself.
