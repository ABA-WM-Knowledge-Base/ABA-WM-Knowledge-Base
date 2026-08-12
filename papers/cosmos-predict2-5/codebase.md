---
id: world-model-kb.papers.cosmos-predict2-5.codebase
title: Cosmos-Predict2.5 Released Implementation Graph
kind: reference
status: maintained
last_updated: 2026-08-12
owners:
  - AIBuildAI world-model group
---

# Cosmos-Predict2.5 Released Implementation Graph

## Retrieval metadata

**Relevant queries:** Predict2.5 repository, inference call chain, training entrypoint, checkpoint mapping, action-conditioning code, conditional-frame mask, multiview code, distillation implementation, or paper-code mismatch.

**Knowledge provided:** immutable repository revisions, mechanism-to-module mappings, runtime and training call chains, tensor contracts, released change surfaces, and unresolved divergences between the paper and public implementation.

**Related pages:** [`paper.md`](paper.md) owns reported mechanisms and evidence; [`reproduction.md`](reproduction.md) owns executed state; [diffusion and flow matching](../../foundations/learning-objectives/diffusion-and-flow-matching.md) owns the generic objective; [Cosmos3-Nano codebase](../../models/cosmos3-nano/codebase.md) owns the successor framework rather than this archived implementation.

## 1. Revision policy

The implementation graph is mapped at `f2146f47a07abf72459c92a9958484ff447ed37d`, the 2026-02-23 `Release version 1.5.0` feature commit. A same-day hotfix followed before the report-date README commit `a24ac3df55d55f87deff7067907afcaf961045f1`; that later commit is the paper-era execution identity because its tree includes both the features and hotfix. Current maintenance facts use `a2c298b0a3df3778b973fe65e9e58877b292d8a7`, whose README redirects users to Cosmos 3 and describes Predict2.5 as no longer actively developed. [P25-CODE-PAPER; P25-CODE-REPORT-UPDATE; P25-CODE-CURRENT]

The mutable tag `v1.5.0` currently resolves to `39a59cbd3323f519fbea50bd1833694644d67f81`, an April maintenance commit rather than either February snapshot. A tag-only reproduction would therefore silently select a post-report dependency state. This entry does not infer how or when the tag target changed. All code locators below are relative to the feature-release commit unless marked report-date or current.

## 2. Released surface versus paper surface

| Paper mechanism or capability | Released at feature-release commit | Principal public surface | Coverage boundary |
|---|---|---|---|
| Base T2W/I2W/V2W inference | yes | `examples/inference.py`, `cosmos_predict2/inference.py` | Loads released checkpoints and sampling pipeline; does not recreate base pre-training. |
| Clean-prefix conditioning | yes | `Video2WorldCondition`, `Video2WorldModelRectifiedFlow` | Implements mask and frame replacement; exact paper training data is absent. |
| 2B/14B DiT definitions | yes | `configs/video2world/defaults/net.py` | Contains a 2B block-count discrepancy documented below. |
| Reason1 text embedding | yes for runtime/post-training | text embedding modules and experiment configs | Reason1 pretraining and the paper's foundation run are external. |
| General 2B/14B SFT | yes | `scripts/train.py`, base experiments, documentation | Example datasets and recipes, not the paper's five private specialist datasets or exact merge. |
| LoRA SFT | yes | LoRA experiments and docs | Repository extension useful for adaptation; not evaluated in the paper. |
| Domain merge and 4K cooldown | no complete public recipe | checkpoint loading/conversion utilities only | Merge coefficients, sweep, selection set, and final merge script are not exposed. |
| VideoAlign/DDRL reward post-training | no paper-equivalent recipe | no public end-to-end RL pipeline matching Section 4.2.2 | Final post-trained checkpoints may embody the result, but training is not reproducible from this repo. |
| rCM four-step distillation | no matching public recipe | paper names rCM; repo documents DMD2/TrigFlow | Treat methods and results as non-equivalent. |
| DMD2 distillation | yes | `docs/distillation.md`, `interactive/`, distill configs | Public alternative, including an action-conditioned four-step recipe. |
| Driving multiview | yes | `examples/multiview.py`, `predict2_multiview/` | Requires separate data and large multi-GPU resources. |
| Robot action-conditioned model | yes | `examples/action_conditioned.py`, `predict2/action/` | Bridge-specific observation predictor; not a policy. |
| Robot multiview AgiBot | yes | `examples/robot_multiview.py`, camera model code | Requires calibrated cameras; full private training data is unavailable. |
| Cosmos Policy | later repository addition | checkpoint tree and Cosmos Cookbook recipe | Separate 2026 paper/capability, not a result from the Predict2.5 report. [P25-COSMOS-POLICY] |

## 3. Base inference graph

```text
examples/inference.py
  -> Args / SetupArguments / InferenceArguments.from_files
  -> cosmos_oss.init.init_environment + init_output_dir
  -> cosmos_predict2.inference.Inference
       -> Video2WorldInference(... checkpoint, experiment, CP, offload flags ...)
       -> generate(samples)
            -> generate_vid2world(...) or generate_autoregressive_from_batch(...)
            -> text/video guardrail runners when enabled
            -> save_img_or_video(..., fps=16)
```

`examples/inference.py` parses one or more JSON parameter files with Tyro/Pydantic. `SetupArguments` resolves a model key to a checkpoint, and explicit `--checkpoint-path` plus `--experiment` override the released model configuration for local post-training checkpoints. `Inference.__init__` builds `Video2WorldInference`, saves its resolved LazyConfig to `output_dir/config.yaml`, and optionally initializes prompt and video guardrails. `Inference.generate` processes samples sequentially without reloading the model. [P25-CODE-PAPER, `examples/inference.py`, `cosmos_predict2/config.py`, `cosmos_predict2/inference.py`]

The standard generation branch calls `generate_vid2world` with prompt, optional input path, guidance, output frames, conditional latent frames, resolution, seed, negative prompt, and denoising steps. The autoregressive branch additionally exposes chunk size and overlap. Output arguments are serialized beside the MP4. These files are necessary reproduction artifacts because command-line defaults and input JSON jointly determine the run.

### 3.1 Checkpoint keys in the feature-release code

| Model key | Registered checkpoint identifier |
|---|---|
| `2B/pre-trained` | `d20b7120-df3e-4911-919d-db6e08bad31c` |
| `2B/post-trained` | `81edfebe-bd6a-4039-8c1d-737df1a790bf` |
| `2B/distilled` | `575edf0f-d973-4c74-b52c-69929a08d0a5` |
| `14B/pre-trained` | `54937b8c-29de-4f04-862c-e67b04ec41e8` |
| `14B/post-trained` | `e21d2a49-4747-44c8-ba44-9f6f9243715f` |
| `2B/auto/multiview` | `524af350-2e43-496c-8590-3646ae1325da` |
| `2B/robot/action-cond` | `38c6c645-7d41-4560-8eeb-6f4ddc0e6574` |
| `2B/robot/multiview-agibot` | `f740321e-2cd6-4370-bbfe-545f4eca2065` |

These identifiers select files inside the current Hugging Face repositories through `cosmos_oss.checkpoints_predict2`. The outer Hugging Face repository revision must also be recorded: an inner identifier alone does not prevent repository-tree changes. [P25-CODE-PAPER, `cosmos_predict2/config.py`; P25-HF-2B; P25-HF-14B]

## 4. Clean-prefix and flow implementation

`Video2WorldCondition.set_video_condition` creates a binary tensor shaped `[B, 1, T, H, W]`, marks the first `N` latent frames, and stores `num_conditional_frames_B`. It accepts either a fixed count, a uniform integer range, or a probability mapping such as `{0: 0.5, 1: 0.25, 2: 0.25}`. `Video2WorldModelRectifiedFlow.denoise` replaces noisy positions with encoded ground-truth latents, optionally gives those positions a separate timestep, passes the mask to the network, and overwrites their velocity output with the ground-truth velocity when configured. [P25-CODE-PAPER, `configs/video2world/defaults/conditioner.py`, `models/video2world_model_rectified_flow.py`]

This realizes the paper's unified conditional-frame task. The contract is latent-frame based: a user-facing count of pixel frames and `num_latent_conditional_frames` are not interchangeable. Context parallel splitting may flatten time/space if the temporal dimension cannot be divided by the process group, so shape validation should be performed after resolved configuration rather than inferred from the CLI.

The base DiT configuration exposes `patch_temporal=1`, `patch_spatial=2`, 16 latent channels, 3D RoPE, AdaLN-LoRA rank 256, and `extra_per_block_abs_pos_emb=False` for 2B and 14B. The 2B config uses width 2,048, 16 heads, and **28** blocks; 14B uses width 5,120, 40 heads, and 36 blocks. [P25-CODE-PAPER, `configs/video2world/defaults/net.py`]

## 5. Training and checkpoint lifecycle

The public SFT path is:

```text
scripts/train.py
  -> Hydra/LazyConfig experiment
  -> dataset + sampler + dataloader
  -> rectified-flow model and optimizer
  -> FSDP/DCP training checkpoint
  -> scripts/convert_distcp_to_pt.py
  -> model.pt / model_ema_fp32.pt / model_ema_bf16.pt
  -> examples/inference.py --checkpoint-path ... --experiment ...
```

The NeMo-assets example launches eight processes with `predict2_video2world_training_2b_cosmos_nemo_assets`, uses 93 frames at `704 x 1280`, batch size one per loader process, and stores DCP checkpoints under `IMAGINAIRE_OUTPUT_ROOT`. It demonstrates the released post-training interface but does not reconstruct the paper's web-scale pre-training or specialist mixture. [P25-CODE-PAPER, `docs/post-training_video2world_cosmos_nemo_assets.md`]

The action example launches one process with `ac_reason_embeddings_rectified_flow_2b_256_320`, Bridge 13-frame data, learning rate `2^-14.5`, and weight decay `0.1`. Its document describes gripper-frame relative displacement and a binary gripper dimension. This is a released SFT recipe whose action semantics must be preserved through any dataset adapter. [P25-CODE-PAPER, `docs/post-training_video2world_action.md`]

The multiview example launches eight processes and uses `predict2_multiview_post_train_waymo`. Caption selection defaults to the front-view caption unless `single_caption_camera_name=None`, and tags can be sampled by configured probability. That default is an important confounder: a per-view language experiment can appear ineffective if the loader silently uses one camera's caption. [P25-CODE-PAPER, `docs/post-training_multiview.md`]

## 6. Action-conditioned implementation

```text
examples/action_conditioned.py
  -> ActionConditioned*Arguments
  -> cosmos_predict2.action_conditioned.inference
  -> action preprocessing from robot state
  -> fixed-length action chunk
  -> action-conditioned DiT step_inference
  -> feed final generated frame into next chunk
```

The DiT flattens `[B, T_action, D_action]` into one chunk representation. Two MLPs produce a `D_model` action embedding and a `3 * D_model` AdaLN embedding. These are added to the timestep embedding and its AdaLN-LoRA modulation before every transformer block. The released default expects 12 actions per chunk; an incomplete tail is skipped, and the chunk size must respect the tokenizer's temporal compression. [P25-CODE-PAPER, `action/networks/action_conditioned_minimal_v1_lvg_dit.py`, `action/inference/inference.py`]

The code derives relative translation and rotation from robot pose, uses a configurable gripper scale, and can resize the first frame. The exact coordinate frame, Euler/quaternion conversion, temporal downsampling, gripper polarity, and scaling are therefore part of model input, not incidental preprocessing. A model-comparison run is invalid if these transformations differ.

The public DMD2 action-distillation command uses `dmd2_trigflow_distill_cosmos_predict2_2B_action_conditioned_bridge_13frame_256x320_no_s3`, with the document illustrating 4,000 training steps and four-step sampling. These outputs must not be labeled as the paper's rCM student. [P25-CODE-PAPER, `docs/post-training_video2world_action.md`, `docs/distillation.md`; P25-DMD2]

## 7. Multiview implementation surfaces

- `examples/multiview.py` and `cosmos_predict2/_src/predict2_multiview/` own the seven-camera driving path.
- `examples/robot_multiview.py`, `cosmos_predict2/robot_multiview.py`, and camera-model modules own calibrated robot-view synthesis.
- Plucker raymaps are projected to visual-token width and added before self-attention; the feature-release robot camera recipe freezes all parameters except self-attention and camera projection.
- The current inference guide states that auto multiview needs at least eight GPUs with 80 GB each; this is a documented deployment requirement for that public configuration, not a measured lower bound for every specialized checkpoint. [P25-CODE-CURRENT, `docs/inference_auto_multiview.md`]

## 8. Paper-code conflicts and uncertainty ledger

| ID | Conflict | Safe interpretation | Consequence for optimization |
|---|---|---|---|
| `CP25-CODE-GAP-01` | Paper Table 3 lists 32 layers for 2B; released base and action configs use 28 blocks. | Preserve both facts; a reported “layer” may include modules not counted as `num_blocks`, or the evaluated architecture may differ. No source resolves it. | Do not calculate parameter allocation or load a checkpoint from the paper table alone. |
| `CP25-CODE-GAP-02` | Paper distills with rCM; repository trains DMD2/TrigFlow. | Two different distillation methods share a low-step deployment goal. | Do not attribute public DMD2 results to Tables 7-8 or assume the rCM recipe is released. |
| `CP25-CODE-GAP-03` | Paper reports VideoAlign/DDRL RL; matching training code/config is absent. | Final released post-trained weights may include RL, but the causal training path is paper-only. | RL experiments require a new implementation and cannot claim exact reproduction. |
| `CP25-CODE-GAP-04` | Paper reports specialist merging and selection; exact scripts, coefficients, and sets are absent. | Only the high-level method and preference plots are public. | A new merge study must define its own grid and held-out selection protocol. |
| `CP25-CODE-GAP-05` | Current checkpoint tree and registered inner identifiers can change independently. | Bind outer repository revision and inner checkpoint identifier. | Checkpoint comparisons without both identities are non-auditable. |
| `CP25-CODE-GAP-06` | Current repository contains Cosmos Policy, while the paper capability table does not. | Policy is a later, separately published extension. | Never use policy success as evidence for the base video model or this paper's experiments. |
| `CP25-CODE-GAP-07` | Current setup supports newer Python/CUDA variants and carries later fixes. | Maintenance fixes may be useful but are not paper-era dependencies. | Record whether a run uses feature-release code, the report-date tree, current code, or a backported patch. |
| `CP25-CODE-GAP-08` | Paper notation calls action dimension seven `GripperWidth`; the released Bridge guide and loader treat it as a current binary open/close state, despite the field name `continuous_gripper_state`. | The public Bridge recipe consumes the current gripper-state scalar at each target frame; another dataset's physical width is not automatically compatible. | Bind gripper semantics, polarity, range, and conversion in every adapter and comparison. |
| `CP25-CODE-GAP-09` | The action inference guide says the setup default is `robot/multiview`, while `ActionConditionedSetupArguments` fixes both the default and allowed model literal to `robot/action-cond`. | The code is the executable interface at the pinned commit; the guide's stated default is stale or incorrect. | Pass and record `--model=2B/robot/action-cond` explicitly instead of relying on the prose default. |
| `CP25-CODE-GAP-10` | The Bridge paper protocol is 5 FPS, low-level action examples show `--save_fps 4`, and the public high-level config plus bundled JSON default to `save_fps=20`. | Input temporal sampling and output MP4 playback metadata are distinct contracts; `save_fps` controls serialization rather than the learned action interval. | Record source-frame rate, temporal downsampling, action rate, generated frame interval, and encoded playback FPS separately; never infer one from another. |

## 9. Change surfaces

| Intervention type | Primary modules | Required controls |
|---|---|---|
| Noise/time distribution | rectified-flow model config and time sampler | resolution, steps, conditional-frame mixture, total samples |
| Conditional-frame curriculum | `Video2WorldCondition`, experiment config | latent versus pixel frame count, loss mask, task mixture |
| Text representation | text embedding loader/projection and cross-attention config | same prompts, tokenizer, Reason1 revision, guidance |
| Codec/patching | VAE checkpoint and net patch config | decoded resolution/FPS, latent rate, DiT token budget |
| Action interface | action dataset transforms, action MLP, time/AdaLN injection | units, coordinate frame, frequency, chunk length, gripper semantics |
| Multiview interface | dataloader, view embeddings, RoPE, camera projection | camera calibration, caption assignment, view count, CP layout |
| SFT or LoRA | experiment config, optimizer, data loader | source checkpoint, trainable parameter set, step and token budget |
| Distillation | `interactive/`, distill model/config | teacher identity, student initialization, solver steps, GAN/critic settings |

These surfaces identify where a hypothesis could attach. They do not prescribe which experiment AIBuildAI should run or how it should schedule work.

## Sources

All code claims bind an immutable repository snapshot registered in [`sources.yaml`](sources.yaml). Executed commands and outputs belong in [`reproduction.md`](reproduction.md).
