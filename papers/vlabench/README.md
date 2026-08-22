---
id: world-model-kb.papers.vlabench
title: VLABench Benchmark Knowledge Entry
kind: paper
status: maintained
last_updated: 2026-08-21
owners:
  - AIBuildAI world-model group
---

# VLABench Benchmark Knowledge Entry

## Retrieval metadata

**Relevant queries:** VLABench, language-conditioned manipulation benchmark, OpenMOSS, ICCV 2025, six tracks, in-distribution, cross-category, common sense, semantic instruction, unseen texture, progress score, intention score, primitive fine-tune dataset, Franka MuJoCo dm_control, skill library, leaderboard.

**Knowledge provided:** benchmark identity and versions, the evaluation protocol that current leaderboards use (and the legacy one the paper used), metric definitions as implemented, the official training set, released baselines, evaluator defects, and transfer hypotheses for a policy trained on it.

**Related pages:** [Xiaomi-Robotics-1 model entry](../../models/xiaomi-robotics-1/README.md) owns the policy under study; [ERVLA](../ervla/README.md) owns a CoT method evaluated on VLABench; [evaluation methodology](../../foundations/data-and-evaluation/evaluation-methodology.md) owns comparison principles; [embodied systems](../../foundations/embodied-systems/robotics-and-embodied-ai.md) owns observation/controller interfaces.

## Identity and revision boundary

| Field | Canonical value | Consequence |
|---|---|---|
| Work | *VLABench: A Large-Scale Benchmark for Language-Conditioned Robotics Manipulation with Long-Horizon Reasoning Tasks* (Zhang et al., Fudan; arXiv:2412.18194, 2024-12-24; ICCV 2025) | The paper describes the legacy evaluation; the maintainer states its metric text is outdated [VLAB-PAPER; VLAB-ISSUE-55] |
| Code | `OpenMOSS/VLABench@cf588fe60c0c7282174fe979f5913170cfe69017` (2025-11-11), MIT | The protocol that leaderboards and Xiaomi's numbers use lives in this tree's `configs/evaluation/tracks` [VLAB-CODE] |
| Training set | `VLABench/vlabench_primitive_ft_lerobot_video@9846a2f6…` (5,000 episodes) | The only sanctioned training data for Track-1-based comparisons [VLAB-DATA-LEROBOT] |
| Leaderboard data | `OpenMOSS/Awesome-WAM` leaderboard (Track 1-4 PS average) | A different statistic from the 5-track SR average [VLAB-WAM-LEADERBOARD] |

## Operational model boundary

VLABench is an evaluation harness, not a model: a MuJoCo/dm_control simulator with a 7-DoF Franka Emika Panda and parallel gripper, 100 task categories (60 primitive, 40 composite), 163 object categories / 2,164 items, end-effector control through inverse kinematics, a skill library with motion planners (RRT, SLERP) that generates demonstrations automatically, and two evaluation modes: interactive (policies stepping the simulator) and non-interactive (VLMs emitting skill sequences). [VLAB-PAPER, Sec. 3-4]

| Surface | Inputs | Outputs | Invalid projection |
|---|---|---|---|
| Interactive policy eval | observation dict (4 RGB views, ee_state, instruction) | per-episode success, intention score, progress score | A VLM-QA score |
| Track protocol (6 tracks, 5 public) | fixed episode configs per task | macro-averaged metrics | The paper's legacy seen/unseen categories |
| Data generation | task + scene sampler + skill library | HDF5 trajectories | Human-demonstration statistics |

## Knowledge map

| Question | Canonical page |
|---|---|
| Design, tasks, metrics, baselines, limits | [`paper.md`](paper.md) |
| Evaluator, tracks, configs, data formats, defects | [`codebase.md`](codebase.md) |
| What has been executed locally | [`reproduction.md`](reproduction.md) |
| Interventions a policy can take on this benchmark | [`optimization-transfer.md`](optimization-transfer.md) |
| Identities | [`sources.yaml`](sources.yaml) |

## High-value evidence anchors

- Paper baselines (legacy protocol, 1,600 fine-tuning trajectories): Octo 1.34 % seen / 0.77 % unseen, OpenVLA 11.74 / 7.93, RDT-1B 15.37 / 9.08; composite 0 / 2.66 / 3.34. [VLAB-PAPER, Table 2]
- Current-protocol baselines released by the maintainers (Track 1 SR): pi0 47.0, pi0.5 40.6, pi0-FAST 29.1 (relative chunk) vs 51.2 (delta chunk) - "action representation matters". [VLAB-HF-ORG; VLAB-CODE README]
- Strongest published 5-track result: Xiaomi-Robotics-1 59.1 SR; ERVLA 53.2. [XR1-TR; ERV-PAPER]
- Evaluator defects open at the pinned commit: issues 55, 80, 82, 88. [VLAB-ISSUE-55; VLAB-ISSUE-80; VLAB-ISSUE-82; VLAB-ISSUE-88]

## Sources

Resolve through [`sources.yaml`](sources.yaml); the Xiaomi-Robotics-1 and ERVLA numbers resolve through their own entries.
