---
type: cv
variant: tailored
target: Lumen Cloud — Platform Engineer (Observability)
date: 2026-06-02
status: draft
---

# Jordan Rivera

jordan.rivera@example.com | +351 912 000 000 | Lisbon, Portugal (remote, EU/US overlap) | [linkedin.com/in/jordan-rivera-dev](https://linkedin.com/in/jordan-rivera-dev) | [github.com/jordan-rivera-dev](https://github.com/jordan-rivera-dev)

## Headline

Platform Engineer | Observability & Reliability | Prometheus · Grafana · OpenTelemetry · Datadog

## Summary

Platform engineer who treats observability as a product. Builds the metrics, tracing, and dashboards that let teams operate distributed systems confidently — Prometheus, Grafana, OpenTelemetry, and Datadog over Go services on Kubernetes, provisioned with Terraform. Equally comfortable cutting cost and latency by acting on what the traces reveal, and reducing on-call toil with automation.

## Skills

- **Observability:** Prometheus, Grafana, OpenTelemetry, Datadog, structured logging, SLOs
- **Languages:** Go, Python, TypeScript
- **Cloud / Infra:** AWS (EKS, Lambda, RDS), Kubernetes, Terraform, Docker, GitHub Actions
- **Distributed Systems:** Apache Kafka, event-driven architecture, microservices, gRPC
- **Data:** PostgreSQL, Redis

## Experience

### Heliograph — Senior Backend / Platform Engineer
Mar 2022 – Present | Go, AWS (EKS, Lambda, RDS, Bedrock), Kubernetes, Apache Kafka, Terraform, Datadog, Prometheus, Grafana, OpenTelemetry

- Instrumented 6 Go services with OpenTelemetry traces and Prometheus metrics behind Grafana and Datadog dashboards, making the ingestion path observable end to end across 3 AWS regions.
- Reduced RDS cost 28% per region by acting on redundant query patterns that OpenTelemetry tracing made visible.
- Built an AI incident-triage assistant on AWS Bedrock that correlates alerts, recent deploys, and Datadog metrics, cutting mean time to first diagnosis 55%.
- Authored the Terraform and GitHub Actions promotion pipeline deploying all 6 services identically across 3 Kubernetes regions.

### Nimbus Freight — Senior Backend Engineer
Jun 2019 – Feb 2022 | Python, Django, GCP (GKE, Pub/Sub, Cloud SQL), PostgreSQL, Celery, RabbitMQ, Redis

- Cut carrier-callback failures ~95% by replacing synchronous fan-out with an observable Celery/RabbitMQ worker fleet (retries, dead-letter queues, idempotency) with per-queue metrics.
- Cut routing compute cost 35% and halved p95 quote latency by precomputing and caching route costs.
- Built the GitLab CI and GKE pipeline with canary rollouts and health checks across a platform tracking 2M+ shipments.

### Coriolis Analytics — Software Engineer
Aug 2017 – May 2019 | Node.js, TypeScript, Apache Kafka, Kafka Streams, Elasticsearch, Redis, AWS (Lambda, ECS, DynamoDB), Docker

- Built a Kafka Streams pipeline that scaled real-time ingestion 5x (5k → 25k events/sec) on the same AWS footprint.
- Cut malformed-event dashboard stalls to 0 with dead-letter handling, replay tooling, and alerting on the dead-letter rate.

## Education

B.Sc. Computer Engineering — University of Lisbon, 2009–2013

## Certifications

- AWS Certified Solutions Architect – Associate (2021)
- Certified Kubernetes Administrator (CKA) (2022)

## Languages

- Portuguese — Native
- English — C2 Proficient
- Spanish — Professional working proficiency
