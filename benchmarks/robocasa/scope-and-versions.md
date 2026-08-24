---
id: world-model-kb.benchmarks.robocasa.scope-and-versions
title: Original RoboCasa Scope and Version Boundaries
kind: benchmark
status: maintained
last_updated: 2026-08-24
owners:
  - AIBuildAI world-model group
---

# Original RoboCasa Scope and Version Boundaries

## Retrieval metadata

**Relevant queries:** Original RoboCasa, RoboCasa RSS 2024, RoboCasa v0.2, RoboCasa365, simulator revision, task count, scene count, asset count, benchmark migration, or result comparability.

**Knowledge provided:** the canonical Original RoboCasa identity, the fixed code and paper revisions, the successor boundary, and a protocol-identity key for preventing cross-version contamination.

**Related pages:** [Tasks and environments](tasks-and-environments.md) owns the included task and simulator distributions; [protocol and metrics](protocol-and-metrics.md) owns evaluation tuples; [codebase](codebase.md) maps the fixed release to implementation. [RoboCasa benchmark index](README.md) provides the document map.

## Canonical identity

This entry represents the benchmark and simulation system introduced by *RoboCasa: Large-Scale Simulation of Everyday Tasks for Generalist Robots* at RSS 2024. The paper identity is `arXiv:2406.02523v1`; the code identity is official tag `v0.2`, commit `756598a5be52e052339bb2d957426e39015c2afb`, package version `0.2.0`. The release labels itself “Original RoboCasa.” [RC24-PAPER-V1, pp.1-16; RC24-CODE-V02, `setup.py`; RC24-RELEASE-V02]

The benchmark family name alone is not an evaluation identity. A result requires at least:

```text
(RoboCasa release, task subset, environment distribution,
 object split, robot/controller, cameras, action convention,
 dataset/checkpoint, horizon, rollout sampling, success evaluator,
 aggregation rule)
```

Changing one field can produce a different evaluation even when the reported label remains “RoboCasa.”

## Included and excluded lineages

| Dimension | Original RoboCasa in this entry | RoboCasa365 successor, excluded here |
|---|---|---|
| Canonical release | RSS 2024 paper; code `v0.2` | ICLR 2026 system; code `v1.0+` |
| Kitchen scenes | 10 layouts × 12 styles = 120 scenes | 2,500 pretraining scenes plus held-out target scenes |
| Tasks | 25 atomic + 75 composite = 100 | 365 tasks with a different benchmark organization |
| Objects | 2,509 assets over 153 categories | Expanded object and asset distributions |
| Demonstration surface | Original human and MimicGen releases | Larger human and automated pretraining/target datasets |
| Evaluation | Paper-defined atomic, composite, and real-transfer studies; later works often select the 24 manipulation tasks | RoboCasa365 benchmark settings, horizons, splits, and leaderboard |

The `v1.0` release explicitly states that RoboCasa365 builds on the original release and introduces its own tasks, assets, demonstrations, and benchmarking support. Those additions are not retroactive facts about the RSS 2024 benchmark. [RC365-RELEASE-V10]

## Mutable documentation hazard

The project domain and repository default branch now serve the evolving RoboCasa family. Pages mentioning 2,500 scenes, 300 pretraining tasks, target kitchens, a 1.5× horizon update, or the RoboCasa365 leaderboard describe the successor unless a fixed Original RoboCasa revision proves otherwise. The canonical content source for this entry is the `v0.2` tree, not mutable `main` or the current documentation build. [RC24-PROJECT; RC24-CODE-V02; RC365-RELEASE-V10]

The official `v0.2` README records an update dated 31 October 2024 and instructs users to install the `master` branch of robosuite. The RoboCasa code is pinned here, but that dependency instruction is mutable; a reproduction must additionally record the resolved robosuite commit. The release tag does not make its unpinned dependencies immutable. [RC24-CODE-V02, `README.md`]

## Result identity rules

- “100 tasks” identifies the task catalog, not a claim that every reported policy result averages all 100 tasks.
- “100K+ trajectories” combines the paper's human and generated data surfaces; a model may use only the 24-task MimicGen subset or a separately converted dataset.
- The commonly used 24-task policy suite excludes navigation and is a subset of the 25 atomic tasks. It must be named explicitly.
- X-WAM's 24-task, 100-episode evaluation is a later model-specific protocol. It is valid RoboCasa evidence but not identical to the original paper's 50-trial, five-scene atomic experiment.
- A number obtained with RoboCasa365 `v1.0+` must not be placed in an Original RoboCasa comparison table without an explicit cross-version study.

These boundaries preserve causal interpretation: an apparent model improvement can otherwise be caused by task-set, horizon, scene, object, controller, or evaluator drift rather than the intervention.

## Sources

Source identities resolve through [`sources.yaml`](sources.yaml): `RC24-PAPER-V1`, `RC24-CODE-V02`, `RC24-RELEASE-V02`, `RC24-PROJECT`, and `RC365-RELEASE-V10`.
