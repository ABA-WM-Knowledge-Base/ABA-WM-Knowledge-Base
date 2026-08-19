---
id: world-model-kb.components
title: World Model Components
kind: index
status: maintained
last_updated: 2026-08-19
owners:
  - AIBuildAI world-model group
---

# World Model Components

## Retrieval metadata

**Relevant queries:** world-model component knowledge, reasoning component, generative modeling component, independently scoped component entry, current Component entrypoints.

**Knowledge provided:** The current Component entrypoints, the knowledge boundary declared by each entry, and the relationship between Component knowledge and the other three KB parts.

**Related pages:** [Foundations](../foundations/README.md) owns model-independent definitions and formalisms; [Papers](../papers/README.md) owns individual-work methods and experiments; [Models](../models/README.md) owns concrete model implementations and execution state; the [global index](../INDEX.md) exposes all four parts as peer knowledge inputs.

## Scope

`components/` is an extension space for independently scoped world-model knowledge. Each Component declares what it owns, how its material is organized, and how it connects to Foundations, Papers, Models, or other Components. The part does not impose a common chapter outline, evidence-question sequence, file inventory, retrieval index, or internal directory depth.

Reasoning and Generative Modeling currently use a cross-paper evolutionary synthesis because that structure fits these two topics. Their shared sequence—earlier bottleneck, intervention, mechanism, evidence, and remaining limitation—is a local design choice for these entries, not a template for future Components.

Component knowledge can inform model diagnosis, intervention design, and experiment interpretation. It does not select Agents, repositories, task order, execution schedules, permissions, or stopping behavior; those remain properties of AIBuildAI and the active task.

## Knowledge map

| Component | Capability boundary | Historical span | Entry |
|---|---|---|---|
| Reasoning for World Models | Latent simulation, imagined decision learning, predictive representation, explicit physical reasoning, and reasoning-to-generation coupling | World Models through Cosmos 3 | [Reasoning](reasoning/README.md) |
| Generative Modeling | Conditional future modeling across autoregressive, diffusion, latent, flow, video, and action-conditioned systems | Early recurrent prediction through Cosmos 3 | [Generative Modeling](generative-modeling/README.md) |

The two entries are non-exclusive. For example, action-conditioned video planning may require both the reasoning synthesis and the generative-modeling synthesis, together with canonical action, planning, and evaluation pages from Foundations.

## Ownership boundary

| Knowledge type | Canonical owner |
|---|---|
| General definition, formalism, or method family | [Foundations](../foundations/README.md) |
| One paper's architecture, protocol, code, result, or reproduction state | [Papers](../papers/README.md) |
| Knowledge declared by one Component entry | That Component's declared owner page or pages |
| One named model's checkpoint, interface, training recipe, metric, or execution state | [Models](../models/README.md) |

The two current entries cite and link to other canonical owners instead of reproducing their full accounts. Their local source registries contain only identities not already owned elsewhere in the repository.

## Extensibility

Future Components may use a single page, several topic pages, machine-readable metadata, a local source registry, or another structure appropriate to their knowledge surface. They do not need to copy either current directory layout or section order.

For repository interoperability, a new entry should expose a stable entrypoint in this knowledge map or the [global index](../INDEX.md), state its canonical knowledge boundary, keep links resolvable, and reuse globally unique source IDs when it cites registered evidence. These are repository-level discoverability and provenance properties, not a prescribed Component design.

No part-level Component retrieval index is currently used. The two current entries expose page-level retrieval metadata by their own design; another Component may choose a different retrieval representation without introducing workflow-orchestration authority.
