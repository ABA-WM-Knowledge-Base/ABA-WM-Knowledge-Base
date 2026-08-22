---
id: world-model-kb.models.xiaomi-robotics-1.research-queue
title: Xiaomi-Robotics-1 Open Research Registry
kind: record
status: maintained
last_updated: 2026-08-21
owners:
  - AIBuildAI world-model group
---

# Xiaomi-Robotics-1 Open Research Registry

## Retrieval metadata

**Relevant queries:** unresolved question, missing evidence, undisclosed recipe, CoT payoff, stats convention, memory at batch 48, episode wall clock, evaluator defects, discriminating experiment.

**Knowledge provided:** a descriptive registry of unresolved questions with known facts, missing evidence, minimum experiments, and closure rules. Dependency-impact labels do not schedule AIBuildAI work.

**Related pages:** [Reproduction](reproduction.md) holds executed state; [Optimization playbook](optimization-playbook.md) holds experiment patterns; [Limitations](limitations.md) holds guardrails; [open problems](../../foundations/research-frontiers/open-problems.md) owns cross-model unknowns.

## Registry semantics

`critical` blocks trustworthy execution or attribution; `decision` blocks selection among optimization paths; `traceability` improves completeness. States: `ready`, `blocked`, `in_progress`, `resolved`, `superseded`.

## Dependency graph

```text
RQ-ANCHOR-001 -> RQ-BRIDGE-001 -> all training decisions
RQ-SMOKE-001  -> budget sizing
RQ-STATS-001  -> RQ-COT-001, RQ-TRACK-001
RQ-EVAL-001   -> interpretation of IS/PS
```

## Critical dependency impact

### RQ-ANCHOR-001 - Released checkpoint L2 on the campaign fleet

- **Dependency impact:** `critical`; **State:** `resolved` on the developer host (run `xr1-l2-released-20260821-01`: sr_avg_5track 50.4, IS 70.8, 250 episodes, 21 s/episode effective on 2 workers); re-measure on the rental before the campaign
- **Decision:** the comparison baseline for every node; the per-episode wall clock.
- **Known:** 59.1 / 70.3 / 69.9 reported over 50 episodes per task; client constants fixed. [XR1-TR; XR1-CODE-EVAL-VLABENCH]
- **Unknown:** the number on the pinned VLABench commit with EGL on the rental GPUs; episode seconds.
- **Minimum experiment:** serve the released dir, run the 250-episode prefix, retain the bundle.
- **Closure rule:** `sr_avg_5track` within ~6 pp of 59.1 with < 10 % interface errors; wall clock recorded.

### RQ-BRIDGE-001 - Importer/exporter round trip preserves behaviour

- **Dependency impact:** `critical`; **State:** `resolved` (`xr1-roundtrip-20260821-02`: 49/50 track-1 episodes agree with the anchor, equal to the same-checkpoint rerun band; the first attempt with float32-rounded stats agreed on 42/50 - stats precision is part of the bridge contract)
- **Known:** the HF checkpoint lacks the choice heads; the trainer load is strict; the export keeps the reference's 1,120 keys. [XR1-CODE; XR1-HF-VLABENCH]
- **Unknown:** whether an untrained import -> export reproduces the anchor's per-episode outcomes.
- **Minimum experiment:** export the untrained warm start; score with the same seed and configs.
- **Closure rule:** identical outcomes, or SR within 1 pp. Measured repeatability floor: 1/50 flips between two runs of the same checkpoint and seed.

### RQ-SMOKE-001 - Memory and step time at the framework defaults

- **Dependency impact:** `critical`; **State:** `resolved` (`xr1-smoke-lambda-20260821-01`: batch 48 x 8 ranks on A100-80GB SXM4 = ~7 s/step, batch 32 = ~5 s/step, no OOM; nvidia-smi reserved ~80 GB at both so allocated headroom is unmeasured; 2 x batch 8 on PCIe = ~2 s/step). Budget arithmetic: 3,000 steps at batch 48 x 8 = ~6 h, the 10,000-step default = ~20 h
- **Known:** 5B bf16, ZeRO-2, gradient checkpointing on; batch 48 per rank in the real-robot demo config; no published footprint. [XR1-CODE]
- **Unknown:** peak VRAM and s/step on 80 GB cards at batch 48 with three 480x480 views.
- **Minimum experiment:** 5-step smoke at `gpus` 8 and 2; read `train/token`.
- **Closure rule:** recorded peak memory and s/step; a batch that fits.

### RQ-STATS-001 - Which normalization stats to train under

- **Dependency impact:** `decision`; **State:** `ready`
- **Known:** released stats have roll/yaw std ~10x pitch (unwrapped Euler differences); the data path wraps deltas. [XR1-HF-VLABENCH]
- **Unknown:** whether re-estimated (wrapped) stats improve or hurt a warm start from weights trained under the released stats.
- **Minimum experiment:** two otherwise identical fine-tunes (released stats vs re-estimated), paired L2.
- **Closure rule:** a difference beyond 6 pp in either direction, or equivalence.

## Decision dependency impact

### RQ-COT-001 - Does self-generated CoT at `cot_prob` 0.5 move the language tracks?

- **Dependency impact:** `decision`; **State:** `blocked` (depends on labels + RQ-SMOKE-001)
- **Known:** the report used ERVLA-style CoT at 50 %; ERVLA found grounded motion/trajectory content helpful (+4.1 / +4.8) and abstract fields harmful in its setting; Xiaomi's labels are unreleased. [XR1-TR; ERV-PAPER, Table 1]
- **Unknown:** the effect of our VLM-written labels on Tracks 3/4 at equal steps.
- **Minimum experiment:** `cot_prob` 0 vs 0.5, same steps/seed, paired L2; optionally a content ablation (motion-only vs full).
- **Closure rule:** per-track paired differences with the noise band.

### RQ-TRACK-001 - Which intervention moves cross-category and common-sense SR?

- **Dependency impact:** `decision`; **State:** `blocked` (depends on RQ-ANCHOR-001)
- **Known:** in-distribution 75.6 vs 53.0 / 48.4; no published intervention on top of this checkpoint. [XR1-TR, Table 4]
- **Unknown:** whether failures there are grounding (IS) or grasp (PS) dominated.
- **Minimum experiment:** label the anchor's failed episodes on those tracks with the diagnosis protocol; pick the lever by the dominant label.
- **Closure rule:** a labelled failure table for the anchor.

### RQ-INFER-001 - Inference-time levers

- **Dependency impact:** `decision`; **State:** `ready`
- **Known:** `num_steps`, seed, `replan_steps` are client/server arguments; none reported. The gripper probe on `select_fruit` shows the release command appearing at chunk positions 7-9 while the client executes 5, so `replan_steps` is not a neutral speed knob for this checkpoint: executing more of the chunk (or re-querying with the executed prefix) is the first lever to test for the release-timing failures. [XR1-CODE-EVAL-VLABENCH; XR1-HF-VLABENCH; probe `xr1-grip-probe-20260821-01`]
- **Minimum experiment:** released checkpoint at steps 5 vs 10, replan 5 vs 10, seeds 42 vs ensemble of 3; paired L2.
- **Closure rule:** recorded deltas; any protocol change is reported separately from the official-protocol number.

## Traceability dependency impact

### RQ-EVAL-001 - Evaluator defects and their effect on IS/PS

- **Dependency impact:** `traceability`; **State:** `ready`
- **Known:** issues 55, 80, 82, 88 open at the pinned commit. [VLAB-ISSUE-55; VLAB-ISSUE-80; VLAB-ISSUE-82; VLAB-ISSUE-88]
- **Minimum experiment:** count IS = 0 on successes in the anchor run; hold-still test on one task.
- **Closure rule:** a measured defect rate to annotate IS/PS comparisons.

### RQ-SOURCE-001 - Episode-count statement

- **Dependency impact:** `traceability`; **State:** `resolved` (2,460 executable vs "2,500" in prose). [XR1-TR; VLAB-CODE]

## Sources

[XR1-TR]; [XR1-CODE]; [XR1-CODE-EVAL-VLABENCH]; [XR1-HF-VLABENCH]; [VLAB-CODE]; [ERV-PAPER]; [VLAB-ISSUE-55]; [VLAB-ISSUE-80]; [VLAB-ISSUE-82]; [VLAB-ISSUE-88].
