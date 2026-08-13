---
id: world-model-kb.foundations.embodied-systems.robotics-and-embodied-ai
title: Robotics and Embodied AI
kind: reference
status: maintained
last_updated: 2026-08-13
owners:
  - AIBuildAI world-model group
---

# Robotics and Embodied AI

## Retrieval metadata

**Relevant queries:** embodied AI, robot world model, vision-language-action model, robot policy, embodiment transfer, observation-action contract, action chunk, control rate, latency, sim-to-real, or closed-loop evaluation.

**Knowledge provided:** a systems boundary for embodied agents, distinctions among VLA, world-model, WAM, planner, and controller surfaces, reusable adaptation variables, and evidence criteria for executable behavior.

**Related pages:** [Planning and control](../decision-making/planning-and-control.md) covers decision mechanisms; [world action models](../definitions-and-taxonomy/world-action-model.md) covers joint action-and-future generation; [datasets and supervision](../data-and-evaluation/datasets-and-supervision.md) covers embodiment data.

## Definition and formalism

An embodied agent acts through a physical or simulated body and receives consequences through sensors. A useful systems abstraction is a partially observed feedback loop:

```text
environment state s[t]
  -> sensors and observation adapter -> o[t]
  -> estimator / model / policy / planner -> action representation a_model[t]
  -> action decoder and low-level controller -> command u[t]
  -> robot and environment transition -> s[t+1].
```

The learned model is only one component. Executable behavior also depends on sensing, calibration, coordinate transforms, timing, controller semantics, constraints, and recovery. An observation-action pair can be represented as

```text
o[t] = {camera views, proprioception, task context, history, timestamps}
a[t:t+H-1] = {control mode, values, units, frames, rate, horizon}.
```

Those braces describe a semantic contract, not merely tensor shapes. Two systems with equal action width can control different joints, frames, rates, or absolute/delta quantities.

## Assumptions and scope

Embodied performance combines semantic generalization and physical grounding. Internet-scale visual-language pretraining can support object recognition, instruction interpretation, and semantic reasoning, while robot interaction data supplies action semantics and physical outcomes. RT-2 reports co-fine-tuning vision-language tasks and robot trajectories by representing actions as tokens, with gains in its evaluated semantic generalization tasks. This is evidence for a VLA transfer mechanism, not evidence that RT-2 explicitly learns forward dynamics. [EMB-RT2-2023]

Octo reports a generalist transformer policy trained on 800,000 Open X-Embodiment trajectories and adaptation/evaluation across nine robot platforms. Its design explicitly accommodates different sensors and action spaces. The result supports reusable policy initialization under its protocols; it does not imply zero-shot compatibility with an arbitrary embodiment. [EMB-OCTO-2024]

Robot world models, policies, and simulators answer different questions:

| Surface | Primary question | Native output |
|---|---|---|
| Perception/reasoning model | What is present, happening, or required? | state, label, language, relation |
| Direct policy or VLA | What action follows from this observation and goal? | action or action token |
| Forward world model | What follows if this action is applied? | future state or observation |
| Inverse model | What action explains or realizes this transition? | action candidate |
| World action model | What action and future jointly fit this goal/context? | action plus future |
| Planner | Which candidate action best serves an objective? | selected action or subgoal |
| Low-level controller | How are desired states converted into actuator commands? | timed hardware command |
| Simulator | How does an environment respond to commands? | next state and sensor observations |

One implementation can span several surfaces, but evidence does not transfer automatically between them.

## Mechanism families

| Family | Learning/interface pattern | Reusable strength | Main boundary |
|---|---|---|---|
| Behavior cloning | supervised `o,g -> a` from demonstrations | direct action learning | covariate shift and demonstration support |
| VLA policy | pretrained VLM adapted to output actions | semantic and visual transfer | action grounding depends on robot data and decoder |
| Generalist robot policy | shared backbone over multiple datasets/embodiments | reusable initialization | fragmented action and sensor contracts |
| Model-predictive robot control | action-conditioned model plus online search | flexible goal-conditioned decisions | model error and inference latency |
| WAM policy | joint future/action model used in feedback | dense future supervision and action proposal | coupled hallucination and heavy inference |
| Hierarchical embodied agent | high-level language/goal planner plus low-level skills | long task composition | subgoal feasibility and error propagation |
| Simulator-trained policy | policy learning in analytic or learned environment | scalable experience and controlled variation | simulation-to-real gap |

RoboCasa provides a large-scale simulation framework with 100 household task definitions and synthetic demonstration generation. Its paper reports scaling evidence in simulation and selected real-world experiments; each result remains bound to its corresponding domain and protocol. Simulation visual realism is not sufficient evidence of matching contact, actuator, sensor, or recovery distributions. [BENCH-ROBOCASA-2024]

## Design implications and trade-offs

| Lever | Mechanistic rationale | Expected signal | Risk | Discriminating evidence |
|---|---|---|---|---|
| Observation adapter | aligns views, crops, proprioception, and history | lower perception and policy error | view-order or camera shortcut | held-out camera/layout tests and ablation |
| Action adapter | maps shared output to units, frames, joints, and control mode | correct physical commands | silent semantic mismatch | round trip, per-axis pulse, and replay tests |
| Control rate and latency | determine how long each prediction remains valid | stable feedback and recovery | stale commands or oscillation | success versus measured end-to-end latency |
| Action chunk length | trades temporal coherence for feedback frequency | smoother multi-step skills | open-loop drift after disturbances | perturbation success by chunk size |
| Proprioceptive and temporal memory | exposes hidden velocity, contact, and robot state | better state estimation | sensor-specific overfit | sensor ablation and held-out dynamics |
| Embodiment metadata | separates robot identity and action semantics | cross-robot transfer | dataset-identity shortcut | leave-one-embodiment-out transfer |
| Failure/recovery data | represents off-nominal states and corrections | improved recovery | lower success-data density | controlled disturbances and recovery curves |
| Simulation/real mixture | scales diversity while retaining reality anchor | coverage and data efficiency | negative transfer from sim artifacts | mixture matrix on real held-out tasks |
| Constraint-aware decoding | filters joint, collision, or workspace violations | safer candidate execution | rejects feasible uncommon actions | violation and false-rejection rates |

These implications are system-level synthesis. Their effect depends on robot mechanics, data, task, and controller. An adapter intervention is scientifically separable from backbone tuning: if both change, the source of improvement is ambiguous.

## Evaluation and falsification

Embodied evaluation retains the exact checkpoint, observation contract, action contract, controller, hardware or simulator version, task definition, reset/intervention policy, control rate, and rollout budget. Useful measurement layers are:

1. semantic goal and object understanding;
2. offline action prediction and feasibility;
3. stage progress and terminal task success;
4. collision, force, limit, and other constraint events;
5. latency, effective control frequency, and dropped observations;
6. recovery after object, camera, or execution perturbations;
7. generalization across object, scene, task, language, and embodiment;
8. adaptation efficiency as a curve over target data and updates.

Offline action error is not a substitute for closed-loop success because small errors alter future observations and compound. Conversely, task success alone can hide unsafe or brittle behavior; constraint, intervention, and failure-slice metrics preserve operational meaning.

A cross-embodiment transfer claim is falsified or narrowed when the target requires unreported calibration, demonstrations, normalization, or controller changes. A simulation-transfer claim is narrowed when improvement is confined to simulator-specific textures, dynamics, or reset conditions.

## Failure modes

- **Contract mismatch:** action dimensions, units, frames, joint order, gripper sign, or absolute/delta semantics differ.
- **Observation mismatch:** camera order, crop, intrinsics, viewpoint, proprioception, or timestamps differ from training.
- **Latency mismatch:** inference plus communication exceeds the control loop's stability margin.
- **Covariate shift:** small early errors move the policy into states absent from demonstrations.
- **Semantic-physical gap:** the model identifies the correct goal but lacks a feasible manipulation strategy.
- **Embodiment shortcut:** robot or dataset appearance predicts actions instead of shared task structure.
- **Contact blind spot:** visual loss underweights force, friction, compliance, or grasp state.
- **Open-loop chunk drift:** a multi-step action continues despite changed observations.
- **Recovery deficit:** policy handles nominal demonstrations but not failure states.
- **Simulator overfit:** policy uses artifacts or dynamics that do not transfer.
- **Metric shortcut:** aggregate task success hides a critical object, scene, safety, or long-horizon regression.

## Cross-part instantiations

- [IRASim](../../papers/irasim/README.md) exposes the boundary between an action-conditioned visual forward model, an external proposal policy, an external value function, and physical execution; its public code does not include the ICCV-v2 planning stack.
- [Cosmos3-Nano Reasoner](../../models/cosmos3-nano/reasoner.md) supplies perception, reasoning, and text planning rather than direct physical commands.
- [Cosmos3-Nano action modeling](../../models/cosmos3-nano/action-modeling.md) supplies base FD, ID, and WAM representations with domain adapters.
- [Cosmos3-Nano Policy-DROID](../../models/cosmos3-nano/policy.md) defines a DROID-specific three-view/proprioceptive input and 32-step action output; it does not establish RoboCasa compatibility.
- [Cosmos3-Nano modalities and I/O](../../models/cosmos3-nano/modalities-and-io.md) owns concrete modality types and time contracts.
- [Cosmos3-Nano limitations](../../models/cosmos3-nano/limitations.md) and [evaluation](../../models/cosmos3-nano/evaluation.md) record model-specific evidence boundaries.
- [Paper entries](../../papers/README.md) can preserve RT-2, Octo, DROID, RoboCasa, and other embodied-system protocols and results.

## Sources

- [EMB-RT2-2023] Zitkovich et al., *RT-2: Vision-Language-Action Models Transfer Web Knowledge to Robotic Control*, CoRL 2023, PMLR 229:2165-2183.
- [EMB-OCTO-2024] Ghosh et al., *Octo: An Open-Source Generalist Robot Policy*, RSS 2024, DOI:10.15607/RSS.2024.XX.090.
- [DATA-DROID-2024] Khazatsky et al., *DROID: A Large-Scale In-The-Wild Robot Manipulation Dataset*, RSS 2024, DOI:10.15607/RSS.2024.XX.120.
- [BENCH-ROBOCASA-2024] Nasiriany et al., *RoboCasa: Large-Scale Simulation of Household Tasks for Generalist Robots*, RSS 2024, DOI:10.15607/RSS.2024.XX.050.
- [PLAN-VISUAL-FORESIGHT-2017] Finn and Levine, *Deep Visual Foresight for Planning Robot Motion*, ICRA 2017, DOI:10.1109/ICRA.2017.7989324.
