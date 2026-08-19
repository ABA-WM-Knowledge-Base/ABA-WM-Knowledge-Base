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

**Relevant queries:** world-model capability evolution, cross-paper mechanism lineage, reasoning component, generative modeling component, recurring intervention pattern, historical bottleneck, component-level research gap.

**Knowledge provided:** Cross-paper syntheses that explain how a major world-model capability evolved, which mechanism changes addressed earlier bottlenecks, what evidence supports each change, and which limitations remain unresolved.

**Related pages:** [Foundations](../foundations/README.md) owns model-independent definitions and formalisms; [Papers](../papers/README.md) owns individual-work methods and experiments; [Models](../models/README.md) owns concrete model implementations and execution state; the [global index](../INDEX.md) exposes all four parts as peer knowledge inputs.

## Scope

Components is the cross-paper synthesis layer of the KB. A Component follows one capability across several model families and historical stages. Its primary unit is not a paper, checkpoint, or taxonomy category, but a recurring technical problem such as producing decision-relevant reasoning or learning a conditional distribution over future observations.

Each Component answers the same evidence-oriented questions:

1. What limitation existed at the preceding stage?
2. What representation, objective, architecture, data, or inference change was introduced?
3. Through what mechanism could that change improve the target capability?
4. Which experiments or ablations support the claim, under which protocol?
5. Which limitation survived, and what measurement would distinguish the next proposed improvement?

The resulting synthesis can inform model diagnosis, intervention design, and experiment interpretation. It does not select Agents, repositories, task order, execution schedules, permissions, or stopping behavior; those remain properties of AIBuildAI and the active task.

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
| Cross-paper evolution, recurring mechanism pattern, and unresolved component gap | Components |
| One named model's checkpoint, interface, training recipe, metric, or execution state | [Models](../models/README.md) |

Component pages cite and link to those owners instead of reproducing their full accounts. Their source registries contain only identities not already owned elsewhere in the repository.

## Entry contract

Each active entry contains a canonical `README.md` and a local `sources.yaml`. The page begins with retrieval metadata, defines the capability boundary, reconstructs the historical sequence, compares supported intervention patterns, records failure boundaries, maps model-specific attachment points, and preserves open questions as scientific uncertainties rather than work assignments.

No separate Component retrieval index is needed at the present scale. The [global index](../INDEX.md), this knowledge map, page-level retrieval metadata, and semantic retrieval expose both entries without introducing a second routing or orchestration layer.
