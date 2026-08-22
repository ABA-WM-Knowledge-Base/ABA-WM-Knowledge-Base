---
id: world-model-kb.papers.vlabench.codebase
title: VLABench Released Implementation Graph
kind: reference
status: maintained
last_updated: 2026-08-21
owners:
  - AIBuildAI world-model group
---

# VLABench Released Implementation Graph

## Retrieval metadata

**Relevant queries:** VLABench repository, Evaluator, evaluate_single_episode, load_env, track json, task_config.json, max_episode_length, download_assets.py, requirements.txt mujoco 3.2.2, dm_control 1.0.22, evaluate_policy.py, Policy base class, control_mode ee, get_qpos_from_ee_pos, convert_to_lerobot.py, data formats.

**Knowledge provided:** the pinned repository's call graph for interactive evaluation, the track configuration surface, data-format tooling, dependency pins, and the known defects with their code locations.

**Related pages:** [`paper.md`](paper.md) owns the protocol; [`reproduction.md`](reproduction.md) owns execution state; [Xiaomi-Robotics-1 policy](../../models/xiaomi-robotics-1/policy.md) owns one concrete client built on this API.

## 1. Revision policy

All mappings use `OpenMOSS/VLABench@cf588fe60c0c7282174fe979f5913170cfe69017` (2025-11-11). Xiaomi's eval README installs `main` without a pin; later commits can change the evaluator or the tracks. [VLAB-CODE]

## 2. Repository map

```text
VLABench/
|-- VLABench/
|   |-- configs/evaluation/tracks/track_{1_in_distribution,2_cross_category,3_common_sense,4_semantic_instruction,6_unseen_texture}.json
|   |-- configs/task_config.json              per-task evaluation.max_episode_length overrides (100 poker/painting series, 300 add_condiment series)
|   |-- evaluation/evaluator/base.py          Evaluator (interactive policy evaluation)
|   |-- evaluation/evaluator/vlm.py           non-interactive VLM evaluation
|   |-- evaluation/model/policy/{base,openvla,openpi,gr00t}.py   Policy interface and reference adapters
|   |-- envs/, tasks/, robots/                load_env, task classes and conditions, Franka (IK, gripper predicate)
|   `-- assets/                               populated by scripts/download_assets.py (Google Drive zips)
|-- scripts/{evaluate_policy,evaluate_vlm,trajectory_generation,convert_to_rlds,convert_to_lerobot,download_assets}.py
|-- sh/evaluation/example_multi_gpu_eval.sh, sh/data_generation/multi_gpu_data_generation.sh
|-- third_party/openpi (submodule), docs/issues.md, tutorials/
`-- requirements.txt
```

[VLAB-CODE]

## 3. Interactive evaluation call path

```text
Evaluator(tasks, n_episodes, episode_config=<track json>, max_substeps=1, metrics=[...], save_dir, visulization)
  .evaluate(policy):
     for task: cap = task_config[task].evaluation.max_episode_length or 200
       for i < n_episodes: evaluate_single_episode(policy, task, i, episode_config[task][i])
          env = load_env(task, episode_config=cfg, random_init=False, eval=False, run_mode="eval"); env.reset()
          loop: obs = env.get_observation(require_pcd=False); obs["instruction"] = env.task.get_instruction()
                if policy.control_mode == "ee": pos, euler, gripper = policy.predict(obs); qpos = env.robot.get_qpos_from_ee_pos(...)
                timestep = env.step([qpos, gripper]); success = timestep.last()
          info = {success, consumed_step, intention_score = env.get_intention_score(0.1), progress_score = env.get_task_progress()}
       compute_metric -> metrics.json; detail_info.json per task; optional video "<i>_success_<bool>_progress_<ps>.mp4"
```

Episodes that raise are caught, printed, and skipped (the maintainers note unstable episodes); a consumer must treat a missing record as an error, not a failure. [VLAB-CODE, `evaluation/evaluator/base.py`]

## 4. Track configuration surface

Each track JSON maps task name to a list of episode configs (`components` with object classes, poses, materials/styles, and instruction-relevant attributes). `n_episodes` takes the list prefix; the Evaluator asserts `len(config[task]) >= n_episodes`. Tasks per public track: 10; configs per task: 50 except Track 2 `insert_flower` (10). Track 3 replaces two tasks with `select_nth_largest_poker` and `select_unique_type_mahjong`. [VLAB-CODE, `configs/evaluation/tracks/`]

## 5. Data tooling

`scripts/trajectory_generation.py` (+ `dataset_generation.sh`, multi-GPU variant) writes HDF5; `convert_to_rlds.py` builds a TFDS builder; `convert_to_lerobot.py` follows openpi's LIBERO conversion (`datasets==3.2.0` required per `docs/issues.md`). The official LeRobot release has 3 views at 480x480, 7-D absolute pose state/actions, 10 fps. [VLAB-CODE; VLAB-DATA-LEROBOT]

## 6. Dependency pins

`requirements.txt`: `mujoco==3.2.2`, `mujoco-mjx==3.2.2`, `dm_control==1.0.22`, `gym==0.26.2`, `gymnasium==0.29.1`, `numpy==1.25.0`, `h5py==3.11.0`, `scipy==1.14.0`, `tensorflow-datasets==4.9.2`, `rrt-algorithms` (git), `lerobot` at a pinned commit, `open3d==0.18.0`, `mediapy`, `opencv-python`; `setup.py` core: gym, ipdb, mujoco, dm_control, imageio. Headless rendering: `MUJOCO_GL=egl` (or osmesa) plus Mesa/GL system libs. [VLAB-CODE, `requirements.txt`, `docs/issues.md`]

## 7. Known defects (code locations)

| Issue | Location | Effect |
|---|---|---|
| 55 | task `get_task_progress` | PS differs from the paper formula; code authoritative |
| 80 | robot controller / IK step | motion under a null delta |
| 82 | intention score | IS 0 on successes; action representation sensitivity |
| 88 | `robots/single_arm/franka.py::get_ee_open_state` | returns true when closed (source comment acknowledges) |

[VLAB-ISSUE-55; VLAB-ISSUE-80; VLAB-ISSUE-82; VLAB-ISSUE-88]

## Sources

[VLAB-CODE]; [VLAB-DATA-LEROBOT]; [VLAB-ISSUE-55]; [VLAB-ISSUE-80]; [VLAB-ISSUE-82]; [VLAB-ISSUE-88].
