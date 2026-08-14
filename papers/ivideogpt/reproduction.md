---
id: world-model-kb.papers.ivideogpt.reproduction
title: iVideoGPT Reproduction State and Experiment Contracts
kind: record
status: maintained
last_updated: 2026-08-14
owners:
  - AIBuildAI world-model group
---

# iVideoGPT Reproduction State and Experiment Contracts

## Retrieval metadata

**Relevant queries:** iVideoGPT reproduced, predict.py, oxe-64-act-free, train_gpt.py, Meta-World MBPO, RLVR-World not in scope.

**Knowledge provided:** inspection-only state, documented commands, checkpoint naming contract. No training or inference executed.

**Related pages:** [`codebase.md`](codebase.md); [`paper.md`](paper.md); [evaluation methodology](../../foundations/data-and-evaluation/evaluation-methodology.md).

## 1. Current execution state

| Surface | Evidence state | Recorded evidence | Permitted claim |
|---|---|---|---|
| Paper v3 | source inspected | ar5iv HTML of arXiv:2405.15223; Tables 1, 2, 6-8 extracted | Numbers inspected. |
| GitHub | source inspected | recursive tree at `d601d5cac9e96c6aa0c17cb37ed6a7c7ca1fb210`; README | Scripts and byte sizes are real. |
| Hub collection | metadata inspected | `thuml/ivideogpt-674c59cae32231024d82d6c5` names in README | Inner SHA256s not registered. |
| `inference/predict.py` | not attempted | documented | No video. |
| Tokenizer / transformer train | not attempted | none | No loss curve. |
| Table 1 metrics | not attempted | paper-only | Not reproduced. |
| VP2 / MBPO | not attempted | scripts present | Not reproduced. |
| RLVR-World | out of scope | README news only | Not iVideoGPT evidence. |

Static inspection is not inference. No row may be promoted without an immutable run record.

## 2. Reproduction vocabulary

- **Documented:** a pinned paper or repository describes a behavior.
- **Source inspected:** relevant pages or files were reconciled.
- **Artifact reachable:** an immutable URL responds.
- **Artifact verified:** complete file SHA256 retained.
- **Executed:** a command completes with raw artifacts.
- **Metric reproduced:** pinned checkpoint and protocol yield the declared metric within a predeclared tolerance.
- **Paper result reproduced:** model, data, code, evaluator, and aggregation identities match the named table.

## 3. Artifact and environment boundary

OXE occupies about 5 TB. Smoke should use `inference/samples/fractal_sample.npz` plus one named OXE act-free checkpoint. FVD needs I3D `pretrained_models/i3d/i3d_torchscript.pt` from the README Dropbox URL. Python 3.9 in README; `requirements.txt` is not a lockfile. 64x64 fits ~24 GB/device; 256x256 needs ~40 GB. [IVG-PAPER, Appendix C; IVG-CODE]

`mbrl/cfgs/mbpo_config.yaml` uses absolute paths. Do not copy those paths into this KB; rewrite them in a recorded derivative before any MBRL smoke.

Tsinghua Cloud is documented as a Hub fallback. Treat it as an alternate URL, not a different model.

## 4. Commands documented, not executed

```bash
git clone https://github.com/thuml/iVideoGPT.git
cd iVideoGPT
git checkout d601d5cac9e96c6aa0c17cb37ed6a7c7ca1fb210
conda create -n ivideogpt python==3.9
conda activate ivideogpt
pip install -r requirements.txt

python inference/predict.py \
  --pretrained_model_name_or_path "thuml/ivideogpt-oxe-64-act-free" \
  --input_path inference/samples/fractal_sample.npz \
  --dataset_name fractal20220817_data
```

Finetune examples: `scripts/finetune/bair-64-act-cond.sh`, `robonet-64-act-cond.sh`, `robonet-256-act-cond.sh`. Eval: `bash ./scripts/evaluation/bair-64-act-cond.sh`. Pretrain: `bash ./scripts/pretrain/oxe-64-act-free.sh` (and medium / goal / 256 variants). OXE extract: `python datasets/oxe_data_converter.py --dataset_name bridge --input_path ... --output_path ...` for every name in `OXE_SELECT` (`ivideogpt/data/dataset_mixes.py`).

MBRL:

```bash
pip install git+https://github.com/Farama-Foundation/Metaworld.git@83ac03ca3207c0060112bfc101393ca794ebf1bd
python mbrl/train_metaworld_mbpo.py task=plate_slide num_train_frames=100002 demo=true
```

Do not download RLVR-World weights for these contracts. Do not claim OXE action-conditioned prediction from official OXE Hub names.

## 5. Minimum smoke contract

Pinned commit; Hub id `thuml/ivideogpt-oxe-64-act-free` hashed; sample npz hashed; `predict.py` writes a video with expected frame count; conditioning mode recorded as action-free. This is **not** Table 1.

## 6. Table 1 metric contract

**BAIR:** 43k train / 256 test; 15 frames from 1; best-of-100 for PSNR/SSIM/LPIPS; FVD uses all 100; SSIM/LPIPS scaled x100; three runs. Bind act-free versus act-cond checkpoints explicitly (`ivideogpt-bair-64-act-free` vs `...-act-cond`).

**RoboNet:** 162k / 256 test; 10 frames from 2; overlapping OXE test clips filtered. 256 RoboNet weights may be absent; if so, drop the 256 row rather than substituting OXE-256-act-free.

Predeclare tolerances. Do not mix MAGVIT's action-free FVD win into an "iVideoGPT SOTA" sentence without the PSNR/SSIM/LPIPS columns.

## 7. Identity checklist

| Check | Required value | Status |
|---|---|---|
| Paper | arXiv:2405.15223 **v3** | source inspected |
| Commit | `d601d5cac9e96c6aa0c17cb37ed6a7c7ca1fb210` | source inspected |
| Hub name | README name, not YAML alias alone | documented |
| RLVR-World | excluded | documented |
| I3D | hashed if FVD is claimed | not recorded |
| Meta-World | commit `83ac03c...` if MBPO | not attempted |

## 8. Run-record template

```text
Experiment ID:
Commit:
Hub id (act-free|goal-cond|bair-act-cond|...):
SHA256 weights and npz:
Command:
Metrics (FVD/PSNR or success):
RLVR-World involved? (must be no):
Evidence conclusion:
```

No run record is registered.

## 9. Non-goals for this KB session

No training, no `predict.py`, no FVD, no MBPO. Do not fetch RLVR-World. Do not treat Tsinghua Cloud as a different model — only as a URL fallback. OXE ~5 TB is out of smoke scope.

## 10. Training and metric reproducibility boundary

| Regime | Publicly recoverable | Missing for exact reproduction |
|---|---|---|
| Act-free smoke | `predict.py`, fractal npz, `thuml/ivideogpt-oxe-64-act-free` | inner SHA256, frame-count check |
| BAIR Table 1 | 43k/256 split, 15-from-1, best-of-100, FVD-all-100 | I3D hash, three-run seeds, act-free vs act-cond Hub files |
| RoboNet 64 | 162k/256, 10-from-2, OXE-overlap filter | FitVid comparison code, FVD protocol |
| RoboNet 256 | paper numbers | **Hub weights may be deleted**; do not substitute OXE-256 |
| VP2 Table 6 | `vp/script.sh` | IsaacGym pin, 0.1611 open-slide evaluator |
| MBPO Meta-World | `train_metaworld_mbpo.py`, Meta-World `83ac03c` | rewritten YAML paths (do not copy absolute paths), figure-only success |
| OXE pretrain | 35-dataset mix, ~1.4M traj, 5 TB | full shards; smoke uses one npz |

[IVG-HF-OXE-64-ACT-COND] is a **named Hub identity**, not OXE pretrain evidence. [IVG-HF-OXE-256] is a long-context card, not RoboNet-256 Table 1.

## 11. Acceptance checks that must not be skipped

1. Camera-ready paper is arXiv:2405.15223 **v3**.
2. RLVR-World 2025 weights are excluded.
3. MAGVIT BAIR action-free FVD 62.0 remains in the table (iVideoGPT 75.0 is not a universal FVD win).
4. Conditioning mode (act-free / act-cond / goal) is recorded as an identity.
5. 256 RoboNet row is dropped if the Hub file is absent rather than silently swapped.

## Sources

- [IVG-PAPER] Table 1 protocol.
- [IVG-CODE] `inference/predict.py`, `scripts/`.
- Hub cards in [`sources.yaml`](sources.yaml), including [IVG-HF-OXE-64-ACT-FREE], [IVG-HF-OXE-64-ACT-COND], [IVG-HF-OXE-256], [IVG-HF-OXE-64-GOAL-COND], [IVG-HF-OXE-MEDIUM].
