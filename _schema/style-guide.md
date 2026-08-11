---
id: world-model-kb.style
title: Knowledge-Oriented Writing Style
kind: guide
status: maintained
last_updated: 2026-08-11
owners:
  - AIBuildAI world-model group
---

# Knowledge-Oriented Writing Style

## Optimize for decisions

Write for an agent selecting, implementing, or evaluating a model intervention. A page is complete when it supports a decision under explicit conditions, not when it summarizes every source paragraph.

Prefer this chain:

`observed behavior → plausible mechanism → controllable lever → implementation surface → predicted metric movement → controlled test → failure or stop condition`

A statement such as “the model supports video and action” is insufficient. Specify the encoder or representation, token or latent placement, temporal contract, attention or denoising behavior, objective, updated parameters, output contract, relevant configuration, and the conditions under which the capability fails.

## Describe retrieval without controlling workflow

Every canonical model-topic page starts with `## Retrieval metadata` and the labels `Relevant queries`, `Knowledge provided`, and `Related pages`. Query terms support lexical or semantic discovery, while canonical ownership identifies where a topic is explained completely.

`agent-index.yaml` maps task themes to knowledge, strategies, best practices, and evidence that can ground Agent decisions. It supports dynamic retrieval but does not define AIBuildAI's Agent selection, repository selection, task sequencing, execution scheduling, permissions, or external actions.

Progressive disclosure may be useful as a retrieval pattern, but it remains a choice of the consuming workflow rather than a KB requirement.

## Preserve canonical ownership

Place the full explanation in one owner page. Elsewhere, state only the dependency needed for the local argument and link to the owner. Do not duplicate tables, result sets, input/output contracts, or training recipes across pages.

When sources disagree, preserve the precise variant, revision, and operating conditions for each statement. Do not merge them into an apparent consensus.

## Use decision-ready facts

A reusable fact states:

- subject and exact model or component variant;
- mechanism or interface;
- operating conditions and scope;
- optimization or evaluation consequence;
- failure boundary or missing condition;
- precise source locator.

Use provenance grammar without ranking sources:

- “The technical report reports …” for a paper result.
- “The pinned implementation computes …” for a code fact.
- “Run `<experiment-id>` produced …” for a local observation.
- “Optimization hypothesis: …” for a proposed causal intervention.
- “Unresolved: …” for a condition that still blocks a decision.

Never turn a reported correlation or an uncontrolled local result into a causal optimization rule.

## Specify optimization levers

For every recommended lever, name the target behavior, change surface, mechanism, expected metric and direction, required data, compute cost, interaction risks, regression metrics, controlled baseline, acceptance threshold, and falsification result. Separate low-cost inference controls from data, objective, architecture, and post-training changes.

Avoid generic recommendations such as “use better data,” “fine-tune the model,” or “improve reasoning.” Replace them with variables an agent can set or code it can change.

## Record experiments reproducibly

An experiment record includes exact revisions, environment, data identity, resolved configuration, command, random seeds or rollouts, baseline, intervention, controlled variables, raw outputs, metrics, aggregation, artifacts, failures, fixes, and a conclusion tied to a predeclared criterion.

Keep execution records in `reproduction.md` or referenced artifacts. Canonical topic pages may include a stable conclusion and scope after the record exists; they must not embed transient status narration.

## Quantitative results

Every result retains model variant, task, dataset, metric definition and direction, protocol, comparison set, key generation or control parameters, judge or human-evaluation conditions, seed count or rollout count, compute conditions when material, and date for changing leaderboards. If a field is absent from the source, state the missing field rather than inventing it.

## Sources and locators

Resolve every source ID through the entry's `sources.yaml`. Use locators such as `[C3-TR, p. 14, Table 2]`, `[C3-FW-ARGS, OmniSetupOverrides]`, or `[LOCAL-REPRO-20260809, run_summary]`. Link to the canonical owner when the source has already been interpreted there.

## Language and form

Canonical KB content is English. Preserve official product names, code identifiers, prompts, and source titles verbatim when required for identity or reproduction.

Use compact paragraphs for causal reasoning, tables for exact mappings, and diagrams only for nontrivial flows. Avoid fragmented bullet accumulation, promotional adjectives, undefined “SOTA,” and claims of support without interface and operating conditions.

Exclude progress narration, reading completion, team activity, audience-directed project justification, and statements whose only function is to persuade a human that the topic is relevant. State the actionable consequence directly.

Visual realism does not establish physical correctness. A text plan does not establish executable policy behavior. A public checkpoint does not establish complete training or benchmark reproducibility. Encode these distinctions wherever they affect a decision.
