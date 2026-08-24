---
id: world-model-kb.models.x-wam.codebase
title: X-WAM Released Codebase Map
kind: model
status: maintained
last_updated: 2026-08-24
owners:
  - AIBuildAI world-model group
---

# X-WAM Released Codebase Map

## Retrieval metadata

**Relevant queries:** X-WAM class, source file, runner, checkpoint loading, training script, dataset parser, configuration, policy server, RoboCasa client, RoboTwin client, scheduler, depth block, or implementation mismatch.

**Knowledge provided:** a fixed-commit navigation map from model concepts and public artifacts to concrete symbols, call paths, configuration sources, and integration boundaries.

**Related pages:** The [Paper codebase](../../papers/x-wam/codebase.md) maps claims to implementation; this page owns navigation for using and modifying the released model. [Inference](inference.md) owns runtime semantics, [modalities and I/O](modalities-and-io.md) owns adapter contracts, and [reproduction](reproduction.md) owns executed state.

## Fixed repository graph

The canonical source identity is `sharinka0715/X-WAM@72cfb86b33fc5060963ef63412f16439fcfa472f`, licensed Apache-2.0. Its submodules bind the released evaluators to Original RoboCasa `756598a5be52e052339bb2d957426e39015c2afb`, robosuite `232ce7d4a6ed89c949a9aba024a05c8c32fdd08b`, and RoboTwin `c3ddfa8b97d5519efa828b075999bd0006778e5e`. [XWAM-CODE-72CF; XWAM-ROBOSUITE-PIN; XWAM-ROBOTWIN-PIN]

```text
X-WAM repository
|-- modules/                    model and Wan-derived Transformer code
|-- runners/                    loss, scheduler, generation, encode/decode
|-- data/                       episode parsing and canonical robot tensors
|-- configs/                    model, data, optimizer, and benchmark composition
|-- scripts/train_sft.py        SFT entrypoint and distributed setup
`-- evaluation/                 broker, model server, benchmark clients
    |-- robocasa/               Original RoboCasa submodule
    |-- robosuite/              pinned simulator dependency
    `-- RoboTwin/               pinned dual-arm benchmark dependency
```

The repository tree was inspected at this commit; no file in it was executed during the KB update.

## Symbol map

| Concern | Canonical symbol or path | Diagnostic value |
|---|---|---|
| unified network | `modules/wan_model.py::XWAMModel` | token construction, timestep embeddings, shared blocks, output heads |
| depth branch | `XWAMModel.extra_blocks`, `extra_heads`, `_forward_single` | copied-layer count and unilateral main-to-depth KV flow |
| Wan initialization | `XWAMModel.init_from_wan_checkpoint` | which weights derive from Wan and how depth blocks are initialized |
| training and inference wrapper | `runners/xwam_runner.py::XWAMRunner` | VAE/text setup, schedulers, loss terms, CFG, early stop, decode |
| sample preparation | `data/robot_dataset.py::RobotDataset` | view/time alignment, raw actions, state masks, quantile normalization |
| SFT launcher | `scripts/train_sft.py` | OmegaConf composition, checkpoint restore, Lightning/DeepSpeed execution |
| experiment configs | `configs/` and HF `config.yaml` files | effective architecture, data, optimizer, and scheduler parameters |
| model service | `evaluation/policy_server.py` | state restoration, preprocessing, generation, action denormalization |
| request transport | `evaluation/policy_broker.py` | request routing between simulator clients and model servers |
| RoboCasa adapter | `evaluation/robocasa_client.py` | camera/state conversion, layout/style scenarios, action execution, success |
| RoboTwin adapter | `evaluation/robotwin_client.py` | dual-arm observations/actions and clean/randomized evaluation |

[XWAM-CODE-72CF]

## Training call path

```text
OmegaConf config + command-line overrides
  -> train_sft.py
  -> RobotDataset / DataLoader
  -> XWAMRunner.training_step
  -> encode RGB and depth with Wan VAE
  -> encode instruction with UMT5
  -> sample video/action timesteps and masks
  -> XWAMModel._forward_single
  -> video + action + state + depth losses
  -> Lightning strategy / DeepSpeed optimizer state
```

`RobotDataset` is a semantic adapter, not only a file reader. It maps dataset-specific state/action fields into a canonical dual-arm layout, supplies masks, loads quantile statistics, applies RoboCasa raw-action and gripper transformations, and aligns action frequency with video frequency. Changes here can produce policy deltas without changing the network.

The implementation exposes synchronous, independently decoupled, and joint/coupled timestep sampling. The exact branch is determined by `use_decoupled_sampling`, `use_joint_distribution`, and `clean_action_ratio`; a run manifest should store all three because the label “ANS” is insufficient to reconstruct the distribution.

## Inference call path

```text
policy_server.py
  -> load experiment config and DeepSpeed state["module"]
  -> construct BF16 XWAMRunner
  -> preprocess images/state/instruction
  -> XWAMRunner.generate
       -> prepare conditions and noise
       -> repeated XWAMModel.forward calls
       -> action/state scheduler stops after configured steps
       -> optional video continuation and depth branch
       -> denormalize/decode outputs
  -> benchmark-specific action transform
  -> broker response
```

The policy server uses `early_stop=True` and `run_depth=False`. Full RGB-D generation exists through the runner but is not the same execution path as the policy result. `torch.compile`, distributed state, BF16, attention behavior, and VAE decode can each affect resource measurements and numerical reproducibility. [XWAM-CODE-72CF]

## Configuration precedence and artifact layout

The public HF snapshot contains separate experiment directories for pretrained, RoboCasa SFT, and RoboTwin SFT, each with a config and DeepSpeed-style state file. The code also contains repository defaults, and launch commands may override nested values. Treat the effective configuration as:

```text
code defaults < composed YAML < checkpoint-associated config < explicit launch overrides
```

This ordering describes the surfaces that must be reconciled; the exact merge behavior should be captured from the resolved runtime object. The associated Wan directory is separately required and should be pinned to `Wan-AI/Wan2.2-TI2V-5B@921dbaf3f1674a56f47e83fb80a34bac8a8f203e`, while tokenizer identity is `google/umt5-xxl@66cb9e7e85526fe440a945569e42c72fb6cbc0ad`. [XWAM-HF-CHECKPOINTS; XWAM-WAN22-HF; XWAM-UMT5-HF]

## High-risk modification surfaces

- Changing sequence layout requires updating masks, RoPE/frequency tensors, split lengths, and checkpoint compatibility together.
- Changing state/action dimensions requires synchronized loader statistics, validity masks, MLP shapes, decoder shapes, policy-server denormalization, and client transforms.
- Changing `num_extra_layers` changes state-dict keys, parameter count, initialization, depth compute, and potentially shared-layer semantics.
- Changing temporal skips alters the learned action/video ratio and should not be treated as an evaluation-only option.
- Changing view ordering without preserving view embeddings can create a silent camera-identity permutation.
- Loading only keys that happen to match can conceal a partial checkpoint; missing and unexpected keys require explicit review.

## Release gaps

The fixed commit does not contain a complete manifest for the 5,873.9-hour pretraining corpus, a turnkey script reproducing the paper's Table 3 aggregation, raw paper evaluation logs/seeds, or real-robot deployment integration. These are release-scope gaps, not locally observed runtime failures. [XWAM-PAPER-V2; XWAM-CODE-72CF]

## Sources

Code navigation uses `XWAM-CODE-72CF`; artifacts and upstream assets use `XWAM-HF-CHECKPOINTS`, `XWAM-WAN22-HF`, and `XWAM-UMT5-HF`; submodules use `XWAM-ROBOSUITE-PIN` and `XWAM-ROBOTWIN-PIN`.
