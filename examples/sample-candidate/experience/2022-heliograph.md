---
type: experience
company: Heliograph
role: Senior Backend / Platform Engineer
team-type: remote
start: 2022-03
end: present
status: active
tags: [backend, platform, go, aws, kubernetes, kafka, terraform, observability, ai-augmented, reliability]
---

# Heliograph (2022 – Present)

## Context

Heliograph is a climate-data SaaS that ingests telemetry from environmental sensors
(weather stations, soil probes, air-quality monitors) and turns it into APIs and
dashboards for agriculture and insurance customers. I sit on the **platform team** that
owns the ingestion pipeline and the shared service infrastructure: Go microservices on
EKS across 3 AWS regions, a Kafka backbone, and the Terraform that provisions all of it.

- **Team:** 6 engineers + 1 EM; I am one of two senior ICs on the platform team.
- **Scale:** 50,000+ active sensors, ~120k events/second at peak, 3 AWS regions.
- **Role:** Senior Backend / Platform Engineer (IC), owning ingestion + observability.

## Tech Stack

- **Languages:** Go (primary), Python (tooling, data jobs)
- **Cloud:** AWS — EKS, Lambda, EventBridge, RDS (PostgreSQL), S3, API Gateway, Bedrock
- **Infrastructure:** Kubernetes, Terraform, Docker, GitHub Actions
- **Messaging & Data:** Apache Kafka, PostgreSQL, Redis
- **APIs:** gRPC (internal), REST (public)
- **Observability:** Datadog, Prometheus, Grafana, OpenTelemetry

## IC Impact Categories

### 1) Architecture

Re-architected the ingestion path from a single Go monolith writing straight to Postgres
into a Kafka-fronted pipeline with stateless consumers, decoupling ingest from
persistence and giving us a durable buffer for traffic spikes and downstream outages.

### 2) Reliability

Introduced per-consumer backpressure and idempotent writes keyed on sensor + timestamp,
eliminating a recurring class of duplicate-record incidents and surviving a 4x traffic
spike during a regional heatwave with zero data loss.

### 3) Performance

Profiled and tuned the hot ingestion path (batched writes, connection pooling, protobuf
encoding) to cut p99 write latency from 210ms to 125ms while raising sustained throughput.

### 4) Automation

Wrote the Terraform modules and a GitHub Actions promotion pipeline that deploy the
platform identically across all 3 regions, replacing a partly manual, drift-prone process.

### 6) AI-Augmented Engineering

Built an incident-triage assistant using Anthropic Claude via AWS Bedrock: it reads the
firing alert, correlates recent deploys and Datadog metrics, searches the runbooks, and
posts a ranked hypothesis to the incident channel — cutting mean time to first diagnosis
by 55% across the first quarter of use.

## Quantified Outcomes

- **p99 ingestion write latency** — 210ms → 125ms (-40%); evidence: Datadog APM dashboards.
- **Mean time to first diagnosis** — ~22 min → ~10 min (-55%) after the triage assistant shipped.
- **Peak sustained throughput** — survived a 4x spike (30k → 120k events/sec) with zero data loss.
- **RDS cost** — reduced 28% per region by right-sizing instances and cutting redundant queries.
- **Deploy footprint** — 3 regions provisioned from one Terraform codebase, 0 manual steps.

## CV-Ready Bullets

- Re-architected a Go ingestion pipeline onto Apache Kafka, cutting p99 write latency 40% and surviving a 4x traffic spike with zero data loss across 3 AWS regions.
- Built an AI incident-triage assistant with Anthropic Claude on AWS Bedrock that correlates alerts, deploys, and Datadog metrics — cutting mean time to first diagnosis 55%.
- Authored the Terraform and GitHub Actions promotion pipeline deploying 6 Go services identically across 3 EKS regions, removing all manual deploy steps.
- Reduced RDS cost 28% per region by right-sizing instances and eliminating redundant query patterns surfaced through OpenTelemetry tracing.

## STAR Story Seeds

**Kafka re-architecture**
**S:** A Go monolith wrote sensor telemetry straight to Postgres; a downstream outage or a
traffic spike caused dropped records and cascading write timeouts.
**T:** Decouple ingest from persistence and make the pipeline spike- and outage-tolerant.
**A:** Introduced a Kafka backbone, stateless consumers, idempotent writes, and per-consumer
backpressure; rolled out region by region behind a traffic-shadowing flag.
**R:** Survived a 4x heatwave spike with zero data loss; p99 write latency down 40%.

**Incident-triage assistant**
**S:** On-call engineers spent the first 20+ minutes of every incident manually correlating
alerts, recent deploys, and dashboards before forming a hypothesis.
**T:** Cut the time to a credible first diagnosis without removing human judgment.
**A:** Built a Bedrock + Claude workflow that gathers the alert, deploy history, Datadog
metrics, and runbooks, then posts a ranked hypothesis as an advisory comment.
**R:** Mean time to first diagnosis fell 55%; the assistant is advisory only, so humans
still own the call.
