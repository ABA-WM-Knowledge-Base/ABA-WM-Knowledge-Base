---
id: world-model-kb.foundations.problem-formulation.problem-formulation
title: World-Model Problem Formulation
kind: concept
status: maintained
last_updated: 2026-08-11
owners:
  - AIBuildAI world-model group
---

# World-Model Problem Formulation

## Retrieval metadata

**Relevant queries:** MDP, POMDP, trajectory factorization, transition model, observation model, reward model, termination model, world-model notation, or rollout distribution.

**Knowledge provided:** a common stochastic-process formulation for fully and partially observed environments, explicit model interfaces, and tests for temporal, probabilistic, and downstream-use assumptions.

**Related pages:** [State, observation, and belief](state-observation-and-belief.md) defines information states; [actions and interventions](actions-and-interventions.md) defines control semantics; [world models](../definitions-and-taxonomy/world-model.md) defines the model category.

## Definition and formalism

A finite- or infinite-horizon Markov decision process can be written

```text
M = (S, A, T, R, gamma, rho_0),
```

with transition kernel `T(s' | s,a)`, reward distribution or function `R`, discount `gamma`, and initial-state distribution `rho_0`. Under policy `pi`, a trajectory factorizes as

```text
p_pi(tau) = rho_0(s_0) product_t pi(a_t | s_t) T(s_{t+1} | s_t,a_t),
J(pi) = E_pi[sum_t gamma^t r_t].
```

A partially observable model adds observations and an observation kernel:

```text
P = (S, A, O, T, Z, R, gamma),
p(tau) = p(s_0) product_t Z(o_t | s_t) pi(a_t | h_t)
         R(r_t | s_t,a_t,s_{t+1}) T(s_{t+1} | s_t,a_t).
```

Notation differs across sources: `O` may denote the observation set or kernel, the kernel may be `Z`, and reward may depend on `(s,a)`, `(s,a,s')`, or an observation history. The dependency graph, timing, and units are more important than the symbol names.

A learned world model may approximate any subset of this process. Its contract should identify the conditional distribution being estimated, for example `p(o_{t+1}|h_t,a_t)`, `p(z_{t+1},r_t,d_t|z_t,a_t)`, or a joint future over a fixed action chunk.

## Assumptions and scope

The Markov property is conditional: a state is Markov when the future is independent of earlier history given the current state and action. Raw observations generally need not satisfy it. Stationarity, time discretization, action availability, reward observability, and episode termination are additional assumptions rather than consequences of the notation.

The formulation covers environment prediction but does not require a control objective. Conversely, a policy can optimize behavior without exposing an explicit model. Offline logged trajectories identify predictions primarily within their state-action support; extrapolation to new policies is a separate claim.

## Model-surface families

| Surface | Learned conditional | Information retained | Typical use |
|---|---|---|---|
| Observation dynamics | `p(o_{t+1}|h_t,a_t)` | sensor-level evidence | forecasting and visual planning |
| Latent state-space model | `q(z_t|h_t)`, `p(z_{t+1}|z_t,a_t)` | compressed history | imagination and estimation |
| Reward/termination model | `p(r_t,d_t|z_t,a_t)` | task and episode events | planning or policy learning |
| Value/policy-equivalent model | abstract transition plus value/policy heads | decision-relevant information | search |
| Sequence model | `p(x_1,...,x_N|c)` under a serialization | mixed modalities | scalable generative modeling |
| Joint action-future model | `p(a_{t:t+H-1},y_{t+1:t+H}|h_t,g)` | behavior and consequence | policy and outcome generation |

## Design implications and trade-offs

Temporal semantics should be fixed before changing architectures: whether `r_t` follows `a_t`, whether action chunks are open-loop, whether observations are pre- or post-action, and how dropped or delayed sensor frames are represented. Misalignment can appear as irreducible stochasticity.

One-step maximum likelihood is statistically natural for the logged distribution, but deployment often queries multi-step rollouts under a different policy. Multi-step losses, overshooting, closed-loop data, uncertainty, or task heads may improve the queried surface, but each changes bias, variance, compute, or information allocation. Reward and termination models deserve separate validation because small event errors can dominate planning even when state predictions look accurate.

## Evaluation and falsification

Evaluation should preserve the factorization being claimed:

- compare one-step conditional likelihood or error under matched support;
- roll out without posterior correction to expose transition accumulation;
- stratify by horizon, action magnitude, event type, and policy coverage;
- measure reward and termination calibration separately from observation quality;
- perturb actions while holding history fixed to test conditional sensitivity;
- replay planned actions in an independent environment to expose model exploitation.

A Markov-state claim is weakened when histories with the same proposed state produce systematically different next-outcome distributions. A stationary-transition claim is weakened by time, scene, or embodiment strata that require different kernels. A planning-sufficiency claim is falsified when errors concentrate on distinctions selected by the planner.

## Failure modes

- **Observation-as-state error:** the observation omits velocity, occluded objects, intent, or contact state.
- **Timing mismatch:** actions, rewards, and frames use different clocks or interval conventions.
- **Policy-support shift:** the learned conditional is queried for actions absent from training.
- **Termination omission:** imagined rollouts continue through absorbing or unsafe states.
- **Reward leakage:** future or privileged labels enter the estimated state during training.
- **Teacher-forced optimism:** posterior-corrected predictions hide open-loop drift.
- **Aggregate-metric masking:** common transitions dominate rare contacts or task-critical events.

## Cross-part instantiations

- [Cosmos3-Nano modalities and I/O](../../models/cosmos3-nano/modalities-and-io.md) owns concrete temporal and tensor contracts.
- [Action modeling](../../models/cosmos3-nano/action-modeling.md) instantiates forward, inverse, and joint conditionals.
- [Generator](../../models/cosmos3-nano/generator.md) instantiates a conditional media distribution; [Reasoner](../../models/cosmos3-nano/reasoner.md) instantiates a language-output surface.
- [Evaluation](../../models/cosmos3-nano/evaluation.md) should be interpreted against the exact factorization and checkpoint under test.
- [Paper entries](../../papers/README.md) retain source-specific notation and protocol details.

## Sources

- [FND-ASTROM-1965] Astrom, *Optimal Control of Markov Processes with Incomplete State Information*, Journal of Mathematical Analysis and Applications, 1965, DOI:10.1016/0022-247X(65)90154-X.
- [CTRL-POMDP-1998] Kaelbling, Littman, and Cassandra, *Planning and Acting in Partially Observable Stochastic Domains*, Artificial Intelligence, 1998, DOI:10.1016/S0004-3702(98)00023-X.
- [MBRL-DYNA-1990] Sutton, *Integrated Modeling and Control Based on Reinforcement Learning and Dynamic Programming*, NeurIPS 1990.
- [PLAN-MUZERO-2020] Schrittwieser et al., *Mastering Atari, Go, Chess and Shogi by Planning with a Learned Model*, Nature, 2020, DOI:10.1038/s41586-020-03051-4.
