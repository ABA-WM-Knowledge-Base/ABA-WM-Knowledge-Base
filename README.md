---
id: world-model-kb.home
title: World Model Knowledge Base
kind: index
status: maintained
last_updated: 2026-08-19
owners:
  - AIBuildAI world-model group
---

# World Model Knowledge Base

This repository is a structured knowledge and evidence layer for world-model research. It contains reusable World Model Foundations, thirteen representative-paper entries, two cross-paper Components, and an active NVIDIA Cosmos3-Nano model entry. The content connects general formalisms, representation and learning choices, capability evolution, paper mechanisms and ablations, model interfaces, evaluation conditions, source code, execution records, and candidate optimization experiments.

## Authority boundary

The KB is a knowledge-guidance layer. It is intended to shape Agent understanding, judgment, and strategy selection, while leaving workflow orchestration to AIBuildAI.

- AIBuildAI runtime instructions, Agent configuration, task instructions, permissions, and policies remain authoritative.
- The KB provides model facts, high-level knowledge instructions, strategies, best practices, diagnostic frameworks, and experiment-quality criteria.
- AIBuildAI may dynamically retrieve this knowledge to ground design and implementation decisions.
- Retrieval profiles support that dynamic loading but are not mandatory workflow routes.
- The KB does not decide which Agent to call, which solution repository to advance or abandon, task order, execution scheduling, permissions, approvals, or external actions.
- Scientific caveats describe what evidence supports a claim; they are not Agent-control rules.

## Architecture

```mermaid
flowchart TD
    O["AIBuildAI workflow orchestration"] --> T["Current task and state"]
    T --> R["AIBuildAI dynamic knowledge retrieval"]
    R --> I["INDEX.md: non-exclusive knowledge map"]

    I --> F["Foundations"]
    I --> P["Papers"]
    I --> X["Components"]
    I --> M["Models"]

    F --> F1["Definitions and problem formulations"]
    F --> F2["Representations and learning objectives"]
    F --> F3["Decision-making and embodied systems"]
    F --> F4["Data, evaluation, and research frontiers"]

    P --> PE["Representative-paper mechanisms, experiments, code, and transfer evidence"]
    X --> XR["Reasoning evolution and evidence"]
    X --> XG["Generative-modeling evolution and evidence"]
    M --> C["Cosmos3-Nano model knowledge and execution evidence"]

    F1 --> S["Task-relevant knowledge synthesis"]
    F2 --> S
    F3 --> S
    F4 --> S
    PE --> S
    XR --> S
    XG --> S
    C --> S

    S --> D["Ground Agent reasoning, diagnosis, and strategy selection"]
    D -.->|informs without controlling| O
```

The four content parts are peer, non-exclusive knowledge inputs. Retrieval can combine relevant Foundation concepts, paper evidence, cross-paper Component syntheses, and model-specific facts; it does not have to enter through Cosmos3-Nano, a Component, or a paper. All four parts are active.

The repository separates five concerns:

1. **Discovery:** indexes describe which documents may be relevant.
2. **Canonical knowledge:** one page owns each reusable topic.
3. **Provenance:** source IDs resolve to pinned papers, code revisions, model revisions, or local artifacts.
4. **Execution evidence:** reproduction records distinguish documented capability from an observed run.
5. **Experiment design:** optimization references connect failures, mechanisms, variables, measurements, and confounders without scheduling work.

## Top-level structure

```text
world_model_kb/
|-- README.md                         # Repository guide
|-- INDEX.md                          # Global topic map
|-- CHANGELOG.md                      # Schema, path, and ownership history
|-- _schema/                          # Content and metadata contracts
|-- foundations/                      # Part I: model-independent knowledge
|-- papers/                           # Part II: paper-specific knowledge
|-- components/                       # Cross-paper capability evolution
|-- models/                           # Part III: model-specific knowledge
`-- tools/                            # Structural validation
```

The four content parts are peers:

| Part | Scope | Current content |
|---|---|---|
| [Foundations](foundations/README.md) | Model-independent concepts, formalisms, representations, objectives, control, embodiment, data, and evaluation | Active; eight semantic subparts |
| [Papers](papers/README.md) | Paper-specific mechanisms, implementations, experiments, and transfer hypotheses | Thirteen active entries |
| [Components](components/README.md) | Cross-paper capability evolution, recurring intervention patterns, and unresolved component gaps | Reasoning and Generative Modeling are active |
| [Models](models/README.md) | Model-specific architecture, interfaces, learning, evaluation, code, and execution evidence | Cosmos3-Nano is active |

## How to navigate

Start from [`INDEX.md`](INDEX.md) for the global topic map. AIBuildAI may dynamically combine model-independent Foundations, Paper-specific evidence, cross-paper Components, and Model-specific knowledge rather than assigning a task to exactly one part. The Foundation [`retrieval-index.yaml`](foundations/retrieval-index.yaml), Component page metadata, and Cosmos3-Nano [`agent-index.yaml`](models/cosmos3-nano/agent-index.yaml) expose advisory query-to-knowledge associations without taking workflow authority.

Within a topic page, `Retrieval metadata` identifies related questions and pages. Stable source IDs resolve through the nearest owning source registry, such as Foundation [`sources.yaml`](foundations/sources.yaml), a Paper entry's registry such as IRASim [`sources.yaml`](papers/irasim/sources.yaml), a Component registry such as Reasoning [`sources.yaml`](components/reasoning/sources.yaml), or Cosmos3-Nano [`sources.yaml`](models/cosmos3-nano/sources.yaml). Observed execution evidence remains in the relevant entry's `reproduction.md`. The `_schema/` directory defines how KB content is represented; it does not define AIBuildAI workflow orchestration.

## Validation

[`tools/validate_kb.py`](tools/validate_kb.py) checks UTF-8 and English content, metadata, links, source references, artifact hashes, required Foundation, Paper, Component, and Model files, and both knowledge-guidance retrieval indexes.

Run from the repository root:

```bash
python tools/validate_kb.py
```

## Important evidence distinctions

- A public checkpoint does not establish complete training reproducibility.
- A documented command does not establish that it ran successfully in a local environment.
- A hosted model ID does not reveal its deployed checkpoint SHA unless the service publishes it.
- A Reasoner text plan is not a robot action tensor.
- A realistic video is not automatically a physically correct future.
- A benchmark score is meaningful only with its checkpoint, task mode, protocol, evaluator, and inference budget.
- An unresolved hypothesis is not a model fact.

These statements define the scope of evidence in the KB. They do not constrain how AIBuildAI organizes or executes work.
