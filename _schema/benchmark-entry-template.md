---
id: world-model-kb.benchmark-entry-template
title: Benchmark Entry Template
kind: guide
status: maintained
last_updated: 2026-08-24
owners:
  - AIBuildAI world-model group
---

# Benchmark Entry Template

A benchmark entry represents an evaluation system, not only a metric name. It keeps simulator and asset identity, tasks, datasets, protocols, evaluators, baselines, code, and observed execution state connected under explicit versions.

## Entry contract

Each active entry declares its concrete file inventory in `metadata.schema.yaml`. The current RoboCasa entry uses `benchmark.yaml` for identity and protocol boundaries, `retrieval-index.yaml` for advisory query-to-knowledge associations, canonical Markdown owners for detailed knowledge, and `sources.yaml` for provenance. This structure describes the current entry and does not grant the KB workflow-orchestration authority.

## Required knowledge boundaries

- **Scope and versions:** distinguish the named release from predecessors, successors, forks, and mutable documentation.
- **Tasks and environments:** bind task identifiers and success predicates to scene, object, embodiment, controller, camera, and reset distributions.
- **Datasets:** preserve trajectory provenance, supervision, sampling, filtering, licenses, and train/evaluation separation.
- **Protocol and metrics:** define the rollout unit, horizon, termination, seed and scenario generation, success aggregation, and uncertainty reporting.
- **Results:** retain model/checkpoint identity and every protocol condition needed to compare numbers.
- **Code and reproduction:** map claims to pinned symbols and keep documented capability separate from locally observed execution.
- **Optimization reference:** connect failure slices to measurable model changes without turning benchmark knowledge into a task scheduler.

Every canonical Markdown page uses the retrieval metadata and provenance rules in the [style guide](style-guide.md). Future benchmark entries may use different topic pages when their evaluation system demands different owners; their inventories must be declared rather than inferred from RoboCasa.
