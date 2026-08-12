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

Write for an agent defining, selecting, implementing, or evaluating a model intervention. A page is complete when it supports a judgment under explicit conditions, not when it summarizes every source paragraph.

Prefer this chain:

`observed behavior → plausible mechanism → controllable lever → implementation surface → predicted metric movement → controlled test → failure or stop condition`

A statement such as “the model supports video and action” is insufficient. Specify the encoder or representation, token or latent placement, temporal contract, attention or denoising behavior, objective, updated parameters, output contract, relevant configuration, and the conditions under which the capability fails.

## Describe retrieval without controlling workflow

Every canonical Foundation, Paper, or model-topic page starts with `## Retrieval metadata` and the labels `Relevant queries`, `Knowledge provided`, and `Related pages`. Query terms support lexical or semantic discovery, while canonical ownership identifies where a topic is explained completely.

Foundation `retrieval-index.yaml` and model-entry `agent-index.yaml` map query themes to knowledge, strategies, best practices, and evidence that can ground Agent decisions. They support dynamic retrieval but do not define AIBuildAI's Agent selection, repository selection, task sequencing, execution scheduling, permissions, or external actions.

Progressive disclosure may be useful as a retrieval pattern, but it remains a choice of the consuming workflow rather than a KB requirement.

## Preserve canonical ownership

Place the full explanation in one owner page. Elsewhere, state only the dependency needed for the local argument and link to the owner. Do not duplicate tables, result sets, input/output contracts, or training recipes across pages.

When sources disagree, preserve the precise variant, revision, and operating conditions for each statement. Do not merge them into an apparent consensus.

## Write model-independent foundations

A Foundation page owns a transferable concept rather than a single paper's narrative or a single model's implementation. Organize it around the question the concept resolves:

- preserve competing definitions when the field has no universal one;
- define variables, distributions, objectives, and assumptions before comparing methods;
- separate what is represented from how it is learned and how it is used for decisions;
- distinguish a source-reported claim from a KB synthesis across sources;
- state which evidence would make a proposed generalization invalid;
- connect to representative-paper evidence and model-specific instantiations without duplicating their results or implementation detail.

Do not universalize terminology coined by one product or paper. Labels such as world foundation model and world action model require an explicit capability and interface boundary. A Foundation comparison may influence design judgment, but it must not encode task priority, required reading order, Agent selection, or execution policy.

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

Resolve every source ID through the nearest owning registry: `foundations/sources.yaml`, `papers/<paper-id>/sources.yaml`, or `models/<model-id>/sources.yaml`. Attach a precise section, page, table, figure, equation, theorem, symbol, or artifact locator; existing examples include `[C3-TR, p. 14, Table 2]`, `[C3-FW-ARGS, OmniSetupOverrides]`, and `[LOCAL-REPRO-20260809, run_summary]`. Link to the canonical owner when the source has already been interpreted there.

Source type, venue, and version describe provenance; they do not substitute for claim-level reasoning. For broad or contested claims, triangulate primary sources with different assumptions and identify the resulting synthesis explicitly.

## Language and form

Canonical KB content is English. Preserve official product names, code identifiers, prompts, and source titles verbatim when required for identity or reproduction.

Use compact paragraphs for causal reasoning, tables for exact mappings, and diagrams only for nontrivial flows. Avoid fragmented bullet accumulation, promotional adjectives, undefined “SOTA,” and claims of support without interface and operating conditions.

Exclude progress narration, reading completion, team activity, audience-directed project justification, and statements whose only function is to persuade a human that the topic is relevant. State the actionable consequence directly.

Visual realism does not establish physical correctness. A text plan does not establish executable policy behavior. A public checkpoint does not establish complete training or benchmark reproducibility. Encode these distinctions wherever they affect a decision.
