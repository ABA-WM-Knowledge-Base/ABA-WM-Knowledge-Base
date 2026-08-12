---
id: world-model-kb.foundations.definitions-and-taxonomy.world-model
title: World Models
kind: concept
status: maintained
last_updated: 2026-08-11
owners:
  - AIBuildAI world-model group
---

# World Models

## Retrieval metadata

**Relevant queries:** world model definition, environment model, learned dynamics, predictive model, generative simulator, model-based agent, video model versus world model, or task-sufficient dynamics.

**Knowledge provided:** an operational definition, a component-level formalism, boundaries between adjacent model classes, and criteria for deciding whether a learned model is useful for prediction, planning, or control.

**Related pages:** [Problem formulation](../problem-formulation/problem-formulation.md) defines the stochastic process; [state, observation, and belief](../problem-formulation/state-observation-and-belief.md) defines the information state; [history and taxonomy](history-and-taxonomy.md) maps the major lineages; [world action models](world-action-model.md) covers joint future-action models.

## Definition and formalism

`World model` has no single architecture-independent definition. In this knowledge base it denotes a learned or specified model of environment-relevant variables and their evolution, possibly conditioned on actions and context, that can support prediction, simulation, estimation, planning, or control. The definition concerns the modeled process and usable interface, not whether the implementation is a neural network, a video generator, or a named product.

A broad learned state-space surface is

```text
M_theta = {
  q_theta(z_t | h_t),
  p_theta(z_{t+1} | z_t, a_t),
  p_theta(o_t | z_t),
  p_theta(r_t | z_t, a_t),
  p_theta(d_t | z_t, a_t)
}.
```

Here `h_t` is the available history, `z_t` is a learned information state, `o_t` is an observation, `a_t` is an action, `r_t` is reward or utility evidence, and `d_t` is termination. Components are optional. A video predictor may expose only an observation rollout; a task-oriented model may expose latent transitions, reward, and value without reconstructing observations. The minimal predictive contract is therefore better written as

```text
p_theta(y[t+1:t+H] | h_t, a[t:t+H-1], c),
```

where the target `y`, conditioning `c`, action semantics, and horizon must be stated. MuZero is an important boundary case: its learned model predicts quantities needed for search without reconstructing the environment observation. This shows that task sufficiency and visual reconstruction are distinct design goals. [PLAN-MUZERO-2020]

## Assumptions and scope

The term covers several partially overlapping traditions: state estimation and control, model-based reinforcement learning, learned latent dynamics, action-conditioned video prediction, and large generative models of physical scenes. These traditions disagree about which variables must be represented and what counts as evidence of a useful model.

The following boundaries prevent category errors:

- A visually plausible video generator is not necessarily an action-conditioned or interventional model.
- A static 3D scene representation is not a dynamics model unless it represents change or transition.
- A policy is not a world model merely because its parameters encode world knowledge.
- A vision-language reasoner that describes consequences provides semantic predictions, but not automatically a calibrated transition model or executable action interface.
- A learned latent is not automatically the true physical state or a Bayesian belief state.

These are interface distinctions rather than mutually exclusive product classes. One system may combine several surfaces.

## Mechanism families

| Family | Native representation | Typical predicted surface | Characteristic strength | Characteristic limitation |
|---|---|---|---|---|
| Classical state-space model | explicit state or belief | state, observation, reward | interpretable uncertainty and control semantics | restrictive modeling assumptions |
| Latent dynamics model | continuous or discrete learned state | latent transition and task heads | compact imagined rollouts | information can be omitted or exploited |
| Pixel or video world model | frames or video latents | future observations | preserves dense scene evidence | appearance quality can obscure dynamics error |
| Object- or graph-centric model | entities and relations | entity transitions | compositional interactions | discovery and identity binding are fragile |
| Spatial 3D/4D model | fields, occupancy, points, or Gaussians | geometry through space and time | view consistency and geometric grounding | reconstruction need not imply controllable dynamics |
| Task-oriented predictive model | abstract search state | reward, value, policy, or outcome | allocates capacity to decisions | may not answer general physical queries |
| Joint world-action model | actions plus future state/video | joint action-outcome distribution | couples behavior with predicted consequence | joint self-consistency can still be physically wrong |

Representation family, learning objective, conditioning, and downstream use are orthogonal axes. For example, a latent video model can be autoregressive or diffusion-based, action-free or action-conditioned, and used for generation or planning.

## Design implications and trade-offs

The downstream query determines what the model must preserve. Control needs action-sensitive and temporally aligned variables; planning needs calibrated multi-step consequences and terminal events; open-ended generation may value sample coverage and perceptual detail; reasoning may need semantic state and causal relations. Adding every possible head is not neutral: observation reconstruction can consume capacity that a compact controller would use for reward-relevant detail, while a task-only latent can discard evidence needed after the task distribution changes.

Useful optimization levers include representation capacity, transition stochasticity, observation and task-head weighting, rollout horizon, action encoding, uncertainty parameterization, and data coverage under the policies that will query the model. Their effects should be interpreted through the model's explicit contract. Better reconstruction alone does not establish better planning; better one-step likelihood alone does not establish stable long-horizon simulation.

## Evaluation and falsification

A world-model claim should identify which of the following is tested:

1. **One-step prediction:** accuracy or likelihood under the logged distribution.
2. **Open-loop rollout:** compounding error, uncertainty, and temporal consistency over horizon.
3. **Action sensitivity:** matched counterfactual changes under controlled action perturbations.
4. **Task sufficiency:** planning, control, or reasoning performance when the model is actually used.
5. **Distributional validity:** calibration and coverage under policy, scene, embodiment, and horizon shifts.

The strongest test compares predicted consequences with an independent environment rollout. A claim that the model learned controllable dynamics is weakened when outputs remain invariant to feasible action changes, when action effects are correct only inside the behavior-policy support, or when a planner exploits model errors. A claim of task sufficiency is falsified by systematic failures on distinctions that the downstream task requires even if reconstructions remain attractive.

## Failure modes

- **Observation-state conflation:** treating a camera frame as a complete Markov state.
- **Plausibility substitution:** using perceptual realism as evidence of causal or physical correctness.
- **Passive-data confounding:** interpreting correlations in uncontrolled trajectories as intervention effects.
- **Long-horizon drift:** small transition errors move imagined states outside the training distribution.
- **Model exploitation:** an optimizer selects actions whose predicted benefit arises from model error.
- **Uncertainty collapse:** a point prediction or narrow decoder hides genuinely multimodal futures.
- **Interface overclaim:** semantic text, latent codes, or generated futures are treated as executable controls without a validated decoder.
- **Metric mismatch:** likelihood, PSNR, FVD, or reconstruction score improves while downstream behavior regresses.

## Cross-part instantiations

- [Cosmos3-Nano architecture](../../models/cosmos3-nano/architecture.md) identifies the model's documented Reasoner, Generator, and action-related surfaces.
- [Cosmos3-Nano Generator](../../models/cosmos3-nano/generator.md) is a generative world-model surface; its exact objectives and I/O contract belong to the model-specific page.
- [Cosmos3-Nano Reasoner](../../models/cosmos3-nano/reasoner.md) produces language reasoning rather than an executable transition tensor.
- [Action modeling](../../models/cosmos3-nano/action-modeling.md) and [Policy-DROID](../../models/cosmos3-nano/policy.md) distinguish base action-conditioned modeling from a specialized policy checkpoint.
- [Evaluation](../../models/cosmos3-nano/evaluation.md) and [limitations](../../models/cosmos3-nano/limitations.md) own checkpoint-specific evidence and untested conditions.
- [Paper entries](../../papers/README.md) preserve paper-level architectures and protocols without turning any paper's preferred terminology into a universal definition.

## Sources

- [FND-ASTROM-1965] Astrom, *Optimal Control of Markov Processes with Incomplete State Information*, Journal of Mathematical Analysis and Applications, 1965, DOI:10.1016/0022-247X(65)90154-X.
- [CTRL-POMDP-1998] Kaelbling, Littman, and Cassandra, *Planning and Acting in Partially Observable Stochastic Domains*, Artificial Intelligence, 1998, DOI:10.1016/S0004-3702(98)00023-X.
- [MBRL-DYNA-1990] Sutton, *Integrated Modeling and Control Based on Reinforcement Learning and Dynamic Programming*, NeurIPS 1990.
- [FND-WORLD-MODELS-2018] Ha and Schmidhuber, *Recurrent World Models Facilitate Policy Evolution*, NeurIPS 2018, arXiv:1809.01999.
- [PLAN-MUZERO-2020] Schrittwieser et al., *Mastering Atari, Go, Chess and Shogi by Planning with a Learned Model*, Nature, 2020, DOI:10.1038/s41586-020-03051-4.
