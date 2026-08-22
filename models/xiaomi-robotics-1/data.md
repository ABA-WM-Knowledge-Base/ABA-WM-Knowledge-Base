---
id: world-model-kb.models.xiaomi-robotics-1.data
title: Xiaomi-Robotics-1 Data System and VLABench Training Set
kind: model
status: maintained
last_updated: 2026-08-21
owners:
  - AIBuildAI world-model group
---

# Xiaomi-Robotics-1 Data System and VLABench Training Set

## Retrieval metadata

**Relevant queries:** UMI data, 100K hours, auto-labeling, Qwen3.5-27B captions, post-training mixture, 7,200 hours, Bridge V2, RT-1, DROID, sampling ratio, VLABench primitive dataset, 5,000 episodes, LeRobot v3, episode JSON, CoT labels.

**Knowledge provided:** the counting units and sources of every training stage, what is and is not released, and the VLABench training set's fields, sizes, and conventions.

**Related pages:** [Training](training.md) owns objectives; [Post-training](post-training.md) owns benchmark recipes; [VLABench paper entry](../../papers/vlabench/paper.md) owns the benchmark's data generation; [datasets and supervision](../../foundations/data-and-evaluation/datasets-and-supervision.md) owns the model-independent vocabulary.

## 1. Data model: keep stages and units separate

| Stage | Unit | Size | Released |
|---|---|---|---|
| UMI pre-training | hours of hand-held-gripper trajectories | > 100,000 h, 1,700+ scenarios (households, commercial, industrial, offices, outdoor) | no |
| Vision-language co-training | image/text samples | unspecified | no |
| Cross-embodiment post-training | hours | ~10,000 h: > 7,200 h in-house mobile manipulators and dual-arm robots, > 1,000 h human-annotated UMI, plus Bridge V2, RT-1, DROID | no (the open-source parts are public elsewhere) |
| VLABench fine-tune | episodes | 10 tasks x 500 = 5,000 episodes, 575,101 frames at 10 fps | yes [VLAB-DATA-LEROBOT] |
| RoboCasa fine-tune | demos | official 300 synthetic demos per task ("MG" set) | yes (benchmark) |
| RoboCasa365 fine-tune | trajectories | 32,043 trajectories / ~29.1M frames at 20 Hz | yes (benchmark) |

[XR1-TR, Sec. 4-5; XR1-ISSUE-4; VLAB-DATA-LEROBOT]

## 2. Pre-training corpus and auto-labeling

The report divides each UMI trajectory into equal-length segments and uses Qwen3.5-27B to caption "the state transitions of both the grippers and the interacting objects in the scene within each segment"; the full corpus was labelled in about two weeks with a producer-consumer pipeline. The segment length and label examples beyond Figures 11-12 are not stated. Scaling experiments use a ~20K h subset at 12.5/25/50/100 %. [XR1-TR, Sec. 4, Sec. 6]

## 3. Post-training mixture

Sampling ratio vision-language : open-source robot : annotated UMI : in-house = 0.5 : 0.5 : 0.5 : 8.5. Embodiment alignment unifies arm actions as relative delta end-effector poses with aligned frames; instruction alignment replaces scene-transition captions with imperative instructions. [XR1-TR, Sec. 4]

## 4. The VLABench training set (the only data the campaign may use)

`VLABench/vlabench_primitive_ft_lerobot_video` (LeRobot v3.0, revision `9846a2f6…`): [VLAB-DATA-LEROBOT]

| Field | Value |
|---|---|
| episodes / frames / fps | 5,000 / 575,101 / 10 |
| tasks | `add_condiment`, `insert_flower`, `select_book`, `select_chemistry_tube`, `select_drink`, `select_fruit`, `select_mahjong`, `select_painting`, `select_poker`, `select_toy` (500 each); 128 distinct instruction strings |
| video keys | `image` (front), `second_image`, `wrist_image`, 480x480, one AV1 (libsvtav1) mp4 per episode and view; decord cannot decode AV1, PyAV/libdav1d can (measured 2026-08-21) |
| `state` | 7-D float32: robot-frame `[x, y, z, roll, pitch, yaw, gripper]`; ranges x in [-0.47, 0.47], y in [-0.03, 0.80], z in [-0.01, 0.63] |
| `actions` | 7-D float32 absolute target pose + gripper (same ranges) |
| provenance | scripted demonstrations from the benchmark's skill library (RRT + SLERP), not teleoperation [VLAB-PAPER] |
| size | 13.1 GB (18,960 files) |

The 817 GB `raw_primitive_datasets` adds depth, point clouds, joint states, and velocities at 212 timesteps per episode; the community `lerobot/vlabench_unified` (10,977 episodes, 295 tasks, 224x224) is NOT the official training set and changes leaderboard provenance. [VLAB-DATA-RAW; VLAB-DATA-UNIFIED]

Gripper polarity: the dataset `state` gripper bit carries the benchmark's legacy "closed" predicate while the `actions` bit means 1 = open (95.2 % of rows are complements). The served client feeds the same observation predicate, so a data path that copies `state` unchanged stays consistent; a data path that "fixes" the bit does not. [VLAB-ISSUE-88]

### aibuildai episode JSON

The deploy converts each episode to one JSON (`xr1_vlabench_episode_v1`: instruction, three video references with `start`, `state`, `actions`, optional `cot` per frame) read by `mibot/ext/vlabench_data.py` with PyAV; the release's `meta/episodes` data-file and `dataset_from_index` columns are wrong, so episodes are located by scanning the parquet files; CoT strings are VLM-generated per keyframe and carried forward. This is the data the `cot_prob` switch reads. [deploy tree `deploy/xr1_vlabench/ports/`]

## 5. Controllable data levers

| Lever | Surface | Expected signal | Risk |
|---|---|---|---|
| Per-task reweighting / duplication | `paths` list | Balance weak tasks (PS per task) | Overfits a task's 500 demos |
| Instruction paraphrasing | JSON `instruction` | Track 4 (semantic instruction) | Paraphrases that leak test phrasings from the track files are forbidden |
| Image augmentation beyond colour jitter | dataset `_augment` | Track 6 (textures) | Train/eval resolution asymmetry already exists |
| CoT labels content | label generator | Track 3/4 | Self-generated, unvalidated |
| Frame subsampling / chunk stride | sampler | Throughput | Changes effective control rate |

## 6. Attribution-risk signals

- Any frame drawn from `configs/evaluation/tracks/*.json` scenes contaminates the test set.
- `MAX_LENGTH` packing drops samples silently; the effective batch is smaller than declared unless `train/token` is read.

## Sources

[XR1-TR] Sec. 4-6; [XR1-ISSUE-4]; [VLAB-DATA-LEROBOT]; [VLAB-DATA-RAW]; [VLAB-DATA-UNIFIED]; [VLAB-ISSUE-88]; [VLAB-PAPER] Sec. 3.
