---
id: world-model-kb.papers.ervla.reproduction
title: ERVLA Reproduction State and Experiment Contracts
kind: record
status: maintained
last_updated: 2026-08-21
owners:
  - AIBuildAI world-model group
---

# ERVLA Reproduction State and Experiment Contracts

## Retrieval metadata

**Relevant queries:** ERVLA reproduced, ERVLA checkpoint unavailable, CoT ablation replication, reasoning dropout replication on Xiaomi-Robotics-1, not attempted, contracts.

**Knowledge provided:** the current non-execution state, why direct reproduction is not possible, and the proxy experiments on a public stack that would test the paper's transferable claims.

**Related pages:** [`codebase.md`](codebase.md) owns the surface map; [`paper.md`](paper.md) owns values; [Xiaomi-Robotics-1 reproduction](../../models/xiaomi-robotics-1/reproduction.md) owns the campaign-side ledger where a proxy run would be recorded.

## 1. Current execution state

| Surface | Evidence state | Recorded evidence | Permitted claim |
|---|---|---|---|
| Paper | source inspected | arXiv:2606.03784v1 [ERV-PAPER] | Tables and mechanism read |
| Code / weights / corpus | unavailable | project page announcement [ERV-PROJECT] | Nothing executable |
| LIBERO-Plus / VLABench tables | not reproducible | no checkpoint | Numbers remain paper-reported |
| CoT content ablation (Table 1) | not reproducible as published | no corpus | |
| Proxy: reasoning dropout on Xiaomi-Robotics-1 with self-generated labels | not attempted | none | |

## 2. Why direct reproduction is blocked

No artifact exists; the annotation pipeline depends on detectors and simulator replay the paper describes but does not ship; the training corpus is a 2,592-hour multi-source mix. Until a release, every ERVLA claim is source-reported.

## 3. Proxy contracts (testing the transferable claims on a public stack)

- **Reasoning dropout helps language tracks:** Xiaomi-Robotics-1 warm start, VLABench official set, two runs (`cot_prob` 0 vs 0.5) at equal steps and seed with VLM-generated grounded CoT (target, relative position, sub-goal, next motion); paired L2 per track. Acceptance: Track 3/4 paired SR difference beyond the noise band with Track 1 unchanged.
- **Grounded beats abstract content:** three label variants (motion-only, abstract-only, full) at `cot_prob` 0.5; paired L2. Acceptance: ordering consistent with Table 1's direction.
- **Inference without reasoning preserves gains:** the served HF model cannot generate text, so this claim is structurally satisfied by the serving path and cannot be tested against a "with reasoning" arm on this stack.

Records, when produced, belong in the model entry's ledger with run IDs, commits, data hashes, and artifacts.

## Sources

[ERV-PAPER]; [ERV-PROJECT]; [XR1-TR].
