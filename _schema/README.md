---
id: world-model-kb.schema
title: Agent Retrieval and Authoring Contract
kind: reference
status: maintained
last_updated: 2026-08-24
owners:
  - AIBuildAI world-model group
---

# Knowledge Retrieval and Authoring Contract

`_schema/` defines how KB content and retrieval metadata are represented. It contains no world-model facts and does not define AIBuildAI workflow.

## Operating concepts

| Concept | Contract |
|---|---|
| Retrieval profile | A machine-readable association between query themes and decision-grounding knowledge. It supports dynamic loading without carrying workflow-orchestration authority. |
| Canonical ownership | One page owns the full reusable explanation of a topic. Other pages summarize only the dependency and link to the owner. |
| Part-local provenance | Foundation, Paper, Model, and Benchmark entries keep source identities in their owning registries. A Component may use a local registry when that suits its design; source IDs remain unique across the repository. |
| Progressive disclosure | An optional retrieval pattern in which additional sources are opened when more detail is useful. |
| Workflow authority | AIBuildAI runtime, Agent configuration, task instructions, and policies remain authoritative. |
| Decision-ready fact | A scoped statement that includes mechanism, operating conditions, optimization consequence, failure boundary, and source locator. |
| Optimization lever | A controllable variable connected to an implementation surface, predicted metric movement, trade-offs, and a falsification test. |
| Experiment record | A reproducible record of baseline, intervention, configuration, environment, inputs, outputs, metrics, seeds or rollouts, artifacts, failures, and deviations. |

## Retrieval metadata use

[The global index](../INDEX.md) exposes non-exclusive knowledge areas. The Foundation [`retrieval-index.yaml`](../foundations/retrieval-index.yaml) associates model-independent queries with canonical concepts; each active Model can expose an `agent-index.yaml`; and each registered Benchmark can expose a `retrieval-index.yaml`. The current Reasoning and Generative Modeling Components expose page-level retrieval metadata by local design; `components/` has no required common retrieval representation. AIBuildAI may dynamically combine these inputs according to the current task and state. None of these knowledge interfaces selects Agents, repositories, task order, or execution schedule.

## Canonical page contract

Every canonical Foundation, Paper, Model, or Benchmark topic page begins its body with `## Retrieval metadata` and exposes `Relevant queries`, `Knowledge provided`, and `Related pages`. Foundation pages own transferable concepts; Paper entries own work-specific evidence; Model pages own concrete instantiations; Benchmark pages own versioned evaluation systems. The remaining content is intended to influence model understanding, diagnosis, strategy selection, and evidence-based decisions without prescribing AIBuildAI workflow orchestration.

Component authors choose the content structure, file layout, and retrieval representation appropriate to their own knowledge surface. The two current Components voluntarily use the same retrieval fields and historical evidence pattern; that choice is not part of the canonical page contract for future Components.

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
| [`metadata.schema.yaml`](metadata.schema.yaml) | Frontmatter, directory boundary, required model files, and retrieval fields |
| [`manifest.schema.yaml`](manifest.schema.yaml) | Model identity, pinned revisions, mode-specific interfaces, execution-state pointer, and document map |
| [`sources.schema.yaml`](sources.schema.yaml) | Stable source identities, revisions, locators, and local integrity fields |
| [`naming-conventions.md`](naming-conventions.md) | Stable paths, IDs, model names, versions, and terminology |
| [`style-guide.md`](style-guide.md) | Agent-oriented content, provenance grammar, optimization detail, and experiment requirements |
| [`page-template.md`](page-template.md) | Canonical model-topic page template |
| [`foundation-page-template.md`](foundation-page-template.md) | Canonical model-independent concept-page template |
| [`paper-entry-template.md`](paper-entry-template.md) | Representative-paper entry contract |
| [`benchmark-entry-template.md`](benchmark-entry-template.md) | Versioned Benchmark entry contract and suggested canonical owners |
| [`benchmark.schema.yaml`](benchmark.schema.yaml) | Benchmark identity, version boundary, environment, task, protocol, metric, and document-map fields |

## Update placement

| New information | Canonical destination |
|---|---|
| Model-independent definition, formalism, mechanism family, or evaluation principle | The owning nested page under `foundations/<subpart>/` |
| Foundation source identity or immutable artifact version | `foundations/sources.yaml` |
| Foundation query-to-knowledge association | `foundations/retrieval-index.yaml` |
| One paper's proposed mechanism, assumptions, and reported evidence | `papers/<paper-id>/paper.md` |
| Paper-claim-to-code mapping, executable interfaces, or release mismatch | `papers/<paper-id>/codebase.md` |
| Paper-specific command, environment, artifact, deviation, or execution state | `papers/<paper-id>/reproduction.md` |
| Falsifiable transfer from one paper mechanism to another model | `papers/<paper-id>/optimization-transfer.md` |
| Paper, code commit, checkpoint revision, benchmark, or entry-local artifact identity | `papers/<paper-id>/sources.yaml` |
| Component-specific knowledge or retrieval representation | The owner path declared by that Component; no shared internal layout is required |
| Source identity unique to a Component | An optional `sources.yaml` placed in a directory chosen by that Component |
| Stable model mechanism, interface, or limitation | The owning page under `models/<model-id>/` |
| Model identity, revision, license, or component inventory | `models/<model-id>/manifest.yaml` |
| Model source identity, immutable version, or artifact hash | `models/<model-id>/sources.yaml` |
| Model-local command, failure, fix, output, or run state | `models/<model-id>/reproduction.md` |
| Reusable model intervention and selection rule | `models/<model-id>/optimization-playbook.md` |
| Unresolved model condition that changes a decision | `models/<model-id>/research-queue.md` |
| Benchmark identity, included/excluded version, and protocol boundary | `benchmarks/<benchmark-id>/benchmark.yaml` and `scope-and-versions.md` |
| Benchmark tasks, environment, data, evaluator, metric, result context, or limitation | The owning page under `benchmarks/<benchmark-id>/` |
| Benchmark source identity or immutable artifact version | `benchmarks/<benchmark-id>/sources.yaml` |
| Benchmark execution state or local evaluator result | `benchmarks/<benchmark-id>/reproduction.md` |
| Path, retrieval-metadata, or schema change | `CHANGELOG.md` and the relevant schema file |

A statement is promoted from an experiment record into a canonical topic page only when its scope, conditions, and reusable consequence are explicit. Moving a model observation into Foundations additionally requires model-independent support or an explicitly labeled cross-source synthesis; one implementation alone does not establish a universal principle.
