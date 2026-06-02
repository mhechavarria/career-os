---
type: cv
variant: tailored
target: Quasar — Staff Backend Engineer, Distributed Systems
date: 2026-06-02
status: draft
---

# Jordan Rivera

jordan.rivera@example.com | +351 912 000 000 | Lisbon, Portugal (remote, EU/US overlap) | [linkedin.com/in/jordan-rivera-dev](https://linkedin.com/in/jordan-rivera-dev) | [github.com/jordan-rivera-dev](https://github.com/jordan-rivera-dev)

## Headline

Staff-level Backend Engineer | Distributed Systems & Event-Driven Architecture | Kafka · PostgreSQL · Kubernetes

## Summary

Backend engineer operating at staff scope: designing event-driven, highly available systems and the platform they run on. Deep experience with Apache Kafka, event sourcing, and PostgreSQL under real production load, plus the system-design judgment to make durability, idempotency, and backpressure trade-offs explicit. Sets technical direction through ADRs and design reviews while still shipping the hard parts.

## Skills

- **Languages:** Go, Python, TypeScript, Java
- **Distributed Systems:** Apache Kafka, Kafka Streams, event-driven architecture, event sourcing, high availability, system design
- **Cloud / Infra:** AWS (EKS, Lambda, EventBridge, RDS), GCP (GKE), Kubernetes, Terraform, Docker
- **Data:** PostgreSQL, Redis, Elasticsearch, gRPC, REST APIs
- **Observability:** Datadog, Prometheus, Grafana, OpenTelemetry

## Experience

### Heliograph — Senior Backend / Platform Engineer
Mar 2022 – Present | Go, AWS (EKS, Lambda, EventBridge, RDS, Bedrock), Kubernetes, Apache Kafka, gRPC, Terraform, Datadog, OpenTelemetry

- Re-architected a Go ingestion pipeline onto an Apache Kafka backbone with stateless consumers and idempotent writes, designing for backpressure and surviving a 4x spike with zero data loss across 3 AWS regions.
- Cut p99 write latency 40% and reduced RDS cost 28% per region through targeted system-design and query changes surfaced via OpenTelemetry.
- Built an AI incident-triage assistant on AWS Bedrock that correlates alerts, deploys, and Datadog metrics, cutting mean time to first diagnosis 55%.
- Authored Terraform and GitHub Actions delivery for 6 services across 3 EKS regions and the ADRs governing the ingestion redesign.

### Nimbus Freight — Senior Backend Engineer
Jun 2019 – Feb 2022 | Python, Django, GCP (GKE, Pub/Sub, Cloud SQL), PostgreSQL, Celery, RabbitMQ, Redis

- Designed an event-sourced shipment lifecycle on PostgreSQL handling 2M+ shipments/year, giving the business a full audit trail and rebuildable projections.
- Cut carrier-callback failures ~95% by moving from synchronous webhook fan-out to a Celery/RabbitMQ worker fleet with retries, dead-letter queues, and idempotency.
- Cut routing compute cost 35% and halved p95 quote latency via precomputation and caching.

### Coriolis Analytics — Software Engineer
Aug 2017 – May 2019 | Node.js, TypeScript, Apache Kafka, Kafka Streams, Elasticsearch, Redis, AWS (Lambda, ECS, DynamoDB), Docker

- Built a Kafka Streams pipeline that scaled real-time ingestion 5x (5k → 25k events/sec) on the same AWS footprint.
- Added dead-letter handling and replay tooling that cut malformed-event dashboard stalls to 0 after bad releases.

## Education

B.Sc. Computer Engineering — University of Lisbon, 2009–2013

## Certifications

- AWS Certified Solutions Architect – Associate (2021)
- Certified Kubernetes Administrator (CKA) (2022)

## Languages

- Portuguese — Native
- English — C2 Proficient
- Spanish — Professional working proficiency
