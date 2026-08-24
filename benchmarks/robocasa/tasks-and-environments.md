---
id: world-model-kb.benchmarks.robocasa.tasks-and-environments
title: Original RoboCasa Tasks and Environment Distribution
kind: benchmark
status: maintained
last_updated: 2026-08-24
owners:
  - AIBuildAI world-model group
---

# Original RoboCasa Tasks and Environment Distribution

## Retrieval metadata

**Relevant queries:** RoboCasa task class, atomic skill, composite task, kitchen layout, style, texture, object category, PandaOmron, camera, controller, reset distribution, or success predicate.

**Knowledge provided:** the task taxonomy, scene and asset construction, embodiment and observation surfaces, and variables that define the benchmark distribution.

**Related pages:** [Scope and versions](scope-and-versions.md) fixes the Original release; [datasets](datasets.md) maps task coverage to trajectories; [protocol and metrics](protocol-and-metrics.md) binds these environments to rollouts. General embodiment contracts are owned by [robotics and embodied AI](../../foundations/embodied-systems/robotics-and-embodied-ai.md).

## Environment composition

RoboCasa builds room-scale kitchens on robosuite and MuJoCo. A scene is a floor-plan/layout and architectural-style combination. The original release models 10 layouts and 12 styles, producing 120 base scenes. Layouts control fixture topology and dimensions; styles control textures, fixture instances, cabinet panels, and handles. Four texture families—walls, floors, counters, and cabinet panels—each contain 100 MidJourney-generated alternatives used for additional appearance randomization. [RC24-PAPER-V1, pp.4-5, Figures 3-4]

The asset library contains 2,509 curated 3D objects across 153 categories; 1,592 were sourced from Luma.ai text-to-3D output and the remainder include Objaverse assets. Fixtures and appliances are articulated and stateful: doors and drawers move, stove knobs affect burner state, and buttons or levers participate in task predicates. Visual diversity therefore coexists with MuJoCo contact dynamics and explicit simulator state; image realism is not itself the success oracle. [RC24-PAPER-V1, p.5, Figure 5]

## Atomic task taxonomy

The 25 atomic tasks instantiate eight skill families. The names below are semantic families; the fixed code contains aliases such as `PnPCounterToCab` for class-level entrypoints. [RC24-PAPER-V1, pp.5, 12-13, Figure 11; RC24-CODE-V02, `robocasa/environments/kitchen/single_stage/`]

| Skill family | Task surface | Diagnostic burden |
|---|---|---|
| Pick and place | Eight source–destination variants among counter, cabinet, sink, microwave, and stove | Object diversity, grasp affordance, localization, collision-free transport |
| Open/close doors | Single and double cabinet or microwave doors | Articulation geometry, contact, force direction, multi-stage completion |
| Open/close drawers | Drawer opening and closing | Handle localization and constrained motion |
| Twist knobs | Turn stove burners on or off | Small control target, rotation direction, discrete state transition |
| Turn levers | Faucet on/off and sink-spout turning | Articulated state estimation and precise contact |
| Press buttons | Coffee-machine and microwave controls | Small target and task-state verification |
| Insertion | Place/remove mug at the coffee-machine holder | Fine alignment and tolerance |
| Navigation | Move the mobile manipulator to a named fixture | Base motion and room-scale localization |

Atomic task variants can bind the language goal to an object category, burner, or target appliance. Therefore “same task class” need not mean the same language, object, or fixture instance distribution.

## Composite task taxonomy

The 75 composite tasks sequence atomic-style subtasks into 20 activity families, including brewing, washing dishes, restocking, chopping, making toast, defrosting, boiling, meat preparation, table setting and clearing, sanitizing, snack preparation, cabinet organization, washing produce, frying, reheating, mixing, baking, serving, and steaming. GPT-4 generated high-level activity candidates; GPT-4 and Gemini 1.5 generated task blueprints. Humans rejected logically invalid proposals, modified others, and wrote the executable task code. LLM generation is thus a task ideation mechanism, not automatic verified environment synthesis. [RC24-PAPER-V1, pp.5-6, Figure 6]

Composite tasks differ materially in horizon and skill transitions. Some are restricted to compatible fixtures or scenes. The task catalog should not be treated as 75 exchangeable i.i.d. episodes, and average success without the exact subset hides whether failure comes from perception, one primitive, transition logic, or compounding horizon.

## Embodiment and observation contracts

The paper's primary simulated policy experiments use a Franka Panda arm on an Omron mobile base, resembling Omni-Frankie. The BC-Transformer receives a 10-observation history, proprioception, language encoded with CLIP, and three camera views: eye-in-hand plus left and right workspace cameras. Dedicated ResNet-18 encoders and FiLM fuse visual and language features; the policy predicts 10 actions and executes only the first before replanning. [RC24-PAPER-V1, pp.6, 11]

The simulator uses workspace end-effector control. Paper timing is 25 simulation steps per second (`0.04 s` per step); a measured rendered run on RTX A5000 and AMD EPYC 7543 reached 25.2 fps, while no-render stepping reached 31.9 fps. These throughput measurements describe simulator execution, not policy inference latency. [RC24-PAPER-V1, p.11]

Later 24-task WAM evaluations can use the same `PandaOmron` embodiment but different camera sizes, histories, action chunks, control transforms, horizons, scene tuples, and seeds. For example, the released X-WAM client uses three 256×256 views, a 16-dimensional padded proprioceptive vector, 7-dimensional single-arm actions, and task-specific maximum steps. Those values belong to that model's protocol and do not redefine every RoboCasa evaluation. [XWAM-CODE-72CF, `evaluation/robocasa_client.py`]

## Success semantics

Each environment implements a task-specific binary success check, exposed through the environment's `_check_success()` path. A success predicate can combine object containment, contact-independent geometric thresholds, and appliance or fixture state. It does not score motion smoothness, collision count, action efficiency, task progress, or visual prediction quality unless an external evaluator adds those measures. Consequently, two policies with equal binary success can differ substantially in safety and behavior quality. [RC24-CODE-V02, task classes and `robocasa/environments/kitchen/kitchen.py`]

## Sources

Core source identities are `RC24-PAPER-V1` and `RC24-CODE-V02` in [`sources.yaml`](sources.yaml). The X-WAM code source is owned by the [X-WAM Paper entry](../../papers/x-wam/sources.yaml).
