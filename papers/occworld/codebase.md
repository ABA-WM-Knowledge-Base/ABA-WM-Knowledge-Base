---
id: world-model-kb.papers.occworld.codebase
title: OccWorld Released Implementation Graph
kind: reference
status: maintained
last_updated: 2026-08-14
owners:
  - AIBuildAI world-model group
---

# OccWorld Released Implementation Graph

## Retrieval metadata

**Relevant queries:** wzzheng OccWorld commit 1ee7f77, TransVQVAE, train_vqvae, train_occworld, eval_metric_stp3, visualize_demo, PlanUtransformer, VectorQuantizer, or nuScenes pickle.

**Knowledge provided:** the pinned implementation call graph, configuration and tensor contracts, exact mechanism attachment points, released artifacts, static defects, and paper-code boundaries.

**Related pages:** [`paper.md`](paper.md) owns the method and results; [`reproduction.md`](reproduction.md) owns executed status and license; [3D and 4D world models](../../foundations/representations/3d-and-4d-world-model.md) owns geometric forecasting; [Cosmos3-Nano generator](../../models/cosmos3-nano/generator.md) owns the parallel-head attachment.

## 1. Revision and release policy

All mappings use `wzzheng/OccWorld@1ee7f77ecc4c984a4f7f6411d95c2e6e73806b6e`, dated 2024-04-12. Identity is commit-only (no release tag). [OCCSRC-CODE-CURRENT]

Foundation paper identity: [REP-OCCWORLD-2024] — not duplicated in [`sources.yaml`](sources.yaml).

At this commit the demo script is spelled **`visualize_demo.py`**. Older README text used **`visulize_demo.py`**. Record the historical typo; invoke the filename that exists at the pin. [OCCSRC-CODE-CURRENT]

## 2. Released surface versus paper surface

| Capability | Paper | Public implementation at pinned commit | Consequence |
|---|---|---|---|
| VQ tokenizer | (50², 128, 512), ds=4 | `config/train_vqvae.py`, `model/VAE/vae_2d_resnet.py`, `model/VAE/quantizer.py` | released stage-1 |
| OccWorld transformer + pose | 2 s → 3 s, joint occupancy/ego | `config/train_occworld.py`, `model/TransVQVAE.py`, `model/transformer/PlanUtransformer.py`, `pose_encoder.py`, `pose_decoder.py` | released stage-2 |
| OccWorld-O metrics | Tables 1-2 | `eval_metric_stp3.py` + `config/occworld.py` | needs nuScenes+Occ3D+pickles |
| OccWorld-D / T / S | Tables 1-2 named rows | observation comes from dataset occupancy vs camera/LiDAR pipelines | bind config + data, not filename alone |
| Visualization | qualitative figures | `visualize_demo.py` | correct spelling at this SHA |
| Copy&Paste baseline | Table 1 | `TransVQVAE.without_all` repeats last occupancy / last pose | paper baseline, code flag |
| Sampling decode | not the main table | `generate_inference` contains `pdb.set_trace()` | not a usable sampler |
| `forward_autoreg` without pose | — | method body is `pass` | dead API |

There is no `tools/train.py`. The training entry is repo-root `train.py`. Dataset code is `dataset/dataset.py`, not `datasets/`.

## 3. Configuration resolution

```text
python train.py --py-config config/train_vqvae.py --work-dir out/vqvae
python train.py --py-config config/train_occworld.py --work-dir out/occworld
python eval_metric_stp3.py --py-config config/occworld.py --work-dir out/occworld
python visualize_demo.py --py-config config/train_occworld.py --work-dir out/occworld
```

`train_occworld.py` freezes the VAE (`freeze_dict.vae = True`), loads `out/vqvae/epoch_125.pth`, uses AdamW `lr=1e-3`, `weight_decay=0.01`, `batch_size=1`, `return_len_=15`, `offset=1`. Tokenizer yaml uses `n_e_=512`, `base_channel=64` so `e_dim = z_channels = 128`, encoder `ch_mult=(1,2,4)` on `resolution=200` → **50×50** latents. [OCCSRC-CODE-CURRENT, `config/train_vqvae.py`, `config/train_occworld.py`]

Dependencies are hinted in `environment.yaml`. This is not a fully pinned lock across CUDA and mmengine.

## 4. Tensor contracts

From `TransVQVAE.forward_train` / `forward_inference`:

- occupancy `x`: `[B, F, H, W, D]` with `F == num_frames + offset` (15+1 in the OccWorld trainer);
- encoder latent before quantize: `[B*F, C, 50, 50]`, `C=128`;
- codebook indices rearranged to `[B, F, 50, 50]`;
- `ce_labels`: indices for frames `[offset:]`, flattened;
- transformer input: quantized `z_q[:, :num_frames]` as `[B, T, C, 50, 50]`;
- `ce_inputs`: per-token logits over `n_e=512`;
- pose input: `rel_poses` concatenated with `gt_mode` → 5-D, then `PoseEncoder`;
- `pose_decoded`: `[B, T, 3, 2]` (three modes, XY);
- semantic pred: argmax over 18 classes; class **17** treated as empty for IoU (`pred_iou`).

[OCCSRC-CODE-CURRENT, `model/TransVQVAE.py`, `config/train_occworld.py`]

## 5. Call graph

```text
train.py --py-config config/train_vqvae.py
  -> dataset/dataset.py  nuScenesSceneDatasetLidar
  -> model VAERes2D + VectorQuantizer
  -> loss/recon_loss.py + Lovasz + loss/emb_loss.py
  -> out/vqvae/epoch_*.pth

train.py --py-config config/train_occworld.py
  -> load frozen VAE
  -> TransVQVAE
       vae.encode / quantize
       PlanUAutoRegTransformer(z_q, pose_tokens)
       PoseEncoder / PoseDecoder
  -> loss/ce_loss.py + loss/plan_reg_loss_lidar.py
  -> out/occworld/

eval_metric_stp3.py --py-config config/occworld.py
  -> TransVQVAE.autoreg_for_stp3_metric
  -> PlanningMetric L2 + collision at 1/2/3 s

visualize_demo.py --py-config config/train_occworld.py
  -> decode occupancy + overlay ego
```

## 6. Paper-code gap ledger

| ID | Evidence | Effect | Minimal repair boundary |
|---|---|---|---|
| `OCCW-CODE-GAP-01` | historical README `visulize_demo.py`; pin file is `visualize_demo.py` | old commands FileNotFound | use the pin filename; note the typo |
| `OCCW-CODE-GAP-02` | nuScenes terms | blocks casual eval | license + Occ3D + Tsinghua pickles |
| `OCCW-CODE-GAP-03` | pickle paths `data/nuscenes_infos_*_temporal_v3_scene.pkl` | missing files crash the loader | record pickle revision hashes |
| `OCCW-CODE-GAP-04` | `generate_inference` calls `pdb.set_trace()` | sampler is not runnable | do not use this method for tables |
| `OCCW-CODE-GAP-05` | `forward_autoreg` is `pass` | dead API | use `forward_autoreg_with_pose` |
| `OCCW-CODE-GAP-06` | `delta_input` branch in autoreg uses `torch.cat(...)` without a list in one path | runtime TypeError if enabled | keep `delta_input=False` (yaml default) |
| `OCCW-CODE-GAP-07` | `environment.yaml` partial pins | env drift | external lock |
| `OCCW-CODE-GAP-08` | variant O/D/T/S is a **data** choice, not four model classes | easy to score the wrong Table 1 row | bind occupancy vs camera vs LiDAR inputs in the run record |
| `OCCW-CODE-GAP-09` | `without_all` implements Copy&Paste-like repeat | useful baseline; easy to leave on | log the flag |
| `OCCW-CODE-GAP-10` | class 17 hardcoded as empty | label-mapping drift breaks IoU | keep `config/label_mapping/nuscenes-occ.yaml` |

## 7. Change surfaces for optimization

| Intervention | Primary code surface | Controlled variables |
|---|---|---|
| Codebook size / spatial tokens | `n_e_`, encoder `resolution` / `ch_mult` | Table 3 recon vs forecast |
| Spatial vs temporal attn | `PlanUtransformer.py` `num_layers`, `temporal_attn_layers` | Table 4 |
| Ego-temporal tokens | `pose_encoder.py`, `pose_decoder.py`, `pose_attn_layers` | planning L2/collision |
| Joint vs occupancy-only | `PlanRegLossLidar` weight 0.1 | CE vs plan |
| Copy&Paste | `without_all` | Table 1 floor |
| Horizon | `num_frames`, `offset`, autoreg `mid_frame`/`end_frame` | 2 s → 3 s protocol |
| Auxiliary occupancy on a video model | **not in this repo** | Cosmos3 Generator parallel head; see [`optimization-transfer.md`](optimization-transfer.md) |

## 8. Cosmos3 attachment surface

OccWorld occupancy is an **auxiliary geometric head parallel to the Generator**, not a replacement for Generator pixels or FD/WAM video. A Cosmos3 experiment may predict coarse BEV/occupancy from Generator intermediate tokens while leaving RGB latents on the Wan VAE path. Replacing FD/WAM decode with occupancy voxels is out of scope unless an explicit bridge is trained. [OCCSRC-PAPER; Cosmos3-Nano generator; Cosmos3-Nano action modeling]

## Sources

- [OCCSRC-CODE-CURRENT] `wzzheng/OccWorld@1ee7f77ecc4c984a4f7f6411d95c2e6e73806b6e`.
- [OCCSRC-PAPER] variant and architecture claims.
- [OCCSRC-NUSCENES] dataset license boundary.
- [REP-OCCWORLD-2024] Foundation identity.
