---
id: world-model-kb.papers.ervla.paper
title: ERVLA Method, Chain-of-Thought Taxonomy, and Evidence
kind: paper
status: maintained
last_updated: 2026-08-21
owners:
  - AIBuildAI world-model group
---

# ERVLA Method, Chain-of-Thought Taxonomy, and Evidence

## Retrieval metadata

**Relevant queries:** embodied CoT taxonomy, task understanding, spatial grounding, action-oriented guidance, motion description, bounding box hurts, point trajectory helps, reasoning dropout p_cot, knowledge truncation, choice policy branch, LIBERO-Plus perturbation tracks, VLABench Table 4, ablation.

**Knowledge provided:** the paper's question, the CoT content taxonomy and its ablation, the training scheme, architecture, data, benchmark results with per-track values, and evidence limits.

**Related pages:** [`README.md`](README.md) owns identity; [`optimization-transfer.md`](optimization-transfer.md) owns interventions; [Xiaomi-Robotics-1 VLM backbone](../../models/xiaomi-robotics-1/vlm-backbone.md) owns the adopting model; [autoregressive modeling](../../foundations/learning-objectives/autoregressive-modeling.md) owns the objective family.

## 1. Problem statement

Embodied chain-of-thought (ECoT) has been proposed to make VLAs reason before acting, but which reasoning content actually helps action generation, and whether reasoning must be produced at inference, were unresolved. The paper asks both questions with controlled ablations across CoT content types and a training scheme that decouples training-time reasoning supervision from inference-time generation. [ERV-PAPER, Sec. 1]

## 2. Method

### 2.1 CoT taxonomy

Four hierarchical categories of reasoning fields: task understanding and semantic reasoning (goal, planning, subtask), spatial grounding (bounding box, object identification), action-oriented guidance (end-effector movement, point trajectory, gripper position), and motion description. Annotations are produced automatically: detector-generated labels plus simulator replay to obtain grounded signals (object and gripper positions), extended to multi-view and bimanual settings. [ERV-PAPER, Sec. 3, Appendix B]

### 2.2 Reasoning dropout

Each training sample is rendered either as `/cot` (instruction followed by the reasoning text the model must predict) or `/no_cot` (no reasoning) with probability `p_cot`. The stated purposes: reduce reliance on visible reasoning, mitigate noisy CoT supervision, internalize reasoning into backbone states, and enable test-time reasoning dropout (acting without generating reasoning). The value of `p_cot` is not stated; Xiaomi-Robotics-1 reports using 50 %. [ERV-PAPER, Sec. 3; XR1-TR]

### 2.3 Architecture and objective

Qwen3-VL-4B backbone; a flow-matching DiT action head; a choice policy branch predicting N candidate chunks with a selection/score loss; "knowledge truncation" that restricts the DiT's access to the semantic-prefix KV cache; an auxiliary action-query regression. Loss: `L = lambda_vlm L_vlm + lambda_flow L_flow + lambda_choice L_choice + lambda_score L_score`. Training steps, batch, and GPUs are not given. [ERV-PAPER, Sec. 3]

### 2.4 Data

978,743 trajectories, 226.3M samples, 2,592.5 hours from Bridge, Fractal, DROID, MolmoAct, and AgiBot, annotated with ECoT. [ERV-PAPER, Sec. 4]

## 3. Results

### 3.1 CoT content ablation (VLABench, Bridge pre-training + dropout; Table 1)

Baseline 25.2; full ECoT +4.0; no movement -0.6 (relative to full); no point trajectory -0.9; no gripper -0.8; no bounding box +3.2. Separately: movement alone +4.1, point trajectory alone +4.8; high-level fields alone reduced performance; the full ECoT set reached +7.4 in another setting. The conclusion: "action-related CoT signals support action generation more directly than high-level understanding alone". [ERV-PAPER, Table 1]

### 3.2 Design ablation (LIBERO-Plus)

| Configuration | Total |
|---|---:|
| ERVLA (full) | 86.9 |
| choice + no knowledge truncation | 84.7 |
| no choice + knowledge insulation | 83.8 |
| no CoT | 77.4 |
| no choice (end-to-end) | 70.8 |

[ERV-PAPER]

### 3.3 Benchmarks

LIBERO-Plus total 86.9 (spatial 89.6, object 79.6, goal 82.1, long 77.2) versus pi0.5 85.5, OpenVLA-OFT 84.0, PokeVLA 79.4, pi0-FAST 74.4; perturbation tracks 75.3-95.1. VLABench 5-track SR/PS/IS 53.2 / 65.9 / 70.4; per track (SR/PS/IS): in-distribution 69.7/81.1/84.2; cross-category 47.0/61.0/66.4; common 44.0/55.0/57.2; instruction 58.0/70.2/73.8; texture 47.4/62.3/70.6. Baselines in the same table: pi0.5 48.1 (65.4/38.2/43.9/48.2/44.9), ACoT-VLA 47.4, pi0-FAST 39.8 (56.2/31.0/38.0/35.0/39.0). [ERV-PAPER, Table 4]

## 4. Evidence limits

- No explicit inference-time ablation (CoT generated vs dropped) with numbers; the claim that dropping reasoning at inference preserves gains is stated through the dropout mechanism, not a table.
- `p_cot`, training compute, and the annotation VLM are not stated.
- Xiaomi-Robotics-1's Table 4 agrees with ERVLA's for ERVLA, pi0.5, and pi0-FAST, which supports protocol consistency between the two reports but is not independent replication (shared authors). [XR1-TR]
- Corpus and checkpoints are unreleased; the VLABench CoT annotations cannot be reused.

## Sources

[ERV-PAPER] Sec. 1-4, Tables 1 and 4, design ablation; [ERV-PROJECT]; [ERV-ACOT-CODE]; [XR1-TR] Sec. 5.3.
