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

1. Move entries from `[Unreleased]` into a new `[X.Y.Z]` section in
   `CHANGELOG.md` (with the date) and commit.
2. Tag and push:

   ```bash
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```

3. The `release.yml` workflow publishes a GitHub Release from that version's
   changelog section.
