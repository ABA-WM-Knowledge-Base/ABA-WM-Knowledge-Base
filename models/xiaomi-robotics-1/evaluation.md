---
id: world-model-kb.models.xiaomi-robotics-1.evaluation
title: Xiaomi-Robotics-1 Evaluation Protocols and Reported Results
kind: model
status: maintained
last_updated: 2026-08-21
owners:
  - AIBuildAI world-model group
---

# Xiaomi-Robotics-1 Evaluation Protocols and Reported Results

## Retrieval metadata

**Relevant queries:** VLABench results, 59.1, per-track SR PS IS, in-distribution 75.6, cross-category 53.0, common-sense 48.4, semantic instruction 55.8, unseen texture 62.6, RoboCasa 74.5, RoboCasa365 57.4, RoboDojo 20.07, leaderboard, Awesome-WAM, comparison key, noise band.

**Knowledge provided:** checkpoint- and protocol-bound published results, the comparison key that makes a VLABench number interpretable, the two leaderboard statistics in circulation, and the comparison-validity rules.

**Related pages:** [Limitations](limitations.md) owns confounders; [Policy](policy.md) owns the client; [VLABench paper entry](../../papers/vlabench/paper.md) owns the benchmark and metric definitions; [evaluation methodology](../../foundations/data-and-evaluation/evaluation-methodology.md) owns model-independent principles.

## 1. Comparison key and score grammar

```text
checkpoint revision + robot_type + action conventions + VLABench commit
+ track file + episodes per task + client settings (chunk, replan, image size, cot flag, seed)
+ aggregation (macro over tasks, then over tracks) + run date
```

Invariants:

1. The report's VLABench "average" is the 5-track macro mean of per-track task means of SR; PS and IS are averaged the same way. 50 episodes per task per track (2,460 episodes given Track 2 `insert_flower`'s 10 configs). [XR1-TR, Sec. 5.3; XR1-CODE-EVAL-VLABENCH]
2. Awesome-WAM's VLABench `overall_score` is the Track 1-4 **progress-score** average; entries from the original paper (pre-track protocol), cherry-picked task subsets, and VLM-QA uses are flagged non-standard there. XR-1 is not listed in the 2026-05-16 snapshot; its Track 1-4 PS average is 69.2. [VLAB-WAM-LEADERBOARD]
3. A prefix of the official configs (e.g. the first 5 per task) is an unbiased estimate of the full protocol on identical scenes; a random re-sample is not the same protocol. [VLAB-CODE, `evaluator/base.py`]

## 2. VLABench (Table 4 of the report; released checkpoint)

| Track | SR | PS | IS |
|---|---:|---:|---:|
| In-distribution | 75.6 | 85.0 | 79.8 |
| Cross-category | 53.0 | 66.6 | 66.4 |
| Common-sense | 48.4 | 58.3 | 58.2 |
| Semantic instruction | 55.8 | 66.8 | 70.2 |
| Unseen texture | 62.6 | 74.9 | 74.8 |
| **Average** | **59.1** | **70.3** | **69.9** |

Baselines in the same table (same protocol, Xiaomi's runs): ERVLA 53.2 / 65.9 / 70.4; pi0.5 48.1 / 62.3 / 64.9; pi0-FAST 39.8 / 49.5 / 58.6. [XR1-TR, Table 4; XR1-HF-VLABENCH]

Noise: with p ~ 0.6 the standard error of a 50-episode track-task cell is ~7 pp; of the 2,460-episode average ~1 pp; of a 250-episode prefix ~3 pp.

## 3. Other benchmarks (different checkpoints)

| Benchmark | XR-1 | Second best | Protocol |
|---|---:|---:|---|
| RoboCasa (24 tasks) | 74.5 (card: 74.21 over 2,400) | 72.6 | 300 MG demos per task; 100 episodes per task in the card |
| RoboCasa365 | 57.4 (80.2 atomic, 57.1 composite-seen, 32.1 composite-unseen) | 46.6 | official pre-training split |
| RoboDojo | 20.07 score / 13.93 % SR | 13.07 / 8.80 % | 42+ tasks, five capability axes |

[XR1-TR, Tables 2, 3, 5; XR1-HF-ROBOCASA; XR1-PWC]

## 4. Causal ablation state

The report publishes no ablation table for the choice heads, frequency loss, async prefix, or CoT on VLABench; the only stated ablation-like observation is qualitative (excluding action tokens from DiT attention helped). Attribution of any component's contribution to 59.1 is therefore unsupported. [XR1-TR]

## 5. Known protocol conflicts

- Report text says "2,500 rollouts"; the pinned track file gives Track 2 `insert_flower` 10 configs, so the executable total is 2,460. [XR1-TR; VLAB-CODE]
- Evaluator defects open upstream: IS = 0 on successes, PS formula differs from the paper, null-action drift, gripper-bit polarity. SR is the robust metric. [VLAB-ISSUE-82; VLAB-ISSUE-55; VLAB-ISSUE-80; VLAB-ISSUE-88]
- Xiaomi's eval README pins no VLABench commit; a later VLABench change can move the number.

## 6. Optimization decision framework

Select on the 5-track SR macro average with paired episodes; report PS/IS and per-track SR as context; treat a gain on one track that costs another as neutral until the average moves beyond the noise band; never compare against an Awesome-WAM PS number with an SR number.

## 7. Evaluation-invalidity signals

Majority of episodes erroring or ending at step 0; a chunk length other than 10; a processor whose `action_config` lacks `vlabench_choice`; an unset `VLABENCH_ROOT`; track files edited.

## Sources

[XR1-TR] Tables 2-5, Sec. 5; [XR1-HF-VLABENCH]; [XR1-HF-ROBOCASA]; [XR1-PWC]; [XR1-CODE-EVAL-VLABENCH]; [VLAB-CODE]; [VLAB-WAM-LEADERBOARD]; [VLAB-ISSUE-55]; [VLAB-ISSUE-80]; [VLAB-ISSUE-82]; [VLAB-ISSUE-88].
