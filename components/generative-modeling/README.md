---
id: world-model-kb.components.generative-modeling
title: Generative Modeling for World Models
kind: component
status: maintained
last_updated: 2026-08-19
owners:
  - AIBuildAI world-model group
---

# Generative Modeling for World Models

## Retrieval metadata

**Relevant queries:** generative world model, autoregressive video prediction, diffusion world model, latent diffusion, diffusion Transformer, flow matching, rectified flow, interactive simulator, action-conditioned generation, Cosmos-Predict2.5, Cosmos3-Nano Generator, temporal consistency, physical fidelity.

**Knowledge provided:** A cross-paper reconstruction of how generative world modeling evolved from recurrent and autoregressive prediction through diffusion, latent compression, Transformer scaling, flow matching, interactive video models, and Cosmos omnimodal generation; supported design patterns, trade-offs, failure diagnostics, and Cosmos3-Nano attachment points.

**Related pages:** Canonical concepts are owned by [video world models](../../foundations/representations/video-world-model.md), [latent world models](../../foundations/representations/latent-world-model.md), [autoregressive modeling](../../foundations/learning-objectives/autoregressive-modeling.md), [diffusion and flow matching](../../foundations/learning-objectives/diffusion-and-flow-matching.md), [actions and interventions](../../foundations/problem-formulation/actions-and-interventions.md), [forward dynamics](../../foundations/problem-formulation/forward-dynamics.md), and [evaluation methodology](../../foundations/data-and-evaluation/evaluation-methodology.md). Individual evidence is owned by the [iVideoGPT](../../papers/ivideogpt/README.md), [IRASim](../../papers/irasim/README.md), [DIAMOND](../../papers/diamond/README.md), and [Cosmos-Predict2.5](../../papers/cosmos-predict2-5/README.md) entries. Concrete Cosmos surfaces are owned by [Generator](../../models/cosmos3-nano/generator.md), [action modeling](../../models/cosmos3-nano/action-modeling.md), and [training](../../models/cosmos3-nano/training.md).

## 1. Capability boundary

A generative world model learns a conditional distribution over future environment-relevant variables:

\[
p_\theta(y_{t+1:t+H}\mid h_t,\;u_{t:t+H-1},\;c),
\]

where history \(h_t\) may contain observations, latent state, language, audio, or proprioception; \(u\) may be an action, camera trajectory, goal, or another intervention; \(c\) denotes additional context; and \(y\) may be future pixels, video latents, audio, actions, rewards, occupancy, or a joint output.

Three properties must be kept separate:

1. **Distribution modeling:** generated samples cover the conditional data distribution.
2. **World-dynamics validity:** samples preserve state, time, object identity, physical events, and intervention effects across a rollout.
3. **Decision utility:** generated futures improve planning, policy learning, or control under a fixed compute and interaction budget.

An image generator can satisfy the first property without representing dynamics. A visually convincing video can fail the second. A physically reasonable rollout can still be too slow, poorly calibrated, or misaligned with actions to satisfy the third. Generative modeling becomes a world-model component only when its conditioning, temporal contract, and predicted variables support an environment-relevant transition or simulation claim.

## 2. Historical evolution

### 2.1 Recurrent and autoregressive prediction: factorize the future

**Inherited bottleneck.** Directly predicting high-dimensional futures requires a tractable factorization and a representation that can carry temporal context. Deterministic regression collapses multiple possible futures toward a conditional average.

**Intervention.** Early learned world models compressed observations and predicted the next latent recurrently. World Models used an MDN-RNN to model a mixture distribution over the next VAE latent conditioned on the current latent, action, and hidden state. Later discrete-video systems factorized token likelihood autoregressively:

\[
p_\theta(x_{1:N}\mid c)=\prod_{i=1}^{N}p_\theta(x_i\mid x_{<i},c).
\]

The token sequence can include compressed video, actions, rewards, or goals, allowing a single causal Transformer to express several conditional tasks. [FND-WORLD-MODELS-2018, Secs. 2–4; IVG-PAPER, Secs. 3–4]

**Mechanism.** Compression reduces the prediction dimension; recurrent or causal state summarizes history; stochastic output heads represent more than one next state. Teacher-forced maximum likelihood gives a stable local objective and a normalized conditional distribution for discrete tokens.

**Evidence.** World Models showed that a stochastic recurrent latent could support controller training, while iVideoGPT later showed that an autoregressive video tokenizer and Transformer could reuse action-free pretraining for action-conditioned prediction, visual planning, and model-based reinforcement learning. In the BAIR comparison reported by iVideoGPT, adding action conditioning changed FVD from 75.0 to 60.8 for the named model and protocol, indicating that the conditioning signal materially affected future prediction. [FND-WORLD-MODELS-2018; IVG-PAPER, Tables 1–2]

**Remaining limitation.** Autoregressive decoding is serial, and train-time teacher forcing exposes the model to ground-truth prefixes that are unavailable in long open-loop rollout. Tokenizer errors and early sampling errors propagate. The likelihood factorization does not itself ensure action sensitivity, physical correctness, or task utility.

### 2.2 Denoising diffusion: model multimodal data through iterative refinement

**Inherited bottleneck.** Autoregressive generation accumulates ordered token errors and imposes a serial factorization; adversarial generators can be difficult to train and may lose modes. High-dimensional continuous data still has a complex multimodal distribution.

**Intervention.** Denoising diffusion probabilistic models define a fixed forward process that gradually adds Gaussian noise and a learned reverse process that denoises:

\[
q(x_t\mid x_0)=\mathcal{N}(\sqrt{\bar{\alpha}_t}x_0,(1-\bar{\alpha}_t)I).
\]

The widely used simplified objective trains a network to predict the added noise at sampled timesteps. Sampling integrates the learned reverse process from noise to data through many model evaluations. [OBJ-DDPM-2020, Secs. 2–4]

**Mechanism.** Instead of predicting the whole multimodal distribution in one step, the model learns local denoising fields across noise levels. Parameter sharing across timesteps and a simple regression objective provide stable optimization, while stochastic reverse trajectories can produce diverse samples.

**Evidence.** The original DDPM reported CIFAR-10 FID 3.17 and Inception Score 9.46 under its protocol, together with high sample quality but likelihood below the strongest likelihood models of that period. The result established denoising diffusion as a competitive generative family; it did not establish temporal consistency or world-model utility. [OBJ-DDPM-2020, Sec. 4 and Table 1]

**Remaining limitation.** Iterative denoising is expensive. Pixel-space training spends compute on rendering detail, and image FID does not measure long-horizon state, action response, or control. Extending diffusion to video adds temporal scale and consistency problems rather than solving them automatically.

### 2.3 Latent diffusion and DiT: move generation into compressed space and scale the backbone

**Inherited bottleneck.** Pixel diffusion repeatedly evaluates a large network in a high-dimensional observation space. A convolutional U-Net provides useful image priors but does not expose the same straightforward depth, width, and token scaling axes as a Transformer.

**Intervention 1 — latent diffusion.** Latent diffusion first trains an autoencoder, then applies diffusion to a lower-dimensional latent. Cross-attention injects text, spatial layouts, or other conditions into the denoiser. The codec introduces an explicit rate–distortion choice: stronger compression lowers compute but can remove fine or task-relevant information. [COMP-GEN-LDM-2022, Secs. 3–4]

**Evidence.** The CVPR study reports at least 2.7-fold training/sampling efficiency improvement for matched pixel- versus latent-based variants in the analyzed setting and shows that moderate spatial compression can preserve high image quality. These are image-generation findings; they do not determine the correct compression for contact, small-object state, or robot control. [COMP-GEN-LDM-2022, Sec. 4 and Tables 8–9]

**Intervention 2 — diffusion Transformer.** DiT replaces the U-Net denoiser with a Transformer operating on patches of a latent spatial representation. Depth, width, and patch size change forward-pass compute; adaptive layer normalization provides class and timestep conditioning. [COMP-GEN-DIT-2023, Secs. 3–4]

**Evidence.** Under the paper's class-conditional ImageNet protocol, larger DiT forward-pass Gflops—obtained through greater depth, width, or token count—correlated with lower FID. DiT-XL/2 reported FID 2.27 at 256×256 with classifier-free guidance. Conditioning-block ablations favored adaptive layer normalization with zero initialization for the tested architecture. [COMP-GEN-DIT-2023, Figs. 2–8 and Tables 1–2]

**Remaining limitation.** Codec loss and denoiser capacity trade off against each other; more Transformer compute can improve an image metric while leaving temporal memory or action causality unchanged. The DiT scaling result binds to class-conditional image generation and cannot be treated as proof that a larger video DiT is a better world model.

### 2.4 Flow matching and rectified flow: learn continuous transport fields

**Inherited bottleneck.** Diffusion objectives and samplers involve a chosen noise process, parameterization, and often many reverse evaluations. The relation between training path and efficient deterministic transport can be indirect.

**Intervention.** Flow matching trains a continuous normalizing flow by regressing a vector field associated with a chosen probability path, without simulating the learned ordinary differential equation during training. For a straight interpolation,

\[
x_\sigma=(1-\sigma)x_0+\sigma\epsilon,\qquad
v^\star=\epsilon-x_0,
\]

and the network regresses \(v_\theta(x_\sigma,\sigma,c)\) toward the target velocity. Diffusion paths are members of the broader conditional flow-matching family. Rectified flow emphasizes learning straighter transports between paired endpoint distributions; reflow can further straighten trajectories. [OBJ-FLOW-MATCHING-2023, Secs. 2–4; OBJ-RECTIFIED-FLOW-2023, Secs. 2–3]

**Mechanism.** A straighter probability path can be integrated accurately with fewer solver steps, while direct vector-field regression avoids backpropagating through ODE trajectories during training. The path, coupling, weighting, solver, and guidance remain independent design choices.

**Evidence.** In matched CIFAR-10 and ImageNet experiments from the Flow Matching paper, the optimal-transport path achieved favorable FID, likelihood, and function-evaluation trade-offs relative to the compared diffusion paths; the paper also reports lower numerical error at a given evaluation budget for its selected settings. Rectified Flow reports that reflow produces straighter trajectories and improves few-step generation in its experiments. [OBJ-FLOW-MATCHING-2023, Tables 1–3 and Figs. 4–6; OBJ-RECTIFIED-FLOW-2023, Secs. 4–5]

**Remaining limitation.** “Flow” does not imply one-step generation, perfect invertibility, or universal speed. Solver order, step count, path curvature, guidance, latent codec, and hardware determine latency and quality. An efficient image transport does not establish temporally coherent or action-causal video.

### 2.5 Interactive and action-conditioned video models: turn generation into a transition surface

The next stage did not introduce one universal architecture. It attached controls, actions, rewards, or policy learning to several generative families.

| Work | Generative mechanism | Exact intervention | Supported improvement | Remaining boundary |
|---|---|---|---|---|
| UniSim | conditional latent video diffusion over heterogeneous real-world data | unifies actions such as robot controls, camera motion, and text through task-specific conditioning | reported interactive simulation and selected policy/planning transfer across several domains | heterogeneous controls are not one action ontology; selected transfer is not universal simulator validity |
| iVideoGPT | compressive conditional VQ tokenizer plus causal Transformer | action-free video pretraining followed by action-, goal-, or reward-conditioned adaptation | BAIR action-conditioned FVD improvement and downstream VP2/MBRL demonstrations | serial rollout, dataset-specific action spaces, no universal OXE action-conditioned checkpoint |
| IRASim | latent diffusion Transformer with frame-level action modulation | aligns each action segment with its corresponding future-frame latent inside every block | improved action-conditioned robot-rollout quality and reported Push-T candidate-planning IoU under its protocol | released implementation/protocol gaps, external value model, large data/checkpoint cost |
| DIAMOND | pixel-space EDM-style diffusion inside an RL world model | retains visual details rather than relying on aggressive latent compression | Atari 100k mean human-normalized score 1.459 and ablations showing denoising-step sensitivity | not overall best on every aggregate, expensive rollout, visual detail benefit is environment-dependent |

[WFM-UNISIM-2024; IVG-PAPER, Sec. 4; IRASRC-PAPER-V2, Secs. 3–4; DIASRC-PAPER, Secs. 3–4]

**Cross-source synthesis.** Action conditioning is not merely another prompt. It must bind a control value to a time interval, coordinate frame, embodiment, and predicted effect. iVideoGPT demonstrates reuse of passive-video pretraining, IRASim emphasizes frame-level action alignment, UniSim emphasizes heterogeneous control interfaces, and DIAMOND demonstrates that discarded visual detail can matter for an RL agent. Together they motivate measuring action counterfactuals and decision utility, but they do not identify a universally best objective or representation.

**Remaining limitation.** A model can generate internally consistent action and video pairs that are jointly wrong. Planning can exploit generator error just as controllers exploited early latent simulators. Ground-truth replay, independent state/contact measurements, and closed-loop outcomes remain necessary.

### 2.6 Cosmos-Predict2.5: large-scale latent flow video foundation modeling

**Inherited bottleneck.** Research systems often specialized in one direction—text-to-video, image-conditioned continuation, or action-conditioned prediction—and used small, domain-specific datasets. High-resolution physical-AI video requires scalable data filtering, conditioning, and resolution curricula.

**Intervention.** Cosmos-Predict2.5 combines a causal video autoencoder, a diffusion Transformer trained with flow matching, and a Cosmos-Reason1 text encoder. A clean-prefix formulation replaces noise on conditioning frames with exact latent context, allowing Text2World, Image2World, and Video2World within one model family. Training progresses across task mix and resolution, followed by domain supervised fine-tuning, model merging, reward post-training, and distillation for named variants. [P25-TR, pp. 6–14]

The report describes filtering more than six billion candidate clips to roughly 200 million curated clips. It also reports that drawing 5% of training samples from the highest 2% of noise levels reduced abrupt transitions between conditioning frames and generated frames. This is a direct example of changing the time/noise sampling distribution to target an observed boundary artifact. [P25-TR, pp. 8–10]

**Mechanism.** Latent flow lowers spatial-temporal compute; clean prefixes make the condition an exact boundary rather than a partially noised target; high-noise oversampling trains difficult global transitions; progressive resolution and domain adaptation separate broad generative learning from specialist refinement.

**Evidence.** The report evaluates base and post-trained variants on physical-AI video benchmarks and presents robot, driving, multiview, and action-conditioned specialist applications. Each result belongs to its named checkpoint and protocol. The [paper entry](../../papers/cosmos-predict2-5/paper.md) preserves the exact result tables, code-release mismatch, and application boundaries. [P25-TR, pp. 15–39]

**Remaining limitation.** Reward optimization, merging, distillation, and action-conditioned specialists are not all released as one reproducible path. Perceptual and preference metrics remain imperfect proxies for physical state and decision utility. Predict2.5 concepts inform Cosmos 3 lineage, but its weights, architecture, and results are not Cosmos3-Nano facts.

### 2.7 Cosmos 3: omnimodal rectified-flow generation with action modes

**Inherited bottleneck.** A video-only generator cannot natively share semantic reasoning, audio, and action representations. Separate models also duplicate context processing and complicate alignment across output modalities.

**Intervention.** Cosmos 3 uses a mixture-of-transformers design with an autoregressive stream for language and visual context and a diffusion stream for continuous media and actions. The Nano Generator is an approximately 8B diffusion tower within the approximately 16B Reasoner-plus-Generator checkpoint. Diffusion queries attend to both autoregressive and diffusion tokens. The training objective uses rectified-flow interpolation with modality masks and time sampling, while task-specific input/output schemas expose image, video, audio, forward-dynamics, inverse-dynamics, and joint world-action modes. [C3-TR, pp. 8–13, 27–30, 55–69]

**Mechanism.** Modality-specific continuous latents avoid forcing audio, video, and actions into one discrete vocabulary. Autoregressive semantic context can guide diffusion outputs, and joint attention lets continuous modalities condition one another. Separate parameter streams preserve different objectives while sharing sequence-level context.

**Evidence.** The report provides component-specific media, physical-reasoning, action, and policy evaluations. This establishes an integrated family and several post-training surfaces, not one universal score for “world-model quality.” Base Generator, action-specialized modes, and Policy-DROID must remain variant-specific. [C3-TR, pp. 31–69]

**Remaining limitation.** The model does not document a persistent explicit 3D state, calibrated world uncertainty, or a guarantee that samples obey interventions. Generator latency and peak memory vary by workload, backend, resolution, duration, denoising steps, and parallelism. Joint output is not closed-loop control evidence, and media quality cannot substitute for replayed action consistency.

## 3. Evolution summary

| Stage | Distribution parameterization | Representation | Conditioning advance | Main gain | Principal cost or risk |
|---|---|---|---|---|---|
| Recurrent / autoregressive | next-state mixture or causal token likelihood | VAE latent or discrete tokens | action and history in recurrent/causal state | tractable normalized sequence model | serial error accumulation |
| DDPM | learned reverse noising process | pixels or continuous data | timestep plus optional condition | stable multimodal generation | many evaluations and pixel cost |
| Latent diffusion | diffusion in autoencoder latent | compressed continuous latent | cross-attention conditions | lower compute at useful quality | codec may remove control detail |
| DiT | diffusion with latent-patch Transformer | compressed patches | adaptive normalization or cross-attention | scalable backbone and compute axis | image evidence does not prove dynamics |
| Flow / rectified flow | continuous transport vector field | pixel or latent | arbitrary conditional field | flexible paths and potential few-step sampling | path/solver sensitivity |
| Interactive video WMs | AR, diffusion, or flow with temporal/action interfaces | token, pixel, or latent video | timed action, goal, camera, reward | simulation, planning, or policy-learning surface | model exploitation and interface mismatch |
| Cosmos-Predict2.5 | latent flow-matching DiT | causal video VAE latent | clean prefix and task/resolution curriculum | scalable multi-task physical-AI video | specialist and release fragmentation |
| Cosmos 3 | omnimodal rectified flow coupled to AR context | modality-specific video/audio/action latents | semantic and cross-modal joint attention | one family for media and action modes | variant boundaries, compute, and unproven causality |

No row dominates every axis. Autoregressive models provide exact causal factorization but serial decoding; diffusion and flow provide flexible continuous generation but iterative integration; latent compression saves compute but can discard small state; pixel generation retains detail at high cost. The target decision and measurement contract determine the useful trade-off.

## 4. Supported intervention patterns

### 4.1 Choose compression by task information, not reconstruction alone

Latent diffusion demonstrates a major compute advantage from moderate compression, while DIAMOND provides evidence that visual details discarded by common latent models can matter for Atari control. [COMP-GEN-LDM-2022; DIASRC-PAPER, Sec. 4]

**Cross-source synthesis.** Codec selection is a Pareto problem over compute, perceptual fidelity, temporal state, contact/small-object information, and decision utility. Useful tests compare codec variants with identical dynamics capacity, then measure reconstruction, rollout state error, action sensitivity, and downstream success. A lower reconstruction FID does not prove a better control latent.

### 4.2 Make the condition path temporally and semantically explicit

iVideoGPT's action-conditioned delta, IRASim's frame-level action modulation, Predict2.5's clean prefix, and Cosmos 3's mode-specific schemas all show that the condition interface is a core model mechanism. [IVG-PAPER, Tables 1–2; IRASRC-PAPER-V2, Sec. 3; P25-TR, pp. 8–11; C3-TR, pp. 55–69]

The condition contract includes source timestamp, effect interval, coordinate frame, units, missing-value behavior, masking, and attention path. If changing an action does not produce the corresponding state change while all other inputs remain fixed, generic sample quality cannot rescue the world-model claim.

### 4.3 Match time/noise sampling to observed failure regions

Predict2.5's reported high-noise oversampling targets abrupt condition-to-generation transitions. Flow and diffusion theory likewise make timestep or path sampling an explicit training distribution. [P25-TR, pp. 8–10; OBJ-FLOW-MATCHING-2023, Sec. 4]

The transferable pattern is to stratify errors by noise/time region, change sampling weight without changing model/data, and verify improvement at the target boundary together with regression metrics. Copying the 5%/2% values without reproducing the failure distribution is unsupported.

### 4.4 Scale architecture only after binding the evidence surface

DiT reports monotonic image-FID improvement with forward-pass compute across its tested family. Video foundation models similarly benefit from greater data and capacity, but temporal horizon, resolution, and conditioning expand compute differently. [COMP-GEN-DIT-2023, Figs. 2–8]

**Cross-source synthesis.** Scaling is interpretable only with fixed data, optimizer, training steps, sampler, guidance, and evaluation budget. For world models, scaling evidence must include horizon-conditioned dynamics and action tests; an image-only scaling curve is a useful architecture prior, not a world-model law.

### 4.5 Optimize sampler and training path as a coupled system

Flow matching and rectified flow show that path geometry affects numerical integration. DIAMOND shows that reducing denoising steps can materially degrade agent performance even when generation remains operational. [OBJ-FLOW-MATCHING-2023; OBJ-RECTIFIED-FLOW-2023; DIASRC-PAPER, Table 4]

Inference steps, solver order, guidance, stochasticity, and distillation should be compared at fixed latency or function-evaluation budgets. A faster sampler is useful only if physical events, diversity, action response, and downstream utility remain within declared tolerances.

### 4.6 Separate broad pretraining from intervention grounding

iVideoGPT, UniSim, Predict2.5, and Cosmos 3 use broad video/media data, while action-conditioned or policy behavior depends on smaller, more structured interaction data and explicit adapters. [WFM-UNISIM-2024; IVG-PAPER; P25-TR; C3-TR]

The plausible transfer mechanism is broad visual-dynamics coverage plus efficient target-domain grounding. Evidence requires a matched scratch-versus-pretrained comparison, controlled action data, held-out scenes or embodiments, and tests that the model changes correctly under counterfactual actions. Passive-video scale alone cannot establish intervention semantics.

## 5. Failure modes and discriminating measurements

| Observable failure | Plausible causes | Discriminating measurement |
|---|---|---|
| Sharp frames, wrong object state | perceptual objective dominates task state; codec loses small state | object/contact/state transition metrics at matched perceptual score |
| Correct short clip, identity drift later | weak memory, rollout exposure gap, tokenizer aliasing | horizon-conditioned identity and state consistency |
| Samples ignore action | alignment bug, conditioning dropout, insufficient counterfactual data | matched histories with swapped actions and effect-direction score |
| One plausible future, poor coverage | low sample diversity, guidance collapse, deterministic decoder | best-of-\(N\) coverage, calibration, and diversity at fixed fidelity |
| Good FID/FVD, poor planning | metric mismatch, reward/state error, model exploitation | candidate-ranking regret and realized closed-loop outcome |
| Good teacher-forced prediction, poor open loop | exposure gap or posterior leakage | open-loop versus filtered/replanned rollout error |
| Faster sampling, worse control | insufficient solver steps or distillation loss of rare events | latency–success and latency–event-fidelity Pareto curve |
| Joint video/action agreement, failed execution | shared hallucination or invalid action schema | replay transition consistency, feasibility, and controller feedback |
| Better aggregate score, rare-event regression | mixture weighting or evaluator insensitivity | event-stratified metrics and worst-slice confidence intervals |

## 6. Current research directions

### Decision-relevant generative objectives

Pixel likelihood, denoising loss, and flow regression optimize data fit, not directly planning value. One direction adds task-state, contact, reward, value, or controllability signals while retaining broad generative coverage. The central risk is overspecialization: a task-aware latent may improve one benchmark while losing reusable environmental structure.

### Long-horizon memory and persistent state

Video latents can mix physical state, camera motion, and rendering. Persistent object, geometry, or belief representations may reduce identity drift and occlusion failures. The relevant evidence is not only novel-view or reconstruction quality, but state persistence through long occlusion, camera change, and action intervention.

### Efficient uncertainty-aware sampling

Few-step flow and distilled samplers reduce latency, while planning requires diverse, calibrated candidate futures. A useful sampler should allocate compute to uncertain or decision-critical branches rather than producing many redundant samples. Compare coverage and decision regret at equal wall-clock and memory budgets.

### Joint media–action modeling without shared hallucination

Joint models can regularize actions through predicted consequences and vice versa, but both heads may agree on an incorrect future. Independent replay, dynamics constraints, and realized transitions are needed to ground consistency. Counterfactual action pairs and failure/recovery episodes are especially informative.

### Heterogeneous data mixtures with explicit provenance

Internet video, robot trajectories, driving logs, synthetic simulations, and generated data differ in observation, action, camera, and success semantics. Mixture weighting should operate on documented units and failure slices rather than only dataset names. Deduplication, leakage checks, synchronization, and provenance become part of the model mechanism because they change the learned conditional distribution.

### Reasoning-conditioned generation and iterative verification

Autoregressive semantic context can guide a diffusion generator, as in Cosmos 3, but the reliability of the semantic-to-continuous interface remains open. Structured state, subgoal, or physical-relation tokens may improve adherence; generated futures may in turn serve as counterexamples for revising reasoning. Controlled bidirectional refinement must be compared at fixed compute.

## 7. Cosmos3-Nano attachment map

This map translates the historical synthesis into model-specific hypotheses and evidence requirements. It does not schedule or authorize experiments.

| Cosmos3-Nano surface | Component insight | Testable attachment hypothesis | Required evidence |
|---|---|---|---|
| Media tokenizer / VAE | compression can save compute or erase control-relevant state | adjust codec capacity or add state/contact preservation signals | rate–distortion, task-state probes, rollout error, and latency |
| Rectified-flow time sampling | difficult path regions can dominate visible artifacts | reweight time/noise regions identified by error stratification | fixed-model sampling ablation and region-specific plus global regressions |
| Generator attention | explicit condition paths determine controllability | strengthen temporal/action alignment or structured AR conditions | swapped-condition counterfactuals and attention-independent outcome tests |
| Video curriculum | scale helps only under controlled mixture and resolution | rebalance event, duration, domain, or resolution buckets | fixed-update data ablation with held-out dynamics slices |
| Sampler / solver | few-step latency trades against fidelity and coverage | tune or distill under a fixed real-time budget | latency–quality–coverage–decision Pareto frontier |
| Forward dynamics | generation becomes a world model through interventions | add task-state or action-consistency supervision | action sensitivity, horizon calibration, replay, and planning gain |
| Joint WAM | paired video/action output may regularize both surfaces | couple losses while preserving typed action adapters | action feasibility, video/action counterfactual agreement, closed-loop success |
| Reasoner-to-Generator context | semantic structure may improve physical adherence | expose object, relation, or subgoal representations to the diffusion stream | frozen-Generator or frozen-Reasoner attribution test with fixed samples |

Exact target-model variables and controlled experiment records belong to the [optimization playbook](../../models/cosmos3-nano/optimization-playbook.md), [training](../../models/cosmos3-nano/training.md), [evaluation](../../models/cosmos3-nano/evaluation.md), and [research queue](../../models/cosmos3-nano/research-queue.md). This Component owns the cross-paper mechanism lineage.

## 8. Open questions

1. Which information should a world-model codec preserve when pixel quality and control utility disagree?
2. How can a generator distinguish uncertainty about the world from harmless visual diversity?
3. What action-conditioning test best detects observational shortcuts before closed-loop deployment?
4. Can few-step flow models retain rare contact, collision, and failure events at real-time latency?
5. When does explicit 3D or object state outperform implicit video latents at a matched compute budget?
6. How should passive video, action-labeled trajectories, synthetic rollouts, and failures be mixed without hiding provenance or leakage?
7. Does joint action/video generation improve causal grounding, or mainly increase internal agreement?
8. Which offline metric most reliably predicts planning gain and closed-loop recovery for long-horizon generation?
9. Can reasoning-conditioned generation improve physical consistency without reducing diversity or increasing shortcut dependence?

These questions describe unresolved knowledge. They do not assign priority, select an Agent, or define AIBuildAI workflow.

## 9. Sources and evidence boundaries

- [COMP-GEN-LDM-2022] and [COMP-GEN-DIT-2023] are Component-owned paper identities for latent diffusion and DiT because those objects were not previously registered elsewhere.
- [OBJ-DDPM-2020], [OBJ-FLOW-MATCHING-2023], and [OBJ-RECTIFIED-FLOW-2023] resolve through the Foundation source registry and own the general objective lineage.
- [WFM-UNISIM-2024] resolves through Foundations. [IVG-PAPER], [IRASRC-PAPER-V2], and [DIASRC-PAPER] resolve through their Paper entries, which own the detailed protocols and code boundaries.
- [P25-TR] identifies Cosmos-Predict2.5 report v2; its [Paper entry](../../papers/cosmos-predict2-5/paper.md) owns architecture, results, release gaps, and specialist boundaries.
- [C3-TR] identifies Cosmos 3 report v4; the [Cosmos3-Nano model entry](../../models/cosmos3-nano/README.md) owns exact model, checkpoint, interface, training, benchmark, and execution facts.

Image metrics, video metrics, prediction likelihood, physical-event accuracy, action sensitivity, planning utility, and closed-loop success test different claims. No result on this page may be transferred across those surfaces without the missing measurement.
