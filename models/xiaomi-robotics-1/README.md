---
id: world-model-kb.models.xiaomi-robotics-1
title: Xiaomi-Robotics-1 Agent Knowledge Entry
kind: model
status: maintained
last_updated: 2026-08-21
owners:
  - AIBuildAI world-model group
---

# Xiaomi-Robotics-1 Agent Knowledge Entry

## Retrieval metadata

**Relevant queries:** Xiaomi-Robotics-1, XR-1, 5B VLA, Qwen3-VL-4B policy, VLABench checkpoint, vlabench_choice, xr1 trainer, MiBoT, UMI pre-training, post-training a VLA on VLABench.

**Knowledge provided:** model identity boundaries, topic ownership, a document map, and the capability distinctions that matter when this model is the object of post-training.

**Related pages:** [`agent-index.yaml`](agent-index.yaml) provides machine-readable profiles; [`manifest.yaml`](manifest.yaml) provides identity and fixed revisions; [Xiaomi-Robotics-1 paper entry](../../papers/xiaomi-robotics-1/README.md) owns the report's claims; [VLABench paper entry](../../papers/vlabench/README.md) owns the benchmark; [ERVLA](../../papers/ervla/README.md) owns the chain-of-thought evidence the report cites. The Foundation pages for [policies and embodied systems](../../foundations/embodied-systems/robotics-and-embodied-ai.md) and [diffusion and flow matching](../../foundations/learning-objectives/diffusion-and-flow-matching.md) own the model-independent definitions. None of these resources defines AIBuildAI workflow orchestration.

## Retrieval integration

[`agent-index.yaml`](agent-index.yaml) groups related queries with knowledge, strategies, and evidence. Source tokens resolve through [`sources.yaml`](sources.yaml) (code, checkpoints, issues) and the paper entry's registry (the technical report, [XR1-TR]). Executed-state claims are recorded in [`reproduction.md`](reproduction.md); topic pages contain stable model knowledge.

## Identity constraints

| Object | Correct scope | Never infer |
|---|---|---|
| `XiaomiRobotics/Xiaomi-Robotics-1-5B` | Post-trained base checkpoint, xr1 trainer format (`model_states.pt`, 10.2 GB), the only artifact carrying the training-only choice heads | That it has HF-format inference weights or benchmark scores of its own |
| `XiaomiRobotics/Xiaomi-Robotics-1-VLABench` | HF-format VLABench fine-tune; robot type `vlabench_choice`, chunk 10, raw state, per-step deltas; 59.1 SR avg over 5 tracks | That the xr1 trainer loads it directly (it lacks the choice heads) or that it scores RoboCasa |
| `XiaomiRobotics/Xiaomi-Robotics-1-RoboCasa` / `-RoboCasa365` | Separate fine-tunes with their own action configs (`robocasa_mg`, 16-step 12-D chunks, 4-frame history) | Any VLABench behaviour |
| VLM component (Qwen3-VL-4B-Instruct) | Autoregressive vision-language backbone; text generation is not used at inference in the released serving path | That the served model emits chain-of-thought text |
| DiT action head | 36-layer flow-matching head reading the VLM KV cache; 5 Euler steps | A world model, future-frame predictor, or safety layer |
| 2B and 10B variants | Report-only scaling points | Released weights |
| `xr1/` trainer | Lightning + DeepSpeed ZeRO-2 post-training for the bimanual real-robot JSON schema | That its `JsonDataset` matches the VLABench checkpoint's conventions |

[XR1-TR, Table 1, Sec. 5; XR1-HF-5B; XR1-HF-VLABENCH; XR1-CODE]

## Model graph

```text
Qwen3-VL-4B-Instruct initialization
  -> UMI pre-training (>100K h, auto-labelled scene-transition captions, flow + choice + 0.1 NTP)
  -> cross-embodiment post-training (~10K h; embodiment + instruction alignment)
  -> XiaomiRobotics/Xiaomi-Robotics-1-5B (model_states.pt)
       -> benchmark fine-tunes (HF format, inference heads only)
            -> -RoboCasa (robocasa_mg)
            -> -RoboCasa365
            -> -VLABench (vlabench_choice)  <- aibuildai campaign warm start
```

The VLM consumes three images, the instruction, a state token, and (in training) the `<a_i>` action tokens; the DiT consumes a sink token, the projected state, and the noisy action chunk while attending into every VLM layer's KV cache. [XR1-TR, Sec. 3; XR1-CODE]

## Retrieval profile catalog

| Query family | Profile ID | Knowledge scope |
|---|---|---|
| Identity, format, revision, license | `model_identity` | Checkpoint and code identity |
| MoT, DiT, slots, prompt, processor | `architecture_and_interfaces` | Computation and interface facts |
| VLM, CoT, instruction grounding | `vlm_knowledge` | Language-side mechanisms and evidence |
| Flow matching, steps, choice heads, async | `action_head_knowledge` | Action-head mechanisms |
| Per-step deltas, client, replanning | `action_and_policy_knowledge` | Closed-loop semantics |
| Mixtures, batch, lr, saves | `data_and_training_knowledge` | Learning state and variables |
| xr1, deploy, eval code | `implementation_knowledge` | Fixed-revision code locations |
| Serving, VRAM, wall clock | `runtime_knowledge` | Runtime references |
| SR/PS/IS, leaderboards | `evaluation_knowledge` | Protocol-bound results |
| Track-level interventions | `optimization_and_open_questions` | Design references and gaps |

## Canonical ownership map

### Model semantics

- [Architecture and computation](architecture.md)
- [Modality and I/O contracts](modalities-and-io.md)
- [VLM backbone](vlm-backbone.md)
- [Action head](action-head.md)
- [Action modeling](action-modeling.md)
- [Policy and closed-loop interface](policy.md)

### Learning and evaluation

- [Data system](data.md)
- [Training](training.md)
- [Post-training and benchmark fine-tunes](post-training.md)
- [Evaluation protocols](evaluation.md)
- [Limitations and risk boundaries](limitations.md)

### Execution and optimization

- [Codebase map](codebase.md)
- [Inference guide](inference.md)
- [Execution-state ledger](reproduction.md)
- [Optimization playbook](optimization-playbook.md)
- [Research queue](research-queue.md)

## Evidence interpretation boundaries

- A result is interpretable when checkpoint revision, robot type, action conventions, VLABench commit, track file, episode count, and client settings (chunk, replan, image size, CoT flag, seed) are known.
- The report's 59.1 is a 5-track success-rate macro average over 50 episodes per task; the Awesome-WAM leaderboard's VLABench statistic is a Track 1-4 progress-score average (69.2 for the same checkpoint). They are different numbers for the same run.
- The released processor stats, not the paper, define the served action space; the paper does not disclose the VLABench fine-tune's steps, batch, or learning rate.
- Training-only components (choice heads, CoT next-token loss) leave no trace in the HF inference checkpoint; their contribution is not measurable from the served model.
- No local inference or training run is registered in this entry; every number here is source-reported until [`reproduction.md`](reproduction.md) says otherwise.
