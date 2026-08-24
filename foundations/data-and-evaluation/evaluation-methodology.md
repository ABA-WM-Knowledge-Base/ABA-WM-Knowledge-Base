---
id: world-model-kb.foundations.data-and-evaluation.evaluation-methodology
title: World-Model Evaluation Methodology
kind: reference
status: maintained
last_updated: 2026-08-24
owners:
  - AIBuildAI world-model group
---

# World-Model Evaluation Methodology

## Retrieval metadata

**Relevant queries:** world-model evaluation, predictive accuracy, FVD, physical consistency, action sensitivity, benchmark protocol, closed-loop success, uncertainty, ablation, reproducibility, or statistical comparison.

**Knowledge provided:** a layered evaluation model, metric-to-claim mappings, comparison and falsification conditions, and failure modes that prevent perceptual or aggregate scores from standing in for decision utility.

**Related pages:** [Datasets and supervision](datasets-and-supervision.md) covers split identity and provenance; [planning and control](../decision-making/planning-and-control.md) covers closed-loop utility; [open problems](../research-frontiers/open-problems.md) connects unresolved measurement gaps; [Original RoboCasa protocol](../../benchmarks/robocasa/protocol-and-metrics.md) is a concrete versioned benchmark contract.

## Definition and formalism

Evaluation is a mapping from a scientific claim to observations capable of supporting or rejecting it. World models expose several non-equivalent claims, so no single scalar establishes overall quality.

For predictive distribution `p_theta(y|x)` and ground truth `y`, relevant quantities can include proper predictive scores such as negative log likelihood, task-state errors `d(f(y_hat), f(y))`, calibration, coverage across samples, and downstream utility. For control, the primary outcome is evaluated under the real or authoritative environment transition rather than only under the learned model:

```text
J_real(pi) = E_{P_real, pi}[sum_t gamma^t r_t].
```

Predicted return `J_model(pi)` is a diagnostic. The gap `J_real - J_model` exposes model-use error but depends on the policy distribution and objective.

## Assumptions and scope

A layered claim model prevents metric substitution:

| Layer | Question | Example evidence | Does not establish |
|---|---|---|---|
| Distribution fit | Does the model assign probability to observed futures? | likelihood, calibration, coverage | perceptual quality or control utility |
| Perceptual/media quality | Do outputs resemble the reference distribution to a feature metric or judge? | FVD, LPIPS, human preference | physical causality or action correctness |
| Dynamics/physical events | Are object state, contact, motion, and geometry correct? | event, pose, trajectory, relation metrics | task-optimal action |
| Conditional controllability | Does changing a condition produce the corresponding change? | matched action or prompt counterfactuals | safe closed-loop operation |
| Decision utility | Does the model improve ranking, planning, or policy learning? | realized return, ranking correlation | broad transfer outside the protocol |
| Embodied outcome | Does the complete system accomplish the task under feedback? | success, stage progress, recovery, violations | causal attribution to one component |
| Transfer/robustness | Does performance persist under declared shift? | held-out scene/task/object/embodiment curves | untested shifts or universal competence |

Fréchet Video Distance was proposed to measure distributional video quality and temporal coherence in a learned feature space and correlated with human judgments in its study. It is not a metric of action causality, contact correctness, or robot task success. Physion evaluates physical prediction across phenomena such as collision and stability, and its study reports stronger results for object-centric representations than non-object-centric alternatives while retaining a gap to humans. These are useful anchors for different layers. [EVAL-FVD-2019; EVAL-PHYSION-2021]

## Mechanism families

### Predictive and generative evaluation

- deterministic state or pixel error for a defined target;
- likelihood or proper score for stochastic predictions;
- calibration and coverage at a declared sample count;
- distributional media metrics such as FVD;
- human or learned-judge preference with disclosed prompts, randomization, and agreement;
- structured event, geometry, object-state, and relation extraction.

### Interventional evaluation

- matched input pairs differing in one action, control, prompt attribute, or initial state;
- sensitivity direction and magnitude against an authoritative transition;
- invariance tests for nuisance variables;
- independent replay of proposed actions;
- outcome ranking across candidate actions.

### Decision and embodied evaluation

- online return or task success under a fixed interaction budget;
- stage progress for long-horizon tasks;
- policy learning curves over real samples and compute;
- collision, penetration, force, joint-limit, and other constraint events;
- end-to-end latency, control rate, intervention, and recovery;
- transfer matrices across objects, scenes, tasks, language, and embodiments.

LIBERO evaluates lifelong robot learning and knowledge transfer across four suites totaling 130 tasks. CALVIN evaluates language-conditioned long-horizon manipulation. Original RoboCasa contributes 100 household task definitions in a large-scale simulation environment. These benchmarks test different capability slices and are not numerically interchangeable. [BENCH-LIBERO-2023; BENCH-CALVIN-2022; RC24-PAPER-V1]

## Design implications and trade-offs

| Evaluation variable | Why it matters | Confounding pattern | More informative evidence |
|---|---|---|---|
| Prediction horizon | error and ambiguity grow with time | one-step score presented as long-horizon competence | horizon-conditioned curves |
| Sample/candidate count | improves best-of-N coverage | more inference compute presented as model quality | score versus samples and wall time |
| Resolution and frame rate | change perceptual detail and event visibility | unmatched media settings | standardized and native-setting results |
| Judge/evaluator | determines what output properties are rewarded | same-family or prompt-sensitive judge | human calibration, agreement, and alternative metrics |
| Seed/rollout count | estimates stochastic variation | single favorable run | distribution, interval, and task-level paired analysis |
| Checkpoint and code revision | binds the evaluated system | mutable alias or mixed components | immutable identity and environment manifest |
| Data split unit | defines the generalization claim | adjacent frames or repeated scenes across splits | trajectory/scene/object/task/embodiment isolation |
| Inference/control budget | changes action quality and feedback | slower method receives more search | equal-budget and quality-latency Pareto results |
| Aggregate weighting | determines which domains dominate | large easy subset hides critical regression | per-slice results plus declared aggregation |

Henderson et al. document substantial variability and reporting problems in deep RL and motivate standardized experimental detail and significance-aware comparisons. This supports multi-seed and protocol-bound evidence; it does not imply one fixed statistical test for every benchmark. [EVAL-RL-MATTERS-2018]

## Evaluation and falsification

A model-improvement claim has a baseline, a single named intervention or factorial design, controlled variables, primary metric, regression metrics, evaluation unit, seeds or rollouts, and a result that contradicts the causal explanation. Examples:

| Hypothesis | Primary evidence | Falsifying or narrowing result |
|---|---|---|
| Better action conditioning improves dynamics | matched counterfactual transition accuracy | perceptual score rises but action-response accuracy is unchanged |
| Stochastic model captures multimodal futures | calibrated coverage at fixed samples | best-of-N rises only with more samples and calibration worsens |
| World-model update improves planning | realized return at fixed planner compute | predicted return rises while realized return falls |
| New data improves embodiment transfer | held-out embodiment adaptation curve | gain is confined to source embodiments or requires undocumented calibration |
| Future prediction improves WAM policy | closed-loop success and coupling ablation | action-only variant matches at equal data, parameters, and compute |
| Longer context improves long-horizon state | horizon-stratified state and task metrics | short tasks improve while long tasks remain unchanged or regress |

Reproduction states remain distinct: a result reported by a source, a command documented by code, a run observed locally, and a causal conclusion from a controlled experiment are different evidence objects. Raw outputs and failure slices make later reinterpretation possible when metrics change.

## Failure modes

- **Metric substitution:** perceptual realism is interpreted as physical or decision correctness.
- **Best-of-N opacity:** sample budget is omitted, preventing fair coverage comparison.
- **Benchmark overfitting:** repeated tuning on a public evaluation set is presented as generalization.
- **Split leakage:** correlated frames, scenes, trajectories, or generated seeds cross train and test.
- **Judge circularity:** the generator and evaluator share model family, training data, or failure modes.
- **Aggregate masking:** an average hides long-horizon, safety-critical, language, or embodiment regression.
- **Protocol drift:** checkpoint, preprocessing, prompt, resolution, controller, or task version differs across rows.
- **Seed undercoverage:** stochastic variance is smaller or larger than the sampled runs reveal.
- **Compute mismatch:** extra candidates, steps, context, or wall time create the observed gain.
- **Simulator-only inference:** success in an approximate evaluator is generalized to real dynamics.
- **Unreported interventions:** human resets, corrections, or safety stops are absent from task-success counts.
- **Non-independent claims:** the same trial set is used to discover, tune, and confirm an intervention.

## Cross-part instantiations

- [IRASim](../../papers/irasim/paper.md) separates paired video reconstruction, human preference, simulated policy ordering, candidate-ranking utility, and real-robot outcomes; its small-task correlation and coupled value-model evidence illustrate why these layers cannot be substituted for one another.
- [DIAMOND](../../papers/diamond/paper.md) binds Atari 100k human-normalized scores to the main branch; CSGO is a separate qualitative surface.
- [OccWorld](../../papers/occworld/paper.md) binds occupancy and planning metrics to nuScenes license terms and named OccWorld variants.
- [Cosmos3-Nano evaluation](../../models/cosmos3-nano/evaluation.md) owns reported benchmark values, task modes, metric directions, and comparison conditions.
- [Cosmos3-Nano limitations](../../models/cosmos3-nano/limitations.md) owns known model-specific gaps and unsupported inferences.
- [Cosmos3-Nano reproduction](../../models/cosmos3-nano/reproduction.md) separates documented capability from locally observed execution state.
- [Cosmos3-Nano action modeling](../../models/cosmos3-nano/action-modeling.md) maps FD, ID, and WAM outputs to geometry, state, dynamics, sensitivity, and task-utility measures.
- [Cosmos3-Nano optimization reference](../../models/cosmos3-nano/optimization-playbook.md) instantiates controlled experiment patterns without owning workflow orchestration.
- [X-WAM evaluation](../../models/x-wam/evaluation.md) separates policy success, RGB/depth/point-cloud fidelity, latency, and no-large-pretraining ablations.
- [Original RoboCasa protocol and metrics](../../benchmarks/robocasa/protocol-and-metrics.md) owns the original rollout tuple and its separation from later X-WAM and RoboCasa365 protocols.
- [Paper entries](../../papers/README.md) can preserve exact benchmark versions, evaluator details, results, and confidence conditions for each publication.

## Sources

- [EVAL-FVD-2019] Unterthiner et al., *Towards Accurate Generative Models of Video: A New Metric and Challenges*, ICLR 2019 workshop, arXiv:1812.01717.
- [EVAL-PHYSION-2021] Bear et al., *Physion: Evaluating Physical Prediction from Vision in Humans and Machines*, NeurIPS Datasets and Benchmarks 2021.
- [BENCH-CALVIN-2022] Mees et al., *CALVIN: A Benchmark for Language-Conditioned Policy Learning for Long-Horizon Robot Manipulation Tasks*, IEEE Robotics and Automation Letters 7(3), DOI:10.1109/LRA.2022.3180108.
- [BENCH-LIBERO-2023] Liu et al., *LIBERO: Benchmarking Knowledge Transfer for Lifelong Robot Learning*, NeurIPS Datasets and Benchmarks 2023, DOI:10.52202/075280-1939.
- [RC24-PAPER-V1] Nasiriany et al., *RoboCasa: Large-Scale Simulation of Everyday Tasks for Generalist Robots*, arXiv:2406.02523v1 / RSS 2024; identity owned by the [Original RoboCasa registry](../../benchmarks/robocasa/sources.yaml).
- [EVAL-RL-MATTERS-2018] Henderson et al., *Deep Reinforcement Learning That Matters*, AAAI 2018, DOI:10.1609/aaai.v32i1.11694.
