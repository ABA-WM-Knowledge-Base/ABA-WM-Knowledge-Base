---
id: world-model-kb.models.xiaomi-robotics-1.training
title: Xiaomi-Robotics-1 Training State and Optimization Levers
kind: model
status: maintained
last_updated: 2026-08-21
owners:
  - AIBuildAI world-model group
---

# Xiaomi-Robotics-1 Training State and Optimization Levers

## Retrieval metadata

**Relevant queries:** training recipe, loss weights, FusedAdam, lr 2e-5, cosine warmup 500, batch 48, max_steps 10000, save_interval, DeepSpeed ZeRO-2, bf16-mixed, gradient clip 1.0, async_train, MAX_LENGTH, scaling curve, validation MSE.

**Knowledge provided:** the disclosed objective, the pinned trainer's defaults, what the report discloses about recipes per benchmark, the scaling evidence, and the checkpoint lifecycle.

**Related pages:** [Action head](action-head.md) owns the loss terms; [Data](data.md) owns mixtures; [Post-training](post-training.md) owns benchmark recipes; [Codebase](codebase.md) owns file locations.

## 1. Checkpoint lineage is part of the experimental state

```text
Qwen3-VL-4B-Instruct -> UMI pre-training -> cross-embodiment post-training
   -> Xiaomi-Robotics-1-5B (model_states.pt)         [trainer format]
   -> -VLABench / -RoboCasa / -RoboCasa365 (HF)       [inference format]
```

A fine-tune's `pretrained` must be a trainer-format file with every key of the `xr1` module; the HF fine-tunes lack 15 training-only tensors (choice heads, `<a_i>`/`<score>` embeddings, the untied `lm_head`). [XR1-CODE, `BaseRunner.configure_model`; XR1-HF-5B; XR1-HF-VLABENCH]

## 2. Objective

Total loss in the pinned trainer: `0.5 * loss_mse + freq_coefficient * loss_freq + 0.5 * loss_choice + 0.5 * loss_score`; the report adds `0.1 * L_NTP` on vision-language data during pre-training and a 50 %-probability CoT next-token loss for the VLABench fine-tune (not implemented in the public trainer). Timestep `t = (1 - Beta(1.5, 1)) * 0.999`. [XR1-TR, Sec. 3, 5.3; XR1-CODE]

## 3. Pinned trainer defaults (`xr1/configs/trainer/deepspeed.yaml`)

| Variable | Default | Note |
|---|---|---|
| precision | `bf16-mixed` | Lightning + `DeepSpeedStrategy` (ZeRO stage 2 by default; allgather/reduce buckets 5e8) |
| optimizer | `deepspeed.ops.adam.FusedAdam`, betas (0.9, 0.95), weight decay 0.1 (no decay on bias/norm/rotary/adaln) | `lr: 1.` is a placeholder scaled by the scheduler |
| schedule | cosine with warmup: 500 warmup steps from 5e-7, peak 2e-5, floor 5e-6 | `num_training_steps = max_steps` |
| max_steps / save_interval | 10000 / 10000 | `ModelCheckpoint(save_top_k=-1, save_last=True, every_n_train_steps=save_interval)` |
| accumulate_grad_batches | 1 | |
| gradient clip | 1.0 (norm) | |
| per-rank batch | 48 (`data.params.train_datasets.batch_size`) | real-robot demo config |
| action_length | 30 (real robot); 10 for VLABench | chunk K |
| seed | 42 + rank | `seed_everything(..., workers=True)` |
| `MAX_LENGTH` | 20000 tokens per packed batch (env in `train.sh`) | samples exceeding it are dropped |
| model flags | `ffn_gradient_checkpointing: true`, `async_train: true`, `freq_coefficient: 1.0`, `freq_excluded_dims: [17, 18, 19]` | |

[XR1-CODE, `xr1/configs/*`, `xr1/tools/train.py`, `xr1/scripts/train.sh`]

## 4. Disclosed benchmark recipes

| Benchmark | Steps | Global batch | Peak lr | Other | Source |
|---|---:|---:|---:|---|---|
| RoboCasa365 | 120k | 512 | 3e-5 | 4-frame history every 2 sim steps, 16-step 12-D chunks | [XR1-ISSUE-4] |
| RoboDojo | 60k | 256 | 1e-5 | no history, two end-effector poses | [XR1-ISSUE-4] |
| RoboCasa | not disclosed | | | 300 MG demos per task | [XR1-TR, Sec. 5.1] |
| **VLABench** | **not disclosed** | | | official 10-task set; CoT NTP at 50 % | [XR1-TR, Sec. 5.3] |

Pre-training compute (GPU count, hours) is not disclosed. [XR1-TR]

## 5. Scaling evidence

Validation action error (MSE) decreases monotonically with pre-training data fraction (12.5/25/50/100 % of a ~20K h subset; "doubling the data from 50 % to 100 % yields an additional 6 percentage point improvement") and with model size (2B -> 5B -> 10B), with "no sign of saturation". The metric is open-loop error, not closed-loop success. [XR1-TR, Sec. 6]

## 6. Training-system state

One `torchrun` launch per host (`scripts/train.sh`, `RESOURCE_GPU` ranks; multi-node via `WORLD_SIZE/RANK/MASTER_ADDR/MASTER_PORT`), Hydra config, a WandbLogger created unconditionally (offline mode avoids login), `config.py`/`config.yaml` dumped into the run dir, `last.ckpt/` DeepSpeed directory with `latest` tag + per-rank optimizer shards. Resume: `trainer.ckpt_path` (same world size only). [XR1-CODE, `tools/train.py`, `utils/cfg_utils.py`, `server/deploy.py`]

## 7. Controllable training levers

| Lever | Surface | Expected signal | Risk | Validation |
|---|---|---|---|---|
| Steps and batch at fixed lr | `trainer.max_steps`, `batch_size` | SR on Track 1 first | Over-training a 5k-episode set; no disclosed anchor | Paired L2 at 2-3 step budgets |
| Peak lr 1e-5 .. 3e-5 | `trainer.scheduler.params.max_lr` | Warm-start stability | Report used 3e-5 (RoboCasa365), 1e-5 (RoboDojo) | Loss curve + L2 |
| Gradient accumulation | `accumulate_grad_batches` | Larger global batch without memory | Slower steps | s/step |
| `async_train` off | model flag | Simpler loss; no effect on the synchronous client | Loses prefix robustness for real-robot use | L2 parity |
| `MAX_LENGTH` | env | Stops silent sample drops | Memory | `train/token` log |

## Sources

[XR1-TR] Sec. 3-6; [XR1-CODE] `xr1/configs/trainer/deepspeed.yaml`, `xr1/tools/train.py`, `xr1/mibot/models/runner/base_runner.py`; [XR1-ISSUE-4]; [XR1-HF-5B]; [XR1-HF-VLABENCH].
