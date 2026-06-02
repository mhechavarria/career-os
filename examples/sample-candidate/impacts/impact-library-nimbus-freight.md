---
company: Nimbus Freight
period: 2019–2022
type: impact-library
tags: [backend, python, django, gcp, kubernetes, postgresql, event-sourcing, reliability]
---

# Impact Library — Nimbus Freight

> Backend Engineer → Senior (2019 – 2022). Logistics / freight-tracking platform.

## Top Bullets

- Designed an event-sourced shipment lifecycle on PostgreSQL handling 2M+ shipments/year, giving the business a full audit trail and rebuildable projections. [tags:: architecture, event-sourcing, postgresql] [company:: Nimbus Freight] [category:: technical-depth]
- Replaced synchronous webhook fan-out with a Celery/RabbitMQ worker fleet (retries, dead-letter queues, idempotency), taking carrier-callback failures from weekly incidents to near-zero. [tags:: reliability, async, rabbitmq] [company:: Nimbus Freight] [category:: reliability]
- Cut routing compute cost 35% and halved p95 quote latency by precomputing and caching route costs instead of computing them per request. [tags:: performance, cost, redis] [company:: Nimbus Freight] [category:: cost-optimization]
- Built the GitLab CI and GKE deployment pipeline that replaced manual SSH deploys with one-click canary rollouts and automated migrations. [tags:: automation, cicd, kubernetes] [company:: Nimbus Freight] [category:: automation]
