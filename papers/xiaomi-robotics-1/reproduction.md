---
id: world-model-kb.papers.xiaomi-robotics-1.reproduction
title: Xiaomi-Robotics-1 Reproduction State and Experiment Contracts
kind: record
status: maintained
last_updated: 2026-08-21
owners:
  - AIBuildAI world-model group
---

# Xiaomi-Robotics-1 Reproduction State and Experiment Contracts

## Retrieval metadata

**Relevant queries:** Xiaomi-Robotics-1 reproduced, VLABench table reproduction, RoboCasa table reproduction, documented commands, not attempted, blockers, hardware identity, what can be reproduced from public artifacts.

**Knowledge provided:** the current non-execution state per surface, documented commands, known blockers, and the minimum contracts that would promote a row from documented to executed.

**Related pages:** [`codebase.md`](codebase.md) owns the released surface; [`paper.md`](paper.md) owns reported values; [model reproduction ledger](../../models/xiaomi-robotics-1/reproduction.md) owns the campaign-side contracts; [evaluation methodology](../../foundations/data-and-evaluation/evaluation-methodology.md) owns comparison validity.

## 1. Current execution state

| Surface | Evidence state | Recorded evidence | Permitted claim |
|---|---|---|---|
| Paper identity | source inspected | arXiv:2607.15330v1 [XR1-TR] | Tables and sections cited here were read from the snapshot |
| Official repository | source inspected | pinned commit `556cca33…` [XR1-CODE] | READMEs, configs, trainer, servers, eval clients inspected; no command run |
| HF checkpoints | metadata inspected | cards, file lists, `preprocessor_config.json`, `model.safetensors.index.json` [XR1-HF-VLABENCH; XR1-HF-5B] | Artifacts advertised; inner tensors not loaded locally |
| Table 4 (VLABench) | not attempted | none | 59.1 remains paper-reported |
| Table 2/3 (RoboCasa/365) | not attempted | none | |
| Table 5 (RoboDojo) | not reproducible from release | no checkpoint | |
| Table 6 (real robot) | not reconstructable | in-house robots and data | |
| Scaling curves | not reproducible | no pre-training code or corpus | |
| Pre-training | not reproducible | corpus and code absent | |

Static inspection is not inference reproduction.

## 2. Reproduction vocabulary

Documented; source inspected; artifact reachable; artifact verified (SHA256 + structure); executed (command completed in a recorded environment with raw artifacts); metric reproduced (pinned checkpoint and protocol within a predeclared tolerance); paper result reproduced (model, data, code, evaluator, sampling, aggregation matched). None of the last three is claimed here.

## 3. Artifact and environment boundary

Documented serving: Python 3.12, torch 2.8.0 cu128, transformers 4.57.1, flash-attn 2.8.3; ~13 GB VRAM per server. Documented evaluation: a second Python 3.10 environment with MuJoCo 3.2.2 / dm_control 1.0.22 and the VLABench assets (Google Drive). Training of the fine-tunes: undisclosed hyperparameters; the public trainer's data path does not match the VLABench checkpoint's conventions. [XR1-CODE; XR1-CODE-EVAL-VLABENCH; XR1-ISSUE-12]

## 4. Documented commands, not executed

```bash
# serving (env mibot)
hf download XiaomiRobotics/Xiaomi-Robotics-1-VLABench --local-dir "$MODEL_PATH"
bash scripts/deploy.sh "$MODEL_PATH" 8 8
# evaluation (env vlabench, VLABENCH_ROOT set, EGL)
bash scripts/launch_vlabench.sh 8 ./eval_vlabench/eval_logs "$MODEL_PATH"
# smoke
NUM_EVAL_EPISODES=1 bash scripts/launch_vlabench.sh 1 ./eval_vlabench/eval_logs_smoke "$MODEL_PATH"
# post-training (env xr1, from xr1/)
RESOURCE_GPU=8 bash scripts/train.sh trainer.project=p trainer.exp_name=e data=<cfg> model=posttrain model.params.pretrained=pretrained_ckpt/model_states.pt
```

[XR1-CODE-EVAL-VLABENCH; XR1-CODE-XR1-README]

## 5. Minimum contracts to promote a row

- **Table 4 reproduced:** the released VLABench dir, the pinned VLABench commit, 50 configs per task per track, client defaults, per-track SR/PS/IS within 2 standard errors (about 2 pp on the average; about 7 pp per cell), full artifact bundle retained.
- **Serving executed:** one decoded chunk of shape (10, 60) from a real observation, with the seed and processor identity recorded.
- **Training executed:** a smoke from the 5B base with the public demo data, loss finite, environment recorded.

## Sources

[XR1-TR]; [XR1-CODE]; [XR1-CODE-XR1-README]; [XR1-CODE-EVAL-VLABENCH]; [XR1-HF-VLABENCH]; [XR1-HF-5B]; [XR1-ISSUE-12].
