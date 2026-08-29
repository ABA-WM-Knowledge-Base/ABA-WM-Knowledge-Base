---
id: world-model-kb.papers.vlabench.reproduction
title: VLABench Reproduction State and Protocol Contracts
kind: record
status: maintained
last_updated: 2026-08-21
owners:
  - AIBuildAI world-model group
---

# VLABench Reproduction State and Protocol Contracts

## Retrieval metadata

**Relevant queries:** VLABench installed, assets downloaded, evaluator executed, track run, baseline checkpoint evaluated, episode wall clock, not attempted, what promotes a row.

**Knowledge provided:** the current non-execution state, the documented installation and evaluation commands, blockers, and the contracts that would promote a surface to executed.

**Related pages:** [`codebase.md`](codebase.md) owns the call graph; [`paper.md`](paper.md) owns the protocol; [Xiaomi-Robotics-1 reproduction](../../models/xiaomi-robotics-1/reproduction.md) owns the policy-side contracts that depend on this benchmark being executable.

## 1. Current execution state

| Surface | Evidence state | Recorded evidence | Permitted claim |
|---|---|---|---|
| Paper | source inspected | arXiv:2412.18194 [VLAB-PAPER] | Design and legacy protocol read |
| Repository | source inspected | pinned commit [VLAB-CODE] | Evaluator, tracks, pins inspected; not installed |
| Track files | artifact inspected | task and config counts per track | 10 tasks per track, 50 configs (Track 2 `insert_flower` 10) |
| Assets | not attempted | Google Drive ids only | Size unknown until download |
| Dataset | metadata inspected | `meta/info.json`, `meta/episodes`, `stats.json` [VLAB-DATA-LEROBOT] | Field layout and ranges known; videos not decoded |
| Evaluator execution | not attempted | none | No episode has been run |
| Baseline checkpoints (pi0 family) | metadata inspected | org listing [VLAB-HF-ORG] | Track-1 numbers remain maintainer-reported |

## 2. Documented installation and evaluation

```bash
conda create -n vlabench python=3.10 && conda activate vlabench
git clone https://github.com/OpenMOSS/VLABench.git && cd VLABench && git checkout cf588fe60c0c7282174fe979f5913170cfe69017
pip install -r requirements.txt && pip install -e .
python scripts/download_assets.py            # obj.zip + scene.zip from Google Drive (gdown)
export VLABENCH_ROOT=$PWD/VLABench MUJOCO_GL=egl
python scripts/evaluate_policy.py --policy openpi --host ... --port ... --eval-track track_1_in_distribution --n-episode 50
```

Evaluation "of each task in a single process typically takes around 30 minutes to 1 hour"; multi-GPU parallel evaluation via `sh/evaluation/example_multi_gpu_eval.sh`. [VLAB-CODE README]

## 3. Blockers and environment notes

- Assets come from Google Drive; availability and size are not pinned in the repository.
- `requirements.txt` pins a `lerobot` git commit and `numpy==1.25.0`; Xiaomi's recipe installs VLABench with `--no-deps` after the requirements and force-reinstalls the MuJoCo/dm_control pins, then adds torch 2.8 and transformers 4.57.1. Expect resolver conflicts if the order changes. [VLAB-CODE; XR1-CODE-EVAL-VLABENCH]
- Headless rendering needs `MUJOCO_GL=egl` and the GL system libraries (`docs/issues.md`).
- Evaluator defects (issues 55, 80, 82, 88) are open at the pin; a reproduction must record their effect on IS/PS.

## 4. Contracts to promote a row

- **Benchmark executed:** one track, one task, one episode through `Evaluator` with a random or scripted policy; record wall clock, rendering backend, and the metrics dict.
- **Baseline reproduced:** a released pi0-family checkpoint through the openpi server on Track 1, 50 configs per task, SR within ~7 pp per task of the README number.
- **Protocol fixed:** record the VLABench commit, the track file hashes, and the per-task episode caps alongside any policy result.

## Sources

[VLAB-PAPER]; [VLAB-CODE] README, `requirements.txt`, `docs/issues.md`; [VLAB-DATA-LEROBOT]; [VLAB-HF-ORG]; [XR1-CODE-EVAL-VLABENCH]; [VLAB-ISSUE-55]; [VLAB-ISSUE-80]; [VLAB-ISSUE-82]; [VLAB-ISSUE-88].
