---
id: world-model-kb.papers.xiaomi-robotics-1
title: Xiaomi-Robotics-1 Paper Knowledge Entry
kind: paper
status: maintained
last_updated: 2026-08-21
owners:
  - AIBuildAI world-model group
---

# Xiaomi-Robotics-1 Paper Knowledge Entry

## Retrieval metadata

**Relevant queries:** Xiaomi-Robotics-1 report, 100K hours UMI, embodiment-free pre-training, scaling VLA, auto-labeling scene transitions, Mixture-of-Transformers policy, RoboCasa 74.5, RoboCasa365 57.4, VLABench 59.1, RoboDojo 20.07, real-robot adaptation, arXiv 2607.15330.

**Knowledge provided:** the report's identity and artifacts, the pre-training/post-training paradigm and its scaling evidence, the benchmark protocols and numbers bound to named checkpoints, what the report does not disclose, and falsifiable transfer hypotheses for post-training the released model.

**Related pages:** [Xiaomi-Robotics-1 model entry](../../models/xiaomi-robotics-1/README.md) owns the released checkpoints, code, and conventions; [VLABench](../vlabench/README.md) owns the benchmark; [ERVLA](../ervla/README.md) owns the chain-of-thought recipe the report adopts; [embodied systems](../../foundations/embodied-systems/robotics-and-embodied-ai.md) owns robot interfaces; [datasets and supervision](../../foundations/data-and-evaluation/datasets-and-supervision.md) owns data vocabulary.

## Identity and revision boundary

| Field | Canonical value | Consequence |
|---|---|---|
| Work | *Xiaomi-Robotics-1: Scaling Vision-Language-Action Models with over 100K Hours of Real-World Trajectories* | Technical report, arXiv:2607.15330v1, 2026-07-16 [XR1-TR] |
| Authors | Xiaomi Robotics Team (Jun Guo, Piaopiao Jin, Jason Li, Peiyan Li, Yingyan Li, Futeng Liu, Wanli Peng, Optimus Qin, Yifei Su, et al.) | |
| Code and weights | `XiaomiRobotics/Xiaomi-Robotics-1` @ `556cca33…`; HF collection (5B base + three fine-tunes), released 2026-08-03 | Post-training and evaluation code only; no pre-training code or UMI corpus [XR1-CODE; XR1-HF-COLLECTION] |
| Predecessor | Xiaomi-Robotics-0 (arXiv:2602.12684) | Source of the asynchronous-execution recipe; its numbers are not XR-1's [XR0-TR] |
| Leaderboard | Papers with Code RoboCasa row verified by the authors | No VLABench row there [XR1-PWC] |
| Project page and mirror | robotics.xiaomi.com project page; ModelScope collection | Presentation surface and download mirror; numbers remain paper-owned [XR1-PROJECT; XR1-MODELSCOPE] |

## Operational model boundary

The report claims a two-stage recipe: embodiment-free pre-training on >100K h of UMI data auto-labelled with scene-transition captions, then cross-embodiment post-training (~10K h) for embodiment and instruction alignment, yielding a model that performs mobile manipulation out of the box and adapts to new tasks from < 10 h of demonstrations. Benchmark numbers come from per-benchmark fine-tunes of the post-trained 5B. [XR1-TR, Abstract, Sec. 4-5]

| Surface | Inputs | Outputs | Invalid projection |
|---|---|---|---|
| Post-trained 5B | 3 views, instruction, state | action chunk | Benchmark scores without the benchmark fine-tune |
| Benchmark fine-tunes | benchmark views/state | benchmark action convention | Cross-benchmark reuse |
| Scaling curves | pre-training subsets, 2B/5B/10B | validation action MSE | Closed-loop success |

## Knowledge map

| Question | Canonical page |
|---|---|
| Method, data, training, experiments, evidence limits | [`paper.md`](paper.md) |
| Released implementation and its boundary with the paper | [`codebase.md`](codebase.md) |
| What has been executed locally | [`reproduction.md`](reproduction.md) |
| Transferable interventions and falsification tests | [`optimization-transfer.md`](optimization-transfer.md) |
| Paper and mirror identities | [`sources.yaml`](sources.yaml); code and checkpoints resolve through the model entry's registry |

## High-value evidence anchors

- Table 1: 2B/5B/10B = 2.6B/5.1B/10.5B total parameters; only the 5B is released. [XR1-TR]
- Table 4: VLABench 59.1 SR / 70.3 PS / 69.9 IS over five tracks; ERVLA 53.2, pi0.5 48.1, pi0-FAST 39.8 under the same protocol. [XR1-TR]
- Scaling: validation action error improves monotonically with data (12.5 -> 100 % of ~20K h) and size; "no sign of saturation". [XR1-TR, Sec. 6]
- Real-robot adaptation: 75 % success with < 10 h per task versus pi0.5's 40 %. [XR1-TR, Table 6]
- Not disclosed: pre-training compute, VLABench/RoboCasa fine-tune hyperparameters, any ablation table. [XR1-TR; XR1-ISSUE-4]

## Sources

Paper identity resolves through [XR1-TR]; code, checkpoints, and issues through the [model entry's registry](../../models/xiaomi-robotics-1/sources.yaml).
