---
id: world-model-kb.foundations.decision-making.planning-and-control
title: Planning and Control with World Models
kind: reference
status: maintained
last_updated: 2026-08-13
owners:
  - AIBuildAI world-model group
---

# Planning and Control with World Models

## Retrieval metadata

**Relevant queries:** planning, control, model-predictive control, MPC, belief-space planning, latent planning, CEM, trajectory optimization, model exploitation, receding horizon, or terminal value.

**Knowledge provided:** decision formalisms under partial observation, model-use families, planning variables and trade-offs, and tests that separate imagined objective value from real closed-loop utility.

**Related pages:** [Model-based RL](model-based-rl.md) covers model learning coupled to policy improvement; [forward dynamics](../problem-formulation/forward-dynamics.md) covers the predictive model; [robotics and embodied AI](../embodied-systems/robotics-and-embodied-ai.md) covers physical execution contracts.

## Definition and formalism

Planning selects future actions using an objective and a model of their consequences. Control closes the loop by converting current information into action while the environment continues to evolve. Under partial observation, a standard abstraction is a POMDP

```text
M = (S, A, T, O, Z, R, gamma),
```

with state `s`, action `a`, transition `T(s'|s,a)`, observation `o`, observation model `Z(o|s)`, reward or cost `R`, and discount `gamma`. A belief state summarizes available information:

```text
b_t(s) = P(s_t = s | o_{<=t}, a_{<t}).
```

Kaelbling, Littman, and Cassandra provide the canonical planning-and-acting treatment for partially observable stochastic domains. Learned recurrent or latent world states can approximate a belief statistic, but a neural hidden state is not guaranteed to be a calibrated posterior. [CTRL-POMDP-1998]

Given a current state or belief, finite-horizon action selection can be written as

```text
a*[t:t+H-1] = argmax_a E_model[
    sum(k=0..H-1) gamma^k r(s[t+k], a[t+k])
    + gamma^H V_terminal(s[t+H])
].
```

Model-predictive control repeatedly solves such a finite-horizon problem, applies the first action or a short prefix, observes the real system again, and replans. This receding-horizon structure limits open-loop exposure but does not remove model bias. [CTRL-MPC-2000]

## Assumptions and scope

Planning quality depends jointly on state estimation, model accuracy over candidate trajectories, objective specification, search coverage, constraints, and execution latency. Improving only one component need not improve the closed loop.

The predictive representation need not reconstruct the entire world. MuZero learns iterable reward, value, and policy predictions relevant to search without learning a full observation reconstruction. TD-MPC2 performs local trajectory optimization in an implicit decoder-free latent model. By contrast, visual foresight and UniSim expose predicted video. These systems demonstrate multiple valid model scopes; they do not establish equivalence between visual fidelity and value-equivalent planning state. [PLAN-MUZERO-2020; MBRL-TDMPC2-2024; PLAN-VISUAL-FORESIGHT-2017; WFM-UNISIM-2024]

Planning text, action proposals, and control commands are different interfaces. A language model can decompose a task without satisfying geometry, timing, collision, or actuator constraints. A world model can propose a plausible rollout without providing a stable feedback controller. A policy can act without explicit test-time search.

## Mechanism families

| Family | Decision computation | Strength | Limitation |
|---|---|---|---|
| Open-loop trajectory optimization | optimize a complete action sequence once | simple and globally coordinated horizon | no correction after unmodeled events |
| Model-predictive control | replan finite horizon from each new observation | feedback reduces drift | repeated inference cost and latency |
| Sampling-based planning | random shooting, CEM, MPPI, or related candidate updates | works with non-differentiable models/objectives | candidate count grows with action dimension and horizon |
| Gradient-based planning | differentiate objective through model | efficient local improvement with smooth dynamics | exploits gradient/model artifacts and local optima |
| Tree search | expand discrete or abstract action branches | combines lookahead and value estimates | branching and representation design |
| Amortized policy in imagination | train actor/critic from model rollouts | fast deployment after training | policy inherits model bias without test-time correction |
| Hybrid planner-policy | policy proposes candidates or terminal value; planner refines | balances amortization and online adaptation | more coupled components and attribution difficulty |
| Hierarchical planning | high-level goals or skills plus low-level controller | longer effective horizon | interface and subgoal feasibility errors |

PlaNet uses cross-entropy-method planning in latent dynamics. PETS combines sampling-based MPC with probabilistic ensembles and trajectory sampling. Dreamer trains actor and value functions through latent imagination rather than optimizing each action sequence online. MuZero combines learned dynamics with tree search. These results establish viable mechanism instances under their protocols, not a general ranking. [FD-PLANET-2019; MBRL-PETS-2018; MBRL-DREAMER-2020; PLAN-MUZERO-2020]

## Design implications and trade-offs

| Lever | Mechanistic effect | Expected benefit | Risk or cost | Informative measurement |
|---|---|---|---|---|
| Planning horizon | exposes delayed consequences | better long-horizon coordination | compounding model error and harder search | return and model error versus horizon |
| Replanning interval | controls feedback frequency | faster disturbance correction | inference latency and action jitter | success-latency curve under perturbations |
| Candidate count/iterations | expands search coverage | stronger action sequence | compute confounding and diminishing returns | utility versus candidates, steps, and wall time |
| Terminal value | represents outcomes beyond finite horizon | reduced horizon truncation | value extrapolation error | ablation by task delay and horizon |
| Uncertainty cost | discourages unsupported rollouts | less model exploitation | excessive conservatism | real return versus calibrated uncertainty penalty |
| Constraint model | encodes collisions, limits, or safety sets | fewer invalid trajectories | false feasibility or infeasibility | violation and false-rejection rates |
| Action abstraction | reduces effective horizon and branching | scalable long tasks | subgoal or skill interface mismatch | success by composition length and recovery case |
| Policy proposals | seeds search with likely actions | lower search cost | planner collapses to policy bias | policy-only, planner-only, and hybrid comparison |

These are design variables, not a fixed planning recipe. Their useful values depend on dynamics, control frequency, action dimension, reward delay, and model calibration. Equal-compute reporting is necessary when search budget changes.

## Evaluation and falsification

Planning evaluation distinguishes prediction, optimization, and execution:

- **Model layer:** candidate-trajectory error, uncertainty calibration, and counterfactual action response.
- **Optimizer layer:** best objective found versus evaluations, wall time, and action dimension.
- **Decision layer:** real return, task success, ranking correlation between predicted and realized outcome, and regret against available baselines.
- **Control layer:** end-to-end latency, effective control rate, disturbance recovery, constraint violations, and action smoothness.
- **Generalization layer:** held-out initial states, objects, layouts, tasks, dynamics, and embodiments.

A planning gain is supported when the intervention improves realized outcomes under a fixed model, objective, data, and compute budget. It is narrowed when predicted return rises but realized return falls, a signature of model or objective exploitation. A longer-horizon claim is falsified when gains disappear after equalizing terminal value, candidate count, or wall-clock budget.

Closed-loop evaluation preserves intervention and reset rules, controller frequency, execution horizon, failure definitions, and environment version. Offline video or action likelihood is supporting evidence, not a substitute for the real evaluator used by the decision claim.

## Failure modes

- **Model exploitation:** the optimizer selects actions in regions where predicted reward is high because dynamics are wrong.
- **Objective misspecification:** planned behavior optimizes the declared metric without accomplishing the intended task.
- **Belief failure:** hidden velocity, contact, or object state is not represented in the planning state.
- **Horizon truncation:** delayed costs or task completion lie beyond the optimized horizon.
- **Search collapse:** candidate distribution becomes prematurely narrow or misses a valid mode.
- **Latency instability:** observation-to-action time is too long for the changing system.
- **Constraint mismatch:** learned or approximate constraints disagree with the executor.
- **Open-loop drift:** a long action chunk continues after the environment diverges.
- **Hierarchy mismatch:** a high-level plan requests a subgoal outside the low-level controller's reachable set.
- **Shared evaluator bias:** a generated rollout is judged by the same model family that produced it.

## Cross-part instantiations

- [IRASim model-based planning](../../papers/irasim/paper.md) supplies a concrete candidate-rank experiment in which larger search helps only after the world model sees policy success/failure rollouts; its `P=0` row is direct evidence of search-amplified model/evaluator error.
- [Cosmos3-Nano Reasoner](../../models/cosmos3-nano/reasoner.md) can emit natural-language plans; these require grounding and control to become physical action.
- [Cosmos3-Nano action modeling](../../models/cosmos3-nano/action-modeling.md) provides FD, ID, and WAM candidates that can participate in planning experiments after domain decoding and calibration.
- [Cosmos3-Nano Policy-DROID](../../models/cosmos3-nano/policy.md) exposes a specialized action chunk and serving contract relevant to feedback rate and latency.
- [Cosmos3-Nano inference](../../models/cosmos3-nano/inference.md) owns concrete backend and runtime facts; [limitations](../../models/cosmos3-nano/limitations.md) owns model-specific evidence boundaries.
- [Paper entries](../../papers/README.md) can retain exact PlaNet, PETS, Dreamer, MuZero, TD-MPC2, and visual-foresight algorithms and benchmarks.

## Sources

- [CTRL-POMDP-1998] Kaelbling, Littman, and Cassandra, *Planning and Acting in Partially Observable Stochastic Domains*, Artificial Intelligence 101, DOI:10.1016/S0004-3702(98)00023-X.
- [CTRL-MPC-2000] Mayne et al., *Constrained Model Predictive Control: Stability and Optimality*, Automatica 36, DOI:10.1016/S0005-1098(99)00214-9.
- [PLAN-VISUAL-FORESIGHT-2017] Finn and Levine, *Deep Visual Foresight for Planning Robot Motion*, ICRA 2017, DOI:10.1109/ICRA.2017.7989324.
- [MBRL-PETS-2018] Chua et al., *Deep Reinforcement Learning in a Handful of Trials using Probabilistic Dynamics Models*, NeurIPS 2018.
- [FD-PLANET-2019] Hafner et al., *Learning Latent Dynamics for Planning from Pixels*, ICML 2019.
- [MBRL-DREAMER-2020] Hafner et al., *Dream to Control: Learning Behaviors by Latent Imagination*, ICLR 2020.
- [PLAN-MUZERO-2020] Schrittwieser et al., *Mastering Atari, Go, Chess and Shogi by Planning with a Learned Model*, Nature 588, DOI:10.1038/s41586-020-03051-4.
- [MBRL-TDMPC2-2024] Hansen, Su, and Wang, *TD-MPC2: Scalable, Robust World Models for Continuous Control*, ICLR 2024.
