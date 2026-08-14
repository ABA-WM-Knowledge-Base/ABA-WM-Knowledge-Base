---
id: world-model-kb.papers.occworld
title: OccWorld Paper Knowledge Entry
kind: paper
status: maintained
last_updated: 2026-08-14
owners:
  - AIBuildAI world-model group
---

# OccWorld Paper Knowledge Entry

## Retrieval metadata

**Relevant queries:** OccWorld, 3D occupancy world model, OccWorld-O, VQ-VAE (50^2, 128, 512), PlanU transformer, nuScenes planning, ego trajectory, HD-map-free occupancy GT, or geometric 4D WM.

**Knowledge provided:** ECCV 2024 identity, occupancy-token forecasting plus joint ego-trajectory prediction, named-variant evidence (O/D/T/S), license constraints, reproduction state, and falsifiable transfers toward a Cosmos3-Nano occupancy head **parallel to** Generator FD/WAM — not pixel replacement.

**Related pages:** [3D and 4D world models](../../foundations/representations/3d-and-4d-world-model.md); [latent world models](../../foundations/representations/latent-world-model.md); [autoregressive modeling](../../foundations/learning-objectives/autoregressive-modeling.md); [planning and control](../../foundations/decision-making/planning-and-control.md); [Cosmos3-Nano generator](../../models/cosmos3-nano/generator.md); [action modeling](../../models/cosmos3-nano/action-modeling.md).

Foundation registry [REP-OCCWORLD-2024](../../foundations/representations/3d-and-4d-world-model.md) owns the cross-entry source identity — this paper entry does not duplicate that registration. [OCCSRC-PAPER]

## Identity and revision boundary

| Field | Canonical value | Consequence |
|---|---|---|
| Work | *OccWorld: Learning a 3D Occupancy World Model for Autonomous Driving* | ECCV 2024 is the scientific anchor. |
| Venue | ECCV 2024; `arXiv:2311.16038` | Forecasting and planning metrics bind here. [OCCSRC-PAPER] |
| Official code | `wzzheng/OccWorld@1ee7f77ecc4c984a4f7f6411d95c2e6e73806b6e` | Pin dated **2024-04-12**. [OCCSRC-CODE-CURRENT] |
| Demo filename | `visualize_demo.py` at this commit | Historical README typo `visulize_demo.py`. |
| Dataset license | nuScenes + Occ3D GT + Tsinghua pickles | Casual local eval blocked. [OCCSRC-NUSCENES] |

## Operational model boundary

OccWorld tokenizes **semantic 3D occupancy** with a VQ-VAE and forecasts future tokens plus ego waypoints with a spatial-temporal transformer. Default tokenizer **(50², 128, 512)**, downsample 4, **2 s history → 3 s future**.

```text
past occupancy -> VQ tokens (50 x 50 x 512-way)
PlanU transformer + pose tokens -> future occupancy + ego modes
decode -> 3D occupancy for STP3 L2 / collision
```

**OccWorld-O uses occupancy GT.** It drops instance/HD-map aux relative to UniAD; it is not unlabeled. OccWorld-S is camera-only and is not an occupancy WM. [OCCSRC-PAPER, Tables 1-2]

| Surface | Inputs | Output | Evidence boundary |
|---|---|---|---|
| Tokenizer | occupancy volumes | discrete 50×50 tokens | recon is not the selection metric (Table 3) |
| OccWorld-O | 3D-Occ GT, no instance/map aux | forecast + plan | Table 1 17.14 mIoU; Table 2 L2 1.17 col 0.60 FPS 18 |
| OccWorld-D | camera + 3D-Occ | same heads | 8.62 / 16.53 FPS 2.8 |
| OccWorld-T | camera + semantic LiDAR | same heads | 3.56 / 8.34 |
| OccWorld-S | camera, none | same heads | 0.26 / 5.00; plan 1.83 / 2.02 |
| STP3 eval | licensed val split | L2, collision 1/2/3 s | not the VAD/dagger row |

Cosmos3 attachment: occupancy as a **parallel geometric head** beside Generator FD/WAM, not a pixel replacement.

## Documented commands (not executed)

```bash
python train.py --py-config config/train_vqvae.py --work-dir out/vqvae
python train.py --py-config config/train_occworld.py --work-dir out/occworld
python eval_metric_stp3.py --py-config config/occworld.py --work-dir out/occworld
python visualize_demo.py --py-config config/train_occworld.py --work-dir out/occworld
```

Real files at the pin include `model/TransVQVAE.py`, `model/VAE/{quantizer,vae_2d_resnet}.py`, `model/transformer/{PlanUtransformer,pose_encoder,pose_decoder}.py`, `loss/{ce_loss,emb_loss,recon_loss,plan_reg_loss_lidar}.py`, `dataset/dataset.py`, and `environment.yaml`. Do not invoke historical `visulize_demo.py` or `tools/train.py`. [`codebase.md`](codebase.md); [`reproduction.md`](reproduction.md)

## Knowledge map

| Question | Canonical page |
|---|---|
| Problem, architecture, tables, ablations, limits? | [`paper.md`](paper.md) |
| Pinned files, tensor contracts, code gaps? | [`codebase.md`](codebase.md) |
| Execution state and license boundary? | [`reproduction.md`](reproduction.md) |
| Geometric transfers to Cosmos3 Generator? | [`optimization-transfer.md`](optimization-transfer.md) |
| Source identities? | [`sources.yaml`](sources.yaml) |

## High-value evidence anchors

- **Table 1 forecasting (mIoU/IoU avg 1–3 s):** Copy&Paste 11.33/20.52; OccWorld-O **17.14/26.63 FPS 18.0** (1 s mIoU **25.78**, 3 s **10.51**); OccWorld-D 8.62/16.53 FPS 2.8; OccWorld-T 3.56/8.34; OccWorld-S 0.26/5.00. [OCCSRC-PAPER, Table 1]
- **Table 2 planning:** UniAD 1.03/0.31 (heavy aux); OccWorld-O **1.17/0.60 FPS 18**, L2 **0.43/1.08/1.99**, col **0.07/0.38/1.35**; dagger/VAD **0.64/0.24** (other protocol); OccWorld-S 1.83/2.02. [OCCSRC-PAPER, Table 2]
- **Table 3 tokenizer:** (100²,128,512) recon mIoU **78.12** but forecast **12.38** < **17.14**; codebook 1024 overfits. [OCCSRC-PAPER, Table 3]
- **Table 4:** w/o spatial forecast mIoU **10.07**; w/o temporal **8.98**; w/o ego temporal plan L2 **5.89** col **6.23**. [OCCSRC-PAPER, Table 4]
- **Recipe:** 8× RTX 4090, batch 1/GPU, AdamW 1e-3, wd 0.01; two-stage `train_vqvae` then `train_occworld`. [OCCSRC-PAPER, Sec. 4; OCCSRC-CODE-CURRENT]
- **License gate:** nuScenes + Occ3D + pickles. [`reproduction.md`](reproduction.md)
- **Code gaps:** `visulize_demo.py` typo; `generate_inference` debugger; `forward_autoreg` is `pass`. [`codebase.md`](codebase.md)
- **Execution:** all training and inference **not attempted**.

## Limits that change retrieval

- **OccWorld-O is occupancy GT**, not an unlabeled method. OccWorld-S (camera, none) is mIoU **0.26** and is a negative control. [OCCSRC-PAPER, Table 1]
- Do not mix STP3 Table 2 (L2 1.17 / col 0.60) with dagger/VAD **0.64 / 0.24**. [OCCSRC-PAPER, Table 2]
- Tokenizer recon mIoU **78.12** at 100² is **not** a world-model win: forecast drops to **12.38**. [OCCSRC-PAPER, Table 3]
- 3 s occupancy mIoU **10.51** is near Copy&Paste **11.33** average; long-horizon layout remains open. [OCCSRC-PAPER, Table 1]
- Cosmos3 attachment is a **parallel occupancy head** beside Generator FD/WAM, not voxel-for-pixel replacement. [`optimization-transfer.md`](optimization-transfer.md)
- nuScenes license + Occ3D + Tsinghua pickles block casual eval. [`reproduction.md`](reproduction.md)
- Default tokenizer **(50², 128, 512)**, downsample 4, class **17** empty for IoU, `without_all` is Copy&Paste-like. [`codebase.md`](codebase.md)
- Transfers: `OCCW-XFER-01`..`10` on a parallel occupancy head; never voxel-for-pixel Generator replacement. [`optimization-transfer.md`](optimization-transfer.md)
- Paper compute is **8× RTX 4090**, batch 1/GPU; FPS 18.0 (O) vs 2.8 (D) is a 4090-class number, not a laptop measurement. [OCCSRC-PAPER, Tables 1-2]

## What this entry is not

It is not a nuScenes redistribution, not an OccWorld-S-as-O scorecard, not a Generator pixel replacement recipe, and not an executed metric run. Occupancy GT, license, and named variants are first-class retrieval constraints.

## Sources

[`sources.yaml`](sources.yaml). Cross-entry registration: [REP-OCCWORLD-2024](../../foundations/representations/3d-and-4d-world-model.md).
