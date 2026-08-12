---
id: world-model-kb.foundations.representations.object-centric-world-model
title: Object-Centric World Models
kind: concept
status: maintained
last_updated: 2026-08-11
owners:
  - AIBuildAI world-model group
---

# Object-Centric World Models

## Retrieval metadata

**Relevant queries:** object-centric world model, slots, entities, relation network, graph dynamics, interaction network, compositional dynamics, object permanence, or slot binding.

**Knowledge provided:** entity-and-relation representations, interaction equations, object discovery and temporal-binding trade-offs, and evaluation criteria for compositional physical prediction.

**Related pages:** [Latent world models](latent-world-model.md) covers unstructured learned state; [state, observation, and belief](../problem-formulation/state-observation-and-belief.md) covers persistence under partial observability; [3D and 4D world models](3d-and-4d-world-model.md) covers spatial representations.

## Definition and formalism

An object-centric world model represents a scene as a set or graph of entity variables and predicts their individual and relational evolution. For object states `o_j`, relation attributes `r_k`, and directed edges `k`, an Interaction Network has the schematic form

```text
e_k = f_R(o_sender(k), o_receiver(k), r_k),
o'_j = f_O(o_j, sum_{k: receiver(k)=j} e_k, x_j),
```

where `e_k` is an interaction effect and `x_j` can contain external forces or action information. Permutation-equivariant aggregation enables the same mechanism to act on different entity counts and orderings. [REP-INTERACTION-NET-2016]

Learned `slots` are exchangeable latent variables intended to bind recurring scene components. A slot is not necessarily a physical object: it may encode a part, group, background region, texture, or view-dependent fragment. Objecthood and stable identity require empirical validation.

## Assumptions and scope

Object-centric representations are attractive when dynamics depend on persistent entities, sparse interactions, and reusable relational rules. They are less natural for fluids, smoke, lighting, deformable continua, or global fields unless combined with dense representations.

Supervised object state assumes entity labels or detectors. Unsupervised object discovery assumes that reconstruction, attention, or temporal regularities make useful entities identifiable. Neither guarantees that slots align with task-relevant causal units.

## Representation and mechanism families

| Family | Entity source | Interaction model | Main boundary |
|---|---|---|---|
| Supervised object state | boxes, masks, tracks, simulator state | MLP or graph network | depends on annotation/detector ontology |
| Interaction/graph network | explicit nodes and edges | learned pairwise or message passing | graph construction and long-range effects |
| Slot-based encoder | competition over image features | shared slot dynamics | identity and segmentation are emergent |
| Probabilistic object model | latent entities with iterative inference | generative relational dynamics | expensive inference and local optima |
| Hybrid object-background model | slots plus dense global field | graph plus convolution/transformer | information can leak through background |

Visual Interaction Networks predicted physical trajectories from images using object representations. Contrastive Structured World Models learned object-factored dynamics without pixel reconstruction. Slot Attention introduced iterative competitive binding, while OP3 combined object-centric perception, prediction, and planning. [REP-VIN-2017; REP-CSWM-2020; REP-SLOT-ATTENTION-2020; REP-OP3-2020]

## Design implications and trade-offs

Optimization choices include slot count and dimensionality, binding iterations, temporal matching, relation graph sparsity, shared versus type-specific dynamics, birth/death rules, background capacity, action attribution, and occlusion memory. Fixed slot counts simplify batching but can under-segment crowded scenes or create empty/duplicate entities. Strong reconstruction can reward texture partitions instead of causal objects.

Temporal consistency can be trained with matching, recurrent slots, prediction losses, or tracked supervision. Matching solves permutation ambiguity at a particular step but does not by itself preserve semantic identity through occlusion. Relation inductive biases improve data efficiency when the graph matches the process; incorrect locality or pairwise assumptions can suppress global and higher-order interactions.

## Evaluation and falsification

- Measure segmentation or tracking only when ground truth exists, and separate it from dynamics quality.
- Test entity identity through occlusion, re-entry, collision, and camera motion.
- Evaluate compositional generalization to novel object counts, arrangements, and interaction graphs.
- Intervene on one entity or relation and check localized and propagated effects.
- Compare planning or prediction against an unstructured latent under matched capacity and compute.
- Probe whether task-relevant information is carried by slots or bypassed through background/global features.

An object-centric claim is weakened when slot assignments vary arbitrarily across time, when relations do not improve intervention predictions, or when generalization disappears outside the training object count. A causal-object claim is falsified if interventions on the proposed entity variable do not correspond to coherent environment changes.

## Failure modes

- **Identity switching:** slots exchange entities across frames.
- **Under- or over-segmentation:** one slot merges multiple objects or fragments one object.
- **Occlusion reset:** hidden entities are forgotten or re-created with different state.
- **Background leakage:** global features carry the dynamics, leaving slots decorative.
- **Fixed-cardinality mismatch:** births, deaths, or crowded scenes exceed the slot budget.
- **Interaction misspecification:** pairwise/local graphs omit global, contact, or higher-order effects.
- **Object bias mismatch:** amorphous or deformable phenomena do not decompose cleanly.
- **Metric substitution:** segmentation quality is treated as evidence of predictive or control sufficiency.

## Cross-part instantiations

- [Cosmos3-Nano architecture](../../models/cosmos3-nano/architecture.md) does not inherit an object-centric representation unless its documented implementation exposes one.
- [Reasoner](../../models/cosmos3-nano/reasoner.md) may describe objects and relations in language without using explicit persistent slots internally.
- [Generator](../../models/cosmos3-nano/generator.md) can be probed for identity, occlusion, and compositional interaction; such probes test behavior, not internal ontology.
- [Optimization playbook](../../models/cosmos3-nano/optimization-playbook.md) can treat object/slot auxiliaries as ablation hypotheses where task failures indicate binding or interaction errors.

## Sources

- [REP-INTERACTION-NET-2016] Battaglia et al., *Interaction Networks for Learning about Objects, Relations and Physics*, NeurIPS 2016, arXiv:1612.00222.
- [REP-VIN-2017] Watters et al., *Visual Interaction Networks: Learning a Physics Simulator from Video*, NeurIPS 2017, arXiv:1706.01433.
- [REP-CSWM-2020] Kipf, van der Pol, and Welling, *Contrastive Learning of Structured World Models*, ICLR 2020, arXiv:1911.12247.
- [REP-SLOT-ATTENTION-2020] Locatello et al., *Object-Centric Learning with Slot Attention*, NeurIPS 2020, arXiv:2006.15055.
- [REP-OP3-2020] Veerapaneni et al., *Entity Abstraction in Visual Model-Based Reinforcement Learning*, CoRL 2019, PMLR 100 (2020).
