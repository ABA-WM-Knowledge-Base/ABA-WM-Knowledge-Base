---
id: world-model-kb.foundations.data-and-evaluation
title: Data and Evaluation
kind: index
status: maintained
last_updated: 2026-08-11
owners:
  - AIBuildAI world-model group
---

# Data and Evaluation

## Retrieval metadata

**Relevant queries:** data composition, supervision, curation, contamination, coverage, benchmark design, rollout error, physical consistency, calibration, downstream utility, or controlled comparison.

**Knowledge provided:** model-independent principles for constructing learning evidence and evaluating predictive, generative, physical, and decision-making claims under explicit conditions.

**Related pages:** [Representations](../representations/README.md), [learning objectives](../learning-objectives/README.md), and [decision-making](../decision-making/README.md) define what data and metrics must test; [Cosmos3-Nano evaluation](../../models/cosmos3-nano/evaluation.md) owns model-specific results.

## Canonical boundary

This subpart owns data identity, sampling, supervision, coverage, leakage, evaluation protocols, metric validity, aggregation, and confounding. It does not own a particular model's dataset mixture, benchmark score, or local reproduction state.

## Topic map

| Topic | Canonical scope |
|---|---|
| [Datasets and supervision](datasets-and-supervision.md) | Data domains, sequence construction, labels, synthetic data, filtering, mixture design, contamination, and provenance |
| [Evaluation methodology](evaluation-methodology.md) | Capability decomposition, one-step and rollout metrics, physical and causal validity, downstream control, calibration, protocols, and statistical comparison |

Evidence criteria guide interpretation and strategy selection; they do not schedule experiments or determine AIBuildAI stopping and retry behavior.
