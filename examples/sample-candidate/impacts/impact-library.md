---
type: impact-library
---

# Impact Library

> Aggregate index of CV-ready bullets across all roles. Each company has its own file
> with the full set; the strongest bullets are surfaced here by impact type.
>
> **Bullet format:** `Verb + what you did + measurable outcome`
> Every bullet must: (1) start with a past-tense action verb, (2) contain a number or
> scale metric, (3) answer "so what?" for a hiring manager.

## Architecture & System Design

- Re-architected a Go ingestion pipeline onto Apache Kafka with idempotent writes, cutting p99 write latency 40% and surviving a 4x traffic spike with zero data loss. [company:: Heliograph]
- Designed an event-sourced shipment lifecycle on PostgreSQL handling 2M+ shipments/year with a full audit trail and rebuildable projections. [company:: Nimbus Freight]

## Reliability & Resilience

- Replaced synchronous webhook fan-out with a Celery/RabbitMQ worker fleet (retries, DLQ, idempotency), taking carrier-callback failures from weekly incidents to near-zero. [company:: Nimbus Freight]
- Added dead-letter handling and replay tooling that contained malformed-event blast radius, ending stream-wide dashboard stalls. [company:: Coriolis Analytics]

## Performance & Scalability

- Built a Kafka Streams pipeline that scaled real-time ingestion 5x (5k → 25k events/sec) on the same AWS ECS footprint. [company:: Coriolis Analytics]
- Cut overnight report-generation time 75% (6h → 90min) by replacing cron batches with a retryable queue. [company:: Tessera Health]

## Automation & Developer Experience

- Authored Terraform and a GitHub Actions promotion pipeline deploying 6 Go services identically across 3 EKS regions, removing all manual deploy steps. [company:: Heliograph]
- Automated motor-controller firmware flashing over UART, cutting per-robot programming to a single ~2-minute step. [company:: Vela Robotics]

## Cross-Layer Impact

- Built the first end-to-end telemetry pipeline (MQTT → Python ingest → AWS IoT Core) for a ~30-robot fleet. [company:: Vela Robotics]

## AI-Augmented Engineering

- Built an incident-triage assistant using Anthropic Claude on AWS Bedrock that correlates alerts, deploys, and Datadog metrics, cutting mean time to first diagnosis 55%. [company:: Heliograph]

## Cost Optimization

- Reduced RDS cost 28% per region by right-sizing and eliminating redundant queries surfaced through OpenTelemetry tracing. [company:: Heliograph]
- Cut routing compute cost 35% by precomputing and caching route costs instead of computing them per request. [company:: Nimbus Freight]

## Company Libraries

- [Heliograph (2022–Present)](impact-library-heliograph.md)
- [Nimbus Freight (2019–2022)](impact-library-nimbus-freight.md)
- [Coriolis Analytics (2017–2019)](impact-library-coriolis-analytics.md)
- [Tessera Health (2015–2017)](impact-library-tessera-health.md)
- [Vela Robotics (2013–2015)](impact-library-vela-robotics.md)
