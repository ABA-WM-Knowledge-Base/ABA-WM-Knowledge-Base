---
id: world-model-kb.benchmarks.robocasa.reproduction
title: Original RoboCasa Reproduction State
kind: record
status: maintained
last_updated: 2026-08-24
owners:
  - AIBuildAI world-model group
---

# Original RoboCasa Reproduction State

## Retrieval metadata

**Relevant queries:** RoboCasa reproduction status, installation, environment smoke test, dataset download, policy rollout, local result, failure, hardware, command, or artifact.

**Knowledge provided:** a claim-level execution-state registry, the documented reproduction contract, and the evidence required to promote simulator, dataset, or policy-evaluation claims to locally observed status.

**Related pages:** [Codebase](codebase.md) maps executable surfaces; [protocol and metrics](protocol-and-metrics.md) defines valid rollouts; [scope and versions](scope-and-versions.md) fixes the release. This page owns execution state only, not stable benchmark semantics.

## Execution-state registry

| Claim | Fixed identity | Current state | Evidence retained | Promotion condition |
|---|---|---|---|---|
| Source can be resolved and inspected | RoboCasa `v0.2`, `756598a5...` | Source-inspected | Commit, tree, setup metadata, docs, task and evaluator symbols | Already satisfied as source inspection; not an execution claim |
| Package imports in a compatible environment | Same code plus resolved robosuite/assets | Not attempted | None | Environment lock, install log, successful `import robocasa`, resolved asset hashes |
| Kitchen and task reset/step works | Named task, scene, seed, robot/controller | Not attempted | None | Non-empty observation, deterministic reset evidence, stepped rollout, saved video/log |
| Dataset downloader resolves original artifacts | Named dataset types and tasks | Not attempted | None | URL/version, byte count, file hashes, episode counts, task distribution |
| Task success evaluator fires correctly | Named task and scenario | Not attempted | None | Positive and negative controlled states or trajectories with expected `_check_success()` values |
| Published BC-Transformer result is reproduced | Paper protocol and paper-era policy implementation | Not attempted | None | Fixed policy code/checkpoint or complete retraining, exact protocol, raw 24×50 outcomes |
| X-WAM 79.2% result is reproduced | X-WAM HF revision and 24×100 protocol | Not attempted | None | Successful model load, 2,400 rollout records, task summaries, aggregate and environment hashes |

Repository and PDF inspection do not count as simulator or policy execution. No local benchmark result is asserted by this entry.

## Simulator smoke-test contract

A minimal execution record retains operating system, Python, compiler, MuJoCo, robosuite and RoboCasa commits, package lock, GPU/renderer, downloaded asset archive identity, macro configuration, and the exact command. The observation artifact should record keys, shapes, dtypes, camera names, action dimension, control frequency, task language, layout/style IDs, object instances, seed, reset time, step throughput, and a short video.

The fixed documentation suggests Python 3.10, editable installation, `download_kitchen_assets.py`, `setup_macros.py`, and module entrypoints such as `python -m robocasa.demos.demo_tasks`. These are source-documented references, not commands observed in this workspace. [RC24-CODE-V02, `README.md`]

## Evaluator unit-test contract

For one atomic task, a robust evaluator check contains at least:

1. a reset state known to be unsuccessful;
2. a successful demonstration replay or deliberately constructed terminal state;
3. one near-success state violating exactly one predicate;
4. `_check_success()` outputs and the underlying object/fixture state values;
5. task horizon and early-termination behavior;
6. repeated resets under the same and different seeds.

This distinguishes an environment that renders from an evaluator that measures the intended behavior. It also catches task alias, object-placement, and state-threshold drift.

## Policy-evaluation artifact contract

One closed-loop record preserves:

```text
benchmark release + dependency commits
task list and ordered aliases
scene/style/object scenario manifest
robot, controller, cameras, preprocessing, action transform
checkpoint and normalization revisions
horizon, chunking, termination, seeds, rollout count
per-step action and success state
per-rollout binary outcome and failure label
per-task success with uncertainty and final aggregation
logs, videos, resolved config, and artifact hashes
```

A comparison should reuse paired scenarios and seeds where implementation permits. The baseline and intervention must keep the entire tuple fixed except for the declared model change. If a dependency or asset identity cannot be recovered, the run remains a documented approximation rather than an exact paper reproduction.

## Known setup risks before execution

The fixed package pins NumPy `1.23.3` and Numba `0.56.4`; those older dependencies constrain compatible Python versions and can conflict with modern ML environments. The README's mutable robosuite `master` dependency is another source of import or API drift. X-WAM avoids one ambiguity by pinning RoboCasa and robosuite as submodules, but its checkpoint and base Wan weights require substantial storage and GPU memory. None of these expected risks is recorded as a locally observed failure until an execution log exists. [RC24-CODE-V02; XWAM-CODE-72CF, `.gitmodules`]

## Sources

Documented setup and evaluation surfaces use `RC24-CODE-V02`, `RC24-EVAL-DOC-V02`, and `RC24-ROBOMIMIC-BRANCH` from [`sources.yaml`](sources.yaml). X-WAM execution identity is owned by the [model reproduction page](../../models/x-wam/reproduction.md).
