---
id: world-model-kb.papers.mimicgen.paper
title: MimicGen Method, System, and Experimental Evidence
kind: paper
status: draft
last_updated: 2026-08-13
owners:
  - AIBuildAI world-model group
---

# MimicGen Method, System, and Experimental Evidence

## Retrieval metadata

**Relevant queries:** MimicGen, demonstration generation, object-centric subtask, segment transform, replay-based imitation, data generation rate, success-only filtering, source demonstration selection, nearest-neighbor segment selection, reset distribution variant, D0 D1 D2, robot transfer, synthetic demonstrations for behavioral cloning.

**Knowledge provided:** the system's formal problem and assumptions, the complete generation pipeline from source demonstrations to filtered datasets, generation and policy-training protocols, the main success-rate evidence with its conditions, the ablations that isolate what matters, and the measured bias and evidence boundaries of success-only acceptance.

**Related pages:** [Data curation and filtering](../../foundations/data-and-evaluation/data-curation-and-filtering.md) owns the general selection-operator account this system instantiates; [datasets and supervision](../../foundations/data-and-evaluation/datasets-and-supervision.md) owns dataset composition principles; [evaluation methodology](../../foundations/data-and-evaluation/evaluation-methodology.md) owns protocol validity; [robotics and embodied AI](../../foundations/embodied-systems/robotics-and-embodied-ai.md) owns embodiment interfaces; [actions and interventions](../../foundations/problem-formulation/actions-and-interventions.md) owns action semantics.

## 1. Problem statement

### 1.1 Motivation and formal setup

Teleoperated demonstration collection is the cost bottleneck of imitation learning: a single-scene, single-object robomimic pick-and-place task needed 200 human demonstrations for 73.3 percent success, and scaling efforts (RT-1) spent nearly 1.5 years of multi-operator collection. Much of such data plausibly repeats similar object-relative motions in different contexts. [MIMICGEN-PAPER-V1, pp.1-2]

Each task is an MDP; a policy pi maps states to actions and is trained by Behavioral Cloning on a demonstration dataset D of state-action trajectories, with initial states drawn from a reset distribution. MimicGen is a data generation system, not a learner: given a small source dataset D_src of human demonstrations on task M, produce a large dataset D on M or on task variants where the reset distribution, the objects, or the robot arm change. A generation attempt samples a start state, adapts a chosen source demonstration into a new trajectory, executes it, and keeps the trace only if task success is achieved. [MIMICGEN-PAPER-V1, pp.2-3]

### 1.2 Assumptions

1. **Delta end-effector pose action space** with a gripper open/close channel, giving an equivalence between demonstration actions and controller target-pose sequences. [MIMICGEN-PAPER-V1, p.3]
2. **Tasks are known sequences of object-centric subtasks** S_1(o_S1) ... S_M(o_SM), each manipulation expressed relative to one object's frame; the sequence is human-specified. [MIMICGEN-PAPER-V1, p.3]
3. **Object poses are observable at the start of each subtask during data generation** (not during policy deployment). [MIMICGEN-PAPER-V1, p.3]

## 2. System and data flow

### 2.1 End-to-end pipeline

```text
source human demos D_src (per task, typically 10)
        |
  parse each trajectory into contiguous object-centric
  subtask segments via automatic subtask-end metrics
        |
========== per generation attempt on a new scene ==========
  sample start state from target variant (D0/D1/D2, O, R)
        |
  for each subtask S_i(o_Si):
        |-- choose reference segment from the N source segments
        |     (random, or nearest-neighbor over object poses nnk=3,
        |      optionally chosen independently per subtask)
        |-- transform segment: preserve controller-pose-to-object-frame
        |     relation under the new object pose
        |     T_C't_W = T_O0_W (T_O'0_W)^-1 T_Ct_W
        |-- prepend linear interpolation from current end-effector
        |     pose to the transformed segment start
        |-- execute as delta-pose actions + source gripper actions
        |
  run task success check on the completed episode
        |
  keep episode only on success; discard otherwise
============================================================
        |
  repeat until 1,000 successes per task variant
        |
  train BC-RNN on the generated dataset
```

The ratio of successful to attempted generations is the data generation rate (DGR). [MIMICGEN-PAPER-V1, pp.3-5]

### 2.2 What the system is not

There is no learned generative model: generation is deterministic replay of transformed source segments plus a noise scale sigma on actions. Acceptance is a per-task binary success predicate applied to whole episodes; there is no cross-task or cross-episode ranking, no quality score, and no curation step beyond the predicate. The pipeline depends only on object frames and controller frames, which is what enables transfer across reset distributions, object instances (given canonical frames), and arms (given a shared end-effector control convention). [MIMICGEN-PAPER-V1, pp.4-5]

For mobile manipulation, segments containing base motion are split into manipulator / base / manipulator sub-segments; base actions are copied verbatim from the reference segment, an acknowledged simplification. [MIMICGEN-PAPER-V1, p.37]

## 3. Generation and training protocol

- **Source data:** 10 human demonstrations per task on the default variant D0 (exceptions: Mobile Kitchen 25; Square reuses the robomimic Square PH set). [MIMICGEN-PAPER-V1, p.5]
- **Volume:** generation proceeds until 1,000 successes per task variant; failed attempts are discarded. 50K+ demonstrations across 18 tasks in robosuite/MuJoCo and Factory/Isaac Gym plus a physical arm, from about 200 source demonstrations total. [MIMICGEN-PAPER-V1, pp.1, 5]
- **Generation hyperparameters:** defaults sigma = 0.05, n_interp = 5, n_fixed = 0, random selection without per-subtask choice; nearest-neighbor (nnk = 3) for Square and Nut Assembly, nearest-neighbor with per-subtask selection for Stack, Stack Three, Pick Place. Real-robot runs use sigma = 0.02 and n_interp = n_fixed = 25 for hardware safety. [MIMICGEN-PAPER-V1, pp.37-38]
- **Policy training:** BC-RNN with robomimic defaults (low-dim learning rate raised to 1e-3); image agents use front + wrist views at 84x84 (real: 120x160) with pixel-shift augmentation; low-dim agents additionally see ground-truth object poses. [MIMICGEN-PAPER-V1, p.39]
- **Evaluation protocol:** 50 rollouts per checkpoint during training; the reported number is the maximum success rate across all evaluated checkpoints, across 3 seeds (real robot: last checkpoint, 50 episodes). This max-over-checkpoints convention inflates absolute numbers and is a known flattering protocol for degrading training curves; comparisons inside the paper share it, cross-paper comparisons must not ignore it. [MIMICGEN-PAPER-V1, p.39]
- **Hardware:** one V100, 8 CPUs, 32 GB per generation or training run. [MIMICGEN-PAPER-V1, p.39]

## 4. Main results

### 4.1 Source vs generated data, image agents, max-over-checkpoints, 3 seeds

| Task | Source (10 demos) | D0 (1000 gen) | D1 | D2 |
|---|---|---|---|---|
| Stack | 26.0 +/- 1.6 | 100.0 +/- 0.0 | 99.3 +/- 0.9 | - |
| Stack Three | 0.7 +/- 0.9 | 92.7 +/- 1.9 | 86.7 +/- 3.4 | - |
| Square | 11.3 +/- 0.9 | 90.7 +/- 1.9 | 73.3 +/- 3.4 | 49.3 +/- 2.5 |
| Threading | 19.3 +/- 3.4 | 98.0 +/- 1.6 | 60.7 +/- 2.5 | 38.0 +/- 3.3 |
| Coffee | 74.0 +/- 4.3 | 100.0 +/- 0.0 | 90.7 +/- 2.5 | 77.3 +/- 0.9 |
| Three Pc. Assembly | 1.3 +/- 0.9 | 82.0 +/- 1.6 | 62.7 +/- 2.5 | 13.3 +/- 3.8 |
| Hammer Cleanup | 59.3 +/- 5.7 | 100.0 +/- 0.0 | 62.7 +/- 4.7 | - |
| Mug Cleanup | 12.7 +/- 2.5 | 80.0 +/- 4.9 | 64.0 +/- 3.3 | - |
| Kitchen | 54.7 +/- 8.4 | 100.0 +/- 0.0 | 76.0 +/- 4.3 | - |
| Nut Assembly | 0.0 +/- 0.0 | 53.3 +/- 1.9 | - | - |
| Pick Place | 0.0 +/- 0.0 | 50.7 +/- 6.6 | - | - |
| Coffee Preparation | 12.7 +/- 3.4 | 97.3 +/- 0.9 | 42.0 +/- 0.0 | - |
| Mobile Kitchen | 2.0 +/- 0.0 | 46.7 +/- 18.4 | - | - |
| Nut-and-Bolt Assembly | 8.7 +/- 2.5 | 92.7 +/- 2.5 | 81.3 +/- 8.2 | 72.7 +/- 4.1 |
| Gear Assembly | 14.7 +/- 5.2 | 98.7 +/- 1.9 | 74.0 +/- 2.8 | 56.7 +/- 1.9 |
| Frame Assembly | 10.7 +/- 6.8 | 82.0 +/- 4.3 | 68.7 +/- 3.4 | 36.7 +/- 2.5 |

[MIMICGEN-PAPER-V1, p.6, Fig.4]

### 4.2 Comparisons and transfer

- **Generated vs human volume:** agents trained on 200 MimicGen demonstrations (from 10 source demos) perform comparably to agents trained on 200 human demonstrations on most tested tasks; generating 200 -> 1000 demos gives a large jump, 1000 -> 5000 diminishing returns. [MIMICGEN-PAPER-V1, pp.6-7, Fig.4]
- **Source dataset size:** 10 vs 50 vs 200 source demonstrations changes downstream success only modestly (2 to 21 points); 1 source demo is task-dependent (much worse on Square, unchanged on Three Piece Assembly). [MIMICGEN-PAPER-V1, p.7]
- **Robot transfer:** Panda source data generates Sawyer/IIWA/UR5e datasets; DGR varies widely (38 to 74 percent, Square D0) while trained policy success stays in a narrow band (80 to 91 percent). [MIMICGEN-PAPER-V1, p.6]
- **Object transfer:** Mug Cleanup with one unseen mug 90.7 percent, with a 12-mug set 75.3 percent. [MIMICGEN-PAPER-V1, p.6]
- **Prior-work context:** BUDS reached 68.6 (Hammer Cleanup) and 72.0 (Kitchen) with 100 human demos; BC-RNN on 1000 generated D0 demos reaches 100.0 on both. [MIMICGEN-PAPER-V1, pp.6-7]
- **Real robot:** 10 source demos per task; DGR 82.3 percent (Stack, 243 attempts) and 52.1 percent (Coffee, 192 attempts); trained agents reach 36 percent (Stack) and 14 percent (Coffee) versus 0 percent for the source-only agents in the paper's comparison (the text is ambiguous about whether that evaluation used the narrow source region or the broader distribution); the paper attributes the low absolute numbers partly to the longer safety interpolations (50 steps vs 5) that decouple motion from observations. [MIMICGEN-PAPER-V1, p.8]

## 5. Ablations and mechanism analysis

- **Selection strategy (Table N.2):** removing nearest-neighbor or per-subtask selection cuts DGR sharply but barely moves policy success on most tasks: Square D0 DGR 73.7 -> 36.7 while low-dim success 98.0 -> 94.7; Stack Three D0 DGR 71.3 -> 37.8 while success 88.0 -> 84.0. Selection strategy mainly buys generation throughput, not final policy quality. [MIMICGEN-PAPER-V1, pp.37-38]
- **Replay with noise baseline (Table N.1):** replaying noisy source demos on source configurations improves over raw source data (Square 11.3 -> 42.0, Threading 19.3 -> 74.0) but stays well below MimicGen's transformed generation (90.7, 98.0), isolating the contribution of the object-frame transform + interpolation mechanism. [MIMICGEN-PAPER-V1, pp.36-37, Table N.1]
- **Source-demonstration usage is highly non-uniform:** generated Gear Assembly D1 drew over 850 of 1000 episodes from just 3 source demonstrations; Threading D0 drew over 170 episodes from one source demo and under 10 from another, with attempts roughly uniform, so the skew is success-driven. [MIMICGEN-PAPER-V1, p.7]
- **More varied source data (Appendix S):** sourcing from D2 instead of D0 shifts DGR (Square 73.7 -> 54.4 on D0, 31.8 -> 52.3 on D2), trading nominal-variant throughput for hard-variant throughput. [MIMICGEN-PAPER-V1, p.43]

## 6. Generation rate does not predict policy success

DGR and downstream policy success are decoupled, in both directions. Gear Assembly: DGR 46.9 / 8.2 / 7.1 percent (D0/D1/D2) against policy success 92.7 / 76.0 / 64.0. Additional cases: Mug Cleanup D0 29.5 DGR vs 82.0 success; Three Piece Assembly D0 35.6 vs 74.7; Coffee D2 27.7 vs 76.7. Full DGR table:

| Task | D0 | D1 | D2 |
|---|---|---|---|
| Stack | 94.3 | 90.0 | - |
| Stack Three | 71.3 | 68.9 | - |
| Square | 73.7 | 48.9 | 31.8 |
| Threading | 51.0 | 39.2 | 21.6 |
| Coffee | 78.2 | 63.5 | 27.7 |
| Three Pc. Assembly | 35.6 | 35.5 | 31.3 |
| Hammer Cleanup | 47.6 | 20.4 | - |
| Mug Cleanup | 29.5 | 17.0 | - |
| Kitchen | 100.0 | 42.7 | - |
| Nut Assembly | 50.0 | - | - |
| Pick Place | 32.7 | - | - |
| Coffee Preparation | 53.2 | 36.1 | - |
| Mobile Kitchen | 20.7 | - | - |
| Nut-and-Bolt Assembly | 66.0 | 59.4 | 47.6 |
| Gear Assembly | 46.9 | 8.2 | 7.1 |
| Frame Assembly | 45.3 | 32.7 | 28.9 |

Consequence: acceptance-rate style quality signals are not proxies for dataset usefulness under this generation mechanism. [MIMICGEN-PAPER-V1, pp.7, 40, Table P.1]

## 7. Bias, artifacts, and evidence boundaries

- **Measured initial-state bias of success-only acceptance (Appendix R).** Method: discretize each object's placement range into bins (n = 3 per dimension; Threading D1 has n^6 combined bins), count non-empty bins over the 1,000 generated episodes, report covered fraction of the reset-distribution support. Results run in both directions: high coverage for Coffee D1 98.8, Coffee D2 89.3, Square D1 92.6 percent; substantial bias for Three Piece Assembly D1 43.5, Threading D2 61.2, Mug Cleanup D1 64, Square D2 66.4, Three Piece Assembly D0 67.9, Threading D1 71 percent. The paper flags the analysis as coarse (bin-count sensitivity, no within-support uniformity measure, no motion-level bias measure). This is initial-state support coverage of generated episodes, not full state-space coverage, and there is no per-region or rare-mode conditional evaluation anywhere in the paper. [MIMICGEN-PAPER-V1, p.42]
- **Artifacts:** interpolation bridges can produce long, unnatural, potentially collision-including motions that are hard to imitate; acceptance checks task success only, so non-task-relevant collisions can be retained. [MIMICGEN-PAPER-V1, pp.8, 42]
- **Scope limits:** known subtask sequences and start-of-subtask object poses are required during generation; quasi-static tasks with rigid objects; novel objects assumed same-category with canonical frames. [MIMICGEN-PAPER-V1, pp.3, 8]
- **Protocol caveats for reuse:** max-over-checkpoints reporting (Sec. 3 above); DGR-success decoupling (Sec. 6); per-task success predicates mean "filtering" here is a predicate acceptance step, not score ranking; comparisons with score-ranking curators must not conflate the two operator families. [MIMICGEN-PAPER-V1, pp.4, 39-40]

## Cross-part connections

- **Foundation owners:** the acceptance step instantiates the outcome-predicate family in [data curation and filtering](../../foundations/data-and-evaluation/data-curation-and-filtering.md); the coverage measurement and max-over-checkpoints caveats belong to [evaluation methodology](../../foundations/data-and-evaluation/evaluation-methodology.md).
- **Model instantiations:** none in this KB; RoboCasa-era synthetic-demonstration pipelines (DreamGen-style) face the same acceptance-bias question at larger scale.
- **Open questions:** whether stratified acceptance across initial-state bins prevents the measured coverage collapse, and which failed attempts contain recoverable rare behavior, are open; the entry's optimization-transfer page states the testable intervention.

## Sources

- [MIMICGEN-PAPER-V1] Mandlekar et al., *MimicGen: A Data Generation System for Scalable Robot Learning using Human Demonstrations*, CoRL 2023, arXiv:2310.17596v1 (26 Oct 2023), local PDF and verified text extraction.

All quantitative claims above carry page locators into the arXiv v1 PDF. Entry-local source identities (paper pin, official code revision, dataset releases) resolve through this entry's `sources.yaml`.
