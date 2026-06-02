---
name: promql-lab
slug: promql-lab
status: shipped
role: Creator / maintainer
stack: [Prometheus, Grafana, Docker, Go]
links:
  repo: https://github.com/jordan-rivera-dev/promql-lab
visibility: public
period: 2022–present
---

# promql-lab — Observability Teaching Sandbox

A one-command Docker Compose stack — Prometheus, Grafana, and a set of sample exporters
emitting realistic metrics — plus a tutorial series that teaches PromQL from first
principles. Repo:
[github.com/jordan-rivera-dev/promql-lab](https://github.com/jordan-rivera-dev/promql-lab).

## Outcomes

- `docker compose up` brings up a full Prometheus + Grafana environment with live sample data.
- A 6-part tutorial taking readers from `rate()` and histograms to alerting rules and SLOs.
- Adopted as pre-reading for an internal on-call onboarding rotation.

## Context & Architecture

A small Go exporter generates plausible request-rate, latency-histogram, and error metrics so
learners can write meaningful PromQL against data that behaves like a real service. Prometheus
scrapes the exporter; Grafana ships with pre-built dashboards and a folder of example queries.
The tutorial pairs each PromQL concept with a dashboard panel and an alerting rule, so the
reader leaves able to instrument and alert on a service rather than just recite functions.
