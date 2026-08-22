---
id: world-model-kb.papers.ervla
title: ERVLA Paper Knowledge Entry
kind: paper
status: maintained
last_updated: 2026-08-21
owners:
  - AIBuildAI world-model group
---

# ERVLA Paper Knowledge Entry

## Retrieval metadata

**Relevant queries:** ERVLA, embodied chain-of-thought, revisiting ECoT, reasoning dropout, CoT dropout, /cot /no_cot, grounded language action guidance, point trajectory, end-effector movement, knowledge truncation, choice policy branch, LIBERO-Plus 86.9, VLABench 53.2, arXiv 2606.03784.

**Knowledge provided:** the paper's identity, its finding on which chain-of-thought content helps a VLA, the reasoning-dropout training scheme that Xiaomi-Robotics-1 adopted for VLABench, architecture and ablation evidence, and transfer hypotheses for a CoT auxiliary loss on another VLA.

**Related pages:** [Xiaomi-Robotics-1 VLM backbone](../../models/xiaomi-robotics-1/vlm-backbone.md) owns the model that adopts the recipe; [VLABench](../vlabench/README.md) owns the benchmark; [autoregressive modeling](../../foundations/learning-objectives/autoregressive-modeling.md) owns the next-token objective family; [evaluation methodology](../../foundations/data-and-evaluation/evaluation-methodology.md) owns comparison validity.

## Identity and revision boundary

| Field | Canonical value | Consequence |
|---|---|---|
| Work | *Revisiting Embodied Chain-of-Thought for Generalizable Robot Manipulation* (Sun, Zhang, Yang, Zhao, Li, Guo, Song, Ding, Suo, Su, Xiao, Li, Liu; Tsinghua, Xiaomi Robotics, PKU, CASIA, HKUST(GZ), ZJU, Fudan, WHU, SII); arXiv:2606.03784v1, 2026-06-02 | [ERV-PAPER] |
| Artifacts | "Code, data, and model checkpoints will be released" at the project page; none available on 2026-08-21 | The CoT corpus used on VLABench is not obtainable [ERV-PROJECT] |
| Relation to Xiaomi-Robotics-1 | Shared authors; XR-1 states it uses "CoT labeling as in ERVLA" with a 50 % next-token loss for VLABench | The labels themselves are unreleased by both [XR1-TR] |
| Comparison method | ACoT-VLA (CVPR 2026) | Public code; different CoT design [ERV-ACOT-CODE] |

## Operational model boundary

ERVLA is a VLA (Qwen3-VL-4B backbone + flow-matching DiT with a choice policy branch and "knowledge truncation" that limits the DiT to the semantic-prefix KV cache) trained on a 2,592-hour multi-source corpus (Bridge, Fractal, DROID, MolmoAct, AgiBot; 978,743 trajectories) with embodied CoT annotations, then evaluated on LIBERO-Plus and VLABench. Its CoT is consumed at training time with reasoning dropout; at inference the model acts without visible reasoning. [ERV-PAPER]

| Surface | Inputs | Outputs | Invalid projection |
|---|---|---|---|
| Training with CoT | images, instruction, `/cot` or `/no_cot` | action chunk (+ CoT tokens under `/cot`) | That inference reasoning is required |
| Inference | images, instruction, `/no_cot` | action chunk | A different base model's numbers |

## Knowledge map

| Question | Canonical page |
|---|---|
| Method, CoT taxonomy, ablations, results | [`paper.md`](paper.md) |
| Released implementation (none yet) and the closest public code | [`codebase.md`](codebase.md) |
| What has been executed locally | [`reproduction.md`](reproduction.md) |
| Transferable CoT interventions | [`optimization-transfer.md`](optimization-transfer.md) |
| Identities | [`sources.yaml`](sources.yaml) |

## High-value evidence anchors

- Grounded, action-oriented CoT helps; abstract fields alone can hurt: on VLABench with Bridge pre-training and dropout, movement +4.1, point trajectory +4.8, full ECoT +4.0 over a 25.2 baseline; removing bounding boxes +3.2. [ERV-PAPER, Table 1]
- Design ablation on LIBERO-Plus: full 86.9; without knowledge truncation 84.7; without the choice branch 83.8; without CoT 77.4; end-to-end without choice 70.8. [ERV-PAPER]
- VLABench 5-track SR/PS/IS 53.2 / 65.9 / 70.4 (in-dist 69.7, category 47.0, common 44.0, instruction 58.0, texture 47.4); pi0.5 48.1, ACoT-VLA 47.4, pi0-FAST 39.8. [ERV-PAPER, Table 4]
- Reasoning dropout: each sample is rendered `/cot` or `/no_cot` with probability `p_cot` (value not stated); the mechanism "enables test-time reasoning dropout". [ERV-PAPER]

## Sources

Resolve through [`sources.yaml`](sources.yaml).
