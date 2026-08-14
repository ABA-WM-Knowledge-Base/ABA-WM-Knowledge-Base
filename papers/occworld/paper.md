---
id: world-model-kb.papers.occworld.paper
title: OccWorld Method, Architecture, and Experimental Evidence
kind: paper
status: maintained
last_updated: 2026-08-14
owners:
  - AIBuildAI world-model group
---

# OccWorld Method, Architecture, and Experimental Evidence

## Retrieval metadata

**Relevant queries:** OccWorld VQ-VAE occupancy, PlanU transformer, nuScenes forecasting, OccWorld-O vs D/T/S, tokenizer 50^2 128 512, Table 1 mIoU, planning L2 collision, spatial temporal ablation, or ECCV 2024.

**Knowledge provided:** the paper's problem formulation, complete occupancy-token architecture, data and training protocol, forecasting and planning tables bound to named variants, ablations with numbers, and the limits of each claim.

**Related pages:** [3D and 4D world models](../../foundations/representations/3d-and-4d-world-model.md) owns geometric forecasting; [latent world models](../../foundations/representations/latent-world-model.md) owns VQ tokenization; [autoregressive modeling](../../foundations/learning-objectives/autoregressive-modeling.md) owns GPT-style sequence modeling; [datasets and supervision](../../foundations/data-and-evaluation/datasets-and-supervision.md) owns occupancy labels; [evaluation methodology](../../foundations/data-and-evaluation/evaluation-methodology.md) owns evidence-layer distinctions.

Foundation bibliographic identity: [REP-OCCWORLD-2024].

## 1. Problem statement

### 1.1 Joint occupancy and ego-motion prediction

OccWorld is a **geometric** world model for driving, not a pixel video generator. Given a short history of semantic 3D occupancy, it forecasts future occupancy and the ego trajectory:

```text
O[t+1:t+T_fut], tau[t+1:t+T_fut] = f(O[t-T_hist+1:t])
```

The paper protocol uses **2 s of history → 3 s of future**. Occupancy volumes are semantic voxel grids (nuScenes / Occ3D classes). The ego head predicts multimodal relative waypoints. The model does not output RGB, instance tracks, or an HD-map raster as a required input of the OccWorld-O variant. [OCCSRC-PAPER, Sec. 1-3, Tables 1-2]

### 1.2 Supervision axis and named variants

Variants differ by **which geometric observation** is available at inference. They are not interchangeable rows:

| Name | Observation at the world-model input | Aux instance / HD-map labels |
|---|---|---|
| **OccWorld-O** | **3D occupancy GT** (Occ3D) | none beyond occupancy + ego motion |
| **OccWorld-D** | camera + 3D occupancy | occupancy still present |
| **OccWorld-T** | camera + semantic LiDAR | weaker geometry than O |
| **OccWorld-S** | camera only | none |

**OccWorld-O is occupancy-supervised, not “no labels at all.”** It removes instance segmentation and HD-map supervision relative to UniAD-class stacks; it still needs Occ3D occupancy ground truth. OccWorld-S is the camera-only extreme and is near Copy&Paste on occupancy IoU. [OCCSRC-PAPER, Tables 1-2]

## 2. Method and architecture

### 2.1 End-to-end data flow

```text
semantic occupancy clip O  [B, F, H, W, D]
        |
   2-D VQ-VAE encoder (spatial downsample 4)
        |
   latent z  [B*F, 128, 50, 50]     # default (50^2, 128, 512)
        |
   VectorQuantizer  codebook 512 x 128-d
        |
   discrete tokens  (spatial 50 x 50 per frame)
        |
   PlanUAutoRegTransformer
        |-- spatial attention over the 50x50 token map
        |-- temporal attention across frames
        |-- pose tokens from PoseEncoder (rel_poses || gt_mode)
        |
   future token logits (512-way) + pose features
        |
   codebook lookup -> VQ decoder -> future occupancy logits
   PoseDecoder -> multimodal ego waypoints  [B, T, 3, 2]
```

Only future tokens are supervised with cross-entropy against encoder-quantized labels. Ego waypoints are supervised with an L2 planning regression loss. [`codebase.md`](codebase.md) owns `TransVQVAE` branch names. [OCCSRC-PAPER, Sec. 3; OCCSRC-CODE-CURRENT, `model/TransVQVAE.py`, `config/train_occworld.py`]

### 2.2 Occupancy tokenizer (VQ-VAE)

A 2-D residual encoder (`VAERes2D` / `vae_2d_resnet.py`) compresses each occupancy frame with **downsample 4**, producing a **50×50** latent for a **200×200** BEV layout. The quantizer (`model/VAE/quantizer.py`) uses:

```text
n_e = 512 codebook entries
e_dim = 128
beta = 1.0   # commitment
```

Default tokenizer setting in the paper is **(50², 128, 512)** — spatial tokens, embedding width, codebook size. Reconstruction is a means to a discrete sequence, not the final product. Stage-1 losses are reconstruction CE, Lovasz, and VQ embedding loss. [OCCSRC-PAPER, Sec. 3, Table 3; OCCSRC-CODE-CURRENT, `config/train_vqvae.py`]

### 2.3 Spatial-temporal transformer and ego tokens

`PlanUAutoRegTransformer` (`model/transformer/PlanUtransformer.py`) attends spatially inside each token map and temporally across the 2 s history. A `PoseEncoder` (`in_channels=5`: relative XY plus 3-way mode) injects ego tokens; a `PoseDecoder` emits **3 motion modes**. Removing spatial attention, temporal attention, or ego-temporal pose tokens is Table 4. [OCCSRC-PAPER, Table 4; OCCSRC-CODE-CURRENT]

Autoregressive inference (`forward_autoreg_with_pose`) feeds predicted tokens and decoded poses back for the 3 s future. Training is closer to teacher-forcing next-token CE on the offset future frames. [OCCSRC-CODE-CURRENT, `TransVQVAE`]

### 2.4 Training recipe

Two stages, both AdamW **1e-3**, weight decay **0.01**, batch **1 per GPU**, **8× RTX 4090** in the paper: [OCCSRC-PAPER, Sec. 4; OCCSRC-CODE-CURRENT]

1. **Tokenizer:** `config/train_vqvae.py`, recon + Lovasz + embed, `return_len_=10`.
2. **World model:** `config/train_occworld.py`, freeze VAE, train transformer + pose encoder/decoder, CE weight 1.0 + `PlanRegLossLidar` weight 0.1, `return_len_=15`, `offset=1`, load `out/vqvae/epoch_125.pth`.

## 3. Experimental setup

### 3.1 Data

| Resource | Role |
|---|---|
| nuScenes | licensed driving sequences [OCCSRC-NUSCENES] |
| Occ3D occupancy GT | voxel semantics for OccWorld-O / D |
| Tsinghua temporal pickle files | `nuscenes_infos_{train,val}_temporal_v3_scene.pkl` |

Casual eval without a nuScenes license is blocked. Occupancy GT quality caps OccWorld-O; that is still a labeling pipeline. [OCCSRC-PAPER; OCCSRC-NUSCENES]

### 3.2 Metrics

Forecasting: semantic **mIoU** and binary **IoU**, averaged over 1–3 s, plus per-horizon (1 s / 3 s). Planning: trajectory **L2** (m) and **collision** rate, averaged and at 1/2/3 s, STP3-style (`eval_metric_stp3.py`). FPS is reported on the paper's 4090 setup. [OCCSRC-PAPER, Tables 1-2]

### 3.3 Baselines

Copy&Paste (repeat last occupancy) is the geometric lower bound. UniAD is a heavily supervised planning baseline (instance, map, and related aux labels). OccWorld-O is compared as **occupancy-only** supervision, not as an unsupervised method. [OCCSRC-PAPER, Tables 1-2]

## 4. Results

### 4.1 Occupancy forecasting (Table 1, mIoU / IoU averaged 1–3 s)

| Method | mIoU | IoU | FPS | Notes |
|---|---:|---:|---:|---|
| Copy&Paste | 11.33 | 20.52 | — | last-frame repeat |
| **OccWorld-O** (3D-Occ, no aux) | **17.14** | **26.63** | **18.0** | 1 s mIoU **25.78**, 3 s **10.51** |
| OccWorld-D (camera+3D-Occ) | 8.62 | 16.53 | 2.8 | slower, weaker than O |
| OccWorld-T (camera+semantic LiDAR) | 3.56 | 8.34 | — | geometry degraded |
| OccWorld-S (camera, none) | 0.26 | 5.00 | — | near floor |

OccWorld-O is the only variant that clearly beats Copy&Paste on mIoU. Camera-only OccWorld-S does **not** instantiate an occupancy world model in any useful sense. Horizon decay is severe: 25.78 at 1 s → 10.51 at 3 s. [OCCSRC-PAPER, Table 1]

### 4.2 Planning (Table 2)

| Method | L2 avg (m) | Collision avg | Extra |
|---|---:|---:|---|
| UniAD | 1.03 | 0.31 | lots of aux labels |
| **OccWorld-O** | **1.17** | **0.60** | FPS **18**; L2 **0.43 / 1.08 / 1.99** at 1/2/3 s; collision **0.07 / 0.38 / 1.35** |
| OccWorld-O dagger (VAD metric) | 0.64 | 0.24 | different metric protocol |
| OccWorld-S | 1.83 | 2.02 | camera-only |

OccWorld-O approaches UniAD L2 without instance/HD-map heads, with higher collision (0.60 vs 0.31) and much higher FPS than camera-heavy stacks. OccWorld-S planning is not competitive. Dagger numbers use the VAD metric and must not be mixed into the STP3 row. [OCCSRC-PAPER, Table 2]

### 4.3 Tokenizer (Table 3)

| Setting | Reconstruction mIoU / IoU | Forecast avg mIoU | Planning L2 avg | FPS |
|---|---:|---:|---:|---:|
| Default **(50², 128, 512)** | **66.38 / 62.29** | **17.14** | **1.17** | 18.0 |
| **(50², 128, 256)** | 63.40 / 60.33 | 16.24 | 1.15 | 17.8 |
| **(50², 128, 1024)** | 60.50 / 59.07 | 16.30 | 1.28 | 17.8 |
| **(25², 256, 512)** | 36.28 / 44.02 | 8.81 | 6.53 | 28.1 |
| **(100², 128, 512)** | **78.12 / 71.63** | **12.38** | 1.36 | 6.7 |
| **(50², 64, 512)** | 64.98 / 61.50 | 14.67 | 1.33 | 20.1 |

Higher reconstruction can **hurt** forecasting: a 100² tokenizer overfits low-level tokens. Larger codebooks (1024) similarly overfit. The world-model objective is next-token forecast, not recon IoU. [OCCSRC-PAPER, Table 3]

### 4.4 Attention / ego ablations (Table 4)

| Ablation | Forecast mIoU | Planning |
|---|---:|---|
| w/o spatial attention | **10.07** | — |
| w/o temporal attention | **8.98** | — |
| w/o ego temporal | — | L2 **5.89**, collision **6.23** |

Spatial and temporal occupancy attention both matter for forecast (10.07 and 8.98 vs 17.14). Removing ego-temporal pose tokens collapses planning (L2 5.89 vs 1.17). [OCCSRC-PAPER, Table 4]

### 4.5 Copy&Paste, empty class, and FPS

Copy&Paste (repeat last occupancy) is the geometric floor: mIoU 11.33 / IoU 20.52. The released `without_all` flag implements a related last-frame/last-pose repeat and must be logged if enabled. Semantic IoU treats class **17** as empty in `TransVQVAE` (`pred_iou`). OccWorld-O FPS **18.0** versus OccWorld-D **2.8** shows that camera lifting, not the transformer, dominates latency when occupancy GT is withheld. [OCCSRC-PAPER, Table 1; OCCSRC-CODE-CURRENT, `model/TransVQVAE.py`]

Training is two-stage on **8× RTX 4090**, batch **1/GPU**, AdamW **1e-3**, weight decay **0.01**. Stage-1 tokenizer uses recon CE, Lovasz, and VQ embed loss. Stage-2 freezes the VAE and adds token CE (weight 1.0) plus `PlanRegLossLidar` (weight 0.1) on three ego modes. History is **2 s**, future **3 s**, `offset=1`. [OCCSRC-PAPER, Sec. 4; OCCSRC-CODE-CURRENT, `config/train_vqvae.py`, `config/train_occworld.py`]

## 5. Limits and evidence boundaries

- **Occupancy GT is still a label.** OccWorld-O is not unsupervised; it is map/instance-light. [OCCSRC-PAPER, Tables 1-2]
- **Named variants are not a menu.** Do not cite OccWorld-O numbers for OccWorld-S or D. [OCCSRC-PAPER, Table 1]
- **Horizon decay:** 3 s mIoU 10.51 is below the 1 s 25.78; Copy&Paste is 11.33 average. Long-horizon occupancy remains open. [OCCSRC-PAPER, Table 1]
- **Collision vs UniAD:** 0.60 vs 0.31 average; 3 s collision 1.35. Geometric forecast does not equal safe planning. [OCCSRC-PAPER, Table 2]
- **nuScenes license** plus Occ3D plus Tsinghua pickles block casual metric runs. [OCCSRC-NUSCENES]
- **No RGB.** Appearance, traffic-light color, and texture are out of scope.
- **nuScenes-centric.** Other cities/sensors need new occupancy GT.
- **Dagger / VAD** metrics are a different protocol from STP3 Table 2.
- **High recon ≠ better WM** (Table 3). Do not tune codebook size on reconstruction alone.
- **Cosmos3:** occupancy is an auxiliary geometric head **parallel to** Generator FD/WAM, not a pixel replacement. [`optimization-transfer.md`](optimization-transfer.md)
- **Released demo spelling:** `visualize_demo.py` at `1ee7f77e…`; historical docs may still say `visulize_demo.py`. [OCCSRC-CODE-CURRENT]

These limits narrow the evidence; they do not negate OccWorld-O’s 17.14 mIoU or 18 FPS. [`reproduction.md`](reproduction.md) owns executed-state claims.

## Sources

- [OCCSRC-PAPER] Zheng et al., ECCV 2024 / arXiv:2311.16038.
- [OCCSRC-CODE-CURRENT] public implementation at the pinned commit.
- [OCCSRC-NUSCENES] nuScenes license and dataset terms.
- [REP-OCCWORLD-2024] Foundation identity (not re-registered in this entry's `sources.yaml`).
