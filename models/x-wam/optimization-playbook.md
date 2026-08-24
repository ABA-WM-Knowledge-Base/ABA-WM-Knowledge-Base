---
id: world-model-kb.models.x-wam.optimization-playbook
title: X-WAM Optimization Reference
kind: model
status: maintained
last_updated: 2026-08-24
owners:
  - AIBuildAI world-model group
---

# X-WAM Optimization Reference

## Retrieval metadata

**Relevant queries:** improve X-WAM, optimization lever, depth branch, ANS, action horizon, history, data mixture, loss weight, normalization, view robustness, latency, ablation, controlled experiment, or failure diagnosis.

**Knowledge provided:** mechanism-linked intervention cards with controllable surfaces, expected signals, attribution controls, regression measures, and falsification conditions for X-WAM-specific optimization.

**Related pages:** [Architecture](architecture.md), [data and training](data-and-training.md), and [inference](inference.md) own the mechanisms; [evaluation](evaluation.md) owns baselines; [RoboCasa optimization reference](../../benchmarks/robocasa/optimization-reference.md) owns benchmark-side slices. [Research queue](research-queue.md) records unresolved decision-changing questions.

## Diagnostic decomposition

X-WAM policy performance can change through at least five surfaces:

```text
data and supervision
  -> learned representation and joint dynamics
  -> denoising/inference schedule
  -> normalization and embodiment adapter
  -> controller and benchmark protocol
```

A model change is interpretable only after deterministic interface fixtures rule out camera permutation, state/action convention, normalization, gripper sign, and chunk-execution drift. Visual fidelity, action error, and closed-loop success should be measured together when the intervention claims cross-modal benefit.

## Geometry branch intervention card

**Mechanism.** Ten copied late Transformer blocks predict depth while reading main-branch key/value states; policy inference disables this branch. Depth loss can still update shared early blocks during training. [XWAM-CODE-72CF; XWAM-PAPER-V2, pp.4-6]

**Controllable surfaces.** Number and placement of copied blocks; branch capacity; depth loss weight; source-specific depth masks; freezing shared blocks; detaching main features before the depth branch; supervised-depth versus pseudo-depth sampling.

**Discriminating comparison.** Match initialization, data exposure, total optimizer updates, and main-branch capacity. Compare no depth, auxiliary depth with shared gradients, auxiliary depth with shared features detached/frozen, and a parameter-count control without depth supervision.

**Primary evidence.** RoboCasa task success, action error by horizon, AbsRel/delta1, point-cloud Chamfer Distance, shared-feature probes, gradient cosine or update norm by block, training/inference memory and latency.

**Falsification.** If gains remain under a capacity-only control or disappear when shared gradients are preserved but depth targets are shuffled, geometry supervision is not the supported cause. If better depth does not improve action or task slices involving occlusion/contact, avoid claiming policy benefit from geometry.

## Noise-distribution and asynchronous sampling card

**Mechanism.** ANS trains a coupled joint distribution with `t_video >= t_action` and clean-action mass, then inference stops action/state earlier than video. [XWAM-PAPER-V2, pp.5-6 and Table 4]

**Controllable surfaces.** Coupling rule, action/video timestep marginals, `clean_action_ratio`, action and video denoising steps, scheduler type, and whether clean decoded actions condition later video calls.

**Discriminating comparison.** Hold weights, model-call budget, seeds, CFG semantics, and evaluation set fixed when testing inference steps. Hold examples, optimizer updates, and sampled marginal histograms fixed when testing coupling. Compare synchronous, independent-decoupled, and coupled ANS rather than using a single binary label.

**Primary evidence.** closed-loop success, action error versus denoising step, video metrics, conditional consistency between predicted action and future media, action-decision latency, full-generation latency, and failure rate.

**Falsification.** If an apparent gain vanishes after matching action model calls or marginal timestep exposure, it is a compute/distribution effect rather than coupling evidence. If video continuation is unchanged by replacing clean actions, the claimed action-conditioned future may not be causally sensitive.

## Temporal context and action-chunk card

**Mechanism.** The release conditions on one frame/state and predicts 32 actions spanning eight future visual intervals. Closed-loop clients choose how much of that chunk to execute before replanning.

**Controllable surfaces.** Observation history length, frame spacing, action horizon, action frequency, actions executed per inference, and temporal positional encoding. Architecture changes are required if tensor lengths exceed checkpoint-compatible shapes.

**Discriminating comparison.** Evaluate paired deterministic scenarios with identical weights for execute-1, execute-4, execute-8, and full-chunk policies; separately train matched models when changing learned history or horizon. Record observation age and compute budget.

**Primary evidence.** success, drift, recovery, action smoothness, collision/saturation, P50/P95 action latency, calls per episode, and per-horizon action error.

**Falsification.** If shorter replanning improves success only by increasing model calls beyond the comparison budget, it is a systems trade-off, not a better world model. If added visual history helps only static tasks, the proposed partial-observability mechanism is unsupported.

## Data-mixture and depth-provenance card

**Mechanism.** Pretraining combines real and simulated embodiments plus rendered, sensor, or pseudo-depth targets. Source exposure can improve transfer or create schema/domain interference.

**Controllable surfaces.** Source sampling weights, task balance, real/sim ratio, depth provenance, language quality, failure retention, action-validity masks, and target-domain replay.

**Discriminating comparison.** Keep total episodes/frames, optimizer updates, temporal sampling, and evaluation constant. Use source-level exposure logs and an episode-family split that prevents near-duplicate leakage. Compare target-only, target plus one mechanistically relevant source, and target plus balanced replay.

**Primary evidence.** learning-curve area, target per-task success, unseen layout/style/object slices, source-domain regressions, action/state normalization coverage, and depth metrics stratified by provenance.

**Falsification.** A gain that disappears under equal exposure or is localized to duplicated scenarios does not support cross-embodiment transfer. Aggregate improvement with severe source-specific regression should be reported as a trade-off, not universal scaling benefit.

## Action/state objective card

**Mechanism.** Unit-weight flow losses jointly supervise video, action, state, and depth; an FFT-based action-frequency loss exists with default zero weight.

**Controllable surfaces.** modality loss weights, horizon weighting, translation/rotation/gripper decomposition, frequency loss, action masks, quantile bounds, and state auxiliary loss.

**Discriminating comparison.** Normalize loss magnitudes and report per-parameter gradient norms before interpreting scalar weights. Change one weighting family around a rerun baseline, preserving data order and scheduler. Include a version that matches effective gradient contribution rather than raw coefficient.

**Primary evidence.** component-wise action error, spectral jerk, gripper event timing, predicted-state consistency, closed-loop success, RGB-D regressions, and gradient conflict diagnostics.

**Falsification.** Lower offline MSE without closed-loop or gripper-event gain does not support policy improvement. A frequency penalty that smooths actions while missing required fast contact transitions is a failure despite lower jerk.

## Multi-view robustness card

**Mechanism.** Learned view embeddings identify three token streams; the loader has optional view shuffling, while released configs preserve fixed ordering.

**Controllable surfaces.** view dropout, calibrated permutation augmentation, embedding regularization, cross-view consistency loss, camera-role tokens, and static/dynamic camera type encoding.

**Discriminating comparison.** Retain a calibrated fixed-order baseline and test single-view occlusion, one-camera removal, permitted camera perturbation, and deliberately permuted inputs. Any permutation augmentation must permute pixels, calibration, and role metadata together.

**Primary evidence.** success and action error by missing/shifted camera, cross-view RGB-D consistency, clean-condition regression, and attention/use diagnostics.

**Falsification.** Robustness obtained by ignoring wrist views should appear as no degradation when those views are corrupted and should not be described as better fusion. Gains under invalid calibration permutations do not establish real camera robustness.

## Inference-efficiency card

**Mechanism.** Policy mode skips depth and video decode and stops after action denoising; CFG and compilation alter model-call cost.

**Controllable surfaces.** action steps, CFG path, compilation, precision, attention kernel, caching, parallelism, and action-only parameter extraction where state compatibility permits.

**Discriminating comparison.** Use the same checkpoint and fixtures, warm-up convention, batch, views, resolution, hardware, and quality protocol. Report model calls and output equality/tolerance alongside latency and memory.

**Primary evidence.** task success, action deviation from reference, action-decision latency, throughput, peak allocated/reserved/device memory, load time, and failure rate.

**Falsification.** A faster path that silently changes preprocessing, scheduler semantics, or checkpoint coverage is not an inference optimization. Policy latency cannot be generalized to full RGB-D mode.

## Result record

Every optimization result is most reusable when it binds the baseline and intervention to immutable code/checkpoint/data revisions; records the single declared variable and any unavoidable differences; retains resolved configuration, exposure, seeds, raw outputs and rollouts; reports mechanism diagnostics, primary metrics, regressions, resource cost and uncertainty; and states the observation that would contradict the proposed explanation. These fields improve attribution without assigning AIBuildAI task order or repository decisions.

## Sources

Optimization mechanisms use `XWAM-PAPER-V2`, `XWAM-CODE-72CF`, `XWAM-HF-CHECKPOINTS`, `XWAM-HF-ROBOCASA`, and `XWAM-HF-ROBOTWIN`.
