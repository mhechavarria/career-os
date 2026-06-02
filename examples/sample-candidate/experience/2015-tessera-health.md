---
type: experience
company: Tessera Health
role: Backend Developer
team-type: onsite
start: 2015-07
end: 2017-07
status: complete
tags: [backend, java, spring-boot, postgresql, sql-server, rest, oauth, compliance]
---

# Tessera Health (2015 – 2017)

## Context

Tessera Health built clinical-records software for outpatient clinics. I worked on the
**backend services** that stored and exchanged patient records, with the compliance
constraints that come with health data. This is where I moved from embedded into
server-side product engineering, in Java and Spring Boot.

- **Team:** 7 engineers; I owned the records API and the data-migration work.
- **Scale:** records platform used across a few hundred clinic seats.
- **Role:** Backend Developer (IC).

## Tech Stack

- **Languages:** Java
- **Frameworks:** Spring Boot, Hibernate
- **Data:** SQL Server (legacy) → PostgreSQL (migration target)
- **APIs & Auth:** REST APIs, OAuth 2.0
- **Async:** RabbitMQ

## IC Impact Categories

### 1) Architecture

Led the migration of the records store from a single SQL Server instance to PostgreSQL,
introducing a repository abstraction so services could be cut over table-group by
table-group without a big-bang switch.

### 2) Reliability

Replaced nightly cron-driven report jobs with a RabbitMQ-backed queue so a slow or failed
report no longer blocked the next night's batch, and failures became individually retryable.

### 4) Automation

Built a data-validation harness that compared source and target rows during the database
migration, catching schema- and encoding-mismatch bugs before they reached production.

## Quantified Outcomes

- **Report generation time** — overnight batch cut from ~6 hours to ~90 minutes (-75%) after queueing.
- **Migration correctness** — automated row-level validation caught mismatches across 40+ tables pre-cutover.
- **Database migration** — SQL Server → PostgreSQL completed incrementally with no customer-visible downtime.

## CV-Ready Bullets

- Led an incremental SQL Server → PostgreSQL migration for a clinical records platform with zero customer-visible downtime, using a repository abstraction for table-group cutover.
- Cut overnight report-generation time 75% (6h → 90min) by replacing cron batches with a RabbitMQ-backed, individually retryable queue.
- Built a row-level data-validation harness that caught schema and encoding mismatches across 40+ tables before the production cutover.

## STAR Story Seeds

**Zero-downtime database migration**
**S:** A single aging SQL Server instance held all clinical records and was a scaling and
licensing bottleneck.
**T:** Move to PostgreSQL without downtime a clinic would notice or any data integrity risk.
**A:** Introduced a repository layer, dual-read/dual-write per table group, and an automated
row-comparison harness to verify every group before cutover.
**R:** Migrated 40+ tables incrementally with no customer-visible downtime and no data-loss incidents.
