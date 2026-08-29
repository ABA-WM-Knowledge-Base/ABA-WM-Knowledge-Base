---
id: world-model-kb.components.world-representation
title: World Representation and Latent State
kind: component
status: maintained
last_updated: 2026-08-29
owners:
  - AIBuildAI world-model group
---

# World Representation and Latent State

## Retrieval metadata

**Relevant queries:** world-model state, latent state, pixel-space world model, reconstructive VAE, RSSM observation head, JEPA embedding as state, occupancy token, multimodal latent stream.

**Knowledge provided:** A method-oriented map of how world-model systems choose what to treat as state, how they compress it, which information they keep or discard, and which evidence bounds those choices.

**Related pages:** [Latent world models](../../foundations/representations/latent-world-model.md) owns generic latent formalisms; [video world models](../../foundations/representations/video-world-model.md) owns observation-surface prediction; [dynamics modeling](../dynamics-modeling/README.md) owns the transition \(p(s_{t+1}\mid s_t,a_t)\); [reasoning](../reasoning/README.md) owns using a state for imagination or planning; [generative modeling](../generative-modeling/README.md) owns how futures are sampled.

## Component boundary

World representation in this Component means the variables a system treats as its current world state: pixels, reconstructive latents, predictive embeddings, discrete tokens, geometric occupancy, or heterogeneous multimodal streams. It answers what is stored and what compression discards. It does not own the transition law, the generative sampler family, or the decision loop that consumes the state.

| Representation surface | Typical state variable | Evidence needed |
|---|---|---|
| Observation-space state | RGB frame or video clip | task-state retention plus action-sensitive visual change |
| Reconstructive latent | VAE or RSSM code with a decoder | rate–distortion plus control-state probes |
| Predictive embedding | target-feature prediction without RGB reconstruction | transfer probes; not automatic dynamics or control |
| Discrete or structured token | VQ or occupancy code | reconstruction versus forecast or planning jointly |
| Multimodal stream | separate semantic and continuous latents | which stream is the executable world state |

A sharp reconstructed frame is not proof that the latent retains contact, object identity, or proprioception. A strong frozen probe is not a world state sufficient for closed-loop control. Quantized latent actions, as in LAPA, are action representations and are not world state; that distinction belongs to a future Action Representation Component.

## Method map

The multi-page layout below is specific to this World Representation Component.

| Method page | Canonical knowledge owned |
|---|---|
| [Observation-space state](observation-space-state.md) | Pixels or video as the state itself; DIAMOND and Vista; perceptual fidelity versus task state |
| [Reconstructive latents](reconstructive-latents.md) | Decoder-backed compression; World Models \(V\), DreamerV3 RSSM, Predict2.5/IRASim/Cosmos codecs as state |
| [Predictive embeddings](predictive-embeddings.md) | Reconstruction-free embeddings as state; V-JEPA 2; information kept versus discarded |
| [Discrete and structured state](discrete-and-structured-state.md) | VQ and occupancy tokens; iVideoGPT and OccWorld; object-centric evidence gap |
| [Multimodal state](multimodal-state.md) | Heterogeneous streams; Cosmos3-Nano AR versus diffusion latents; X-WAM RGB-D/state |
| [Comparison and optimization](comparison-and-optimization.md) | Selection axes, failure diagnostics, Cosmos3-Nano attachment points, and open questions |

These methods are compositional. A system may encode observations with a VAE, predict in that latent, and also keep a language stream. The pages identify the owner of each state medium rather than forcing one exclusive category.

## Evidence ownership

Work-specific architectures, tables, and reproduction state remain in the [Paper](../../papers/README.md) entries. Concrete tensor layouts and interface contracts remain under their named [Model](../../models/README.md) entries. Foundation pages keep model-independent definitions. This Component cites those owners and synthesizes the representation choice across works.

The section pattern used across these method pages is a local organizational choice for this Component. It is not a template or validation requirement for other Components.
