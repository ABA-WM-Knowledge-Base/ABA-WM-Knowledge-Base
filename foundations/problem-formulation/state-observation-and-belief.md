---
id: world-model-kb.foundations.problem-formulation.state-observation-and-belief
title: State, Observation, and Belief
kind: concept
status: maintained
last_updated: 2026-08-11
owners:
  - AIBuildAI world-model group
---

# State, Observation, and Belief

## Retrieval metadata

**Relevant queries:** hidden state, observation, history, belief state, information state, filtering, state estimation, partial observability, posterior-prior gap, or RSSM.

**Knowledge provided:** precise distinctions among physical state, sensor observation, history, Bayesian belief, and learned latent state, with filtering equations and optimization diagnostics.

**Related pages:** [Problem formulation](problem-formulation.md) defines the process; [latent world models](../representations/latent-world-model.md) covers learned state parameterizations; [actions and interventions](actions-and-interventions.md) defines transition conditioning.

## Definition and formalism

Let `s_t` denote the environment state, `o_t` a sensor observation, and

```text
h_t = (o_0, a_0, o_1, ..., a_{t-1}, o_t)
```

the observable history. A Bayesian belief is the posterior distribution

```text
b_t(s) = P(s_t = s | h_t).
```

For transition `T(s'|s,a)` and observation kernel `Z(o|s',a)`, the Bayes filter is

```text
b_{t+1}(s') = eta Z(o_{t+1}|s',a_t)
              sum_s T(s'|s,a_t) b_t(s),
```

where `eta` normalizes the distribution. The prediction step propagates uncertainty through `T`; the update step conditions it on the new observation.

A learned latent `z_t=f_theta(h_t)` is an information-state candidate. It becomes belief-like only when its distribution and update approximate the uncertainty needed for future prediction or decision making. A deterministic embedding, token sequence, or recurrent hidden state should not be described as a calibrated belief without evidence.

## Assumptions and scope

Kalman filtering gives an exact recursive posterior for a linear dynamical system with Gaussian noise and known parameters. It is an instructive special case, not a general solution to nonlinear, multimodal, partially observed worlds. POMDP beliefs can be sufficient for optimal control under the specified model, but exact beliefs are usually intractable in high-dimensional learned systems.

State is relative to a query. A compact state sufficient for predicting reward under one task may omit texture, identity, or geometry needed by another. Observation and state may coincide in a fully observed simulator, but this should be demonstrated rather than assumed for camera input.

## Representation and estimator families

| Family | Update | Uncertainty | Main trade-off |
|---|---|---|---|
| Kalman or structured Bayesian filter | analytic predict/update | explicit distribution | strong structural assumptions |
| Particle or sampling filter | weighted samples | multimodal in principle | cost and degeneracy in high dimensions |
| Deterministic recurrent state | learned recurrence over history | implicit only | efficient but can hide ambiguity |
| Stochastic latent state-space model | learned prior and observation posterior | parameterized latent distribution | posterior-prior mismatch and collapse |
| Token memory or transformer context | attention over serialized history | implicit, context-bound | long context cost and weak calibration |
| Object or scene memory | persistent entities/geometry | structured but often approximate | data association and occlusion |

PlaNet's recurrent state-space model combines deterministic memory with stochastic latent state:

```text
h_t = f_theta(h_{t-1}, z_{t-1}, a_{t-1}),
prior:     p_theta(z_t | h_t),
posterior: q_theta(z_t | h_t, o_t).
```

Training can use the posterior, while imagination must usually use the prior. Their gap is therefore operationally important. [FD-PLANET-2019]

## Design implications and trade-offs

History length, recurrence, observation fusion, stochastic capacity, and update frequency determine which hidden variables can be inferred. Posterior-prior alignment improves autonomous rollout but excessive regularization can erase observation-specific information. Larger latents improve reconstruction capacity yet may carry nuisance detail or make dynamics harder to learn.

Sensor timestamps, camera pose, proprioception, and action history can be as important as encoder scale. When camera motion and object motion are confounded, an estimator may spend capacity explaining viewpoint rather than world dynamics. Missing-observation training and state resets expose whether the representation performs filtering or merely frame recognition.

## Evaluation and falsification

- Evaluate posterior-corrected prediction and prior-only rollout separately.
- Stratify state probes by hidden variables: velocity, occluded identity, contact, object permanence, and camera pose.
- Test uncertainty with proper scoring rules, coverage, and calibration rather than sample diversity alone.
- Construct aliased observations with different histories and ask whether the representation predicts different futures.
- Remove or delay observations to test filtering and recovery.
- Check whether future observations or labels leak into training-time state construction.

A belief-state claim is weakened when nominal credible regions are miscalibrated, alternative hypotheses collapse prematurely, or state updates ignore informative observations. A Markov-latent claim is weakened when adding older history systematically improves next-state prediction after conditioning on the latent.

## Failure modes

- **Perceptual aliasing:** identical observations correspond to different hidden states.
- **Posterior collapse:** the stochastic latent carries little information because the decoder or recurrent path bypasses it.
- **Prior drift:** autonomous rollout enters latent regions not visited by posterior states.
- **Future leakage:** bidirectional context or labels reveal outcomes unavailable at inference.
- **False calibration:** diverse samples or a variance head are treated as calibrated belief.
- **Identity loss:** occluded entities reappear with switched or reset identities.
- **Clock and pose confounding:** asynchronous sensors or ego-motion masquerade as environment stochasticity.

## Cross-part instantiations

- [Cosmos3-Nano modalities and I/O](../../models/cosmos3-nano/modalities-and-io.md) specifies which observation histories and auxiliary signals are actually accepted.
- [Architecture](../../models/cosmos3-nano/architecture.md) records model-specific latent and memory mechanisms; they should not be inferred from this generic formalism.
- [Generator](../../models/cosmos3-nano/generator.md) can be tested for prior-only temporal persistence, while [action modeling](../../models/cosmos3-nano/action-modeling.md) adds control-conditioned state queries.
- [Evaluation](../../models/cosmos3-nano/evaluation.md) and [limitations](../../models/cosmos3-nano/limitations.md) own checkpoint-specific evidence about observability and temporal consistency.

## Sources

- [FND-KALMAN-1960] Kalman, *A New Approach to Linear Filtering and Prediction Problems*, Journal of Basic Engineering, 1960, DOI:10.1115/1.3662552.
- [FND-ASTROM-1965] Astrom, *Optimal Control of Markov Processes with Incomplete State Information*, Journal of Mathematical Analysis and Applications, 1965, DOI:10.1016/0022-247X(65)90154-X.
- [CTRL-POMDP-1998] Kaelbling, Littman, and Cassandra, *Planning and Acting in Partially Observable Stochastic Domains*, Artificial Intelligence, 1998, DOI:10.1016/S0004-3702(98)00023-X.
- [FD-PLANET-2019] Hafner et al., *Learning Latent Dynamics for Planning from Pixels*, ICML 2019, PMLR 97.
