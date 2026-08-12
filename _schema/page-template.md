---
id: world-model-kb.page-template
title: Canonical Model Page Template
kind: guide
status: maintained
last_updated: 2026-08-11
owners:
  - AIBuildAI world-model group
---

# Canonical Model Page Template

Copy the template below for a model-topic page. For a representative-paper entry, use [`paper-entry-template.md`](paper-entry-template.md), then apply this page-level metadata pattern to each Markdown owner. Replace every angle-bracket field before validation. Remove sections that are structurally inapplicable, but preserve `## Retrieval metadata` so a consuming system can discover the page without inheriting a workflow policy.

```markdown
---
id: <stable-dot-separated-id>
title: <page-title>
kind: <overview|model|reference|guide|record>
status: <draft|maintained|archived>
last_updated: <YYYY-MM-DD>
owners:
  - <owner>
---

# <Page title>

## Retrieval metadata

**Relevant queries:** <state concrete query patterns and terms related to this page>.

**Knowledge provided:** <state the facts, mechanisms, interfaces, or evidence available here>.

**Related pages:** <link adjacent canonical topics without prescribing a reading order>.

## Operational summary

State the mechanism, scope boundary, and optimization consequence. Omit reading history, project narrative, and generic motivation.

## System boundary and interfaces

Define the component boundary, model variant, inputs, outputs, shapes, time axes, configuration, and assumptions.

## Mechanism

Explain the causal computation or training process. Connect representations, modules, objectives, data flow, and parameter updates.

## Optimization levers

| Lever | Implementation surface | Expected signal | Constraint or regression risk | Validation |
|---|---|---|---|---|
| <controllable variable> | <config/module/data stage> | <metric and direction> | <failure condition> | <controlled test> |

Include only levers supported by a mechanism or mark them explicitly as hypotheses.

## Evaluation and falsification

Specify baseline, controlled comparison, metric, protocol, seeds or rollouts, acceptance threshold, and the result that rejects the hypothesis.

## Failure modes and guardrails

Describe observable symptoms, likely causes, affected regimes, detection signals, and safe fallback behavior.

## Decision blockers

List only unknowns that can change an implementation or experiment decision. Broader unresolved items belong in `research-queue.md`.

## Sources

Resolve source IDs through the model entry's `sources.yaml`; include page, table, section, symbol, or artifact locator where available.
```

The model entry's `optimization-playbook.md`, `evaluation.md`, `codebase.md`, and `reproduction.md` provide additional experiment, evaluation, implementation, and execution evidence. The consuming AIBuildAI workflow determines whether and when to use them.
