---
type: experience
company: Coriolis Analytics
role: Software Engineer
team-type: hybrid
start: 2017-08
end: 2019-05
status: complete
tags: [backend, nodejs, typescript, kafka, streaming, elasticsearch, aws, redis, docker]
---

# Coriolis Analytics (2017 – 2019)

## Context

Coriolis was an early-stage product-analytics startup: customers embedded an SDK and we
ingested clickstream events, then served real-time funnels and retention reports. I was
an early backend hire and built much of the **event ingestion and stream-processing**
layer in Node.js/TypeScript on AWS.

- **Team:** 5 engineers (seed-stage); I owned ingestion and the streaming pipeline.
- **Scale:** grew sustained ingest from ~5k to ~25k events/second over the role.
- **Role:** Software Engineer (IC) — backend, with a real-time data focus.

## Tech Stack

- **Languages:** Node.js, TypeScript
- **Cloud:** AWS — Lambda, ECS, DynamoDB, API Gateway, S3
- **Streaming & Data:** Apache Kafka, Kafka Streams, Elasticsearch, Redis
- **Infrastructure:** Docker, CloudFormation, GitHub Actions

## IC Impact Categories

### 1) Architecture

Built the ingestion API and a set of Kafka Streams processors that turned a raw event
firehose into per-customer funnels and retention aggregates, with Elasticsearch as the
query layer for the dashboards.

### 3) Performance

Introduced batching, payload validation at the edge, and partition-aware consumers that
let the same ECS footprint absorb a 5x growth in event volume without re-architecture.

### 2) Reliability

Added a dead-letter path and replay tooling for malformed events, so a single bad SDK
release stopped being able to poison the stream and stall every customer's dashboards.

## Quantified Outcomes

- **Sustained ingest throughput** — scaled ~5k → ~25k events/second (5x) on the same ECS footprint.
- **Dashboard freshness** — real-time aggregates available within ~2 seconds of an event.
- **Bad-event blast radius** — contained to a replayable dead-letter queue instead of a full stall.

## CV-Ready Bullets

- Built a Kafka Streams pipeline in TypeScript that scaled real-time analytics ingestion 5x (5k → 25k events/sec) on the same AWS ECS footprint.
- Designed the event ingestion API and Elasticsearch query layer powering sub-2-second funnels and retention dashboards for early-stage customers.
- Added dead-letter handling and replay tooling that contained malformed-event blast radius, ending stream-wide dashboard stalls from bad SDK releases.

## STAR Story Seeds

**Scaling ingestion 5x without a rewrite**
**S:** A growing customer base pushed event volume up fast; the naive consumer design was
falling behind and dashboards lagged.
**T:** Absorb several times the traffic without a ground-up rewrite or a bigger bill.
**A:** Moved to partition-aware Kafka consumers, batched writes, and edge-side validation,
and load-tested each change against a replayed production stream.
**R:** Sustained 25k events/sec (5x) on the same footprint with sub-2-second dashboard freshness.
