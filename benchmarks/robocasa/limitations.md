---
id: world-model-kb.benchmarks.robocasa.limitations
title: Original RoboCasa Validity Limits
kind: benchmark
status: maintained
last_updated: 2026-08-24
owners:
  - AIBuildAI world-model group
---

# Original RoboCasa Validity Limits

## Retrieval metadata

**Relevant queries:** RoboCasa limitation, benchmark validity, composite failure, dexterity, deformable object, bimanual task, data artifact, binary success, simulator gap, version drift, or invalid comparison.

**Knowledge provided:** benchmark scope limits, measurement blind spots, data and protocol confounders, and claims that the available evidence cannot support.

**Related pages:** [Protocol and metrics](protocol-and-metrics.md) owns evaluation tuples; [datasets](datasets.md) owns trajectory limitations; [scope and versions](scope-and-versions.md) prevents RoboCasa365 leakage. Model-specific failures belong to the relevant [Model entry](../../models/README.md).

## Task and environment coverage

Original RoboCasa focuses on kitchens and rigid-object mobile manipulation. The task suite omits rich deformable manipulation, highly dexterous hand use, and bimanual behavior. The paper also identifies navigation as unsupported by its MimicGen pipeline. Success on the 24 atomic manipulation tasks therefore does not establish general household competence, mobile navigation quality, deformable-object reasoning, or dual-arm coordination. [RC24-PAPER-V1, pp.6, 9]

The 120 scenes are combinations of 10 designed layouts and 12 styles rather than 120 independently sourced physical homes. Texture randomization expands appearance but not necessarily geometry, appliance dynamics, or contact diversity. “Scene count” should not be used as a proxy for independent environmental support without reporting the layout/style composition.

## Task-generation limits

LLMs proposed activity labels and blueprints, but humans filtered logical flaws and implemented task code. The release does not demonstrate fully automatic task synthesis or reward correctness. Some composite tasks are scene-restricted, and the five evaluated composite tasks remain near zero to 12% success. Atomic-task averages do not measure robust multi-stage planning or stage-transition memory. [RC24-PAPER-V1, pp.5-8]

## Dataset limits

MimicGen retains trajectories that satisfy a terminal success predicate. The paper reports jerky motion and collisions among successful trajectories, so accepted does not equal safe, smooth, efficient, or imitation-friendly. Generated data is conditioned on source demonstrations, known subtask structure, simulator state, and task-specific acceptance. It can amplify success-conditioned coverage bias and does not prove open-ended behavioral diversity. [RC24-PAPER-V1, pp.5-6, 9; MIMICGEN-PAPER-V1, pp.3-8, 42]

The paper and fixed release documentation differ in how broadly they describe composite demonstration availability. Dataset claims must be resolved through an actual registry and downloaded artifact, not the headline “100 tasks” or “100K+ trajectories.”

## Metric blind spots

Binary `_check_success()` ignores time-to-completion, collisions, near misses, smoothness, force, controller saturation, path efficiency, stage progress, and recovery behavior. Longer horizons can raise success by allowing more attempts while degrading efficiency. Action chunks can reduce compute but increase open-loop error. Two policies with identical success can therefore differ materially in deployability.

Aggregate success conceals skill and task heterogeneity. The original paper reports doors and drawers as much easier than diverse pick-and-place and insertion. An intervention that improves easy articulation tasks can raise the mean while harming precise manipulation. Per-task, per-skill, per-scene, per-style, and per-object slices are required for diagnosis.

## Protocol and implementation limits

- The original paper does not publish one immutable scenario manifest and seed set for every experiment.
- The `v0.2` README depends on mutable robosuite `master`; assets are downloaded outside the Git commit.
- Official policy learning is delegated to a mutable robomimic branch.
- Current project docs can describe RoboCasa365 under the same domain and repository.
- Later WAM papers use their own cameras, action conversions, horizons, task aliases, training data, and rollout counts.
- Reported baseline tables can mix copied and reproduced numbers under non-identical pretraining conditions.

[RC24-CODE-V02; RC24-EVAL-DOC-V02; XWAM-PAPER-V2, pp.7, 17]

## Simulation-to-real limits

The real-transfer experiment changes controller implementation, control frequency, camera calibration, lighting, and base placement. Co-training improves the reported means, but absolute success remains low and unseen-object uncertainty is high. The result supports a scoped data-transfer hypothesis; it does not establish zero-shot sim-to-real deployment or physical safety. [RC24-PAPER-V1, pp.8-9]

## Unsupported claims

The current evidence does not support any of the following without additional protocol-specific experiments:

- a RoboCasa365 result is directly comparable to Original RoboCasa;
- 24-task success predicts 75-task composite competence;
- visual fidelity or depth quality guarantees closed-loop success;
- generated-data scale alone caused every performance gain;
- one aggregate success value identifies the failing model mechanism;
- source inspection or successful environment import reproduces a policy result;
- a checkpoint compatible with one RoboCasa adapter is compatible with another action or controller convention.

These limits constrain inference from evidence; they do not select or schedule AIBuildAI work.

## Sources

Primary limits use `RC24-PAPER-V1`, `RC24-CODE-V02`, and `RC24-EVAL-DOC-V02`. Cross-model protocol evidence uses `XWAM-PAPER-V2`; data-generation assumptions use `MIMICGEN-PAPER-V1`.
