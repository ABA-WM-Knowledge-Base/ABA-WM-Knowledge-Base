---
id: world-model-kb.components.reasoning.reasoning-generation-action
title: Reasoning–Generation–Action Integration
kind: component
status: maintained
last_updated: 2026-08-19
owners:
  - AIBuildAI world-model group
---

# Reasoning–Generation–Action Integration

## Retrieval metadata

**Relevant queries:** unified reasoner generator, Cosmos 3 mixture of transformers, autoregressive diffusion coupling, reasoning conditioned generation, forward dynamics, inverse dynamics, WAM, reasoning-to-action interface.

**Knowledge provided:** How Cosmos 3 places explicit reasoning and continuous generation in one sequence model, what information can flow between the streams, which action surfaces remain distinct, and how to test transfer across the interface.

**Related pages:** [Generative Modeling omnimodal generation](../generative-modeling/omnimodal-generation.md) owns the generative lineage; [Cosmos3-Nano architecture](../../models/cosmos3-nano/architecture.md) owns exact model implementation; [action modeling](../../models/cosmos3-nano/action-modeling.md) owns FD/ID/WAM interfaces.

## Integration problem

An explicit Reasoner can describe intent or physical relations without producing a future trajectory. A Generator can produce a plausible future without exposing the semantic state used. A policy can issue actions without generating either explanation or media. Integration attempts to share context among these surfaces while preserving their different objectives and output representations.

The critical questions are architectural rather than terminological:

- Which tokens or latents represent each modality?
- Which stream may attend to which other stream?
- Which loss updates which parameters?
- Can generated evidence revise the reasoning state?
- Which output is sampled, decoded, or executed?
- What measurement establishes transfer across the interface?

Calling a model “unified” does not answer these questions.

## Cosmos 3 mixture-of-transformers interface

Cosmos 3 uses paired autoregressive and diffusion parameter streams. The Nano checkpoint contains an approximately 8B autoregressive Reasoner tower and an approximately 8B diffusion Generator tower. Autoregressive tokens represent language and visual context; diffusion subsequences represent continuous video, audio, and action latents. [C3-TR, pp. 8–13]

The attention rule is directional:

- autoregressive queries attend to autoregressive context;
- diffusion queries attend to both autoregressive and diffusion context.

This lets semantic context influence continuous generation. It does not let the current diffusion state update the current autoregressive hidden state within the same pass. A reason–generate–inspect–revise loop would therefore require an explicit iterative interface or a later pass. [C3-TR, Fig. 3]

Separate parameter streams also mean that a shared sequence does not imply a shared objective. The Reasoner is autoregressive; the Generator uses rectified flow. Any claim that one tower improves the other needs an ablation at the coupling surface.

## Distinct action surfaces

Cosmos 3 exposes several action-related modes:

| Surface | Conditional question | Output | Not equivalent to |
|---|---|---|---|
| Forward dynamics | what future follows these actions? | future media/state latent | action policy |
| Inverse dynamics | which action could explain a transition? | inferred action | unique causal action |
| Joint world-action modeling | which actions and futures co-occur? | joint action/media sample | verified closed-loop controller |
| Reasoner planning | what subgoals or steps make sense? | language plan | typed action tensor |
| Policy-DROID | what action chunk should this robot execute? | embodiment-specific action | base Nano WAM |

[C3-TR, pp. 55–69]

Internal agreement between generated action and generated video can be a shared hallucination. Grounding requires replay against realized transitions, feasibility checks, and closed-loop outcomes.

## Transfer hypotheses

### Structured semantic context

Object, relation, affordance, or subgoal representations in the autoregressive stream may improve Generator condition adherence. The architecture makes the path plausible because diffusion queries attend to autoregressive tokens. A valid test freezes Generator weights and sampling parameters, changes only the semantic representation, and measures physical event accuracy and action response.

### Generated-future verification

Generated futures may reveal contradictions in a language plan. Because same-pass diffusion feedback does not update the Reasoner, this requires an explicit second-stage verification loop. Compare the loop with a Reasoner-only self-revision baseline at matched latency and total model evaluations.

### Shared representation for action

Reasoner or Generator features may reduce action-post-training data needs. This remains false unless a matched frozen-feature or initialization comparison improves held-out control without weakening the typed action contract.

### Joint consistency objectives

Action and future-video losses may regularize one another. The hypothesis fails if internal consistency rises while realized transition error, feasibility, or closed-loop success does not.

## Evaluation matrix

| Claim | Minimum comparison | Primary metrics | Required controls |
|---|---|---|---|
| Better reasoning improves generation | rich versus ablated semantic context | condition adherence, event/state accuracy | frozen Generator, fixed seeds and sampler |
| Generated futures improve reasoning | one-pass versus explicit verify-and-revise | counterfactual answer and plan correctness | matched total compute |
| Joint WAM improves actions | action-only versus joint action/video | feasibility and closed-loop success | same action data and policy capacity |
| Shared features reduce data needs | pretrained versus scratch/frozen/adapted | sample-efficiency curve | same target data and optimizer |
| Longer internal loop helps | iterations at fixed or reported compute | accuracy–latency Pareto | identical stopping/evaluator |

Media quality, text accuracy, action error, and closed-loop success remain separate columns. Aggregating them into one “reasoning” score would obscure the interface being tested.

## Failure modes

- **Semantic bypass:** Generator ignores Reasoner tokens; detect with condition swaps and attention-independent outcome changes.
- **Language shortcut:** Reasoner answers correctly without relevant visual evidence; detect with counterfactual images and evidence removal.
- **Shared hallucination:** action and media outputs agree but both conflict with realized dynamics; detect through replay.
- **Interface bottleneck:** useful semantic state cannot pass through token format or attention; detect with oracle structured context.
- **Latency collapse:** iterative verification improves accuracy but violates control rate; report the full accuracy–latency frontier.
- **Variant leakage:** Policy-DROID results are assigned to base Nano; bind every result to its checkpoint and action schema.

## Ownership boundary

This page owns the cross-surface integration logic. Exact MoT tensors and parameterization belong to [architecture](../../models/cosmos3-nano/architecture.md); media generation belongs to [Generator](../../models/cosmos3-nano/generator.md); action schemas belong to [action modeling](../../models/cosmos3-nano/action-modeling.md); and executable DROID behavior belongs to [policy](../../models/cosmos3-nano/policy.md).

## Sources

- [C3-TR] identifies Cosmos 3 report v4 and supplies the MoT attention, Reasoner, Generator, action, and policy surfaces.
