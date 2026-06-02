---
type: cv
variant: master
date: 2026-06-02
status: draft
---

# Jordan Rivera

jordan.rivera@example.com | +351 912 000 000 | Lisbon, Portugal (remote, EU/US overlap) | [linkedin.com/in/jordan-rivera-dev](https://linkedin.com/in/jordan-rivera-dev) | [github.com/jordan-rivera-dev](https://github.com/jordan-rivera-dev)

## Summary

Senior backend engineer with over a decade building and operating distributed systems, from embedded firmware to cloud-native platforms. Specializes in event-driven services on Kubernetes and AWS — Go, Python, and TypeScript around Apache Kafka and PostgreSQL — with a strong observability and reliability practice. Recently shipped AI-augmented tooling that cut incident triage time by more than half. Seeking senior backend or platform roles on remote-first teams with real distributed-systems problems.

## Experience

### Heliograph — Senior Backend / Platform Engineer
Mar 2022 – Present | Go, AWS (EKS, Lambda, EventBridge, RDS, Bedrock), Kubernetes, Apache Kafka, Terraform, Datadog, OpenTelemetry, gRPC

- Re-architected a Go ingestion pipeline onto Apache Kafka with idempotent writes, cutting p99 write latency 40% and surviving a 4x traffic spike with zero data loss across 3 AWS regions.
- Built an AI incident-triage assistant using Anthropic Claude on AWS Bedrock that correlates alerts, deploys, and Datadog metrics, cutting mean time to first diagnosis 55%.
- Authored the Terraform and GitHub Actions promotion pipeline deploying 6 Go services identically across 3 EKS regions, removing all manual deploy steps.
- Reduced RDS cost 28% per region by eliminating redundant query patterns surfaced through OpenTelemetry tracing.

### Nimbus Freight — Senior Backend Engineer
Jun 2019 – Feb 2022 | Python, Django, GCP (GKE, Pub/Sub, Cloud SQL), PostgreSQL, Celery, RabbitMQ, Redis

- Designed an event-sourced shipment lifecycle on PostgreSQL handling 2M+ shipments/year with a full audit trail and rebuildable projections.
- Cut carrier-callback failures ~95% (from a weekly incident to near-zero) by replacing synchronous webhook fan-out with a Celery/RabbitMQ worker fleet using retries, dead-letter queues, and idempotency.
- Cut routing compute cost 35% and halved p95 quote latency by precomputing and caching route costs instead of computing them per request.
- Built the GitLab CI and GKE pipeline that replaced manual deploys with one-click canary rollouts across a platform tracking 2M+ shipments.

### Coriolis Analytics — Software Engineer
Aug 2017 – May 2019 | Node.js, TypeScript, Apache Kafka, Kafka Streams, Elasticsearch, Redis, AWS (Lambda, ECS, DynamoDB), Docker

- Built a Kafka Streams pipeline in TypeScript that scaled real-time analytics ingestion 5x (5k → 25k events/sec) on the same AWS ECS footprint.
- Designed the event ingestion API and Elasticsearch query layer powering sub-2-second funnels and retention dashboards.
- Cut malformed-event-driven dashboard stalls to 0 after bad SDK releases by adding dead-letter handling and replay tooling.

### Tessera Health — Backend Developer
Jul 2015 – Jul 2017 | Java, Spring Boot, SQL Server, PostgreSQL, REST APIs, OAuth 2.0, RabbitMQ

- Led an incremental SQL Server to PostgreSQL migration for a clinical records platform with zero downtime, cutting over 40+ tables table-group by table-group.
- Cut overnight report-generation time 75% (6h to 90min) by replacing cron batches with a RabbitMQ-backed, retryable queue.

### Vela Robotics — Embedded Software Engineer
Sep 2013 – Jun 2015 | C, C++, Python, MQTT, Modbus, AWS IoT Core, Linux

- Built the first end-to-end telemetry pipeline (MQTT to Python ingest to AWS IoT Core) for a 30-robot fleet, delivering real-time fleet-health visibility.
- Automated firmware flashing and verification over UART, cutting per-robot programming to a single 2-minute step.

## Skills

- **Languages:** Go, Python, TypeScript, Java, C, C++
- **Cloud — AWS:** EKS, Lambda, EventBridge, RDS, S3, API Gateway, Bedrock
- **Cloud — GCP:** GKE, Pub/Sub, Cloud SQL
- **Infrastructure / IaC:** Terraform, Docker, Kubernetes, GitHub Actions, GitLab CI
- **Messaging & Data:** Apache Kafka, Kafka Streams, RabbitMQ, PostgreSQL, Redis, Elasticsearch
- **Architecture:** Distributed systems, event-driven architecture, microservices, gRPC, REST APIs
- **Observability:** Datadog, Prometheus, Grafana, OpenTelemetry
- **AI-Augmented:** AWS Bedrock, Anthropic Claude, prompt engineering

## Education

B.Sc. Computer Engineering — University of Lisbon, 2009–2013

## Certifications

- AWS Certified Solutions Architect – Associate (2021)
- Certified Kubernetes Administrator (CKA) (2022)

## Languages

- Portuguese — Native
- English — C2 Proficient
- Spanish — Professional working proficiency
