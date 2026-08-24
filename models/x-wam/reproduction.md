---
id: world-model-kb.models.x-wam.reproduction
title: X-WAM Execution-State Ledger
kind: record
status: maintained
last_updated: 2026-08-24
owners:
  - AIBuildAI world-model group
---

# X-WAM Execution-State Ledger

## Retrieval metadata

**Relevant queries:** X-WAM reproduction status, source inspection, checkpoint download, model load, action inference, RGB-D generation, RoboCasa rollout, training run, failure, artifact, or acceptance criterion.

**Knowledge provided:** the sole mutable execution-state registry for the X-WAM model entry and claim-specific promotion requirements that prevent source documentation from being interpreted as a completed run.

**Related pages:** [Inference](inference.md) defines executable modes; [evaluation](evaluation.md) owns reported baselines; the [Paper reproduction page](../../papers/x-wam/reproduction.md) owns paper-level reproduction targets; [RoboCasa reproduction](../../benchmarks/robocasa/reproduction.md) owns simulator and benchmark state.

## Claim registry

| Claim surface | Fixed identity | Current state | Retained evidence | Promotion condition |
|---|---|---|---|---|
| model architecture and runtime source resolve | code `72cfb86...` | Source-inspected | symbol map, configs, submodule pins | satisfied only as source inspection |
| three public X-WAM artifacts resolve | HF `bb6fd1...` | Metadata-inspected | revision, paths, roles, byte sizes | satisfied only as remote metadata |
| public SFT data identities resolve | RoboCasa `f439f3...`; RoboTwin `383c3b...` | Metadata-inspected | revisions, episode/frame counts, card fields | satisfied only as remote metadata |
| one X-WAM checkpoint file downloads intact | named artifact and revision | Not attempted | none | byte count plus retained cryptographic hash and download log |
| checkpoint assembles with Wan base and loads | named X-WAM state + Wan `921dba...` | Not attempted | none | complete load, reviewed key report, resolved config, environment, memory trace |
| RoboCasa action-only fixture returns output | RoboCasa SFT fixed revision | Not attempted | none | finite `[1,32,14]` raw and denormalized actions from a retained fixture |
| full unified prediction returns RGB-D/state/action | named checkpoint, 50 video steps | Not attempted | none | decodable multi-view outputs with expected shapes, hashes, logs, and resources |
| closed-loop Original RoboCasa result is reproduced | pinned simulator and 24-task protocol | Not attempted | none | raw per-rollout records and protocol-complete aggregate |
| benchmark SFT executes | one released SFT config and dataset revision | Not attempted | none | nonzero training steps, loss trace, saved state, resolved exposure and resources |
| cross-embodiment pretraining is reproduced | paper corpus and distributed recipe | Blocked by unavailable complete corpus manifest and current compute | paper/source inspection only | complete source membership and a compute-matched, artifact-complete run |

No local checkpoint, inference, rollout, or training success is asserted by this ledger.

## Inspection evidence retained in the KB

The paper PDF was resolved as arXiv v2 and hashed before extraction; its architecture and main result pages were visually checked. The official repository was inspected at the pinned commit down to model, runner, data, training, configuration, and evaluation symbols. HF repository metadata was inspected at immutable revisions, including the three state-file byte sizes and two dataset inventories. These actions support identities and implementation knowledge but do not execute any neural or simulator computation. [XWAM-PAPER-V2; XWAM-CODE-72CF; XWAM-HF-CHECKPOINTS; XWAM-HF-ROBOCASA; XWAM-HF-ROBOTWIN]

## Checkpoint-load acceptance

A load record should retain code and artifact revisions, file hashes, exact filesystem roles, OS, Python, package lock, CUDA/driver, GPU topology, precision, attention backend, compile setting, host RAM, and resolved configuration. It should report missing/unexpected state keys without suppressing them, parameter count measured from the assembled network, load duration, and peak allocated/reserved/device memory.

Acceptance requires that the intended Wan and X-WAM states are applied to every expected parameter group and that a deterministic forward fixture produces finite tensors. An import, config parse, or partial `strict=False` load does not satisfy this claim.

## Action-only acceptance

The smallest policy fixture contains a fixed instruction, three named RGB views, a 16D canonical state, checkpoint-specific quantile statistics, view order, image preprocessing, and seed. It records normalized input tensors, condition masks, raw predicted normalized actions, denormalized canonical actions, and benchmark-adapter output.

For RoboCasa, acceptance includes output shape `[1,32,14]`, zero/masked unused right-arm channels where expected, finite values, correct gripper inversion, and a no-op/small-motion adapter test. This remains an open-loop model-interface result until actions are executed in a pinned environment.

## Full-world acceptance

Full mode must continue the 50-step video schedule, enable the depth branch, and retain RGB, inverse-depth/depth, predicted state, and action outputs for all views and time positions. Evidence includes latent and decoded shapes, scheduler indices, condition preservation, media files, output hashes, seed, model-call count, VAE/depth settings, wall time, and peak memory. An action-only early-stop response cannot promote this row.

## Closed-loop acceptance

Original RoboCasa promotion requires the benchmark's pinned code/dependencies plus task list, five layout/style pairs, object split, cameras, controller, horizon, success predicate, seeds, action-chunk execution rule, retry/timeout behavior, and per-step traces. Retain every rollout outcome, per-task summary, aggregate uncertainty, logs, videos or a declared retention policy, and failure labels. [XWAM-CODE-72CF, `evaluation/robocasa_client.py`; RC24-CODE-V02]

Exact equality with the rounded 79.2% paper mean is not the only diagnostic. First compare per-task outcomes and confidence intervals, then localize differences to environment state, adapter, checkpoint/config, inference, or stochastic evaluation. A result under RoboCasa365 remains a separate claim.

## Training acceptance boundary

Released-checkpoint SFT reproduction follows the pinned HF config and records any explicit override. Paper-recipe reproduction follows the paper values and records unavailable implementation details. Because learning rate and RoboTwin step counts conflict, neither target may be described as the other. Pretraining acceptance additionally requires episode-level source manifests, sampling/exposure traces, pseudo-depth provenance, distributed topology, resolved batch semantics, optimizer/scheduler state, checkpoints, and evaluation artifacts.

## Sources

Execution identities use `XWAM-CODE-72CF`, `XWAM-PAPER-V2`, `XWAM-HF-CHECKPOINTS`, `XWAM-HF-ROBOCASA`, `XWAM-HF-ROBOTWIN`, `XWAM-WAN22-HF`, and `RC24-CODE-V02`.
