---
type: company
company: <% await tp.system.prompt("Company name") %>
doc: research
status: <% await tp.system.prompt("Status (researching/applied/interviewing/offer/closed)", "researching") %>
tags: []
---

# <% await tp.system.prompt("Company name") %> — Company Research

> The research hub for one company — the single row that shows in the pipeline
> dashboard. Companion docs: [[interview-prep]] · [[people]].
> _Last researched: <% tp.date.now("YYYY-MM-DD") %>._

## How to use this file

> Delete this block once you get the idea. Research is done when you can answer five
> questions in your own words — what they do, why it matters, the hard technical
> problem, why you fit, what you must ask — not when every section is full. Two
> disciplines run throughout: **separate confirmed facts from inferred ones and cite
> the source** (mark each `confirmed via JD/docs/source` or `inferred` — never list a
> stack you guessed as fact); and **stay honest in "Why I Fit"** — map real experience
> and name gaps with the adjacent work that covers them.

## Snapshot

> The 30-second version: what the company is, stage, size, and the role. Fill this from
> the JD and the company site first.
> _Example: "Dev-infra company, Series A (~40 people). Role: Senior Backend, remote EU."_

- **What:**
- **Stage / funding:**
- **Team size:**
- **Role:**

## Product / Business

> What do they sell, to whom, and how do they make money? What is the core product and
> the wedge that makes it work? This is where your "why this company" answer comes from.
> _Example: "Code-first integrations platform sold to developers; wedge = control plus
> raw API count vs. managed-schema competitors."_

-

## Competitive Landscape

> Who else plays here, and what is this company's edge? You don't need a full market
> map — enough to speak to where they win and the trade-off they own.
> _Example: "vs. a managed-schema competitor — they trade breadth for developer control."_

| Competitor | Shape | Their edge vs. it |
|---|---|---|
|  |  |  |

## Tech Stack (confirmed)

> What is verified vs. inferred? Cite where each fact came from and mark confidence.
> This maps directly onto likely interview topics.
> _Example: "TypeScript/Node monorepo (confirmed via public repo); Postgres + Redis
> (confirmed via docs); custom scheduler, migrated off Temporal (inferred from a blog)."_

- **Languages / runtime:**
- **Datastores:**
- **Infra / deploy:**

## Why I Fit (honest)

> Map your real experience to their problem — one line per angle, each tied to a
> documented impact. Then name the biggest gap openly and the adjacent experience that
> covers it. Do not inflate; "used/extended" is not "built/owned."
> _Example: "Integrations against messy third-party APIs = their core problem. Gap: no
> Go in production — closest is a large Node-to-TypeScript migration I owned end to end."_

-

## Open Questions

> What you still don't know that changes your decision or your prep — comp, level,
> on-call, equity, roadmap. Promote the important ones into `interview-prep`.
> _Example: "Comp band for this level? Senior vs. staff scope here? On-call model?"_

- [ ]

## Links

> The receipts — JD, tailored CV, application file, site, repo, careers page, and any
> funding or launch posts you cited above.

- JD: `jds/<slug>.txt`
- Tailored CV: `cv/versions/<slug>.md`
- Application: `applications/<company>-<role>-YYYY-MM.md`
- Site:
- Careers:
