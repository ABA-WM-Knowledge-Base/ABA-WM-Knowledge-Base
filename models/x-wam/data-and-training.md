---
id: world-model-kb.models.x-wam.data-and-training
title: X-WAM Data and Training Contracts
kind: model
status: maintained
last_updated: 2026-08-24
owners:
  - AIBuildAI world-model group
---

# X-WAM Data and Training Contracts

## Retrieval metadata

**Relevant queries:** X-WAM pretraining data, RoboCasa SFT, RoboTwin SFT, pseudo-depth, flow matching loss, asynchronous noise sampling, optimizer, batch size, learning rate, normalization, or released training config.

**Knowledge provided:** dataset composition, temporal and modality preprocessing, objective construction, public configuration values, and paper-to-release discrepancies that affect attribution or reproducibility.

**Related pages:** [Architecture](architecture.md) owns token and branch structure; [modalities and I/O](modalities-and-io.md) owns coordinate contracts; [evaluation](evaluation.md) binds results to checkpoints and protocols. The [X-WAM Paper entry](../../papers/x-wam/paper.md) owns reported methods and experiments, while [Original RoboCasa datasets](../../benchmarks/robocasa/datasets.md) owns the benchmark-era demonstration sets rather than X-WAM's derived SFT release.

## Training stages and artifact identity

X-WAM has two materially different learning stages. Cross-embodiment pretraining initializes the unified RGB-depth-state-action model from Wan2.2-TI2V-5B and exposes it to five robotics corpora. Benchmark SFT then adapts that state separately to the released RoboCasa and RoboTwin interfaces. The three public X-WAM state files are distinct artifacts even though each is approximately 38.89 GB. Loading the pretrained state with an SFT config, or pairing one benchmark state with the other benchmark's normalization and action adapter, is not an equivalent baseline. [XWAM-PAPER-V2, pp.6-8, 16-18; XWAM-HF-CHECKPOINTS]

The paper reports 1,492,026 pretraining episodes totaling 5,873.9 hours:

| Source | Episodes | Hours | Contribution |
|---|---:|---:|---|
| AgibotWorld-Beta | 866,562 | 2,221.5 | large real-robot manipulation corpus |
| DROID | 74,734 | 280.3 | diverse real single-arm data |
| InternA1-Aloha | 184,803 | 1,337.3 | simulated ALOHA trajectories |
| InternA1-Genie1 | 50,638 | 174.0 | simulated robot trajectories |
| InternA1-Lift2 | 231,018 | 1,464.7 | simulated manipulation trajectories |
| RoboCasa MimicGen | 56,771 | 282.4 | simulated single-arm household manipulation |
| RoboTwin 2.0 | 27,500 | 113.7 | simulated dual-arm tasks |

These rows describe the paper corpus, not downloadable contents of the X-WAM repository. Dataset licenses, versions, filters, language generation, camera availability, and exact episode membership remain source-specific dependencies. Aggregate hours do not establish equal task diversity or equal sampling probability. [XWAM-PAPER-V2, pp.7 and 16]

## Public SFT datasets

The released RoboCasa SFT snapshot contains 1,235 episodes and 341,017 frames across 24 single-arm tasks, with three RGB-D views, state, actions, and language. The dataset card reports approximately 5.1 GB and 20 fps. The released RoboTwin snapshot contains 27,500 episodes and 6,138,940 frames across 50 dual-arm tasks, with three RGB-D views and approximately 94 GB of files. Both identities are revision-pinned in [`sources.yaml`](sources.yaml); neither payload was downloaded during KB construction. [XWAM-HF-ROBOCASA; XWAM-HF-ROBOTWIN]

X-WAM's RoboCasa SFT data is not the Original RoboCasa paper's entire 72K or 100K+ generated corpus. It is a smaller released training set with its own episode membership and preprocessing. Therefore, an X-WAM result must not be attributed to a generic “RoboCasa dataset” without recording the exact X-WAM dataset revision.

## Sample construction and alignment

`RobotDataset` loads an instruction, multiple RGB-D streams, proprioceptive state, actions, dataset statistics, and optional camera metadata. A sample contains nine RGB/state time positions and 32 action positions. The initial RGB frame and state are conditions; the remaining eight video/state positions and all actions are prediction targets. In the released RoboCasa configuration, `frame_skip=4` and `action_skip=1` align four action commands with each predicted video interval. [XWAM-CODE-72CF, `data/robot_dataset.py`; XWAM-HF-CHECKPOINTS]

Depth targets are inverse-depth images repeated over three channels so the Wan VAE can encode them using the RGB-shaped path. When measured depth is absent, preprocessing can derive pseudo-depth. This makes “depth supervision” heterogeneous: sensor depth, rendered simulator depth, and monocular pseudo-depth do not have identical scale, uncertainty, or boundary behavior. Any mixture or loss study should retain a depth-provenance field rather than pooling all targets under one label. [XWAM-PAPER-V2, pp.5-7; XWAM-CODE-72CF]

State and action dimensions are mapped by per-dataset validity masks and `q01`/`q99` statistics. Masked dimensions do not contribute to loss. Single-arm RoboCasa occupies the left-arm portion of the dual-arm canonical layout, while the right-arm portion is padded and masked. These masks, statistics, action reconstruction choices, and gripper conversion are part of the learned interface, not incidental loader details. [XWAM-CODE-72CF, `RobotDataset`]

## Objective and noise distribution

The runner applies flow-matching objectives to video, action, state, and depth predictions. The released baseline assigns unit weight to each of these four MSE terms. The implementation also exposes an FFT-based frequency action loss, but its default weight is zero; its existence in code is not evidence that it contributed to reported results. [XWAM-CODE-72CF, `runners/xwam_runner.py::training_step`]

Asynchronous Noise Scheduling changes the joint training distribution. In the paper's coupled construction, the video timestep is constrained to be no earlier than the action timestep, and a clean-action component is sampled with probability 0.5. This trains the model both to jointly denoise modalities and to continue visual futures after actions become clean. Independent action/video timestep sampling and synchronous sampling are separate ablation conditions. [XWAM-PAPER-V2, pp.5-6 and 11]

The schedule should be recorded as a distribution, not only as a flag:

```text
P(t_video, t_action)
  = coupled noisy region with t_video >= t_action
  + clean-action mass controlled by clean_action_ratio
```

Changing `clean_action_ratio`, timestep coupling, or marginal distributions changes data exposure in noise space even if optimizer steps and examples remain constant.

## Released configuration versus paper values

The public checkpoint snapshot contains serialized YAML configs, but several values differ from the paper's training-description tables:

| Field | Paper description | Released public config | Interpretation |
|---|---:|---:|---|
| pretraining batch per GPU | 8 | 4 | unresolved run/config difference; do not silently substitute |
| benchmark SFT learning rate | `3e-5` | `1e-5` | checkpoint provenance follows released config unless an author artifact says otherwise |
| RoboCasa SFT steps | 20,000 | 20,000 | aligned |
| RoboTwin SFT steps | 20,000 | 40,000 | material mismatch for exposure and compute |

The paper reports a global pretraining batch of 2,048, implying a large distributed run on NVIDIA H20 GPUs. A local or reduced-scale run can test software and optimization behavior but is not a compute-matched reproduction. [XWAM-PAPER-V2, pp.16-18; XWAM-HF-CHECKPOINTS]

The released configs reference a separate Wan checkpoint directory containing the VAE and BF16 UMT5 encoder; the tokenizer identity is `google/umt5-xxl@66cb9e7e85526fe440a945569e42c72fb6cbc0ad`. Exact resolved configs, command-line overrides, world size, gradient accumulation, precision, and DeepSpeed state must be retained because the YAML alone is not the complete effective training configuration. [XWAM-WAN22-HF; XWAM-UMT5-HF; XWAM-CODE-72CF]

## Attribution controls

Useful training comparisons hold checkpoint initialization, episode membership, sampling counts, temporal alignment, camera order, normalization statistics, optimizer updates, precision, and evaluation protocol fixed while changing one hypothesized mechanism. Data-mixture studies should report source-level exposures rather than dataset-list presence. Depth studies should separate added capacity, extra supervision, shared-gradient effects, and inference-time depth use. ANS studies should match model calls and distinguish the training joint distribution from the asynchronous inference schedule.

## Sources

Training facts use `XWAM-PAPER-V2`, `XWAM-CODE-72CF`, `XWAM-HF-CHECKPOINTS`, `XWAM-HF-ROBOCASA`, `XWAM-HF-ROBOTWIN`, `XWAM-WAN22-HF`, and `XWAM-UMT5-HF`.
