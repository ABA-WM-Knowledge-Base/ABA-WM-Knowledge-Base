---
id: world-model-kb.benchmarks.robocasa.codebase
title: Original RoboCasa Code and Evaluator Map
kind: benchmark
status: maintained
last_updated: 2026-08-24
owners:
  - AIBuildAI world-model group
---

# Original RoboCasa Code and Evaluator Map

## Retrieval metadata

**Relevant queries:** RoboCasa v0.2 code, environment class, scene builder, task registry, success check, dataset downloader, evaluation utility, robosuite dependency, robomimic branch, or installation failure.

**Knowledge provided:** the fixed implementation graph, executable entrypoints, external dependency boundary, and paper/code surfaces that remain underspecified for exact reproduction.

**Related pages:** [Scope and versions](scope-and-versions.md) fixes the release; [protocol and metrics](protocol-and-metrics.md) owns evaluator semantics; [reproduction](reproduction.md) owns locally observed state. Model-specific adapters belong to their model entries.

## Fixed repository identity

The canonical code tree is `robocasa/robocasa` tag `v0.2`, commit `756598a5be52e052339bb2d957426e39015c2afb`, package `robocasa==0.2.0`. The package pins Python-side dependencies such as NumPy `1.23.3`, Numba `0.56.4`, MuJoCo `3.2.6`, and Tianshou `0.4.10`, but the README instructs installation of robosuite from mutable `master`. Exact reproduction therefore needs an additional robosuite commit record. [RC24-CODE-V02, `README.md`, `setup.py`]

## Implementation graph

| Knowledge surface | Fixed implementation location | Role |
|---|---|---|
| Base kitchen environment | `robocasa/environments/kitchen/kitchen.py` | Episode initialization, fixtures, objects, observations, metadata, and shared task utilities |
| Atomic tasks | `robocasa/environments/kitchen/single_stage/` | Task reset logic and task-specific `_check_success()` predicates |
| Composite tasks | `robocasa/environments/kitchen/multi_stage/` | Activity-specific object/fixture placement and multi-condition success |
| Scene registry | `robocasa/models/scenes/scene_registry.py` | Layout and style enumeration |
| Scene assembly | `scene_builder.py`, `kitchen_arena.py`, layout/style YAML files | Fixture topology and visual configuration |
| Object registry | `robocasa/models/objects/kitchen_objects.py` and `kitchen_object_utils.py` | Category and instance sampling |
| Environment creation | `robocasa/utils/env_utils.py` | User-facing environment factory |
| Dataset identity | `robocasa/utils/dataset_registry.py` | Task-to-human/MimicGen artifact mapping |
| Dataset download | `robocasa/scripts/download_datasets.py` | Fetch selected dataset types and tasks |
| Evaluation helpers | `robocasa/utils/eval_utils.py` | `create_eval_env` and random-rollout helpers |
| Policy training/evaluation | external `ARISE-Initiative/robomimic` `robocasa` branch | BC-Transformer config generation, checkpoint loading, and rollouts |

[RC24-CODE-V02; RC24-EVAL-DOC-V02; RC24-ROBOMIMIC-BRANCH]

## Documented executable surfaces

The fixed README documents Python 3.10, editable installs of robosuite and RoboCasa, a roughly 5 GB kitchen-asset download, and private macro generation. Smoke surfaces include kitchen-scene visualization, task-demonstration playback, object browsing, and keyboard/SpaceMouse teleoperation. Evaluation documentation exposes `create_eval_env(env_name, seed)` and `run_random_rollouts`, but random rollouts validate environment execution rather than policy quality. [RC24-CODE-V02, `README.md`; RC24-EVAL-DOC-V02]

Official policy support is split across repositories. The RoboCasa docs point to the robomimic `robocasa` branch, generate BC-Transformer training commands through `robomimic/scripts/config_gen/bc_xfmr_gen.py`, and generate checkpoint-evaluation commands through `eval_ckpt.py`. The documentation does not pin the branch commit; `271a76c2d55c8b0f94d3d589f26fcae0d47f64a1` is only the branch head observed for this KB on 24 August 2026, not evidence of the paper-era training revision. [RC24-EVAL-DOC-V02; RC24-ROBOMIMIC-BRANCH]

## Task-name and protocol adapters

Class names, dataset names, and later evaluation aliases are not always identical. The original docs use names such as `PickPlaceCounterToCabinet`; later policy clients use `PnPCounterToCab`. A model adapter must resolve the environment registry at its pinned revision and save the final ordered task list. Silent alias substitution can change result ordering or omit a task.

Observation and action adapters are outside the benchmark core. They must document camera names and resolutions, image orientation and normalization, proprioceptive frame and quaternion order, action frame and scaling, gripper sign, controller configuration, action chunking, and base-control dimensions. X-WAM, for example, rotates end-effector axes, converts `xyzw` to `wxyz`, pads the single-arm state to 16 dimensions, and negates the gripper channel on output. Those transformations belong to the X-WAM evaluation client, not to a universal RoboCasa API. [XWAM-CODE-72CF, `evaluation/robocasa_client.py`, `evaluation/policy_server.py`]

## Reproducibility gaps visible in code

- robosuite is requested from mutable `master`; a compatible commit is not fixed by `v0.2`.
- Asset archives are downloaded outside Git and require their own version or hashes.
- The current external robomimic branch can differ from the paper implementation.
- The paper's five fixed atomic evaluation scenes and all training seeds are not represented as one immutable scenario manifest in the core repository documentation.
- Task `_check_success()` is the terminal metric but does not record near-success, collision, or progress.
- Current project documentation may describe RoboCasa365 even when imported through the same domain.

These are experiment-identity fields, not reasons to substitute RoboCasa365 or an unpinned environment silently.

## Sources

Implementation sources resolve through [`sources.yaml`](sources.yaml): `RC24-CODE-V02`, `RC24-EVAL-DOC-V02`, and `RC24-ROBOMIMIC-BRANCH`. X-WAM adapter code resolves through the [X-WAM paper registry](../../papers/x-wam/sources.yaml).
