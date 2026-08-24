---
id: world-model-kb.papers.x-wam.reproduction
title: X-WAM Paper Reproduction State
kind: record
status: maintained
last_updated: 2026-08-24
owners:
  - AIBuildAI world-model group
---

# X-WAM Paper Reproduction State

## Retrieval metadata

**Relevant queries:** reproduce X-WAM paper, source inspection, checkpoint download, model load, action inference, RGB-D generation, RoboCasa evaluation, training reproduction, hardware, failure, artifact, or acceptance criterion.

**Knowledge provided:** claim-separated reproduction states and the evidence needed to distinguish source inspection, released-model execution, benchmark reproduction, and paper-training reproduction.

**Related pages:** [Codebase](codebase.md) owns executable paths and source conflicts; [X-WAM Model reproduction](../../models/x-wam/reproduction.md) owns public-checkpoint runtime state; [RoboCasa reproduction](../../benchmarks/robocasa/reproduction.md) owns simulator/evaluator state.

## Claim registry

| Claim | Identity | State | Retained evidence | Acceptance condition |
|---|---|---|---|---|
| Paper v2 method and experiments can be resolved | `arXiv:2604.26694v2` | Source-inspected | PDF SHA256, extracted text, visual checks of Figures 1-2 and Tables 1-4 | Satisfied as document inspection only |
| Official code implements the proposed core mechanisms | commit `72cfb86...` | Source-inspected | Class/function mapping, configs, submodule commits | Satisfied as source mapping; no runtime implication |
| Public checkpoint repository is resolvable | HF `bb6fd1...` | Metadata-inspected | Revision, eight-file tree, three 38,892,887,xxx-byte weights, configs | Satisfied as remote metadata; weights not downloaded |
| One checkpoint loads and returns non-empty actions | released model + Wan2.2 base | Not attempted | None | Successful BF16 load, fixed input, output `[1,32,14]`, log, latency, peak memory, artifacts |
| Full world mode returns RGB and depth | same revision, 50 steps | Not attempted | None | Decoded nine-frame multi-view RGB-D output plus state/action, shapes and hashes |
| 79.2% RoboCasa result is reproduced | RoboCasa SFT, 24 tasks ×100 episodes | Not attempted | None | 2,400 raw outcomes, videos, environment/config hashes, exact aggregate |
| 89.8%/90.7% RoboTwin result is reproduced | RoboTwin SFT, 50 tasks ×100 per setting | Not attempted | None | 10,000 raw outcomes plus protocol artifacts |
| Table 3 reconstruction metrics are reproduced | paper evaluation implementation | Not attempted | None | Fixed scenario set, predictions, ground truth, per-sample and aggregate metric code/artifacts |
| 5,873.9-hour pretraining is reproduced | paper training recipe | Blocked by unavailable full corpus/manifest and compute in current workspace | Source-level dataset table only | Complete data identity, 256-H20-class run, resolved paper/release discrepancies, training artifacts |

No source-inspection state is promoted to model inference or benchmark reproduction.

## Released-model smoke-test contract

The smallest meaningful model execution uses the pinned X-WAM code, one named HF checkpoint config and weight file, the pinned Wan2.2-TI2V-5B base, UMT5-XXL encoder, VAE, one three-view RGB observation, one 16D state, and one instruction. It records dependency lock, GPU, CUDA, BF16/TF32 settings, compile mode, seeds, resolved config, preprocessing tensors, model-load warnings, output shapes, latency, and peak memory.

Policy acceptance requires finite actions with shape `[B,32,14]`, masked unused right-arm channels for RoboCasa, and correct denormalization/gripper sign under the checkpoint config. Full-world acceptance additionally requires decodable RGB-D across the expected view/time layout; action-only success does not establish depth generation.

## Benchmark reproduction contract

RoboCasa reproduction pins the X-WAM submodules, exact checkpoint and base revisions, task order, five layout/style pairs, object split `B`, cameras, controller, horizon table, deterministic seed function, action length, success predicate, and 100 episodes per task. Broker and server logs, client JSON, all videos or a declared retention sample, and the merged per-task table are artifacts. [XWAM-CODE-72CF, `evaluation/README.md`, `evaluation/robocasa_client.py`]

The paper's 79.2% acceptance threshold should be accompanied by binomial uncertainty and per-task differences, not only exact equality of the rounded mean. A mismatch must first be localized to task, environment, checkpoint/config, action transform, horizon, or nondeterministic kernel before it is interpreted as a model-quality failure.

## Training reproduction identity split

Two valid but different targets exist:

- **Paper recipe:** Appendix B values, including benchmark LR `3e-5` and 20K steps for the shared fine-tuning description.
- **Released checkpoint recipe:** HF config values, including LR `1e-5`, RoboCasa 20K, and RoboTwin 40K.

A run cannot simultaneously claim exact reproduction of both. The missing distributed pretraining state, data filtering implementation, pseudo-depth artifacts, and full source data further prevent a complete paper-pretraining reproduction from being inferred from the released SFT code.

## Resource boundary

Each X-WAM checkpoint state file is approximately 38.89 GB, and the collection contains three such files before the Wan2.2 base and text/VAE weights. GPU memory requirements are not published as a single minimum. The paper trains on H20 clusters and reports policy ablation latency on RTX 3090 plus real deployment on RTX 5090 D; these facts do not guarantee that a 5B base plus copied depth blocks fits an arbitrary consumer GPU. [XWAM-HF-CHECKPOINTS; XWAM-PAPER-V2, pp.9, 17-20]

## Sources

Paper and code states use `XWAM-PAPER-V2` and `XWAM-CODE-72CF`. Model artifact metadata uses `XWAM-HF-CHECKPOINTS` and `XWAM-WAN22-HF`, owned by the [X-WAM Model registry](../../models/x-wam/sources.yaml).
