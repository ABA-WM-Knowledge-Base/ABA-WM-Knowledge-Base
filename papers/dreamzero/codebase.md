---
id: world-model-kb.papers.dreamzero.codebase
title: DreamZero Released Implementation Graph
kind: reference
status: maintained
last_updated: 2026-08-14
owners:
  - AIBuildAI world-model group
---

# DreamZero Released Implementation Graph

## Retrieval metadata

**Relevant queries:** dreamzero0/dreamzero, socket_test_optimized_AR.py, wan_video_dit_action_casual_chunk.py, droid_relative.yaml, embodiment_tags, --enable-dit-cache, DreamZero-DROID.

**Knowledge provided:** pinned commit paths, embodiment adapters, inference server, training scripts, and gaps. WAM weights are not a universal policy.

**Related pages:** [`paper.md`](paper.md); [`reproduction.md`](reproduction.md).

## 1. Revision

`dreamzero0/dreamzero@ab790c198fbce33503358efbbd4187ce9a89adf3` (2026-04-19), Apache-2.0. Python 3.11, CUDA 12.9+, 2+ GPUs for distributed inference. [DZ-CODE]

Checkpoints: `GEAR-Dreams/DreamZero-DROID` (14B, DROID) and `GEAR-Dreams/DreamZero-AgiBot` (~45 GB, post-train starting point). Camera view **order** must match the guide for positive transfer. [DZ-HF-DROID; DZ-HF-AGIBOT]

## 2. Tree (mechanism files)

```text
socket_test_optimized_AR.py      # multi-GPU WebSocket server
test_client_AR.py
eval_utils/run_sim_eval.py
eval_utils/policy_client.py
docs/DATASET_TO_GEAR_AND_TRAIN.md
docs/DROID_CONVERSION.md
docs/WAN22_BACKBONE.md
scripts/train/droid_training.sh
scripts/train/droid_training_lora.sh
scripts/train/droid_training_full_finetune_wan21.sh
scripts/train/droid_training_wan22.sh
scripts/train/agibot_training.sh
scripts/train/yam_training.sh
scripts/inference/build_trt_engine.sh
groot/vla/data/schema/embodiment_tags.py
groot/vla/configs/data/dreamzero/droid_relative.yaml
groot/vla/configs/data/dreamzero/agibot_relative.yaml
groot/vla/configs/data/dreamzero/yam_relative.yaml
groot/vla/configs/model/dreamzero/vla.yaml
groot/vla/configs/model/dreamzero/action_head/wan_flow_matching_action_tf.yaml
groot/vla/model/dreamzero/action_head/wan_flow_matching_action_tf.py
groot/vla/model/dreamzero/modules/wan_video_dit.py
groot/vla/model/dreamzero/modules/wan_video_dit_action_casual_chunk.py
groot/vla/model/dreamzero/modules/flow_match_scheduler.py
groot/vla/model/dreamzero/modules/wan_video_vae.py
groot/vla/model/dreamzero/transform/dreamzero_cotrain.py
groot/vla/data/dataset/lerobot.py
```

`groot/vla/model/n1_5/` is a GR00T-line leftover, not the DreamZero WAM.

Pinned-commit sizes (GitHub tree JSON):

| Path | Bytes |
|---|---:|
| `wan_video_dit_action_casual_chunk.py` | 99864 |
| `wan_flow_matching_action_tf.py` | 66474 |
| `lerobot.py` | 114070 |
| `lerobot_sharded.py` | 69733 |
| `state_action.py` transform | 39633 |
| `video.py` transform | 42635 |
| `experiment/base.py` | 36098 |
| `wan_video_dit.py` | 32363 |
| `dreamzero_cotrain.py` | 29638 |
| `tensorrt_utils.py` | 32627 |
| `droid_relative.yaml` | 1526 |
| `agibot_relative.yaml` | 1658 |
| `yam_relative.yaml` | 1573 |
| `droid_relative_wan22.yaml` | 1756 |

Wan2.2-TI2V-5B scripts (`droid_training_wan22.sh`, `droid_relative_wan22.yaml`) are an alternate backbone, **not** the 14B paper agent.

## 3. Inference graph

```text
CUDA_VISIBLE_DEVICES=0,1 python -m torch.distributed.run --standalone --nproc_per_node=2 \
  socket_test_optimized_AR.py --port 5000 --enable-dit-cache --model-path <ckpt>
python test_client_AR.py --port 5000
```

Optional GB200 TensorRT: `LOAD_TRT_ENGINE=.../WanModel_nvfp4.trt` and `DYNAMIC_CACHE_SCHEDULE=true`. First calls warm up for minutes. Outputs MP4 under `{model_path}/real_world_eval_gen_*`. [DZ-CODE README]

## 4. Training graph

```text
hf download Wan-AI/Wan2.1-I2V-14B-480P --local-dir ./checkpoints/Wan2.1-I2V-14B-480P
hf download google/umt5-xxl --local-dir ./checkpoints/umt5-xxl
hf download GEAR-Dreams/DreamZero-DROID-Data --repo-type dataset --local-dir ./data/droid_lerobot
bash scripts/train/droid_training.sh
```

Hydra + DeepSpeed ZeRO-2. README defaults: `max_steps=10` is a **sanity check**, not 100K paper training. `save_lora_only: true` by default. New embodiment: `docs/DATASET_TO_GEAR_AND_TRAIN.md` plus `yam_relative.yaml` / `agibot_relative.yaml`. Wan2.2-TI2V-5B is an alternate backbone (`droid_training_wan22.sh`), not the 14B paper agent. [DZ-CODE]

## 5. Embodiment adapters

Relative joint YAML per robot (`droid_relative.yaml`, `agibot_relative.yaml`, `yam_relative.yaml`) and `embodiment_tags.py` are the released contract. DROID views: `exterior_image_1_left`, `exterior_image_2_left`, `wrist_image_left`. Do not load AgiBot weights on Franka without the adapter path. This is why the WAM is **not** a universal policy.

## 6. Gap ledger

| ID | Evidence | Effect | Repair |
|---|---|---|---|
| `DREAMZERO-CODE-GAP-01` | `max_steps=10` default | copied train is a toy run | set 100K in a recorded YAML |
| `DREAMZERO-CODE-GAP-02` | LoRA default vs paper full DiT | underfit | `droid_training_full_finetune_wan21.sh` |
| `DREAMZERO-CODE-GAP-03` | README latency ≠ Table 1/3 | Hz confusion | log flags: cache, Flash, TRT, GPU |
| `DREAMZERO-CODE-GAP-04` | 2 GPU minimum | single-GPU README fail | record nproc |
| `DREAMZERO-CODE-GAP-05` | n1_5 tree present | wrong module import | use `model/dreamzero/` |
| `DREAMZERO-CODE-GAP-06` | AgiBot vs DROID ckpts | silent embodiment mismatch | pin Hub id |
| `DREAMZERO-CODE-GAP-07` | camera order requirement | negative transfer | follow dataset guide |

## 7. Change surfaces

| Intervention | Files |
|---|---|
| Joint video-action DiT | `wan_video_dit_action_casual_chunk.py`, `wan_flow_matching_action_tf.py` |
| Flash / scheduler | `flow_match_scheduler.py` |
| DiT cache | `socket_test_optimized_AR.py --enable-dit-cache` |
| Embodiment | `*_relative.yaml`, `embodiment_tags.py` |
| Co-train video-only | `dreamzero_cotrain.py` |

## 8. Train script map

| Script | Use |
|---|---|
| `scripts/train/droid_training.sh` | default LoRA sanity (`max_steps=10`) |
| `scripts/train/droid_training_lora.sh` | LoRA |
| `scripts/train/droid_training_full_finetune_wan21.sh` | paper-closer full DiT |
| `scripts/train/droid_training_wan22.sh` | Wan2.2 5B, **not** 14B paper |
| `scripts/train/agibot_training.sh` | AgiBot embodiment |
| `scripts/train/yam_training.sh` | YAM adapter |
| `scripts/inference/build_trt_engine.sh` | optional GB200 TRT |

Camera order for DROID: `exterior_image_1_left`, `exterior_image_2_left`, `wrist_image_left`. Wrong order is negative transfer, not a "universal WAM" failure.

Also: `eval_utils/policy_client.py`, `policy_server.py`, `serve_dreamzero_wan22.py`, `groot/vla/configs/conf.yaml`, `action_head/wan_flow_matching_action_tf.yaml`, `transform/dreamzero_cotrain.yaml`, `modules/flow_unipc_multistep_scheduler.py`, `wan2_1_attention.py`, `vram_management.py`, `docs/DATASET_TO_GEAR_AND_TRAIN.md`, `docs/DROID_CONVERSION.md`, `docs/WAN22_BACKBONE.md`. `n1_5/` remains out of the WAM path.

## Sources

- [DZ-CODE] pinned commit.
- [DZ-HF-DROID], [DZ-HF-AGIBOT].
