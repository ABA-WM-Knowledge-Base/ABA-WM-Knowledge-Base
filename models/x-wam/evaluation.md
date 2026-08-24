---
id: world-model-kb.models.x-wam.evaluation
title: X-WAM Evaluation Evidence
kind: model
status: maintained
last_updated: 2026-08-24
owners:
  - AIBuildAI world-model group
---

# X-WAM Evaluation Evidence

## Retrieval metadata

**Relevant queries:** X-WAM result, RoboCasa success, RoboTwin success, RGB-D quality, point cloud, PSNR, SSIM, LPIPS, AbsRel, delta1, Chamfer Distance, latency, ablation, baseline, or evaluation protocol.

**Knowledge provided:** reported results bound to their checkpoint and protocol, metric semantics, ablation scope, and comparability conditions for optimization experiments.

**Related pages:** The [X-WAM Paper](../../papers/x-wam/paper.md) owns full reported tables; [Original RoboCasa](../../benchmarks/robocasa/README.md) owns benchmark identity; [reproduction](reproduction.md) owns locally observed execution. [Evaluation methodology](../../foundations/data-and-evaluation/evaluation-methodology.md) owns model-independent comparison principles.

## Checkpoint-bound policy results

The paper reports an average success rate of **79.2%** on its 24-task RoboCasa evaluation for X-WAM and **89.8% / 90.7%** on RoboTwin under clean/randomized conditions. These values belong to the paper's benchmark-specific SFT states, action adapters, task suites, camera setup, controller, rollout procedure, and inference settings. They do not describe the cross-embodiment pretrained checkpoint, the Wan base, Cosmos3-Nano, or RoboCasa365. [XWAM-PAPER-V2, pp.8-10]

The X-WAM repository pins Original RoboCasa at commit `756598a5be52e052339bb2d957426e39015c2afb`, matching the benchmark's v0.2 code identity. Its RoboCasa evaluation covers the original 24 manipulation tasks used by the benchmark's atomic-policy experiment rather than the full set of 100 task definitions or a RoboCasa365 suite. [XWAM-CODE-72CF; RC24-CODE-V02]

For a comparable rerun, retain at minimum: X-WAM state and config revision, Wan revision, simulator and robosuite commits, task list, scene/layout/style selection, object-instance policy, camera names and resolution, state/action normalization, controller, action-chunk execution rule, random seeds, trials per task, timeout, success detector, and aggregation formula. The published average alone cannot reconstruct these fields.

## World-prediction fidelity

The paper's X-WAM row reports:

| Output family | Metric | Reported value | Direction |
|---|---|---:|---|
| RGB | PSNR | 23.46 | higher |
| RGB | SSIM | 0.8942 | higher |
| RGB | LPIPS | 0.0513 | lower |
| depth | AbsRel | 0.0349 | lower |
| depth | delta1 | 0.9738 | higher |
| lifted 3D | Chamfer Distance | 0.0049 | lower |

[XWAM-PAPER-V2, Table 3]

These metrics diagnose different error surfaces. PSNR favors per-pixel similarity; SSIM measures local structural similarity; LPIPS uses learned perceptual features; AbsRel is scale-sensitive relative depth error; delta1 counts depth ratios within a threshold; Chamfer Distance depends on depth, intrinsics, extrinsics, pose alignment, point sampling, units, and aggregation. None alone establishes controllability or closed-loop success. A new result should preserve the exact evaluation set, horizon, crop/resize path, depth representation and scale, camera calibration, and metric implementation.

## Architecture ablation evidence

The paper reports an ablation regime without the large cross-embodiment pretraining used by the final checkpoint. Under that narrower regime, depth integration and noise/sampling variants produce:

| Variant | Success (%) | Reported latency |
|---|---:|---:|
| no depth branch | 63.0 | 1,033 ms |
| sequence-concatenated depth | 68.7 | 1,888 ms |
| channel-concatenated depth | 64.2 | 1,266 ms |
| unilateral interleaved depth | 67.8 | 1,033 ms |
| synchronous training and inference | 66.4 | 4,665 ms |
| decoupled training, synchronous inference | 66.3 | 4,665 ms |
| decoupled training, asynchronous inference | 67.2 | 1,033 ms |
| ANS training, asynchronous inference | 67.8 | 1,033 ms |

[XWAM-PAPER-V2, Table 4]

The two groups share a table but test different factors. The depth comparison changes architecture/capacity and may change compute. The scheduling comparison changes the training noise distribution and/or inference state machine. These 63.0–68.7 values must not be compared directly with the final 79.2% result as if only one switch differed; the final model also changes pretraining and potentially other training conditions.

The unilateral depth branch matching the no-depth policy latency is consistent with disabling that branch during policy inference. It supports a training-time auxiliary-representation hypothesis, not direct evidence that the policy reads generated geometry online. A causal study needs matched parameter capacity or freezing controls and a direct measurement of shared-gradient effects.

## Baseline comparison contract

Before comparing X-WAM with another policy or world-action model, align:

- training demonstrations and pretraining exposure;
- observation views, image history, proprioception, and language;
- action representation, horizon, control frequency, and replanning interval;
- simulator revision, task selection, scene randomization, and trial count;
- inference compute, model calls, latency, and any generated-media decoding;
- success detector and aggregation, including whether failures or resets are filtered.

If alignment is impossible, report a structured non-equivalence instead of a single ranking. A model trained on more demonstrations, longer history, privileged depth, or different task instances answers a different question.

## Optimization evaluation bundle

An X-WAM optimization should pair the primary closed-loop task metric with mechanism diagnostics and regressions. Recommended diagnostic groups are action error by horizon, gripper/rotation/translation error, RGB/depth/point-cloud fidelity, action-decision latency, full-generation latency, memory, collision/saturation/timeout rates, and per-task/per-layout slices. Report paired seeds and uncertainty; preserve failed episodes rather than retaining only successful rollouts.

The baseline row must be rerun under the same implementation and protocol when practical. If only the paper number is available, label it as reported by the authors in the experiment artifact and avoid treating a cross-hardware or cross-code delta as causal.

## Current KB evidence state

All numeric values on this page are transcribed from the fixed paper revision or pinned public metadata. No checkpoint was downloaded, no metric implementation was executed, and no policy or world-generation result was reproduced locally during this KB update. The exact state and acceptance gates are canonical in [Reproduction](reproduction.md).

## Sources

Evaluation facts use `XWAM-PAPER-V2`, `XWAM-CODE-72CF`, and `RC24-CODE-V02`.
