# Companies — Research & Interview Prep

One subfolder per company you're researching, applying to, or interviewing with:
`companies/<slug>/`. Each folder is just markdown you stamp from the templates in
[`../templates/`](../templates/) — there's no script here. A company folder is prose
and judgment, not computation.

## The conventional docs

- **`research.md`** — the company hub: product, business, funding, tech stack,
  why-I-fit, open questions, links. **This is the one row that shows in the pipeline
  dashboard** (`applications/pipeline.md`), so keep its `status` current.
- **`interview-prep.md`** — likely themes, the STAR stories to lead with, system-design
  prep, questions to ask, and a prep checklist.
- **`people.md`** — founders, team, interviewers, and warm-intro paths.

Add any other doc a company needs, with the same frontmatter:

- **`architecture.md`** — a technical deep-dive. Optional; recommended for senior/staff
  or source-available/deeply technical targets, skippable otherwise.
- **`comp.md`**, **`take-home.md`**, … — comp and negotiation notes, take-home intel,
  or anything else worth keeping.

## How to research well

The value of a company folder is the judgment in it, not the folder itself. Five
principles keep it worth the time:

1. **Separate confirmed from inferred.** Mark every fact as verified or a guess.
2. **Cite the source.** Note where each fact came from — JD, docs, source code,
   Glassdoor — so you can weigh it and defend it.
3. **Research until you can answer five questions** — what they do, why it matters, the
   hard technical problem, why you fit, and what you must ask — not until every section
   is full.
4. **Name gaps honestly.** In "Why I Fit," map real experience and call out the biggest
   gap with the adjacent work that covers it. A stretched claim costs you the interview,
   not the screen.
5. **Treat this folder as sensitive** — it holds interviewer names and comp figures.
   See the privacy note below.

## Frontmatter

```yaml
---
type: company
company: <Name>
doc: research | interview-prep | people   # or any custom doc name
status: researching | applied | interviewing | offer | closed
tags: []
---
```

## How it ties into the pipeline

The dashboard (`applications/pipeline.md`) lists **one row per company** by querying
`type = "company" AND doc = "research"`, so keep the company-level `status` current on
`research.md`. Link each doc to its application file (`applications/<slug>-YYYY-MM.md`)
and JD (`jds/<slug>.txt`) so Obsidian backlinks close the loop from research →
application → CV.

## Privacy

Company research can hold sensitive notes — interviewer names, comp figures, process
intel. **This folder's contents are gitignored by default** (only this README and a
`.gitkeep` are tracked). Un-ignore your own company folders only in a **private** fork;
never commit real names or numbers to a public one.
