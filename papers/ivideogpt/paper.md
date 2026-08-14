---
id: world-model-kb.papers.ivideogpt.paper
title: iVideoGPT Method, Architecture, and Experimental Evidence
kind: paper
status: maintained
last_updated: 2026-08-14
owners:
  - AIBuildAI world-model group
---

# iVideoGPT Method, Architecture, and Experimental Evidence

## Retrieval metadata

**Relevant queries:** iVideoGPT, compressive conditional VQGAN, OXE pretrain, BAIR FVD 75.0, RoboNet PSNR 23.8, VP2, MBPO Meta-World, act-free versus act-cond, or NeurIPS 2024 camera-ready v3.

**Knowledge provided:** tokenizer and AR architecture, OXE mixture, numbered prediction and control tables, named Hugging Face checkpoints, and the RLVR-World 2025 boundary.

**Related pages:** [`README.md`](README.md); [`codebase.md`](codebase.md); [autoregressive modeling](../../foundations/learning-objectives/autoregressive-modeling.md); [forward dynamics](../../foundations/problem-formulation/forward-dynamics.md); [model-based RL](../../foundations/decision-making/model-based-rl.md).

Canonical paper: arXiv:2405.15223 **v3** (2024-11-01 camera-ready). [IVG-PAPER]

## 1. Problem statement

iVideoGPT is an **interactive video world model**: a compressive visual tokenizer plus an autoregressive transformer that can ingest context frames, optional actions, optional goals, and rewards. It is pretrained action-free on heterogeneous robot and human video, then finetuned for action-conditioned prediction, visual MPC, or MBRL. It is not RLVR-World (NeurIPS 2025), which is a later reward-finetuning method that can *use* iVideoGPT. [IVG-PAPER, Abstract, Sec. 1; IVG-CODE README]

```text
context frames -> context VQ encoder E_c
future frames  -> prediction encoder E_p (tighter bottleneck, cross-attends to E_c)
tokens + optional action/goal/reward -> LLaMA-style AR transformer
decode future tokens with D_p conditioned on context features
```

## 2. Architecture

### 2.1 Compressive conditional VQGAN

Two encoder-decoder pairs share a VQGAN layout but the prediction path downsamples `16 x 16` embeddings to `4 x 4` before the codebook, so future tokens carry mostly dynamics. Context features enter via multi-scale cross-attention (ContextWM-style). Codebook size **8192**, embedding dim 64. [IVG-PAPER, Appendix A.1, Table 2]

| VQGAN | Low-res 64x64 | High-res 256x256 |
|---|---|---|
| Parameters | 114M | 310M |
| Down channels | [128, 256, 512] | [128, 256, 256, 512, 768] |
| Down blocks | 3 | 5 |

Independent `16 x 16` per-frame tokens OOM at the paper's transformer training setting; `4 x 4` is cheap but weaker. The compressive design sits in between: training 2.62 it/s and 22.3 GB versus `4 x 4` at 3.10 it/s and 10.6 GB (A100, batch 16/device). Generation on 4090: compressive 1.11 s versus `16 x 16` 22.5 s. [IVG-PAPER, Tables 7-8]

### 2.2 Autoregressive transformer

| Transformer | Small | Medium |
|---|---|---|
| Parameters | 138M | 436M |
| Layers / heads / width | 12 / 12 / 768 | 24 / 16 / 1024 |

Actions, when used, are tokenized into the same AR stream (`--action_conditioned --action_dim`). Rewards use a symlog transform in the MBRL setting. Goal-conditioned variants prepend a goal frame. [IVG-PAPER, Table 2, Appendix A.5]

### 2.3 Pretraining data

About **1.4 million** trajectories: 35 OXE datasets after Octo-like filtering (drop no-image, mobile robots, low-res, heavy repetition) plus Something-Something v2 (95 motion classes, 15% mixture weight) for the tokenizer. Transformer pretraining uses OXE only. 1% per subset held out for validation. [IVG-PAPER, Sec. 3, Appendix A.2, Table 4]

Low-res tokenizer pretrain: `1e6` steps, batch 64, 17 GPU-days. High-res tokenizer: `2.5e5` steps, batch 32, 16 GPU-days. OXE occupies about 5 TB. 64x64 fits 24 GB/device; 256x256 needs 40 GB. [IVG-PAPER, Table 3, Appendix C]

## 3. Video prediction (Table 1)

Protocol: BAIR 43k train / 256 test, 15 frames from 1 frame. RoboNet 162k videos / 256 test, 10 frames from 2 frames; overlapping OXE test clips filtered. Best-of-100 samples for PSNR/SSIM/LPIPS; FVD uses all 100. SSIM/LPIPS scaled x100. Three runs. [IVG-PAPER, Sec. 4.1, Table 1]

**BAIR 64x64 action-free**

| Method | FVD ↓ | PSNR ↑ | SSIM ↑ | LPIPS ↓ |
|---|---:|---:|---:|---:|
| MAGVIT | 62.0 | 19.3 | 78.7 | 12.3 |
| iVideoGPT | 75.0 ± 0.20 | **20.4 ± 0.01** | **82.3 ± 0.05** | **9.5 ± 0.01** |

**BAIR 64x64 action-conditioned**

| Method | FVD ↓ | PSNR ↑ | SSIM ↑ | LPIPS ↓ |
|---|---:|---:|---:|---:|
| MaskViT | 70.5 | — | — | — |
| iVideoGPT | **60.8 ± 0.08** | 24.5 ± 0.01 | 90.2 ± 0.03 | 5.0 ± 0.01 |

Action conditioning improves BAIR FVD by about 20% relative (`75.0 -> 60.8`). MAGVIT still wins action-free FVD.

**RoboNet 64x64 action-conditioned**

| Method | FVD ↓ | PSNR ↑ | SSIM ↑ | LPIPS ↓ |
|---|---:|---:|---:|---:|
| FitVid | **62.5** | **28.2** | 89.3 | **2.4** |
| iVideoGPT | 63.2 ± 0.01 | 27.8 ± 0.01 | **90.6 ± 0.02** | 4.9 ± 0.00 |

**RoboNet 256x256 action-conditioned**

| Method | FVD ↓ | PSNR ↑ | SSIM ↑ | LPIPS ↓ |
|---|---:|---:|---:|---:|
| MaskViT | 211.7 | 20.4 | 67.1 | 17.0 |
| iVideoGPT | **197.9 ± 0.66** | **23.8 ± 0.00** | **80.8 ± 0.01** | **14.7 ± 0.01** |

Public 256x256 RoboNet checkpoints were deleted accidentally per README; paper numbers remain. [IVG-PAPER, Table 1; IVG-CODE README]

With 1000 action-conditioned BAIR trajectories after pretrain, FVD 82.3 (text, not Table 1). Pretraining helps most at 100–1000 downstream trajectories. [IVG-PAPER, Sec. 4.1]

Human study on action-free BAIR: 386 annotations, 9 participants, versus VideoGPT and MCVD (Fig. 20). [IVG-PAPER, Appendix B.2]

### 3.1 Tokenizer and transformer efficiency (Tables 7-8)

A100, batch 16/device, mixed precision as in the paper:

| Tokenizer layout | Train it/s | Train mem GB | 4090 gen s (bs=1) |
|---|---:|---:|---:|
| Independent `4 x 4` | 3.10 | 10.6 | (faster, weaker) |
| Compressive (released) | 2.62 | 22.3 | **1.11** |
| Independent `16 x 16` | OOM | OOM | 22.5 |

Codebook size **8192**, embedding dim 64. Context encoder keeps higher spatial resolution; prediction encoder compresses dynamics. [IVG-PAPER, Tables 7-8, Appendix A.1]

### 3.2 Pretrain compute (Table 3)

| Stage | Steps | Batch | GPU-days |
|---|---:|---:|---:|
| Low-res tokenizer 64 | 1e6 | 64 | 17 |
| High-res tokenizer 256 | 2.5e5 | 32 | 16 |
| Transformer (small, OXE) | see scripts | 16/device typical | (script-defined) |

64x64 fits 24 GB/device; 256x256 needs 40 GB. OXE ~5 TB on disk after npz extract. [IVG-PAPER, Table 3, Appendix C]

## 4. Visual planning and MBRL

VP2: 5k Robosuite and 35k RoboDesk trajectories. Table 6 mean success (iVideoGPT column first in the HTML table): Robosuite push **0.7833**, open drawer **0.3750**, blue button **0.9556**, red button **0.9222**, open slide **0.1611** (weaker than SVG′ 0.5733). Flat block is near floor for all learned models. [IVG-PAPER, Table 6, Fig. 5]

MBRL: MBPO + DrQ-v2 on six Meta-World tasks; iVideoGPT as the imagination model; compared to DreamerV3 ± pretraining. Curves are in figures, not a single scalar table in the HTML extract. FitVid-as-WM loses on 5/6 tasks (Fig. 21). Released entry: `python mbrl/train_metaworld_mbpo.py task=plate_slide num_train_frames=100002`. Task YAMLs exist for `button_press_topdown_wall`, `coffee_push`, `door_lock`, `hammer`, `handle_pull_side`, `plate_slide`, plus `easy`/`medium`/`hard` mixes. [IVG-PAPER, Sec. 4.3, Appendix B.4; IVG-CODE, `mbrl/`]

### 4.1 VP2 Table 6 (iVideoGPT column)

| Task | iVideoGPT success |
|---|---:|
| Robosuite push | **0.7833** |
| Open drawer | 0.3750 |
| Blue button | 0.9556 |
| Red button | 0.9222 |
| Open slide | **0.1611** (SVG′ 0.5733) |
| Flat block | near floor for all learned models |

VP2 data: 5k Robosuite and 35k RoboDesk trajectories. Weak open-slide is attributed to discretization and VP2 rewards, not claimed as a tokenizer win. [IVG-PAPER, Table 6, Fig. 5]

## 5. Named checkpoints versus later work

Released OXE names in the pinned README:

- `thuml/ivideogpt-oxe-64-act-free` (114M tok + 138M trm)
- `thuml/ivideogpt-oxe-64-act-free-medium` (436M transformer)
- `thuml/ivideogpt-oxe-64-goal-cond`
- `thuml/ivideogpt-oxe-256-act-free`

README states there is **no OXE action-conditioned** model because action spaces are heterogeneous. Downstream act-cond checkpoints are BAIR/RoboNet/VP2-specific. Collection `thuml/ivideogpt-674c59cae32231024d82d6c5` groups these. **RLVR-World 2025 is not an iVideoGPT table** and must not be used as OXE-act-cond evidence. [IVG-CODE README; IVG-HF-COLLECTION]

[`sources.yaml`](sources.yaml) lists `ivideogpt-oxe-64-act-cond` and `ivideogpt-oxe-medium` / `ivideogpt-oxe-256` as Hub titles; bind claims to the README names above when they differ.

## 6. Limits

- MAGVIT wins BAIR action-free FVD; FitVid wins RoboNet 64 FVD/PSNR/LPIPS.
- Open-slide VP2 is weak; discretization and VP2 rewards are blamed.
- No public OXE act-cond WM.
- 256x256 RoboNet weights missing from Hub.
- MBRL numbers live in figures; exact Meta-World success rates were not a single HTML table.
- Training/inference not executed here.

## 7. Cosmos3 attachment map

| iVideoGPT mechanism | Cosmos3 surface | Not this surface |
|---|---|---|
| Compressive ctx VQ | Generator visual tokenizer / FD tokens | Reasoner |
| Action / goal / reward AR tokens | Generator FD/WAM | RLVR-World 2025 |
| OXE unlabeled pretrain | video FD pretrain | OXE act-cond Hub as pretrain |
| MBPO imagination | WAM rollouts for control | DreamerV3 Nature tables |

## 8. Released script contract

| Goal | Script | Notes |
|---|---|---|
| OXE act-free 64 | `scripts/pretrain/oxe-64-act-free.sh` | 114M+138M |
| OXE medium | `oxe-64-act-free-medium.sh` | 436M transformer |
| OXE goal | `oxe-64-goal-cond.sh` | still action-free OXE |
| OXE 256 | `oxe-256-act-free.sh` | README: undertrained start |
| BAIR act-cond | `scripts/finetune/bair-64-act-cond.sh` | Table 1 act-cond row |
| RoboNet 64 | `scripts/finetune/robonet-64-act-cond.sh` | FitVid still wins some cells |
| RoboNet 256 | `robonet-256-act-cond.sh` | Hub weights deleted |
| VP2 | `vp/script.sh`, `vp/ivideogpt_interface.py` | Table 6 |
| MBPO | `mbrl/train_metaworld_mbpo.py` | rewrite YAML paths |

Tokenizer finetune example from README (documented, not executed): `accelerate launch train_tokenizer.py --model_type ctx_vqgan --oxe_data_mixes_type bair --resolution 64 --segment_length 8 --context_length 1 --max_train_steps 200005`. Transformer: `train_gpt.py --action_conditioned --action_dim 4 --max_train_steps 100005`. [IVG-CODE README]

### 8.1 OXE mixture note

About **1.4 million** trajectories: 35 OXE datasets after Octo-like filtering plus Something-Something v2 (95 motion classes, 15% mixture weight) for the tokenizer. Transformer pretraining uses OXE only. 1% per subset held out. Extract via `datasets/oxe_data_converter.py` for every name in `OXE_SELECT` (`ivideogpt/data/dataset_mixes.py`). [IVG-PAPER, Sec. 3, Appendix A.2, Table 4]

### 8.2 Low-data finetune

With 1000 action-conditioned BAIR trajectories after pretrain, FVD 82.3 (prose, not Table 1). Pretraining helps most at 100–1000 downstream trajectories. This is the two-stage transfer (`IVIDEO-XFER-08`), not an OXE act-cond Hub file. [IVG-PAPER, Sec. 4.1]

### 8.3 Architecture recap

```text
E_c(context frames) -> high-res context codes
E_p(future frames | context) -> 4x4 dynamics codes, codebook 8192
AR transformer (12x768=138M or 24x1024=436M)
  optional: action tokens, goal frame, symlog reward
D_p(future codes | context features) -> RGB
```

Independent `16x16` per-frame tokens OOM at the paper AR setting. MAGVIT still wins BAIR action-free FVD; FitVid still wins RoboNet 64 FVD. [IVG-PAPER, Tables 1, 2, 7-8]

Human study: 386 annotations, 9 participants, action-free BAIR versus VideoGPT and MCVD (Fig. 20). MBRL curves versus DreamerV3 ± pretraining live in figures; FitVid-as-WM loses on 5/6 Meta-World tasks (Fig. 21). [IVG-PAPER, Appendix B.2, B.4]

## Sources

- [IVG-PAPER] arXiv:2405.15223v3.
- [IVG-CODE] `thuml/iVideoGPT@d601d5cac9e96c6aa0c17cb37ed6a7c7ca1fb210`.
- Named Hub cards in [`sources.yaml`](sources.yaml).
