---
type: experience
company: Nimbus Freight
role: Senior Backend Engineer
team-type: remote
start: 2019-06
end: 2022-02
status: complete
tags: [backend, python, django, gcp, kubernetes, postgresql, celery, rabbitmq, event-sourcing]
---

# Nimbus Freight (2019 – 2022)

## Context

Nimbus Freight ran a logistics platform that brokered and tracked freight shipments
between shippers and carriers. I owned the **shipment lifecycle services** — the
state machine that tracks a shipment from quote to delivery — built in Python/Django
on GCP, and grew from Backend Engineer to Senior over the role.

- **Team:** 8 engineers across two squads; I led the shipment-platform squad's backend.
- **Scale:** 2M+ shipments tracked per year; asynchronous worker fleet processing events.
- **Role:** Backend Engineer → Senior Backend Engineer (IC, informal squad lead).

## Tech Stack

- **Languages:** Python (Django, asyncio tooling)
- **Cloud:** GCP — GKE, Pub/Sub, Cloud SQL (PostgreSQL), Cloud Storage
- **Infrastructure:** Kubernetes (GKE), Docker, GitLab CI
- **Async & Data:** Celery, RabbitMQ, PostgreSQL, Redis
- **APIs:** REST APIs (Django REST Framework)

## IC Impact Categories

### 1) Architecture

Modelled the shipment lifecycle as an event-sourced state machine — every transition
an immutable event — which gave the business a full audit trail and let us rebuild
projections (ETA, billing, carrier scorecards) without touching the source of truth.

### 2) Reliability

Replaced a brittle synchronous webhook fan-out with a Celery + RabbitMQ worker fleet
with retries, dead-letter queues, and idempotency keys, taking carrier-callback failures
from a weekly incident to a non-event.

### 3) Performance

Rewrote the route-cost computation from per-request synchronous calls to a cached,
batch-precomputed model, cutting quote latency and reducing routing compute cost 35%.

### 4) Automation

Built the GitLab CI pipeline and Kubernetes manifests that took deploys from a manual,
SSH-based ritual to one-click, with automated migrations and canary rollout on GKE.

## Quantified Outcomes

- **Carrier-callback failures** — from a weekly incident to effectively zero via DLQ + retries.
- **Quote latency** — p95 cut roughly in half by precomputing route costs instead of per-request.
- **Routing compute cost** — reduced 35% through caching and batch precomputation.
- **Shipments tracked** — scaled the platform to 2M+ shipments/year on the same service footprint.

## CV-Ready Bullets

- Designed an event-sourced shipment lifecycle on PostgreSQL handling 2M+ shipments/year, giving the business a full audit trail and rebuildable projections.
- Replaced synchronous webhook fan-out with a Celery/RabbitMQ worker fleet (retries, dead-letter queues, idempotency), taking carrier-callback failures from weekly incidents to near-zero.
- Cut routing compute cost 35% and halved p95 quote latency by precomputing and caching route costs instead of computing them per request.
- Built the GitLab CI and GKE deployment pipeline that replaced manual SSH deploys with one-click canary rollouts and automated migrations.

## STAR Story Seeds

**Event sourcing the shipment lifecycle**
**S:** Shipment state lived in mutable rows; billing disputes and "why did this status change?"
questions were impossible to answer reliably.
**T:** Make every state change auditable and let us derive new views without risky backfills.
**A:** Re-modelled the lifecycle as an append-only event log with projections for ETA, billing,
and carrier scorecards, migrated incrementally behind a dual-write.
**R:** Full audit trail; new projections shipped without touching the source of truth; supported
2M+ shipments/year.
