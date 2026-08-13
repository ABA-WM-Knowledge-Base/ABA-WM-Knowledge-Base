---
id: world-model-kb.papers.irasim.codebase
title: IRASim Released Implementation Graph
kind: reference
status: maintained
last_updated: 2026-08-13
owners:
  - AIBuildAI world-model group
---

# IRASim Released Implementation Graph

## Retrieval metadata

**Relevant queries:** IRASim repository, code revision, file map, tensor shape, Frame-Ada implementation, training loop, sampler, data loader, checkpoint, configuration, evaluation script, code bug, paper-code mismatch, or change surface.

**Knowledge provided:** the pinned implementation call graph, configuration and tensor contracts, exact mechanism attachment points, released artifacts, static defects, and the boundary between v1 code and ICCV-v2 paper claims.

**Related pages:** [`paper.md`](paper.md) owns the method and results; [`reproduction.md`](reproduction.md) owns executed status and minimal fixes; [action interventions](../../foundations/problem-formulation/actions-and-interventions.md) owns generic action semantics; [Cosmos3-Nano action modeling](../../models/cosmos3-nano/action-modeling.md) owns target-model attachment surfaces.

## 1. Revision and release policy

All file and symbol mappings below use `bytedance/IRASim@c72b6dade6fcd65971e0aa8ab49ea39b15108c90`, the current inspected `main` commit dated 2025-07-08. The repository has no release tag, no lockfile, and no model repository with one checksum per inner checkpoint. Full commits and the outer Hugging Face dataset revision are therefore the only stable public identities available. [IRASRC-CODE-CURRENT; IRASRC-HF-BUNDLE]

The repository is Apache-2.0 and attributes substantial implementation ancestry to Latte. Its README, configs, and archive paths remain organized around the 2024 v1 paper and `opensource_IRASim_v1`; the ICCV-v2 paper is the canonical scientific source but is not fully implemented by the public tree. [IRASRC-PAPER-V1; IRASRC-PAPER-V2; IRASRC-CODE-CURRENT]

## 2. Released surface versus paper surface

| Capability | Paper v2 | Public implementation at pinned commit | Consequence |
|---|---|---|---|
| RT-1, Bridge, Language-Table Frame-Ada | reported | train/evaluation configs, loaders, checkpoints, metrics | released core reproduction surface |
| Video-Ada, LVDM, VDM comparison | reported | evaluation configs and model code; checkpoints in bundle | comparison surface exists, but exact environment is unpinned |
| Long autoregressive rollout | reported | generator scripts exist, but one core script is syntax-invalid | requires a minimal repair before execution |
| Keyboard Language-Table control | reported | `application/languagetable.py` | closest interactive released application |
| VR RT-1 control | reported | `application/vive_controller_traj2video.py`, syntax-invalid | documented surface cannot parse unchanged |
| RoboNet | reported | no dataset case, config, or checkpoint | paper-only in the released tree |
| LIBERO policy evaluation | reported | no LIBERO data loader, post-training recipe, human success UI, or adapted model | paper-only end-to-end experiment |
| Push-T planning | reported | no Push-T, proposal policy, ResNet50 value model, ranking loop, or checkpoint | paper-only end-to-end experiment |
| Real-robot goal-image planning | reported | no private dataset, goal-cost pipeline, planner, or hardware interface | paper-only end-to-end experiment |
| OpenSora initialization | reported for decision-use adaptation | no OpenSora loading path in core training | exact v2 adaptation is unreleased |

Static repository search found no `robonet`, `libero`, `push-t`, `pusht`, `opensora`, or policy-evaluation implementation tokens outside documentation. Absence in this pinned tree is evidence of a release gap, not evidence that the authors never used private code.

## 3. Configuration resolution

`main.py --config <yaml>` calls `util.get_args`, which merges, in order:

1. `configs/base/data.yaml` for local roots;
2. the selected train/evaluation YAML for dataset and model settings;
3. `configs/base/diffusion.yaml` for beta schedule, sampler, and sampling steps.

`util.update_paths` then constructs annotation, video, checkpoint, VAE, and evaluator paths. The default base configuration assumes a local project directory named `IRASim`, a local SDXL repository at `pretrained_models/stabilityai/stable-diffusion-xl-base-1.0`, and the official archive tree under `robotdata/opensource_robotdata`. It does not download the VAE automatically. [IRASRC-CODE-CURRENT; IRASRC-SDXL-VAE]

The README's single-GPU command is executable through a fallback distributed initialization, but the fallback hard-codes `CUDA_VISIBLE_DEVICES='1'`. On a one-GPU machine whose usable device is 0, this can hide the only GPU before NCCL initialization. A recorded run should set the distributed environment explicitly or patch the fallback; it should not treat the README command as environment-independent.

## 4. Model construction and tensor contract

`models.get_models(args)` maps `IRASim-XL/2` to `models.irasim.IRASim_XL_2`. For the released short-video settings:

- input video/latent tensor: `[B, F, C, H, W]`;
- `F=16`, with one clean historical position and 15 predicted positions;
- `C=4` for pre-encoded SDXL latents;
- RT-1/Bridge action tensor: `[B, 15, 7]`;
- Language-Table action tensor: `[B, 15, 2]`;
- patch size 2, with fixed spatial and temporal sinusoidal embeddings;
- output: epsilon prediction with the same five-dimensional layout.

The repository exposes S/B/L/XL model constructors and patch sizes 2/4/8, but the official configs use XL/2. `learn_sigma: false` makes the model output four latent channels rather than eight mean/variance channels. [IRASRC-CODE-CURRENT, `models/__init__.py`, `models/irasim.py`, official YAMLs]

## 5. Frame-Ada and Video-Ada code paths

### 5.1 Frame-Ada: `extras == 3`

`IRASim.__init__` selects action dimension 2 for Language-Table and 7 for RT-1/Bridge. `IRASim.forward` embeds each action independently, prepends a learned mask embedding for the history position, and obtains one condition vector per frame. For every spatial block it computes `diffusion_timestep + per_frame_action_embedding`. Temporal blocks receive only the repeated diffusion timestep in the released implementation. [IRASRC-CODE-CURRENT, `models/irasim.py:247-262, 345-443`]

This differs subtly from the paper wording, which says temporal blocks share a video-level trajectory condition. In the public `extras == 3` branch, temporal conditioning at lines 425-431 contains no trajectory embedding. The released checkpoint therefore instantiates **per-frame spatial action conditioning without explicit action conditioning in temporal blocks**, unless that condition is conveyed indirectly through spatially updated tokens. [IRASRC-PAPER-V2, pp.5-6, 20-21; IRASRC-CODE-CURRENT]

The final output AdaLN is also unconditioned on actions by default. The source comment identifies this as a legacy checkpoint bug: `final_frame_ada: false` preserves checkpoint compatibility, while setting it true applies frame action conditions to the final layer. This is a high-value ablation surface because it separates compatibility from the architecture the comment says “should be” used. [IRASRC-CODE-CURRENT, `models/irasim.py:434-441`; official YAMLs]

### 5.2 Video-Ada: `extras == 5`

The complete action chunk is flattened or concatenated after per-action embedding, reduced to one vector, randomly dropped during training with probability 0.1, then repeated across frames and patches. Both spatial and temporal blocks receive this global vector added to the diffusion-timestep embedding, and the final layer is also globally conditioned. [IRASRC-CODE-CURRENT, `models/irasim.py:263-275, 392-435`]

The random 10% condition drop creates an implicit unconditional branch. Evaluation configs set `guidance_scale: 1.0`, so the official reported path does not apply classifier-free guidance. The sampling pipeline's generic default is 4.5, which would duplicate latents but not duplicate the action tensor; direct callers must preserve the official config or verify batch shapes before enabling guidance.

## 6. Masked diffusion and training call graph

```text
main.py
  -> util.get_args / update_paths
  -> models.get_models
  -> dataset.get_dataset
  -> AutoencoderKL.from_pretrained(..., subfolder="vae")
  -> create_mask_diffusion(1000 linear-beta steps)
  -> DDP(model)
  -> for batch:
       video -> frozen VAE latent, or load pre-encoded latent
       action -> model_kwargs
       random diffusion timestep
       MaskGaussianDiffusion.training_losses
         -> keep history latent clean
         -> noise future latent positions only
         -> IRASim.forward
         -> MSE on future positions only
       gradient accumulation -> clip -> AdamW -> constant LR -> EMA
       checkpoint {model, ema, opt, args}
```

`mask_gaussian_diffusion.py` explicitly slices out the prefix both in target construction and MSE aggregation. This matches the paper's clean-history and future-only objective. `main.py` freezes the VAE and saves full training state every 10,000 updates. The code uses `update_ema` after each optimizer step and the published configs stop at 300,000 updates. [IRASRC-PAPER-V2, pp.5-6, 21-24; IRASRC-CODE-CURRENT]

## 7. Dataset implementation

`dataset.get_dataset` supports only `languagetable`, `rt1`, `droid`, and `bridge`; there is no RoboNet branch. `Dataset_3D` reads episode JSON, extracts exact-length sliding windows, loads MP4 or pre-encoded latent tensors, and computes 7-D relative actions from successive end-effector poses and gripper states. Relative translation is rotated into the previous end-effector frame; relative rotation is converted through a ZYX Euler convention. [IRASRC-CODE-CURRENT, `dataset/__init__.py`, `dataset/dataset_3D.py`, `dataset/dataset_util.py`]

The 3-D loader multiplies the seven action components by `[20,20,20,20,20,20,1]`. This scaling is not stated in the paper and is essential for action-condition magnitude. Reproduction records must preserve it. `Dataset_2D` supplies the Language-Table path and its own normalization/preprocessing surface.

The `droid` token appears in the loader but has no official config and no paper role. `main.py` duplicates DROID action batches under Frame-Ada without an explained matching data duplication. It is an experimental remnant, not evidence of a released DROID model.

## 8. Inference and evaluation graph

`main.py` loads the official checkpoint, preferring its `ema` field, generates samples with `Trajectory2VideoGenPipeline`, and writes MP4s, latent tensors, and frames. The pipeline creates full-video Gaussian latents, restores the historical prefix after every PNDM step, sends the action tensor into `IRASim.forward`, and decodes each frame with the frozen VAE. The official diffusion config selects 50 PNDM steps and guidance 1.0. [IRASRC-CODE-CURRENT, `main.py`, `sample/pipeline_trajectory2videogen.py`]

The released evaluation scripts compute:

- paired latent L2 from saved latent videos;
- PSNR and SSIM from decoded videos;
- FID with the vendored `pytorch-fid` code;
- FVD with the vendored `stylegan-v` code and a hard-coded eight-GPU command.

The README names `evaluate/evaluation_short_script.py` and `evaluate/evaluation_long_script.py`, but the files are named `evaluate_short_script.py` and `evaluate_long_script.py`. The short evaluator also hard-codes prediction date `06/14`, reduces the dataset list to Bridge and model list to Frame-Ada, and requires manual editing for a general table reproduction. These are released research scripts rather than a self-contained benchmark CLI.

## 9. Static defects and mismatch ledger

| ID | Evidence | Effect | Minimal repair boundary |
|---|---|---|---|
| `IRA-CODE-GAP-01` | `sample/sample_autoregressive.py` duplicates `if args.sample_method == 'PNDM':` | Python `IndentationError`; long-rollout script cannot import | remove only the duplicate line, retain a patch diff |
| `IRA-CODE-GAP-02` | `application/vive_controller_traj2video.py` has the same duplicate line | VR application cannot parse | same one-line repair |
| `IRA-CODE-GAP-03` | README uses nonexistent `evaluation_*` filenames | copied evaluation commands fail | invoke `evaluate_short_script.py` / `evaluate_long_script.py` or patch README |
| `IRA-CODE-GAP-04` | fallback distributed setup hides all but CUDA device 1 | single-GPU startup may fail | explicitly set rank/device environment or remove hard-coded mask |
| `IRA-CODE-GAP-05` | `wandb.login(key='')` and empty entity are in experiment setup | login/init can block or fail despite offline intent | make logging optional and record the patch |
| `IRA-CODE-GAP-06` | `scripts/install.sh` pins only Diffusers 0.24.0; PyTorch points to CUDA 11.8, most packages are unpinned, no Python version | environment cannot be reconstructed exactly | create an external lock for a replication; do not call it author-provided |
| `IRA-CODE-GAP-07` | README citation says `arXiv:2406.12802` | bibliographic identity is wrong | use `2406.14540`; do not rewrite source history |
| `IRA-CODE-GAP-08` | public Frame-Ada temporal/final blocks differ from paper description | mechanism identity is not exact | evaluate released-compatible and paper-faithful variants separately |
| `IRA-CODE-GAP-09` | v2 experiment code/weights absent | LIBERO/Push-T/real planning cannot be reconstructed from official tree | label as paper-only or build an explicitly non-author replication |
| `IRA-CODE-GAP-10` | RT-1 and LanguageTable training configs set `debug: True`; `get_dataset` then returns the validation split for both training and validation, and dataset loaders truncate non-evaluation debug data to ten samples | the documented training command does not run the full training protocol when copied unchanged | derive a recorded config with `debug: False`; verify split manifests and sample counts before optimization |

A static `py_compile` audit at the pinned commit found exactly two syntax-invalid Python files out of 28: the two duplicate-condition scripts above. The remaining files compiling under Python 3.12 does not establish dependency compatibility or runtime correctness. Configuration audit must be separate from syntax audit: the released RT-1 and LanguageTable training configs select debug data behavior even though their filenames and README commands present them as training configurations.

## 10. Change surfaces for optimization

| Intervention | Primary code surface | Controlled variables to retain |
|---|---|---|
| Frame versus global action modulation | `IRASim.forward`, `extras` | backbone, parameter count, data order, condition dropout, sampler |
| Add action condition to temporal blocks | `models/irasim.py:425-431` | released checkpoint compatibility, spatial path, final layer |
| Repair final-layer Frame-Ada | `final_frame_ada` branch | initialization and whether the old checkpoint is frozen or finetuned |
| Action magnitude and frame semantics | `Dataset_3D._get_actions`, `c_act_scaler` | units, Euler order, coordinate frame, gripper target, temporal rate |
| Failure-rollout data | data manifest and sampler, not present in v2 public code | expert count, success/failure mix, scene/task distribution, policy version |
| Horizon robustness | `mask_frame_num`, `num_frames`, autoregressive script | train horizon, inference horizon, number of generated prefixes, sampler budget |
| Decision-aware selection | external proposal and value stack | proposal distribution, `K`, model-data `P`, value model, execution budget |

Any implementation derived from this map should distinguish a **released-compatible** experiment from a **paper-faithful reconstruction**. The first preserves public checkpoint behavior; the second may correct documented omissions but no longer reproduces the released model exactly.

## Sources

- [IRASRC-CODE-CURRENT] ByteDance IRASim repository at `c72b6dade6fcd65971e0aa8ab49ea39b15108c90`.
- [IRASRC-PAPER-V2] ICCV 2025 / arXiv v2 paper for claimed architecture and experiment surfaces.
- [IRASRC-HF-BUNDLE] public outer archive and checkpoint bundle revision.
- [IRASRC-SDXL-VAE] current SDXL dependency identity; exact paper-era revision unresolved.
