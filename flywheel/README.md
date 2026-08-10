# The Judgment Flywheel — full-momentum upgrade (Claude Code)

Career OS ships a **retro loop** out of the box: Phase 9 captures a short retro on every terminal
outcome, and recurring lessons graduate into `lessons.md`, which Phases 7.0 / 7 / 8 read back so each
run starts sharper. That loop works in **any** AI editor with zero setup — it is the universal
default, and nothing here replaces it.

This folder is an **optional upgrade for [Claude Code](https://claude.com/claude-code) users** that
adds *momentum* to that loop: a persistent, per-project **memory** the agent carries between sessions,
plus a `save-memory` skill that captures what each session learned before the context is lost. Where
`lessons.md` compounds *job-search judgment*, this compounds *everything else a returning session needs
to know* — who you are, how you like to work, what's in flight — so you stop re-explaining it every
time.

> **Other editors (Cursor, etc.): stay on `lessons.md`.** The memory store and skill below rely on the
> Claude Code harness, so this upgrade is Claude-Code-only by design. You lose nothing by skipping it —
> the retro loop is fully functional on its own.

## What the memory holds

The agent's memory lives in your Claude Code memory directory (outside the repo, so nothing sensitive
is ever committed) as a `MEMORY.md` index plus one small file per fact, sorted into four types:

- **user** — who you are: role, seniority, preferences, goals.
- **feedback** — how you like the agent to work (corrections *and* confirmed wins).
- **project** — what's in flight: an active search, a decision, a deadline (with dates).
- **reference** — where things live: a tracker, a doc, an external system.

Durable, generalized *job-search lessons* still belong in `lessons.md` (Phase 9) — the `save-memory`
skill reminds the agent to promote them there so they stay editor-agnostic.

## Set up the flywheel

In a Claude Code session opened on your Career OS clone, just say:

> **Set up the flywheel.**

The agent will follow the runbook below. There is no script to run — the steps are plain file
operations Claude Code performs for you.

### Runbook (the agent performs these)

**Install the `save-memory` skill.**

1. **Check for a global copy first.** If `~/.claude/skills/save-memory/` already exists, **do not**
   copy — report "`save-memory` is already available globally, skipping the project copy" and point
   the user at `flywheel/skills/save-memory/SKILL.md` in case they want to diff this Career OS version
   against their global one (it adds a `lessons.md` promotion step they may not have).
2. **Otherwise install it into the repo.** Copy `flywheel/skills/save-memory/` →
   `.claude/skills/save-memory/`. `.claude/` is gitignored, so the installed copy stays local and is
   never committed.
3. **Confirm.** Tell the user they can now run `/save-memory` (or "save memory") before compacting or
   ending a session, and that the harness auto-loads the `MEMORY.md` index at the start of every
   session so the agent already knows what memories exist.

That is the whole default install: **one skill.** The harness already auto-creates the memory
directory and auto-loads its `MEMORY.md` index natively, so there is nothing else to wire for the loop
to start turning — you run `/save-memory`, memory accumulates, and every future session opens with the
index in context.

## Advanced (optional): the index-first manifest hook

Once your memory has grown to *many* files, you may want the session to open with a compact **manifest**
— each memory's filename, size, and last-modified date — on top of the auto-loaded index, so drift
between a hand-edited `MEMORY.md` and what's actually on disk is visible at a glance. This is a
convenience, **not** required: the harness already loads the index, and `save-memory` keeps it in sync.

It is deliberately **out of the default runbook** because it edits your live Claude Code settings.
Only add it if you want it, and only by hand-merging (never blind-overwriting) into
`.claude/settings.local.json`:

- If the file exists, **read it, preserve every existing key**, and add one `SessionStart` hook entry.
  If it is malformed or held open by a live session, **stop and report** — do not overwrite it.
- Set `D` to the **absolute path your session's `# Memory` context names** (do not hand-derive the
  slug). The hook emits the **manifest only** — filenames, dates, sizes — and **never** the file
  bodies (catting every body into context overflows it; that is why bodies are read on demand):

```bash
D="<the absolute memory dir your session's # Memory context names>"
if [ -d "$D" ]; then
  echo "=== auto-memory index (bodies Read on demand) ==="
  echo "MEMORY.md (index) is in context above. Read the specific <name>.md from $D before acting on that topic. Manifest — file | modified | bytes:"
  for f in "$D"/*.md; do
    b=$(basename "$f"); [ "$b" = "MEMORY.md" ] && continue
    printf '  %s | %s | %s\n' "$b" "$(date -r "$f" +%Y-%m-%d)" "$(wc -c < "$f")"
  done
fi
```

As a `SessionStart` command hook it looks like:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "D=\"<your memory dir>\"; if [ -d \"$D\" ]; then echo \"=== auto-memory index (bodies Read on demand) ===\"; echo \"MEMORY.md (index) is in context above. Read the specific <name>.md from $D before acting on that topic. Manifest — file | modified | bytes:\"; for f in \"$D\"/*.md; do b=$(basename \"$f\"); [ \"$b\" = \"MEMORY.md\" ] && continue; printf '  %s | %s | %s\\n' \"$b\" \"$(date -r \"$f\" +%Y-%m-%d)\" \"$(wc -c < \"$f\")\"; done; fi",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

**Restart the session** to activate the hook.

## Advanced (optional): a durable, checked memory store

The default install above keeps your memory local to this one machine. If you want a real
backup — so a lost laptop does not erase everything the flywheel accumulated — you can turn the
memory directory into its own git repo with an integrity gate on top. This is a second, separate
opt-in layer; skip it if the manifest hook above is enough for you.

**Create the remote private, before anything else.** Your memory holds personal facts,
corrections, and in-flight decisions, so before you run `git init` anywhere, create the remote
repo (GitHub, GitLab, etc.) and set its visibility to **private**.

**One recommended shape: a separate git repo, outside your Career OS clone.** Do not nest it
inside this repository or any other project's checkout.

1. **Use the harness-reported path.** Your session's `# Memory` context names the exact absolute
   path to the current project's memory directory — use that path verbatim. A hand-derived slug
   strands the repo at the old location if the project's path is later moved or renamed; the
   harness-reported path does not have that problem.
2. **Initialize it as its own repo** at that path, then point it at your private remote:

   ```bash
   git -C <the memory dir your session's # Memory context names> init
   git -C <memory dir> remote add origin <your private remote URL>
   ```

3. **Copy the integrity check and hook** from this repo into the memory dir, then re-mark them
   executable (Windows, and some archivers, drop the exec bit on copy):

   ```bash
   cp flywheel/check_memory.sh <memory dir>/check_memory.sh
   mkdir -p <memory dir>/.git/hooks
   cp flywheel/hooks/pre-push <memory dir>/.git/hooks/pre-push
   chmod +x <memory dir>/check_memory.sh <memory dir>/.git/hooks/pre-push
   ```

4. From here on, `save-memory`'s step 7 reminds you to commit and push whenever the memory
   directory is a git repo — it never runs the commit or the push itself.

### What the check catches

`check_memory.sh` runs five read-only checks against the memory directory: the index-file size
band, the 160-char per-line cap, whether every memory body has an index line pointing at it,
whether every index link resolves to a **tracked** file, and whether frontmatter matches the
documented file format. The `pre-push` hook runs it before anything leaves the machine and
blocks the push on any `FAIL`. The escape hatch is `git push --no-verify`.

Here is one real failure, from an index line pointing at a body that was written but never
`git add`ed. This is the failure a new adopter is most likely to hit, because it is invisible on
the machine where it happens and only breaks for whoever clones the repo next:

```text
memory check: /home/you/.claude-memory/career-os
  ok    index 108 bytes [GREEN]
  ok    all 1 bodies resolve to an index line
  FAIL  index link(s) whose body is NOT tracked by git — a clone would see a dangling link:
          project-example.md  (git add "project-example.md")
  ok    frontmatter readable in all 1 bodies

MEMORY CHECK FAILED — 1 problem(s), 0 warning(s)
Fix, or push anyway with:  git push --no-verify
```

**Known limit, stated plainly.** `check_memory.sh` validates the **working tree**, not `HEAD`. A
body file that is staged but not yet committed passes this check locally while still being
absent from the tree you actually push. Checking `HEAD` instead would close that gap, but it
would also fire on every ordinary edit cycle — saving a memory before committing it — and a gate
that is noisy in the common case gets bypassed with `--no-verify` instead of fixed. The gate is
not airtight; it catches the failure mode above, not every possible one.

## What this never does

- Never commits or pushes anything itself — it only writes into the **gitignored** `.claude/`
  directory, the external Claude Code memory directory, and, if you opt into the durability tier
  above, `<memory-dir>/.git/hooks/`, still outside this repo. The `save-memory` step 7 above only
  *reminds* you to commit and push; it never runs either command.
- Never overwrites existing memory or existing settings — installs are additive and idempotent
  (re-running the runbook no-ops on the skill and re-reports the global-skip).
