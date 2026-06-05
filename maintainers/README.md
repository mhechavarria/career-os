# Maintainer tooling

Scripts in this directory are for **maintaining the Career OS project itself** —
cutting releases, repo chores. They are not part of the career-intake workflow
and you never need them to build your own CV. (The user-facing toolchain lives
in [`scripts/`](../scripts/).)

## `prepare_release.py`

Finalizes a release locally so a bad cut fails on your machine instead of after
a tag is already pushed. It mirrors the guards in
[`.github/workflows/release.yml`](../.github/workflows/release.yml) and performs
the CHANGELOG surgery (move `[Unreleased]` into a dated `[X.Y.Z]` section and
refresh the compare links).

Because this repo squash-merges, releasing is **two phases** — the branch commit
gets a new SHA when the PR lands, so the tag can only be created afterwards on
`main` (or `release.yml` would reject it as not an ancestor of `main`):

```bash
# phase 1 — on a release branch: rewrite CHANGELOG.md and make the commit
python3 maintainers/prepare_release.py --bump minor --commit

#   ...push the branch, open a PR, and squash-merge it...

# phase 2 — on an up-to-date main: tag the merged release commit
python3 maintainers/prepare_release.py --version 1.4.0 --tag
git push origin v1.4.0
```

Use `--bump major|minor|patch` or `--version X.Y.Z`. Run with neither `--commit`
nor `--tag` to only rewrite `CHANGELOG.md` and review the diff first. `--commit`
and `--tag` are mutually exclusive (they are different phases).

It **never pushes** and **never creates the GitHub Release** — `release.yml`
publishes that from the CHANGELOG when the tag is pushed. See
[CONTRIBUTING.md](../CONTRIBUTING.md#releasing-maintainers) for the full flow.
