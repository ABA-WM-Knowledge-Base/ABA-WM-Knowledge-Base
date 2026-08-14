---
id: world-model-kb.papers.mimicgen.codebase
title: MimicGen Released Implementation Graph
kind: reference
status: draft
last_updated: 2026-08-13
owners:
  - AIBuildAI world-model group
---

# MimicGen Released Implementation Graph

## Retrieval metadata

**Relevant queries:** mimicgen code, DataGenerator, selection strategy implementation, task spec, subtask term signal, env interface, waypoint trajectory, generate_dataset script, prepare_src_dataset, datagen_info, mimicgen datasets download, mimicgen license.

**Knowledge provided:** the pinned official repository revision, the mechanism-to-symbol map for parsing, selection, transformation, interpolation, execution, and acceptance, the configuration and environment contracts, and the boundaries between what the paper reports and what the release contains.

**Related pages:** [`paper.md`](paper.md) owns the paper's mechanisms and evidence; [`reproduction.md`](reproduction.md) owns local execution state; [`optimization-transfer.md`](optimization-transfer.md) owns intervention hypotheses.

## 1. Pinned revision and release history

- Repository: `NVlabs/mimicgen` (official CoRL 2023 release). Local clone pinned at commit `72bd767c255545f462e7ccfb2731f2e5d4c1d9bb` (2025-08-16, merge of PR #64 fixing dataset parsing). [MIMICGEN-CODE-CURRENT]
- Release timeline from the README: v0.1.0 initial code and paper release 2023-09-28; v0.1.1 dataset license relaxed to CC-BY 4.0 on 2024-04-04; **v1.0.0 full data-generation code release 2024-07-09, about nine months after the paper**; v1.0.1 moved dataset hosting to Hugging Face 2024-09-19. The repository still receives fixes as of the pinned commit. [MIMICGEN-CODE-CURRENT, README.md]
- Licenses: code under the custom NVIDIA License (not an OSI license; business use routed to NVIDIA Research Licensing); released datasets under CC-BY 4.0. [MIMICGEN-CODE-CURRENT, LICENSE, README.md]
- Released datasets: over 48,000 demonstrations across 12 tasks. The paper reports 50K+ across 18 tasks; the Factory (Isaac Gym) tasks and real-robot data are not part of the public dataset or environment release (see Sec. 6). [MIMICGEN-PAPER-V1, p.1; MIMICGEN-CODE-CURRENT, README.md]

## 2. Repository layout

```text
mimicgen/
|-- configs/         # MG_Config, MG_TaskSpec, robosuite config classes
|-- datagen/         # DataGenerator, DatagenInfo, selection strategies, waypoints
|-- env_interfaces/  # MG_EnvInterface abstract contract + robosuite implementations
|-- envs/robosuite/  # 12 task families in 9 modules + shared base single_arm_env_mg.py; D2 variants in four
|-- exps/templates/robosuite/  # per-task generation config templates (JSON)
|-- models/          # asset files
|-- scripts/         # end-to-end drivers and dataset tooling
`-- utils/           # pose math, config/file/robomimic helpers
```

## 3. Mechanism-to-implementation map

| Paper mechanism | Implementation | Symbol |
|---|---|---|
| Parse source demos into object-centric segments | `scripts/prepare_src_dataset.py` adds per-timestep DatagenInfo to the source hdf5; `scripts/annotate_subtasks.py` and `scripts/get_source_info.py` support annotation and inspection | `DatagenInfo` in `datagen/datagen_info.py` |
| Subtask boundary detection and randomization | boundaries derived from `subtask_term_signal` with `subtask_term_offset_range` jitter, resampled per attempt | `DataGenerator.randomize_subtask_boundaries` (`datagen/data_generator.py:82`) |
| Reference segment selection (random / nearest-neighbor) | registry-based strategy classes; `nn_k` for neighbor count | `RandomStrategy`, `NearestNeighborObjectStrategy`, `NearestNeighborRobotDistanceStrategy` (`datagen/selection_strategy.py:98,132,209`); dispatch in `DataGenerator.select_source_demo` (`data_generator.py:116`) |
| Object-frame SE(3) segment transform (the T_C't_W equation) | pose math on the sliced target-pose sequence | `PoseUtils.transform_source_data_segment_using_object_pose` (`utils/pose_utils.py`) |
| Interpolation bridge to segment start | waypoint container merge with `num_steps_interp` and `num_steps_fixed`; noise optionally gated during interpolation | `WaypointTrajectory.merge`, `.add_waypoint_sequence_for_target_pose`, `.execute` (`datagen/waypoint.py:251,175,313`) |
| Segment execution as delta-pose actions + source gripper actions | target-pose-to-action conversion inside the env interface contract | `MG_EnvInterface` abstract methods (`env_interfaces/base.py`) |
| Success-only acceptance | per-attempt success flag; only successful episodes written and merged | `DataGenerator.generate` returns `success`; driver keeps successes (`scripts/generate_dataset.py`), `scripts/merge_hdf5.py` combines them |
| Generate-until-1000-successes protocol | `guarantee` flag: loop until N successes if set, else N attempts | `mg_config.experiment.generation.guarantee` read in `scripts/generate_dataset.py:303` |
| Data generation rate reporting | success/attempt statistics summary | stats helper `get_important_stats` (`scripts/generate_dataset.py:49-89`) |
| Per-task hyperparameters (sigma, interpolation steps, selection strategy) | JSON templates per task; sweep generators for paper experiments | `exps/templates/robosuite/*.json`; `scripts/generate_core_configs.py` |

## 4. Generation call chain

`scripts/generate_dataset.py` (driver) -> builds env + `MG_EnvInterface` -> constructs `DataGenerator` from `MG_TaskSpec` + prepared source hdf5 -> per attempt calls `DataGenerator.generate(env, env_interface, select_src_per_subtask, ...)`:

1. `env.reset()`; record initial simulator state.
2. `randomize_subtask_boundaries()` resamples every source demo's subtask segmentation for this attempt.
3. Per subtask: `env_interface.get_datagen_info()` provides current eef and object poses; `select_source_demo(...)` runs the configured strategy (always on the first subtask; on every subtask only if `select_src_per_subtask`).
4. Slice the chosen source segment (eef poses, target poses, gripper actions); on the first subtask (or with `transform_first_robot_pose`) prepend the source's first robot pose so interpolation targets where the source robot started.
5. `PoseUtils.transform_source_data_segment_using_object_pose` re-expresses target poses under the current object pose.
6. Build `WaypointTrajectory`; `merge(..., num_steps_interp, num_steps_fixed, action_noise * apply_noise_during_interpolation)` prepends the interpolation bridge (from the previous segment's last target pose when `interpolate_from_last_target_pose`, else from the current robot pose); `pop_first()`; `execute(...)` steps the environment.
7. Success accumulates across subtask executions as `generated_success = generated_success or exec_results["success"]`.

The driver counts the attempt, keeps the episode only on success, and repeats until the configured number of successes (`guarantee`) or attempts is reached; successful per-episode hdf5s are merged by `merge_hdf5.py`.

## 5. Contracts

- **Subtask spec** (`MG_TaskSpec.add_subtask`, `configs/task_spec.py:23`): `object_ref`, `subtask_term_signal`, `subtask_term_offset_range`, `selection_strategy` (default `"random"`), `selection_strategy_kwargs`, `action_noise` (default 0.0), `num_interpolation_steps` (default 5), `num_fixed_steps` (default 0), `apply_noise_during_interpolation` (default False). Paper-reported defaults (sigma = 0.05) live in the per-task JSON templates, not in the class defaults.
- **Environment interface** (`MG_EnvInterface`, `env_interfaces/base.py`): abstract `get_robot_eef_pose`, target-pose/action conversions, `get_object_poses`, `get_subtask_term_signals`, composed by `get_datagen_info`; per-simulator subclasses register through `MG_EnvInterfaceMeta`. This is the surface a new simulator or a RoboCasa-era pipeline must implement.
- **DatagenInfo** (`datagen/datagen_info.py`): per-timestep eef pose, object poses, gripper action, target pose, and subtask termination signals; written into source hdf5s by `prepare_src_dataset.py` and consumed by the generator.

## 6. Paper/code boundaries and code-level observations

1. **Environment coverage:** the release contains the robosuite/MuJoCo environments only: 12 task families in 9 modules plus the shared base `single_arm_env_mg.py`. The paper's Factory (Isaac Gym) high-precision tasks (Nut-and-Bolt, Gear, Frame Assembly) and the physical-robot stack are not in the release; their results are not locally reproducible from this repository. [MIMICGEN-PAPER-V1, p.5; MIMICGEN-CODE-CURRENT]
2. **A third selection strategy exists in code:** `NearestNeighborRobotDistanceStrategy` alongside the paper-documented random and nearest-neighbor-object strategies. The appendix pages we verified (pp.37-38) describe random and `nnk = 3` object-pose selection; treat the robot-distance variant as released-but-not-covered-by-our-verified-pages rather than a confirmed paper omission. [MIMICGEN-CODE-CURRENT, `selection_strategy.py:209`]
3. **Success semantics:** acceptance is accumulated with a logical OR across subtask-segment executions, so an episode counts as successful when the success check fires at any execution step, not only after the final segment completes. The paper text says success is checked "after executing all segments"; behaviorally equivalent for tasks whose success predicate only fires at completion, but the code semantics matter when adapting to tasks with reversible success states. [MIMICGEN-PAPER-V1, p.4; MIMICGEN-CODE-CURRENT, `data_generator.py`]
4. **DGR accounting:** attempts that raise environment errors are retried without counting toward the attempt total (`generate_dataset.py:322`), so the reported data generation rate's denominator excludes crashed attempts. Relevant when comparing DGR across environments with different crash rates. [MIMICGEN-CODE-CURRENT]
5. **Generation options beyond the paper text:** `transform_first_robot_pose` and `interpolate_from_last_target_pose` change interpolation targets and are exposed as arguments with quality implications noted in docstrings; the paper does not discuss them. [MIMICGEN-CODE-CURRENT, `data_generator.py:182`]
6. **Training is external:** policy learning is delegated to robomimic (BC-RNN); this repository only generates configs (`generate_core_training_configs.py`) and datasets. Claims about policy results depend on the robomimic version used, which the entry's reproduction records must pin separately. [MIMICGEN-CODE-CURRENT]

## Sources

- [MIMICGEN-PAPER-V1] Mandlekar et al., *MimicGen: A Data Generation System for Scalable Robot Learning using Human Demonstrations*, CoRL 2023, arXiv:2310.17596v1 (26 Oct 2023), local PDF and verified text extraction.
- [MIMICGEN-CODE-CURRENT] `NVlabs/mimicgen` at commit `72bd767c255545f462e7ccfb2731f2e5d4c1d9bb` (2025-08-16), local clone under `external/mimicgen`, NVIDIA License; datasets CC-BY 4.0 on Hugging Face.

Line numbers refer to the pinned commit and drift with any other revision.
