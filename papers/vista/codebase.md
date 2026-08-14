---
id: world-model-kb.papers.vista.codebase
title: Vista Released Implementation Graph
kind: reference
status: maintained
last_updated: 2026-08-14
owners:
  - AIBuildAI world-model group
---

# Vista Released Implementation Graph

## Retrieval metadata

**Relevant queries:** OpenDriveLab Vista, sample.py, train.py, reward.py, vista_phase1.yaml, vwm/modules, --low_vram, --action traj, or vista.safetensors EMA.

**Knowledge provided:** pinned commit file map, training/sampling graphs, control-mode flags, EMA-merge warning, and paper-code gaps.

**Related pages:** [`paper.md`](paper.md); [`reproduction.md`](reproduction.md); [Cosmos3-Nano Generator](../../models/cosmos3-nano/generator.md).

## 1. Revision policy

Inspected tree: `OpenDriveLab/Vista@cc9821b4253ca7987c32757613d2fc2448fa9f5d` (2025-07-02), Apache-2.0. Ancestry is Stability AI `generative-models` (SVD). [VISTA-CODE]

Hugging Face `OpenDriveLab/Vista` hosts `vista.safetensors`. README: **earlier EMA merge error — download the latest file**. [VISTA-HF]

This repository is not Wayve GAIA.

## 2. Tree at the pinned commit

```text
train.py                         # DeepSpeed ZeRO-2 training
sample.py / sample_utils.py      # DDIM sampling, control modes
reward.py / reward_utils.py      # ensemble reward without GT actions
bin_to_st.py                     # pytorch_model.bin -> vista.safetensors
init_proj_path.py
configs/example/nusc_train.yaml
configs/inference/vista.yaml
configs/training/vista_phase1.yaml
configs/training/vista_phase2_stage1.yaml
configs/training/vista_phase2_stage2.yaml
docs/INSTALL.md, TRAINING.md, SAMPLING.md, ISSUES.md
vwm/models/diffusion.py
vwm/models/autoencoder.py
vwm/modules/diffusionmodules/video_model.py
vwm/modules/diffusionmodules/sampling.py
vwm/modules/diffusionmodules/guiders.py
vwm/modules/diffusionmodules/loss.py
vwm/modules/encoders/modules.py  # action/condition encoders
vwm/modules/ema.py
vwm/data/dataset.py
vwm/data/subsets/nuscenes.py
vwm/data/subsets/youtube.py
vwm/data/subsets/common.py
```

Pinned-commit blobs that implement the graphs below (sizes from GitHub tree JSON):

| Path | Bytes | Role |
|---|---:|---|
| `train.py` | 34532 | DeepSpeed ZeRO-2 entry |
| `sample.py` | 9454 | DDIM sampling CLI |
| `sample_utils.py` | 12794 | overlap decode, control packing |
| `reward.py` | 8890 | ensemble reward CLI |
| `reward_utils.py` | 11280 | variance-to-reward |
| `bin_to_st.py` | 2002 | `pytorch_model.bin` to safetensors |
| `configs/training/vista_phase1.yaml` | 7126 | 576x1024 unlabeled OpenDV |
| `configs/training/vista_phase2_stage1.yaml` | 8594 | 320x576 LoRA control |
| `configs/training/vista_phase2_stage2.yaml` | 8595 | 576x1024 control adaptation |
| `configs/inference/vista.yaml` | 5760 | sampler / CFG |
| `configs/example/nusc_train.yaml` | 8574 | **debug**, not paper phase 1 |
| `vwm/modules/diffusionmodules/loss.py` | 7206 | EDM + dynamics + structure |
| `vwm/modules/diffusionmodules/guiders.py` | 4167 | triangular CFG |
| `vwm/modules/diffusionmodules/video_model.py` | 18609 | SVD-style UNet |
| `vwm/modules/encoders/modules.py` | 18691 | Fourier action / condition |
| `vwm/modules/ema.py` | 3222 | EMA (Hub merge historically broken) |
| `vwm/data/subsets/nuscenes.py` | 3894 | edit `data_root` |
| `vwm/data/subsets/youtube.py` | 999 | OpenDV layout |
| `docs/TRAINING.md` | 4815 | 128-GPU / 8-GPU recipes |
| `docs/SAMPLING.md` | 2773 | `--n_rounds`, `--low_vram`, `--action` |

## 3. Training graph

```text
torchrun train.py --base configs/training/vista_phase*.yaml
  -> vwm data (youtube.py / nuscenes.py)
  -> SVD UNet + EDM loss (vwm/modules/diffusionmodules/loss.py)
  -> optional LoRA on attention (phase 2)
  -> DeepSpeed ZeRO-2 shards
  -> merge: zero_to_fp32.py then bin_to_st.py -> ckpts/vista.safetensors
```

Documented launches [VISTA-CODE, `docs/TRAINING.md`]:

- Phase 1: `--base configs/training/vista_phase1.yaml` with 16 nodes x 8 GPUs (paper: 128 A100, 20K).
- Phase 2 stage 1: `vista_phase2_stage1.yaml --finetune ${PATH}/pytorch_model.bin` (8 GPUs, 120K).
- Phase 2 stage 2: `vista_phase2_stage2.yaml` (10K).
- Example/debug: `configs/example/nusc_train.yaml` on 1 GPU (not the paper recipe).

`vwm/data/subsets/nuscenes.py` requires editing `data_root`. SVD init weight `svd_xt.safetensors` is placed in `ckpts`. Training wants 80 GB GPUs; low-resolution variants may fit smaller devices.

## 4. Sampling graph

```text
python sample.py [--n_rounds 6] [--action traj|cmd|steer|goal] [--low_vram]
  -> load vista.safetensors (must match all keys)
  -> configs/inference/vista.yaml
  -> DDIM in vwm/modules/diffusionmodules/sampling.py
  -> guiders.py triangular CFG
  -> decode with 3-frame overlap
```

Flags from `docs/SAMPLING.md`: `--dataset` (nuScenes or `IMG` folder), `--n_rounds` (~2.3 s per extra round), `--n_steps`, `--rand_gen`, `--low_vram` (GPUs < 80 GB; 32 GB suggested minimum). Mismatched checkpoint keys yield a blur sequence.

## 5. Reward graph

```text
python reward.py --ens_size M
  -> sample futures per (frame, action)
  -> uncertainty -> scalar reward (reward.py, reward_utils.py)
```

This is the paper's GT-free reward surface. Default ensemble size is configurable; paper uses `M=5` and 10 denoising steps for reward, not the full 50-step showcase sampler. [VISTA-PAPER, Appendix C.6; VISTA-CODE]

## 6. Paper-code gap ledger

| ID | Evidence | Effect | Repair boundary |
|---|---|---|---|
| `DRIVE-CODE-GAP-01` | earlier Hub EMA merge error | blur / wrong weights | latest `vista.safetensors` only |
| `DRIVE-CODE-GAP-02` | `data_root` hardcoded in subset files | copied commands fail | record edited path hashes; no workstation filesystem location in the KB |
| `DRIVE-CODE-GAP-03` | example YAML is nuScenes debug, not 128-GPU phase 1 | under-training if copied as Vista | use `configs/training/vista_phase*.yaml` |
| `DRIVE-CODE-GAP-04` | DeepSpeed merge two-step | inference needs `bin_to_st.py` | retain both hashes |
| `DRIVE-CODE-GAP-05` | `--low_vram` undocumented quality delta | possible FVD regression | ablate versus full VRAM |
| `DRIVE-CODE-GAP-06` | no lockfile; `requirements.txt` only | env drift | external lock |
| `DRIVE-CODE-GAP-07` | Waymo/CODA eval code not a one-click table | Table 3 Waymo needs extra data | label as reconstruction |

## 7. Optimization change surfaces

| Intervention | Files | Controls |
|---|---|---|
| Control mode | `sample.py --action`; `vwm/modules/encoders/modules.py` | CFG, priors, sampler steps |
| Dynamic priors | condition-frame count in train YAML / sampler | clip length 25 |
| Auxiliary losses | `vwm/modules/diffusionmodules/loss.py` | `lambda_1`, `lambda_2` |
| Triangular CFG | `guiders.py` | `s_min`/`s_max` |
| LoRA control phase | phase 2 YAMLs | rank 16, freeze vs full |
| Reward ensemble | `reward.py --ens_size` | denoising steps 10 vs 50 |

## 8. Sampling and install docs (pinned)

`docs/INSTALL.md` (1578 B): 80 GB training GPUs; low-res variants may fit smaller devices. `docs/SAMPLING.md` (2773 B): `--n_rounds` (~2.3 s extra), `--action {traj,cmd,steer,goal}`, `--low_vram`, `--rand_gen`, `--n_steps`. `docs/ISSUES.md` (1308 B): known issues including blur from mismatched keys. `init_proj_path.py` (261 B) must run so `vwm` imports resolve. `vwm/modules/diffusionmodules/model.py` (23240 B) and `openaimodel.py` (10238 B) are SVD UNet ancestry. `vwm/modules/attention.py` (21922 B) and `video_attention.py` (9968 B) are the LoRA/control insertion points in phase 2.

Do not launch `configs/example/nusc_train.yaml` as Vista Phase 1. Merge path is always ZeRO `zero_to_fp32.py` then `bin_to_st.py`.

## 9. Remaining vwm blobs

`vwm/models/diffusion.py` (15142 B), `autoencoder.py` (20070 B), `denoiser.py` (2407 B), `discretizer.py` (2277 B), `sigma_sampling.py` (1320 B), `wrappers.py` (1430 B), `temporal_ae.py` (4923 B), `ema.py` (3222 B), `util.py` (5034 B), `data/dataset.py` (3619 B), `subsets/common.py` (3083 B). Control Fourier path: `vwm/modules/encoders/modules.py` (18691 B). These paths are the attachment points for `DRIVE-XFER-01` (encoders), `DRIVE-XFER-09` (`loss.py`), and `DRIVE-XFER-10` (`guiders.py`).

## Sources

- [VISTA-CODE] `cc9821b4253ca7987c32757613d2fc2448fa9f5d`.
- [VISTA-HF] latest `vista.safetensors`.
- [VISTA-PAPER] claimed recipes.
