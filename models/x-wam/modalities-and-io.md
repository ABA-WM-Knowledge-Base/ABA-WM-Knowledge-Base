---
id: world-model-kb.models.x-wam.modalities-and-io
title: X-WAM Modalities and Interface Contracts
kind: model
status: maintained
last_updated: 2026-08-24
owners:
  - AIBuildAI world-model group
---

# X-WAM Modalities and Interface Contracts

## Retrieval metadata

**Relevant queries:** X-WAM input shape, RGB view, depth, state dimension, action dimension, quaternion, axis-angle, gripper sign, camera pose, normalization, frame rate, horizon, policy output, or environment adapter.

**Knowledge provided:** mode-specific inputs and outputs, temporal alignment, coordinate and normalization semantics, and adapter fields that must match a checkpoint before closed-loop control.

**Related pages:** [Inference](inference.md) owns runtime call paths; [data and training](data-and-training.md) owns dataset construction; [RoboCasa tasks and environments](../../benchmarks/robocasa/tasks-and-environments.md) owns the simulator side of the interface.

## Canonical model contract

The learned interface conditions on language, current multi-view RGB, and current proprioceptive state. It generates eight future RGB frames per view, eight future depth frames per view, eight future states, and 32 future actions. Including the fixed conditions, internal tensors contain nine video frames and nine state positions. Actions are four times denser than video/state across the same horizon. [XWAM-PAPER-V2, pp.4-5]

| Modality | Released representation | Temporal role |
|---|---|---|
| Language | UMT5-XXL token embeddings, max text length 512 | Fixed context for all denoising calls |
| RGB | Three views, VAE latent channels, one fixed + eight predicted frames | World observation and visual prior |
| Depth | Inverse depth repeated to three channels and encoded by the same VAE | Auxiliary future geometry; optional at inference |
| State | 16D dual-arm absolute end-effector pose and gripper | One fixed current + eight predicted states |
| Action | 14D dual-arm relative pose change and gripper action | 32 predicted control commands |

[XWAM-HF-CHECKPOINTS; XWAM-CODE-72CF]

## State and action coordinates

Per arm, state contains Cartesian position `(x,y,z)`, quaternion `(w,x,y,z)` after adapter conversion, and gripper openness. Per arm, action contains relative Cartesian displacement, relative axis-angle rotation, and gripper command. Single-arm RoboCasa occupies the left-arm slots; right-arm state and action channels are masked or padded. RoboTwin supervises both arms. [XWAM-PAPER-V2, pp.16-17; XWAM-CODE-72CF, `data/robot_dataset.py`]

Quantile statistics are checkpoint-specific. The data loader maps valid dimensions using per-dataset `q01/q99`; missing-arm dimensions receive zero with zero loss mask. RoboCasa `raw_actions` override reconstructed target-pose action fields. The loader negates the raw gripper value because RoboCasa uses the opposite open/close sign, and the policy server reverses the sign again before environment execution. [XWAM-CODE-72CF, `RobotDataset._build_raw_action_tensor`, `evaluation/policy_server.py`]

No adapter should infer coordinates from dimension alone. Position origin, end-effector axes, rotation ordering, delta convention, controller scaling, and gripper sign are all part of the checkpoint/environment contract.

## Camera and preprocessing contracts

The RoboCasa SFT artifact uses `robot0_agentview_left`, `robot0_agentview_right`, and `robot0_eye_in_hand`. The released dataset stores 256×256 H.264 RGB-D at 20 fps; training config samples nine frames with `frame_skip=4`, producing 5 Hz video, and actions with `action_skip=1`, producing four actions per video interval. Training resizes/crops to `[256,320]` after loading, while the evaluation client renders 256×256 and the server applies its configured resize/center crop. Exact preprocessing tensors should be captured because the dataset-card resolution and training target dimensions are not identical descriptions. [XWAM-HF-ROBOCASA; XWAM-CODE-72CF, configs and evaluation code]

RoboTwin stores head, left wrist, and right wrist RGB-D at 320×240 and roughly 16.7 fps. The same nine-frame/four-action alignment is constructed after configured skips. View types distinguish static and dynamic cameras; optional view shuffling exists but is disabled in released configs. [XWAM-HF-ROBOTWIN; XWAM-CODE-72CF]

## 3D lifting contract

Static camera poses must be known. Wrist pose is derived from predicted end-effector pose and a fixed hand-eye transform. Metric 3D reconstruction therefore requires camera intrinsics, static extrinsics, hand-eye calibration, depth scale, end-effector coordinate semantics, and a common world/base frame. The network's RGB-D tensors alone are insufficient to reproduce point clouds. [XWAM-PAPER-V2, p.5]

## Runtime modes

| Mode | Inputs | Outputs | Required switches | Boundary |
|---|---|---|---|---|
| Policy action | current RGB/state/instruction | 32×14 action plus predicted states | `early_stop=True`, `run_depth=False`, 10 action steps | No video or depth is decoded |
| Full unified prediction | same | RGB-D future, states, actions | `early_stop=False`, `run_depth=True`, 50 video steps | Much higher compute; requires VAE decode |
| RGB/state/action without depth | same | RGB future, states, actions | full video schedule, `run_depth=False` | Cannot support native depth metrics |
| Action-conditioned continuation | conditions plus actions clean after early phase | later RGB and optional depth | continue video scheduler with action/state timestep zero | Internal sampler behavior; not a separate checkpoint |

## Adapter validation

A safe integration records input ranges and shapes before model execution, then validates output finiteness, masks, action range, quaternion/axis-angle conversions, zero-action semantics, gripper direction, action dimension accepted by the environment, and controller response on a no-op and a small known motion. Open-loop tensor success is necessary but insufficient for closed-loop compatibility.

## Sources

Interface facts use `XWAM-PAPER-V2`, `XWAM-CODE-72CF`, `XWAM-HF-CHECKPOINTS`, `XWAM-HF-ROBOCASA`, and `XWAM-HF-ROBOTWIN`.
