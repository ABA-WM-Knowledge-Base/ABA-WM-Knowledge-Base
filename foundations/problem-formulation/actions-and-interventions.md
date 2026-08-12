---
id: world-model-kb.foundations.problem-formulation.actions-and-interventions
title: Actions and Interventions
kind: concept
status: maintained
last_updated: 2026-08-11
owners:
  - AIBuildAI world-model group
---

# Actions and Interventions

## Retrieval metadata

**Relevant queries:** action conditioning, intervention, causal dynamics, forward model, inverse model, latent action, behavior-policy support, action chunking, or embodiment adapter.

**Knowledge provided:** the semantics required for action-conditioned prediction, distinctions among forward, inverse, and joint models, and diagnostics for causal control claims.

**Related pages:** [Problem formulation](problem-formulation.md) owns the process factorization; [world action models](../definitions-and-taxonomy/world-action-model.md) owns joint action-future interfaces; [state, observation, and belief](state-observation-and-belief.md) owns the information state.

## Definition and formalism

An action `a_t` is a variable through which an agent or controller changes the transition distribution. The controlled Markov surface is

```text
p(s_{t+1} | s_t, a_t).
```

Its semantics require units, reference frame, control mode, application interval, actuator, and timing relative to observations. Tensor compatibility is not semantic compatibility.

Three commonly confused conditionals are

```text
forward dynamics: p(s_{t+1} | s_t, a_t)
inverse dynamics: p(a_t | s_t, s_{t+1})
joint model:      p(a_t, s_{t+1} | s_t, g).
```

Inverse dynamics need not be unique: many actions can produce similar observations, and hidden contacts or controller state can change the required command. A joint model can be factorized action-first or future-first without proving that either branch uses the other causally.

Observing `p(y|h,a)` in logged data is not by itself the same as identifying `p(y|h, do(a))`. They agree only under assumptions such as adequate state adjustment, correct temporal ordering, no unmodeled common causes relevant to action selection and outcome, and sufficient action support. [ACT-PEARL-1995]

## Assumptions and scope

Action-conditioned prediction is strongest within the state-action support of the data-generating behavior policy. Extrapolating to rare, unsafe, or physically infeasible commands is a separate capability. Randomized or exploratory actions can improve identification, but exploration design, actuator limits, and safety constraints shape what is learnable.

`Latent action` is also contested. In passive video models it often denotes a learned code that explains visual change. Such a code can enable interaction-like generation without corresponding to calibrated robot commands, forces, or affordances. Mapping it to an embodiment requires additional evidence.

## Mechanism families

| Family | Interface | Useful property | Main boundary |
|---|---|---|---|
| Known control input | measured command conditions transition | clear actuator semantics | executed action can differ from command |
| Learned forward dynamics | action predicts consequence | counterfactual rollout | off-support errors invite exploitation |
| Learned inverse dynamics | transition predicts action | labels or action recovery | multimodal and non-identifiable |
| Latent-action model | learned code explains change | can learn from unlabeled video | code is not automatically executable |
| Action chunk model | sequence of controls predicted jointly | temporal abstraction and speed | open-loop errors and chunk timing |
| Joint world-action model | actions and outcomes sampled together | shared behavior-outcome representation | shared hallucination and marginal collapse |
| Embodiment adapter | maps canonical to robot-specific action | parameter sharing across robots | units and controller dynamics may not align |

## Design implications and trade-offs

Action normalization, coordinate frames, absolute versus delta control, gripper convention, chunk length, control frequency, and sensor latency are first-order design variables. Increasing the chunk horizon reduces inference frequency but creates longer open-loop intervals. A canonical cross-embodiment action space can improve sharing while hiding morphology-specific feasibility.

Action sensitivity can be encouraged with diverse interventions, inverse or contrastive auxiliaries, explicit contact/state targets, and matched counterfactual data. These can still learn shortcuts if action selection correlates with scene or task labels. Counterfactual augmentation is informative only when the resulting action-outcome pair is physically valid.

## Evaluation and falsification

- Hold history fixed, perturb one feasible action component, and compare predicted and independently observed consequences.
- Stratify performance by action density and distance from behavior-policy support.
- Test command versus executed-action logs when low-level control or latency changes the transition.
- Measure inverse-model multimodality rather than only mean error.
- Evaluate chunk lengths under equal wall-clock and closed-loop budgets.
- Transfer across embodiments only after validating frames, units, rates, and actuator semantics.

A causal action claim is weakened when predictions are unchanged under interventions, when the apparent effect disappears after conditioning on task or state, or when only impossible/offline correlations are tested. An executable-action claim is falsified when decoded commands cannot be replayed through the stated controller interface.

## Failure modes

- **Behavior-policy confounding:** task or state predicts both the logged action and outcome.
- **Support extrapolation:** planning selects actions absent from training.
- **Command-execution mismatch:** saturation, delay, compliance, or low-level control changes the applied action.
- **Frame or unit mismatch:** numerically valid tensors have different physical meanings.
- **Inverse ambiguity:** averaging several valid actions produces an invalid command.
- **Camera-action confusion:** ego-motion or edits are learned as object dynamics.
- **Latent-action overclaim:** a video-change code is treated as a robot command without grounding.
- **Chunk drift:** early errors within an open-loop action chunk cannot be corrected.

## Cross-part instantiations

- [Cosmos3-Nano action modeling](../../models/cosmos3-nano/action-modeling.md) owns its forward, inverse, and WAM contracts and action adapters.
- [Policy-DROID](../../models/cosmos3-nano/policy.md) owns the specialized executable observation/action interface; base generation should not inherit that evidence.
- [Modalities and I/O](../../models/cosmos3-nano/modalities-and-io.md) records action tensor, temporal, and conditioning semantics.
- [Evaluation](../../models/cosmos3-nano/evaluation.md) should distinguish self-consistency from independent replay; [limitations](../../models/cosmos3-nano/limitations.md) records unsupported embodiments and action regimes.

## Sources

- [ACT-PEARL-1995] Pearl, *Causal Diagrams for Empirical Research*, Biometrika, 1995, DOI:10.1093/biomet/82.4.669.
- [FND-ASTROM-1965] Astrom, *Optimal Control of Markov Processes with Incomplete State Information*, Journal of Mathematical Analysis and Applications, 1965, DOI:10.1016/0022-247X(65)90154-X.
- [CTRL-POMDP-1998] Kaelbling, Littman, and Cassandra, *Planning and Acting in Partially Observable Stochastic Domains*, Artificial Intelligence, 1998, DOI:10.1016/S0004-3702(98)00023-X.
- [FND-OH-VIDEO-2015] Oh et al., *Action-Conditional Video Prediction using Deep Networks in Atari Games*, NeurIPS 2015.
- [WFM-GENIE-2024] Bruce et al., *Genie: Generative Interactive Environments*, ICML 2024, arXiv:2402.15391.
- [C3-TR] NVIDIA, *Cosmos 3: Omnimodal World Models for Physical AI*, arXiv:2606.02800.
