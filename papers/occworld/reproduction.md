---
id: world-model-kb.papers.occworld.reproduction
title: OccWorld Reproduction State and Experiment Contracts
kind: record
status: maintained
last_updated: 2026-08-14
owners:
  - AIBuildAI world-model group
---

# OccWorld Reproduction State and Experiment Contracts

## Retrieval metadata

**Relevant queries:** OccWorld reproduced, nuScenes license, train_vqvae, train_occworld, eval_metric_stp3, visualize_demo, OccWorld-O, Occ3D, Tsinghua pickle, or acceptance criteria.

**Knowledge provided:** all-not-attempted execution state, license boundary, documented commands bound to real repo files, and acceptance contracts. No training or inference was run for this entry.

**Related pages:** [`codebase.md`](codebase.md) owns the released call graph and gaps; [`paper.md`](paper.md) owns reported values; [datasets and supervision](../../foundations/data-and-evaluation/datasets-and-supervision.md) owns occupancy labels.

## 1. Current execution state

| Surface | Evidence state | Recorded evidence | Permitted claim |
|---|---|---|---|
| ECCV 2024 / arXiv:2311.16038 | source inspected | [OCCSRC-PAPER]; [REP-OCCWORLD-2024] | Method and named-variant claims refer to the paper. |
| Public repository | source inspected | `1ee7f77ecc4c984a4f7f6411d95c2e6e73806b6e` (2024-04-12) | Module map, configs, and README typo gap recorded. |
| nuScenes license | policy inspected | terms block casual local eval | No local metric reproduction without registration. |
| Occ3D GT / Tsinghua pickles | not attempted | none | No label or pickle hash registered. |
| VQ-VAE training | **not attempted** | none | No reconstruction run. |
| OccWorld transformer training | **not attempted** | none | No forecasting run. |
| `eval_metric_stp3.py` | **not attempted** | none | Tables 1-2 remain paper evidence. |
| `visualize_demo.py` | **not attempted** | filename documented at pin | No visualization artifact. |

**All execution surfaces are not attempted.**

## 2. Reproduction vocabulary

- **Documented / source inspected / artifact reachable / verified / executed / metric reproduced / paper result reproduced** as in the IRASim entry.
- **Named variant** `{OccWorld-O | OccWorld-D | OccWorld-T | OccWorld-S}` is mandatory. OccWorld-O means occupancy GT, not “no labels.”

These terms describe evidence only.

## 3. License and data boundary (critical)

nuScenes [terms of use](https://www.nuscenes.org/terms-of-use) require registration and restrict redistribution. **Casual local evaluation is blocked** without accepting the license and obtaining:

- nuScenes through official channels;
- Occ3D occupancy ground truths;
- Tsinghua temporal pickle files (`data/nuscenes_infos_train_temporal_v3_scene.pkl`, `data/nuscenes_infos_val_temporal_v3_scene.pkl` as referenced by `config/train_vqvae.py` / `train_occworld.py`).

This KB records protocols only. It does not distribute nuScenes or occupancy labels. [OCCSRC-NUSCENES]

Permitted without license: source inspection, config reading, and dry-run argument parsing that does not load proprietary tensors.

Paper compute: **8× RTX 4090**, batch **1 per GPU**, AdamW **1e-3**, weight decay **0.01**. [OCCSRC-PAPER, Sec. 4]

## 4. Released commands: documented, not executed

### 4.1 Clone and pin

```bash
git clone https://github.com/wzzheng/OccWorld.git
cd OccWorld
git checkout 1ee7f77ecc4c984a4f7f6411d95c2e6e73806b6e
# create env from environment.yaml; record a resolved lock if executing later
```

### 4.2 Stage-1 tokenizer (documented)

```bash
python train.py --py-config config/train_vqvae.py --work-dir out/vqvae
```

Stage-1 uses recon + Lovasz + VQ embed losses, `return_len_=10`, codebook 512 × 128-d. [OCCSRC-CODE-CURRENT, `config/train_vqvae.py`]

### 4.3 Stage-2 OccWorld (documented)

```bash
python train.py --py-config config/train_occworld.py --work-dir out/occworld
```

This config freezes the VAE, loads `out/vqvae/epoch_125.pth` (comment: pick the best tokenizer), `return_len_=15`, `offset=1`, CE + plan-reg 0.1. Bind the observation tensors to **OccWorld-O** (3D-Occ GT) before comparing to Table 1’s 17.14 mIoU. [OCCSRC-CODE-CURRENT, `config/train_occworld.py`; OCCSRC-PAPER, Table 1]

### 4.4 STP3 metrics (documented)

```bash
python eval_metric_stp3.py --py-config config/occworld.py --work-dir out/occworld
```

Produces L2 and collision at 1/2/3 s. Do not mix this protocol with the paper’s dagger / VAD row (L2 0.64, col 0.24). [OCCSRC-PAPER, Table 2; OCCSRC-CODE-CURRENT]

### 4.5 Visualization (documented)

```bash
python visualize_demo.py --py-config config/train_occworld.py --work-dir out/occworld
```

If a fork README still cites `visulize_demo.py`, apply `OCCW-CODE-GAP-01`. At this commit the correct file is `visualize_demo.py`. [OCCSRC-CODE-CURRENT]

Do **not** call `TransVQVAE.generate_inference` (`pdb.set_trace`) or `forward_autoreg` (`pass`). Use `forward_autoreg_with_pose` / `autoreg_for_stp3_metric`. [OCCSRC-CODE-CURRENT, `OCCW-CODE-GAP-04`, `OCCW-CODE-GAP-05`]

## 5. Minimum smoke contract (licensed environments only)

**Executed smoke (tokenizer):** a recorded step count on a tiny licensed subset; finite recon loss; checkpoint saved.

**Executed smoke (forecast):** short autoregressive rollout; decoded occupancy tensor non-empty; `without_all` flag logged.

Smoke does not satisfy ECCV table reproduction.

## 6. Full metric reproduction contract

Bind:

- commit SHA `1ee7f77e…` and exact py-config;
- named variant and observation tensors (O vs D vs T vs S);
- nuScenes version, Occ3D revision, pickle hashes;
- tokenizer checkpoint hash (`epoch_125` or the actual best);
- transformer checkpoint hash;
- 2 s history → 3 s future, `offset=1`;
- tokenizer (50², 128, 512) unless Table 3 is the question;
- STP3 script vs VAD/dagger;
- 8×4090-equivalent batch 1/GPU or an explicit deviation;
- predeclared tolerance on mIoU/IoU/L2/collision/FPS.

Table 1 OccWorld-O targets: avg mIoU **17.14**, IoU **26.63**, FPS **18.0**, 1 s mIoU **25.78**, 3 s **10.51**. Table 2 OccWorld-O: L2 avg **1.17**, col avg **0.60**, L2 **0.43/1.08/1.99**, col **0.07/0.38/1.35**. [OCCSRC-PAPER, Tables 1-2]

## 7. Mechanism reproduction

| Variant | Spatial attn | Temporal attn | Ego temporal | Observation |
|---|---|---|---|---|
| OccWorld-O released | on | on | on | 3D-Occ GT |
| Table 4 spatial off | off | on | on | same |
| Table 4 temporal off | on | off | on | same |
| Table 4 ego off | on | on | off | same |
| Copy&Paste / `without_all` | n/a | n/a | n/a | last frame |
| OccWorld-S | on | on | on | camera only |

A transfer claim is falsified if OccWorld-O numbers are quoted for camera-only inputs, or if a tokenizer is selected on recon mIoU 78.12 despite forecast 12.38. [OCCSRC-PAPER, Tables 3-4]

## 8. Run-record template

```text
Experiment ID:
Named variant: {OccWorld-O | OccWorld-D | OccWorld-T | OccWorld-S}
nuScenes license registration ID (not stored in KB):
Occ3D / pickle hashes:
Commit and py-config:
Tokenizer and transformer checkpoint hashes:
Command:
Metrics vs paper table row (STP3 vs VAD):
without_all / delta_input flags:
Deviation:
Evidence conclusion:
```

No run record registered.

## 9. Training reproducibility boundary

| Regime | Publicly recoverable | Missing for exact reproduction |
|---|---|---|
| Stage-1 VQ | `config/train_vqvae.py`, recon+Lovasz+embed | Occ3D hashes, pickle hashes, 8×4090 run, best-epoch choice |
| Stage-2 OccWorld-O | `config/train_occworld.py`, frozen VAE, CE+plan-reg 0.1 | occupancy GT tensors, `epoch_125.pth` identity |
| STP3 eval | `eval_metric_stp3.py`, 1/2/3 s L2 and collision | licensed val split, variant observation contract |
| OccWorld-D/T/S | named in paper Table 1 | camera/LiDAR pipelines not a single extra yaml name |
| `generate_inference` | present | `pdb.set_trace()` — not a table path |
| Dagger / VAD row | paper Table 2 | different metric; do not use STP3 script as a substitute |

## Sources

- [OCCSRC-PAPER] evaluation protocols and named variants.
- [OCCSRC-CODE-CURRENT] commands and `visualize_demo.py` spelling.
- [OCCSRC-NUSCENES] license constraint.
- [REP-OCCWORLD-2024] Foundation identity.
