---
id: world-model-kb.components.action-conditioning
title: Action Representation and Conditioning
kind: component
status: draft
last_updated: 2026-08-20
owners:
  - AIBuildAI world-model group
---

# Action Representation and Conditioning

## Retrieval metadata

**Relevant queries:** action representation, action conditioning route, latent frame injection, joint video-action denoising, asynchronous denoising, latent action, pseudo-action labeling, future-state auxiliary supervision, action history conditioning.

**Knowledge provided:** A method-oriented map of how actions are represented inside world/action models: the three verified representation routes, denoising-schedule choices for jointly predicted actions, and the measured coupling between action decoding and future prediction.

**Related pages:** [Action-conditioned video modeling](../generative-modeling/action-conditioned-video.md) owns action timing and semantics, the UniSim/iVideoGPT/IRASim/DIAMOND cross-architecture evidence, planning use, and failure diagnosis; [actions and interventions](../../foundations/problem-formulation/actions-and-interventions.md) owns causal action semantics; [inverse dynamics](../../foundations/problem-formulation/inverse-dynamics.md) owns the action-recovery formulation; [Cosmos3-Nano action modeling](../../models/cosmos3-nano/action-modeling.md) owns the concrete target-model action surfaces.

## Component boundary

This Component answers one question: where do actions live inside the model? Three routes are verified in the corpus, and they are not interchangeable:

| Route | Actions are | Verified instances | Method page |
|---|---|---|---|
| Conditioning input | an input the model is conditioned on | UniSim embeddings, V-JEPA 2-AC 7D actions, IRASim frame-aligned modulation | owned by [action-conditioned video](../generative-modeling/action-conditioned-video.md); this Component adds only the route comparison |
| Jointly denoised output modality | an output predicted together with futures | DreamZero, X-WAM, Cosmos Policy latent frames | [Latent-frame injection](latent-frame-injection.md), [joint denoising and schedules](joint-denoising-and-schedules.md) |
| Inferred latent or pseudo-action | a variable recovered from video, not logged | Genie latent actions, LAPA, DreamGen pseudo-labels | [Latent and pseudo-actions](latent-and-pseudo-actions.md) |

The route decision precedes every downstream choice: it fixes what supervision is needed, whether an inverse-dynamics model enters the pipeline, and whether action quality can be audited independently of video quality.

## Method map

The multi-page layout below is specific to this Action Conditioning Component.

| Method page | Canonical knowledge owned |
|---|---|
| [Latent-frame injection](latent-frame-injection.md) | representing robot modalities as latent frames in an unchanged video diffusion objective; normalization and duplication contract; training-mix evidence |
| [Joint denoising and schedules](joint-denoising-and-schedules.md) | shared vs asynchronous video/action noise timesteps, closed-loop context replacement, measured latency and success effects |
| [Latent and pseudo-actions](latent-and-pseudo-actions.md) | mining actions from unlabelled video, inference-time action substitution, post-hoc pseudo-action labeling, precision limits |
| [Future-prediction coupling](future-prediction-coupling.md) | the measured dependence of action decoding on predicted futures; failure attribution; the shared history-free gap |
| [Comparison and optimization](comparison-and-optimization.md) | route selection axes, supported patterns, Cosmos3-Nano attachment points, and open questions |

## Evidence ownership

System details remain in the [Cosmos Policy](../../papers/cosmos-policy/README.md), [DreamZero](../../papers/dreamzero/README.md), [LAPA](../../papers/lapa/README.md), [IRASim](../../papers/irasim/README.md), and [V-JEPA 2](../../papers/v-jepa-2/README.md) Paper entries. Cosmos 3 action surfaces remain in the [Cosmos3-Nano Model entry](../../models/cosmos3-nano/README.md). The local [source registry](sources.yaml) registers only X-WAM, which no other registry owns.

This method decomposition belongs to the current Action Conditioning Component. It is not a structure requirement for other Components.
