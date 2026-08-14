---
id: world-model-kb.papers.cosmos-policy.paper
title: Cosmos Policy Method, Architecture, and Experimental Evidence
kind: paper
status: maintained
last_updated: 2026-08-14
owners:
  - AIBuildAI world-model group
---

# Cosmos Policy Method, Architecture, and Experimental Evidence

## Retrieval metadata

**Relevant queries:** latent frame injection, Cosmos-Predict2-2B policy, EDM denoiser, joint policy world model value, auxiliary targets, best-of-N, majority mean, LIBERO 98.5, RoboCasa 67.1, ALOHA 93.6, Table 4 scratch ablation, Table 5 future-state ablation, or sigma_min 4.

**Knowledge provided:** the paper's problem, complete latent-sequence architecture, joint training mixture, planning protocol, benchmark protocols, numbered results bound to named checkpoints, ablations, latency, and evidence limits.

**Related pages:** [`README.md`](README.md) owns identity boundaries; [`codebase.md`](codebase.md) owns the Predict2 tree; [diffusion and flow matching](../../foundations/learning-objectives/diffusion-and-flow-matching.md) owns the EDM family; [planning and control](../../foundations/decision-making/planning-and-control.md) owns candidate ranking; [evaluation methodology](../../foundations/data-and-evaluation/evaluation-methodology.md) owns comparison validity.

## 1. Problem statement

### 1.1 Control task

Cosmos Policy is a **single-stage post-trained visuomotor policy**, not a new video-generation benchmark and not Cosmos-Predict2.5. Given current multi-view images, proprioception, and language, it samples an action chunk. Optionally it also samples a future observation and a scalar value so that test-time search can rank proposals. [P25-COSMOS-POLICY, Abstract, Sec. 1]

The intended generation order is the MDP tuple `(s, a, s', V(s'))`, where `s` and `s'` are observations at times `t` and `t+K`, `a` is a `K`-step action chunk, and `V(s')` is a Monte Carlo return from a sparse terminal reward in `[0, 1]`:

```text
V^pi(s) = E[ gamma^{H-t} R(s_H, a_H) | s_t = s ]
```

History beyond the current observation is not used. The model does not output a safety certificate or a receding-horizon plan. [P25-COSMOS-POLICY, Sec. 3, 4.1]

### 1.2 Design problem

Prior video-to-policy methods either add a second-stage action module or train a custom video-action architecture from scratch. Cosmos Policy asks whether Cosmos-Predict2-2B-Video2World can become a robot policy through one post-training stage on target-platform demonstrations, **with no new networks**. The hypothesis is that a pretrained latent video denoiser already models high-dimensional multimodal sequences, so actions, extra cameras, proprioception, and values can occupy latent frames rather than new heads. [P25-COSMOS-POLICY, Sec. 1-2]

## 2. Method and architecture

### 2.1 End-to-end data flow

Figure 2 of the paper can be reconstructed as:

```text
language -> T5-XXL embedding (cross-attention condition c)
multi-view RGB + proprioception
        |
   Wan2.1 spatiotemporal VAE on images only
   tile normalized [-1, +1] vectors into H' x W' x 16 volumes
        |
interleaved latent frames (two third-person + wrist example, 11 frames):
  placeholder, proprio_t, wrist_t, cam1_t, cam2_t,
  action_chunk, proprio_{t+K}, wrist_{t+K}, cam1_{t+K}, cam2_{t+K}, value
        |
EDM denoiser DiT D_theta (Cosmos-Predict2-2B)
  clean prefix / noisy targets per conditioning mask
        |
decode action chunk (direct policy)
optionally decode future images, future proprioception, and value (planning)
```

The VAE compresses `(1+T) x H x W x 3` to `(1+T/4) x H/8 x W/8 x 16`. A blank placeholder exists because of that temporal compression scheme. Sequence order is `(s, a, s', V(s'))` so actions, futures, and values can be generated left to right. A one-camera robot uses seven latent frames after dropping extra views. [P25-COSMOS-POLICY, Sec. 3-4.1, Fig. 2; Appendix A.1]

### 2.2 Pretrained objective reused without architecture change

The initialization is Cosmos-Predict2-2B-Video2World, trained with EDM denoising score matching:

```text
L(D_theta, sigma) = E || D_theta(x_0 + n; sigma, c) - x_0 ||_2^2
n ~ N(0, sigma^2 I)
```

`D_theta` conditions on T5-XXL text via cross-attention and on `sigma` via AdaLN. Cosmos Policy keeps this denoiser and tokenizer; it only changes which latent frames are present and which of them stay clean. [P25-COSMOS-POLICY, Sec. 3]

At sampling the paper raises the EDM floor from `sigma_min = 0.002` to `sigma_min = 4` (`sigma_max = 80`) because final near-zero-noise steps were less accurate for actions, futures, and values. Training also replaces the base log-normal noise schedule with a hybrid log-normal-uniform schedule that puts more mass on higher noise. [P25-COSMOS-POLICY, Appendix A.2.1, Fig. 9]

### 2.3 Joint training of policy, world model, and value

Each batch of `(s, a, s', V(s'))` tuples is split 50/25/25 by conditioning mask, not by extra networks:

- 50% demonstration data trains `p(a, s', V(s') | s)` (policy with auxiliary futures and values);
- 25% rollout data trains `p(s', V(s') | s, a)` (world model);
- 25% rollout data trains `p(V(s') | s, a, s')` (value).

Rollout data initially includes failed demonstrations when they exist (about 10-20% of LIBERO/RoboCasa replay failures). ALOHA teleoperation is treated as all-success, so demonstration and rollout sets start equal. Sparse terminal rewards are credited as Monte Carlo returns `gamma^{H-t} R_H`. [P25-COSMOS-POLICY, Sec. 4.2, Fig. 12]

Parallel decoding generates action, future, and value together and is used for **direct policy** evaluation. Autoregressive left-to-right decoding is used when planning needs higher-quality futures and values. Direct-policy execution discards future and value outputs. [P25-COSMOS-POLICY, Sec. 4.2; Appendix A.3.1]

### 2.4 Planning after rollout fine-tuning

Demonstration-only world models see mostly successes. The paper therefore collects on-policy and mixed-policy rollouts (505 evaluation rollouts plus 143 extra ziploc episodes, 648 total), then fine-tunes with 90% of each batch on world-model and value targets and 10% on the policy. Dual deployment keeps the original checkpoint as the proposal policy and the refined checkpoint as the planning model. [P25-COSMOS-POLICY, Sec. 4.3, 5.3]

Best-of-N: sample N action chunks from the policy model; for each proposal draw 3 world-model futures and 5 values per future (15 values); aggregate with **majority mean** (threshold success/failure, then average within the majority); execute the **full** selected chunk. Planning experiments use `N=8` on 8 H100s. Value masks at this stage choose `V(s')` (mask `(s,a)`) versus `Q(s,a)` (mask `s'`). [P25-COSMOS-POLICY, Sec. 4.3, 5.3; Appendix A.4.2]

## 3. Data and evaluation protocols

| Domain | Data | Chunk / rate | Protocol | Bound checkpoint |
|---|---|---|---|---|
| LIBERO Spatial/Object/Goal/Long | 50 demos/task; unsuccessful demos filtered for policy, kept for WM/value | 16-step chunk, full execution | 500 trials/suite, 3 seeds, 6000 trials | LIBERO-Predict2-2B |
| RoboCasa 24 kitchen tasks | 50 human demos/task only (not 1000 MimicGen) | 32-step chunk, execute 16 then re-query | 50 trials x 24 tasks x 3 seeds = 3600; unseen objects; 2/5 scenes unseen styles | RoboCasa-Predict2-2B |
| ALOHA four bimanual tasks | 80/15/45/45 demos; one policy on all 185; 25 Hz | 50-step / 2 s chunk, full execution | 101 matched initial states (30+20+25+26); ID and OOD splits in Table 3 | ALOHA-Predict2-2B plus optional planning model |

Training compute: 64xH100 48 h, 40K steps, global batch 1920 (LIBERO); 32xH100 48 h, 45K steps, batch 800 (RoboCasa); 8xH100 48 h, 50K steps, batch 200 (ALOHA). All non-image modalities are rescaled to `[-1, +1]`. Compared ALOHA VLAs receive the same 48 h / 8xH100 wall-clock budget but different step counts. [P25-COSMOS-POLICY, Sec. 5.1; Appendix A.2-A.3]

## 4. Direct-policy results

### 4.1 LIBERO

Cosmos Policy average success 98.5% over 6000 trials. UVA and Video Policy report Long-only cells (90.0 and 94.0) and must not be averaged with full-suite rows. [P25-COSMOS-POLICY, Table 1, Sec. 5.2]

| Method | Spatial | Object | Goal | Long | Average |
|---|---:|---:|---:|---:|---:|
| Diffusion Policy | 78.3 | 92.5 | 68.3 | 50.5 | 72.4 |
| Dita | 97.4 | 94.8 | 93.2 | 83.6 | 92.3 |
| π0 | 96.8 | 98.8 | 95.8 | 85.2 | 94.2 |
| UniVLA | 96.5 | 96.8 | 95.6 | 92.0 | 95.2 |
| π0.5 | 98.8 | 98.2 | 98.0 | 92.4 | 96.9 |
| OpenVLA-OFT | 97.6 | 98.4 | 97.9 | 94.5 | 97.1 |
| CogVLA | 98.6 | 98.8 | 96.6 | 95.4 | 97.4 |
| Cosmos Policy | 98.1 | 100.0 | 98.2 | 97.6 | 98.5 |

### 4.2 RoboCasa

Average success 67.1% with 50 demos/task versus comparators trained on 300 to 3000 demos (plus DreamGen synthetic 10k in one row). The 50-versus->300 demo gap is part of the claim. [P25-COSMOS-POLICY, Table 2, Sec. 5.2]

| Method | Demos/task | Average SR (%) |
|---|---:|---:|
| GR00T-N1 | 300 | 49.6 |
| UVA | 50 | 50.0 |
| DP-VLA | 3000 | 57.3 |
| GR00T-N1 + DreamGen | 300 + 10k synthetic | 57.6 |
| π0 | 300 | 62.5 |
| GR00T-N1.5 | 300 | 64.1 |
| Video Policy | 300 | 66.0 |
| FLARE | 300 | 66.4 |
| GR00T-N1.5 + HAMLET | 300 | 66.4 |
| Cosmos Policy | 50 | 67.1 |

### 4.3 ALOHA

Completion scores use staged rubrics (plate 50+50, shirt 10-point stages, five candies at 20 each, ziploc five 20-point stages). 101 matched initial states. Preserve the OOD reversal: π0.5 92.5 versus Cosmos Policy 89.3. [P25-COSMOS-POLICY, Fig. 4, Table 3, Sec. 5.2, Appendix A.3]

| Split | Method | Plate | Fold shirt | Candies | Ziploc | Average |
|---|---|---:|---:|---:|---:|---:|
| ID | Cosmos Policy | 100.0 | 99.2 | 100.0 | 86.0 | 96.3 |
| ID | π0.5 | 97.5 | 99.2 | 98.7 | 56.0 | 87.8 |
| OOD | Cosmos Policy | 100.0 | 100.0 | 74.0 | 83.3 | 89.3 |
| OOD | π0.5 | 100.0 | 100.0 | 90.0 | 80.0 | 92.5 |
| Full | Cosmos Policy | 100.0 | 99.5 | 89.6 | 85.4 | 93.6 |
| Full | π0.5 | 98.3 | 99.5 | 95.2 | 61.5 | 88.6 |
| Full | π0 | 85.0 | 98.5 | 71.2 | 56.9 | 77.9 |
| Full | OpenVLA-OFT+ | 68.3 | 99.5 | 21.6 | 58.5 | 62.0 |
| Full | Diffusion Policy | 63.3 | 23.5 | 32.8 | 14.6 | 33.6 |

## 5. Ablations

### 5.1 LIBERO auxiliary targets and pretraining (Table 4)

| Variant | Spatial | Object | Goal | Long | Average |
|---|---:|---:|---:|---:|---:|
| Full Cosmos Policy | 98.1 | 100.0 | 98.2 | 97.6 | 98.5 |
| w/o auxiliary losses | 97.6 | 99.8 | 96.7 | 94.0 | 97.0 |
| w/o pretrained model | 94.7 | 98.9 | 96.3 | 88.6 | 94.6 |

Removing auxiliary `s', V` targets costs 1.5 points. Training from scratch costs 3.9 points, concentrated on Long (97.6 -> 88.6). A from-scratch ALOHA fold-shirt score of 80.8 is 18.7 below the pretrained policy; the paper stops that variant after jerky motion. [P25-COSMOS-POLICY, Table 4, Sec. 5.2]

### 5.2 RoboCasa joint-objective peel-down (Table 5)

| Variant | Average SR (%) |
|---|---:|
| Full, 5 denoising steps | 67.1 |
| (1) no value-function training samples | 66.6 |
| (2) policy-only samples (no WM/value batches) | 64.0 |
| (3) plus no auxiliary value on policy samples | 62.5 |
| (4) policy predicts only `p(a|s)` | 44.4 |
| Full, 1 denoising step | 66.4 |

The largest drop is ablating future-state supervision on the policy (62.5 -> 44.4). One-step sampling retains 66.4% at 0.16 s/chunk versus 0.61 s at five steps on one H100. [P25-COSMOS-POLICY, Table 5, Appendix A.4.1-A.4.2]

### 5.3 Planning versus Q-search (Figure 7)

On two hard ALOHA tasks under harder initial states, model-based `V(s')` search adds a reported 12.5-point completion gain versus the base policy. The paper reports that `V(s')` outperforms `Q(s,a)` under the same limited rollout pool. Planning latency is 4.9 s for `N=8` on 8 H100s (10/5/5 denoising steps for action/future/value). [P25-COSMOS-POLICY, Fig. 6-7, Sec. 5.3, Sec. 6; Appendix A.4.2]

## 6. Image, noise, and sampling contracts

LIBERO training uses `flip_images=True` plus JPEG-style compression augmentation. Wrist and third-person RGB are encoded by Wan2.1; proprioception, actions, and values are tiled into `H' x W' x 16` volumes after `[-1, +1]` rescaling and are **not** VAE-encoded. [P25-COSMOS-POLICY, Appendix A.2-A.3; CPOL-CODE]

Sampling raises the EDM floor from `sigma_min = 0.002` to `sigma_min = 4` with `sigma_max = 80`. Direct-policy tables use **parallel** decoding: 5 denoising steps on LIBERO/RoboCasa and 10 on ALOHA. Planning uses **autoregressive** 10/5/5 steps for action/future/value. A README snippet that splits 5/1/1 steps is not Table 1 protocol. [P25-COSMOS-POLICY, Appendix A.2.1, A.3.1; CPOL-CODE]

## 7. Latency and VRAM (paper-documented)

| Mode | Hardware | Latency | Documented VRAM |
|---|---|---|---|
| Direct policy, 5 steps | 1x H100 | 0.61 s/chunk | 6.8 GB LIBERO; 8.9 GB RoboCasa; 6.0 GB ALOHA |
| Direct policy, 10 steps | 1x H100 | 0.95 s/chunk | same family |
| Direct policy, 1 step | 1x H100 | 0.16 s/chunk; RoboCasa 66.4% | same family |
| Planning `N=8` | 8x H100 | 4.9 s | 10.0 GB serial or N GPUs parallel |

These numbers are paper/README measurements, not local runs. One-step 66.4% is an ablation, not a substitute for the 5-step 67.1% table identity. [P25-COSMOS-POLICY, Appendix A.4.2; CPOL-CODE]

## 8. Related-method boundary

Cosmos Policy is not a second-stage action head on frozen video features, not π0/π0.5 as a VLA architecture, and not Cosmos-Predict2.5 video generation. Video Policy and UVA report Long-only LIBERO cells and must not be averaged into full-suite rows. Policy-DROID on Cosmos3-Nano is a later product with a different backbone and protocol. [P25-COSMOS-POLICY, Tables 1-3]

## 9. Limits

- “No architectural modification” still changes the token layout and requires full-backbone post-training; it is not zero-cost reuse.
- Table 1-2 “SOTA” cells are protocol-bound: LIBERO 6000 trials, RoboCasa 50-demo training versus comparators with 300-3000 demos, ALOHA 101 private initial states. Demo counts and OOD splits are not optional metadata.
- Table 3 OOD reverses the full-split ranking: π0.5 92.5 versus Cosmos Policy 89.3. Do not convert 93.6 into universal OOD superiority.
- Best-of-N executes the full chunk, not receding horizon, and multiplies GPU count with N.
- Values are Monte Carlo returns from sparse task scores in `[0, 1]`, not calibrated physical rewards.
- Predict2.5 Cookbook recipes, if any, are out of scope for Tables 1-5.
- Cosmos3-Nano Policy-DROID is a different product and must not inherit 98.5% / 67.1% / 93.6%.
- ALOHA hardware identity is private; public code cannot reconstruct Table 3 without the matched robot and 101-state protocol.

## Sources

[P25-COSMOS-POLICY] owns paper claims. [CPOL-CODE] owns released commands, configs, and documented VRAM.
