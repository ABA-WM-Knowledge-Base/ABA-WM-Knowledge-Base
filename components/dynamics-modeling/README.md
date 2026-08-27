---
id: world-model-kb.components.dynamics-modeling
title: Dynamics Modeling
kind: component
status: maintained
last_updated: 2026-08-27
owners:
  - AIBuildAI world-model group
---

# Dynamics Modeling

## Retrieval metadata

**Relevant queries:** world-model dynamics, latent transition, RSSM dynamics, decoder-free dynamics, observation-space forward model, occupancy forecasting, joint video-action transition.

**Knowledge provided:** A method-oriented map of how world-model systems implement \(p(s_{t+1}\mid s_t,a_t)\), which error modes distinguish useful transitions from plausible continuation, and which neighboring Components own generation, imagination, and action schemas.

**Related pages:** [Forward dynamics](../../foundations/problem-formulation/forward-dynamics.md) owns the mathematical FD contract; [world representation](../world-representation/README.md) owns what \(s_t\) is; [generative modeling](../generative-modeling/README.md) owns AR/diffusion/flow families; [reasoning](../reasoning/README.md) owns using transitions for imagination or planning.

## Component boundary

Dynamics in this Component means the learned transition: how a named state is updated under an action, context, or open-loop prior. Inverse dynamics (inferring actions from observed transitions) is out of scope and belongs with Action Representation. Policy heads, best-of-N controllers, and “world model as policy” interfaces belong to a future World Model–Policy Interface Component.

| Dynamics question | In scope | Out of scope |
|---|---|---|
| What predicts the next state? | latent MLP, RSSM, video generator-as-transition, occupancy transformer, joint WAM denoiser | diffusion versus flow as a generic sampler family |
| Does the transition respond to actions? | counterfactual tests | action tokenization recipes |
| Does error compound? | prior rollout, chained clips | actor–critic credit assignment |
| Is the model exploitable? | virtual–real gap, \(P=0\) search | which planner to schedule in AIBuildAI |

A realistic video that is invariant to swapped actions is not successful forward dynamics. A calibrated latent transition is not a policy.

## Method map

The multi-page layout below is specific to this Dynamics Modeling Component.

| Method page | Canonical knowledge owned |
|---|---|
| [Recurrent latent dynamics](recurrent-latent-dynamics.md) | MDN-RNN and RSSM transitions; World Models \(M\); Dreamer/DreamerV3; imagination use linked out |
| [Decoder-free latent dynamics](decoder-free-latent-dynamics.md) | TD-MPC2 SimNorm transitions without observation reconstruction |
| [Observation-space dynamics](observation-space-dynamics.md) | Next-observation transitions; IRASim, DIAMOND, Vista, iVideoGPT; action-video interface linked out |
| [Structured occupancy dynamics](structured-occupancy-dynamics.md) | OccWorld occupancy and ego-trajectory forecasting |
| [Joint multimodal dynamics](joint-multimodal-dynamics.md) | Joint video–state–action transitions; DreamZero, X-WAM, Cosmos FD; not Policy-DROID |
| [Comparison and optimization](comparison-and-optimization.md) | Selection axes, drift and action-invariance tests, Cosmos3-Nano FD attachment, open questions |

## Evidence ownership

Exact architectures, tables, and reproduction state remain in [Paper](../../papers/README.md) entries. Cosmos3-Nano FD/ID/WAM contracts remain on [action modeling](../../models/cosmos3-nano/action-modeling.md). This Component cites those owners and compares transition mechanisms.

The section pattern used across these method pages is a local organizational choice for this Component. It is not a template or validation requirement for other Components.
