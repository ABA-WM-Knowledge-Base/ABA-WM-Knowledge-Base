---
id: world-model-kb.foundations.data-and-evaluation.datasets-and-supervision
title: Datasets and Supervision for World Models
kind: reference
status: maintained
last_updated: 2026-08-14
owners:
  - AIBuildAI world-model group
---

# Datasets and Supervision for World Models

## Retrieval metadata

**Relevant queries:** world-model data, robot trajectory, video data, action supervision, language annotation, multimodal alignment, data mixture, synthetic data, deduplication, leakage, embodiment data, or failure trajectories.

**Knowledge provided:** data-unit and supervision semantics, representative primary dataset evidence, mixture and transformation levers, and evaluation conditions needed to attribute a model change to data.

**Related pages:** [Forward dynamics](../problem-formulation/forward-dynamics.md) and [inverse dynamics](../problem-formulation/inverse-dynamics.md) define transition supervision; [robotics and embodied AI](../embodied-systems/robotics-and-embodied-ai.md) defines action contracts; [evaluation methodology](evaluation-methodology.md) defines split and comparison evidence.

## Definition and formalism

A world-model dataset is a distribution over temporally related observations, optional hidden-state labels, interventions, and context. A general record can be written as

```text
d_i = {
  observations o[0:T], actions a[0:T-1], timestamps tau,
  task or language g, rewards r, states s, events e,
  embodiment m, environment q, provenance p
}.
```

Only some fields exist in any dataset. Missing action, state, reward, or timing information changes which conditionals are identifiable. Video-only data supports observation dynamics and possibly inferred latent actions; it does not directly supervise a physical controller. Robot trajectories can supervise action-conditioned transitions only when action semantics and temporal alignment are preserved.

Dataset size has no single unit. Frames, clips, hours, transitions, trajectories, episodes, tasks, skills, scenes, objects, embodiments, and tokens measure different properties. A claim comparing dataset scale retains the counting unit and deduplication rule.

## Assumptions and scope

Supervision can be grouped by the factor it identifies:

| Supervision | Identified information | Missing-condition risk |
|---|---|---|
| Consecutive video | temporal appearance and observed motion | agent action and hidden causes unknown |
| Recorded action | intervention associated with transition | units, frame, rate, and controller may be missing |
| Proprioception/state | robot or simulator state | privileged state may not exist at deployment |
| Reward/success | task preference or outcome | sparse reward and annotation policy bias |
| Language/goal | semantic task context | underspecified physical execution |
| Contact/force/event | interaction discontinuities | sensor noise and embodiment specificity |
| Multi-view/calibration | geometry and cross-view correspondence | synchronization and occlusion |
| Failure/recovery label | off-nominal dynamics and correction | failure taxonomy and collection bias |
| Synthetic provenance | known generator/simulator and parameters | simulation artifacts and reality gap |

Large and diverse data can support generalization, but diversity is multidimensional. Ego4D reports 3,670 hours from 931 camera wearers across 74 locations in nine countries, providing broad egocentric daily-life observation. BridgeData V2 reports 53,896 robot trajectories across 24 environments. DROID's current RSS PDF reports 76,000 trajectories/350 hours across 564 scenes and 86 tasks, while the RSS HTML abstract retains an older 65,000-trajectory count. The discrepancy is preserved because dataset version and counting source affect reproducibility. [DATA-EGO4D-2022; DATA-BRIDGEV2-2023; DATA-DROID-2024]

These scale facts do not establish interchangeable supervision. Ego4D lacks native robot motor commands; BridgeData V2 is tied to a particular low-cost platform and collection protocol; DROID adds in-the-wild scene diversity and synchronized robot sensing but retains a specific embodiment and action contract.

## Mechanism families

| Data family | Common learning use | Strength | Limitation |
|---|---|---|---|
| Internet or curated video | visual-temporal pretraining, latent actions, generative prior | scale and appearance diversity | weak intervention and physical-state labels |
| Egocentric human video | hand-object and daily activity dynamics | embodiment-relevant viewpoint and task breadth | human-to-robot action gap |
| Teleoperated robot demonstration | behavior cloning, inverse/forward dynamics | direct action-observation alignment | expensive and policy-biased coverage |
| Autonomous robot interaction/play | dynamics, exploration, recovery | broader action and failure coverage | safety, reset, and collection complexity |
| Simulator trajectory | state-rich dynamics and scalable tasks | exact state, action, and event labels | simulator and rendering gap |
| Synthetic generated media | rare scenes and controllable appearance | scalable tail coverage | generator bias and unverified physics |
| Multi-dataset embodiment mixture | generalist policy or shared world model | transfer across tasks and robots | inconsistent sensors, actions, rates, and labels |

Octo uses 800,000 trajectories from Open X-Embodiment and explicitly supports flexible observation and action spaces. Its cross-platform evaluations provide evidence that heterogeneous robot pretraining can be useful when the model and adapters account for those differences. They do not establish that raw concatenation of datasets is sufficient. [EMB-OCTO-2024]

## Design implications and trade-offs

The following are reusable synthesis patterns; their effects remain experiment-dependent.

| Lever | Mechanistic rationale | Expected signal | Regression risk | Evidence that isolates the lever |
|---|---|---|---|---|
| Domain/embodiment mixture weight | changes exposure to target and transferable dynamics | target gain with retained breadth | negative transfer or dataset shortcut | mixture matrix at fixed samples/tokens/steps |
| Temporal window distribution | changes event and credit horizon | better long-horizon prediction | fewer independent samples and more padding | horizon-stratified metrics at fixed token budget |
| Action normalization/canonicalization | exposes comparable numeric ranges and semantics | lower action error and transfer cost | hidden non-invertibility or rate mismatch | exact inverse transform and physical-unit metrics |
| Contact and transition sampling | increases rare discontinuity density | contact and manipulation accuracy | oversampling distorts overall frequency | event-stratified evaluation plus aggregate guardrail |
| Failure/recovery inclusion | supplies off-policy states and corrections | better disturbance recovery | behavior ambiguity or reduced success density | controlled perturbation and recovery curves |
| Hard counterfactual pairs | distinguishes causal response from visual prior | stronger action sensitivity | collection or simulation cost | matched context/action intervention tests |
| Language schema and verification | stabilizes task semantics | prompt adherence and compositional transfer | templating shortcut or hallucinated attributes | assertion-level audit and paraphrase split |
| Real/synthetic ratio | scales coverage while retaining reality anchor | tail gains and data efficiency | persistent real-domain regression | mixture curve on untouched real evaluation |
| Deduplication threshold | reduces memorization and split leakage | more credible transfer | removes legitimate repeated dynamics | threshold sensitivity and audited clusters |
| Multi-view packing/alignment | combines geometry and context | stronger cross-view prediction | layout identity and timestamp shortcut | held-out layout, view masking, and offset tests |

Sampling weights are part of the effective dataset. Reported raw counts do not reveal how often a source is seen after filtering, resampling, sequence packing, or curriculum. Likewise, a “data-only” conclusion is weak if optimizer, training steps, token budget, resolution, or model initialization changes simultaneously.

## Evaluation and falsification

A data intervention is interpretable when its evidence identifies:

- immutable source versions or hashes, licenses, and provenance;
- counting unit and pre/post-filter counts;
- task, scene, object, trajectory, participant, and embodiment split keys;
- deduplication representation, threshold, cluster policy, and cross-split audit;
- observation and action transformations, units, frames, normalization, and timestamp alignment;
- mixture weights before and after resampling;
- total examples, tokens, steps, resolution, frame rate, and compute;
- unchanged model and optimization variables for a data-only comparison;
- target metrics plus domain, generalization, safety, and retention slices;
- seeds or rollout counts and uncertainty of the measured difference.

The split unit matches the generalization claim. Random frame splitting is inadequate for scene, trajectory, participant, task, or embodiment generalization because adjacent frames and repeated episodes are correlated. A cross-embodiment claim requires a held-out embodiment or a target-adaptation curve; a new-object claim requires object identity isolation rather than new frames of the same object.

A scale hypothesis is falsified or narrowed when gains disappear at equal effective token exposure, arise from leakage, or fail to extend beyond near-duplicate domains. A synthetic-data hypothesis is narrowed when synthetic validation improves while untouched real-domain performance persistently regresses.

## Failure modes

- **Counting-unit confusion:** frames, clips, trajectories, and hours are compared as if equivalent.
- **Identity leakage:** the same or near-duplicate scene, trajectory, object, participant, or generated seed crosses splits.
- **Timestamp misalignment:** actions and views describe different physical moments.
- **Non-invertible action transform:** normalized outputs cannot be recovered as valid commands.
- **Dataset identity shortcut:** camera, robot, background, or language template predicts the target.
- **Long-tail deletion:** quality filtering removes failures, rare events, languages, or environments needed for robustness.
- **Synthetic monoculture:** generated data amplifies one model's artifacts or physics errors.
- **Failure-label ambiguity:** unsuccessful episodes mix perception, planning, control, and reset failures.
- **Sampling opacity:** nominal dataset composition differs from actual training exposure.
- **Mixture attribution error:** data, optimizer, steps, or checkpoint changes are bundled into one result.
- **Consent/license mismatch:** provenance or allowed use does not support the intended research artifact.

## Cross-part instantiations

- [IRASim](../../papers/irasim/paper.md) distinguishes episodes from overlapping clips and supplies a decision-use example where expert demonstrations are augmented with policy rollouts containing successes and failures; its entry owns the exact `P x K` evidence and public-data gaps.
- [Cosmos-Predict2.5](../../papers/cosmos-predict2-5/paper.md) supplies a paper-specific example of staged filtering, multi-granularity captions, semantic deduplication, domain sharding, and dataset-unit ambiguity at foundation scale.
- [LAPA](../../papers/lapa/paper.md) distinguishes unlabeled video latent-action pretraining from labeled Open-X robot finetuning.
- [iVideoGPT](../../papers/ivideogpt/paper.md) pretrains on heterogeneous OXE human and robot trajectories; checkpoint names encode action-free versus action-conditioned supervision.

- [Cosmos3-Nano data](../../models/cosmos3-nano/data.md) owns its exact pretraining, action, synthetic, and post-training mixtures and source-specific transformations.
- [Cosmos3-Nano training](../../models/cosmos3-nano/training.md) owns stage schedules, objectives, packing, and optimizer variables that interact with data.
- [Cosmos3-Nano action modeling](../../models/cosmos3-nano/action-modeling.md) owns domain action widths, normalization, and H/H+1 temporal alignment.
- [Cosmos3-Nano Policy-DROID](../../models/cosmos3-nano/policy.md) owns the checkpoint-specific DROID observation/action contract.
- [Cosmos3-Nano evaluation](../../models/cosmos3-nano/evaluation.md) records reported model results; data claims retain the associated checkpoint and protocol.
- [Paper entries](../../papers/README.md) can preserve dataset-specific collection, licenses, schema, statistics, and empirical results for Ego4D, BridgeData V2, DROID, Open X-Embodiment, and RoboCasa.

## Sources

- [DATA-EGO4D-2022] Grauman et al., *Ego4D: Around the World in 3,000 Hours of Egocentric Video*, CVPR 2022.
- [DATA-BRIDGEV2-2023] Walke et al., *BridgeData V2: A Dataset for Robot Learning at Scale*, CoRL 2023, PMLR 229:1723-1736.
- [DATA-DROID-2024] Khazatsky et al., *DROID: A Large-Scale In-The-Wild Robot Manipulation Dataset*, RSS 2024, DOI:10.15607/RSS.2024.XX.120. The RSS PDF and HTML retain different trajectory counts (76k and 65k respectively).
- [EMB-OCTO-2024] Ghosh et al., *Octo: An Open-Source Generalist Robot Policy*, RSS 2024, DOI:10.15607/RSS.2024.XX.090.
- [BENCH-ROBOCASA-2024] Nasiriany et al., *RoboCasa: Large-Scale Simulation of Household Tasks for Generalist Robots*, RSS 2024, DOI:10.15607/RSS.2024.XX.050.
