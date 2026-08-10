---
name: save-memory
description: Review the current session and persist everything worth keeping into this repo's auto-memory (user / feedback / project / reference), updating existing entries and the MEMORY.md index. Run before ending a session or clearing/compacting context. Trigger on "/save-memory", "save memory", "update memory before we close", "checkpoint memory".
---

# Save Memory

Before this session's context is lost, durably capture what a future session would need. Update the auto-memory for **the repo this session is running in** (your Career OS clone).

**Memory directory:** the auto-memory directory for the **current** project. Your session context (the harness "Memory" instructions) names the exact absolute path — use that. If you ever need to derive it yourself, it is:
`~/.claude/projects/<current-working-directory with every "/" replaced by "-">/memory/`
and `MEMORY.md` inside that directory is the index.

## Procedure

1. **Read the current index and existing memories.** Read `MEMORY.md` and skim the existing memory files so you know what already exists and avoid duplicates.

2. **Scan this session for anything worth persisting.** Walk the conversation and pull out items that will matter in a future session, sorted into the four types:
   - **user** — new facts about who the user is, their role, preferences, expertise, goals.
   - **feedback** — corrections AND confirmations about how to work. Lead with the rule, then `**Why:**` and `**How to apply:**`. Capture successes ("yes, that was right") not just corrections.
   - **project** — decisions, plans, status, who/why/by-when. Lead with the fact, then `**Why:**` and `**How to apply:**`. Convert relative dates to absolute (today is in the env context).
   - **reference** — pointers to external systems (where X is tracked/found).

3. **Decide: update vs. create vs. delete.**
   - Prefer **updating** an existing memory over writing a new one.
   - **Correct or remove** anything this session proved stale or wrong.
   - **Do NOT save**: ephemeral task state, anything derivable from current code / `git log`, fix recipes already in the commit, or content already in `AGENT.md`. If the user explicitly asks to save such a thing, save only what was *surprising or non-obvious* about it.

4. **Write each memory** as its own file with this frontmatter, then add/refresh its one-line pointer in `MEMORY.md`.

   **Index discipline (hard rules):**
   - An index line is a HOOK, not a changelog: hard cap **160 chars**, one line, no frontmatter in the index.
   - When updating an existing entry, **rewrite its index line from scratch** to state only the *current* status + at most one next action. **Never append** new facts, dates, or status to an existing line.
   - Any fact you are tempted to put in the index goes into the **body first** (dated); the index line only points to it.

   **Archive sweep (index budget gate — checked every save):**
   - Run `wc -c MEMORY.md` and classify: **green** `< 16,000` (report only), **amber**
     `16,000–19,999` (run an archive sweep before this save reports done; if the sweep finds
     nothing eligible, say so and report done anyway — amber never blocks on its own), **red**
     `>= 20,000` (this save may not report clean until the index is under `12,000` bytes, or
     the user explicitly waives the sweep). The sweep trigger is bytes only — the index's line
     count is reported, never a trigger. The 160-char per-line cap above is a separate hard gate.
     These bands measure the auto-loaded context budget, not the store's total size — the same
     numbers apply to every session, and they are meant to be edited locally if your harness's
     context budget differs.
   - **Archive eligibility**: a memory moves to `<memory-dir>/archive/` (move it — use `git mv` if
     your memory dir is a git repo, never delete) plus a rewritten hook line in
     `<memory-dir>/ARCHIVE.md` only when it is `project_*` **and** terminal
     (REJECTED/CLOSED/PASSED/SHIPPED/DONE/EXECUTED) **and** actionless (no next action, no future
     date). FROZEN/PARKED/PAUSED/DEFERRED entries and any entry carrying a future date stay
     active. `user_*`/`feedback_*`/`reference_*` never archive — they are standing, not episodic.
     Nothing is ever deleted; a wrong archive is one move back plus a fresh `MEMORY.md` line.
     `archive/` and `ARCHIVE.md` are created on first use.
   - Before finishing, verify: `grep '^- \[' MEMORY.md | awk 'length($0)>160'` prints **nothing**
     and the byte band above is satisfied — run the sweep if amber/red (the facts are already in
     bodies) before reporting done.

   **File name:** `<type>_<kebab-case-slug>.md`, using the same four types as the
   frontmatter (`user_`, `feedback_`, `project_`, `reference_`). That prefix is what the
   archive-eligibility rules above key on, so a memory saved without it can never be
   swept and the byte gate can never be cleared. The `name:` field below stays the **bare
   slug with no prefix** — it is what `[[links]]` resolve to, so prefixing it would break
   every link.

   File format:
   ```markdown
   ---
   name: {{kebab-case-slug}}
   description: {{specific one-line summary}}
   metadata:
     type: {{user | feedback | project | reference}}
   ---

   {{body — for feedback/project use the rule/fact + **Why:** + **How to apply:** structure. Link related memories with [[their-slug]].}}
   ```

5. **Keep it coherent.** Link related memories with `[[slug]]`. Keep `name`/`description`/`type` in sync with the body. Don't leave duplicate or contradicting entries.

6. **Feed the flywheel — promote durable lessons.** Auto-memory is session-to-session momentum, but it is Claude-Code-specific. When a `feedback` or `project` memory captures a **durable, generalized job-search lesson** (a no-go pattern, what predicted an outcome, a comp or triage rule that will recur), also promote the generalized form into `lessons.md` (Phase 9 of `AGENT.md`). That store is editor-agnostic and is what Phases 7.0 / 7 / 8 read back — so a lesson written there sharpens every future run, not just Claude Code sessions.

7. **Back up the store, if it is one.** Check that the memory directory is a repository **root**:
   `git -C <memory-dir> rev-parse --show-toplevel` must succeed *and* print `<memory-dir>` itself,
   **ignoring a trailing slash**. Strip any trailing `/` from both sides before comparing:
   `--show-toplevel` never emits one, and a memory directory is very often written with it, so a
   literal comparison reports a mismatch on a setup that is in fact correct. Use `--show-toplevel`,
   not `--git-dir`: `--git-dir` also succeeds when the memory directory merely sits somewhere
   inside an unrelated repository — a dotfiles repo rooted at `$HOME`, say — and the commands
   below would then stage your memory into that repo. If the check fails or the normalized paths
   differ, the memory directory is not its own git repo: this step performs no action and prints
   nothing at all, not even a suggestion to set one up. If it matches, print the exact commands to
   run and stop; never run them yourself:
   ```bash
   git -C <memory-dir> add <changed files>
   git -C <memory-dir> commit -m "<conventional commit message>"
   git -C <memory-dir> push origin <branch>
   ```

8. **Report** a concise summary: which files were created, updated, or removed, and the index changes. No need to dump file contents.

## Scope notes
- Only touch the **current** repo's memory dir (the one named in your session context) — never another project's memory.
- This skill is for cross-session persistence. For in-session step tracking use tasks; for implementation alignment use a plan — not memory.
