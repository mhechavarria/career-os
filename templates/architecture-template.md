---
type: company
company: <% await tp.system.prompt("Company name") %>
doc: architecture
status: <% await tp.system.prompt("Status (researching/applied/interviewing/offer/closed)", "researching") %>
tags: []
---

# <% await tp.system.prompt("Company name") %> — Architecture

> **Optional** — worth it for senior/staff roles or source-available / deeply technical
> targets; skip it for a standard application. A technical deep-dive that doubles as
> system-design prep. See [[research]] and [[interview-prep]].
> Same discipline as everywhere: mark each fact `confirmed` (you read it in the docs or
> the source) or `inferred` (your best guess from the JD and product). An inferred
> architecture is still useful prep — just don't present a guess as fact in the room.

## Primitives — what the product exposes

> The building blocks a user or developer actually consumes. Naming them right is half of
> "do you understand what they build."
> _Example: "Auth, Proxy, and Functions — the three things their API gives you."_

-

## Service Architecture

> The main services and how one request or job flows end to end. If it's source-available,
> cite real paths; if not, reason from the product and mark it inferred.
> _Example: "request → API → scheduler (Postgres-as-queue) → runner → result store;
> scheduler is custom, not Temporal (confirmed via their blog)."_

-

## Data + Infra

> Datastores and what each is for, plus how it's deployed. This is where "PostgreSQL for
> X, Redis for Y" earns you credibility.
> _Example: "Postgres = control plane + task queue; Redis = cache + locks; ES = logs."_

| Component | Role | Confirmed / inferred |
|---|---|---|
|  |  |  |

## The Hard Problems Here

> The genuinely difficult engineering — and therefore your talking points and the likely
> design questions. Tie each to your own experience where you can.
> _Example: "A homegrown distributed scheduler (heartbeats, backpressure, exactly-once
> dequeue) — why build it vs. Temporal? Maps to my queue-ownership story."_

-

## Open Questions

> What you'd confirm in the code or ask in the interview — these make great questions and
> often become the design deep-dive itself.
> _Example: "How do they guarantee a task is dequeued once — a row lock, or SKIP LOCKED?"_

- [ ]
