---
id: world-model-kb.papers.vlabench.paper
title: VLABench Design, Protocol, Metrics, and Evidence
kind: paper
status: maintained
last_updated: 2026-08-21
owners:
  - AIBuildAI world-model group
---

# VLABench Design, Protocol, Metrics, and Evidence

## Retrieval metadata

**Relevant queries:** VLABench tasks, 100 categories, primitive composite, 2,164 objects, skill library, RRT SLERP, progress score formula, alpha 0.2, intention score threshold, success predicate, track protocol, 50 episodes per task, legacy seen unseen protocol, baseline results, VLM evaluation, skill recall.

**Knowledge provided:** what the benchmark measures and how, both the paper's legacy protocol and the track protocol leaderboards use now, metric definitions as written and as implemented, the training set's provenance, baseline evidence, and the limits of comparing across protocols.

**Related pages:** [`README.md`](README.md) owns identity; [`codebase.md`](codebase.md) owns the implementation; [evaluation methodology](../../foundations/data-and-evaluation/evaluation-methodology.md) owns protocol principles; [Xiaomi-Robotics-1 evaluation](../../models/xiaomi-robotics-1/evaluation.md) owns the strongest current result.

## 1. Problem statement

Existing manipulation benchmarks under-test what language-conditioned VLA policies need: world knowledge and commonsense transfer, natural-language instructions with implicit intent (not templates), long-horizon multi-step reasoning, and joint evaluation of action policies and language models. VLABench provides 100 task categories with strong in-category randomization over 2,000+ objects, and an automated data-generation framework. [VLAB-PAPER, Abstract, Sec. 1]

## 2. Benchmark construction

### 2.1 Simulator and robot

MuJoCo with dm_control; a 7-DoF Franka Emika Panda with a parallel gripper; targets are end-effector positions (3D) and orientations (quaternions) solved to joints by inverse kinematics; 10 Hz control; multi-view RGB-D, segmentation, and point clouds are available; four views are used for VLM evaluation. [VLAB-PAPER, Sec. 3]

### 2.2 Tasks and assets

100 categories: 60 primitive (average ~120 timesteps) and 40 composite (average > 500 timesteps); 163 object categories, 2,164 items. Primitive tasks are organized along five evaluation dimensions: mesh & texture understanding, spatial understanding, common sense & world knowledge, semantic understanding, physical-law understanding. [VLAB-PAPER, Sec. 3]

### 2.3 Automatic demonstration generation

A skill library with task-specific motion planners: RRT for paths, SLERP for orientation interpolation, prior information (environment point clouds, grasp points, target entities), rejection sampling and failure-triggered early termination. Demonstrations are therefore scripted and clean rather than human; the maintainers later report that many tasks' generators fail or stop early (issues 73, 87). [VLAB-PAPER, Sec. 4; VLAB-CODE]

## 3. Metrics

### 3.1 As written (paper)

Progress Score `PS = alpha * (n_correct / N) + (1 - alpha) * (m_done / M)` with `alpha = 0.2`: N target objects/receptacles, `n_correct` correctly selected, M substeps, `m_done` completed. Correct target identification contributes 20 % of the score, task success the full score. Success is the binary task predicate. [VLAB-PAPER, Sec. 5]

### 3.2 As implemented (authoritative per the maintainer)

`Evaluator.evaluate_single_episode` records `success` (the environment signals `timestep.last()`), `intention_score = env.get_intention_score(threshold=0.1)` (did the gripper approach the correct object), and `progress_score = env.get_task_progress()` (task-specific stage conditions plus a grasp term). The maintainer states the paper's PS definition is outdated and the code is the reference. Known defects at the pinned commit: IS can be 0 on a successful episode; the gripper "open" predicate has inverted polarity; a null action can still move the arm through the IK controller. [VLAB-CODE, `evaluation/evaluator/base.py`; VLAB-ISSUE-55; VLAB-ISSUE-82; VLAB-ISSUE-88; VLAB-ISSUE-80]

## 4. Evaluation protocols

### 4.1 Legacy protocol (the paper)

Policies fine-tuned on 100 trajectories per task category (1,600 total) and evaluated on seen/unseen object splits, base/commonsense categories, semantic instructions, unseen tasks, and composite tasks; results reported as success percentages. [VLAB-PAPER, Sec. 6, Table 2]

### 4.2 Track protocol (the code; 2025-03 onward)

Six tracks of fixed episode configurations under `configs/evaluation/tracks/`: (1) in-distribution, (2) cross-category (object category and instance generalization), (3) common sense, (4) semantic instruction, (5) cross-task (open, user-defined, not in the standard average), (6) unseen texture (backgrounds and table textures). 10 tasks per public track, 50 configs each (Track 2 `insert_flower`: 10). Training data: the primitive fine-tune set, 10 tasks x 500 episodes. Reported numbers are macro averages over tasks per track; the 5-track SR average is Xiaomi's headline; Awesome-WAM uses the Track 1-4 PS average. [VLAB-CODE README; VLAB-WAM-LEADERBOARD]

### 4.3 VLM / workflow evaluation (non-interactive)

VLMs output skill sequences in a DSL; metrics are skill recall, parameter recall, skill-and-parameter-pair recall, plus a precise-matching rate; supported models include GPT-4V, Qwen2-VL, InternVL2, MiniCPM-V2.6, GLM-4V, LLaVA-NeXT. Not used for policy comparison. [VLAB-PAPER, Sec. 5; VLAB-CODE]

## 5. Baseline evidence

| Protocol | Model | Result |
|---|---|---|
| legacy | Octo | 1.34 % seen / 0.77 % unseen; composite 0 % |
| legacy | OpenVLA | 11.74 / 7.93; composite 2.66 % |
| legacy | RDT-1B | 15.37 / 9.08; composite 3.34 % |
| track, Track 1 SR | pi0 (10-task fine-tune) | 47.0 |
| track, Track 1 SR | pi0.5 | 40.6 |
| track, Track 1 SR | pi0-FAST relative chunk / delta chunk | 29.1 / 51.2 |
| track, 5-track SR | pi0-FAST / pi0.5 / ERVLA / Xiaomi-Robotics-1 | 39.8 / 48.1 / 53.2 / 59.1 |

[VLAB-PAPER, Table 2; VLAB-CODE README; VLAB-HF-ORG; ERV-PAPER; XR1-TR]

## 6. Limits stated by the authors and observed

The authors conclude that current VLAs perform poorly even on primitive pick-and-place tasks and that foundation-model workflows suffer from limited closed-loop feedback on physical-reasoning tasks. Observed since: the two protocols are not comparable; the evaluator has open correctness issues; the infrastructure release ("complete infra framework ... a new leaderboard") is still announced as forthcoming. [VLAB-PAPER, Sec. 7; VLAB-CODE README]

## Sources

[VLAB-PAPER] Abstract, Sec. 3-7, Table 2; [VLAB-CODE] README, `evaluation/evaluator/base.py`, `configs/evaluation/tracks/`; [VLAB-HF-ORG]; [VLAB-WAM-LEADERBOARD]; [VLAB-ISSUE-55]; [VLAB-ISSUE-80]; [VLAB-ISSUE-82]; [VLAB-ISSUE-88]; [ERV-PAPER]; [XR1-TR].
