---
id: world-model-kb.models.cosmos3-nano.policy
title: Cosmos3-Nano Policy-DROID Adaptation Reference
kind: reference
status: maintained
last_updated: 2026-08-11
owners:
  - AIBuildAI world-model group
---

# Cosmos3-Nano Policy-DROID Adaptation Reference

## Retrieval metadata

**Relevant queries:** Policy-DROID identity, observation/action contract, action chunking, policy serving, DROID adaptation, embodiment transfer, latency, or closed-loop evidence.

**Knowledge provided:** checkpoint lineage, DROID-specific interfaces, server semantics, adaptation variables, failure interpretations, safety evidence, and published policy results. DROID and RoboLab metrics belong to the specialized checkpoint, not base Nano.

**Related pages:** [Architecture](architecture.md) covers base-model structure; [Reasoner](reasoner.md) covers text plans; [Action modeling](action-modeling.md) covers base action modes; [Generator](generator.md) covers media generation.

## Canonical identity and lineage

`nvidia/Cosmos3-Nano-Policy-DROID@6706d7680581c255ff61e0f3bb49d90eac55c79e` is a DROID-specific checkpoint post-trained from mid-trained Cosmos3-Nano. It consumes a language instruction, proprioceptive state, and a canonical three-view RGB canvas and generates 32 future absolute joint-position actions. Training also predicts future RGB as an auxiliary target. The published and fixed-server contract uses 15 Hz, 4 denoising steps, guidance 3, and flow shift 5.[C3-POLICY-DROID-HF; C3-TR, pp.31-32 and p.73, Table 21; C3-FW-POLICY-SERVER]

```text
Reasoner training
  -> Generator pre-training
  -> action-inclusive mid-training
  -> DROID-specific post-training
  -> Cosmos3-Nano-Policy-DROID
```

Policy post-training adds newly initialized action encoder, action-decoding MLP, and action embeddings. Action-specific modules use a 5x learning-rate multiplier.[C3-TR, pp.31-32]

Bind every experiment row to the full checkpoint ID and revision. This checkpoint is not an alias for `nvidia/Cosmos3-Nano`, and its results do not establish zero-shot performance on another embodiment or benchmark.

## Surface boundaries

| Surface | Native output | Specialized control post-training | Correct use |
|---|---|---|---|
| Reasoner | natural-language tokens | no | perception, explanation, high-level planning |
| Base inverse dynamics | domain action representation | action mid-training only | infer candidate action from transition |
| Base WAM | action plus visual rollout | action mid-training only | joint proposal and imagined consequence |
| Policy-DROID | 32-step DROID action chunk | yes | DROID-contract closed-loop control |

[C3-TR, pp.25-32; C3-FW-INFERENCE; C3-FW-POLICY-DROID-DOC; C3-FW-POLICY-SERVER]

The policy can predict future video as an auxiliary output, but the control surface is action generation. Runtime may disable video decoding without changing the training lineage.

## Observation and action contract

### Training data

The report describes the DROID corpus as approximately 76,000 trajectories, 350 hours, 86 tasks, and 564 scenes.[C3-TR, pp.31-32] These values describe training diversity, not distributional equivalence to a target benchmark.

### Input

Each sample contains:[C3-TR, pp.31-32]

- language instruction;
- current proprioceptive state;
- a 540x640 canvas built from three RGB views;
- aligned action sequence and auxiliary future-RGB target.

The fixed server preserves the wrist view as a full region and downsizes two exterior views before composing the canvas.[C3-FW-POLICY-SERVER] View order, crop, scale, and placement are checkpoint inputs. A generic three-image concatenation or a single camera does not satisfy the contract.

### Output

Policy predicts 32 future **absolute joint-position actions** at a 15 Hz time scale and an auxiliary future RGB target.[C3-TR, pp.31-32] The report gives base learning rate `2e-4`, with the higher multiplier for action-specific modules.

The auxiliary visual objective can regularize future-state structure, but it does not guarantee pixel-accurate rollout or safe action. Runtime need not decode the predicted video.

### Fixed inference defaults

| Parameter | Policy-DROID value |
|---|---:|
| Action chunk | 32 |
| Observation/action scale | 15 Hz |
| Denoising steps | 4 |
| Classifier-free guidance | 3 |
| Flow shift | 5 |
| RGB canvas | 540x640 |
| Fixed-server default action dimension | 8 |
| Framework resolution bucket | 480 |
| Decode predicted video | false |

[C3-TR, p.73, Table 21; C3-FW-POLICY-SERVER]

Four-step diffusion is a policy latency-quality tradeoff, not a general Generator default. Thirty-two actions span approximately 2.13 seconds at 15 Hz, but this does not imply executing all 32 open loop.

## Official server semantics

The fixed Framework separates a CUDA policy server from a RoboLab simulation client. Nano and Edge use the same server entry with different checkpoint arguments.[C3-FW-POLICY-DROID-DOC]

Canonical Nano server properties:

- checkpoint `nvidia/Cosmos3-Nano-Policy-DROID`;
- default port 8000;
- observation dictionary input;
- dictionary output containing action and optional predicted video;
- `joint_pos` or `midtrain` action spaces;
- CUDA runtime;
- consolidated safetensors by default, with an explicit option for DCP checkpoint layout.[C3-FW-POLICY-SERVER]

The server constructs state from observation/history, generates action, strips the matching history prefix, and flips the gripper convention for the external interface.[C3-FW-POLICY-SERVER] Raw-model integration must reproduce these transforms exactly; otherwise apparent model errors may be contract errors.

## Canonical closed-loop pattern

```text
observe three RGB views and proprioception
  -> construct canonical 540x640 canvas
  -> generate 32-step action chunk
  -> strip history and inverse-normalize
  -> convert gripper and action-space conventions
  -> apply limits, IK/collision, and controller checks
  -> execute a short prefix
  -> re-observe and replan
```

The number of executed actions before replanning is an independent control variable. Optimize it against latency, prediction drift, contact sensitivity, and observation noise.

## Target-domain contract diff

Before adaptation, produce a machine-readable source-to-target diff:

| Contract field | DROID source | Required target entry |
|---|---|---|
| Embodiment | DROID robots in published corpus | robot model, joint limits, kinematics |
| Action space | absolute joint position; server also exposes named spaces | target control space and conversion |
| Action width/order | checkpoint/server-defined | exact target indices and masks |
| Gripper | server conversion is part of interface | sign, range, binary/continuous mapping |
| Observation cameras | wrist plus two exterior views | camera names, ordering, intrinsics/extrinsics, crop |
| Canvas | 540x640 canonical composition | deterministic target composition |
| Proprioception | server observation keys | target keys, units, normalization |
| Rate | 15 Hz | target observation and control rates |
| Horizon | 32 generated actions | generated and executed prefix lengths |
| Language | DROID instruction distribution | target task grammar and specificity |
| Success | RoboLab/RoboArena/MolmoSpaces protocols | target predicates and termination |

Do not start tower tuning until the diff has no unspecified coordinate, normalization, or timing field.

## Optimization levers

### Adaptation order

1. Reproduce the fixed server preprocessing and post-processing on recorded DROID-format samples.
2. Implement and unit-test the target observation/action contract without model inference.
3. Train only new target action projections and normalization layers with the Nano backbone frozen.
4. Add target-domain policy post-training with replay from source or general action data.
5. Tune action-specific learning-rate multiplier, horizon curriculum, and executed prefix.
6. Add or replace auxiliary future-RGB targets with task-state, depth, segmentation, or contact targets when they improve decision metrics.
7. Selectively unfreeze upper Generator blocks only if adapter-only tuning plateaus.
8. Validate closed-loop behavior through replay, shadow, short-prefix simulation, and increasing task complexity.

### Observation optimization

Evaluate view layout independently of action learning:

- canonical versus swapped exterior views;
- wrist view present versus removed;
- source-like canvas versus native multi-camera tokens;
- crop and resolution sweeps for gripper-object contact;
- current frame versus short history;
- RGB alone versus optional target-domain state auxiliaries.

If changing the 540x640 layout, initialize a new adapter or explicitly fine-tune the visual pathway. Silent layout substitution shifts the spatial distribution.

### Action optimization

Compare action representations under matched data and controller:

- absolute joint position versus delta joint position;
- joint versus end-effector delta;
- 6D versus other rotation representations when applicable;
- fixed 32-step target versus shorter/variable horizon;
- 4-step diffusion versus latency-quality alternatives;
- single sample versus multiple candidates with a feasibility or world-model selector.

Use per-dimension normalization and saturation diagnostics. Track whether gains come from better direction, magnitude, gripper timing, or recovery behavior.

### Language optimization

Instruction specificity is a demonstrated system variable. Train and evaluate matched vague, default, and specific instructions for the same trajectories. Separate:

- object identification;
- spatial relation;
- ordered subgoals;
- termination condition;
- recovery instruction.

Do not label a gain as improved Reasoner planning when more specific language simply reduces policy ambiguity.

### Auxiliary world-model targets

Future RGB can regularize dynamics but may overemphasize pixels. Candidate target-domain auxiliaries include object pose, receptacle relation, gripper state, depth, segmentation, contact onset, collision, and success predicate. Add one target at a time and require improvement in action selection or closed-loop success, not only auxiliary accuracy.

## Diagnostics and failure signatures

| Signature | Likely cause | Minimum diagnostic |
|---|---|---|
| Canvas is valid but actions are wrong | view order/crop differs from training | persist source images and composed canvas; compare pixel geometry with server code |
| Arm moves in wrong direction or scale | absolute joint mapping, joint order, or normalization | one-joint sweep and encode/decode round trip |
| Gripper command is inverted | external convention differs from server | unloaded open/close calibration |
| Later chunk actions drift | open-loop horizon exceeds valid prediction | shorten execution prefix and sweep replan rate |
| Vague instructions fail more often | language ambiguity and training distribution | matched specificity test with identical task state |
| New objects/scenes cause collapse | visual and task distribution shift | separate perception probes, offline action errors, and closed-loop tests |
| Predicted video is plausible but action fails | auxiliary visual objective is not controller feasibility | environment replay plus IK, collision, and safety checks |
| Server cannot load weights | consolidated safetensors/DCP mismatch | inspect checkpoint layout; do not substitute base Nano |
| Latency exceeds control budget | denoising, video decode, hardware, or transport | disable video decode and profile preprocess/model/network/controller separately |
| Output history is off by one | server history stripping/chunk convention | log raw output, stripped output, and executed indices |
| Offline action error improves but success does not | metric, horizon, or distribution mismatch | failure-slice closed-loop evaluation and terminal-state metrics |
| Source tasks regress after target tuning | catastrophic forgetting | source replay, lower trainable scope, and source retention suite |

## Safety boundary

Policy output requires downstream enforcement of joint position, velocity, and acceleration limits; workspace constraints; collision and self-collision checks; controller feasibility; observation timeout; and emergency stop. The official server does not make the checkpoint a hard-safety controller.[C3-FW-POLICY-SERVER]

Escalate execution in this order:

1. observation/action schema and numerical round trip;
2. dataset replay with action and terminal-state metrics;
3. simulator shadow mode with no action execution;
4. simulator execution of one or a short action prefix;
5. receding-horizon simulation under a restricted task set and safety envelope;
6. broader simulation only after failure thresholds are met;
7. physical robot deployment only under separate authorization and safety review.

## Published evaluation anchors

### RoboLab instruction specificity

The report gives overall Policy-DROID success by instruction specificity:[C3-TR, p.68, Table 19]

| Instruction form | Overall success |
|---|---:|
| Vague | 20.6 |
| Default | 36.8 |
| Specific | 39.7 |

Complex tasks reach 29.4 under specific instructions.[C3-TR, p.68, Table 19] This supports instruction specificity as an optimization variable. It does not isolate whether the gain comes from language understanding, reduced action ambiguity, or both.

### RoboArena and MolmoSpaces

The report records Policy-DROID as rank 1 on the paper-time RoboArena snapshot and reports 39.0 on MolmoSpaces.[C3-TR, pp.68-70] Treat the rank as a dated snapshot and preserve the exact external protocol.

### LIBERO is a separate branch

LIBERO-specific post-training compares mid-training initialization (MT-init) with pre-training initialization (PT-init). MT-init reports 24.6/91.4/95.8/97.4 at 500/1000/1500/2000 iterations; PT-init reports 0.0/73.8/93.4/95.2.[C3-TR, p.70, Table 20]

This supports action-inclusive mid-training as a more sample-efficient initialization for that separate LIBERO experiment. It is not zero-shot Policy-DROID performance and must not be attached to the DROID checkpoint.

The narrow supported conclusions are:

- action/world-model mid-training can improve initialization for specialized DROID and LIBERO post-training;
- a DROID-specific Nano policy can perform multitask control under its reported protocols;
- instruction specificity materially affects system performance;
- few-step diffusion can support a lower-latency action surface.

Do not infer zero-shot control of arbitrary arms, target-benchmark transfer, action safety from auxiliary video, permanent leaderboard rank, or LIBERO performance for Policy-DROID.

## Experiment guidance

Minimum target-domain adaptation matrix:

| Factor | Baseline | Variants |
|---|---|---|
| Trainable scope | action modules only | plus visual connector; upper Generator blocks; broader tower |
| Initialization | action-mid-trained Nano | task-relevant alternative and ablated initialization |
| Action space | source-like absolute joint position | delta joint; end-effector delta |
| Horizon | 32 generated, short executed prefix | shorter generation; variable prefix/replan |
| Views | canonical source-like composition | target-native layouts and view ablations |
| Language | default | vague, specific, structured subgoals |
| Auxiliary target | future RGB | none; state; depth; segmentation; contact |
| Data | target successes | plus failures, recovery, contact-rich, and source replay |
| Sampling | 4 steps, guidance 3, shift 5 | controlled latency-quality grid |

Required metrics:

- schema, normalization, and action-bound violation rate;
- offline per-joint and gripper error;
- terminal-state and task-predicate accuracy;
- candidate feasibility and action diversity;
- preprocess, model, network, and controller latency;
- short-prefix and full-task closed-loop success;
- success by task, object, view, instruction specificity, and failure class;
- retention on source or general action probes;
- safety intervention rate.

Record checkpoint revision, code commit, server configuration, exact observation dictionary, raw and transformed actions, executed prefix, timestamps, normalization, safety clipping, seeds, and raw model outputs.

Execution outcomes belong in [reproduction.md](reproduction.md). Stable adaptation choices belong in [optimization-playbook.md](optimization-playbook.md). Unresolved details such as DROID camera calibration, replan horizon, action-space conversion, or target-domain transfer belong in [research-queue.md](research-queue.md).

## Related knowledge

- Data and policy post-training: [data.md](data.md), [training.md](training.md), [post-training.md](post-training.md)
- Action representation and WAM: [action-modeling.md](action-modeling.md)
- Input and server contracts: [modalities-and-io.md](modalities-and-io.md), [codebase.md](codebase.md), [inference.md](inference.md)
- Published protocols and limitations: [evaluation.md](evaluation.md), [limitations.md](limitations.md)
- Source registry: [sources.yaml](sources.yaml)
