---
type: cv
variant: tailored
target: Orbital Systems — Senior Go Backend Engineer
date: 2026-06-02
status: draft
---

# Jordan Rivera

jordan.rivera@example.com | +351 912 000 000 | Lisbon, Portugal (remote, EU/US overlap) | [linkedin.com/in/jordan-rivera-dev](https://linkedin.com/in/jordan-rivera-dev) | [github.com/jordan-rivera-dev](https://github.com/jordan-rivera-dev)

## Headline

Senior Go Backend Engineer | Distributed Systems on Kubernetes & AWS | Kafka · gRPC · Terraform

## Summary

Senior backend engineer specializing in high-throughput Go services on Kubernetes and AWS. Designs event-driven systems around Apache Kafka, gRPC, and PostgreSQL, provisioned with Terraform and instrumented with OpenTelemetry and Datadog. Comfortable owning a service from API contract through CI/CD to on-call, and recently built AI-augmented tooling that cut incident triage time by more than half.

## Skills

- **Languages:** Go, Python, TypeScript
- **Cloud / Infra:** AWS (EKS, Lambda, EventBridge, RDS), Kubernetes, Terraform, Docker, infrastructure as code
- **CI/CD:** GitHub Actions, Docker, CI/CD pipelines
- **Distributed Systems:** Apache Kafka, Kafka Streams, gRPC, event-driven architecture, microservices, REST APIs
- **Data:** PostgreSQL, Redis, Elasticsearch
- **Observability:** Datadog, Prometheus, Grafana, OpenTelemetry, distributed tracing, structured logging

## Experience

### Heliograph — Senior Backend / Platform Engineer
Mar 2022 – Present | Go, AWS (EKS, Lambda, EventBridge, RDS, Bedrock), Kubernetes, Apache Kafka, gRPC, Terraform, Datadog, OpenTelemetry

- Re-architected a Go ingestion pipeline onto Apache Kafka with idempotent writes and gRPC internal APIs, cutting p99 write latency 40% and surviving a 4x traffic spike with zero data loss across 3 AWS regions.
- Authored the Terraform and GitHub Actions promotion pipeline deploying 6 Go services identically across 3 EKS regions, removing all manual deploy steps.
- Built an AI incident-triage assistant using Anthropic Claude on AWS Bedrock that correlates alerts, deploys, and Datadog metrics, cutting mean time to first diagnosis 55%.
- Reduced RDS cost 28% per region by eliminating redundant query patterns surfaced through OpenTelemetry tracing.

### Nimbus Freight — Senior Backend Engineer
Jun 2019 – Feb 2022 | Python, Django, GCP (GKE, Pub/Sub, Cloud SQL), PostgreSQL, Celery, RabbitMQ, Redis

- Designed an event-sourced shipment lifecycle on PostgreSQL handling 2M+ shipments/year with a full audit trail and rebuildable projections.
- Cut carrier-callback failures ~95% by replacing synchronous webhook fan-out with a Celery/RabbitMQ worker fleet using retries, dead-letter queues, and idempotency.
- Built the GitLab CI and Kubernetes (GKE) pipeline that replaced manual deploys with one-click canary rollouts across a platform tracking 2M+ shipments.

### Coriolis Analytics — Software Engineer
Aug 2017 – May 2019 | Node.js, TypeScript, Apache Kafka, Kafka Streams, Elasticsearch, Redis, AWS (Lambda, ECS, DynamoDB), Docker

- Built a Kafka Streams pipeline in TypeScript that scaled real-time ingestion 5x (5k → 25k events/sec) on the same AWS ECS footprint.
- Designed the event ingestion API and Elasticsearch query layer powering sub-2-second dashboards.
- Cut malformed-event-driven dashboard stalls to 0 by adding dead-letter handling and replay tooling.

## Education

B.Sc. Computer Engineering — University of Lisbon, 2009–2013

## Certifications

- AWS Certified Solutions Architect – Associate (2021)
- Certified Kubernetes Administrator (CKA) (2022)

## Languages

- Portuguese — Native
- English — C2 Proficient
- Spanish — Professional working proficiency
