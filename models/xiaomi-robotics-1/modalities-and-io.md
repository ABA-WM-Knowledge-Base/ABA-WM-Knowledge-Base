---
id: world-model-kb.models.xiaomi-robotics-1.modalities-and-io
title: Xiaomi-Robotics-1 Modality Representations and I/O Contracts
kind: model
status: maintained
last_updated: 2026-08-21
owners:
  - AIBuildAI world-model group
---

# Xiaomi-Robotics-1 Modality Representations and I/O Contracts

## Retrieval metadata

**Relevant queries:** input contract, prompt template, Ego View, Base View, Left-Wrist View, image resize, max_pixels, state tensor, action_config, robot_type, action mask, raw action shape, processor, decode_action.

**Knowledge provided:** the served and trained input/output contracts per robot type, the image, text, state, and action tensor layouts, and the asymmetries between training and serving that a data path must respect.

**Related pages:** [Architecture](architecture.md) owns computation; [Action modeling](action-modeling.md) owns action semantics; [Policy](policy.md) owns the closed-loop client; [Codebase](codebase.md) owns the processor and collate code.

## Four interface layers

| Layer | Training (xr1 trainer) | Serving (HF `deploy/server.py`) |
|---|---|---|
| Images | decoded from mp4 at a frame index; `resize_image(factor=32, max_pixels=160000)`; colour jitter; collate passes `do_resize=False` | PIL images from the simulator, resized to 480x480 by the client, then the processor's `size.longest_edge=90000` resize |
| Text | chat template with `<image>` placeholders, instruction, `/no_cot` or `/cot`, assistant `<cot>...</cot>`, then `Robot state: <state>` and `<a_0>..<a_{K-1}><score>` | identical user turn; assistant `<cot></cot>` pre-filled when CoT is off; no action tokens |
| State | `(1, 60)` float; trainer path normalizes by q01/q99 into [-1, 1] with clipping | `(1, 1, 60)` raw float, no normalizer in `MiBoTForActionGeneration` |
| Action | `(K, 60)` normalized by per-slot mean/std; mask from the temporal validity | `(K, 60)` sampled in normalized space; `processor.decode_action` multiplies by std and adds mean of the robot type |

[XR1-CODE, `json_dataset.py`, `custom_collate.py`, `mibot/utils/io.py`; XR1-HF-VLABENCH, `processing_mibot.py`, `modeling_mibot.py`]

## Canonical modality matrix

### Images

Three views are titled in the prompt: `# Ego View`, `# Base View`, `# Left-Wrist View` (the real-robot schema names them ego / wrist-left / wrist-right; the VLABench client maps VLABench's `rgb[2]` front camera to Ego, `rgb[0]` second camera to Base, and `rgb[3]` wrist camera to Left-Wrist). The Qwen3-VL vision tower tokenizes with patch 16 and spatial merge 2; a 300x300 image yields about 88 tokens, a 400x400 image about 156. [XR1-CODE-EVAL-VLABENCH; XR1-HF-VLABENCH, `preprocessor_config.json`]

### Text tokens

Special tokens appended to the Qwen tokenizer: `<score>` (id 151669), `<state>` (151670), `<a_0>`..`<a_59>` (151671..151730). The collate verifies these ids at construction. The VLM replaces `<state>` embeddings with `state_projector_choice(state)` in training. [XR1-CODE, `custom_collate.py`, `qwen3vl.py`]

### State

60 slots. The real-robot trainer layout is joints 0..6 (left arm), 7 left gripper, 8..14 right arm, 15 right gripper. The VLABench fine-tune instead receives `[x, y, z, roll, pitch, yaw, gripper]` in slots 0..6 (robot frame: world position minus `(0, -0.4, 0.78)`), zeros elsewhere. The served model has no quantile normalizer, so the VLABench state reaches the projector raw. [XR1-CODE-EVAL-VLABENCH, `main.py:_model_state`; XR1-HF-VLABENCH]

### Action

60 slots with the parts table `left_ee_pos 0:3, left_ee_aa 3:6, left_gripper 6, right_ee_pos 8:11, right_ee_aa 11:14, right_gripper 14, waist 16, base 17:20`. A robot type's `action_config` holds `mean` and `std` of shape `(K, 60)`; slots with `std <= 1e-5` are masked. `vlabench_choice`: K = 10, active slots 0..6, identical rows. [XR1-CODE, `io.py:ACTION_PARTS`; XR1-HF-VLABENCH]

## Framework mode contracts

| Mode | Inputs | Outputs | Owner |
|---|---|---|---|
| `hf_action_generation` | processor batch (`input_ids`, `pixel_values`, `image_grid_thw`, `state`, `action_mask`) + `task_id` (robot type) + `seed` | `actions` `(1, K, 60)` normalized; client decodes | `deploy/server.py`, `deploy/client.py` |
| `vlabench_choice` | three 480x480 views, instruction, 7-D robot-frame state | 10 x 7 per-step deltas + absolute gripper | `eval_vlabench/main.py` |
| `xr1_trainer` | packed chat sequences + `action`, `action_mask`, `state`, `vlm_action_*` | loss dict | `xr1/tools/train.py` |
| `async_prefix` | `(N, 60)` executed action prefix, N in 1..6 | chunk continuation | `mibot/server/runtime/client.py` (real-robot runtime only) |

The HF path and the xr1 runtime path are different wire protocols (pickle vs npz) with different processors; a checkpoint must be exported to serve on the HF path. [XR1-CODE]

## Temporal, length, and spatial contracts

- Chunk length K is a property of the robot type's stats (10 for VLABench, 30 for the real-robot trainer default, 16 for RoboCasa365 per the maintainers). [XR1-HF-VLABENCH; XR1-ISSUE-4]
- Control rate: VLABench data and simulator run at 10 Hz; the client replans every 5 executed steps (0.5 s). [VLAB-DATA-LEROBOT; XR1-CODE-EVAL-VLABENCH]
- Sequence budget: the collate packs samples until `MAX_LENGTH` (env, default 20000 in `train.sh`) and silently drops samples that would exceed it. [XR1-CODE, `custom_collate.py`]

## Optimization levers

| Lever | Surface | Expected signal | Risk | Validation |
|---|---|---|---|---|
| Match train/eval image resolution | dataset `max_pixels` 160000 vs processor 90000 | Texture-track robustness | Changes the token count and memory | Track 6 SR paired |
| State normalization | leave raw (released) vs normalized | None expected; raw is the served contract | Any train-side normalizer the server lacks breaks the policy | Do not change without exporting a matching processor |
| Camera titles/order | prompt text in the data path | Must match the client exactly | Swapped views invalidate the checkpoint | Assert prompt equality against `_build_messages` |

## Sources

[XR1-CODE] `xr1/mibot/utils/io.py`, `xr1/mibot/data/collate/custom_collate.py`, `eval_vlabench/main.py`; [XR1-HF-VLABENCH] `processing_mibot.py`, `preprocessor_config.json`; [XR1-ISSUE-4]; [VLAB-DATA-LEROBOT].
