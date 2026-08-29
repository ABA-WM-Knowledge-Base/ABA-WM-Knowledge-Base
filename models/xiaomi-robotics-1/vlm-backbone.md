---
id: world-model-kb.models.xiaomi-robotics-1.vlm-backbone
title: Xiaomi-Robotics-1 Vision-Language Backbone and Chain-of-Thought
kind: model
status: maintained
last_updated: 2026-08-21
owners:
  - AIBuildAI world-model group
---

# Xiaomi-Robotics-1 Vision-Language Backbone and Chain-of-Thought

## Retrieval metadata

**Relevant queries:** Qwen3-VL-4B-Instruct, VLM backbone, vision tower, deepstack, next-token loss, lambda 0.1, chain-of-thought, CoT, reasoning dropout, /cot, /no_cot, instruction grounding, language track, semantic instruction.

**Knowledge provided:** what the backbone contributes, which of its parts train, how language supervision enters pre-training and the VLABench fine-tune, and why chain-of-thought is a training-time-only mechanism in the released system.

**Related pages:** [Architecture](architecture.md) owns the MoT coupling; [Training](training.md) owns objectives and weights; [ERVLA](../../papers/ervla/paper.md) owns the chain-of-thought evidence the report adopts; [Evaluation](evaluation.md) owns the instruction-track numbers.

## Identity and capability boundary

The backbone is `Qwen/Qwen3-VL-4B-Instruct` (36 layers, hidden 2560, interleaved mRoPE with sections [24, 20, 20], deepstack visual features injected at layers 8/16/24). The trainer instantiates it from the config and loads the weights from the checkpoint; the server loads the full `MiBoTForActionGeneration` with the VLM inside. [XR1-HF-VLABENCH, `config.json`; XR1-CODE, `XR1.py`]

What the backbone does at serving: encode the three views and the instruction, emit a per-layer KV cache for the DiT. What it does not do at serving: generate text. `skip_logits` semantics in the trainer and the absence of any `generate` call in `modeling_mibot.py` mean the `/cot` prompt variant produces no reasoning string; it is a prompt-conditioning difference only. [XR1-HF-VLABENCH, `modeling_mibot.py:forward`]

## Canonical mechanisms and invariants

### Language supervision in pre-training

The report co-trains the VLM with a next-token-prediction loss (`L_NTP`, weight 0.1) on vision-language data alongside the flow and regression losses, and auto-labels the UMI corpus with scene-transition captions written by Qwen3.5-27B ("caption the state transitions of both the grippers and the interacting objects in the scene within each segment"). Pre-training thus teaches the model to act toward a described target state; post-training shifts the text to imperative instructions (instruction alignment). [XR1-TR, Sec. 3-4]

### Chain-of-thought on VLABench

For the VLABench fine-tune the report states: "We leverage chain-of-thought (CoT) labeling as in ERVLA and train our model with a 50% probability on the next-token-prediction loss of CoT alongside the action loss." The released checkpoint is evaluated with the empty `<cot></cot>` assistant turn (`--no-cot`). This is ERVLA's reasoning-dropout pattern: learn from reasoning text during training, act without it at inference. The CoT annotations are not released by either party. [XR1-TR, Sec. 5.3; ERV-PAPER; XR1-CODE-EVAL-VLABENCH]

The public `xr1` trainer does not implement that loss: `XR1.forward` pops `labels` and calls the VLM with `skip_logits=True`. A CoT next-token term must be added to train this way; the aibuildai deploy adds it as a subclass (`xr1_cot`) without editing the released module. [XR1-CODE, `XR1.py:forward`]

### Frozen and trainable scope

Input embeddings are frozen; the vision tower trains with gradient checkpointing; language-model MLPs are wrapped in activation checkpointing when `ffn_gradient_checkpointing` is on. The `lm_head` is tied to the embeddings and therefore effectively frozen too. [XR1-CODE, `XR1.py:_build_model`]

## Deployment contracts

| Surface | Text output | Used by |
|---|---|---|
| HF server | none | benchmark evaluation |
| xr1 runtime server | none | real-robot runtime |
| Trainer with `xr1_cot` | next-token loss over the `<cot>` span only | aibuildai VLABench fine-tunes |

## Optimization levers

| Lever | Surface | Expected signal | Risk | Validation |
|---|---|---|---|---|
| CoT mixing probability (`cot_prob`) | data path | Instruction/commonsense SR (ERVLA: +4.0 to +7.4 from grounded CoT on VLABench/LIBERO-Plus in their setting) | Noisy self-generated labels; ERVLA shows abstract "goal/planning" fields alone can hurt | cot_prob 0 vs 0.5 paired L2, per track |
| CoT content (grounded motion/point trajectory vs semantic) | label generator prompt | ERVLA Table 1: movement +4.1, point trajectory +4.8, bounding box -3.2 relative | Prompt drift across episodes | Ablate content fields with fixed seeds |
| CoT loss weight (`cot_coefficient`) | `xr1_cot` | Trade-off with action loss | Over-weighting degrades action MSE | Monitor `loss_mse` and `loss_cot` jointly |
| Freeze the language model, train DiT + projectors | `requires_grad_` | Faster, memory-light; language tracks may not move | Instruction grounding lives in the VLM | Track-3/4 SR vs full |

Levers are hypotheses on this model; ERVLA's numbers come from a different base and training set.

## Diagnostics and failure signatures

- Instruction-track failures with correct grasps point at grounding, not control: inspect Track 4 episodes for target-object confusion (IS low) before touching the action head.
- A `/cot` prompt at serving time changes nothing except the suffix token; do not read a difference between `--cot` and `--no-cot` runs as "reasoning at inference".

## Sources

[XR1-TR] Sec. 3-5; [XR1-CODE] `xr1/mibot/models/VLA/XR1.py`, `xr1/mibot/models/VLM/qwen3vl.py`; [XR1-HF-VLABENCH] `modeling_mibot.py`, `config.json`; [ERV-PAPER] Table 1 and the reasoning-dropout section; [QWEN3VL-HF-4B].
