---
name: tide-gauge
slug: tide-gauge
status: shipped
role: Creator / maintainer
stack: [Go, C, ESP32, LoRaWAN, PostgreSQL, Grafana]
links:
  repo: https://github.com/jordan-rivera-dev/tide-gauge
visibility: public
period: 2021–present
---

# tide-gauge — Coastal Water-Level IoT Logger

An open-source water-level monitor: a low-power ESP32 sensor node that reports over
LoRaWAN to a Go ingestion service, with PostgreSQL storage and Grafana dashboards.
Repo: [github.com/jordan-rivera-dev/tide-gauge](https://github.com/jordan-rivera-dev/tide-gauge).

## Outcomes

- Runs ~6 months on a single battery by duty-cycling the radio and deep-sleeping between reads.
- Deployed at 4 volunteer monitoring sites feeding a public Grafana dashboard.
- End-to-end stack — firmware, LoRaWAN uplink, Go ingest, storage, dashboards — in one repo.

## Context & Architecture

The node samples an ultrasonic distance sensor, timestamps the reading, and sends a compact
binary frame over LoRaWAN. A Go service consumes uplinks from the network server, decodes the
frame, writes to PostgreSQL, and exposes Prometheus metrics so the ingestion path is itself
observable. Grafana renders both the water-level series and the fleet health (battery, RSSI,
missed uplinks). The project is a tidy demonstration of the same embedded-to-cloud arc as my
day job, at hobby scale.
