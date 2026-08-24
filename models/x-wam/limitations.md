---
id: world-model-kb.models.x-wam.limitations
title: X-WAM Limitations and Evidence Boundaries
kind: model
status: maintained
last_updated: 2026-08-24
owners:
  - AIBuildAI world-model group
---

# X-WAM Limitations and Evidence Boundaries

## Retrieval metadata

**Relevant queries:** X-WAM limitation, failure mode, reproducibility gap, fixed horizon, pseudo-depth, 3D claim, latency, checkpoint size, paper config mismatch, RoboCasa365, baseline comparability, or deployment risk.

**Knowledge provided:** model, artifact, interface, evaluation, and release boundaries that constrain what can be inferred from X-WAM evidence and which diagnostics can distinguish competing causes.

**Related pages:** [Architecture](architecture.md) and [modalities and I/O](modalities-and-io.md) define the released system; [evaluation](evaluation.md) binds reported results; [reproduction](reproduction.md) prevents documented capability from being mistaken for an observed run. [Original RoboCasa scope](../../benchmarks/robocasa/scope-and-versions.md) owns the v0.2 versus RoboCasa365 boundary.

## Model and horizon boundaries

X-WAM predicts a fixed eight-frame visual/state future and a fixed 32-action chunk from one current frame per view and one state. It is not a persistent simulator with an indefinitely maintained latent world. Long-horizon use requires repeated closed-loop calls, so prediction error, action age, scene changes, and occlusion can accumulate outside the training horizon. [XWAM-PAPER-V2, pp.4-6]

The unified sequence uses bidirectional attention over the noisy future tokens. It is a conditional denoising model, not a causal autoregressive dynamics engine. Intermediate denoising states should not be interpreted as physically valid time steps. Generated RGB-D consistency and action competence are learned correlations unless interventions establish causal sensitivity.

Only three configured views and a fixed state/action schema are represented in the release. New camera counts, view roles, calibration, embodiment kinematics, controller types, control frequencies, or action conventions require explicit adapter validation and usually adaptation data. Shape-compatible tensors are not semantic compatibility.

## Geometry boundary

Depth is encoded as inverse-depth-like three-channel imagery through the same VAE and decoded by a copied late branch. Some pretraining sources require pseudo-depth. This design can improve geometric prediction, but it does not create a native persistent 3D scene representation, explicit object permanence, contact graph, or collision model. Point clouds are reconstructed after prediction using depth and camera pose. [XWAM-PAPER-V2, pp.5-7]

Metric 3D quality depends on intrinsics, static-camera extrinsics, end-effector pose prediction, hand-eye calibration, depth scaling, and coordinate alignment. A low Chamfer Distance can degrade through any of these interfaces even if the neural depth tensor improves. Conversely, a policy gain from depth-supervised training does not prove online use of predicted depth because the public policy path disables the depth branch.

## Artifact and resource boundary

Each X-WAM state file is approximately 38.89 GB and still requires the separate Wan2.2 base, VAE, and text components. The release does not provide a compact policy-only state, a quantified minimum-VRAM table, or a guarantee that a single consumer GPU can load the assembled system. [XWAM-HF-CHECKPOINTS; XWAM-WAN22-HF]

The public state files use a DeepSpeed-style path and inherit configuration dependencies. Checkpoint download success does not imply successful reconstruction of optimizer-free inference state. Missing/unexpected keys, configuration precedence, distributed assumptions, attention kernels, precision, and host-memory spikes can all prevent execution.

## Training-data boundary

Pretraining combines simulator and real-robot sources with different cameras, state schemas, action semantics, task distributions, depth provenance, and licenses. Reported episode counts and hours do not reveal the complete sampling weights, deduplication, language-generation process, failure retention, or source-specific quality filters. Domain gains may therefore reflect exposure, scale, or source correlation rather than a unique architecture mechanism. [XWAM-PAPER-V2, pp.6-7 and 16]

The public X-WAM RoboCasa SFT snapshot has 1,235 episodes and is not identical to the Original RoboCasa paper's human or MimicGen releases. Results tied to X-WAM's derived dataset do not automatically transfer to a different RoboCasa dataset, RoboCasa365, or a teammate's custom split. [XWAM-HF-ROBOCASA; RC24-PAPER-V1]

## Source and configuration conflicts

Several paper values differ from the pinned release:

- pretraining batch per GPU is 8 in the paper and 4 in the public config;
- benchmark SFT learning rate is `3e-5` in the paper and `1e-5` in public configs;
- the paper states 20,000 SFT steps for both benchmarks, while the RoboTwin config states 40,000;
- the paper reports CFG scale 1, while code defaults to 0; code semantics indicate intended conditional-output equivalence but different compute paths.

[XWAM-PAPER-V2, pp.16-18; XWAM-HF-CHECKPOINTS; XWAM-CODE-72CF]

These discrepancies do not by themselves invalidate the checkpoint, but they prevent an unqualified claim of exact paper-training reproduction. An experiment should state whether it reproduces the paper description, the released checkpoint behavior, or a deliberately modified configuration.

## Evaluation boundary

The reported 79.2% RoboCasa value is tied to the X-WAM paper's 24-task Original RoboCasa protocol. The repository pins Original RoboCasa v0.2, not RoboCasa365. The score is not evidence for all 100 Original RoboCasa task definitions, unseen layouts/styles beyond the selected protocol, real kitchens, or a newer benchmark generation. [XWAM-PAPER-V2; XWAM-CODE-72CF; RC24-RELEASE-V02]

The depth/ANS ablations omit large-scale pretraining and therefore do not isolate the same factor around the final checkpoint. Reported latency depends on hardware, batch, views, resolution, precision, scheduler steps, CFG path, and whether video/depth decode occurs. It is not a portable runtime guarantee.

Perceptual and geometric metrics do not replace closed-loop success, and success does not diagnose physical correctness. Benchmark aggregation can hide task-, scene-, object-, and failure-mode differences. Comparing another model requires matching data exposure and interface budget or explicitly preserving the mismatch.

## Deployment and control boundary

The public stack provides research evaluation clients, not a safety-certified control system. Broker failures, stale observations, action chunking, gripper sign, rotation conversion, controller saturation, collision, timeout, and emergency stop are external control concerns. Generated action ranges and visually plausible futures do not establish safe execution.

The model predicts relative pose actions under benchmark adapters; it does not expose calibrated uncertainty or a verified out-of-distribution detector. Ensemble variance, denoising variance, or reconstruction error may be studied as diagnostics, but none should be labeled safety confidence without calibration against failures.

## Diagnostic implications

When performance changes, separate at least five causes: model representation, training distribution, preprocessing/normalization, inference schedule, and environment/controller semantics. Geometry interventions need capacity and shared-gradient controls. Data interventions need exposure accounting. Runtime interventions need equal model-call and latency reporting. Interface failures should be tested on deterministic fixtures before any weight change.

## Sources

Limitations use `XWAM-PAPER-V2`, `XWAM-CODE-72CF`, `XWAM-HF-CHECKPOINTS`, `XWAM-HF-ROBOCASA`, `XWAM-WAN22-HF`, `RC24-PAPER-V1`, and `RC24-RELEASE-V02`.
