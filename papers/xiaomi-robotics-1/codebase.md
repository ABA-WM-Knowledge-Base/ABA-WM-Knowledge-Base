---
id: world-model-kb.papers.xiaomi-robotics-1.codebase
title: Xiaomi-Robotics-1 Released Implementation Versus Paper Surface
kind: reference
status: maintained
last_updated: 2026-08-21
owners:
  - AIBuildAI world-model group
---

# Xiaomi-Robotics-1 Released Implementation Versus Paper Surface

## Retrieval metadata

**Relevant queries:** Xiaomi-Robotics-1 code release, what is released, pre-training code absent, UMI corpus absent, xr1 post-training, eval scripts, checkpoint formats, paper-code mismatch, 2026-08-03 release.

**Knowledge provided:** the boundary between what the report describes and what the repository at the pinned revision implements, per mechanism; the checkpoint formats; and the mismatches that matter for reproduction and transfer.

**Related pages:** [`paper.md`](paper.md) owns claims; [model codebase map](../../models/xiaomi-robotics-1/codebase.md) owns the file-level graph of the released tree; [`reproduction.md`](reproduction.md) owns execution state.

## 1. Revision policy

All statements use `XiaomiRobotics/Xiaomi-Robotics-1@556cca33963a2b36d835a40374c3b4c8eef68401` (2026-08-17; release announced 2026-08-03) and the HF checkpoints pinned in the model entry. [XR1-CODE; XR1-HF-COLLECTION]

## 2. Released surface versus paper surface

| Capability | Paper | Pinned repo | Consequence |
|---|---|---|---|
| UMI pre-training (data, labeler, recipe) | Sec. 4, Sec. 6 | absent | Stage 1 is not reproducible; the 5B base is the entry point |
| Cross-embodiment post-training recipe | Sec. 4 | `xr1/` generic post-training (configs for a 5-episode demo) | The mixture and 10K h data are absent; only the trainer is public |
| MoT architecture, losses, async prefix | Sec. 3 | `xr1/mibot/models/VLA/XR1.py` | Released and inspectable; choice/score heads present in the trainer, absent from HF inference weights |
| NTP vision-language loss (0.1) | Sec. 3 | absent (`skip_logits=True`, labels dropped) | Pre-training-only term; CoT NTP for VLABench is also absent |
| Benchmark fine-tunes | Tables 2-5 | HF inference checkpoints + eval clients for RoboCasa, RoboCasa365, VLABench; none for RoboDojo | Evaluation reproducible; training of the fine-tunes not |
| Real-robot deployment | Sec. 5.5 | `mibot/server` runtime, `docs/DEPLOYMENT.md` | Needs Xiaomi's state dict schema and a robot |
| Asynchronous inference | [8] | `action_prefix` in the runtime client and `async_train` in the model | Not used by the benchmark clients |

## 3. Checkpoint formats

| Artifact | Format | Loadable by |
|---|---|---|
| `Xiaomi-Robotics-1-5B/model_states.pt` | `{"module": {"model.<name>": tensor}}`, all trainer keys | `xr1` trainer (`BaseRunner`, strict) and `mibot/server/deploy.py` via a run dir layout |
| `-VLABench`, `-RoboCasa`, `-RoboCasa365` | HF safetensors (1,120 tensors), remote code, processor with `action_config` | `deploy/server.py`; NOT the trainer (15 training-only tensors missing: `*_choice` heads, `action_embed`, `score_embed`, untied `lm_head`) |
| `weight_convert.py` | HF -> trainer by prefixing `model.` | fails the strict load for benchmark fine-tunes unless the 15 training-only tensors are supplied (measured 2026-08-21) |

[XR1-CODE, `xr1/tools/weight_convert.py`, `xr1/mibot/models/runner/base_runner.py`; XR1-HF-5B; XR1-HF-VLABENCH]

## 4. Configuration resolution for evaluation

`scripts/deploy.sh <model> <num_ports> <num_gpus>` + `scripts/launch_vlabench.sh <num_ports> <log dir> [model]` with env knobs `BASE_PORT`, `NUM_EVAL_EPISODES`, `ROBOT_TYPE`, `ACTION_CHUNK_SIZE`, `REPLAN_STEPS`, `VISUALIZATION`, `COT`; `VLABENCH_ROOT` must point at the VLABench package dir. The launcher runs five tracks in order and merges. [XR1-CODE-EVAL-VLABENCH]

## 5. Documentation/code mismatches

- README states "2,500 rollouts" per the paper; the pinned VLABench track files give Track 2 `insert_flower` 10 configs (2,460 executable). [XR1-CODE-EVAL-VLABENCH; VLAB-CODE]
- The eval README's `COT=1` knob changes only the prompt suffix; the HF model has no text generation, so "CoT at inference" is not implemented. [XR1-HF-VLABENCH]
- The README says "transformers ecosystem (pinned to 4.57.1)"; the trainer's `requirements.txt` also pins `lightning==2.5.3`, `deepspeed==0.18.9`, `liger-kernel==0.6.5`, `decord==0.6.0`. [XR1-CODE-XR1-README]
- Issue-tracker pull requests (not merged at the pin) propose replacing the pickle socket protocol, binding servers to localhost, and capping payload sizes; the pinned server binds `localhost` by default already. [XR1-CODE]

## 6. Minimum regression contract

Serving the released VLABench dir through the released client on the pinned VLABench commit and reproducing the per-track table within noise is the only end-to-end check the public code supports; it does not test training.

## Sources

[XR1-CODE]; [XR1-CODE-XR1-README]; [XR1-CODE-EVAL-VLABENCH]; [XR1-HF-5B]; [XR1-HF-VLABENCH]; [XR1-HF-COLLECTION]; [VLAB-CODE].
