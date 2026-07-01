---
type: company
company: Quasar
doc: interview-prep
status: interviewing
tags: [distributed-systems, event-sourcing, kafka, staff]
---

# Quasar — Interview Prep

> See [[research]] for company intel and [[people]] for interviewers. Read [[people]]
> **first**: the highest-value move is to reorder which STAR story I lead with to match the
> interviewer's background — here, a known ex-SRE interviewer means the reliability story
> leads, not the greenfield Kafka re-architecture.

## Process

> Public info is thin for this role, so this is the typical staff shape — confirm with the
> recruiter on the first call.

- Likely: recruiter screen → system-design round → a coding/past-project deep-dive →
  leadership/behavioral. _(Inferred from a standard staff loop; verify.)_
- The **system-design round is the bar** for a staff distributed-systems hire — plan to lead
  it, not just answer it.

## Recruiter / First Call

- **Level this maps to:** Confirm staff vs. senior — the JD says staff; make sure the comp
  and scope match that.
- **Comp band (ask early):** Not public. Get the range before investing in deep prep.
- **Logistics:** Remote; confirm timezone overlap (I'm Lisbon, EU/US overlap works), process
  length, and eligibility.
- **My one-line pitch:** "I build event-driven systems at scale for a living — Kafka
  backbone, idempotent writes, multi-region — which is Quasar's core problem, and I've owned
  the ADRs for that kind of redesign."

## Likely Themes (from the JD)

- Event-driven design at scale (billions of events/day).
- Event sourcing + projections, and how you evolve them safely.
- High availability and disaster recovery across multiple AWS regions.
- Kafka mastery; PostgreSQL data modelling under HA constraints.
- gRPC contracts and backward compatibility.
- Staff leadership: ADRs, design reviews, mentoring, setting standards.

## STAR Stories to Lead With

> Each is an already-documented impact (`impacts/`, `experience/`) mapped to a theme —
> one vivid detail, the mechanism named, a Quasar-tied punchline. Selection, not invention.

- **Event-driven at scale →** Heliograph Kafka re-architecture → **the one detail:** it took
  a **4x traffic spike with zero data loss** because writes were idempotent and the consumers
  were built for backpressure. Punchline: "that's the property Quasar's risk core lives or
  dies on."
- **Event sourcing →** Nimbus event-sourced shipment lifecycle on PostgreSQL → **the detail:**
  projections were **rebuildable from the log**, so a bad projection was a replay, not an
  incident. Directly their "event sourcing model + projections."
- **Reliability / idempotency →** Nimbus webhook fan-out moved to a worker fleet with a **DLQ
  and idempotency keys** → callback failures went from **weekly incidents to near-zero**.
  _(Lead with this one if the interviewer is ex-SRE — see [[people]].)_
- **Kafka depth →** Coriolis Kafka Streams pipeline **scaled 5x (5k → 25k events/sec)** on the
  same footprint → Kafka mastery beyond produce/consume.
- **Staff / AI-augmented →** authored the **ADRs** for the ingestion redesign; built an
  AWS Bedrock incident-triage assistant that cut **mean time to first diagnosis 55%** →
  direction-setting plus modern tooling judgment.

## System-Design Prep (staff — lead this)

> Prep the one design their product implies, on their actual stack (from [[research]]).

- **Design Quasar's event-sourced risk core at billions/day.** Cover: the event log
  (Kafka partitioning + ordering), the event store + **rebuildable projections** (PostgreSQL),
  **idempotency** and exactly-once-ish semantics, **multi-region HA/DR** (failover, RTO/RPO,
  replay), backpressure, **gRPC contracts + backward compatibility**, and observability
  (Datadog/Prometheus/OTel).
- Map every choice onto their stack so the design lives in their world, not a generic one.

## Take-Home / Work-Trial Prep

- Unknown for a staff role — likely a live system-design deep-dive or an architecture review
  rather than a take-home. Confirm on the first call; if there is a take-home, timebox it and
  show judgment (tests + a short README on trade-offs), don't gold-plate.

## Questions to Ask Them

- [ ] What are the RTO/RPO targets for the multi-region DR story today — and where does it
  fall short?
- [ ] What does "set technical direction" mean in practice for this staff role?
- [ ] Why Ansible alongside Terraform + Helm — what does each own?
- [ ] Biggest scaling or reliability challenge in the event-driven core right now?
- [ ] Senior vs. staff expectations and comp on this team?

## Prep Checklist

- [ ] Confirm date, timezone, and format
- [ ] Re-read the JD; map each "what you'll do" bullet to one story above
- [ ] Rehearse the event-sourced-risk-core design out loud
- [ ] Read [[people]]; reorder STAR leads to the confirmed interviewer
- [ ] Prepare the honest Ansible-gap answer (Terraform/Helm adjacent, would ramp fast)
