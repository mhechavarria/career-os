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

4. **Write each memory** as its own file with this frontmatter, then add/refresh its one-line pointer in `MEMORY.md` (index lines stay under ~150 chars, no frontmatter in the index):
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

7. **Report** a concise summary: which files were created, updated, or removed, and the index changes. No need to dump file contents.

## Scope notes
- Only touch the **current** repo's memory dir (the one named in your session context) — never another project's memory.
- This skill is for cross-session persistence. For in-session step tracking use tasks; for implementation alignment use a plan — not memory.
