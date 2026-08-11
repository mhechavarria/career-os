# Upgrading Career OS

Career OS is a **template, not a dependency**. When you click *Use this template*,
GitHub hands you a repository with its own history and no link back to this one, so
there is no `git pull` that brings a new version in. That is by design: your
instance holds your career, and nothing upstream should ever be able to rewrite it.

Upgrading is therefore a deliberate copy of the framework files you actually want.
It is usually small. The v1.6.0 → v1.7.0 release, for example, changed eight files
and **none of them held user data**.

## The one rule

**Never merge this template into your instance.**

Your repository and this one have unrelated histories, so git refuses outright:

```console
$ git pull
There is no tracking information for the current branch.

$ git merge v1.7.0
fatal: refusing to merge unrelated histories
```

The tempting next step is the destructive one. Forcing it turns every file that
exists in both repositories into an add/add conflict — including files the release
never touched:

```console
$ git merge v1.7.0 --allow-unrelated-histories
CONFLICT (add/add): Merge conflict in cv/master.md
CONFLICT (add/add): Merge conflict in lessons.md
...
Automatic merge failed; fix conflicts and then commit the result.
```

Your master CV and your accumulated lessons are now conflicted against a release
that changed neither. Copy files instead.

## What is yours and what is the framework

| Path | Who owns it |
| --- | --- |
| `profile/` · `experience/` · `impacts/` · `cv/` · `applications/` · `jds/` · `companies/` · `sources/` · `lessons.md` | **Yours.** Never take an upstream version. |
| `scripts/` · `templates/` · `tests/` · `examples/` · `flywheel/` · `maintainers/` · `.github/` · `ruff.toml` · `requirements.txt` · `requirements-dev.txt` | Framework. Safe to take wholesale. |
| `AGENT.md` · `README.md` · `CHANGELOG.md` | Framework, but commonly customized. Diff before taking. |

## The procedure

### 1. Find out what actually changed

Read the [release notes](https://github.com/mhechavarria/career-os/releases) or
[`CHANGELOG.md`](CHANGELOG.md). Every entry names the paths it touches, so you can
decide what is worth taking before you copy anything.

### 2. Add this repository as a remote, once

```bash
git remote add template https://github.com/mhechavarria/career-os.git
git fetch template --tags
```

The remote is read-only in practice: you will never merge or pull from it, only
read files out of it. With the tags fetched you can see the exact delta between
the version you started from and the one you want:

```bash
git diff --stat v1.6.0 v1.7.0
```

### 3. Copy only the framework paths you want

`git archive` writes a tree straight into your working directory without touching
git history, which is exactly the semantics you want here:

```bash
git archive v1.7.0 flywheel | tar -x
```

Pass any framework path from the table above. Take one directory at a time and
review the diff before committing:

```bash
git status
git diff
git add flywheel && git commit -m "chore: update flywheel to career-os v1.7.0"
```

### 4. Re-install the flywheel skill, if you use it

**This is the step that is easy to miss.** The flywheel skill is *installed* by
copying it into `.claude/skills/save-memory/`, and `.claude/` is gitignored.
Updating the tracked `flywheel/` directory therefore does **not** update the copy
your agent actually loads — it silently keeps running the old one:

```console
$ wc -l flywheel/skills/save-memory/SKILL.md .claude/skills/save-memory/SKILL.md
  102 flywheel/skills/save-memory/SKILL.md          # what you just updated
   49 .claude/skills/save-memory/SKILL.md           # what the agent loads
```

Re-copy it after every flywheel update:

```bash
cp flywheel/skills/save-memory/SKILL.md .claude/skills/save-memory/
```

If the release also changed `flywheel/check_memory.sh` or `flywheel/hooks/pre-push`,
re-install those into your memory directory too, and re-apply `chmod +x` — see
[`flywheel/README.md`](flywheel/README.md). Git does not run a hook that is not
executable, and it will only tell you in a hint you are likely to scroll past.

### 5. Confirm your own files are untouched

An upgrade that changed one of your files did something wrong. Check before and
after:

```bash
sha256sum cv/master.md lessons.md profile/*.md
```

## Upgrading to v1.7.0

The whole release is framework-only. For a typical instance, one command plus the
skill re-install covers it:

```bash
git fetch template --tags
git archive v1.7.0 flywheel | tar -x
cp flywheel/skills/save-memory/SKILL.md .claude/skills/save-memory/   # if installed
```

That brings the `save-memory` index-discipline rules and the optional durability
tier (`check_memory.sh` and the `pre-push` hook). The remaining changes —
`.github/workflows/ci.yml`, `ruff.toml`, `requirements-dev.txt` — pin the lint and
test toolchain and only matter if you kept this repository's CI. If you did, take
`ruff.toml` and `requirements-dev.txt` together: pinning one without the other
leaves the same trap they were pinned to close.

## If you customized a framework file

Diff it against both versions before deciding, so you can see whether upstream
touched the same lines you did:

```bash
git diff v1.6.0 -- AGENT.md    # your changes since you started
git diff v1.6.0 v1.7.0 -- AGENT.md    # what upstream changed
```

If the two do not overlap, take the upstream version and re-apply your edit. If
they do, merge by hand. Keeping a short note of your framework edits in
`lessons.md` makes every future upgrade cheaper.
