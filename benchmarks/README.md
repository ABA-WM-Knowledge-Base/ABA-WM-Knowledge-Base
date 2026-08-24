---
id: world-model-kb.benchmarks
title: Benchmark Entries
kind: index
status: maintained
last_updated: 2026-08-24
owners:
  - AIBuildAI world-model group
---

# Benchmark Entries

## Retrieval metadata

**Relevant queries:** benchmark identity, simulator version, task suite, environment distribution, dataset, evaluator, metric, rollout protocol, baseline comparability, or benchmark reproduction.

**Knowledge provided:** the Benchmark ownership boundary and the active Original RoboCasa entry.

**Related pages:** [Foundations](../foundations/README.md) owns model-independent evaluation principles; [Papers](../papers/README.md) owns paper-specific experimental evidence; [Components](../components/README.md) contains independently scoped synthesis; [Models](../models/README.md) owns checkpoint-specific results and implementation facts. [Original RoboCasa](robocasa/README.md) is the active benchmark entry.

## Ownership boundary

A benchmark entry owns the versioned evaluation system required to interpret a result: simulator and assets, task and reset distributions, demonstrations, observation and action contracts, success predicates, horizons, rollout sampling, aggregation, and evaluator code. A Paper owns how one work used that system. A Model owns the exact checkpoint and adapter evaluated. Foundations owns transferable comparison and validity principles.

This separation prevents a benchmark name from acting as an underspecified metric label. A result is comparable only within a sufficiently matched protocol tuple; cross-entry links expose dependencies without defining AIBuildAI task order or Agent selection.

## Active entries

| Benchmark | Canonical scope | Excluded identity | Entry point |
|---|---|---|---|
| Original RoboCasa | RSS 2024 environment, 120 kitchen scenes, 100-task taxonomy, original demonstration releases, paper protocols, and official `v0.2` code surface | RoboCasa365 `v1.0+` tasks, scenes, datasets, horizons, and leaderboard | [RoboCasa](robocasa/README.md) |

Each future entry declares its own file inventory and canonical owners. The current RoboCasa structure is not a requirement that unrelated benchmarks answer an identical checklist.
