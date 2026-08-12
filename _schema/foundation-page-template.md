---
id: world-model-kb.foundation-page-template
title: Canonical Foundation Page Template
kind: guide
status: maintained
last_updated: 2026-08-11
owners:
  - AIBuildAI world-model group
---

# Canonical Foundation Page Template

Use this template for model-independent concept pages under `foundations/<subpart>/`. Replace every angle-bracket field before validation. Remove a section only when it is structurally inapplicable; preserve retrieval metadata, provenance, and the distinction between sourced claims, KB synthesis, and hypotheses.

```markdown
---
id: world-model-kb.foundations.<subpart>.<topic>
title: <page-title>
kind: concept
status: <draft|maintained|archived>
last_updated: <YYYY-MM-DD>
owners:
  - <owner>
---

# <Page title>

## Retrieval metadata

**Relevant queries:** <concrete question forms and technical terms associated with this concept>.

**Knowledge provided:** <definitions, formalisms, mechanism comparisons, trade-offs, or evaluation principles available here>.

**Related pages:** <link adjacent Foundation owners and relevant Paper or Model instantiations without prescribing a reading order>.

## Definition and scope

State the concept precisely. Where the literature uses competing definitions, preserve each definition's source, assumptions, and consequences rather than manufacturing a false consensus. Identify neighboring concepts that are not equivalent.

## Formalization

Define variables, domains, time indices, conditional distributions, objectives, inputs, and outputs where applicable. State deterministic, stochastic, partially observed, action-conditioned, or learned approximations explicitly. Define every symbol before use.

## Assumptions and invariants

State observability, stationarity, Markov, causal, geometric, temporal, data, compute, and deployment assumptions that affect whether a conclusion transfers. Separate mathematical assumptions from implementation conventions.

## Mechanism or method families

| Family | Core mechanism | Assumptions | Strengths | Failure boundary | Representative evidence |
|---|---|---|---|---|---|
| <family> | <causal computation or learning signal> | <conditions> | <supported advantage> | <invalid regime> | <source ID and locator> |

Compare mechanisms along independent axes. Do not treat a representation family, learning objective, architecture, training regime, and deployment mode as interchangeable classifications.

## Design implications and trade-offs

Connect the concept to variables that can affect model design or evaluation. For each implication, identify its mechanism, operating conditions, expected observable consequence, interaction risk, and evidence that would argue against it. Mark unsourced causal proposals as hypotheses.

## Evaluation and falsification

Specify what the concept predicts, which measurements distinguish competing explanations, which baselines and controls are required, and which result would invalidate a claimed advantage. Separate one-step prediction, long-horizon rollout, perceptual quality, physical consistency, calibration, and downstream control when they test different properties.

## Failure modes and invalid equivalences

Record observable symptoms, plausible causes, affected regimes, diagnostic evidence, and unsupported equivalences. Scientific guardrails constrain claim interpretation; they do not define AIBuildAI stopping, retry, or rollback behavior.

## Cross-part connections

- **Paper evidence:** <links to representative-paper entries that test or instantiate this concept>.
- **Model instantiations:** <links to model pages that implement the concept under specified conditions>.
- **Open questions:** <link unresolved field-level questions to their owner rather than duplicating them>.

## Sources

Resolve model-independent source IDs through `foundations/sources.yaml`; resolve a paper- or model-specific source through that entry's owning registry without duplicating its identity. Use page, section, table, figure, theorem, equation, or symbol locators where available. Identify KB synthesis explicitly when it combines multiple sources.
```

Foundation content is knowledge guidance. It may shape Agent understanding, diagnosis, design judgment, and strategy selection, while AIBuildAI retains authority over task decomposition, Agent and repository selection, execution scheduling, permissions, and external actions.
