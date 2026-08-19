---
id: world-model-kb.components.reasoning
title: Reasoning for World Models
kind: component
status: maintained
last_updated: 2026-08-19
owners:
  - AIBuildAI world-model group
---

# Reasoning for World Models

## Retrieval metadata

**Relevant queries:** world-model reasoning, latent imagination, learned simulator reasoning, predictive representation, physical common sense, embodied reasoning, chain of thought for physical AI, V-JEPA 2-AC planning, Cosmos-Reason1, Cosmos3-Nano Reasoner, reasoning-to-action gap.

**Knowledge provided:** A cross-paper account of how world-model reasoning evolved from implicit latent simulation to imagined behavior learning, predictive representation, explicit physical reasoning, and coupled reasoning–generation systems; supported intervention patterns, evidence boundaries, failure diagnostics, and Cosmos3-Nano attachment points.

**Related pages:** Canonical concepts are owned by [world-model definitions](../../foundations/definitions-and-taxonomy/world-model.md), [state, observation, and belief](../../foundations/problem-formulation/state-observation-and-belief.md), [latent world models](../../foundations/representations/latent-world-model.md), [representation learning and JEPA](../../foundations/representations/representation-learning-and-jepa.md), [planning and control](../../foundations/decision-making/planning-and-control.md), and [evaluation methodology](../../foundations/data-and-evaluation/evaluation-methodology.md). Individual evidence is owned by the [DreamerV3](../../papers/dreamerv3/README.md) and [V-JEPA 2](../../papers/v-jepa-2/README.md) entries. Concrete Cosmos surfaces are owned by [Reasoner](../../models/cosmos3-nano/reasoner.md), [Generator](../../models/cosmos3-nano/generator.md), [action modeling](../../models/cosmos3-nano/action-modeling.md), and [policy](../../models/cosmos3-nano/policy.md).

## 1. Capability boundary

Reasoning in a world model is the use of a learned representation of environment state or dynamics to infer unobserved state, predict consequences, compare possible futures, or construct an explanation or plan. This operational definition deliberately spans several output surfaces while keeping them distinct.

| Surface | Canonical computation | Observable output | Evidence required |
|---|---|---|---|
| Predictive inference | \(p_\theta(z_{t+1:t+H}\mid h_t,a_{t:t+H-1},c)\) | latent or observation rollout | calibrated multi-step prediction and action sensitivity |
| Decision reasoning | \(\arg\max_{a_{t:t+H-1}}\mathbb{E}[\sum_k\gamma^k r_{t+k}]\) under a learned model | selected action sequence, value, or policy update | closed-loop return or task success under a fixed planning budget |
| Predictive representation | predict target representation \(z_y\) from context \(z_x\), optionally conditioned on actions | task-relevant embedding or latent future | transfer, probing, prediction, and downstream planning evidence |
| Explicit semantic reasoning | \(p_\phi(y\mid o_{\leq t},q,c)\) | answer, rationale, causal explanation, or text plan | task-bound answer accuracy plus tests against visual and language shortcuts |
| Executable control | \(p_\psi(a_{t:t+H-1}\mid o_{\leq t},g)\) | action tensor in a defined embodiment contract | feasibility, latency, and closed-loop success |

These surfaces can share representations but are not interchangeable. A plausible future video is not proof of counterfactual reasoning. A high-scoring text explanation is not an action tensor. A latent model that improves a policy can be useful without producing language, while a language Reasoner can describe an action without representing actuator units, control frequency, or feedback.

The historical sequence below is therefore not a single leaderboard. It tracks how different systems addressed successive bottlenecks in prediction, decision use, abstraction, physical knowledge, and interface integration.

## 2. Historical evolution

### 2.1 World Models: reasoning as compact internal simulation

**Inherited bottleneck.** Pixel-level control entangled perception, dynamics, and policy learning. Direct policy search had to discover behavior while repeatedly processing high-dimensional observations, and a deterministic predictor could not represent multiple plausible futures.

**Intervention.** World Models separated the agent into a variational autoencoder \(V\), a mixture-density recurrent network \(M\), and a small controller \(C\). The VAE compressed each frame into \(z_t\); the MDN-RNN modeled a distribution over \(z_{t+1}\) conditioned on \(z_t\), action \(a_t\), and recurrent state \(h_t\); the controller selected an action from \([z_t,h_t]\). The modules were trained separately, and the controller could be optimized inside the learned virtual environment. [FND-WORLD-MODELS-2018, Secs. 2–4; COMP-REASONING-WORLD-MODELS-PROJECT]

**Mechanism.** The recurrent state becomes a compact predictive memory, while the stochastic mixture output represents uncertainty over future latents. Controller search can reuse imagined trajectories instead of requiring every candidate behavior to be evaluated in the real environment. This is implicit reasoning: the model performs consequence simulation, but does not expose propositions, causal graphs, or natural-language rationales.

**Evidence.** On CarRacing, the full \(V\)-\(M\)-\(C\) system reported \(906\pm21\) average reward across 100 trials, compared with \(632\pm251\) for the \(V\)-only controller and \(788\pm141\) for a larger \(V\)-only controller. The comparison supports the value of predictive recurrent state under that training setup; it does not isolate every change because the controller input and learned dynamics differ together. [FND-WORLD-MODELS-2018, Table 1]

The VizDoom virtual-environment experiment exposed a more important boundary. At low sampling temperature, a controller could exploit inaccuracies in the learned model: virtual scores remained above 2,000 while actual-environment scores were below 200. Increasing temperature made the learned environment harder and reduced the gap, with the reported actual score peaking near temperature 1.15 under that protocol. [FND-WORLD-MODELS-2018, Table 2; COMP-REASONING-WORLD-MODELS-PROJECT]

**Remaining limitation.** A task-agnostic VAE may spend capacity on visually salient but decision-irrelevant details and omit small control-relevant state. Random-policy data may fail to cover states later visited by an optimized policy. Most importantly, successful reasoning inside an imperfect model can mean successful exploitation of model error. Real-environment return, uncertainty, and policy-induced distribution shift therefore become necessary evidence.

### 2.2 Dreamer: reasoning becomes behavior learning through latent imagination

**Inherited bottleneck.** World Models demonstrated controller optimization in a learned simulator, but separate module training and black-box controller search did not provide a unified, differentiable mechanism for improving behavior from imagined consequences.

**Intervention.** Dreamer used a recurrent state-space model to infer compact latent states and predict observations, rewards, and continuation. From posterior states sampled from replay, it rolled the dynamics forward under an actor and trained an actor–critic from imagined trajectories. The critic estimated long-horizon returns; the actor received gradients through the learned dynamics rather than through real environment transitions. [MBRL-DREAMER-2020, Secs. 2–3]

**Mechanism.** Imagination is coupled to a decision objective. The model is not only asked to predict the future; its latent transition, reward model, value estimate, and policy jointly form a differentiable route from possible action to expected outcome. Bootstrapped returns extend the effective reasoning horizon beyond the finite imagined rollout.

**Evidence.** The ICLR 2020 experiments reported strong visual-control results against then-current model-based and model-free baselines across multiple tasks from pixels. The transferable evidence is the demonstrated actor–critic learning loop through a latent model, not a claim that one fixed architecture or imagination horizon is universally optimal. [MBRL-DREAMER-2020, Sec. 4]

**Remaining limitation.** Both actor and critic can exploit the same biased model. Reward and termination prediction introduce additional failure surfaces, and longer imagination magnifies transition error. Reasoning quality must be judged by environment return at matched interactions and compute, not by reconstruction or imagined value alone.

### 2.3 DreamerV3: robust reasoning across heterogeneous scales and domains

**Inherited bottleneck.** Latent imagination worked, but model, reward, value, and policy losses can differ by orders of magnitude across domains. A method that requires per-domain tuning does not provide a stable reasoning substrate for broad task mixtures.

**Intervention.** DreamerV3 retained the world-model–critic–actor decomposition while adding a coordinated robustness stack: symlog transforms for large-magnitude targets, two-hot categorical prediction for reward and value, KL balancing and free bits in the world-model objective, a small uniform mixture for categorical distributions, and percentile-based return normalization. The world model, critic, and actor were trained concurrently from replay and imagined rollouts. [MBRL-DREAMERV3-2025, pp. 648–650; DV3SRC-PAPER-NATURE, Methods]

**Mechanism.** The transformations compress target scale without erasing behavior near zero; categorical two-hot losses decouple gradient magnitude from raw target magnitude; KL balance and free bits regulate posterior–prior learning without forcing the latent bottleneck to collapse; percentile normalization stabilizes policy gradients across sparse and dense reward regimes.

**Evidence.** The Nature evaluation covers more than 150 tasks across eight domains with one main configuration, aside from explicit budget and replay-ratio variations. Figure 6 reports that every robustness technique contributed on the 14-task ablation set, with KL balancing and free bits having the largest aggregate effect, followed by return normalization and symexp two-hot regression. Removing task-specific reward/value gradients or task-agnostic reconstruction gradients affected different subsets, supporting their complementarity rather than the universal dominance of either signal. [MBRL-DREAMERV3-2025, Figs. 4 and 6; DV3SRC-PAPER-NATURE, Fig. 6]

**Remaining limitation.** Robust loss scaling does not solve epistemic uncertainty, causal misidentification, or embodiment transfer. The aggregate ablation hides task-specific sign and magnitude. Reported performance also binds to each benchmark's action repeat, interaction budget, reset protocol, and evaluation conventions; it cannot be transferred to a different robot or video-model interface without a new controlled test.

### 2.4 JEPA and V-JEPA 2: reasoning through predictive abstractions rather than reconstruction

**Inherited bottleneck.** Reconstruction-based world models devote capacity to every decodable detail, even when lighting, texture, or sensor noise is irrelevant to the target decision. Pixel generation also makes multi-candidate planning expensive.

**Intervention.** Joint-embedding predictive architectures predict target representations rather than raw observations. V-JEPA 2 pretrains a video encoder and predictor through masked latent prediction on more than one million hours of video and one million images. The target encoder is an exponential-moving-average copy with stop-gradient; the predictor must infer masked target embeddings from visible spatiotemporal context. V-JEPA 2-AC then freezes the visual encoder and trains a separate 300M-parameter action-conditioned predictor on fewer than 62 hours of DROID interaction data. [OBJ-VJEPA2-2025; VJ2-PAPER, Secs. 3–4]

**Mechanism.** Predicting in representation space can discard rendering detail while retaining structure needed to anticipate events. Freezing the pretrained encoder isolates broad visual representation learning from action grounding. The action-conditioned predictor estimates future latents for candidate action sequences, and cross-entropy-method search selects actions whose predicted latents approach an image goal.

**Evidence.** The largest reported V-JEPA 2 model reached 77.3% on Something-Something-v2 and 39.7 recall@5 on Epic-Kitchens-100 under the paper's evaluation, while the action-conditioned system reported 100% average reach success and lower, task-dependent grasp and pick-place success across two laboratory setups. In the paper's Lab 2 comparison, V-JEPA 2-AC used 800 candidates and reported 16 seconds per action, whereas the compared Cosmos video world model used 80 samples, horizon one, and about four minutes per action. This supports computational promise in that setup but is not a matched universal comparison because models, candidate counts, objectives, and horizons differ. [VJ2-PAPER, Tables 1–3, Sec. 5]

**Remaining limitation.** A predictive embedding is neither a calibrated belief nor a generative explanation. V-JEPA 2-AC still depends on camera viewpoint, image goals, short-horizon search, and embodiment-specific action data. Autoregressive latent rollout can drift, and candidate search grows rapidly with horizon. The result supports a representation-to-planning bridge, not zero-shot action control from passive video alone.

### 2.5 Cosmos-Reason1: explicit physical common sense and embodied reasoning

**Inherited bottleneck.** Latent simulators and predictive representations can support control, but their internal computations are difficult to query for explicit spatial, temporal, physical, and embodied judgments. General vision-language models may recognize scenes while lacking focused supervision for physical consequences and interaction constraints.

**Intervention.** Cosmos-Reason1 post-trained vision-language backbones using a Physical AI curriculum. The current report revision defines two main stages: Physical AI supervised fine-tuning followed by Physical AI reinforcement learning. Its data ontology separates physical common sense—space, time, and fundamental physics—from embodied reasoning over sensory processing, action effects, physical constraints, interaction learning, and embodiment. The report describes roughly four million video–text annotations produced through a mixture of model distillation and human annotation. [R1-TR, pp. 6–15]

The 7B system is based on Qwen2.5-VL; the 56B system uses a larger hybrid Mamba–MLP–Transformer language backbone. Reinforcement learning applies group relative policy optimization with exact-answer and format rewards for multiple-choice reasoning, using nine sampled outputs per question under the reported configuration. [R1-TR, pp. 15, 20]

**Mechanism.** Structured supervision makes latent physical relations externally queryable as language. Reinforcement learning emphasizes answer correctness and response format beyond imitation of the supervised traces. This expands the reasoning surface from implicit prediction to explicit, inspectable judgments and plans.

**Evidence.** For the 7B model, supervised fine-tuning raised the reported physical-common-sense average from 47.4 to 54.3 and the embodied-reasoning average from 50.8 to 61.8 relative to the named Qwen2.5-VL-7B baseline. Across the report's combined evaluation, the RL stage raised the average from 60.7 to 65.7, but individual datasets were not uniformly improved; for example, HoloAssist decreased from 63 to 60 while other rows improved. The intuitive-physics aggregate rose from 42.1 for the base model to 74.5 after SFT and 81.5 after RL under the paper's protocol. [R1-TR, Tables 4, 8–10]

**Remaining limitation.** The reward verifies multiple-choice answer and format, not an executable trajectory or calibrated physical simulation. Language rationales can use dataset priors, and benchmark accuracy can remain high under shortcuts unless counterfactual visual tests remove them. A text plan must still be grounded into embodiment-specific actions and validated through feedback.

### 2.6 Cosmos 3: coupling explicit reasoning with generative and action prediction

**Inherited bottleneck.** Explicit Reasoners and generative world models were often separate systems. The Reasoner could describe a future without generating it; the Generator could produce a plausible future without an explicit semantic account; action models used still another interface.

**Intervention.** Cosmos 3 introduces a mixture-of-transformers architecture with paired autoregressive and diffusion parameter streams. The Nano checkpoint comprises an approximately 8B autoregressive Reasoner tower and an approximately 8B diffusion Generator tower. Autoregressive tokens include language and visual-context tokens; diffusion subsequences represent continuous vision, audio, and action latents. Diffusion queries can attend to both autoregressive and diffusion context, while autoregressive queries attend only to the autoregressive stream. [C3-TR, pp. 8–13; Fig. 3]

The Reasoner is initialized from Qwen3-VL-8B and trained for multimodal understanding and reasoning. The Generator uses rectified-flow objectives and supports media generation as well as forward-dynamics, inverse-dynamics, and joint world-action modes under distinct input/output contracts. [C3-TR, pp. 25–30, 55–69]

**Mechanism.** A shared sequence and attention interface lets semantic autoregressive context condition continuous diffusion generation without collapsing both objectives into one tokenization or loss. The model can therefore connect a language-level representation of intent or physical relations to predicted media and actions while retaining modality-specific generation.

**Evidence.** The report evaluates the Reasoner on multimodal understanding and physical-reasoning suites, the Generator on image/video/audio quality, and action-specialized checkpoints on separate control or action-generation protocols. Those results demonstrate multiple capabilities in one model family; they do not establish that every capability is present in the base Nano checkpoint under every backend, nor that improvement in one tower causally transfers to the other. [C3-TR, pp. 31–69]

**Remaining limitation.** The attention path is asymmetric: current diffusion states do not update the autoregressive Reasoner's current hidden state. A semantic plan can condition generation, but generator feedback does not automatically revise the plan within the same forward process. Base world-action generation is not a controller, and the separately post-trained Policy-DROID checkpoint has its own observation, action, timing, and embodiment contract. Text planning, media prediction, joint action generation, and closed-loop policy success must remain separate evaluation surfaces.

## 3. Evolution summary

| Stage | Representation of the world | Reasoning operation | Primary improvement | Evidence surface | Unresolved boundary |
|---|---|---|---|---|---|
| World Models | compressed stochastic recurrent latent | simulate controller trajectories | separates perception, dynamics, and compact control | real-versus-virtual return | model exploitation and data coverage |
| Dreamer | recurrent latent state with reward and continuation | actor–critic learning through imagined futures | couples prediction to behavior improvement | environment return at fixed interactions | shared model/value bias |
| DreamerV3 | robust categorical latent and scale-normalized targets | same imagination loop across heterogeneous domains | reduces loss-scale and tuning fragility | multi-domain return and ablations | uncertainty and transfer remain |
| V-JEPA 2 / 2-AC | predictive visual embeddings plus action-conditioned latent predictor | latent goal search | avoids reconstructing every pixel and reuses passive video representations | probes, planning success, and latency | viewpoint, horizon, and action grounding |
| Cosmos-Reason1 | VLM representations with physical and embodied language supervision | explicit answer, explanation, and text plan | exposes physical relations and interaction knowledge | benchmark accuracy and SFT/RL deltas | shortcuts and language-to-action gap |
| Cosmos 3 | coupled autoregressive and diffusion streams | semantic conditioning of media/action generation | integrates reasoning, prediction, and action surfaces | component-specific benchmark suites | asymmetric coupling and closed-loop proof |

The progression is compositional rather than substitutive. Explicit language reasoning does not make latent simulation obsolete; a predictive representation does not remove the need for uncertainty; and an omnimodal architecture does not remove embodiment-specific action grounding.

## 4. Supported intervention patterns

### 4.1 Match the reasoning representation to the decision variable

**Cross-source synthesis.** World Models and Dreamer show that a compact latent can support control, while V-JEPA 2 shows that reconstruction-free predictive embeddings can support goal-conditioned search. Cosmos-Reason1 shows a different requirement: explicit physical questions benefit from language-addressable representations. [FND-WORLD-MODELS-2018; MBRL-DREAMER-2020; VJ2-PAPER; R1-TR]

The supported rule is conditional: preserve information needed by the downstream decision, not every observable detail and not only semantic detail. A candidate representation should be tested with matched probes for controllable state, multi-step prediction, and downstream utility. Reconstruction quality alone cannot decide between representations.

### 4.2 Couple predictive learning to consequence-sensitive evidence

World Models' virtual-versus-real gap, Dreamer's environment-return loop, and V-JEPA 2-AC's action-conditioned planning all show that passive prediction metrics are insufficient for decision claims. [FND-WORLD-MODELS-2018, Table 2; MBRL-DREAMER-2020; VJ2-PAPER, Sec. 5]

A reasoning intervention is better supported when action counterfactuals change predicted outcomes in the correct direction and when those predictions improve real or simulator-ground-truth decisions under a matched compute budget. This does not imply that every model should be trained end to end on reward; task-agnostic representation and task-specific signals can be complementary, as DreamerV3's gradient ablations indicate. [MBRL-DREAMERV3-2025, Fig. 6]

### 4.3 Treat robustness techniques as an interacting system

DreamerV3's losses work together: target transforms, categorical prediction, KL regulation, distribution smoothing, and return normalization address different numerical instabilities. The evidence does not support copying one coefficient in isolation into a different architecture. [DV3SRC-PAPER-NATURE, Fig. 6 and Methods]

A transferable test keeps the target task, representation, update ratio, and compute fixed, then measures both aggregate improvement and task-wise regressions. If an intervention helps only when another normalization is present, the interaction is part of the mechanism.

### 4.4 Separate broad representation learning from action grounding

V-JEPA 2 pretrains visual prediction at large scale, then freezes the encoder while learning the action-conditioned predictor from a much smaller interaction set. This establishes a clean attribution boundary between passive-video representation and action grounding. [VJ2-PAPER, Secs. 3–4]

The broader hypothesis is that a reusable perceptual predictor can reduce the interaction data needed for a target embodiment. It remains false unless a matched from-scratch or frozen-feature baseline shows improved sample efficiency without losing action sensitivity.

### 4.5 Use explicit physical supervision for explicit reasoning claims

Cosmos-Reason1's ontology, SFT gains, and subsequent RL gains support targeted physical and embodied supervision for answerable reasoning tasks. The non-uniform per-dataset changes show that aggregate improvement can hide regressions. [R1-TR, Tables 4 and 8–10]

For explicit reasoning, useful evidence includes taxonomy-balanced evaluation, visual counterfactuals, rationale faithfulness tests, and transfer to held-out objects, scenes, and embodiments. Multiple-choice reward alone cannot validate causal simulation or executable control.

### 4.6 Preserve interface boundaries in unified systems

Cosmos 3 demonstrates a technical route for sharing context between autoregressive reasoning and diffusion generation. The transfer hypothesis is that better semantic state can improve conditional generation or action prediction. The architecture makes this plausible because diffusion queries attend to autoregressive context, but it does not prove transfer. [C3-TR, Fig. 3]

Evidence requires an ablation that changes the Reasoner signal while holding Generator weights, sampling budget, and input conditions fixed, then measures condition adherence, physical consistency, action feasibility, and closed-loop outcome separately. A simultaneous update of both towers cannot attribute the gain.

## 5. Failure modes and discriminating measurements

| Observable failure | Competing causes | Measurement that separates them |
|---|---|---|
| High imagined value, low realized return | model exploitation, reward-model bias, policy OOD actions | uncertainty versus error by policy distance; real-versus-imagined return on identical action sequences |
| Good one-step prediction, poor long rollout | compounding transition error, posterior dependence, memory loss | horizon-conditioned calibration and state error under open-loop and replanned control |
| Strong text accuracy, implausible counterfactual answer | language shortcut, missing visual grounding, dataset leakage | matched visual counterfactual pairs and answer change sensitivity |
| Coherent rationale, failed action execution | missing action units/frame, infeasible plan, feedback delay | action-schema validation, kinematic feasibility, closed-loop stage success, latency |
| Strong reconstruction, weak planning | irrelevant-detail capacity, missing reward/control state | task-state probes and matched planning return at equal model compute |
| Strong representation probe, weak control | linear separability without predictive action structure | action-conditioned latent error and candidate-ranking regret |
| Reasoner improvement without Generator gain | unused semantic signal, attention bottleneck, sampler variance | frozen-Generator conditioning ablation with fixed seeds and denoising budget |
| Aggregate benchmark gain with hidden regressions | task-mixture weighting or reward misalignment | per-category deltas, confidence intervals, and worst-slice performance |

## 6. Current research directions

### Calibrated reasoning under multimodal futures

Latent imagination, text answers, and diffusion samples all face multiple valid futures. A useful system should distinguish aleatoric diversity from epistemic uncertainty and propagate both into value or action selection. Multisample coverage, calibration, and decision regret are complementary measurements; a single most-likely rationale or rollout is insufficient.

### Bidirectional reasoning–generation refinement

Cosmos 3 conditions diffusion on autoregressive context but does not provide same-step diffusion-to-Reasoner feedback. An open architectural question is whether iterative exchange—reason, generate or simulate, inspect discrepancy, revise—improves physical consistency enough to justify latency and training complexity. The discriminating evidence is a controlled comparison with the same parameters or compute, not merely an additional refinement pass.

### Action-grounded semantic reasoning

Explicit plans need a typed action language with coordinate frames, units, duration, control rate, gripper semantics, and feedback conditions. Mapping text or abstract latent goals to executable actions should preserve feasibility and uncertainty rather than collapse to one nominal command. Success must be measured on held-out tasks and embodiments, not only plan similarity.

### Decision-aware predictive representation

Reconstruction-free prediction can remove nuisance detail, but can also remove small control-critical features. A promising direction combines predictive representation with task-state, contact, reward, or controllability objectives while preserving broad transfer. The key test is Pareto improvement across transfer, action sensitivity, and closed-loop performance.

### Causal and counterfactual physical reasoning

Observational video contains correlations among actions, camera motion, and outcomes. Reasoning about interventions requires either action-labeled data, controlled perturbations, strong structural assumptions, or combinations of them. Matched endpoint trajectories with different actions, object-property interventions, and held-out causal mechanisms provide stronger evidence than random frame splits.

## 7. Cosmos3-Nano attachment map

This map links component-level knowledge to concrete model surfaces. It identifies plausible mechanisms and required evidence; it does not define an experiment schedule.

| Cosmos3-Nano surface | Component insight | Testable attachment hypothesis | Required evidence |
|---|---|---|---|
| Reasoner SFT data | explicit physical reasoning responds to targeted, balanced supervision | increase counterfactual and failure-recovery examples while preserving general VLM data | category-balanced held-out accuracy, shortcut tests, and regression matrix |
| Reasoner post-training | answer/format reward can improve exact tasks but regress slices | process, consistency, or verifier signals may improve robustness beyond terminal MCQ reward | controlled reward ablation with per-dataset deltas and rationale-faithfulness tests |
| AR context to Generator | semantic state can condition continuous future prediction | expose structured object, relation, and subgoal representations in the AR stream | frozen-Generator conditioning ablation and fixed-seed media/action metrics |
| Generator forward dynamics | decision reasoning requires action-sensitive consequence prediction | add counterfactual action pairs or task-state auxiliaries | matched-action sensitivity, horizon error, calibration, and planning gain |
| Joint world-action mode | internal video/action agreement can still be shared hallucination | consistency objectives may help only if grounded by realized transitions | replay consistency, feasibility, ranking regret, and closed-loop success |
| Policy-DROID | executable control requires its own embodiment interface | reuse Reasoner or Generator features only through an explicit action adapter | action-contract validation, latency, held-out task/scene success, and safety events |

The model-specific [optimization playbook](../../models/cosmos3-nano/optimization-playbook.md) owns concrete experiment contracts, while [research queue](../../models/cosmos3-nano/research-queue.md) owns live unresolved model questions. This Component supplies cross-paper reasoning knowledge only.

## 8. Open questions

1. Which representation retains the minimum information needed for physical decision-making while remaining reusable across tasks and embodiments?
2. How should a model calibrate confidence when several physically valid futures or plans exist?
3. Which reasoning gains come from stronger visual dynamics, and which come from language priors or benchmark format?
4. Can passive-video predictive pretraining reduce action-labeled data needs without weakening counterfactual action sensitivity?
5. When does longer imagination improve decisions, and when does it amplify model exploitation?
6. Does explicit intermediate reasoning improve Cosmos3-Nano generation or action prediction once sampling compute and parameter count are controlled?
7. What feedback interface lets generated futures revise semantic plans without unacceptable latency?
8. Which offline metrics best predict closed-loop failure recovery rather than only nominal-task success?

These are scientific uncertainties. Their presence does not imply task priority or authorize changes to AIBuildAI workflow.

## 9. Sources and evidence boundaries

- [FND-WORLD-MODELS-2018] owns the archival World Models paper identity; [COMP-REASONING-WORLD-MODELS-PROJECT] is the official interactive companion.
- [MBRL-DREAMER-2020] and [MBRL-DREAMERV3-2025] own the Dreamer and DreamerV3 paper identities; the [DreamerV3 paper entry](../../papers/dreamerv3/paper.md) owns detailed architecture and benchmark interpretation.
- [OBJ-VJEPA2-2025] and [VJ2-PAPER] identify the V-JEPA 2 preprint at Foundation and Paper-entry scope; the [V-JEPA 2 paper entry](../../papers/v-jepa-2/paper.md) owns variant-specific evidence.
- [R1-TR] identifies Cosmos-Reason1 report v3. Earlier revisions described different model sizes and training structure; claims here bind to the locally verified v3 artifact.
- [C3-TR] identifies Cosmos 3 report v4. The [Cosmos3-Nano model entry](../../models/cosmos3-nano/README.md) owns exact checkpoint, interface, training, benchmark, and execution facts.

Chronology and architectural similarity do not establish causal improvement. Every numerical result on this page remains bound to its named model, dataset, protocol, and output surface.
