---
type: company
company: Quasar
doc: research
status: interviewing
tags: [distributed-systems, event-sourcing, kafka, staff, remote]
---

# Quasar — Company Research

> Research hub for the Quasar Staff Backend (Distributed Systems) opportunity.
> Companion docs: [[interview-prep]] · [[people]].
> _Last researched: 2026-06-02._

## Snapshot

- **What:** Real-time risk platform processing **billions of events per day** _(confirmed
  via JD)_. Hiring a **Staff Backend Engineer, Distributed Systems** to set technical
  direction for the event-driven core, event sourcing model, and high-availability story.
- **Stage / funding:** Not stated in the JD _(inferred: post-Series-A scale given
  "billions of events/day" and a dedicated staff hire — confirm with the recruiter)_.
- **Team size:** Not stated _(to confirm)_.
- **Role:** Hands-on staff — write code, lead system design, mentor. Remote _(confirmed
  via JD)_.

## Product / Business

- Real-time **risk** platform — the product _is_ the event-driven core: ingest billions of
  events/day, evaluate risk, keep it always-on _(confirmed via JD)_.
- The "why this company" angle: this is a distributed-systems problem as the core product,
  not a feature bolted onto a CRUD app — event sourcing and HA are the differentiators, and
  a staff hire owning them is treated as a first-class investment _(inferred from the JD's
  framing)_.

## Competitive Landscape

> Only the JD is in hand, so this is directional — confirm before leaning on it in the room.

| Competitor | Shape | Their edge vs. it |
|---|---|---|
| Incumbent fraud/risk suites | Managed, rules-first, batch-leaning _(inferred)_ | Real-time, event-sourced, replayable — lower decision latency |
| In-house risk teams | Build-your-own on cloud primitives _(inferred)_ | Platform + the distributed-systems depth already solved |

## Tech Stack (confirmed via JD)

- **Languages:** **Go** and **TypeScript** (JD asks fluency in both).
- **Messaging / core:** **Apache Kafka**, event-driven architecture, **event sourcing** with
  projections on top.
- **Datastores:** **PostgreSQL** under high-availability constraints.
- **Contracts:** **gRPC** service contracts with backward-compatibility standards.
- **Infra / deploy:** **Kubernetes**, **Terraform**, **Helm**, **Ansible** (config
  management), multi-region **AWS** for HA/DR.
- **Observability:** **Datadog**, **Prometheus**, **OpenTelemetry**.

## Why I Fit (honest)

- **Event-driven systems at scale = my current work.** At Heliograph I re-architected a Go
  ingestion pipeline onto a Kafka backbone with idempotent writes and backpressure, across 3
  AWS regions — Quasar's exact problem shape. _(Go + Kafka + multi-region: direct.)_
- **Event sourcing is a real thread, not a keyword.** At Nimbus Freight I designed an
  event-sourced shipment lifecycle on PostgreSQL with rebuildable projections — maps straight
  onto their "event sourcing model + projections."
- **Streaming depth.** Coriolis Kafka Streams pipeline scaled ingestion 5x on the same
  footprint — Kafka mastery beyond just producing/consuming.
- **Staff signals.** I authored the ADRs governing the Heliograph ingestion redesign and led
  the design review — matches their "author ADRs, lead design reviews" nice-to-have.
- **Gap — Ansible.** I run config-as-code with **Terraform + Helm + GitHub Actions**, but I
  have **not used Ansible in production**. Honest gap; the adjacent experience (declarative
  IaC, promotion pipelines across 3 EKS regions) transfers, and I'd ramp on Ansible fast — I
  won't claim it as owned. _(Also confirm Helm depth: I deploy on EKS but should be precise
  about how much of the Helm charting I authored vs. inherited.)_

## Open Questions

- [ ] Comp band for staff (remote, EU/US overlap)? — not public; ask the recruiter early.
- [ ] Senior vs. staff scope here — what distinguishes them on this team?
- [ ] DR specifics: what are the RTO/RPO targets for the multi-region story?
- [ ] On-call / incident model for the event-driven core?
- [ ] Why Ansible alongside Terraform + Helm — what does it own in their stack?

## Links

- JD: `jds/staff-distributed-systems.txt`
- Tailored CV: `cv/versions/staff-distributed-systems.md`
- Application: `applications/quasar-2026-06.md` _(create when you apply)_
- Site / careers: _to add_
