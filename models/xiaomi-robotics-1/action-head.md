---
id: world-model-kb.models.xiaomi-robotics-1.action-head
title: Xiaomi-Robotics-1 Flow-Matching Action Head
kind: model
status: maintained
last_updated: 2026-08-21
owners:
  - AIBuildAI world-model group
---

# Xiaomi-Robotics-1 Flow-Matching Action Head

## Retrieval metadata

**Relevant queries:** DiT action head, flow matching, velocity target, Beta(1.5, 1) timestep, 5 Euler steps, num_steps, frequency-domain loss, choice head, best-of-5, score head, asynchronous prefix, training_repeat, request seed.

**Knowledge provided:** the action head's objective terms and their weights, the sampler, the training-only auxiliary heads, the asynchronous-prefix mechanism, and the inference-time levers that exist without retraining.

**Related pages:** [Architecture](architecture.md) owns the DiT layout; [Action modeling](action-modeling.md) owns what the 60-D vector means; [Training](training.md) owns optimizer state; [diffusion and flow matching](../../foundations/learning-objectives/diffusion-and-flow-matching.md) owns the objective family.

## Identity and strict boundaries

The head denoises a `(K, 60)` normalized action chunk conditioned on the VLM KV cache and the projected state. It is a policy head, not a world model: it predicts no future observation and carries no value estimate. [XR1-TR, Sec. 3; XR1-CODE]

## Canonical mechanisms and invariants

### Flow matching

Training draws `u ~ Beta(1.5, 1)`, sets `t = (1 - u) * 0.999`, forms `x_t = (1 - t) * noise + t * action`, and regresses the velocity `action - noise` with an MSE over the active mask. The pinned trainer repeats each sample 4 times (`training_repeat`) with independent noise and timesteps. [XR1-TR, Sec. 3 (`L_Flow`); XR1-CODE, `XR1.py:forward`]

### Frequency-domain term

`loss_freq = | rfft(pred) - rfft(target) |` along the chunk axis, computed only for samples whose last chunk row is valid, excluding slots 17..19 (base velocity) by default, weighted by `freq_coefficient` (default 1.0). [XR1-CODE, `compute_flow_loss`]

### Choice and score heads (training only)

From the VLM hidden states at the `<a_i>` tokens the model regresses 5 candidate chunks; the per-sample loss is the L1 error of the best candidate, and a score head regresses each candidate's error (`loss_score`). Total loss: `0.5 * mse + freq_coefficient * freq + 0.5 * choice + 0.5 * score`. The report writes this as `L_Regression` with a best-of-K selection. These heads are not in the HF inference checkpoint. [XR1-TR, Sec. 3; XR1-CODE, `compute_choice_loss`]

### Weighting by prefix prediction

When an action prefix is present in training, the flow loss is weighted per element by the absolute error of a no-grad generation from the prefix (`weight` clamped to [0.5, 5] after mean-normalization over the mask), focusing learning on the continuation the model currently gets wrong. [XR1-CODE, `XR1.py:forward`]

### Asynchronous prefix

With probability 0.5 a prefix of 1..6 already-executed actions replaces the first rows of the noisy chunk (`prefix_length`); positions after the prefix receive a +10 position offset and prefix columns are randomly masked. This is the training side of the asynchronous-execution recipe inherited from Xiaomi-Robotics-0; the VLABench eval client never sends a prefix. [XR1-CODE; XR0-TR; XR1-CODE-EVAL-VLABENCH]

## Sampling contract

Inference: `x = randn_like(mask)`, 5 Euler steps with `dt = 1/num_steps`, `t = step/num_steps`, `x += v * dt`. The HF server seeds `torch.manual_seed(seed)` from the request (`request_seed=42` in the client) before drawing the noise and restores the RNG state afterward, so a given observation yields a deterministic chunk per seed. [XR1-HF-VLABENCH, `modeling_mibot.py:forward`]

## Optimization levers

| Lever | Surface | Expected signal | Risk | Validation |
|---|---|---|---|---|
| `num_steps` 3/5/10 | HF `forward` kwarg (server change) | Quality vs 70 ms latency | Released stats at 5 | Paired L2 |
| Seed ensembling | client: average or vote over k seeds | Lower action variance | k-fold serving cost | Paired L2 at k=1,3 |
| `freq_coefficient` | config | Smoother chunks | Over-smoothing fine grasps | `loss_mse` and SR |
| Drop the choice heads from the fine-tune loss | zero their coefficients | Memory/speed | Report attributes choice loss to candidate diversity | SR paired |
| `training_repeat` | constant in `XR1.py` | Per-step cost vs gradient variance | Unmeasured | s/step and loss curves |

Hypotheses; the report publishes no ablation table for these terms.

## Diagnostics and failure signatures

- `loss_freq` exactly 0 across a run: no sample reached the full chunk length (episodes shorter than K from the sampled frame), or the mask is empty.
- A chunk that drifts from the executed state within one replanning window: the per-step-delta convention was violated in the data path, not the head.

## Sources

[XR1-TR] Sec. 3; [XR1-CODE] `xr1/mibot/models/VLA/XR1.py`; [XR1-HF-VLABENCH] `modeling_mibot.py`; [XR0-TR]; [XR1-CODE-EVAL-VLABENCH].
