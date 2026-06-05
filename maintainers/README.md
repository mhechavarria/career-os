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

```bash
# rewrite CHANGELOG.md for the next minor version, print the git steps:
python3 maintainers/prepare_release.py --bump minor

# or name the version explicitly:
python3 maintainers/prepare_release.py --version 1.4.0

# also make the release commit (and optionally the tag); neither pushes:
python3 maintainers/prepare_release.py --bump minor --commit
python3 maintainers/prepare_release.py --bump minor --commit --tag
```

It **never pushes** and **never creates the GitHub Release** — `release.yml`
publishes that from the CHANGELOG when the tag is pushed. See
[CONTRIBUTING.md](../CONTRIBUTING.md#releasing-maintainers) for the full flow.
