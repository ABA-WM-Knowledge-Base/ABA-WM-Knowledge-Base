---
id: world-model-kb.models
title: Model Entries
kind: index
status: maintained
last_updated: 2026-08-24
owners:
  - AIBuildAI world-model group
---

# Model Entries

## Retrieval metadata

**Relevant queries:** model-specific architecture, checkpoint, interface, data, training, evaluation, implementation, execution, or optimization knowledge.

**Knowledge provided:** the Model ownership boundary and its active Cosmos3-Nano, X-WAM, and Xiaomi-Robotics-1 entries.

**Related pages:** [Foundations](../foundations/README.md) covers general concepts; [Papers](../papers/README.md) covers paper-specific knowledge; [Components](../components/README.md) contains independently scoped component knowledge; [Benchmarks](../benchmarks/README.md) owns versioned evaluation systems.

## Active entries

| Entity | Canonical scope | Entry point |
|---|---|---|
| Cosmos3-Nano | Model-specific mechanisms, interfaces, training, evaluation, code, execution state, optimization levers, and decision blockers | [Cosmos3-Nano](cosmos3-nano/README.md) |
| X-WAM | Wan2.2-based RGB-D/state/action architecture, released checkpoints and data, interface and scheduler contracts, benchmark-bound results, execution state, and optimization levers | [X-WAM](x-wam/README.md) |
| Xiaomi-Robotics-1 | Qwen3-VL backbone, flow-matching DiT action head, released base and VLABench checkpoints, interfaces, training and evaluation evidence, execution state, and optimization levers | [Xiaomi-Robotics-1](xiaomi-robotics-1/README.md) |

Each `models/<model-id>/` entry owns facts for one named model and links reusable concepts back to Foundations, paper evidence to Papers, cross-method knowledge to Components when applicable, and evaluation semantics to Benchmarks. An active entry must define its own canonical owners, provenance, retrieval metadata, and execution-evidence boundary; adding an entry does not change the five-part peer architecture.
