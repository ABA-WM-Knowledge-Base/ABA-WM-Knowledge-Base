---
id: world-model-kb.foundations.problem-formulation.inverse-dynamics
title: Inverse Dynamics
kind: reference
status: maintained
last_updated: 2026-08-11
owners:
  - AIBuildAI world-model group
---

# Inverse Dynamics

## Retrieval metadata

**Relevant queries:** inverse dynamics, action inference, transition-to-action prediction, latent action, action ambiguity, multimodal action decoder, action representation, or controllable features.

**Knowledge provided:** the inverse conditional, identifiability and multimodality boundaries, joint forward-inverse representation mechanisms, and evaluations that separate numeric fit from feasible action recovery.

**Related pages:** [Forward dynamics](forward-dynamics.md) owns action-conditioned future prediction; [world action models](../definitions-and-taxonomy/world-action-model.md) owns joint action-and-future generation; [robotics and embodied AI](../embodied-systems/robotics-and-embodied-ai.md) owns executable action contracts.

## Definition and formalism

An inverse dynamics model infers an action or action sequence that explains an observed transition. For states `s_t`, `s_{t+1}`, and optional context `c`,

```text
p_phi(a[t] | s[t], s[t+1], c).
```

For observation-space, partial-observation, or multi-step data,

```text
p_phi(a[t:t+H-1] | o[<=t], o[t+1:t+H], c).
```

The model estimates an inverse of the controlled transition only with respect to the observations and action representation supplied. It need not recover forces, controller internals, or hidden actions that are not identifiable from the recorded transition.

Inverse dynamics differs from inverse reinforcement learning. Inverse dynamics predicts controls from state change; inverse reinforcement learning infers a reward or objective from behavior. It also differs from behavior cloning, which predicts action from current observation and task context without requiring the realized next state.

## Assumptions and scope

An inverse is unique only when the transition and action representation identify a single action. Physical and visual domains commonly violate uniqueness:

- multiple trajectories reach the same endpoint;
- redundant joints realize the same end-effector motion;
- contact forces and gripper motion are occluded;
- camera sampling omits intermediate motion;
- environment dynamics contribute to the transition;
- two controller commands are equivalent after clipping, saturation, or low-level control.

Accordingly, `p(a|s,s')` is often more appropriate than a single regression target. Point regression can estimate a conditional mean that is not itself feasible. This is a structural consequence of a one-to-many inverse, not a claim that every inverse-dynamics dataset is measurably multimodal.

Action identity also depends on representation. Joint position, joint velocity, torque, end-effector delta, absolute pose, base motion, camera motion, gripper state, and learned latent action spaces answer different inverse problems. A model that predicts the correct numeric width under the wrong frame or rate has not recovered the intended action.

## Mechanism families

| Family | Output | Strength | Structural limitation |
|---|---|---|---|
| Deterministic action regression | point estimate | efficient and simple for near-unique transitions | averages multiple valid actions |
| Classification or discretized action model | categorical action/token | supports multimodal modes and autoregression | quantization and vocabulary design |
| Probabilistic continuous decoder | mixture, diffusion, flow, or other distribution | multi-sample feasible coverage | sampling cost and calibration |
| Sequence inverse model | action chunk between observation histories | captures temporally extended motion | weakly observed intermediate actions |
| Joint forward-inverse representation | shared encoder trained by both directions | action-relevant state and mutual regularization | both objectives can share the same shortcut |
| Latent-action model | inferred discrete or continuous interaction code | uses video without recorded physical actions | latent code lacks guaranteed physical semantics |

Learning to Poke reports a joint forward/inverse model in which inverse prediction supplies informative visual features and the forward objective regularizes those features. Pathak et al. use inverse dynamics to learn a feature space intended to emphasize agent-controllable change and reduce nuisance variation before forward prediction. These are mechanism-specific empirical results and design rationales, not a theorem that inverse features always remove uncontrollable factors. [DYN-POKE-2016; REP-ICM-2017]

## Design implications and trade-offs

| Lever | Evidence status and rationale | Expected signal | Risk | Discriminating evidence |
|---|---|---|---|---|
| Action parameterization | Synthesis: continuity and physical semantics shape learnability | lower calibrated error and higher feasibility | representation-specific singularity or discontinuity | encode/decode round trip and per-axis sweeps |
| Multimodal decoder | Synthesis for non-unique inverses | best-of-N feasible coverage | sample inflation and difficult likelihood | coverage-success curve against sample count |
| Observation horizon | longer context can reveal velocity and intermediate motion | lower ambiguity | more latency and irrelevant context | performance by history and target horizon |
| Forward auxiliary | supported in Learning to Poke for its setting | more predictive action features | shared shortcut or loss conflict | forward-only, inverse-only, and joint ablation |
| Feasibility-conditioned ranking | hypothesis: controller constraints select among valid modes | safer candidate set | biased toward easy rather than task-correct actions | feasibility plus terminal-outcome evaluation |
| Embodiment-specific adapter | separates common dynamics from physical command schema | transfer with fewer target samples | hidden unit/rate mismatch | target learning curve after contract calibration |
| Transition hard negatives | synthesis: similar endpoints with different paths expose ambiguity | improved path sensitivity | collection and labeling cost | same endpoint/different-action retrieval test |

Loss selection follows output semantics. Euclidean error is meaningful only after units and scales are defined; angular quantities need a representation-aware distance; gripper or discrete modes may need classification; trajectories can require temporal alignment. Averaging normalized dimensions without denormalized physical metrics can hide the operational error.

## Evaluation and falsification

An inverse-dynamics evaluation includes:

- denormalized error for each action component, with coordinate frame, units, and rate;
- sequence and endpoint error at matched horizons;
- likelihood or calibration when a distribution is modeled;
- top-1 and best-of-N feasible coverage at declared sample counts;
- inverse/forward cycle tests using an independently evaluated forward model or environment;
- controller feasibility, joint-limit, collision, and IK residuals where applicable;
- terminal state and closed-loop task success after decoded action execution;
- held-out object, scene, task, viewpoint, and embodiment slices.

A claim of inverse recovery is falsified when decoded actions do not reproduce the observed transition under independent replay, even if normalized MSE is low. A claim that multimodal decoding resolves ambiguity is narrowed when gains arise only from more samples without improved calibrated coverage or closed-loop utility.

Cycle consistency alone is insufficient if the forward and inverse models share training data, representation, or bias. Environment replay or a separately validated dynamics source provides stronger evidence.

## Failure modes

- **Conditional-mean action:** numeric loss is low but the average action is infeasible or accomplishes neither mode.
- **Hidden-action ambiguity:** the observation pair does not reveal force, contact, gripper, or intermediate motion.
- **Embodiment mismatch:** identical vectors represent different joints, frames, units, or controller modes.
- **Temporal aliasing:** multiple low-level commands occur between recorded frames.
- **Environment attribution:** passive object motion is incorrectly assigned to the agent action.
- **Viewpoint shortcut:** the model predicts action from camera or dataset identity rather than transition dynamics.
- **Shared-cycle shortcut:** forward and inverse models agree with each other but not with the environment.
- **Latent-action overinterpretation:** an inferred controllable code is treated as a physical command without a grounded decoder.
- **Sequence padding artifact:** boundary repetition or masks reveal position rather than action semantics.

## Cross-part instantiations

- [Cosmos3-Nano action modeling](../../models/cosmos3-nano/action-modeling.md) instantiates ID by constructing action placeholders, decoding generated action values, and using a domain-specific action adapter.
- [Cosmos3-Nano modalities and I/O](../../models/cosmos3-nano/modalities-and-io.md) owns concrete shape and time contracts.
- [Cosmos3-Nano Policy-DROID](../../models/cosmos3-nano/policy.md) owns a specialized executable DROID action representation and is not interchangeable with base ID output.
- [Cosmos3-Nano evaluation](../../models/cosmos3-nano/evaluation.md) records report-specific inverse metrics and their conditions.
- [Paper entries](../../papers/README.md) can preserve the evaluated data and architectures of Learning to Poke, ICM, Genie, and future latent-action systems.

## Sources

- [DYN-POKE-2016] Agrawal et al., *Learning to Poke by Poking: Experiential Learning of Intuitive Physics*, NeurIPS 2016.
- [REP-ICM-2017] Pathak et al., *Curiosity-Driven Exploration by Self-Supervised Prediction*, CVPR Workshops 2017.
- [WFM-GENIE-2024] Bruce et al., *Genie: Generative Interactive Environments*, ICML 2024, PMLR 235:4603-4623.
- [C3-TR] NVIDIA, *Cosmos 3: Omnimodal World Models for Physical AI*, arXiv:2606.02800.
