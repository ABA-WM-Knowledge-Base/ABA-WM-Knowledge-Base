---
id: world-model-kb.schema
title: Agent Retrieval and Authoring Contract
kind: reference
status: maintained
last_updated: 2026-08-11
owners:
  - AIBuildAI world-model group
---

# Knowledge Retrieval and Authoring Contract

`_schema/` defines how KB content and retrieval metadata are represented. It contains no world-model facts and does not define AIBuildAI workflow.

## Operating concepts

| Concept | Contract |
|---|---|
| Retrieval profile | A non-binding association between query themes and potentially relevant documents. |
| Canonical ownership | One page owns the full reusable explanation of a topic. Other pages summarize only the dependency and link to the owner. |
| Progressive disclosure | An optional retrieval pattern in which additional sources are opened when more detail is useful. |
| Workflow authority | AIBuildAI runtime, Agent configuration, task instructions, and policies remain authoritative. |
| Decision-ready fact | A scoped statement that includes mechanism, operating conditions, optimization consequence, failure boundary, and source locator. |
| Optimization lever | A controllable variable connected to an implementation surface, predicted metric movement, trade-offs, and a falsification test. |
| Experiment record | A reproducible record of baseline, intervention, configuration, environment, inputs, outputs, metrics, seeds or rollouts, artifacts, failures, and deviations. |

## Retrieval metadata use

[The global index](../INDEX.md) and [`agent-index.yaml`](../models/cosmos3-nano/agent-index.yaml) expose topic and document associations. They are discovery aids, not an execution sequence. A consuming workflow decides what to load, in what order, and whether additional provenance, implementation, evaluation, or reproduction evidence is useful.

## Canonical page contract

Every model-topic page begins its body with `## Retrieval metadata` and exposes `Relevant queries`, `Knowledge provided`, and `Related pages`. The remaining content supports model understanding and evidence-based decisions without prescribing Agent behavior.

Canonical pages must not contain:

- reading history, completion claims, or progress narration;
- generic statements about why a project or topic matters;
- audience-directed explanations that do not change a modeling decision;
- duplicated long-form content owned by another page;
- experiment observations presented without a reproducible record;
- unsupported optimization prescriptions or implied causal conclusions from uncontrolled comparisons.

## File contracts

| File | Contract |
|---|---|
| [`metadata.schema.yaml`](metadata.schema.yaml) | Frontmatter, directory boundary, required model files, and routing fields |
| [`manifest.schema.yaml`](manifest.schema.yaml) | Model identity, pinned revisions, mode-specific interfaces, execution-state pointer, and document map |
| [`sources.schema.yaml`](sources.schema.yaml) | Stable source identities, revisions, locators, and local integrity fields |
| [`naming-conventions.md`](naming-conventions.md) | Stable paths, IDs, model names, versions, and terminology |
| [`style-guide.md`](style-guide.md) | Agent-oriented content, provenance grammar, optimization detail, and experiment requirements |
| [`page-template.md`](page-template.md) | Canonical model-topic page template |
| [`paper-entry-template.md`](paper-entry-template.md) | Representative-paper entry contract |

## Update placement

| New information | Canonical destination |
|---|---|
| Stable mechanism, interface, or limitation | The owning topic page |
| Model identity, revision, license, or component inventory | `manifest.yaml` |
| Source identity, immutable version, or artifact hash | `sources.yaml` |
| Local command, failure, fix, output, or run state | `reproduction.md` |
| Reusable intervention and selection rule | `optimization-playbook.md` |
| Unresolved condition that blocks a decision | `research-queue.md` |
| Path, routing, or schema change | `CHANGELOG.md` and the relevant schema file |

A statement is promoted from an experiment record into a canonical topic page only when its scope, conditions, and reusable consequence are explicit.
