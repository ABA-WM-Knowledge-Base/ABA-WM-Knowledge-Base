---
id: world-model-kb.foundations.research-frontiers.open-problems
title: Open Problems in World Models
kind: reference
status: maintained
last_updated: 2026-08-24
owners:
  - AIBuildAI world-model group
---

# Open Problems in World Models

## Retrieval metadata

**Relevant queries:** world-model open problem, long-horizon prediction, causal action model, uncertainty, multimodal future, compositional generalization, cross-embodiment transfer, sim-to-real, evaluation gap, or real-time world model.

**Knowledge provided:** field-level unresolved questions, the primary evidence that makes each question consequential, competing explanations, and measurements capable of separating them. The page is an evidence map rather than a research schedule.

**Related pages:** [World-model definitions](../definitions-and-taxonomy/world-model.md) delimit the model class; [problem formulation](../problem-formulation/problem-formulation.md), [representations](../representations/README.md), [decision making](../decision-making/README.md), and [evaluation](../data-and-evaluation/evaluation-methodology.md) own established concepts used here.

## Definition and evidence status

An open problem is a condition whose answer remains uncertain and would materially change a model, data, objective, evaluation, or system judgment. It is not merely an unimplemented feature. The entries below distinguish three evidence states:

- **Established observation:** a cited source demonstrates a behavior or limitation under a stated protocol.
- **Cross-source synthesis:** multiple results motivate a general question, but do not establish one universal cause.
- **Testable hypothesis:** a proposed explanation with an intervention and an outcome that can contradict it.

The same question can be resolved for one model and remain open at field level. A result on Atari, a simulated manipulation suite, or one robot embodiment does not close the corresponding question for Physical AI in general.

## Formal view

For a learned model `p_theta`, a decision process `D`, and deployment distribution `q`, useful world-model quality is not a single prediction score. A general target can be represented as

```text
Q(theta; D, q) = {
  predictive fit,
  intervention response,
  uncertainty calibration,
  decision utility,
  robustness and cost
}.
```

An apparent improvement is underdetermined when several components change together. For example, a better task score after increasing model size, data, samples, and search does not identify which component caused the gain. The open problems below therefore connect each broad question to a discriminating comparison rather than treating benchmark progress as causal explanation.

## Assumptions and scope

The registry treats a problem as open when primary evidence leaves at least two materially different explanations or when evidence from one domain does not determine behavior in another. It covers model-independent uncertainties that recur across architectures. Checkpoint defects, missing implementation details, and environment-specific compatibility questions belong to the corresponding model or paper entry.

The entries describe what knowledge could alter a design judgment; they do not rank research value, prescribe experiments, or determine task order. Source results remain bounded by their datasets, model variants, compute, and evaluators. A discriminating test is an evidential pattern, not a claim that the test is sufficient for every deployment.

## Mechanism families

The open questions span interacting mechanism families:

| Family | Unresolved interface |
|---|---|
| State and representation | which observable, latent, object, geometric, or belief variables retain decision-relevant information |
| Predictive objective | how autoregressive, diffusion, flow, contrastive, and decision-aware losses trade likelihood, diversity, and utility |
| Action and intervention | whether control conditions identify causal consequences and transfer across embodiments |
| Memory and temporal abstraction | how hidden state, rollout horizon, skills, and re-observation affect long-horizon validity |
| Uncertainty and model use | how confidence should modify planning, policy learning, and data acquisition under shift |
| Data and supervision | how heterogeneous sources, synthetic data, provenance, and missing labels shape transferable dynamics |
| Embodied systems | how model predictions become timed, constrained, recoverable physical commands |
| Evaluation | which measurements predict physical correctness and downstream utility under fixed compute |

Progress in one family can move a bottleneck elsewhere. A more expressive predictive objective can expose weak action alignment; a stronger planner can exploit small model errors; a better action adapter can reveal missing contact state. This interaction is why the registry retains multiple evidence layers.

## Frontier map

| Open question | Established evidence | What remains unresolved | Discriminating evidence |
|---|---|---|---|
| What information must a world model preserve for decisions? | Value-aware model learning argues that likelihood can model detail irrelevant to a decision; MuZero and TD-MPC2 demonstrate useful planning without full observation reconstruction. [MBRL-VAML-2017; PLAN-MUZERO-2020; MBRL-TDMPC2-2024] | How to retain enough information for changing future tasks without spending capacity on every observable detail. | Compare reconstruction, predictive, and value-aware objectives across multiple downstream tasks, including tasks hidden during representation learning. |
| How can long-horizon rollouts remain useful? | PlaNet introduces multi-step latent overshooting; MBPO analyzes model bias and uses short rollouts from real states; recurrent sequence models still face distribution shift as generated states re-enter context. [FD-PLANET-2019; MBRL-MBPO-2019; OBJ-SCHEDULED-SAMPLING-2015] | Whether architecture, objective, data coverage, uncertainty, memory, temporal abstraction, or closed-loop correction is the dominant limit in a target domain. | Horizon-conditioned error and realized decision utility under controlled changes to rollout training, re-observation, and abstraction. |
| How should partial observability and persistent memory be represented? | POMDP theory makes belief sufficient for optimal control under its assumptions; learned recurrent states approximate rather than guarantee calibrated beliefs. [CTRL-POMDP-1998] | How much history is needed, how memories should be updated under occlusion, and how to test whether hidden state retains task-critical unobserved facts. | Controlled reveal/occlude/reveal tasks, delayed interventions, belief calibration, and probes tied to downstream decisions rather than reconstruction alone. |
| Can uncertainty remain calibrated under policy-induced shift? | PETS uses probabilistic ensembles and trajectory sampling; MBPO documents the policy/model-bias trade-off. [MBRL-PETS-2018; MBRL-MBPO-2019] | How to separate irreducible outcome variation from insufficient-data uncertainty in large generative models, and how planners should use either estimate. | Error-versus-uncertainty curves on on-policy, counterfactual, and held-out shifts, followed by realized risk/return under fixed control budgets. |
| Does action conditioning identify causal dynamics? | Action-conditioned video and robot models can predict controlled transitions in their evaluated settings; inverse/forward joint learning can produce action-relevant features. [FND-OH-VIDEO-2015; DYN-POKE-2016; PLAN-VISUAL-FORESIGHT-2017] | Observational action data can contain policy, scene, and embodiment confounding; the degree to which a model learns intervention effects rather than correlations remains model- and dataset-specific. | Matched action interventions from identical or tightly matched states, randomized behavior policies, environment replay, and held-out policy evaluation. |
| How should multiple valid futures be learned and judged? | Pixel regression can average plausible outcomes; diffusion and stochastic latent models offer distributional alternatives; FVD measures distribution-level video quality but not action correctness. [REP-MATHIEU-2016; OBJ-VIDEO-DIFFUSION-2022; FD-PLANET-2019; EVAL-FVD-2019] | How to jointly measure calibration, semantic mode coverage, physical validity, and decision relevance without rewarding arbitrary samples or unlimited best-of-N compute. | Proper predictive scores plus event-level calibrated coverage, diversity within valid outcome classes, fixed sample counts, and downstream candidate utility. |
| Which representation supports compositional physical generalization? | Interaction Networks, Visual Interaction Networks, CSWM, and object-centric methods encode entities and relations; Physion reports an advantage for object-centric representations in its evaluated physical-prediction setting while retaining a gap to humans. [REP-INTERACTION-NET-2016; REP-VIN-2017; REP-CSWM-2020; EVAL-PHYSION-2021] | Whether explicit objects remain beneficial in clutter, deformable media, identity changes, and open-world scenes, and how object discovery errors interact with dynamics. | Held-out object count, relation composition, topology change, occlusion, and deformable-interaction tests at matched capacity and data. |
| How can persistent 3D/4D geometry coexist with scalable video generation? | NeRF, D-NeRF, 3D Gaussian Splatting, and occupancy world models provide explicit spatial or spatiotemporal representations; video models scale flexible appearance generation. [REP-NERF-2020; REP-DNERF-2021; REP-3DGS-2023; REP-OCCWORLD-2024] | The representation that best balances geometry, dynamics, editability, memory, rendering cost, and action-conditioned prediction across open environments. | Novel-view and re-observation consistency, object permanence, metric trajectory accuracy, interaction response, and real-time cost in the same protocol. |
| When do latent actions transfer to physical controls? | Genie learns controllable latent actions from unlabeled video; inverse models infer actions from observed transitions. [WFM-GENIE-2024; DYN-POKE-2016] | Latent actions are not uniquely identifiable and need not align with robot joints, frames, rates, or forces. | Alignment with recorded physical actions, invertible target adapters, per-axis intervention tests, and target-data adaptation curves. |
| How can action semantics transfer across embodiments? | Octo reports generalist pretraining and adaptation across multiple robot platforms; DROID and BridgeData provide large but embodiment- and protocol-specific trajectory collections. [EMB-OCTO-2024; DATA-DROID-2024; DATA-BRIDGEV2-2023] | Which aspects of action can be shared across kinematics, controllers, rates, sensors, and morphology without creating dataset-identity shortcuts. | Leave-one-embodiment-out evaluation, explicit adapter ablations, canonical-versus-native action comparisons, and physical-unit error after decoding. |
| Can heterogeneous video and robot data be mixed without hidden negative transfer? | Ego4D supplies broad egocentric observation; robot datasets add physical action supervision; UniSim and generalist policies use heterogeneous sources. [DATA-EGO4D-2022; DATA-DROID-2024; WFM-UNISIM-2024; EMB-OCTO-2024] | Effective sampling, alignment, provenance, and supervision ratios are not determined by raw dataset scale, and one domain can dominate shared features. | Fixed-token mixture matrices, leave-one-source-out transfer, dataset-identifiability probes, and per-domain retention rather than one aggregate. |
| When does a learned or analytic simulator support real deployment? | UniSim reports simulator-trained policies transferring in its selected experiments; Original RoboCasa reports scalable simulated household tasks and selected real-world evidence. [WFM-UNISIM-2024; RC24-PAPER-V1] | Visual similarity does not bound errors in contact, sensing, actuator dynamics, latency, recovery, or long-tail events. | Paired simulator/real transition tests, policy ranking correlation, hardware-in-the-loop evaluation, and residual failure analysis across controlled randomization. |
| Can large world models act at the required feedback rate? | Visual MPC demonstrates closed-loop use of an action-conditioned predictor; DreamZero reports a particular 14B WAM operating at 7 Hz. [PLAN-VISUAL-FORESIGHT-2017; WAM-DREAMZERO-2026] | The accuracy-latency frontier across task dynamics, model scale, candidate count, action chunks, and hardware, especially under observation or network delay. | End-to-end timestamped latency, effective control rate, success under injected delay, and equal-wall-clock comparisons of direct policy, cached, distilled, and planning variants. |
| Which metrics track physical and decision competence? | FVD targets video-distribution quality; Physion targets physical prediction; LIBERO, CALVIN, and Original RoboCasa target different embodied capabilities; RL results can vary materially with implementation and seeds. [EVAL-FVD-2019; EVAL-PHYSION-2021; BENCH-LIBERO-2023; BENCH-CALVIN-2022; RC24-PAPER-V1; EVAL-RL-MATTERS-2018] | A common protocol that connects perceptual quality, causal response, physical events, planning value, closed-loop success, safety, and compute without collapsing them into an opaque score. | Metric-to-outcome correlation across diverse systems, preregistered failure slices, fixed inference budgets, multi-seed evaluation, and independent real or authoritative simulators. |

## Design implications and trade-offs

The following examples show how broad frontier statements become falsifiable. They are hypotheses, not established optimization rules.

### Long-horizon failure

Three explanations predict different interventions:

- **One-step model error dominates:** multi-step or overshooting objectives reduce horizon-conditioned transition error and improve planning.
- **Hidden-state loss dominates:** additional memory or state supervision helps specifically after occlusion or delayed effects.
- **Search/model exploitation dominates:** uncertainty-aware or shorter receding-horizon use improves realized return without materially changing open-loop prediction.

A matched experiment can vary one mechanism while holding model capacity, data, action budget, and evaluator fixed. Improvement only in the predicted metric, without realized decision gain, narrows the causal explanation.

### Future prediction in action models

Joint future/action training admits at least three explanations:

- future prediction teaches causal consequences useful for action;
- the future branch regularizes shared visual features without being used as a simulator;
- gains come from added parameters, data, or compute rather than future supervision.

Action-only, joint-training/current-only-inference, and joint-training/joint-inference variants at matched parameters and compute separate these explanations. Independent replay distinguishes correct consequence modeling from internally consistent hallucination. [WAM-DREAMZERO-2026]

### Scale and generality

DreamerV3 reports robust performance across more than 150 tasks with one configuration, while Genie demonstrates a large generative interactive model across varied environments. These results motivate—not settle—the hypothesis that capability grows with model and data scale. [MBRL-DREAMERV3-2025; WFM-GENIE-2024]

Scale is causally identified only when data distribution, optimizer, number of updates, inference budget, and evaluation protocol are accounted for. A larger model that sees more tokens or samples more futures does not isolate a parameter-scaling effect.

## Evaluation and falsification

Evidence for an open-problem hypothesis is stronger when it spans the relevant chain:

```text
intervention
  -> predicted internal change
  -> capability-aligned offline metric
  -> independent transition or decision outcome
  -> held-out robustness slice.
```

The chain can fail at different points. A representation probe can improve without changing rollouts; rollout metrics can improve without changing candidate ranking; candidate ranking can improve in simulation without real transfer. These outcomes refine the hypothesis rather than becoming generic “model failure.”

Useful falsification patterns include:

- matched counterfactual actions and conditions;
- equal-data, equal-update, and equal-compute ablations;
- horizon, sample-count, and latency curves rather than one operating point;
- held-out scene, task, object, policy, and embodiment matrices;
- environment replay independent of the learned model;
- calibration and failure-slice reporting alongside aggregates;
- negative controls that remove the proposed information path.

## Failure modes

- **Terminology as evidence:** calling a system a world foundation model or WAM is treated as proof of generality or causal action understanding.
- **Benchmark closure:** a finite benchmark gain is interpreted as resolving a field-level problem.
- **Mechanism conflation:** model size, data, objective, search, and inference budget change together.
- **Metric substitution:** perceptual quality stands in for physical correctness or task utility.
- **Architecture universalization:** one successful representation or objective is assumed to dominate outside its tested regime.
- **Missing negative result:** a hypothesis has no specified observation that would weaken it.
- **Shared-model circularity:** generated outcomes are evaluated by a closely related model or internal consistency alone.
- **Unbounded best-of-N:** additional sampling is presented as improved calibration or model quality.
- **Embodiment erasure:** tensor shape compatibility is treated as equivalent action semantics.
- **Source-status erasure:** preprint, technical-report, benchmark, and independently reproduced evidence are treated as interchangeable.

## Cross-part instantiations

- [Cosmos3-Nano limitations](../../models/cosmos3-nano/limitations.md) maps field-level risks to the model's actual evidence surface.
- [Cosmos3-Nano research registry](../../models/cosmos3-nano/research-queue.md) records model-specific unresolved dependencies without turning this field map into an execution queue.
- [Cosmos3-Nano action modeling](../../models/cosmos3-nano/action-modeling.md) exposes concrete FD, ID, WAM, action-adapter, and counterfactual questions.
- [Cosmos3-Nano data](../../models/cosmos3-nano/data.md) and [evaluation](../../models/cosmos3-nano/evaluation.md) instantiate mixture, provenance, metric, and protocol questions.
- [Cosmos3-Nano optimization reference](../../models/cosmos3-nano/optimization-playbook.md) contains experiment-design patterns that can test model-specific hypotheses.
- [X-WAM research registry](../../models/x-wam/research-queue.md) narrows geometry, asynchronous sampling, counterfactual action sensitivity, transfer, and resource questions to the released model.
- [Original RoboCasa limitations](../../benchmarks/robocasa/limitations.md) owns benchmark-specific validity gaps and the boundary to RoboCasa365.
- [Representative paper entries](../../papers/README.md) can preserve exact mechanisms, evaluated domains, negative results, and source status for the works cited here.

## Sources

- [CTRL-POMDP-1998] Kaelbling, Littman, and Cassandra, *Planning and Acting in Partially Observable Stochastic Domains*, Artificial Intelligence 101.
- [FD-PLANET-2019] Hafner et al., *Learning Latent Dynamics for Planning from Pixels*, ICML 2019.
- [MBRL-PETS-2018] Chua et al., *Deep Reinforcement Learning in a Handful of Trials using Probabilistic Dynamics Models*, NeurIPS 2018.
- [MBRL-VAML-2017] Farahmand, Barreto, and Nikovski, *Value-Aware Loss Function for Model-Based Reinforcement Learning*, AISTATS 2017.
- [MBRL-MBPO-2019] Janner et al., *When to Trust Your Model: Model-Based Policy Optimization*, NeurIPS 2019.
- [PLAN-MUZERO-2020] Schrittwieser et al., *Mastering Atari, Go, Chess and Shogi by Planning with a Learned Model*, Nature 588.
- [MBRL-TDMPC2-2024] Hansen, Su, and Wang, *TD-MPC2: Scalable, Robust World Models for Continuous Control*, ICLR 2024.
- [MBRL-DREAMERV3-2025] Hafner et al., *Mastering Diverse Control Tasks through World Models*, Nature 640.
- [DYN-POKE-2016] Agrawal et al., *Learning to Poke by Poking*, NeurIPS 2016.
- [PLAN-VISUAL-FORESIGHT-2017] Finn and Levine, *Deep Visual Foresight for Planning Robot Motion*, ICRA 2017.
- [WFM-GENIE-2024] Bruce et al., *Genie: Generative Interactive Environments*, ICML 2024.
- [WFM-UNISIM-2024] Yang et al., *Learning Interactive Real-World Simulators*, ICLR 2024.
- [WAM-DREAMZERO-2026] Ye et al., *World Action Models are Zero-shot Policies*, arXiv:2602.15922; primary preprint.
- [REP-INTERACTION-NET-2016] Battaglia et al., *Interaction Networks for Learning about Objects, Relations and Physics*, NeurIPS 2016.
- [REP-VIN-2017] Watters et al., *Visual Interaction Networks: Learning a Physics Simulator from Video*, NeurIPS 2017.
- [REP-CSWM-2020] Kipf, van der Pol, and Welling, *Contrastive Learning of Structured World Models*, ICLR 2020.
- [REP-NERF-2020] Mildenhall et al., *NeRF: Representing Scenes as Neural Radiance Fields for View Synthesis*, ECCV 2020.
- [REP-DNERF-2021] Pumarola et al., *D-NeRF: Neural Radiance Fields for Dynamic Scenes*, CVPR 2021.
- [REP-3DGS-2023] Kerbl et al., *3D Gaussian Splatting for Real-Time Radiance Field Rendering*, SIGGRAPH 2023.
- [REP-OCCWORLD-2024] Zheng et al., *OccWorld: Learning a 3D Occupancy World Model for Autonomous Driving*, ECCV 2024.
- [OBJ-SCHEDULED-SAMPLING-2015] Bengio et al., *Scheduled Sampling for Sequence Prediction with Recurrent Neural Networks*, NeurIPS 2015.
- [OBJ-VIDEO-DIFFUSION-2022] Ho et al., *Video Diffusion Models*, NeurIPS 2022.
- [DATA-EGO4D-2022] Grauman et al., *Ego4D: Around the World in 3,000 Hours of Egocentric Video*, CVPR 2022.
- [DATA-BRIDGEV2-2023] Walke et al., *BridgeData V2: A Dataset for Robot Learning at Scale*, CoRL 2023.
- [DATA-DROID-2024] Khazatsky et al., *DROID: A Large-Scale In-The-Wild Robot Manipulation Dataset*, RSS 2024.
- [EMB-OCTO-2024] Ghosh et al., *Octo: An Open-Source Generalist Robot Policy*, RSS 2024.
- [EVAL-FVD-2019] Unterthiner et al., *Towards Accurate Generative Models of Video: A New Metric and Challenges*, ICLR 2019 workshop.
- [EVAL-PHYSION-2021] Bear et al., *Physion: Evaluating Physical Prediction from Vision in Humans and Machines*, NeurIPS Datasets and Benchmarks 2021.
- [BENCH-CALVIN-2022] Mees et al., *CALVIN*, IEEE Robotics and Automation Letters 7(3).
- [BENCH-LIBERO-2023] Liu et al., *LIBERO*, NeurIPS Datasets and Benchmarks 2023.
- [RC24-PAPER-V1] Nasiriany et al., *RoboCasa*, arXiv:2406.02523v1 / RSS 2024; identity owned by the [Original RoboCasa registry](../../benchmarks/robocasa/sources.yaml).
- [EVAL-RL-MATTERS-2018] Henderson et al., *Deep Reinforcement Learning That Matters*, AAAI 2018.
