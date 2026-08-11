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

### The changelog-completeness guard

Phase 1 refuses to cut a release when a PR squash-merged since the last tag is
never mentioned in `[Unreleased]`:

```text
error: merged since v1.6.0 but absent from [Unreleased]: #37, #39
  The release notes are generated from that section, so whatever is
  missing from it ships invisible. Add an entry for each (dependabot
  PRs included — they never write their own), or re-run with
  --allow-missing-entries to cut the release without them.
```

It reads the PR numbers off the squash-merge subjects (`git log v<latest>..HEAD`,
where GitHub appends `(#N)`) and looks for each one anywhere in the `[Unreleased]`
body, so a single bullet closing several PRs — `(#9, #10)` — credits both. A
commit with no `(#N)` suffix, such as a direct push or the release commit itself,
carries no number and is not checked.

This lives in the script rather than in a CI job on purpose. A CI check can only
demand a `CHANGELOG.md` edit from a human author, so **dependabot** would have to
be exempted and its bumps would keep slipping through — and a required changelog
check would turn a fresh fork's first PR red for no reason. Checking at the cut
catches every merged PR, costs a forker nothing, and matches what this script is
for: a bad release fails on your machine, not after the tag is public.

Add the entry rather than reaching for the flag. `--allow-missing-entries` exists
so the omission is deliberate and visible, not so it becomes routine.

It **never pushes** and **never creates the GitHub Release** — `release.yml`
publishes that from the CHANGELOG when the tag is pushed. See
[CONTRIBUTING.md](../CONTRIBUTING.md#releasing-maintainers) for the full flow.
