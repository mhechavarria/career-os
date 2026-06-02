---
name: kvlite
slug: kvlite
status: shipped
role: Creator / maintainer
stack: [Go]
links:
  repo: https://github.com/jordan-rivera-dev/kvlite
visibility: public
period: 2020–present
---

# kvlite — Embeddable LSM-Tree Key-Value Store

A small, dependency-free embeddable key-value store written in Go, built to make the
internals of an LSM-tree storage engine legible. Repo:
[github.com/jordan-rivera-dev/kvlite](https://github.com/jordan-rivera-dev/kvlite).

## Outcomes

- Under 2,000 lines of Go implementing a write-ahead log, memtable, SSTable flush, and compaction.
- Benchmarks documenting write and read throughput across compaction strategies.
- Used as the worked example in two internal "how databases store data" workshops.

## Context & Architecture

Writes land in a write-ahead log and an in-memory memtable; when the memtable fills it is
flushed to an immutable on-disk SSTable, and a background compactor merges SSTables to bound
read amplification. The goal was never to compete with production stores but to be readable:
every component is small, tested, and commented for the engineer trying to learn the pattern.
It doubles as my reference implementation when reasoning about storage trade-offs at work.
