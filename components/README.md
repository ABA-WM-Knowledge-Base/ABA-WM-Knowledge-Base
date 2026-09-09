---
id: world-model-kb.components
title: World Model Components
kind: index
status: maintained
last_updated: 2026-09-09
owners:
  - AIBuildAI world-model group
---

# World Model Components

## Retrieval metadata

**Relevant queries:** world-model component knowledge, world representation, dynamics modeling, reasoning, generative modeling, fast video inference, action conditioning, world-model–policy interface, independently scoped component entry, current Component entrypoints.

**Knowledge provided:** The current Component entrypoints, the knowledge boundary declared by each entry, and the relationship between Component knowledge and the other KB parts.

**Related pages:** [Foundations](../foundations/README.md) owns model-independent definitions and formalisms; [Papers](../papers/README.md) owns individual-work methods and experiments; [Models](../models/README.md) owns concrete model implementations and execution state; [Benchmarks](../benchmarks/README.md) owns versioned tasks and evaluation contracts; the [global index](../INDEX.md) exposes all five parts as peer knowledge inputs.

## Scope

`components/` is an extension space for independently scoped world-model knowledge. Each Component declares what it owns, how its material is organized, and how it connects to Foundations, Papers, Models, or other Components. The part does not impose a common chapter outline, evidence-question sequence, file inventory, retrieval index, or internal directory depth.

The seven current entries organize their cross-paper syntheses into topic-appropriate pages because that structure fits their current knowledge. Each entry `README.md` is a compact boundary and discovery map; the linked pages own the detailed knowledge. This is a local design choice of the current entries, not a template for future Components.

Component knowledge can inform model diagnosis, intervention design, and experiment interpretation. It does not select Agents, repositories, task order, execution schedules, permissions, or stopping behavior; those remain properties of AIBuildAI and the active task.

## Knowledge map

| Component | Capability boundary | Current organization | Entry |
|---|---|---|---|
| World Representation and Latent State | Observation-space, reconstructive, predictive-embedding, discrete/structured, and multimodal world state | Five method pages plus comparison | [World Representation](world-representation/README.md) |
| Dynamics Modeling | Recurrent latent, decoder-free latent, observation-space, occupancy/ego, and joint multimodal transitions | Five method pages plus comparison | [Dynamics Modeling](dynamics-modeling/README.md) |
| Reasoning for World Models | Latent simulation, imagined decision learning, predictive representation, explicit physical reasoning, and reasoning-to-generation coupling | Five method and comparison pages | [Reasoning](reasoning/README.md) |
| Generative Modeling | Conditional future modeling across autoregressive, diffusion, latent, flow, video, and action-conditioned systems | Seven method pages plus comparison | [Generative Modeling](generative-modeling/README.md) |
| Fast Video Inference | Reduction of sampling work, repeated computation, attention cost, and delay before usable outputs | Few-step distillation, training-free caching, efficient attention, and causal/streaming generation | [Fast Video Inference](fast-video-inference/README.md) |
| Action Representation and Conditioning | Action representation routes (conditioning input, jointly denoised modality, inferred latent), denoising schedules, and action-to-future-prediction coupling | Five method and comparison pages | [Action Conditioning](action-conditioning/README.md) |
| World Model to Policy Interface | The five consumption modes of world-model output, offline synthetic trajectories, rollout selection and evaluation, deployment boundaries, and the reasoner-to-policy evidence gap | Four method and comparison pages | [WM-Policy Interface](wm-policy-interface/README.md) |

The seven entries are non-exclusive. For example, a low-latency action-conditioned video planner may require representation, dynamics, reasoning, generative-modeling, fast-video-inference, action-conditioning, and world-model–policy-interface knowledge together with canonical action, planning, and evaluation pages from Foundations.

## Ownership boundary

| Knowledge type | Canonical owner |
|---|---|
| General definition, formalism, or method family | [Foundations](../foundations/README.md) |
| One paper's architecture, protocol, code, result, or reproduction state | [Papers](../papers/README.md) |
| Knowledge declared by one Component entry | That Component's declared owner page or pages |
| One named model's checkpoint, interface, training recipe, metric, or execution state | [Models](../models/README.md) |

The current entries cite and link to other canonical owners instead of reproducing their full accounts. Optional local source registries contain only identities not already owned elsewhere in the repository. World Representation and Dynamics Modeling reuse existing Foundation, Paper, and Model source IDs.

## Extensibility

Future Components may use a single page, several topic pages, machine-readable metadata, a local source registry, or another structure appropriate to their knowledge surface. They do not need to copy any current directory layout or section order.

For repository interoperability, a new entry should expose a stable entrypoint in this knowledge map or the [global index](../INDEX.md), state its canonical knowledge boundary, keep links resolvable, and reuse globally unique source IDs when it cites registered evidence. These are repository-level discoverability and provenance properties, not a prescribed Component design.

No part-level Component retrieval index is currently used. The current entries expose page-level retrieval metadata by their own design; another Component may choose a different retrieval representation without introducing workflow-orchestration authority.
