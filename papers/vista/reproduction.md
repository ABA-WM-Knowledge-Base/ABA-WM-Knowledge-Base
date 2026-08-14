---
id: world-model-kb.papers.vista.reproduction
title: Vista Reproduction State and Experiment Contracts
kind: record
status: maintained
last_updated: 2026-08-14
owners:
  - AIBuildAI world-model group
---

# Vista Reproduction State and Experiment Contracts

## Retrieval metadata

**Relevant queries:** Vista reproduced, sample.py, vista.safetensors EMA, --action traj, --low_vram, reward.py, phase1 training, nuScenes FVD 89.4.

**Knowledge provided:** inspection-only execution state, documented commands from the pinned tree, EMA warning, and Table 2/3 contracts. No training or inference was run.

**Related pages:** [`codebase.md`](codebase.md); [`paper.md`](paper.md); [evaluation methodology](../../foundations/data-and-evaluation/evaluation-methodology.md).

## 1. Current execution state

| Surface | Evidence state | Recorded evidence | Permitted claim |
|---|---|---|---|
| NeurIPS paper | source inspected | ar5iv HTML of arXiv:2405.17398; Tables 2-5 and Eqs. 2-9 extracted | Numbers in this entry were read from the paper. |
| GitHub tree | source inspected | API recursive tree at `cc9821b4253ca7987c32757613d2fc2448fa9f5d`; README, TRAINING.md, SAMPLING.md, INSTALL.md | File names, byte sizes, and flags are real. |
| Hub weights | metadata inspected | README EMA-merge warning | Latest `vista.safetensors` not downloaded or hashed. |
| SVD init `svd_xt.safetensors` | documented | TRAINING.md Hugging Face URL | Not fetched. |
| `python sample.py` | not attempted | documented | No video generated. |
| `python reward.py` | not attempted | documented | No reward scalar. |
| Phase 1/2 training | not attempted | 128/8 A100 recipes documented | No optimizer step. |
| Table 2 FID/FVD | not attempted | paper-only | Not reproduced. |
| Table 3 IDM | not attempted | paper-only | Not reproduced. |

Static inspection is not inference. Source availability is not checkpoint integrity. No row may be promoted without an immutable run record.

## 2. Reproduction vocabulary

- **Documented:** a pinned paper or repository describes a behavior.
- **Source inspected:** relevant pages or files were reconciled.
- **Artifact reachable:** an immutable URL responds.
- **Artifact verified:** complete file SHA256 retained.
- **Executed:** a command completes with raw artifacts.
- **Metric reproduced:** pinned checkpoint and protocol yield the declared metric within a predeclared tolerance.
- **Paper result reproduced:** model, data, code, evaluator, sampling, and aggregation identities match the named table.

These terms do not prescribe workflow or experiment priority.

## 3. Artifact and environment boundary

Sampling docs suggest ≥32 GB VRAM; `--low_vram` for GPUs under 80 GB. Training docs require 80 GB GPUs for the paper recipe; low-resolution variants may fit smaller devices. OpenDV-YouTube plus nuScenes are large; a valid smoke need not download all of OpenDV but must hash every selected archive and the exact `vista.safetensors` revision after the EMA-merge fix. [VISTA-CODE, `docs/INSTALL.md`, `docs/SAMPLING.md`; VISTA-HF; VISTA-OPENDV]

Discard any local copy known to predate the EMA-merge fix. `vwm/data/subsets/nuscenes.py` requires editing `data_root`; record a hash of the edited file, not a workstation path, in this KB.

`requirements.txt` is 743 bytes and is not a lockfile. INSTALL.md is an installation hint.

## 4. Commands documented, not executed

### 4.1 Clone and weights

```bash
git clone https://github.com/OpenDriveLab/Vista.git
cd Vista
git checkout cc9821b4253ca7987c32757613d2fc2448fa9f5d
# follow docs/INSTALL.md
# place latest vista.safetensors in ckpts/ (post-EMA-fix Hub revision)
# training also needs svd_xt.safetensors in ckpts/
```

### 4.2 Sampling (smoke candidate)

```bash
python sample.py
python sample.py --n_rounds 6
python sample.py --action traj
python sample.py --action cmd
python sample.py --action steer
python sample.py --action goal
python sample.py --low_vram
python reward.py
```

Record Hub revision, file SHA256, `--dataset` (nuScenes or `IMG`), `n_steps`, CFG, action mode, and whether `--low_vram` was set. Mismatched checkpoint keys yield a blur sequence. This is **not** Table 2.

### 4.3 Training (paper-scale, not a smoke)

```bash
torchrun --nnodes=16 --nproc_per_node=8 train.py \
  --base configs/training/vista_phase1.yaml --num_nodes 16 --n_devices 8
```

Phase 2 stage 1 (8 GPUs, 120K, 320x576) and stage 2 (10K, 576x1024) use `--finetune ${PRIOR}/pytorch_model.bin`. Do not treat `configs/example/nusc_train.yaml` as Phase 1. Merge ZeRO shards with `zero_to_fp32.py`, then `bin_to_st.py` to `ckpts/vista.safetensors`. Single-GPU `python train.py ... --n_devices 1` is documented as too slow.

## 5. Minimum smoke contract

**Executed smoke (sample):** pinned commit, latest Hub file SHA256, one nuScenes or `IMG` condition frame, `sample.py` completes, MP4 non-empty, action mode recorded, CFG and `n_steps` recorded.

**Executed smoke (reward):** `reward.py` returns a finite scalar for GT versus random command on one clip; ensemble size recorded.

Neither smoke is Table 2 or Table 3.

## 6. Table 2 / Table 3 metric contract

**Table 2 bind:** 5369 valid nuScenes validation clips; FID crop/resize to `256 x 448`; FVD all 25 frames downsampled to `224 x 224` following LVDM; latest `vista.safetensors`; 50-step DDIM unless a recorded ablation; compare to cited baselines only if rerun or clearly marked imported. Targets: FID **6.9**, FVD **89.4**.

**Table 3 bind:** 537 samples per dataset; IDM L2 over 2 s; 1/2/3 priors; Waymo held out of training; report action-free and each control mode separately.

Predeclare tolerances before claiming reproduction. Do not average FID into IDM.

## 7. Identity checklist

| Check | Required value | Status |
|---|---|---|
| Paper | arXiv:2405.17398 | source inspected |
| Commit | `cc9821b4253ca7987c32757613d2fc2448fa9f5d` | source inspected |
| Weights | latest Hub `vista.safetensors` SHA256 | not recorded |
| Not GAIA | no Wayve checkpoints mixed | documented |
| Phase YAML | `vista_phase*.yaml` for train claims | documented |
| Action mode | one of traj/cmd/steer/goal or free | not executed |
| Data identity | hashed nuScenes / OpenDV subset | not recorded |

## 8. Run-record template

```text
Experiment ID:
Commit SHA:
vista.safetensors SHA256 (post-EMA-fix revision):
Action mode:
n_rounds / n_steps / low_vram / CFG:
Data-root identity (hashed):
Outputs SHA256:
FID / FVD / IDM L2:
Acceptance:
Evidence conclusion:
```

No run record is registered.

## 9. Non-goals for this KB session

This session does not train, does not sample, does not download Hub weights, and does not push GitHub. Commands above are documentation. Promoting any row to **executed** requires a later run record with hashes.

OpenDV hours (~1735) and 128-GPU Phase 1 are paper/code documented recipes, not local jobs. Waymo Table 3 is zero-shot relative to training, not a claim that Waymo data were used in Phase 1.

## 10. Training and metric reproducibility boundary

| Regime | Publicly recoverable | Missing for exact reproduction |
|---|---|---|
| `sample.py` smoke | commit, action flags, `--low_vram` | post-EMA `vista.safetensors` SHA256, condition-frame hash |
| Table 2 FID/FVD | 5369 clips; FID 256x448; FVD 25 frames 224x224 LVDM | evaluator code pin, 50-step DDIM, imported-baseline flag |
| Table 3 IDM | 537 samples/dataset; 1/2/3 priors; 2 s L2 | IDM weights, Waymo hold-out confirmation |
| Table 4 reward | `reward.py`; GT 0.892 vs random 0.878 | ensemble size; small 0.014 gap must stay labeled |
| Table 5 stop FVD | 132.3 -> 118.9 | stop-control subset identity |
| Phase 1 train | `vista_phase1.yaml`, 16x8 A100, 20K | OpenDV shard hashes; `nusc_train.yaml` is **not** Phase 1 |
| Phase 2 | 320x576 then 576x1024 | ZeRO merge via `zero_to_fp32.py` then `bin_to_st.py` |

Discard any `vista.safetensors` known to predate the EMA-merge fix. This entry is not Wayve GAIA.

## 11. Acceptance checks that must not be skipped

1. Action mode is one of traj / cmd / steer / goal / free.
2. Table 2 targets FID **6.9** and FVD **89.4** only under the 5369-clip protocol.
3. Reward GT-versus-random 0.014 is not treated as a large causal gap.
4. `--low_vram` is recorded; it is a memory path, not a quality identity.
5. No Wayve checkpoints mixed into Hub or run records.

## Sources

- [VISTA-PAPER] protocol and Tables 2-5.
- [VISTA-CODE] `sample.py`, `train.py`, `docs/TRAINING.md`, `docs/SAMPLING.md`.
- [VISTA-HF] latest `vista.safetensors`.
- [VISTA-OPENDV] training-data identity.
