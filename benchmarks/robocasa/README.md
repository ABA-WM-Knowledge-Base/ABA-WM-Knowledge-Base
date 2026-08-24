---
id: world-model-kb.benchmarks.robocasa
title: Original RoboCasa Benchmark Entry
kind: benchmark
status: maintained
last_updated: 2026-08-24
owners:
  - AIBuildAI world-model group
---

# Original RoboCasa Benchmark Entry

## Retrieval metadata

**Relevant queries:** RoboCasa benchmark, Original RoboCasa, RSS 2024, v0.2, household task, kitchen simulator, task suite, demonstration data, success evaluator, rollout protocol, baseline, reproduction, optimization slice, or RoboCasa365 distinction.

**Knowledge provided:** the fixed benchmark identity; tasks, scenes, objects, embodiment and interfaces; original datasets; protocol-bound baselines; evaluator and implementation surfaces; execution state; limitations; and benchmark-side diagnostics for model improvement.

**Related pages:** [Scope and versions](scope-and-versions.md) owns the Original-versus-RoboCasa365 boundary; [X-WAM evaluation](../../models/x-wam/evaluation.md) owns one later model-specific result; [robotics and embodied AI](../../foundations/embodied-systems/robotics-and-embodied-ai.md) owns general embodiment principles. [`retrieval-index.yaml`](retrieval-index.yaml) exposes advisory query associations.

## Canonical identity

This entry covers **Original RoboCasa**, introduced at RSS 2024 and represented by `robocasa/robocasa` tag `v0.2`, commit `756598a5be52e052339bb2d957426e39015c2afb`, package version `0.2.0`. It includes the original 120 kitchen scenes, 25 atomic and 75 composite task definitions, 2,509 object assets across 153 categories, demonstration-generation and dataset surfaces, and paper-era evaluation evidence. [RC24-PAPER-V1; RC24-CODE-V02; RC24-RELEASE-V02]

RoboCasa365 is a successor and is not represented by this entry. Its `v1.0+` scenes, tasks, datasets, horizons, target splits, evaluator, and leaderboard must not be substituted into an Original RoboCasa protocol while retaining the same benchmark label. [RC365-RELEASE-V10]

## Result identity

A RoboCasa result is identified by more than the benchmark name:

```text
release and dependency revisions
  + task subset and task aliases
  + layout/style/object scenario distribution
  + robot, controller, cameras, observation history
  + action representation, frequency, horizon, and replanning
  + dataset/checkpoint and preprocessing
  + rollout count, seeds, timeout, success predicate, aggregation
```

The original paper's main atomic-policy experiment uses 24 manipulation tasks, 50 trials per task, five fixed scenes, unseen object instances, and two styles absent from training. Later X-WAM evaluation also uses 24 tasks but runs 100 episodes per task with its own pinned client, cameras, action chunks, horizons, scenario tuples, and checkpoint. Those numbers belong in distinct protocol rows. [RC24-PAPER-V1, pp.6-7 and 11; XWAM-PAPER-V2; XWAM-CODE-72CF]

## Canonical owners

| Owner | Knowledge |
|---|---|
| [`benchmark.yaml`](benchmark.yaml) | machine-readable identity, release boundary, task counts, primary outcome, and document map |
| [Scope and versions](scope-and-versions.md) | fixed v0.2 identity, successor exclusions, and comparison key |
| [Tasks and environments](tasks-and-environments.md) | scenes, assets, task taxonomy, embodiment, observations, actions, and success predicates |
| [Datasets](datasets.md) | human, MimicGen, AI-object, released-data, transformation, and license boundaries |
| [Protocol and metrics](protocol-and-metrics.md) | rollout units, scenario sampling, horizons, evaluator, aggregation, and comparison requirements |
| [Baselines and results](baselines-and-results.md) | original policy/data-scaling evidence, composite and real transfer, and later protocol-bound WAM rows |
| [Codebase](codebase.md) | fixed simulator/task/evaluator paths, dependencies, dataset tools, and external policy stack |
| [Reproduction](reproduction.md) | sole benchmark execution-state registry and promotion conditions |
| [Limitations](limitations.md) | simulator, task, dataset, evaluator, version, and transfer validity boundaries |
| [Optimization reference](optimization-reference.md) | failure slices, benchmark-side controlled variables, diagnostic measures, and falsification conditions |
| [`sources.yaml`](sources.yaml) | immutable paper, code, release, documentation, and dependency identities |

## Ownership boundary with other parts

This Benchmark entry owns what is being measured and under which environment/protocol. A [Paper entry](../../papers/README.md) owns how a particular work used RoboCasa and what it reported. A [Model entry](../../models/README.md) owns the evaluated checkpoint, preprocessing, adapter, inference configuration, and model-specific result. [Foundations](../../foundations/README.md) owns reusable principles such as closed-loop validity, uncertainty, action semantics, and comparison design. Components retain any cross-paper synthesis they explicitly declare.

For X-WAM, benchmark tasks and evaluators remain here; the proposed method and reported experiment remain in the [X-WAM Paper entry](../../papers/x-wam/README.md); checkpoint, data conversion, adapter, scheduler, and result interpretation remain in the [X-WAM Model entry](../../models/x-wam/README.md). This prevents the benchmark page from becoming a duplicate model report.

## Evidence boundary

Source and PDF inspection establish document identity and code structure, not simulator execution. A documented installer does not establish a compatible local environment. A successful reset/step does not validate `_check_success()`. A policy response does not establish closed-loop task success. A closed-loop score remains non-comparable when task, scenario, action, horizon, evaluator, or aggregation fields differ materially.

The current execution state is `source-inspected` for code/document structure and `not attempted` for local package import, simulator smoke tests, dataset download, evaluator tests, and policy rollout. The canonical claim-level states and acceptance artifacts are in [Reproduction](reproduction.md).

## Sources

Original RoboCasa identities resolve through [`sources.yaml`](sources.yaml). X-WAM identities are owned by its [Paper](../../papers/x-wam/sources.yaml) and [Model](../../models/x-wam/sources.yaml) registries.
