---
id: world-model-kb.benchmarks.robocasa.protocol-and-metrics
title: Original RoboCasa Protocols and Metrics
kind: benchmark
status: maintained
last_updated: 2026-08-24
owners:
  - AIBuildAI world-model group
---

# Original RoboCasa Protocols and Metrics

## Retrieval metadata

**Relevant queries:** RoboCasa evaluation protocol, task success, rollout count, scene split, unseen object, horizon, seed, evaluator, average success rate, confidence interval, or fair comparison.

**Knowledge provided:** the original paper's distinct evaluation protocols, the later 24-task protocol used by X-WAM, metric semantics, and the minimal tuple required to interpret or compare a result.

**Related pages:** [Tasks and environments](tasks-and-environments.md) owns environment variables and success predicates; [baselines and results](baselines-and-results.md) binds reported numbers to these protocols; [evaluation methodology](../../foundations/data-and-evaluation/evaluation-methodology.md) owns general comparison validity.

## No single universal RoboCasa protocol

Original RoboCasa is a simulator, task catalog, dataset family, and set of experimental protocols. The RSS 2024 paper does not define one leaderboard-wide split and aggregation rule for all 100 tasks. At least three protocols appear in the paper, and later works define another common 24-task protocol. Reporting only “RoboCasa average success” is therefore underspecified.

## RSS 2024 atomic-task protocol

The main scaling study trains one multi-task BC-Transformer per dataset condition. It evaluates 24 manipulation tasks; navigation is absent from the generated-data comparison. For each task, the policy runs 50 trials across five fixed scenes with distinct floor plans and styles. Object instances are unseen during training, and two scenes use unseen styles. The published overall success is grouped across task skills and then reported as an overall task-success percentage. [RC24-PAPER-V1, pp.6-7, Figure 7]

Protocol identity:

```text
tasks: 24 atomic manipulation tasks
policy: multi-task BC-Transformer
conditions: Human-50 / Generated-100 / Generated-300 / Generated-3000
rollouts: 50 per task
scenes: five fixed evaluation scenes
generalization: unseen object instances; two unseen styles
outcome: task-defined binary success
```

The paper does not provide a complete public seed list, per-rollout scenario manifest, or uncertainty interval for the aggregate Figure 7 bars. A local reproduction should materialize those fields instead of assuming the fixed scenes alone make runs identical.

## RSS 2024 composite-task protocol

Five representative composite tasks—`ArrangeVegetables`, `MicrowaveThawing`, `RestockPantry`, `PreSoakPan`, and `PrepareCoffee`—are trained as separate single-task policies from 50 human demonstrations each. `Scratch` initializes a new policy; `Fine-tuning` initializes from the atomic-task policy trained on full generated data. The paper reports one success percentage per task and condition. It does not state confidence intervals or a seed count next to Figure 8, so those fields must not be invented. [RC24-PAPER-V1, pp.7-8, Figure 8]

## RSS 2024 real-robot transfer protocol

Three pick-and-place tasks are evaluated on a Franka Panda using DROID hardware: counter-to-sink, sink-to-counter, and counter-to-cabinet. Each task has 50 real demonstrations spanning five object categories. `Real only` uses the target real data; `Real + Sim` co-trains with all simulated single-stage MimicGen demonstrations. Results are means and standard deviations over three training seeds. For each seed, evaluation covers five seen and three unseen object categories, but the exact rollout count per category is not stated in the main text. [RC24-PAPER-V1, pp.8-9, Figures 9-10]

This protocol has controller and frequency shifts: simulated Operational Space Control at 20 Hz versus a different real controller at 15 Hz, plus camera, lighting, and base-placement changes. It tests data transfer, not simulator-identical policy deployment.

## Later 24-task WAM protocol: X-WAM

X-WAM evaluates the 24 manipulation tasks over 100 episodes per task and averages task success. Its released client fixes a task list, task-specific maximum horizons from 300 to 1,000 simulator steps, five `(layout, style)` pairs, object split `B`, `PandaOmron`, three 256×256 cameras, and deterministic seeds computed from environment rank and rollout index. It checks `env._check_success()` after each executed action and saves one JSON summary plus rollout video per episode. [XWAM-PAPER-V2, pp.7, 17-19; XWAM-CODE-72CF, `evaluation/robocasa_client.py`]

This later protocol is useful for comparing X-WAM with the baselines as reported in that paper. It is not numerically interchangeable with the RSS 2024 scaling experiment: model family, training data, cameras, action chunks, scene construction, horizons, and rollout count differ.

## Metric semantics

For task `j` with `N_j` rollouts and binary terminal success `y_ji`, the task success rate is

```text
SR_j = (1 / N_j) * sum_i y_ji
```

An unweighted benchmark average is `mean_j SR_j`; a rollout-weighted average is `sum_j sum_i y_ji / sum_j N_j`. They coincide only when every task has equal rollout count. Reports must identify which aggregation is used. With 100 rollouts per task, one success changes a task rate by one percentage point; uncertainty remains substantial for per-task comparisons, so paired scenario evaluation or binomial intervals are preferable to one aggregate point estimate.

RoboCasa binary success does not measure progress, collision rate, smoothness, latency, video fidelity, depth accuracy, or 3D consistency. X-WAM adds PSNR, SSIM, LPIPS, AbsRel, delta-1, and Chamfer Distance for its world-model output; those are model evaluation metrics computed in RoboCasa, not native task-success replacements. [XWAM-PAPER-V2, pp.8-9, Tables 3-4]

## Comparison key

Every reported value should retain:

| Field | Why it changes interpretation |
|---|---|
| Release and simulator dependencies | Physics, assets, task code, horizons, and rendering can drift |
| Task list and aliases | “24 tasks” can mask inclusions or renamed classes |
| Scene/style/object distribution | Measures memorization, in-distribution control, or generalization differently |
| Robot, controller, action frame, rate | Changes closed-loop dynamics even for identical network outputs |
| Cameras and preprocessing | Changes observation information and visual distribution |
| Dataset/checkpoint revision | Separates model change from data or normalization change |
| Horizon, termination, action chunk | Directly changes opportunity to succeed and compounding error |
| Seeds/scenario manifest and rollout count | Determines pairing, uncertainty, and reproducibility |
| Success predicate and aggregation | Defines the metric itself |

Without this tuple, a number can be retained as a reported claim but cannot support a causal optimization conclusion.

## Sources

Original protocols use `RC24-PAPER-V1`, `RC24-CODE-V02`, and `RC24-EVAL-DOC-V02`. X-WAM protocol sources are owned by the [X-WAM Paper](../../papers/x-wam/README.md).
