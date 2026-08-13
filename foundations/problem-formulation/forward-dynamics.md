---
id: world-model-kb.foundations.problem-formulation.forward-dynamics
title: Forward Dynamics
kind: reference
status: maintained
last_updated: 2026-08-13
owners:
  - AIBuildAI world-model group
---

# Forward Dynamics

## Retrieval metadata

**Relevant queries:** forward dynamics, action-conditioned prediction, transition model, future prediction, rollout, latent dynamics, stochastic dynamics, model error, or action sensitivity.

**Knowledge provided:** controlled-transition formalisms, observation and latent modeling alternatives, training and data levers, and tests that distinguish useful action-conditioned dynamics from visually plausible continuation.

**Related pages:** [State, observation, and belief](state-observation-and-belief.md) defines hidden-state semantics; [inverse dynamics](inverse-dynamics.md) defines action inference from transitions; [planning and control](../decision-making/planning-and-control.md) and [model-based RL](../decision-making/model-based-rl.md) cover downstream model use.

## Definition and formalism

A forward dynamics model predicts how a system changes under an action. For Markov state `s_t`, action `a_t`, and optional context `c`, the one-step transition is

```text
p_theta(s[t+1] | s[t], a[t], c).
```

Multi-step prediction models

```text
p_theta(s[t+1:t+H] | s[t], a[t:t+H-1], c)
  = product_k p_theta(s[t+k+1] | s[t+k], a[t+k], c)
```

for an autoregressive Markov factorization. A direct or sequence-level model need not use this exact factorization. When state is hidden, a model may infer a compact stochastic state `z_t` from observation history and predict

```text
q_phi(z[t] | o[<=t], a[<t])
p_theta(z[t+1] | z[t], a[t])
p_psi(o[t] | z[t]).
```

The observation decoder is optional. MuZero and TD-MPC2 demonstrate decision models that predict planning-relevant quantities or implicit latent dynamics without reconstructing all observation detail, whereas PlaNet and Dreamer include observation reconstruction in their learned state. [PLAN-MUZERO-2020; MBRL-TDMPC2-2024; FD-PLANET-2019; MBRL-DREAMER-2020]

## Assumptions and scope

The Markov formulation assumes `s_t` contains enough information to predict the next-state distribution under an action. Pixels or a single camera frame often violate this assumption through occlusion, velocity ambiguity, unobserved contact forces, and delayed effects. Recurrent state, observation history, proprioception, or belief inference can reduce but not guarantee removal of partial observability.

A deterministic predictor approximates a point such as a conditional mean. A stochastic predictor represents process noise, unobserved variables, or multiple valid futures. Model uncertainty about insufficient data is distinct from irreducible outcome uncertainty; a single learned variance does not necessarily identify the two.

Forward dynamics is defined by action-conditioned prediction, not by visual generation alone. A video continuation model that ignores `a_t` is not useful evidence of controlled dynamics even when its outputs are realistic. Conversely, a compact state model can be useful for control without producing interpretable video.

## Mechanism families

| Family | State/output | Training signal | Strength | Failure boundary |
|---|---|---|---|---|
| Deterministic one-step regression | physical or latent next state | MSE or structured state loss | simple and efficient | averages multimodal futures; compounds recursively |
| Probabilistic transition | distribution over next state | likelihood or distributional loss | represents stochastic outcomes | calibration and distribution family can be wrong |
| Ensemble dynamics | multiple predictive models | resampled or independently initialized fits | practical disagreement signal for data uncertainty | correlated members can be overconfident |
| Latent state-space model | recurrent deterministic and stochastic latent | variational sequence objective, reconstruction, reward | compact rollout under partial observation | representation can omit task-critical factors |
| Action-conditioned video model | future pixels or video latents | autoregressive, diffusion, or flow objective | dense observable prediction | perceptual loss can dominate causal response |
| Decision-relevant implicit model | latent transition plus reward/value/policy features | temporal difference or value-equivalent losses | focuses capacity on decisions | may not support general-purpose simulation |

PlaNet reports a recurrent state-space model with deterministic and stochastic components and a multi-step latent-overshooting objective. PETS combines probabilistic ensemble transitions with trajectory sampling. Learning to Poke jointly trains forward and inverse models so that inverse prediction supplies action-relevant visual features while forward prediction regularizes those features. These are established mechanisms in their evaluated settings, not evidence that any one family is universally superior. [FD-PLANET-2019; MBRL-PETS-2018; DYN-POKE-2016]

## Design implications and trade-offs

| Lever | Evidence status and rationale | Expected signal | Confounder or cost | Discriminating test |
|---|---|---|---|---|
| State representation | Synthesis: prediction is easier when state retains controllable and task-relevant variables | lower task-state and rollout error | representation may discard details needed by a different task | probe state/contact/reward variables and downstream utility |
| Stochastic transition | Supported by PlaNet/PETS mechanisms for their settings | better likelihood, coverage, and calibration | more samples and harder optimization | deterministic versus stochastic model at equal capacity |
| Multi-step objective | PlaNet uses latent overshooting; broader benefit is task-dependent | slower error growth with horizon | oversmoothing or training cost | one-step and horizon-conditioned rollout curves |
| Ensemble disagreement | PETS uses ensembles for uncertainty-aware planning | better risk-sensitive candidate ranking | shared biases remain invisible | error versus disagreement calibration on held-out shifts |
| Action-counterfactual data | Synthesis: paired action variation identifies conditional response | stronger action sensitivity | collection cost and unsafe actions | same context with true, zero, opposite, and shuffled actions |
| Contact/event auxiliary targets | Hypothesis for manipulation domains | contact and object-state accuracy | auxiliary task can dominate shared features | loss ablation with contact and closed-loop metrics |
| Horizon curriculum | Hypothesis: progressive horizon can reduce early optimization difficulty | stable long-horizon learning | curriculum-specific overfitting | fixed-horizon versus curriculum under equal updates |
| Short model rollouts | MBPO supports this pattern for its policy-optimization setting | reduced model-bias exposure | less synthetic data and shorter credit assignment | return versus rollout length from matched real states |

Action serialization is part of the model, not a preprocessing footnote. Coordinate frame, absolute versus delta semantics, units, normalization, rate, latency, view timestamps, and action horizon determine the conditional being learned. Tensor-compatible but semantically mismatched actions can yield low training loss and invalid dynamics.

## Evaluation and falsification

Forward-model evaluation separates distribution fit from causal and decision utility:

- **One-step fit:** likelihood, calibrated state error, or structured event accuracy.
- **Rollout stability:** error and uncertainty as functions of horizon, including discontinuities and contact.
- **Counterfactual sensitivity:** response under matched action interventions, including zero, opposite, shuffled, and true actions.
- **Coverage and calibration:** outcome coverage at declared sample count and confidence/error agreement.
- **Decision utility:** planning return, ranking accuracy, policy improvement, or closed-loop task success under equal search budget.
- **Distribution shift:** held-out scenes, objects, tasks, embodiments, action magnitudes, and temporal rates.

A claim of learned action dynamics is falsified when predictions remain unchanged under meaningful action interventions or when the direction of predicted change conflicts with independently replayed transitions. A claim that improved visual prediction benefits control is narrowed when video metrics improve without task-state, candidate-ranking, or closed-loop gains.

## Failure modes

- **Compounding rollout error:** generated states leave the training distribution and become increasingly unreliable.
- **Action neglect:** the model predicts likely motion from observation history while ignoring the supplied action.
- **Conditional-mean future:** deterministic loss averages mutually exclusive outcomes.
- **State aliasing:** visually identical observations hide different velocity, contact, or object state.
- **Temporal misalignment:** observation and action timestamps or rates describe a different transition than intended.
- **Coordinate mismatch:** direction, units, rotation order, gripper sign, or absolute/delta semantics are wrong.
- **Boundary padding artifact:** repeated or padded frames are learned as real static dynamics.
- **Uncertainty collapse:** confidence does not rise with data support or fall under shift.
- **Planner exploitation:** search finds inputs that maximize predicted reward through model error rather than real progress.

## Cross-part instantiations

- [IRASim](../../papers/irasim/paper.md) instantiates action-conditioned observation-space forward dynamics over robot action chunks, then uses generated rollouts with external evaluators for policy ranking and planning; the entry preserves its logged-action and decision-validity limits.
- [Cosmos-Predict2.5 action conditioning](../../papers/cosmos-predict2-5/paper.md) instantiates an observation-space forward model over a Bridge-specific action chunk, while the base text/image/video generator remains an observational continuation model.

- [Cosmos3-Nano action modeling](../../models/cosmos3-nano/action-modeling.md) instantiates FD with an external action path, domain adapter, padded canonical action tensor, and H-actions/H+1-observations structure.
- [Cosmos3-Nano Generator](../../models/cosmos3-nano/generator.md) owns the rectified-flow generation mechanism used by continuous modalities.
- [Cosmos3-Nano modalities and I/O](../../models/cosmos3-nano/modalities-and-io.md) owns concrete preprocessing and time-axis contracts.
- [Cosmos3-Nano evaluation](../../models/cosmos3-nano/evaluation.md) records reported action-task metrics; [limitations](../../models/cosmos3-nano/limitations.md) records evidence gaps.
- [Paper entries](../../papers/README.md) can preserve the specific PlaNet, PETS, Dreamer, Learning to Poke, and Visual Foresight experiments.

## Sources

- [DYN-POKE-2016] Agrawal et al., *Learning to Poke by Poking: Experiential Learning of Intuitive Physics*, NeurIPS 2016.
- [PLAN-VISUAL-FORESIGHT-2017] Finn and Levine, *Deep Visual Foresight for Planning Robot Motion*, ICRA 2017, DOI:10.1109/ICRA.2017.7989324.
- [FD-PLANET-2019] Hafner et al., *Learning Latent Dynamics for Planning from Pixels*, ICML 2019, PMLR 97:2555-2565.
- [MBRL-PETS-2018] Chua et al., *Deep Reinforcement Learning in a Handful of Trials using Probabilistic Dynamics Models*, NeurIPS 2018.
- [MBRL-MBPO-2019] Janner et al., *When to Trust Your Model: Model-Based Policy Optimization*, NeurIPS 2019.
- [MBRL-DREAMER-2020] Hafner et al., *Dream to Control: Learning Behaviors by Latent Imagination*, ICLR 2020.
- [PLAN-MUZERO-2020] Schrittwieser et al., *Mastering Atari, Go, Chess and Shogi by Planning with a Learned Model*, Nature 588, DOI:10.1038/s41586-020-03051-4.
- [MBRL-TDMPC2-2024] Hansen, Su, and Wang, *TD-MPC2: Scalable, Robust World Models for Continuous Control*, ICLR 2024.
