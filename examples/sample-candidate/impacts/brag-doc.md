---
type: brag-doc
year: 2026
---

# Brag Doc — 2026 (Heliograph)

> Ongoing quarterly achievement log for the current role. Capture work as it happens;
> promote the best entries into `impact-library-heliograph.md` and the CV.

## Q1

- **Initiative:** Kafka ingestion re-architecture, region rollout.
- **Context:** The Go monolith wrote telemetry straight to Postgres; spikes and downstream
  outages caused dropped records.
- **Actions:** Introduced a Kafka backbone, stateless consumers, idempotent writes, and
  per-consumer backpressure; rolled out region by region behind a traffic-shadowing flag.
- **Outcome / Metrics:** p99 write latency 210ms → 125ms (-40%); survived a 4x heatwave spike
  with zero data loss.
- **Evidence:** Datadog APM dashboards; rollout ADR; incident-free spike postmortem.
- **Reusable bullet draft:** Re-architected a Go ingestion pipeline onto Apache Kafka, cutting
  p99 write latency 40% and surviving a 4x spike with zero data loss.

## Q2

- **Initiative:** AI incident-triage assistant (Bedrock + Claude).
- **Context:** On-call spent 20+ minutes per incident manually correlating alerts, deploys,
  and dashboards before forming a hypothesis.
- **Actions:** Built a Bedrock workflow that gathers the alert, deploy history, Datadog metrics,
  and runbooks, then posts a ranked, advisory hypothesis to the incident channel.
- **Outcome / Metrics:** Mean time to first diagnosis ~22 min → ~10 min (-55%) over the quarter.
- **Evidence:** Incident timeline comparisons; on-call survey.
- **Reusable bullet draft:** Built an AI incident-triage assistant with Claude on AWS Bedrock,
  cutting mean time to first diagnosis 55%.

## Q3

- **Initiative:** RDS cost reduction.
- **Context:** RDS spend was climbing faster than traffic across all 3 regions.
- **Actions:** Right-sized instances and removed redundant query patterns found via
  OpenTelemetry traces; added per-query cost dashboards.
- **Outcome / Metrics:** RDS cost down 28% per region with no latency regression.
- **Evidence:** AWS Cost Explorer; OpenTelemetry trace analysis.
- **Reusable bullet draft:** Reduced RDS cost 28% per region by right-sizing and eliminating
  redundant queries surfaced through tracing.

## Q4

- **Initiative:** (in flight) Multi-region failover game-days.
- **Context:** Failover between regions has never been exercised under load.
- **Actions:** Designing chaos game-days and the runbook automation to support them.
- **Outcome / Metrics:** TBD — target is a documented, rehearsed regional failover under 10 min.
- **Evidence:** TBD.
- **Reusable bullet draft:** TBD.
