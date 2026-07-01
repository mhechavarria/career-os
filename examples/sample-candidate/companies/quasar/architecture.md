---
type: company
company: Quasar
doc: architecture
status: interviewing
tags: [distributed-systems, event-sourcing, kafka, architecture]
---

# Quasar — Architecture

> **Optional deep-dive** for this staff distributed-systems role — it doubles as
> system-design prep. See [[research]] and [[interview-prep]].
> **Everything here is inferred from the JD** (no public source or docs in hand), so it's
> marked as such throughout. The value is rehearsing the design in *their* world before
> the room — not walking in claiming to know their internals.

## Primitives — what the product exposes

> _All inferred from the JD's "real-time risk platform / event-driven core."_

- **Event ingestion** — a high-throughput write path taking billions of events/day.
- **Risk decisioning** — the service that evaluates events against risk logic in real time.
- **Query / read APIs** — gRPC service contracts other teams build on _(confirmed via JD:
  "set standards for gRPC service contracts")_.

## Service Architecture (inferred)

> How one event likely flows end to end. Reasoned from the JD; confirm in the interview.

- Producers → **Apache Kafka** (the event log, partitioned by entity key for ordering) →
  stream consumers → **event store** (PostgreSQL) as the source of truth.
- **Projections** are built from the event log and rebuilt by replay — the JD names
  "event sourcing model and the projections built on top of it" _(confirmed via JD)_.
- The **risk-decision** service reads projections and serves decisions over **gRPC**.
- Runs on **Kubernetes** across **multiple AWS regions** for HA/DR _(confirmed via JD)_;
  the open question is the failover/replay mechanism (see below).

## Data + Infra

| Component | Role | Confirmed / inferred |
|---|---|---|
| Apache Kafka | Event log / backbone | Confirmed via JD |
| PostgreSQL | Event store + projections, under HA | Confirmed via JD |
| gRPC | Inter-service contracts, backward-compatible | Confirmed via JD |
| Kubernetes + Terraform + Helm + Ansible | Orchestration, IaC, config mgmt | Confirmed via JD |
| Multi-region AWS | High availability + disaster recovery | Confirmed via JD |
| Datadog / Prometheus / OpenTelemetry | Observability | Confirmed via JD |

## The Hard Problems Here

> My interview talking points — each tied to a real story from `impacts/` / `experience/`.

- **Exactly-once-ish ingestion + idempotency** at billions/day. → my Heliograph
  idempotent-writes-on-Kafka work (survived a 4x spike, zero data loss).
- **Rebuildable projections + schema evolution** — evolving the event sourcing model
  without corrupting downstream reads. → my Nimbus event-sourced lifecycle (projections
  rebuilt from the log).
- **Multi-region HA/DR** — failover, RTO/RPO, replay across regions. → my 3-region
  ingestion design; DR *targets* are a genuine open question and a growth edge for me.
- **Ordering / partitioning** under massive throughput — partition keys, hot partitions,
  backpressure. → my Kafka Streams scaling work at Coriolis (5k → 25k events/sec).
- **gRPC backward compatibility** — evolving contracts without breaking consumers.

## Open Questions

> Great interview material — and likely the design deep-dive itself.

- [ ] How is exactly-once (or effectively-once) achieved on ingest — idempotency keys,
  dedupe store, or transactional outbox?
- [ ] What's the projection-rebuild strategy at this scale — full replay, or snapshots?
- [ ] What are the multi-region DR targets (RTO/RPO), and how does failover actually work?
- [ ] What does Ansible own that Terraform + Helm don't?
- [ ] What's the partitioning key for the event log, and how are hot partitions handled?
