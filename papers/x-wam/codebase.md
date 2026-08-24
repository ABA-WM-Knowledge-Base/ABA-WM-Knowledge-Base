---
id: world-model-kb.papers.x-wam.codebase
title: X-WAM Paper-to-Code Implementation Graph
kind: paper
status: maintained
last_updated: 2026-08-24
owners:
  - AIBuildAI world-model group
---

# X-WAM Paper-to-Code Implementation Graph

## Retrieval metadata

**Relevant queries:** X-WAM source file, class, function, depth block, ANS code, training script, dataset parser, inference call path, evaluation client, submodule revision, config mismatch, or checkpoint loading.

**Knowledge provided:** a fixed-revision claim-to-symbol map, tensor and call paths, dependency pins, and discrepancies between the v2 paper, repository defaults, model card, and released checkpoint configs.

**Related pages:** [Paper](paper.md) owns the method and experimental evidence; [X-WAM Model codebase](../../models/x-wam/codebase.md) owns released artifact navigation; [reproduction](reproduction.md) owns execution state.

## Fixed code identity

The official implementation is commit `72cfb86b33fc5060963ef63412f16439fcfa472f`, Apache-2.0. Its Git submodules pin Original RoboCasa `756598a5be52e052339bb2d957426e39015c2afb`, robosuite `232ce7d4a6ed89c949a9aba024a05c8c32fdd08b`, and RoboTwin `c3ddfa8b97d5519efa828b075999bd0006778e5e`. This is a stronger environment identity than the Original RoboCasa README's mutable robosuite instruction. [XWAM-CODE-72CF, `.gitmodules`; RC24-CODE-V02; XWAM-ROBOSUITE-PIN; XWAM-ROBOTWIN-PIN]

## Claim-to-symbol map

| Paper mechanism | Fixed implementation | Computation |
|---|---|---|
| Unified video/state/action DiT | `modules/wan_model.py::XWAMModel` | Patchifies multi-view video, projects action/state, concatenates tokens, applies shared attention, splits and decodes outputs |
| Camera-view identity | `XWAMModel.view_embedding`; `_create_freqs` | Adds learned view embedding while retaining 3D RoPE |
| Depth branch | `XWAMModel.extra_blocks`, `extra_heads`, `_forward_single` | Copies final `num_extra_layers`; depth blocks read main block KV cache; main branch does not read depth |
| Wan initialization | `XWAMModel.init_from_wan_checkpoint` | Copies Wan blocks and initializes each depth block from the corresponding final main block |
| Coupled ANS training | `runners/xwam_runner.py::XWAMRunner.training_step` | Samples clean-action mixture or `t_video >= t_action` beta-rescaled pairs; masks clean action/state loss |
| Flow losses | `training_step` | MSE velocity losses for video/action/state plus depth latent MSE; optional DCT action loss exists but default weight is zero |
| Separate inference schedules | `XWAMRunner.forward` | Three `FlowUniPCMultistepScheduler` instances; stops action/state after `action_denoise_steps` |
| Policy early stop | `XWAMRunner.generate(... early_stop=True, run_depth=False)` | Returns action and state after the action schedule; skips depth and video decode |
| Dataset interface | `data/robot_dataset.py::RobotDataset` | Loads episode JSON, multi-view RGB/depth, state, action and masks; handles raw RoboCasa action override |
| Post-training | `scripts/train_sft.py`; `configs/model/wan22_5b_sft.yaml` | OmegaConf composition, Lightning/DeepSpeed training, pretrained checkpoint load |
| Closed-loop serving | `evaluation/policy_broker.py`, `policy_server.py`, `robocasa_client.py`, `robotwin_client.py` | Broker dispatches client observations to GPU model servers; clients own simulator adapters and success logging |

[XWAM-CODE-72CF]

## Tensor and inference path

`RobotDataset` yields RGB `[B,V,T,C,H,W]`, depth with the same view/time axes, states `[B,T_p,16]`, actions `[B,T_a,14]`, masks, camera types, and instruction. `XWAMRunner._prepare_condition` VAE-encodes video and depth and UMT5-encodes text. `XWAMModel._forward_single` reshapes video tokens into frame-major multi-view order, concatenates action and state tokens, attaches per-token timesteps, applies the shared DiT, forks depth for the final 10 blocks, and decodes velocity fields. [XWAM-CODE-72CF, `data/robot_dataset.py`, `runners/xwam_runner.py`, `modules/wan_model.py`]

At policy inference, `policy_server.py` loads `{exp_path}/config.yaml` and a DeepSpeed-style file `checkpoints/{steps}.ckpt/checkpoint/mp_rank_00_model_states.pt`, instantiates BF16 `XWAMRunner`, loads `ckpt["module"]`, applies `torch.compile`, and calls `generate` with `early_stop=True`, `run_depth=False`. It denormalizes action quantiles and inverts the single-arm gripper sign before returning the chunk. [XWAM-CODE-72CF, `evaluation/policy_server.py`]

The RoboCasa client uses task-specific maximum steps, three cameras, a fixed end-effector axis transform, `xyzw→wxyz` quaternion reorder, five layout/style pairs, object split `B`, and binary `_check_success()`. These adapter details are part of the result identity. [XWAM-CODE-72CF, `evaluation/robocasa_client.py`]

## Paper and release mismatches

| Field | Paper v2 | Released artifact or code | Consequence |
|---|---|---|---|
| Pretraining batch per H20 | 8; global 2,048 on 256 GPUs | HF pretrained config: `batch_size_per_gpu: 4`; distributed world size not stored in config | Paper compute cannot be reconstructed from config alone |
| Benchmark SFT learning rate | `3e-5` | HF RoboCasa and RoboTwin configs: `1e-5`; repository default also `1e-5` | Released checkpoint recipe differs from Appendix B.2 |
| RoboTwin SFT steps | 20,000 in shared benchmark paragraph | HF config/model card: 40,000; README example overrides to 40,000 | Paper table must not be labeled a verbatim released-config reproduction |
| RoboCasa SFT steps | 20,000 | HF config: 20,000 | Consistent on steps, not learning rate |
| Final action/video steps | `10/50` | configs and evaluation docs: `10/50` | Consistent |
| Ablation action steps | 5 asynchronous; 25 synchronous | not the final checkpoint default | Table 4 latency is not final serving latency |
| CFG | paper says scale 1.0 | client default `cfg=0.0` | In code, `cfg=1` equals conditional prediction and `cfg=0` directly runs the same conditional branch without duplicate unconditional compute; numerical path differs but intended conditional output is equivalent |
| NumPy constraint | appendix does not specify | README says `<1.26`, tested `1.23.5`; requirements file permits `<2` | Evaluation installation should use the narrower documented tested version |

[XWAM-PAPER-V2, pp.9, 17; XWAM-CODE-72CF; XWAM-HF-CHECKPOINTS]

The model card follows released configs for `1e-5`, RoboCasa 20K, and RoboTwin 40K, while also repeats the paper's global pretraining batch. The safest identity language is “paper-reported training” versus “released checkpoint configuration,” not a synthetic merged recipe.

## Released versus paper-only surfaces

Released:

- full post-training code and model definition;
- three checkpoint files and configs;
- converted RoboCasa and RoboTwin datasets;
- broker/server/client closed-loop evaluation;
- depth-enabled full generation through `generate(early_stop=False, run_depth=True)`.

Not released as a turnkey artifact in this commit:

- the 5,873.9-hour pretraining corpus or an end-to-end pretraining dataset manifest;
- a standalone command reproducing Table 3 RGB/depth/point-cloud aggregation;
- real-robot AC One deployment/RTC integration code;
- paper-era raw logs, scenario manifests, per-run seeds, or training scheduler state;
- a small checkpoint or CPU inference path.

## Source conflicts as experiment variables

When reproducing the paper claim, use paper values and record any missing implementation state. When reproducing the public model, use the pinned HF config and label the result as released-checkpoint reproduction. A controlled optimization baseline should start from one of these identities and must not mix the paper learning rate with the released step count while calling it either canonical baseline.

## Sources

The implementation source is `XWAM-CODE-72CF`; method and paper settings use `XWAM-PAPER-V2`. Environment pins use `RC24-CODE-V02`, `XWAM-ROBOSUITE-PIN`, and `XWAM-ROBOTWIN-PIN`. HF artifact identity resolves through the [model registry](../../models/x-wam/sources.yaml).
