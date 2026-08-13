---
id: world-model-kb.models.cosmos3-nano.action-modeling
title: Cosmos3-Nano Action Representation and World-Action Modeling
kind: reference
status: maintained
last_updated: 2026-08-13
owners:
  - AIBuildAI world-model group
---

# Cosmos3-Nano Action Representation and World-Action Modeling

## Retrieval metadata

**Relevant queries:** action-space adaptation, forward dynamics, inverse dynamics, WAM, action conditions, action-aware objectives, coordinates, units, normalization, rate, or horizon.

**Knowledge provided:** action representations, domain adapters, modeling objectives, failure interpretations, and evaluation dimensions. Tensor shape compatibility alone does not establish semantic control compatibility.

**Related pages:** [Reasoner](reasoner.md) covers natural-language planning; [Policy](policy.md) covers Policy-DROID serving; [Modality contracts](modalities-and-io.md) covers typed I/O. Foundation owners define [world action models](../../foundations/definitions-and-taxonomy/world-action-model.md), [actions and interventions](../../foundations/problem-formulation/actions-and-interventions.md), [forward dynamics](../../foundations/problem-formulation/forward-dynamics.md), and [inverse dynamics](../../foundations/problem-formulation/inverse-dynamics.md).

## Strict task boundaries

Cosmos3-Nano treats action as a continuous DM modality in the Generator path, not as natural-language tokens. Base Nano supports three action-modeling objectives through domain-specific encoders, projections, and decoders:[C3-TR, pp.7-10, Figures 3-4; C3-FW-ACTION]

- **Forward dynamics (FD):** predict future observations from current observation and action.
- **Inverse dynamics (ID):** infer an action trajectory from an observed transition.
- **World Action Model (WAM):** jointly generate action and a corresponding visual future.

| Surface | Input | Output | Model path | Executability |
|---|---|---|---|---|
| Reasoner planning | text and image/video | text plan | AR / Reasoner | requires grounding and controller |
| Forward dynamics | observation and action | future observation | DM / Generator | predicts the world, not an action command |
| Inverse dynamics | observation transition | continuous action representation | DM / Generator | candidate must be decoded and checked |
| WAM | observation/instruction | action plus future observation | DM / Generator | research surface, not a specialized policy |
| Policy-DROID | DROID visual/proprioceptive observation and instruction | 32-step action chunk | specialized checkpoint | executable only under the DROID contract |

[C3-TR, pp.7-10 and pp.31-32; C3-FW-INFERENCE; C3-FW-POLICY-SERVER]

Continuous model output becomes a robot command only after coordinate conversion, inverse normalization, joint or end-effector mapping, gripper convention, rate control, and safety validation.

## Canonical action representation

### Domain-specific projections

Physical platforms do not share a native action space. Cosmos 3 maps each domain's continuous representation into the common hidden size through dedicated input and output projections. The backbone can share dynamics structure while adapters retain domain semantics.[C3-TR, pp.7-9, Figure 3]

Pose-oriented actions use relative SE(3) changes. Translation is 3D, rotation uses a continuous 6D representation, and robot actions add grasp state. The 6D rotation avoids Euler periodic discontinuities and quaternion double-cover ambiguity in a regression target.[C3-TR, pp.7-9, Figure 3]

### Reported action families

| Domain family | Canonical width | Report-level semantics |
|---|---:|---|
| Autonomous vehicle | 9D | vehicle motion/control |
| Camera | 9D | camera or ego-pose change |
| Egocentric human | 57D | body- and hand-related motion |
| Single-arm robot | 10D | 3 translation, 6 rotation, 1 grasp |
| Dual-arm robot | 20D | two 10D arms |
| Humanoid | 29D | humanoid-specific state |

[C3-TR, pp.7-9, Figure 3]

These are family-level canonical representations. They are not guaranteed raw widths for every dataset file. Framework may infer some FD representations from raw widths for registered domains such as `hand_pose` or `libero`; other combinations remain constrained by domain registry, adapter, and checkpoint.[C3-FW-ACTION]

### Required adapter schema

An action adapter is incomplete unless it specifies:

| Field | Required definition | Validation probe |
|---|---|---|
| Control space | joint, end-effector, base, camera, or other | one-axis command and decoded response |
| Semantics | absolute or delta/relative | identity and accumulated-motion test |
| Translation | frame, axis order, units, scale | positive/negative single-axis sweep |
| Rotation | representation, frame, composition order | known-angle round trip |
| Joint order | model and environment index mapping | per-joint pulse test |
| Gripper | open/close sign, range, binary/continuous | unloaded open-close calibration |
| Normalization | center, scale, clipping, inverse transform | encode/decode numerical round trip |
| Time | control rate, frame rate, H, duration | timestamp-level H actions/H+1 states check |
| Missing state | padding, mask, interpolation | boundary and dropped-sample tests |

The report's relative SE(3) representation cannot reconstruct a new benchmark's camera frame, control rate, normalization, joint order, or gripper semantics. Version these fields with the data adapter.

## Modeling objectives

### Forward dynamics

Target distribution:

```text
p(o[t+1:t+H] | o[<=t], a[t:t+H-1], instruction/context)
```

Framework FD requires `action_path`. It loads the domain action, pads it to the model's maximum action dimension, and constructs an action-conditioned sequence plan.[C3-FW-INFERENCE; C3-FW-ACTION]

The primary model test is action counterfactual sensitivity. Hold observation, prompt, and seed fixed; vary one action component; compare predicted changes with true environment transitions. A visually plausible continuation that is invariant to action is not successful forward dynamics.

### Inverse dynamics

Target distribution:

```text
p(a[t:t+H-1] | o[t], o[t+1:t+H], instruction/context)
```

Framework ID does not load an external action file. It creates a zero-action placeholder, predicts action, and writes decoded values to `sample_outputs.json`.[C3-FW-INFERENCE; C3-FW-ACTION]

ID is generally multimodal: the same visible transition can be produced by different actions, and occlusion can hide gripper or joint motion. Evaluate executable coverage, terminal-state consistency, and candidate diversity in addition to point error.

### World Action Model

WAM creates an action placeholder and jointly predicts action and a visual rollout.[C3-FW-INFERENCE; C3-FW-ACTION]

This supplies a proposal plus an imagined consequence but is not a closed-loop policy:

- the visual future is a model sample, not an environment transition;
- action still requires a domain decoder and controller;
- re-observation and replanning are external;
- the training objective is not task-success reinforcement learning.

An internal consistency score between predicted action and predicted visual future can be useful, but it must be calibrated against real environment replay to detect shared hallucination.

## Data and training position

Cosmos 3 reports approximately 8.4M action episodes and 61.3K hours across physical domains.[C3-TR, pp.24-25, Figure 9 and Table 4]

| Domain group | Share of action data |
|---|---:|
| Egocentric | 67.4% |
| Autonomous vehicles | 16.3% |
| Robotics | 8.7% |
| Camera | 7.5% |

Do not count all action hours as robot-control supervision; robotics is 8.7% of the reported mixture. Cross-domain transfer can improve general motion structure while leaving robot-domain adapter, contact, and normalization as bottlenecks.

Action enters Generator mid-training as a DM modality, not Reasoner SFT text. It occupies 25% of the published mid-training mixture:[C3-TR, pp.27-30, Table 6]

| Mid-training component | Share |
|---|---:|
| Image | 10% |
| Video | 32% |
| Video plus audio | 8% |
| Action | 25% |
| General transfer | 20% |
| Driving transfer | 5% |

Use [data.md](data.md) for dataset sources and filtering, [training.md](training.md) for optimizer and freeze scope, and [post-training.md](post-training.md) for downstream adaptation.

## Framework adapter contract

### External fields

| Field | Function | Failure risk |
|---|---|---|
| `domain_name` | selects domain ID and action adapter | missing registry entry or checkpoint mismatch |
| `vision_path` | observation or observation transition | view, frame order, crop, or rate mismatch |
| `action_path` | FD action JSON | shape, units, convention, or time mismatch |
| `action_chunk_size` | condition/prediction horizon H | inconsistent observation length |
| `view_point` | view selection or interpretation | benchmark naming mismatch |
| `image_size` | visual size contract | geometric distortion from resize/crop |

[C3-FW-INFERENCE; C3-FW-ACTION]

### H actions and H+1 states

The official adapter sets target visual length to `action_chunk_size + 1`. If observations are too short it replicates boundary frames; if too long it truncates; it then creates the sequence plan, domain ID, and padded action tensor.[C3-FW-ACTION]

This behavior guarantees tensor alignment only:

- replicated frames are not observed static states;
- truncation may remove task completion;
- correct H+1 length does not prove correct time spacing;
- padded action dimensions are not valid domain semantics unless the adapter masks/decodes them correctly.

### Mode-specific loading

- FD loads actions from file and uses them as conditions.
- ID creates placeholders and predicts actions.
- WAM creates placeholders and predicts actions plus visual states.
- action-generation flags must agree with mode validation and decode path.[C3-FW-ACTION; C3-FW-ARGS]

## Optimization levers

### Intervention order

Use the following escalation order:

1. validate serialization, coordinates, normalization, rate, view layout, and H/H+1 alignment;
2. establish frozen-backbone FD and ID baselines with a new domain adapter;
3. tune action input/output projections and normalization;
4. adjust domain sampling, horizon curriculum, and action-loss weight;
5. add state, contact, constraint, or terminal-condition auxiliary losses;
6. selectively unfreeze Generator blocks;
7. add WAM joint training and closed-loop candidate selection;
8. use policy-specific post-training only after offline dynamics are calibrated.

Do not begin by unfreezing all Nano parameters when no adapter round-trip or action-sensitivity test exists.

### Data mixture

An effective target-domain action set should stratify:

- successful, failed, and recovery trajectories;
- no-contact, contact-onset, sustained-contact, and release transitions;
- object, receptacle, pose, and camera variation;
- short primitive and multi-stage horizons;
- common and rare gripper states;
- action magnitude, direction, and near-boundary controls;
- language specificity and paraphrase;
- demonstrations and hard counterfactual negatives.

Oversample informative state transitions rather than long redundant steady segments. Maintain replay from other action domains if cross-domain retention is a goal.

### Objective design

| Objective component | Intended effect | Required diagnostic |
|---|---|---|
| Action regression/flow loss | decode domain actions | per-dimension calibrated error and feasibility |
| Visual rollout loss | model future observation | state/contact metrics, not only pixels |
| Object-state auxiliary loss | preserve task-relevant state | state transition accuracy |
| Contact/collision loss | improve manipulation physics | event F1 and penetration metrics |
| Terminal-state consistency | align ID/WAM with task outcome | final relation and success predicate |
| Action-rollout cycle consistency | align proposal with imagined consequence | calibration against real replay |
| Multi-sample coverage | address inverse-dynamics ambiguity | best-feasible and diversity metrics |

Balance losses using gradient and metric diagnostics. A visual auxiliary that dominates action learning can produce attractive but uncontrollable rollouts; an action-only objective can discard world-state information needed for planning.

## Diagnostics and failure signatures

| Signature | Cause class | Diagnostic or repair entry |
|---|---|---|
| Action shape exception | registry or raw-width mismatch | print domain ID, raw/padded width, mask, and adapter config |
| Numerically valid motion has reversed direction | coordinate frame, absolute/delta, or gripper convention | positive/negative single-axis calibration |
| FD ignores action | weak/incorrect condition or loss | fixed observation and seed with zero/opposite/shuffled actions |
| FD looks plausible but contact is wrong | pixel/judge objective disconnected from dynamics | contact, object pose, relation, and constraint metrics |
| ID mean action is infeasible | multimodal target collapsed to mean | multi-sample generation plus controller-feasibility ranking |
| Trajectory duration is wrong | frame rate, action rate, or chunk misalignment | rebuild alignment from timestamps, not indices |
| End of sequence freezes | missing observations were boundary replicated | mask padded region or collect complete states |
| WAM action and rollout contradict | joint decoding lacks consistency | replay action in real environment and compare transition |
| New domain collapses | adapter/normalization or embodiment shift | frozen-backbone adapter calibration before tower tuning |
| Offline error falls but closed-loop success does not | metric-controller or distribution mismatch | shadow execution, short-prefix loop, and failure-slice analysis |

## Evaluation guidance

The report's Table 18 compares downstream initialization before and after action-inclusive mid-training.[C3-TR, p.65, Table 18]

| Task/domain | Metric | Nano MT-init anchor | Structural interpretation |
|---|---|---:|---|
| Autonomous-vehicle ID | RRE, lower is better | 0.211 | improved over PT-init |
| Autonomous-vehicle ID | RTE, lower is better | 0.014 | improved over PT-init |
| Autonomous-vehicle ID | ATE, lower is better | 0.98 | improved over PT-init |
| Camera FD | RRE, lower is better | 0.147 | improved over PT-init |
| Camera FD | RTE, lower is better | 0.029 | improved over PT-init |
| Camera FD | ATE, lower is better | 1.24 | improved over PT-init |
| Egocentric FD | PSNR, higher is better | 16.12 | improved visual prediction |
| Robotics FD | PSNR, higher is better | 25.52 | improved visual prediction |

Use [evaluation.md](evaluation.md) for exact PT-init values and metric definitions. The table supports action mid-training as a better initialization for those evaluated tasks. It does not establish RoboCasa or DROID closed-loop success, correct contact physics, universal domain transfer, or Policy-DROID performance for base Nano.

For embodied model optimization, decompose evaluation:

| Layer | FD metrics | ID/WAM metrics |
|---|---|---|
| Geometry | object pose and camera reprojection error | end-effector or joint-space error |
| State | open/closed, inside/on, grasp-state accuracy | terminal-state consistency |
| Dynamics | contact/collision F1, penetration, trajectory error | feasibility, IK residual, safety violations |
| Condition sensitivity | action counterfactual separation and calibration | candidate coverage and mode diversity |
| Task utility | rollout-based ranking gain | downstream closed-loop success after controller |

## Experiment guidance

Minimum new-domain program:

1. **Contract tests:** numerical adapter round trip, per-axis calibration, gripper convention, view layout, and time alignment.
2. **Tiny overfit:** one task and short horizon to verify the loss and decoder can fit.
3. **Frozen-backbone baseline:** train only action projections; compare with a simple non-Nano baseline.
4. **FD counterfactuals:** zero, opposite, shuffled, and true actions with matched observations and seeds.
5. **ID multimodality:** sample multiple actions and rank by controller feasibility and terminal state.
6. **WAM consistency:** compare imagined outcomes with replayed true transitions.
7. **Selective unfreezing:** adapter-only versus upper Generator blocks versus broader tower.
8. **Data/objective ablations:** contact sampling, failure trajectories, state auxiliaries, and horizon curriculum.
9. **Closed-loop ladder:** offline replay, shadow, short-prefix execution, then longer receding-horizon control.

Each run records checkpoint revision, code commit, domain ID, raw and canonical action schemas, normalization statistics, observation adapter, rates and timestamps, horizon, trainable modules, data mixture, sampler, metrics, seeds, and raw decoded outputs.

Persist observed execution behavior in [reproduction.md](reproduction.md). Promote robust adapter and objective choices to [optimization-playbook.md](optimization-playbook.md). Register missing domain adapters, normalization details, or proposed discriminating tests in [research-queue.md](research-queue.md).

## Related knowledge

- [IRASim paper entry](../../papers/irasim/README.md) supplies a representative action-conditioned visual forward model, per-frame action modulation, success/failure rollout mixture, and candidate-ranking evidence. Its 2-D/5-D/7-D dataset contracts and external value-model boundary are useful comparisons, not Cosmos3-Nano implementation facts.
- Architecture and DM computation: [architecture.md](architecture.md)
- I/O fields and time contracts: [modalities-and-io.md](modalities-and-io.md)
- Generator sampling and media objectives: [generator.md](generator.md)
- Policy-DROID: [policy.md](policy.md)
- Data, training, and post-training: [data.md](data.md), [training.md](training.md), [post-training.md](post-training.md)
- Evaluation and limitations: [evaluation.md](evaluation.md), [limitations.md](limitations.md)
- Framework execution: [codebase.md](codebase.md), [inference.md](inference.md)
- Source registry: [sources.yaml](sources.yaml)
