---
id: world-model-kb.papers.ivideogpt.codebase
title: iVideoGPT Released Implementation Graph
kind: reference
status: maintained
last_updated: 2026-08-14
owners:
  - AIBuildAI world-model group
---

# iVideoGPT Released Implementation Graph

## Retrieval metadata

**Relevant queries:** thuml iVideoGPT, train_tokenizer.py, train_gpt.py, compressive_vq_model.py, predict.py, mbpo, oxe-64-act-free, RLVR-World boundary.

**Knowledge provided:** pinned commit paths, pretrain/finetune/eval scripts, checkpoint naming, and gaps.

**Related pages:** [`paper.md`](paper.md); [`reproduction.md`](reproduction.md).

## 1. Revision

`thuml/iVideoGPT@d601d5cac9e96c6aa0c17cb37ed6a7c7ca1fb210` (2025-09-23). README already advertises RLVR-World (2025) as a **separate** repo. Do not mix those weights into iVideoGPT tables. [IVG-CODE]

## 2. Tree (selected)

```text
train_tokenizer.py
train_gpt.py
inference/predict.py
inference/utils.py
datasets/oxe_data_converter.py
datasets/preprocess_bair.py
datasets/preprocess_robonet.py
datasets/preprocess_vp2.py
ivideogpt/vq_model/compressive_vq_model.py
ivideogpt/vq_model/conditional_vae.py
ivideogpt/transformer/action_model.py
ivideogpt/data/dataset_mixes.py      # OXE_SELECT
ivideogpt/utils/video_metric.py
scripts/pretrain/oxe-64-act-free.sh
scripts/pretrain/oxe-64-act-free-medium.sh
scripts/pretrain/oxe-64-goal-cond.sh
scripts/pretrain/oxe-256-act-free.sh
scripts/finetune/bair-64-act-cond.sh
scripts/finetune/robonet-64-act-cond.sh
scripts/finetune/robonet-256-act-cond.sh
scripts/evaluation/bair-64-act-cond.sh
mbrl/train_metaworld_mbpo.py
mbrl/video_predictor.py
mbrl/cfgs/mbpo_config.yaml
vp/ivideogpt_interface.py
vp/ivideogpt.yaml
```

## 3. Call graphs

**Tokenizer**

```text
accelerate launch train_tokenizer.py --model_type ctx_vqgan \
  --pretrained_model_name_or_path .../tokenizer
  -> ivideogpt/vq_model/compressive_vq_model.py
```

**Transformer**

```text
accelerate launch train_gpt.py --vqgan_type ctx_vqgan \
  --config_name configs/llama/config.json \
  [--action_conditioned --action_dim 4] [--load_internal_llm]
  -> ivideogpt/transformer
```

**OXE inference**

```text
python inference/predict.py \
  --pretrained_model_name_or_path thuml/ivideogpt-oxe-64-act-free \
  --input_path inference/samples/fractal_sample.npz \
  --dataset_name fractal20220817_data
```

**MBRL**

```text
python mbrl/train_metaworld_mbpo.py task=plate_slide num_train_frames=100002
```

Requires a pinned Meta-World commit in the README. `mbrl/cfgs/mbpo_config.yaml` uses absolute paths — do not copy those paths into this KB.

**VP2** lives under `vp/` with `vp/script.sh`.

Pinned-commit mechanism files (sizes from GitHub tree JSON at `d601d5cac9e96c6aa0c17cb37ed6a7c7ca1fb210`):

| Path | Bytes | Role |
|---|---:|---|
| `train_tokenizer.py` | 54107 | ctx_vqgan training |
| `train_gpt.py` | 42030 | LLaMA-style AR |
| `ivideogpt/vq_model/compressive_vq_model.py` | 15583 | compressive VQ |
| `ivideogpt/vq_model/conditional_vae.py` | 7012 | context/future VAE |
| `ivideogpt/transformer/action_model.py` | 9693 | action tokens |
| `ivideogpt/data/dataset_mixes.py` | 7727 | `OXE_SELECT` |
| `ivideogpt/data/simple_dataloader.py` | 24080 | OXE npz loader |
| `inference/predict.py` | 5721 | Hub smoke |
| `mbrl/train_metaworld_mbpo.py` | 18849 | MBPO entry |
| `mbrl/video_predictor.py` | 14769 | WM as imagination |
| `mbrl/cfgs/mbpo_config.yaml` | 2508 | **absolute paths** |
| `scripts/pretrain/oxe-64-act-free.sh` | 1643 | small OXE |
| `scripts/pretrain/oxe-64-act-free-medium.sh` | 1709 | 436M |
| `scripts/pretrain/oxe-64-goal-cond.sh` | 1758 | goal tokens |
| `scripts/pretrain/oxe-256-act-free.sh` | 1895 | 256 OXE |
| `vp/ivideogpt_interface.py` | 8768 | VP2 glue |

There is **no** `scripts/pretrain/oxe-64-act-cond.sh`. Action-conditioned OXE pretrain is not released.

## 4. Checkpoint contract

| Claim | Bind to |
|---|---|
| OXE action-free 64 | `thuml/ivideogpt-oxe-64-act-free` [IVG-HF-OXE-64-ACT-FREE] |
| OXE action-cond 64 | Hub card `thuml/ivideogpt-oxe-64-act-cond` exists as a named identity; OXE **pretrain** is action-free because action spaces are heterogeneous. Downstream act-cond weights are BAIR/RoboNet/VP2 scripts. [IVG-HF-OXE-64-ACT-COND] |
| OXE 256 | Hub `thuml/ivideogpt-oxe-256`; README may list `ivideogpt-oxe-256-act-free` and warn undertraining. [IVG-HF-OXE-256] |
| OXE medium | README `ivideogpt-oxe-64-act-free-medium`; YAML title `ivideogpt-oxe-medium` [IVG-HF-OXE-MEDIUM] |
| OXE goal | `thuml/ivideogpt-oxe-64-goal-cond` [IVG-HF-OXE-64-GOAL-COND] |
| RLVR-World | different project (2025); not an iVideoGPT table |

I3D for FVD: `pretrained_models/i3d/i3d_torchscript.pt` from the Dropbox URL in README.

## 5. Gap ledger

| ID | Evidence | Effect | Repair |
|---|---|---|---|
| `IVIDEO-CODE-GAP-01` | no OXE act-cond Hub model | cannot reproduce OXE action-cond from official weights | finetune BAIR/RoboNet scripts |
| `IVIDEO-CODE-GAP-02` | 256 RoboNet ckpt deleted | Table 1 256 row not loadable | retrain or drop claim |
| `IVIDEO-CODE-GAP-03` | RLVR-World linked in README | identity confusion | separate entry |
| `IVIDEO-CODE-GAP-04` | mbpo YAML absolute paths | unreproducible as copied | rewrite paths in a recorded derivative |
| `IVIDEO-CODE-GAP-05` | OXE ~5 TB | smoke must use one npz | `inference/samples/fractal_sample.npz` |
| `IVIDEO-CODE-GAP-06` | FVD I3D extra download | metric scripts fail | hash I3D file |
| `IVIDEO-CODE-GAP-07` | Python 3.9 pin; unpinned torch | env drift | external lock |

## 6. Change surfaces

| Intervention | Files |
|---|---|
| Compressive VQ | `compressive_vq_model.py` |
| Action tokens | `train_gpt.py --action_conditioned`; `action_model.py` |
| Goal tokens | `scripts/pretrain/oxe-64-goal-cond.sh` |
| Medium width | `oxe-64-act-free-medium.sh` |
| MBRL imagination | `mbrl/video_predictor.py` |

## 7. Finetune CLI (documented)

Tokenizer (BAIR example): `--model_type ctx_vqgan --disc_start 1000005 --segment_horizon 16 --segment_length 8 --context_length 1 --max_train_steps 200005`. Transformer: `--config_name configs/llama/config.json --load_internal_llm --action_conditioned --action_dim 4 --learning_rate 1e-4 --weight_decay 0.01 --llama_attn_drop 0.1 --embed_no_wd --max_train_steps 100005 --use_fvd --use_frame_metrics`. Action-free: drop `--load_internal_llm --action_conditioned`. [IVG-CODE README]

FVD extra file: `pretrained_models/i3d/i3d_torchscript.pt`. Meta-World pin: `83ac03ca3207c0060112bfc101393ca794ebf1bd`. Collection: `thuml/ivideogpt-674c59cae32231024d82d6c5`.

Additional blobs: `ivideogpt/vq_model/vae.py` (13532), `lpips.py` (6293), `discriminator.py` (1724), `ivideogpt/data/sthsth_dataloader.py` (14654), `datasets/preprocess_bair.py` / `preprocess_robonet.py` / `preprocess_vp2.py`, `scripts/evaluation/bair-64-act-cond.sh`, `mbrl/drqv2.py` (10532), `mbrl/metaworld_env.py` (12780). No `oxe-64-act-cond` pretrain script exists in this tree.

## Sources

- [IVG-CODE] pinned commit.
- Hub cards in [`sources.yaml`](sources.yaml).
