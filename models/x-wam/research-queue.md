---
id: world-model-kb.models.x-wam.research-queue
title: X-WAM Open Research Registry
kind: record
status: maintained
last_updated: 2026-08-24
owners:
  - AIBuildAI world-model group
---

# X-WAM Open Research Registry

## Retrieval metadata

**Relevant queries:** X-WAM unknown, unresolved question, checkpoint provenance, depth policy benefit, ANS causality, action-conditioned video, RoboCasa transfer, data mixture, resource requirement, or model-improvement hypothesis.

**Knowledge provided:** stable decision-changing questions with current knowledge, missing evidence, minimal discriminating measurements, and closure conditions. This registry does not schedule or prioritize AIBuildAI work.

**Related pages:** [Reproduction](reproduction.md) owns execution state; [optimization reference](optimization-playbook.md) owns reusable intervention designs; [limitations](limitations.md) owns established boundaries. Cross-model unknowns remain in [World Model open problems](../../foundations/research-frontiers/open-problems.md).

## Registry semantics

Each item is retained only when its answer could change a model, data, inference, evaluation, or integration decision. `Known` fields are source-backed; `Unknown` fields are not filled by assumption. A closure condition identifies the evidence that can convert the question into stable canonical knowledge. Item order carries no execution priority.

### RQ-XWAM-ARTIFACT-001 — Which recipe produced each public state?

- **Decision affected:** whether a continuation run should follow paper values or the serialized released configuration.
- **Known:** paper and release agree on RoboCasa 20K steps but disagree on SFT learning rate, RoboTwin steps, and pretraining per-GPU batch. [XWAM-PAPER-V2, pp.16-18; XWAM-HF-CHECKPOINTS]
- **Unknown:** exact launch overrides, distributed world size, gradient accumulation, scheduler state, and provenance mapping for each uploaded state.
- **Discriminating evidence:** author-issued run manifests or checkpoint metadata that binds commit, resolved config, topology, data revisions, and optimizer/scheduler state to each file.
- **Closure condition:** each public state has one internally consistent effective recipe; until then, paper-recipe and released-checkpoint reproductions remain separate identities.

### RQ-XWAM-RUNTIME-001 — What is the mode-specific resource envelope?

- **Decision affected:** feasible hardware, parallelism, and whether a compact policy path is necessary.
- **Known:** each X-WAM state is approximately 38.89 GB and requires separate Wan assets; policy mode omits depth/video decode. [XWAM-HF-CHECKPOINTS; XWAM-CODE-72CF]
- **Unknown:** peak host RAM, GPU allocated/reserved/device memory, load time, warm action latency, and full RGB-D latency across supported precision/topology choices.
- **Discriminating evidence:** fixed-fixture load, action-only, RGB-without-depth, and full RGB-D measurements on named hardware with identical checkpoint/config and a complete memory trace.
- **Closure condition:** a mode-indexed capacity table reports successful output, numerical settings, model calls, latency, and all memory measures; one mode is not generalized to another.

### RQ-XWAM-DEPTH-001 — Why does depth supervision improve policy success?

- **Decision affected:** whether to retain, expand, freeze, or remove the copied depth branch during adaptation.
- **Known:** the paper's no-depth versus unilateral-depth ablation changes success from 63.0 to 67.8 in a no-large-pretraining regime, while released policy inference disables the depth branch. [XWAM-PAPER-V2, Table 4; XWAM-CODE-72CF]
- **Unknown:** contribution of extra capacity, shared depth gradients, representation geometry, source/data differences, and initialization.
- **Discriminating evidence:** matched no-depth, capacity-only, shared-gradient, detached-gradient, and shuffled-depth controls with block-wise update diagnostics and geometry/action/task metrics.
- **Closure condition:** one mechanism predicts both representation changes and task-slice gains under capacity- and compute-matched controls.

### RQ-XWAM-ANS-001 — Which part of ANS causes the reported gain?

- **Decision affected:** joint timestep distribution and inference scheduler design.
- **Known:** coupled ANS plus asynchronous inference reports 67.8 versus 67.2 for decoupled training plus asynchronous inference in the paper ablation; synchronous inference is substantially slower in that table. [XWAM-PAPER-V2, Table 4]
- **Unknown:** separate effects of timestep marginal changes, coupling, clean-action mass, model-call budget, and action-conditioned continuation.
- **Discriminating evidence:** factorial comparisons that match timestep marginals and model calls while varying coupling and `clean_action_ratio`; measure action/video conditional consistency and closed-loop success.
- **Closure condition:** a repeatable effect remains after exposure and compute controls and is localized to a defined distributional change.

### RQ-XWAM-CAUSAL-001 — Does generated future media respond causally to actions?

- **Decision affected:** whether RGB-D prediction can support planning, counterfactual selection, or only auxiliary representation learning.
- **Known:** actions and video share attention, and inference can continue video after action denoising completes. [XWAM-PAPER-V2, pp.4-6; XWAM-CODE-72CF]
- **Unknown:** whether controlled action interventions produce the correct future-state and contact differences rather than visually plausible but action-insensitive continuations.
- **Discriminating evidence:** paired initial observations with feasible alternative actions, ground-truth rollouts, action-swap and no-op controls, and metrics on task state, contact, geometry, and counterfactual ranking.
- **Closure condition:** future differences track interventions and predict observed outcome ordering beyond text/scene priors across unseen scenarios.

### RQ-XWAM-CONTEXT-001 — Is one observation sufficient for partial observability?

- **Decision affected:** whether to add image/state history or memory before changing model scale.
- **Known:** the released contract conditions on one frame and state per view and predicts a fixed future. [XWAM-PAPER-V2, pp.4-5]
- **Unknown:** failure contribution from occluded object state, velocity, contact phase, and prior gripper action.
- **Discriminating evidence:** failure labels plus matched one-frame and short-history models, with tasks sliced by occlusion and dynamics and equal training/inference budgets.
- **Closure condition:** history provides a statistically supported gain concentrated in partial-observability slices without unacceptable clean-task or latency regression.

### RQ-XWAM-TRANSFER-001 — Which pretraining sources improve unseen RoboCasa conditions?

- **Decision affected:** source mixture and target replay for further SFT.
- **Known:** the paper combines five source families and reports a final 79.2% RoboCasa average, but the complete source sampling/filter manifest is not public. [XWAM-PAPER-V2, pp.6-10 and 16]
- **Unknown:** source-specific marginal value, interference, duplicate leakage, and whether gains transfer to unseen layouts, styles, objects, or tasks.
- **Discriminating evidence:** equal-exposure leave-one-source-out or influence approximations, episode-family deduplication, source-gradient diagnostics, and Original RoboCasa scenario slices.
- **Closure condition:** a source effect is stable under equal exposure and traceable to declared target slices rather than aggregate scale alone.

### RQ-XWAM-INTERFACE-001 — Can X-WAM transfer beyond its two released embodiments?

- **Decision affected:** adapter-only transfer versus model adaptation for a new robot or benchmark.
- **Known:** the canonical tensors support dual-arm slots, but the released SFT states and clients implement one RoboCasa and one RoboTwin contract. [XWAM-CODE-72CF; XWAM-HF-CHECKPOINTS]
- **Unknown:** tolerance to new camera roles, kinematics, state fields, action/controller semantics, frequencies, and calibration.
- **Discriminating evidence:** a complete source-to-target interface map, deterministic adapter tests, coverage of target values by checkpoint statistics, open-loop actions, then controlled closed-loop adaptation comparisons.
- **Closure condition:** every field has validated semantics and an adapter-only baseline distinguishes interface incompatibility from learned domain mismatch.

### RQ-XWAM-METRICS-001 — Which diagnostics predict closed-loop improvement?

- **Decision affected:** optimization objective and selection metric.
- **Known:** X-WAM reports RGB, depth, point-cloud, latency, and policy-success metrics, but these evaluate different properties. [XWAM-PAPER-V2, Tables 1-4]
- **Unknown:** which offline metrics correlate with success overall and within contact, occlusion, precision, and long-horizon failure slices.
- **Discriminating evidence:** per-episode predictions and rollouts with metric vectors, uncertainty, failure labels, seeded corruptions, and rank/calibration analysis.
- **Closure condition:** a metric bundle detects known failures and predicts held-out closed-loop outcomes sufficiently to support model selection under a declared protocol.

## Sources

Research-state facts use `XWAM-PAPER-V2`, `XWAM-CODE-72CF`, `XWAM-HF-CHECKPOINTS`, `XWAM-HF-ROBOCASA`, and `XWAM-HF-ROBOTWIN`.
