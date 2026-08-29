---
id: world-model-kb.components.action-conditioning.latent-and-pseudo-actions
title: Latent and Pseudo-Actions
kind: component
status: draft
last_updated: 2026-08-20
owners:
  - AIBuildAI world-model group
---

# Latent and Pseudo-Actions

## Retrieval metadata

**Relevant queries:** latent action model, action-free video pretraining, pseudo-action labeling, inverse dynamics labeling, Genie latent actions, LAPA, unlabelled video control.

**Knowledge provided:** The route that recovers actions from video instead of logging them: latent-action mining, inference-time substitution, post-hoc pseudo-labeling, and the precision limits of each.

**Related pages:** The [LAPA Paper entry](../../papers/lapa/README.md) owns latent-action pretraining details and the remapping-to-robot-actions evidence; [inverse dynamics](../../foundations/problem-formulation/inverse-dynamics.md) owns the general action-recovery formulation; [offline synthetic trajectories](../wm-policy-interface/offline-synthetic-trajectories.md) owns the pipeline that consumes pseudo-labeled rollouts.

## Latent actions mined from unlabelled video

Genie trains a tokenizer, a latent action model, and an autoregressive dynamics model on 30,000 hours of unlabelled video; consistent controls emerge without any action labels. At inference, user actions replace the discarded latent-action encoder [WFM-GENIE-2024, pp. 1, 3-4, 7].

The route's verified limits in that instance: one frame per second generation and hallucinated futures [WFM-GENIE-2024, p. 11]. Whether latent actions can represent precise manipulation is untested in the corpus.

LAPA carries the route to robots: latent-action quantization over unlabelled video, then remapping to real robot actions during finetuning. Details and evidence boundaries are owned by the [LAPA Paper entry](../../papers/lapa/README.md).

## Post-hoc pseudo-action labeling

DreamGen generates videos first and infers actions afterwards, with a flow-matching diffusion inverse-dynamics model or a LAPA-style latent-action model [DATA-DREAMGEN-2025, p. 4]. The pseudo-labeled trajectories then train policies at scale; that consumption pipeline, its measured gains, and its missing curation step are owned by [offline synthetic trajectories](../wm-policy-interface/offline-synthetic-trajectories.md).

World2Act avoids the decode-then-label path entirely by aligning action latents with pre-decoding world-model latents; decoding rollouts first raises pseudo-action MSE by 18% and MAE by 19% in its LIBERO measurement [COMP-WPI-WORLD2ACT-2026, p. 25]. The number is registered in the WM-policy interface Component and cited here because it is the only corpus measurement of what pixel decoding costs the action-recovery step.

## Route selection note

Latent and pseudo-actions trade supervision cost against auditability: no action logging is needed, but action quality inherits every error of the recovery model, and there is no ground truth to audit it against. When the downstream consumer is policy training, the audit burden moves to the trajectory level (see [data curation and filtering](../../foundations/data-and-evaluation/data-curation-and-filtering.md)).

## Sources

- [WFM-GENIE-2024] identifies Genie; it resolves through the foundations registry.
- [DATA-DREAMGEN-2025] identifies DreamGen; it resolves through the foundations registry.
- [COMP-WPI-WORLD2ACT-2026] identifies World2Act; it resolves through the WM-policy interface Component's registry.
