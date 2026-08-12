---
id: world-model-kb.foundations.representations
title: World-Model Representations
kind: index
status: maintained
last_updated: 2026-08-11
owners:
  - AIBuildAI world-model group
---

# World-Model Representations

## Retrieval metadata

**Relevant queries:** video prediction, latent state, object-centric structure, 3D or 4D geometry, predictive representation learning, JEPA, invariance, or representation bottlenecks.

**Knowledge provided:** representation domains, structural priors, information bottlenecks, and interfaces between learned state and downstream prediction or decision objectives.

**Related pages:** [Problem formulation](../problem-formulation/README.md) defines represented variables; [learning objectives](../learning-objectives/README.md) defines how representations or predictive distributions are fitted; [evaluation](../data-and-evaluation/README.md) owns evidence protocols.

## Canonical boundary

This subpart owns what information a world model encodes or predicts and which structural assumptions shape that representation. It does not own autoregressive or diffusion training algorithms, dataset-specific recipes, or model-specific tensor layouts.

## Topic map

| Topic | Canonical scope |
|---|---|
| [Video world models](video-world-model.md) | Pixel- and token-space temporal prediction, visual observability, and video-specific failure modes |
| [Latent world models](latent-world-model.md) | Compressed predictive states, sufficiency, reconstruction trade-offs, and latent rollout error |
| [Object-centric world models](object-centric-world-model.md) | Entities, slots, relations, compositionality, binding, and interaction structure |
| [3D and 4D world models](3d-and-4d-world-model.md) | Explicit geometry, occupancy, scene dynamics, coordinate frames, and temporal scene structure |
| [Representation learning and JEPA](representation-learning-and-jepa.md) | Predictive representation objectives, target spaces, collapse avoidance, invariance, and abstraction |

Representation comparisons provide knowledge for strategy selection without imposing an AIBuildAI workflow or implementation order.
