---
type: experience
company: Vela Robotics
role: Embedded Software Engineer
team-type: onsite
start: 2013-09
end: 2015-06
status: complete
tags: [embedded, c, cpp, python, mqtt, modbus, iot, firmware, linux]
---

# Vela Robotics (2013 – 2015)

## Context

Vela Robotics built autonomous shuttles for warehouse fulfilment. As my first job out of
university I wrote **firmware and device tooling** in C/C++ and Python, and built the first
pipeline that pulled robot telemetry off the floor and into the cloud.

- **Team:** 4 engineers (early-stage hardware startup); I owned firmware tooling + telemetry.
- **Scale:** a fleet of ~30 robots across two pilot warehouses.
- **Role:** Embedded Software Engineer (IC).

## Tech Stack

- **Languages:** C, C++ (firmware), Python (tooling, telemetry service)
- **Protocols:** MQTT, Modbus, TCP/IP, UART
- **Platform:** Linux, microcontrollers, AWS IoT Core (early adoption)

## IC Impact Categories

### 4) Automation

Built a Python tool that flashed and verified motor-controller firmware over UART in one
step, replacing a fiddly manual procedure and letting non-firmware staff re-flash robots.

### 5) Cross-Layer Impact

Stood up the first telemetry pipeline end to end — MQTT on the robot, an ingest service in
Python, and AWS IoT Core in the cloud — giving the team real visibility into fleet health
for the first time.

### 3) Performance

Reworked the firmware flashing and self-test sequence to cut per-robot programming time,
which mattered when commissioning a whole warehouse of shuttles on a deadline.

## Quantified Outcomes

- **Firmware flashing time** — manual multi-step process reduced to a single ~2-minute automated run.
- **Fleet visibility** — first real-time telemetry for ~30 robots, surfacing faults before they stalled a line.
- **Commissioning** — reduced the time to bring a new robot online during warehouse rollout.

## CV-Ready Bullets

- Built the first end-to-end telemetry pipeline (MQTT → Python ingest → AWS IoT Core) for a ~30-robot fleet, giving the team real-time fleet-health visibility for the first time.
- Automated motor-controller firmware flashing and verification over UART, cutting per-robot programming to a single ~2-minute step and removing the need for a firmware engineer on site.

## STAR Story Seeds

**First telemetry pipeline**
**S:** The robot fleet was a black box — faults were only discovered when a shuttle physically
stopped on the warehouse floor.
**T:** Get real-time health data off the robots and somewhere the team could see it.
**A:** Added an MQTT publisher to the firmware, wrote a Python ingest service, and pushed
device state into AWS IoT Core with simple dashboards on top.
**R:** First-ever fleet-health visibility for ~30 robots, surfacing faults before they stalled a line.
