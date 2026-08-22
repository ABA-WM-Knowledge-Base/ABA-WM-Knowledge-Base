---
id: world-model-kb.models
title: Part III — Model Entries
kind: index
status: maintained
last_updated: 2026-08-19
owners:
  - AIBuildAI world-model group
---

# Part III — Model Entries

## Retrieval metadata

**Relevant queries:** model-specific architecture, checkpoint, interface, data, training, evaluation, implementation, execution, or optimization knowledge.

**Knowledge provided:** the Part III ownership boundary and its active Cosmos3-Nano model entry.

**Related pages:** [Part I](../foundations/README.md) covers general concepts; [Part II](../papers/README.md) covers paper-specific knowledge; [Components](../components/README.md) contains independently scoped component knowledge; [Cosmos3-Nano](cosmos3-nano/README.md) is the active model entry.

## Active entry

| Entity | Canonical scope | Entry point |
|---|---|---|
| Cosmos3-Nano | Model-specific mechanisms, interfaces, training, evaluation, code, execution state, optimization levers, and decision blockers | [Cosmos3-Nano](cosmos3-nano/README.md) |

Each `models/<model-id>/` entry owns facts for one named model and links reusable concepts back to Foundations and relevant entry-specific knowledge back to Components. Active entries: Cosmos3-Nano and Xiaomi-Robotics-1. A future entry must define its own canonical owners, provenance, retrieval metadata, and execution-evidence boundary; adding an entry does not change the four-part architecture.

- [Xiaomi-Robotics-1](xiaomi-robotics-1/README.md) - 5B VLA (DiT action head over a Qwen3-VL backbone), VLABench campaign entry.
