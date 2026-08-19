---
id: world-model-kb.foundations.learning-objectives.diffusion-and-flow-matching
title: Diffusion and Flow Matching
kind: concept
status: maintained
last_updated: 2026-08-19
owners:
  - AIBuildAI world-model group
---

# Diffusion and Flow Matching

## Retrieval metadata

**Relevant queries:** diffusion world model, DDPM, score model, reverse SDE, probability-flow ODE, flow matching, rectified flow, conditional generation, guidance, or diffusion video.

**Knowledge provided:** diffusion and continuous-flow formulations, distinctions between flow matching and rectified flow, optimization/sampling levers, and tests for conditional dynamics and downstream rollout quality.

**Related pages:** [Video world models](../representations/video-world-model.md) covers the predicted observation surface; [latent world models](../representations/latent-world-model.md) covers codec and state choices; [autoregressive modeling](autoregressive-modeling.md) covers ordered likelihood factorization; the [Generative Modeling Component](../../components/generative-modeling/README.md) owns the cross-paper historical synthesis.

## Definition and formalism

Diffusion models learn to reverse a gradual corruption process. In a variance-preserving discrete process,

```text
q(x_t | x_0) = Normal(sqrt(alpha_bar_t) x_0,
                      (1 - alpha_bar_t) I),
L_epsilon = E[t,x_0,epsilon] ||epsilon - epsilon_theta(x_t,t,c)||^2.
```

Equivalent or related parameterizations predict noise, clean data, score, or a velocity-like target. The reverse process can be expressed as a stochastic chain, a reverse-time SDE, or a probability-flow ODE under the corresponding score model. These surfaces differ in solver, stochasticity, and likelihood/sample trade-offs. [OBJ-DDPM-2020; OBJ-SCORE-SDE-2021]

Flow matching trains a time-dependent vector field for an ODE

```text
dx_t / dt = v_theta(x_t,t,c).
```

For a simple straight conditional path `x_t=(1-t)x_0+t epsilon`, one target is

```text
u_t = epsilon - x_0,
L_FM = E ||v_theta(x_t,t,c) - u_t||^2.
```

The endpoint convention can be reversed, and general flow matching supports other conditional probability paths. `Rectified flow` is a particular straightening/reflow approach, not a synonym for every flow-matching method. Exact interpolation, parameterization, weighting, and masking should be taken from the model implementation. [OBJ-FLOW-MATCHING-2023; OBJ-RECTIFIED-FLOW-2023]

## Assumptions and scope

Diffusion and flow objectives define how a conditional distribution is learned and sampled; they do not determine whether its variables form a world state, whether conditioning is causal, or whether rollouts are calibrated. The generated variable can be pixels, video latents, actions, trajectories, occupancy, or a joint multimodal tensor.

Training generally observes corrupted/interpolated versions of real targets. Autonomous world-model deployment additionally feeds generated outcomes into later context, creating a distribution shift not measured by single-sample denoising loss. A high-quality one-shot video distribution can still have inconsistent transitions over repeated closed-loop use.

## Objective and sampler families

| Family | Learned quantity | Sampling surface | Main trade-off |
|---|---|---|---|
| Discrete diffusion | reverse transition or noise | iterative stochastic/deterministic steps | flexible density, many evaluations |
| Score-SDE model | score over noise time | reverse SDE or probability-flow ODE | unified continuous view, solver sensitivity |
| Latent diffusion | noise/score in codec latent | decode after denoising | reduced cost, codec information loss |
| Video diffusion | spatiotemporal denoising | joint or factorized video sample | temporal memory and large tensors |
| Flow matching | continuous vector field | ODE integration | direct regression, path/solver dependence |
| Rectified flow | straightened transport field | few- or multi-step ODE | potentially efficient paths, reflow/data coupling |
| Joint action-media denoising | coupled heterogeneous variables | joint or clamped conditional sample | loss scaling and semantic alignment |

The original diffusion formulation, DDPM, score-SDE framework, video diffusion models, flow matching, and rectified flow establish these related but non-identical constructions. [OBJ-DIFFUSION-2015; OBJ-DDPM-2020; OBJ-SCORE-SDE-2021; OBJ-VIDEO-DIFFUSION-2022; OBJ-FLOW-MATCHING-2023; OBJ-RECTIFIED-FLOW-2023]

## Design implications and trade-offs

Core levers include data/noise/velocity parameterization, time or noise-level sampling, loss weighting, conditional dropout, guidance strength, codec resolution, temporal masks, action injection, and sampler family, step count, and tolerance. These levers interact: a model trained under one time weighting can regress when sampled with a solver optimized for another error profile.

Classifier-free guidance often improves conditional adherence at the cost of diversity and calibration; its effect should be measured for action and state variables separately. Fewer solver steps reduce latency but can alter high-frequency detail, rare events, and action-future consistency. Joint action-video training requires scale normalization and per-modality diagnostics because high-dimensional video residuals can dominate sparse action variables.

For world-model use, training horizon, context refresh, and repeated rollout are at least as important as per-sample fidelity. DIAMOND provides evidence that diffusion-generated visual details can affect learned behavior, but that result does not imply that every perceptual improvement yields better control. [REP-DIAMOND-2024]

## Evaluation and falsification

- Compare objectives and samplers at matched model, data, conditioning, wall-clock, and network-evaluation budgets.
- Report quality, diversity, conditional adherence, calibration, and solver step count.
- Evaluate one generated horizon and repeated free-running rollout separately.
- Perturb actions or goals while fixing initial noise where appropriate to test conditional sensitivity.
- Stratify denoising and decoded errors by time, modality, event type, and small task-relevant structures.
- Replay generated or selected actions in an independent environment when control utility is claimed.

A diffusion-world-model claim is weakened when strong metrics require best-of-N selection unavailable to the downstream agent, when conditioning changes style but not physical consequence, or when repeated rollouts drift despite good single clips. A rectified-flow efficiency claim should be narrowed if fewer steps reduce latency but degrade action accuracy, diversity, or task success.

## Failure modes

- **Sample-quality substitution:** perceptual quality is treated as evidence of physical or control accuracy.
- **Solver mismatch:** the deployed discretization differs from the vector field's reliable regime.
- **Guidance distortion:** stronger conditioning collapses diversity or creates overconfident artifacts.
- **Codec bottleneck:** latent generation cannot restore details absent from the encoder.
- **Temporal inconsistency:** individually sharp frames violate identity, contact, or geometry.
- **Action-media imbalance:** shared loss or normalization privileges the visual branch.
- **Train-rollout mismatch:** denoising real targets does not prepare the model for generated context.
- **Step-budget confounding:** quality comparisons use different numbers of network evaluations.
- **Terminology collapse:** diffusion, probability-flow ODE, flow matching, and rectified flow are treated as interchangeable.

## Cross-part instantiations

- [Cosmos-Predict2.5](../../papers/cosmos-predict2-5/paper.md) instantiates straight-interpolation velocity matching, shifted time sampling, and low-step distillation; the paper entry owns the exact objective and rCM-versus-public-DMD2 boundary.
- [DIAMOND](../../papers/diamond/paper.md) instantiates image-space diffusion as a world model for Atari MBRL; CSGO-branch sampling is a separate surface.
- [Vista](../../papers/vista/paper.md) instantiates a high-resolution controllable driving video diffusion model whose official weights include a corrected `vista.safetensors` upload.
- [Cosmos Policy](../../papers/cosmos-policy/paper.md) keeps the Predict2 DiT unchanged and injects actions, proprioception, and values as latent frames.

- [Cosmos3-Nano Generator](../../models/cosmos3-nano/generator.md) owns its exact rectified-flow interpolation, masked loss, conditioning, and sampler; the generic equations above do not replace that contract.
- [Training](../../models/cosmos3-nano/training.md) records checkpoint-specific time sampling, masking, modality balancing, and post-training objectives.
- [Action modeling](../../models/cosmos3-nano/action-modeling.md) identifies whether actions are conditions, generated targets, or joint variables.
- [Evaluation](../../models/cosmos3-nano/evaluation.md) should report solver and sample budgets; [limitations](../../models/cosmos3-nano/limitations.md) owns unsupported rollout and control claims.
- [Paper entries](../../papers/README.md) retain objective derivations and implementation-specific conventions.

## Sources

- [OBJ-DIFFUSION-2015] Sohl-Dickstein et al., *Deep Unsupervised Learning using Nonequilibrium Thermodynamics*, ICML 2015, PMLR 37.
- [OBJ-DDPM-2020] Ho, Jain, and Abbeel, *Denoising Diffusion Probabilistic Models*, NeurIPS 2020, arXiv:2006.11239.
- [OBJ-SCORE-SDE-2021] Song et al., *Score-Based Generative Modeling through Stochastic Differential Equations*, ICLR 2021, OpenReview:PxTIG12RRHS.
- [OBJ-VIDEO-DIFFUSION-2022] Ho et al., *Video Diffusion Models*, NeurIPS 2022, arXiv:2204.03458.
- [OBJ-FLOW-MATCHING-2023] Lipman et al., *Flow Matching for Generative Modeling*, ICLR 2023, OpenReview:PqvMRDCJT9t.
- [OBJ-RECTIFIED-FLOW-2023] Liu, Gong, and Liu, *Flow Straight and Fast: Learning to Generate and Transfer Data with Rectified Flow*, ICLR 2023, OpenReview:XVjTT1nw5z.
- [REP-DIAMOND-2024] Alonso et al., *Diffusion for World Modeling: Visual Details Matter in Atari*, NeurIPS 2024, DOI:10.52202/079017-1873.
- [C3-TR] NVIDIA, *Cosmos 3: Omnimodal World Models for Physical AI*, arXiv:2606.02800.
