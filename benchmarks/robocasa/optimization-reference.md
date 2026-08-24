---
id: world-model-kb.benchmarks.robocasa.optimization-reference
title: RoboCasa-Grounded Model Optimization Reference
kind: benchmark
status: maintained
last_updated: 2026-08-24
owners:
  - AIBuildAI world-model group
---

# RoboCasa-Grounded Model Optimization Reference

## Retrieval metadata

**Relevant queries:** optimize a world model on RoboCasa, failure diagnosis, object generalization, scene generalization, action chunk, temporal context, depth supervision, data curation, long horizon, controlled ablation, or falsification.

**Knowledge provided:** benchmark-grounded diagnostic slices and intervention tests that connect observable failures to model, data, inference, and interface mechanisms without prescribing workflow orchestration.

**Related pages:** [Protocol and metrics](protocol-and-metrics.md) owns controlled comparison fields; [X-WAM optimization playbook](../../models/x-wam/optimization-playbook.md) owns model-specific attachment points; [evaluation methodology](../../foundations/data-and-evaluation/evaluation-methodology.md) owns general experimental validity.

## Diagnostic decomposition

RoboCasa failure is not one scalar phenomenon. The task suite separates at least object perception and grasping, articulated contact, fine insertion, small-control targeting, navigation, and multi-stage transition. Scene, style, object instance, task horizon, and controller variables provide additional orthogonal slices. A useful baseline records each slice before selecting a mechanism hypothesis.

```text
binary failure
  -> task stage and skill family
  -> perception / geometry / action / temporal / controller / evaluator class
  -> observable trace and counterfactual intervention
  -> paired protocol result plus regression slices
```

## Falsifiable intervention map

| Observed slice | Mechanism hypothesis | Controllable surface | Expected signal | Confounder and falsification |
|---|---|---|---|---|
| Unseen-object drop concentrated in pick-and-place | Representation or training data misses category/instance affordance variation | Object-balanced sampling, visual augmentation, representation loss, or synthetic-object mix | Higher unseen-instance success without seen-task regression; better grasp-stage completion | Falsified if oracle object masks/poses do not reduce the gap, suggesting controller or action error |
| Unseen-style drop with stable proprioceptive behavior | Appearance encoding is brittle | Texture/style sampling, image encoder adaptation, view-consistent augmentation | Paired gains on held-out styles with unchanged human-curated scene success | Falsified if geometry/controller traces diverge before visual ambiguity appears |
| Insertion and button tasks fail near the target | Spatial precision or action resolution is insufficient | Depth/geometric supervision, crop resolution, action normalization, denoising steps, closed-loop chunk length | Higher terminal precision, lower end-effector target error, improved insertion/button success | Falsified if ground-truth geometry leaves failure unchanged |
| Long-horizon composite tasks fail after successful primitives | Context does not identify progress or action chunks compound error | History conditioning, stage representation, KV cache, shorter replanning interval, progress auxiliary target | Higher stage-transition completion and composite success at fixed primitive success | Falsified if oracle stage labels and shorter chunks do not improve continuation |
| Doors/drawers succeed but pick-and-place remains low | Easy articulation dominates the aggregate; object diversity and grasping are bottlenecks | Skill-balanced batches, hard-task weighting, grasp-rich data, task-conditioned heads | Pick-and-place and insertion gains with reported macro and per-skill means | Falsified if gains vanish under balanced scenarios or come only from longer horizons |
| Generated-data policy is jerky or collision-prone | Terminal-success acceptance preserves poor motion | Collision/jerk filters, trajectory scoring, stratified acceptance, recovery data | Same or higher success with lower collision, jerk, saturation, and path length | Falsified if filtering reduces coverage and success more than behavior quality improves |
| WAM video looks accurate but actions fail | Shared representation or sampling does not guarantee control alignment | Action loss weight, action/video timestep coupling, action head, policy-only branch, action-conditioned rollout loss | Action error and success improve without hidden horizon changes; video regression remains bounded | Falsified if oracle action decoding from the same latent cannot recover successful control |
| Wrist-view 3D reconstruction is inconsistent | Predicted end-effector pose or calibration, not depth pixels, misaligns views | State loss, hand-eye calibration, multi-view consistency, camera-pose head | Lower point-cloud Chamfer Distance and wrist-pose error with stable static-view metrics | Falsified if ground-truth pose does not repair point-cloud alignment |

## Required control tuple

For each intervention, hold fixed the Original RoboCasa revision, robosuite/assets, ordered task list, scenario manifest, camera and controller contract, checkpoint initialization, training sample budget, horizon, action chunk, seeds, rollout count, success evaluator, and aggregation. When a field must change—such as action chunk—it becomes the declared intervention and all coupled compute or horizon effects must be measured.

Minimum outputs include per-rollout success, per-task and macro success with uncertainty, stage/failure labels, latency, action statistics, and model-specific regression metrics. For a generative WAM, retain video/depth/point-cloud metrics; for a policy-only model, retain calibration and action-distribution diagnostics. Overall success alone cannot determine which mechanism changed.

## X-WAM-specific benchmark leverage

RoboCasa is unusually informative for X-WAM because the same simulator can provide multi-view RGB, depth, proprioception, task success, and 3D reconstruction targets. The model's depth branch, asynchronous action/video denoising, action normalization, and early-stop policy mode can be ablated under one environment. However, the X-WAM paper's depth and ANS ablations omit large-scale pretraining and report 67.8% rather than the final 79.2%; an optimization should not assume their effect sizes transfer unchanged to the released pretrained checkpoint. [XWAM-PAPER-V2, pp.8-9, Table 4]

Candidate interactions requiring explicit tests include depth-branch layer count × policy early-stop, ANS action steps × action chunk length, history length × task horizon, pretraining mixture × object/style split, and action-loss weighting × video fidelity. Interaction studies are preferable to independently tuning coupled variables and attributing the final gain to one.

## Evidence promotion boundary

A benchmark observation becomes reusable optimization knowledge only when the model and protocol identities are complete, the mechanism has a controlled counterfactual, uncertainty and regression slices are retained, and an alternative explanation has a discriminating test. A paper correlation or one unpaired local run remains a hypothesis.

This reference can influence Agent diagnosis and experiment design. It does not decide which Agent runs, which repository advances, or when an experiment executes.

## Sources

Benchmark evidence uses `RC24-PAPER-V1` and `RC24-CODE-V02`. X-WAM mechanisms and ablations use `XWAM-PAPER-V2` and `XWAM-CODE-72CF` from the [X-WAM Paper registry](../../papers/x-wam/sources.yaml).
