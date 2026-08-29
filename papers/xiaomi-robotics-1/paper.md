---
id: world-model-kb.papers.xiaomi-robotics-1.paper
title: Xiaomi-Robotics-1 Method, Architecture, and Experimental Evidence
kind: paper
status: maintained
last_updated: 2026-08-21
owners:
  - AIBuildAI world-model group
---

# Xiaomi-Robotics-1 Method, Architecture, and Experimental Evidence

## Retrieval metadata

**Relevant queries:** UMI pre-training, Qwen3.5-27B auto-labeling, scene-transition caption, L_Flow, L_Regression, L_NTP 0.1, Beta(1.5, 1), post-training ratio 0.5:0.5:0.5:8.5, Bridge V2 RT-1 DROID, scaling curve, Table 2 RoboCasa, Table 3 RoboCasa365, Table 4 VLABench, Table 5 RoboDojo, Table 6 real-robot.

**Knowledge provided:** the report's problem statement, architecture and data flow, objectives, data pipeline, post-training alignment, benchmark protocols and numbers, scaling evidence, and the evidence limits.

**Related pages:** [`README.md`](README.md) owns identity; [`codebase.md`](codebase.md) owns the released tree; [model architecture](../../models/xiaomi-robotics-1/architecture.md) owns the computation details of the released 5B; [diffusion and flow matching](../../foundations/learning-objectives/diffusion-and-flow-matching.md) owns the objective family; [evaluation methodology](../../foundations/data-and-evaluation/evaluation-methodology.md) owns comparison validity.

## 1. Problem statement

Robot policy models are data-bound: teleoperated robot data is expensive and embodiment-specific. The report asks whether large-scale **embodiment-free** trajectories collected with hand-held UMI grippers, auto-labelled by a VLM, can serve as a pre-training corpus whose benefits transfer through post-training to real robots and benchmarks, and whether that transfer scales with data and model size. [XR1-TR, Sec. 1]

## 2. Method and architecture

### 2.1 End-to-end data flow

```text
three camera images + instruction (+ state token)
   -> Qwen3-VL VLM (28-36 layers) -> per-layer KV cache
   -> DiT (same layer count, hidden 1024/2048) attends to the cache
   -> flow-matching velocity over an action chunk (60-D slots)
   -> 5-step Euler sampling at inference
```

Table 1: 2B (28 layers, VLM 2.1B, DiT 470M), 5B (36, 4.4B, 604M), 10B (36, 8.8B, 1.5B). The DiT "matches the VLM in the number of layers but employs a smaller hidden size for faster inference". Excluding action tokens from the DiT's attention improved performance (stated qualitatively). [XR1-TR, Sec. 3, Table 1]

### 2.2 Objectives

- Flow matching `L_Flow = || v_theta(...) - u(..., tau) ||^2` with `u ~ Beta(1.5, 1)`, `tau = (1 - u) * 0.999`.
- Regression on a best-of-K candidate branch `L_Regression = || a*_{t:t+H} - a_{t:t+H} ||_1 + sum_k || s_k - s_k_hat ||^2` (candidate chunks plus their scores).
- Vision-language next-token prediction `L_NTP`, weight 0.1, on vision-language data. [XR1-TR, Sec. 3]

### 2.3 Asynchronous execution

Training for asynchronous inference follows Xiaomi-Robotics-0: the model conditions on a prefix of already-executed actions so that chunk boundaries align in time during real-time rollouts. Details beyond the citation are not restated. [XR1-TR; XR0-TR]

## 3. Data

### 3.1 Pre-training corpus

>100K h of UMI trajectories across 1,700+ scenarios (households, commercial premises, industrial sites, offices, outdoor). Each trajectory is split into equal-length segments; Qwen3.5-27B captions "the state transitions of both the grippers and the interacting objects in the scene"; the full corpus was labelled in about two weeks with a producer-consumer pipeline. The model learns to generate actions that take the scene from its current state to the described target state. [XR1-TR, Sec. 4]

### 3.2 Post-training mixture

~10K h: > 7,200 h in-house mobile-manipulator and dual-arm data, > 1,000 h human-annotated UMI, plus Bridge V2, RT-1, DROID; sampling ratio vision-language : open-source : UMI : in-house = 0.5 : 0.5 : 0.5 : 8.5. Embodiment alignment unifies arm actions as relative delta end-effector poses with aligned frame orientations; instruction alignment shifts supervision to imperative instructions. [XR1-TR, Sec. 4]

## 4. Experiments

### 4.1 Simulation benchmarks (per-benchmark fine-tunes)

| Benchmark | Data used | XR-1 | Second best | Table |
|---|---|---:|---:|---|
| RoboCasa (24 kitchen tasks) | official 300 synthetic demos | 74.5 | 72.6 | 2 |
| RoboCasa365 (365 tasks, 2,500+ scenes) | 100 demos per task | 57.4 (80.2 atomic / 57.1 composite-seen / 32.1 composite-unseen) | 46.6 | 3 |
| VLABench (10 tasks x 500, 5 tracks x 50 episodes) | official Track-1 set; CoT labelling as in ERVLA at 50 % NTP | 59.1 SR / 70.3 PS / 69.9 IS | ERVLA 53.2 | 4 |
| RoboDojo (42+ tasks) | 3,500 official samples | 20.07 score / 13.93 % SR | 13.07 / 8.80 % | 5 |

VLABench per track (SR/PS/IS): in-distribution 75.6/85.0/79.8; cross-category 53.0/66.6/66.4; commonsense 48.4/58.3/58.2; instruction 55.8/66.8/70.2; texture 62.6/74.9/74.8. [XR1-TR, Tables 2-5]

Disclosed recipes (maintainers, not the report): RoboCasa365 120k steps, global batch 512, peak lr 3e-5, 4-frame history, 16-step 12-D chunks; RoboDojo 60k steps, batch 256, lr 1e-5, no history. VLABench and RoboCasa recipes are undisclosed. [XR1-ISSUE-4]

### 4.2 Real-robot evaluation

Out-of-the-box tasks (shoe storage, bag packing, table organization, sofa tidying) in unseen environments; adaptation with < 10 h per task on phone packing, printer refilling, laundry loading, box packing: XR-1 75 % success / 90 % progress versus pi0.5 40 % / 66 %; with < 40 h, 85 % vs 53 %. Robot platforms are in-house mobile manipulators and dual-arm robots. [XR1-TR, Sec. 5.5, Table 6]

### 4.3 Scaling

Validation action MSE on held-out data decreases with pre-training data fraction (12.5/25/50/100 % of ~20K h; "doubling the data from 50 % to 100 % yields an additional 6 percentage point improvement") and with model size (2B -> 5B -> 10B); "no sign of saturation". [XR1-TR, Sec. 6]

## 5. Evidence limits

- No ablation tables (choice branch, frequency loss, async prefix, CoT, NTP weight).
- No pre-training compute, no fine-tune hyperparameters for VLABench/RoboCasa.
- Scaling is measured in open-loop MSE; the link to closed-loop success is asserted through the benchmark tables, not measured per scaling point.
- Benchmark baselines were run by the authors under their protocol; Table 4's ERVLA/pi0.5/pi0-FAST numbers match ERVLA's own report for ERVLA and pi0.5 (53.2, 48.1) and pi0-FAST (39.8), which supports protocol agreement between the two papers. [XR1-TR; ERV-PAPER]
- "2,500 rollouts" is prose; the released track files execute 2,460. [XR1-TR; VLAB-CODE]

## Sources

[XR1-TR] Abstract, Sec. 1-6, Tables 1-6; [XR1-ISSUE-4]; [XR0-TR]; [ERV-PAPER]; [VLAB-CODE].
