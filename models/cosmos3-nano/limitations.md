---
id: world-model-kb.models.cosmos3-nano.limitations
title: Cosmos3-Nano Failure Modes and Optimization Guardrails
kind: reference
status: maintained
last_updated: 2026-08-11
owners:
  - AIBuildAI world-model group
---

# Cosmos3-Nano Failure Modes and Optimization Guardrails

## Retrieval metadata

**Relevant queries:** known limitation, model-card risk, failure taxonomy, metric proxy, unsupported extrapolation, regression risk, safety evidence, or deployment uncertainty.

**Knowledge provided:** documented capability boundaries, observable failure signatures, evaluation confounders, transfer risks, and evidence gaps. Risk descriptions are informational and do not define AIBuildAI policy.

**Related pages:** [Evaluation](evaluation.md) contains benchmark scores; [Training](training.md) contains optimizer state; [Post-training](post-training.md) contains recipes; [Reproduction](reproduction.md) contains execution observations. [Open problems](../../foundations/research-frontiers/open-problems.md) owns the cross-model unresolved conditions behind field-level limitations.

## 1. Model-card failure envelope

The Cosmos 3 report has no standalone limitations section, so distinguish direct model-card warnings from boundaries inferred from protocols and results. Earlier Cosmos failure modes are useful test generators but are not automatically observed Cosmos3-Nano facts.

### 1.1 Reasoner

The model card warns that Reasoner may misunderstand object state, causal relations, spatial geometry, temporal order, agent intent, and future outcomes. Long contexts and out-of-distribution inputs can increase hallucinated entities and internally inconsistent explanations. Its output is visually conditioned language, not a calibrated physical-state estimator; fluent reasoning, points, or waypoints do not guarantee executability. [C3-HF, "Limitations"]

Highest-risk probes include:

- object permanence under occlusion;
- identity correspondence after camera or viewpoint change;
- pre-contact versus post-contact causality;
- metric 3D geometry and reference-frame conversion;
- failure detection and recovery planning;
- ambiguity with several physically plausible futures;
- grounded plan steps whose target point is unreachable or collision-prone.

The 48-benchmark average is a distributional summary and does not remove per-example failure risk. [C3-TR, pp.51–53]

### 1.2 Generator

The model card lists temporal inconsistency, unstable camera/object motion, imprecise physical interaction, audio-video desynchronization, and action-state drift. Risk increases with duration, resolution, scene complexity, and contact-rich motion. Cosmos3-Nano is not an explicit physics simulator; 3D geometry, 4D evolution, object permanence, contact dynamics, and physical laws are learned approximations. [C3-HF, "Limitations"]

Observable signatures include object disappearance or deformation, drifting contact points, implausible collision response, hand/tool geometry failure, deviation from camera or spatial control, sound-event timing errors, and disagreement between executed action and generated state. Treat generated media as candidate rollouts, never as ground-truth dynamics.

## 2. Capability-boundary register

| Surface | Known boundary | Claim that must be rejected |
|---|---|---|
| General reasoning | Nano General average 69.6, only +0.7 over Qwen3-VL-8B and below Gemini 3.1 Pro | “Cosmos3-Nano dominates all 48 benchmarks” [C3-TR, pp.51–53] |
| Driving Reasoner | Driving average uses LingoQA and two small internal classifiers | “+29.6 applies to general driving intelligence” [C3-TR, p.53] |
| Scene text | Base Nano CVTG-500L GNED/PNED 24.23/26.53; Chinese 4.63/9.70 | “UniGenBench 84.61 implies reliable text rendering” [C3-TR, p.55, Table 11] |
| Video physics | Physics-IQ direct I2V 40.2, V2V 50.2; best-of-N spends extra inference | “Generated video obeys real physical laws” [C3-TR, p.58, Table 13] |
| Human motion | Competitive HUE/HWB but model card still warns of long-horizon geometry/physics instability | “Hands, contact, and long-horizon motion are solved” [C3-TR, pp.59–60; C3-HF, "Limitations"] |
| Audio | SAV 8.35 versus PQ 6.32 | “Good synchronization implies artifact-free sound” [C3-TR, pp.61–62] |
| Transfer | PAIBench-C tests one control at a time; AVBench-C includes internal data and judges | “Any combination of native controls is reliable” [C3-TR, pp.63–64] |
| Forward dynamics | PSNR compares to one recorded future | “25.52 dB predicts closed-loop task success” [C3-TR, pp.65–67] |
| Policy | RoboLab specific overall 39.7%; complex-specific 29.4% | “Leaderboard rank means complex manipulation is solved” [C3-TR, p.68, Table 19] |

Optimization must target a named failure bucket and retain independent guardrails. An aggregate improvement does not close a failure class unless that class is directly measured.

## 3. Data and supervision risks

### 3.1 Incomplete reconstruction surface

The report exposes curriculum scale, selected sources, filtering architecture, and some thresholds, but not full source manifests, internal driving/egocentric/surveillance logs, the 47-class visual hierarchy, every threshold, judge/captioner prompts, final shards, or exact sampling budgets. Proprietary action data includes 41.3K egocentric hours and 10K AV hours. [C3-TR, pp.20–25]

Implication: public checkpoints and Framework support inference and downstream adaptation, but not bitwise or data-equivalent foundation retraining. Dataset-name equality does not establish equivalence when scene slicing, deduplication, captioning, failure/idle policy, and sampling weights differ.

**Guardrail:** every data-based claim must carry an immutable manifest and state the missing reconstruction fields. Do not label a foundation run “replicated” when only the public recipe shape matches.

### 3.2 Automated-filter error propagation

Reasoner filtering composes embedding models, K-means, and Gemma-4-31B judging. Generator filtering uses an internal VLM, DOVER/VTSS, and Qwen captioners. Audio filtering adds source separation, ASR, lip synchronization, and instrument detection. Each stage can bias language, visual style, geography, embodiment, motion, or failure types. [C3-TR, pp.15–17, 20–24]

The report gives aggregate retention but not false-positive/false-negative rates across demographics, language, embodiment, or failure class. Blurring identifiable people in the dense-pedestrian subset is a specific privacy measure, not proof of equivalent privacy, copyright, and bias audits across all data. [C3-TR, p.19]

**Guardrail:** audit pre-filter and post-filter distributions, label precision/recall, and subgroup retention. Stop if coverage loss or bias is material and unaccounted for.

### 3.3 Synthetic-data shift and negative transfer

All individual SDG variants and SDG-All reduce the PAIBench-G Human score. SDG-RobotSim lowers AV by 1.03 and Industry by 1.22; SDG-PhyxSim lowers AV by 1.42. SDG-All yields small positive movement on 8/9 metrics but Human remains -0.47. [C3-TR, pp.104–105, Table 26]

**Guardrail:** pair synthetic tails with real-data anchors and run per-domain regressions. Reject a synthetic-data intervention when target gain is dominated by real-domain or safety-critical degradation, even if the aggregate is positive.

### 3.4 Action canonicalization discards dynamics

Robotics converts states to pseudo-actions by differencing and normalizes each dimension to approximately `[-1,1]`. This avoids private PID interfaces but removes torque, controller latency, compliance, and actuator dynamics. Source frame rate, synchronization, and failure semantics may also differ. [C3-TR, pp.24–25]

Cross-domain action tokens enable transfer but not a universally optimal mixture. Pairwise synergies include both positive transfer and interference; joint PushT training improves inverse dynamics and policy coverage while lowering forward-dynamics PSNR. [C3-TR, pp.70–72, 109, Figures 28–29 and Table 31]

**Guardrail:** preserve invertible transforms, original units/frame/rate, controller metadata, and per-embodiment metrics. Never compare normalized MSE without denormalized physical error.

## 4. Evaluation confounders

### 4.1 Prompt rewriting changes the evaluated system

T2I uses Claude Opus 4.7; video and audio-video primarily use Claude Opus 4.6 to rewrite prompts into structured JSON. The upsampler may add visual, temporal, or cinematographic details absent from the raw request. Scores therefore measure `rewriter + Cosmos3 + sampler`. [C3-TR, pp.53–56, 61, 73]

**Guardrail:** freeze and archive raw prompt, rewritten prompt, rewriter version, template, and failure policy. For action tasks, reject rewrites that insert oracle state or change task semantics.

### 4.2 Judge dependence and unavailable components

Reasoner evaluation includes internal HealthSurgiBench and driving classifiers. PAIBench-G Domain, UniGenBench, SoundBench, and AVBench-C use model judges; HUE questions are generated by GPT 5.2 with human augmentation. Judge version, prompt, API drift, and stochasticity can change scores. [C3-TR, pp.51–64]

The paper could not reproduce the public PAIBench-G I2V leaderboard judged by Qwen3-VL-235B-A22B and instead reports Qwen2.5-VL-72B-Instruct. Benchmark names alone do not establish comparability. [C3-TR, p.57, footnote 2]

**Guardrail:** bind every score to the actual judge. Run a human or second-judge audit when the effect approaches judge variance or changes sign across judges.

### 4.3 Proxy metrics are not target outcomes

- DOVER, aesthetics, and HPS emphasize perceptual quality, not temporal or physical validity.
- PSNR may penalize plausible stochastic futures and reward blur; it is not policy success.
- Edge/depth/segmentation metrics measure the Generator together with a re-extractor.
- HUE treats `Unclear` as failure but remains limited by question coverage.
- Best-of-N spends extra inference and cannot be mixed with direct single-sample results. [C3-TR, pp.56–64, 110]

**Guardrail:** maintain a metric ladder from cheap proxy to direct capability to closed-loop outcome. Optimize a proxy only after validating its correlation with the target in the intended domain.

### 4.4 Leaderboard state is temporal

Artificial Analysis T2I/I2V snapshots dated 2026-05-28 belong to Super specialists. RoboArena and MolmoSpaces snapshots dated 2026-05-30 and 2026-06-20 belong to Policy-DROID. Participants, votes, and protocols change. [C3-TR, pp.56, 59–60, 68–70]

**Guardrail:** store date, submission, protocol, and raw outputs. Never use “currently best” as a model property or checkpoint-selection criterion.

## 5. Training, system, and deployment risks

### 5.1 Foundation-scale cost

Nano Generator pre-training reports 31.05T tokens on 1,024 GB200 GPUs; mid-training reports 2.4T tokens on 1,024 GB200 GPUs. Public recipe execution does not imply foundation-scale reproducibility. [C3-TR, pp.29–30]

The report conflicts on throughput-benchmark GPU count: p.45 states Nano/Super used 1,024/2,048 GB200 GPUs; the p.46 Table 8 caption states 2,048/4,096. Preserve both until an authoritative correction exists. [C3-TR, pp.45–46, Table 8]

**Guardrail:** compare optimization efficiency in tokens, accelerator-hours, wall-clock, and target quality. Do not compare steps alone across sequence lengths, resolutions, or hardware.

### 5.2 “Nano” is not a lightweight full-stack deployment

Nano MoT totals about 16B parameters: approximately 8B Reasoner plus 8B Generator towers. Loaded components depend on the task path. Full Generator, long video, CFG, VAE, and multimodal caches require materially more memory than Reasoner-only serving. Policy-DROID's reported deployment uses two RTX Pro 6000 GPUs. [C3-TR, pp.13–14, 32, Table 2; C3-REASONER-COOKBOOK]

Hosted Reasoner availability, local BF16 checkpoint loading, full Generator memory, policy deployment, and foundation-training GPU count are different resource claims.

**Guardrail:** measure peak memory, TTFT, steady latency, tail latency, throughput, and output quality for the exact task mode. Do not transfer hardware claims across surfaces.

### 5.3 Robot safety remains external

Policy-DROID emits 32 absolute joint-position actions and delegates execution to a Franky controller. The report does not guarantee collision checking, joint-limit enforcement, human-proximity handling, timeout, emergency stop, or uncertainty calibration. [C3-TR, pp.31–32]

**Guardrail:** require external action bounds, rate limits, collision checks, watchdog, recoverable stop, uncertainty/fallback logic, and human override for physical deployment. Generated video and Reasoner rationale cannot replace this layer.

### 5.4 License and service terms have distinct scope

The fixed HF checkpoint and Reasoner service card identify OpenMDW-1.1. Hosted Generator materials separately reference the NVIDIA Open Model License and API Trial Terms. Downloading weights, calling a preview API, distributing derivatives, and processing inputs/outputs may have different conditions. [C3-HF, "License"; C3-REASONER-CARD, "License and Terms of Use"; C3-GENERATOR-CARD, "License"; C3-SYSTEM-CARD, "Governing Terms"]

**Guardrail:** bind each artifact or service to its applicable terms and recheck them before distribution or production use. Do not collapse them into one unscoped “Cosmos 3 license.”

## 6. Lineage boundaries

- Cosmos-Reason1 uses SFT plus GRPO. Cosmos 3 reports Reasoner pre-training plus SFT; do not insert GRPO into Nano without code/config confirmation. [R1-TR, pp.15, 20; C3-TR, pp.25–27]
- Cosmos-Transfer1/2.5 uses per-control ControlNet/adapter paths; Cosmos 3 uses native control tokens. Earlier adapter weights and limitations are not hidden Nano components. [T1-TR, pp.4–8; C3-TR, p.63]
- Cosmos-Predict2.5 provides a lineage for flow matching, clean prefix, and multiresolution training, but Cosmos 3 adds MoT, audio/action, and a native Reasoner–Generator interface. Predict2.5 results are not Nano results. [P25-TR, pp.6–11; C3-TR, pp.8–13]
- First-generation Cosmos WFM failures in object permanence, contact dynamics, gravity, and fluids are useful probes. Until observed under a fixed Nano protocol, label them hypotheses rather than Nano failures. [C1-TR, p.58]

## 7. Target-domain transfer risks

No public Cosmos3-Nano result establishes performance on every embodied benchmark. DROID, RoboLab, LIBERO, and a target domain such as RoboCasa differ in embodiment, camera topology, action space, control rate, instruction style, horizon, and success definition.

| Shift | Failure signature | Required test before optimization claim |
|---|---|---|
| Observation | Occlusion, texture, view-count, or camera-layout mismatch | Per-view stress tests and canonical-layout control |
| Action semantics | Absolute joints versus delta EEF, gripper conventions, controller differences | Invertible action-contract test and denormalized errors |
| Temporal | 15 Hz and 32-step chunks mismatch target control/replan horizon | Rate/horizon ablation with equal real-time coverage |
| Task composition | Short instructions do not transfer to long compositional tasks | Horizon- and subtask-stratified closed-loop success |
| Metric | Reasoning, PSNR, or DROID success may not predict target success/recovery | Correlation study plus target rollouts |
| Safety | Simulator-valid commands can still violate limits/collisions/timeouts | Safety-wrapper test and adversarial termination cases |

Optimization on a shifted target is not interpretable until observation/action invariants pass. Testable transfer questions are registered in [research-queue.md](research-queue.md), while reusable procedures are owned by [optimization-playbook.md](optimization-playbook.md).

## 8. Failure-to-intervention map

| Observed failure | First diagnostic | Candidate lever | Mandatory guardrail |
|---|---|---|---|
| Hallucinated object or state | Grounding trace and image-region audit | hard negatives, grounding SFT, confidence calibration | General VQA/OCR retention |
| Wrong temporal order | Event-boundary and frame-rate audit | temporal contrastive data, longer windows, FPS encoding | Static-image reasoning |
| Plausible text plan, invalid waypoint | Geometry/frame and reachability check | executable-grounding data, planner verification | collision/reachability rejection |
| Object/contact drift in video | contact-frame and horizon slices | contact-rich real data, temporal/action conditioning | visual quality and non-contact domains |
| Action-state inconsistency | action frame/rate/normalization invariant test | joint FD/policy objective, auxiliary future RGB | action accuracy and closed-loop success |
| Synthetic-domain artifact | nearest-source and style classifier audit | lower synthetic weight, real replay, style randomization | real-domain target and subgroup metrics |
| Good offline action, poor rollout | latency, compounding error, and observation mismatch | receding-horizon tuning, recovery data, uncertainty gate | safety wrapper and timeout |
| Good aggregate, weak rare domain | per-domain confusion and sampling audit | domain-aware sampling or hard-example retrieval | aggregate/general regression budget |

## 9. Minimum risk-validation contract

Before accepting an optimization or deployment, record:

1. target model surface, checkpoint/code revision, input/output contract, and intended operating domain;
2. ranked failure classes with severity, likelihood, detectability, and affected users/assets;
3. direct tests for each critical failure, including distribution shifts, horizon, occlusion, contact, ambiguity, and adversarial inputs;
4. immutable baseline protocol, target metrics, general-retention gates, subgroup/domain slices, physical/safety gates, latency, and compute;
5. raw and rewritten prompts, judge identity, seed/rollout budget, failure artifacts, and uncertainty/fallback behavior;
6. observation/action invariance tests, denormalization, controller bounds, safety-wrapper tests, and emergency-stop behavior for policy use;
7. data lineage, leakage audit, automated-filter audit, license/terms mapping, and privacy review;
8. explicit unsupported claims and unresolved source conflicts;
9. acceptance, rollback, and stop thresholds declared before viewing candidate results.

## 10. Evidence and deployment-risk signals

The following conditions weaken an optimization claim or create deployment risk:

- a critical failure has no direct test or external safeguard;
- an aggregate gain hides a predeclared safety-critical, subgroup, domain, or long-horizon regression;
- a result depends on changed prompt rewriting, judge, best-of-N budget, or checkpoint-selection policy;
- action units/frame/rate, camera layout, temporal synchronization, or normalization is ambiguous;
- synthetic or filtered data introduces unresolved real-domain regression or bias;
- a proxy improves without stable correlation to the intended closed-loop outcome;
- uncertainty, fallback, action limits, collision handling, watchdog, or emergency stop is missing for physical control;
- train/evaluation leakage or proprietary-data scope is unresolved;
- resource or latency limits are exceeded for the intended surface;
- applicable license, service, privacy, or distribution terms are unresolved;
- repeated controlled trials fail to reproduce the effect or effect size falls below the declared practical threshold.

## 11. Related knowledge ownership

- Exact metric protocols, baselines, conflicts, and ablations are owned by [evaluation.md](evaluation.md).
- Data composition, filtering, normalization, and leakage controls are owned by [data.md](data.md).
- Training objectives, optimizer state, and compute accounting are owned by [training.md](training.md).
- Adaptation branches and public SFT execution are owned by [post-training.md](post-training.md).
- Policy I/O, serving, receding horizon, and runtime safety integration are owned by [policy.md](policy.md).
- Unresolved research questions are registered in [research-queue.md](research-queue.md), while reusable optimization strategies are owned by [optimization-playbook.md](optimization-playbook.md).
- Actual run state and produced artifacts are owned by [reproduction.md](reproduction.md).
- Source IDs and fixed revisions resolve through [sources.yaml](sources.yaml).
