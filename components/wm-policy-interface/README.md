---
id: world-model-kb.components.wm-policy-interface
title: World Model to Policy Interface
kind: component
status: draft
last_updated: 2026-08-20
owners:
  - AIBuildAI world-model group
---

# World Model to Policy Interface

## Retrieval metadata

**Relevant queries:** how a policy consumes a world model, synthetic trajectory training, world model as environment, world model as evaluator, WAM as policy, world model planning cost, reasoner to policy evidence.

**Knowledge provided:** A method-oriented map of the five verified ways a policy consumes world-model output, their measured costs and boundaries, and the one causal chain the literature has not established.

**Related pages:** [Latent simulation and imagination](../reasoning/latent-simulation-and-imagination.md) owns imagination-based behavior learning (Dreamer line); [predictive representation and planning](../reasoning/predictive-representation-and-planning.md) owns latent goal search (JEPA line); [action-conditioned video modeling](../generative-modeling/action-conditioned-video.md) owns planning-use mechanics and failure diagnosis; [model-based RL](../../foundations/decision-making/model-based-rl.md) owns the general MBRL formalism; [data curation and filtering](../../foundations/data-and-evaluation/data-curation-and-filtering.md) owns the selection operator over generated trajectories.

## Component boundary

This Component answers one question: how does world-model output become policy behavior? Five consumption modes are verified in the corpus. Each mode has a different failure surface, so evidence from one mode does not transfer to another.

| Mode | World-model output consumed as | Verified instances | Canonical owner |
|---|---|---|---|
| A. Imagination training | online rollouts as RL experience | World Models, Dreamer, DreamerV3 | [Reasoning Component](../reasoning/latent-simulation-and-imagination.md) |
| B. Interactive environment | an environment for hindsight learning and RL | UniSim (0.58 to 0.81 across 48 tasks) [WFM-UNISIM-2024] | this Component ([comparison](comparison-and-optimization.md) holds the reward-reliability caveat) |
| C. Offline synthetic trajectories | training data generated once, consumed offline | DreamGen, World2Act | [Offline synthetic trajectories](offline-synthetic-trajectories.md) |
| D. Planning substrate | futures searched at inference time | V-JEPA 2-AC, Cosmos Policy planning, IRASim | mechanics owned by [Generative](../generative-modeling/action-conditioned-video.md) and [Reasoning](../reasoning/predictive-representation-and-planning.md); this Component owns the cross-system cost boundary |
| E. Evaluator / selector | futures scored to pick candidates or assess policies | Consistency-Consensus, GigaWorld-1 | [Rollout selection and evaluation](rollout-selection-and-evaluation.md) |

A sixth position, the world model acting directly as the policy, is a degenerate interface (no separation at all) and is owned by [deployment boundaries](deployment-boundaries.md).

## Method map

The multi-page layout below is specific to this WM-Policy Interface Component.

| Method page | Canonical knowledge owned |
|---|---|
| [Offline synthetic trajectories](offline-synthetic-trajectories.md) | mode C: pipeline shapes, measured gains and costs, pixel-versus-latent transfer, the missing curation step |
| [Rollout selection and evaluation](rollout-selection-and-evaluation.md) | mode E: consistency-based candidate selection, evaluator validity criteria, known failure modes |
| [Deployment boundaries](deployment-boundaries.md) | WAM-as-policy claims and their limits: latency evidence across systems, robustness boundary versus VLAs |
| [Comparison and optimization](comparison-and-optimization.md) | mode selection axes, supported patterns, the unestablished reasoner-to-policy chain, Cosmos3-Nano attachment points, open questions |

## Evidence ownership

System details remain in the [Cosmos Policy](../../papers/cosmos-policy/README.md), [DreamZero](../../papers/dreamzero/README.md), [V-JEPA 2](../../papers/v-jepa-2/README.md), and [DreamerV3](../../papers/dreamerv3/README.md) Paper entries; DreamGen's identity is owned by the foundations registry [DATA-DREAMGEN-2025]. The local [source registry](sources.yaml) registers World2Act, Consistency-Consensus, GigaWorld-1, the WAM-versus-VLA robustness study, and LaWAM, which no other registry owns.

This method decomposition belongs to the current WM-Policy Interface Component. It is not a structure requirement for other Components.
