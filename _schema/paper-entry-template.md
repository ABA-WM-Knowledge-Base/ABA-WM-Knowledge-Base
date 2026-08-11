---
id: world-model-kb.paper-entry-template
title: Representative Paper Entry Template
kind: guide
status: maintained
last_updated: 2026-08-11
owners:
  - AIBuildAI world-model group
---

# Representative Paper Entry Template

A representative-paper entry converts one work into reusable model-improvement knowledge. It is not a prose summary, reading log, or bibliography record.

## Required directory

```text
papers/<paper-id>/
├── README.md
├── paper.md
├── codebase.md
├── reproduction.md
├── optimization-transfer.md
└── sources.yaml
```

## `README.md`: entrypoint and knowledge map

Provide `## Retrieval metadata` with `Relevant queries`, `Knowledge provided`, and `Related pages`. Record paper identity, version, official artifacts, model family, task boundary, and a page map. Do not narrate who read the paper or why it was selected.

## `paper.md`: mechanism and experiments

Reconstruct the work as a decision model:

- formal problem, inputs, outputs, assumptions, and target behavior;
- architecture, representations, data flow, objectives, parameter updates, and inference algorithm;
- data composition, sampling, filtering, supervision, and leakage controls;
- pre-training, adaptation, and evaluation protocols;
- main results with model variant, dataset, metric direction, comparison class, and compute conditions;
- ablations that isolate causal components, including interactions and negative results;
- efficiency, scaling behavior, capability limits, and invalid transfer conditions.

Do not follow the paper section order unless it is the clearest causal order.

## `codebase.md`: implementation graph

Pin the repository revision and map each claimed mechanism to configuration, module, class, function, tensor contract, checkpoint field, and call chain. Record documentation/code mismatches and distinguish released implementation from paper-only description.

## `reproduction.md`: execution records

Use one immutable record per run or logically atomic run group. Each record includes:

- experiment ID, timestamp, code and model revisions;
- hardware, operating system, driver, CUDA, framework, and dependency lock;
- dataset identity and preprocessing hash;
- exact command and resolved configuration;
- baseline, intervention, controlled variables, seed set or rollout count;
- raw and aggregated metrics, output artifacts, and log locations;
- failures, root cause, minimal fix, patch identity, and remaining deviation;
- acceptance or rejection against a predeclared criterion.

Execution status is tracked separately for inference, evaluation, and training.

## `optimization-transfer.md`: transferable interventions

For each proposed transfer, state the source mechanism, target behavior, target-model attachment point, required data or objective change, expected metric movement, assumptions, compute cost, regression risk, minimum controlled experiment, and falsification result. Label analogy-based proposals as hypotheses; a similar name or architecture is not sufficient transfer support.

## `sources.yaml`: resolvable provenance

Pin the paper version, official code commit, checkpoint revision, dataset version, license, benchmark protocol, and local artifacts. Every source ID used in prose must resolve here, and mutable sources must include an access date.

Use the [canonical page template](page-template.md) and [style guide](style-guide.md) for every Markdown page.
