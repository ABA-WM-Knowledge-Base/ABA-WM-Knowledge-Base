---
id: world-model-kb.components.wm-policy-interface.comparison-and-optimization
title: WM-Policy Interface Comparison and Optimization
kind: component
status: draft
last_updated: 2026-08-20
owners:
  - AIBuildAI world-model group
---

# WM-Policy Interface Comparison and Optimization

## Retrieval metadata

**Relevant queries:** choose world model consumption mode, synthetic data versus planning versus evaluator, reasoner to policy evidence gap, RoboCasa reasoner, Cosmos3-Nano interface optimization, interface open questions.

**Knowledge provided:** Mode selection axes, recurring evidence-supported patterns, the unestablished reasoner-to-policy causal chain, Cosmos3-Nano attachment hypotheses, and unresolved questions.

**Related pages:** [Offline synthetic trajectories](offline-synthetic-trajectories.md), [rollout selection and evaluation](rollout-selection-and-evaluation.md), and [deployment boundaries](deployment-boundaries.md) own method details; [reasoning-generation-action integration](../reasoning/reasoning-generation-action.md) owns the Cosmos 3 tower interface; [evaluation methodology](../../foundations/data-and-evaluation/evaluation-methodology.md) owns general evidence rules.

## Mode selection axes

| Axis | What it separates | Evidence anchor |
|---|---|---|
| When the model runs | training time (modes A, B, C) vs inference time (D, E) | inference-time modes pay the latency tax at every decision ([deployment boundaries](deployment-boundaries.md)) |
| What is consumed | trajectories (A, B, C) vs rankings/scores (D, E) | trajectory modes need trajectory-level curation; score modes need independent grounding |
| Error exposure | policy visits model errors (A, B, D) vs errors frozen into data (C) vs errors filtered post hoc (E) | model exploitation owned by the [Reasoning Component](../reasoning/latent-simulation-and-imagination.md); frozen-data coverage owned by [data curation and filtering](../../foundations/data-and-evaluation/data-curation-and-filtering.md) |
| Compute profile | one-time generation cost (C: 54 h on 1,500 L40s for 240k trajectories) vs per-decision cost (D: 5 s to 4 min per action) | [DATA-DREAMGEN-2025, pp. 9-10]; [deployment boundaries](deployment-boundaries.md) |

The modes compose: one system can train on synthetic trajectories (C), plan at inference (D), and select candidates by consistency (E). Composition multiplies the failure surfaces; it does not average them.

## Recurring supported patterns

### Score the future, not only the action

The auxiliary-supervision ablation (67.1 vs 44.4) and DreamZero's failure attribution show action quality riding on future-prediction quality ([future-prediction coupling](../action-conditioning/future-prediction-coupling.md)). Every consumption mode inherits this: curation, selection, and evaluation must score predicted futures, not action plausibility alone.

### Curate trajectories before they become data

Mode C's verified pipelines are filter-free and quality-bottlenecked ([offline synthetic trajectories](offline-synthetic-trajectories.md)), and the measured precedent (MimicGen's success-only acceptance) shows a single predicate cutting state-space support to 43.5% on its hardest task [MIMICGEN-PAPER-V1]. The selection operator and its stratification repair are owned by [data curation and filtering](../../foundations/data-and-evaluation/data-curation-and-filtering.md).

### Demand independent grounding for scores

Mode E's verified instances work because something outside the generator anchors them: environment replay, 324,000 human-annotated segments, or a separately trained value model ([rollout selection and evaluation](rollout-selection-and-evaluation.md)). A selector scoring its own generator's futures with its own generator is circular.

### Match the protocol before comparing modes

RoboCasa numbers in this Component span at least three protocols (3,600-trial three-seed, 100-episode, 50-trial five-seed, and a 1,200-trial no-stated-seed variant). No cross-mode comparison is valid without protocol parity; the general rule is owned by [evaluation methodology](../../foundations/data-and-evaluation/evaluation-methodology.md).

## The unestablished chain: reasoner to policy

No paper in the corpus connects a reasoner component to RoboCasa policy success:

- Cosmos Policy, the strongest verified direct policy, is built on the generator line with no reasoner tower [P25-COSMOS-POLICY, pp. 1-3].
- Cosmos 3 has the reasoner tower but evaluates its policies on DROID, RoboLab, RoboArena, MolmoSpaces, and LIBERO-10, never RoboCasa [C3-TR, pp. 65-70].
- X-WAM's 79.2% is a generator-policy result whose margin over 67.8% tracks its 1.49M-episode pretraining, not a reasoning component [COMP-ACT-XWAM-2026, pp. 7, 9, 16].

Consequence: "improve the reasoner's physical knowledge to raise RoboCasa success" is a hypothesis with zero direct literature support in either direction. Any plan on that route must include the experiment that would establish the link, and must explain why better reasoning would beat more data. The tower-interface mechanics belong to [reasoning-generation-action integration](../reasoning/reasoning-generation-action.md); this Component owns the evidence gap between that interface and policy outcomes.

## Cosmos3-Nano attachment map

| Target surface | Method knowledge | Testable hypothesis | Evidence required |
|---|---|---|---|
| Synthetic-demo pipeline | mode C plus curation | per-mode stratified selection over generated demonstrations preserves coverage that global scores delete | before/after per-mode coverage report, matched retention budgets |
| Policy evaluation | mode E validity criterion | long-horizon action-faithful consistency predicts policy outcomes better than visual scores | paired trajectory evaluation against realized success |
| Test-time selection | consistency consensus | best-of-N future-agreement selection transfers to the Nano policy stack | matched-protocol ablation with stated seeds |
| Reasoner contribution | the unestablished chain | reasoner conditioning measurably changes policy success at matched data scale | frozen-generator ablation on one benchmark with protocol parity |

Exact experiment configurations remain in the [Cosmos3-Nano optimization playbook](../../models/cosmos3-nano/optimization-playbook.md); this table provides mechanism and evidence logic.

## Open questions

1. Does any reasoning component improve a manipulation policy under a matched-data ablation? A confirmed absence after a real search is itself decision-relevant.
2. How reliable are learned rewards under rollout drift in mode B? Nothing in the corpus quantifies it.
3. Does the consistency-selection gain survive the full 3,600-rollout, stated-seed protocol?
4. Do current inference-time planners (mode D) exploit their model's errors, and how would that be detected online?

These questions define missing evidence, not work priority or workflow.

## Sources

Method-specific source identities and exact locators are listed on the owning method pages. [C3-TR] anchors the Cosmos3-Nano attachment hypotheses; none is a reproduced optimization result.
