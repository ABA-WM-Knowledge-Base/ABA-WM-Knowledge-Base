---
id: world-model-kb.models.xiaomi-robotics-1.optimization-playbook
title: Xiaomi-Robotics-1 Optimization Design Reference for VLABench
kind: guide
status: maintained
last_updated: 2026-08-21
owners:
  - AIBuildAI world-model group
---

# Xiaomi-Robotics-1 Optimization Design Reference for VLABench

## Retrieval metadata

**Relevant queries:** optimization hypothesis, failure diagnosis, which track, generalization intervention, CoT, data augmentation, inference-time lever, controlled comparison, paired episodes, experiment artifact, what to try first.

**Knowledge provided:** optional experiment-design patterns connecting VLABench failure signatures to mechanisms, controllable variables on this model, measurements, confounders, and evidence quality. This page does not prescribe AIBuildAI task planning or execution.

**Related pages:** [Reproduction](reproduction.md) contains execution state; [Evaluation](evaluation.md) contains protocol and numbers; [Limitations](limitations.md) contains guardrails; [ERVLA transfer](../../papers/ervla/optimization-transfer.md), [VLABench transfer](../../papers/vlabench/optimization-transfer.md), and [Xiaomi-Robotics-1 transfer](../../papers/xiaomi-robotics-1/optimization-transfer.md) hold the paper-derived interventions; [evaluation methodology](../../foundations/data-and-evaluation/evaluation-methodology.md) owns comparison validity.

## Experiment description model

```text
target track(s) -> observed failure signature (from per-episode records)
  -> candidate mechanism -> controllable surface on XR-1
  -> minimum discriminating intervention -> paired-episode metric and regressions
  -> artifact bundle -> interpretation against the noise band
```

The anchor is the released checkpoint's own L2 on the same configs; every node is a paired comparison against it, not against the paper's 59.1.

## Evidence prerequisites

Checkpoint provenance (import/export records), data-path conventions asserted equal to the client, VLABench commit, client args, `train/token` versus declared batch, s/step, the per-track profile of the anchor.

## Surface selection

| Observed failure (per-episode records) | Diagnose first | Preferred first intervention | Avoid as first response |
|---|---|---|---|
| Track 3/4 low SR, IS low (wrong object approached) | instruction grounding; compare IS across paraphrases | CoT with grounded content (`cot_prob` > 0), instruction paraphrase augmentation | DiT-only fine-tune; more steps on Track-1 data |
| Track 2 low SR, IS high, PS mid (right object, failed grasp on unseen instance) | grasp geometry vs instance shape | visual augmentation, longer training on grasp-heavy tasks, wrist-view emphasis | CoT |
| Track 6 low SR (texture) | texture sensitivity; check train/eval resolution asymmetry | colour/texture augmentation, resolution matching | language-side changes |
| Track 1 regresses while others rise | over-regularization or catastrophic drift from the warm start | lower lr, fewer steps, midpoint checkpoint | more augmentation |
| All tracks drop sharply after fine-tune | convention mismatch (deltas, gripper, state) or stats mismatch | export-and-score an untrained warm start | hyperparameter search |
| Episodes end at step cap with near-zero motion | degenerate chunk scale; stats or mask wrong | inspect decoded chunks against dataset deltas | retraining |
| Majority errors / step 0 | serving chain | fix environment | anything model-side |

## Diagnosis protocol

1. **Localize** each failed episode with one primary label: `grounding` (wrong target, IS 0 with motion), `grasp` (approached, not lifted: PS < 0.5 with IS 1), `placement` (grasped, not placed), `timeout` (slow but on-path), `interface` (error, step 0, drift). Use `detail_info.json` + videos.
2. **Separate interface from capability**: an interface label in > 10 % of episodes invalidates the run for model comparisons.
3. **Stratified baseline**: the anchor's per-(track, task) SR table; compare cells, not only the average.
4. **Rank mechanisms** by the tracks they can move and by cost: inference-time levers (steps, seed ensembling, replan horizon) cost one eval each; data-path levers cost one training; architecture/freezing levers cost a training plus risk to the warm start.

## Lever hierarchy (cheapest first)

1. Inference-time: `num_steps`, seed ensembling, `replan_steps` (1..10), image crop — no training. Protocol note: any of these changes the comparability with the released numbers; report as a separate protocol.
2. Data-path: CoT mixing and content, paraphrases, visual augmentation, per-task weighting, wrapped-Euler stats.
3. Optimization: lr, steps, batch, midpoint checkpoints.
4. Parameter scope: DiT-only, VLM-frozen, vision-frozen.
5. Objective: `freq_coefficient`, choice-loss weights, `cot_coefficient`.

## Metric bundles

Primary: 5-track SR macro average on paired episodes. Always retained: per-track SR/PS/IS, per-task SR, error count, mean `consumed_step` on successes (speed), wall clock, `train/loss_mse`, `train/loss_cot`. Regression guard: Track 1 SR must not drop beyond the noise band.

## Comparison design

- Same 250 configs for every candidate; report the paired difference and the count of episodes that flipped each way.
- Two-candidate decisions inside ~6 pp of average SR are not decisions; extend episodes (the next 5 configs per task) before eliminating.
- Never mix an SR number with a PS leaderboard number.

## Result interpretation patterns

- A gain concentrated in one task of one track is a task fix, not a generalization gain; check whether that task's PS moved.
- Lower IS with higher SR indicates the evaluator's IS defect, not worse grounding.
- A higher Track-1 SR with lower Track-2/6 SR is memorization of the 500-episode set.

## Sources

[XR1-TR] Table 4; [XR1-CODE]; [VLAB-CODE]; [VLAB-ISSUE-82]; [ERV-PAPER] Table 1.
