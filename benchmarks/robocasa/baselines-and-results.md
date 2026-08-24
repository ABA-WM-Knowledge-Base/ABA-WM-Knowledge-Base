---
id: world-model-kb.benchmarks.robocasa.baselines-and-results
title: Original RoboCasa Baselines and Protocol-Bound Results
kind: benchmark
status: maintained
last_updated: 2026-08-24
owners:
  - AIBuildAI world-model group
---

# Original RoboCasa Baselines and Protocol-Bound Results

## Retrieval metadata

**Relevant queries:** RoboCasa baseline, BC-Transformer, Diffusion Policy, human versus MimicGen, data scaling, composite task, real plus simulation, X-WAM 79.2, Cosmos Policy 67.1, or result comparability.

**Knowledge provided:** the original paper's principal quantitative evidence, later X-WAM comparison results, and the protocol conditions that prevent invalid cross-table conclusions.

**Related pages:** [Protocol and metrics](protocol-and-metrics.md) defines each result tuple; [datasets](datasets.md) owns data composition; the [X-WAM model evaluation](../../models/x-wam/evaluation.md) owns checkpoint-specific interpretation.

## Atomic data-scaling evidence

Under the RSS 2024 24-task atomic manipulation protocol, the multi-task BC-Transformer trained on 50 human demonstrations per task reaches 28.8% overall success. Training on 3,000 accepted MimicGen demonstrations per task reaches 47.6%. The `Generated-100` and `Generated-300` subsets lie between these conditions and exhibit a monotonic overall trend in Figure 7, but the paper does not print their exact aggregate values; they should be digitized from the figure only with an explicit extraction error. [RC24-PAPER-V1, pp.6-7, Figure 7]

This comparison supports a data-scale association within one generation pipeline and evaluation protocol. It does not isolate whether improvement comes from quantity, successful-trajectory selection, scene coverage, object coverage, or motion distribution. Skill slices show large heterogeneity: doors and drawers are much easier than pick-and-place and insertion, so an aggregate gain may not transfer to fine alignment or diverse-object grasping.

## Composite transfer evidence

The five single-task composite experiments compare 50-demonstration scratch training with fine-tuning from the generated-data atomic policy. [RC24-PAPER-V1, pp.7-8, Figure 8]

| Composite task | Scratch | Atomic-pretrained fine-tuning |
|---|---:|---:|
| `ArrangeVegetables` | 2.0% | 12.0% |
| `MicrowaveThawing` | 0.0% | 2.0% |
| `RestockPantry` | 0.0% | 6.0% |
| `PreSoakPan` | 0.0% | 4.0% |
| `PrepareCoffee` | 0.0% | 0.0% |

Atomic pretraining improves four tasks numerically, but absolute performance remains low and `PrepareCoffee` does not improve. The experiment points to stage-transition and long-horizon failures; it does not establish that scaling atomic data alone solves composite behavior.

## Policy architecture comparison

The appendix reports 56% success for BC-Transformer and 12% for a Diffusion Policy implementation on `PickPlaceCounterToSink`. This is not a clean architecture ablation: BC-Transformer receives a history of 10 observations, while the Diffusion Policy configuration uses history 2, prediction horizon 16, action horizon 8, 100 training diffusion steps, and 10 DDIM inference steps. The result motivates a temporal-context experiment but cannot attribute the 44-point gap solely to Transformer versus diffusion output modeling. [RC24-PAPER-V1, p.11]

## Real-data plus simulation evidence

Mean success over three seeds in the real-kitchen transfer study is: [RC24-PAPER-V1, pp.8-9, Figure 10]

| Object group | Task average, Real only | Task average, Real + Sim |
|---|---:|---:|
| Seen categories | 13.6% | 24.4% |
| Unseen categories | 2.6% | 9.3% |

Task-level seen-object gains are counter-to-sink `12.7±2.5 → 22.0±2.8`, sink-to-counter `20.0±5.9 → 29.3±4.1`, and counter-to-cabinet `8.0±1.6 → 22.0±5.8`. Unseen-object estimates have large standard deviations, including `8.9±7.9` and `11.1±11.0`; the directional evidence favors co-training, but precision is low.

## X-WAM 24-task comparison

Under the X-WAM paper's later 100-episode-per-task protocol, average success rates are: [XWAM-PAPER-V2, p.8, Table 1]

| Family | Method | Average success |
|---|---|---:|
| VLA | pi-zero | 62.5% |
| VLA | GR00T-N1.5 | 64.1% |
| WAM | UWM | 60.8% |
| WAM | DreamZero | 62.4% |
| WAM | Cosmos Policy | 67.1% |
| WAM | X-WAM | 79.2% |

The paper states that pi-zero, GR00T-N1.5, UWM, and Cosmos Policy values are taken from the Cosmos Policy paper, while DreamZero is reproduced with its backbone replaced by Wan2.2-5B. The comparison therefore mixes cited and reproduced baselines and does not hold every pretraining corpus or implementation constant. X-WAM exceeds the strongest listed baseline by 12.1 percentage points within the reported table, but the table alone does not isolate depth adaptation, ANS, and 5,873.9-hour pretraining; the paper's no-large-pretraining ablations address only a different training regime. [XWAM-PAPER-V2, pp.7-9, 17]

## Invalid numerical joins

- Do not compare Original-paper 47.6% directly with X-WAM 79.2% as a 31.6-point architecture gain. The training data, policy, scene selection, rollout count, camera and action interface, horizons, and evaluator implementation differ.
- Do not import RoboCasa365 leaderboard values into this table.
- Do not infer composite-task competence from the 24 atomic-task average.
- Do not treat higher PSNR or lower Chamfer Distance as task success; X-WAM reports correlations and joint ablations, not a universal monotonic mapping.
- Do not infer a locally reproduced result from a paper table. Local execution state is recorded separately in [reproduction](reproduction.md).

## Sources

Original results use `RC24-PAPER-V1`. The X-WAM comparison uses `XWAM-PAPER-V2`, resolved through the [X-WAM Paper source registry](../../papers/x-wam/sources.yaml).
