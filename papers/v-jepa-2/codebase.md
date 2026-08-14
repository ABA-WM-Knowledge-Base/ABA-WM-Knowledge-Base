---
id: world-model-kb.papers.v-jepa-2.codebase
title: V-JEPA 2 Released Implementation Graph
kind: reference
status: maintained
last_updated: 2026-08-14
owners:
  - AIBuildAI world-model group
---

# V-JEPA 2 Released Implementation Graph

## Retrieval metadata

**Relevant queries:** vjepa2 repository, commit 204698b4, app/vjepa/train.py, ac_predictor, mpc_utils, vjepa_2_1, droid-256px-8f, vitg-384 eval yaml, torch.hub vjepa2_ac_vit_giant, or paper-code variant map.

**Knowledge provided:** the pinned implementation call graph, configuration and tensor contracts, exact mechanism attachment points, released artifacts, static gaps, and the boundary between V-JEPA 2, 2-AC, and 2.1.

**Related pages:** [`paper.md`](paper.md) owns the method and results; [`reproduction.md`](reproduction.md) owns executed status; [representation learning and JEPA](../../foundations/representations/representation-learning-and-jepa.md) owns the generic objective; [Cosmos3-Nano reasoner](../../models/cosmos3-nano/reasoner.md) owns the target attachment.

## 1. Revision and release policy

All mappings use `facebookresearch/vjepa2@204698b45b3712590f06245fbfba32d3be539812`, dated 2026-03-23. Hugging Face or Meta CDN checkpoints referenced by the repo must record revision and SHA256 on download. The tree is MIT-licensed (some video-aug files Apache-2.0). [VJ2-CODE]

Foundation paper identity: [OBJ-VJEPA2-2025] — not duplicated in [`sources.yaml`](sources.yaml).

V-JEPA **2.1** training code lives under `app/vjepa_2_1/` in this pin. It is a **later recipe**, not a silent alias of paper V-JEPA 2 or 2-AC. [VJ2-CODE]

## 2. Released surface versus paper surface

| Capability | Paper | Public implementation at pinned commit | Consequence |
|---|---|---|---|
| Action-free pretrain (ViT-L→g) | 1M+ h, VideoMix22M, 252K-class + cooldown | `app/vjepa/train.py`, `src/models/vision_transformer.py`, `src/models/predictor.py`, `src/masks/multiseq_multiblock3d.py` | data shards are external; full pretrain is not a local target |
| Progressive 256/16 → 384/64 | scaling section | `configs/train/vitg16/pretrain-256px-16f.yaml`, `configs/train/vitg16/cooldown-384px-64f.yaml` | schedule is config-level |
| Frozen probes | SSv2, EK100, K400 | `evals/video_classification_frozen/`, `evals/action_anticipation_frozen/`, `configs/eval/vitg-384/{ssv2,ek100,k400}.yaml` | needs downloaded ViT-g weights |
| 2-AC DROID post-train | <62 h, frozen ViT-g | `app/vjepa_droid/train.py`, `src/models/ac_predictor.py`, `configs/train/vitg16/droid-256px-8f.yaml` | subset hours must match the paper to cite Table 2 |
| Latent CEM | Tables 2-3 | `notebooks/utils/mpc_utils.py`, `notebooks/utils/world_model_wrapper.py` | **notebook** planner, not a CLI `eval_franka.py` |
| V-JEPA 2.1 | not the Table 2/3 protocol | `app/vjepa_2_1/train.py`, `app/vjepa_2_1/models/vision_transformer.py` | separate evidence object |
| Pixel video generation | no | absent by design | not a gap |

There is no `finetune/ac_predictor.py` or `planning/eval_franka.py` at this commit. Those names are not in the tree.

## 3. Variant-to-path map

| Public name | Entry | Core modules | Configs |
|---|---|---|---|
| V-JEPA 2 | `app/vjepa/train.py` | `src/models/vision_transformer.py`, `src/models/predictor.py`, `src/masks/multiseq_multiblock3d.py` | `configs/train/vitg16/pretrain-256px-16f.yaml`, `cooldown-384px-64f.yaml` |
| V-JEPA 2-AC | `app/vjepa_droid/train.py` | `src/models/ac_predictor.py` (`VisionTransformerPredictorAC`) | `configs/train/vitg16/droid-256px-8f.yaml` |
| V-JEPA 2.1 | `app/vjepa_2_1/train.py` | `app/vjepa_2_1/models/vision_transformer.py` | 2.1 configs under `app/vjepa_2_1/` as present at the pin |
| Frozen eval | evals entry points | classification / anticipation | `configs/eval/vitg-384/ssv2.yaml`, `ek100.yaml`, `k400.yaml` |
| Robot MPC | notebooks | `notebooks/utils/mpc_utils.py`, `world_model_wrapper.py` | experiment cells, not a Hydra job |

Documented launchers at this pin wrap those entries as `python -m app.main --fname <yaml>` (pretrain / DROID) and `python -m evals.main --fname <yaml>` (frozen probes). Record the exact module path in a run log; do not invent `eval_franka.py`. [VJ2-CODE]

## 4. Tensor contracts

### 4.1 Action-free encoder / predictor

Typical ViT-g/16 at 256 px: patch 16, tubelet 2. Spatial grid **16×16**. Encoder width for ViT-g is **1408**, matching the paper's AC feature maps **16×16×1408**. Predictor width is smaller (ViT-small class). Masking produces context vs target token sets; the loss is on predicted vs target embeddings, not RGB. [VJ2-PAPER, Sec. 3-4; VJ2-CODE]

Cooldown configs move to 64 frames and 384 px; token counts scale with frames and spatial grid (384/16 = 24, so 24×24 spatial at cooldown, not 16×16). Do not mix 256-px AC feature-map shapes with 384-px cooldown shapes. [VJ2-CODE, `configs/train/vitg16/cooldown-384px-64f.yaml`]

DROID AC clips in `droid-256px-8f.yaml` are **8-frame / 256 px**, not the 64-frame cooldown setting. [VJ2-CODE]

### 4.2 AC predictor (`VisionTransformerPredictorAC`)

From `src/models/ac_predictor.py`:

- `x`: context tokens `[B, N_ctxt, embed_dim]` with `N_ctxt = T * H * W`;
- `actions`, `states`: `[B, T, action_embed_dim]` with default `action_embed_dim=7`;
- optional `extrinsics`: `[B, T, action_embed_dim-1]` when `use_extrinsics=True`;
- `predictor_embed`: `embed_dim → predictor_embed_dim`;
- `action_encoder` / `state_encoder`: `action_embed_dim → predictor_embed_dim`;
- interleaved sequence per time: `[a, s, z]` or `[a, s, e, z]` then flatten;
- causal `attn_mask` from `build_action_block_causal_attention_mask`;
- output projected back to `embed_dim` (next-z in encoder space).

Teacher-forcing next-z is applied in `app/vjepa_droid/train.py`. CEM uses predicted z sequences from `notebooks/utils/world_model_wrapper.py` scored in `notebooks/utils/mpc_utils.py`. [VJ2-CODE]

## 5. Call graphs

```text
Action-free pretrain
app/vjepa/train.py   (typically python -m app.main --fname configs/train/vitg16/pretrain-256px-16f.yaml)
  -> vision_transformer encoder + predictor
  -> multiseq_multiblock3d masks
  -> JEPA embedding loss, EMA / stop-grad target
  -> later: cooldown-384px-64f.yaml

Frozen understanding
evals/video_classification_frozen/*   + configs/eval/vitg-384/{ssv2,k400}.yaml
evals/action_anticipation_frozen/*    + configs/eval/vitg-384/ek100.yaml

2-AC
app/vjepa_droid/train.py
  -> frozen encoder weights
  -> droid-256px-8f.yaml
  -> VisionTransformerPredictorAC.forward(x, actions, states, extrinsics)
  -> teacher-forcing next-z

Planning (notebook)
world_model_wrapper.encode / predict
  -> mpc_utils CEM
  -> image goal encoding (pick-place: three sub-goals)
  -> execute first action on Franka (hardware bridge not a repo CLI)
```

## 6. Paper-code gap ledger

| ID | Evidence | Effect | Minimal repair boundary |
|---|---|---|---|
| `VJEPA-GAP-01` | robot MPC lives in `notebooks/utils/mpc_utils.py`, not a train/eval CLI | copied “eval_franka.py” commands fail | bind notebook revision and cell parameters |
| `VJEPA-GAP-02` | 2.1 encoder under `app/vjepa_2_1/` | easy to load 2.1 weights into a 2-AC script | freeze the encoder SHA and variant tag |
| `VJEPA-GAP-03` | AC default `action_embed_dim=7`; DROID action convention is code-defined | unit/frame mismatch destabilizes CEM | record action normalization with the checkpoint |
| `VJEPA-GAP-04` | feature maps 16×16×1408 assume 256-px ViT-g/16 | cooldown 384-px grids differ | do not mix cooldown encoder tokens with 256-px AC heads without a documented adapter |
| `VJEPA-GAP-05` | Table 3 Cosmos video WM is an external baseline | not implemented in this repo | do not search the tree for a Cosmos trainer |
| `VJEPA-GAP-06` | VideoMix22M / 1M+ h shards are not in git | pretrain from scratch is not a smoke test | start from released checkpoints |
| `VJEPA-GAP-07` | PerceptionTest 84.0 uses 8B-class LLM alignment | frozen ViT-g probe is a different number | do not run only `video_classification_frozen` and quote 84.0 |
| `VJEPA-GAP-08` | 10-trial robot cells | wide binomial CIs | log raw trial vectors, not only averages |
| `VJEPA-GAP-09` | image sub-goals for pick-place (4 / 10 / 4 steps) | language-only eval is a different protocol | record goal encoding |
| `VJEPA-GAP-10` | `use_extrinsics` optional third token | camera-pose sensitivity in the paper | treat extrinsics on/off as a controlled ablation |

## 7. Change surfaces for optimization

| Intervention | Primary code surface | Controlled variables |
|---|---|---|
| JEPA mask geometry | `src/masks/multiseq_multiblock3d.py` | clip length, patch, tubelet |
| Encoder scale | `src/models/vision_transformer.py` | ViT-L vs g, 256 vs 384 |
| Progressive cooldown | `pretrain-256px-16f.yaml` → `cooldown-384px-64f.yaml` | iteration split, GPU-years |
| AC interleave `(a,s,z)` | `src/models/ac_predictor.py` `forward` | `use_extrinsics`, RoPE, depth |
| Frozen vs unfrozen encoder | `app/vjepa_droid/train.py` | DROID hours |
| CEM budget | `notebooks/utils/mpc_utils.py` | samples, iters, horizon vs Table 3 |
| Goal image encoding | `world_model_wrapper.py` | pick-place three sub-goals |
| 2.1 drop-in | `app/vjepa_2_1/models/vision_transformer.py` | do not relabel Table 2 |

Released-compatible experiments keep the frozen ViT-g + AC predictor + notebook CEM. Paper-faithful reconstructions may change CEM hyperparameters but must not relabel 2.1 or action-free checkpoints as Table 2.

## 8. Cosmos3 attachment surface

V-JEPA 2 attaches to the **Cosmos3-Nano Reasoner** visual tower and to a **latent planner** over Reasoner tokens. It does **not** attach to Generator pixels or to FD/WAM video denoisers. Table 3's Cosmos video WM is a published external baseline, not an invitation to put JEPA losses on the Generator. [VJ2-PAPER, Table 3; Cosmos3-Nano reasoner]

## Sources

- [VJ2-CODE] `facebookresearch/vjepa2@204698b45b3712590f06245fbfba32d3be539812`.
- [VJ2-PAPER] variant-specific claims and tables.
- [OBJ-VJEPA2-2025] action-free vs AC evidence separation.
