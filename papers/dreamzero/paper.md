---
id: world-model-kb.papers.dreamzero.paper
title: DreamZero Method, Architecture, and Experimental Evidence
kind: paper
status: maintained
last_updated: 2026-08-14
owners:
  - AIBuildAI world-model group
---

# DreamZero Method, Architecture, and Experimental Evidence

## Retrieval metadata

**Relevant queries:** DreamZero WAM, Wan2.1-I2V-14B, joint video action, Flash Beta(7,1), Table 1 38x, Table 2 55.4%, Table 3 74%, AgiBot 62.2%, DROID 22.5% success, embodiment adapter, not universal policy.

**Knowledge provided:** WAM formulation, 14B architecture, real-robot tables, Flash/systems latency, cross-embodiment protocols, and the embodiment-specific checkpoint boundary.

**Related pages:** [`README.md`](README.md); [`codebase.md`](codebase.md); [world action models](../../foundations/definitions-and-taxonomy/world-action-model.md); [forward dynamics](../../foundations/problem-formulation/forward-dynamics.md); [Cosmos3-Nano generator](../../models/cosmos3-nano/generator.md).

Foundation bibliographic identity: [WAM-DREAMZERO-2026]. Do not duplicate that ID in [`sources.yaml`](sources.yaml).

## 1. Problem statement

DreamZero is a **World Action Model (WAM)**: a 14B image-to-video diffusion backbone that jointly predicts future video and motor actions. It is not a VLA text-to-action policy and **not a universal zero-shot policy for every robot**. The paper pretrains **separately** per embodiment (AgiBot G1 vs DROID-Franka) and uses adapters plus play-data LoRA when the robot changes. [DZ-PAPER, Abstract, Sec. 4]

The intended factorization is inverse-dynamics alignment: video futures provide a visual plan; actions are the motor realization of those futures. Failures are reported to track video errors more than action-head errors. [DZ-PAPER, Sec. 5 Q1]

## 2. Architecture

### 2.1 Backbone and frozen modules

Initialization: **Wan2.1-I2V-14B-480P**. Ablations also use Wan2.1-I2V-5B-480P. Trainable: DiT blocks, state encoder, action encoder, action decoder. Frozen: text encoder, image encoder, VAE. LoRA-only DiT was tried and called suboptimal for the main recipe. Default action: relative joint positions; idle frames filtered. [DZ-PAPER, Sec. 4.1]

Released Hydra image size for DROID training scripts is `320 x 176`, `num_frames=33`, `action_horizon=24` — implementation contract, not a substitute for the paper's 480P backbone name. [DZ-CODE, `scripts/train/droid_training.sh` defaults in README]

### 2.2 Autoregressive chunks and GT cache

Generation is **autoregressive** over native-rate chunks with KV cache, not a single bidirectional clip (bidirectional is an ablation). After each executed chunk, **real observations** replace generated visual tokens in the cache so closed-loop error does not compound as in open-loop video. [DZ-PAPER, Sec. 3.1, Fig. 4]

### 2.3 Systems stack and Flash

Table 1 cumulative speedups (each row includes rows above):

| Optimization | H100 | GB200 |
|---|---:|---:|
| Baseline | 1x | 1.1x |
| + CFG parallelism | 1.9x | 1.8x |
| + DiT caching | 5.5x | 5.4x |
| + torch.compile + CUDA graphs | 8.9x | 10.9x |
| + kernel/scheduler | 9.6x | 14.8x |
| + NVFP4 quantization | — | 16.6x |
| + DreamZero-Flash | — | **38x** |

Baseline wall time 5.7 s -> 150 ms on GB200 with Flash. DiT cache reuses velocities when cosine similarity is high (16 DiT steps -> 4 effective). Flash trains video times from `t_video = 1 - eta`, `eta ~ Beta(7,1)`, `E[t_video]=0.125`, while action times stay uniform, then 1-step inference. Action chunks are Savitzky-Golay smoothed at 2x upsample. [DZ-PAPER, Table 1, Sec. 3.2]

Paper closed-loop claim: **7 Hz**. README server: ~0.6 s GB200 / ~3 s H100 with `--enable-dit-cache` after warmup — a different measurement surface. [DZ-PAPER, Abstract; DZ-CODE README]

## 3. Data and evaluation protocols

**AgiBot:** ~500 h, 7.2K episodes, 22 environments, mean 4.4 min / ~42 subtasks per episode. Train 100K steps, global batch 128. Seen: 10 tasks x 8 rollouts x 4 robots = 80. Unseen: 10 tasks, 80 rollouts. Progress: folding 5 stages, packing 10 fruits, bussing items, etc. Overlay on initial scene to reduce variance (Barreiros et al. 2025). [DZ-PAPER, Sec. 4]

**DROID-Franka:** public DROID only (no extra cross-embodiment pretrain for DreamZero). 20 seen + 20 unseen verbs, 2 rollouts each, 80 rollouts/checkpoint, partial completion in `[0,1]`.

**Baselines:** GR00T N1.6 and π0.5, from-scratch (VLM init, no robot data) and from-pretrained official, then continued on the **same** AgiBot 500 h or DROID mix. Compute matched on batch and steps.

**Post-train:** shirt folding 33 h, fruit packing 12 h, table bussing 40 h; 50K steps; 10 rollouts/task.

**Cross-embodiment:** 72 video-only trajectories of 9 unseen tasks (8 per task): 20 min YAM, 12 min human. Co-train 1:1 with AgiBot data 10K steps from DreamZero-AgiBot. Few-shot YAM: 55 play trajectories, 11 tasks, ~30 min.

## 4. Results

### 4.1 Seen and unseen (figures; prose numbers)

AgiBot seen, zero-shot env/objects: DreamZero **62.2%** average task progress versus best pretrained VLA **27.4%** (>2x). From-scratch VLAs near zero. [DZ-PAPER, Sec. 5 Q1, Fig. 8]

AgiBot unseen verbs: DreamZero **39.5%** vs pretrained VLA **16.3%**; from-scratch `<1%`. Examples: remove hat 85.7%, shake hands 59.2%. [DZ-PAPER, Sec. 5 Q2, Fig. 9]

DROID-Franka unseen: DreamZero **49%** progress / **22.5%** success versus GR00T N1.6 31% / 12.5% and π0.5 33% / 7.5%. [DZ-PAPER, Sec. 5 Q2]

Post-train (Fig. 10): matches or beats VLAs; fruit packing is the largest gap. Geographic eval-site shift remains.

### 4.2 Table 2 cross-embodiment (video-only)

| Method | Unseen task progress |
|---|---:|
| DreamZero | 38.3% ± 7.6% |
| + human video (12 min) | 54.3% ± 10.4% |
| + YAM robot video (20 min) | **55.4% ± 9.5%** |

No target actions on the transfer videos. Standard errors are large; treat as an early signal. [DZ-PAPER, Table 2]

### 4.3 Table 3 Flash (table bussing)

| Method | Steps | Task progress | Latency | Speedup |
|---|---:|---:|---:|---:|
| DreamZero | 4 | 83% ± 6.1% | 350 ms | 1x |
| DreamZero | 1 | 52% ± 10.2% | 150 ms | 2.33x |
| DreamZero-Flash | 1 | **74% ± 10.1%** | 150 ms | 2.33x |

[DZ-PAPER, Table 3]

### 4.4 Table 4 ablations (50K steps, batch 32, PnP Easy)

| Setting | Task progress |
|---|---:|
| AR 14B repetitive 500 h | 33% ± 4.2% |
| AR 14B diverse 500 h | **50% ± 6.3%** |
| AR 5B diverse | 21% ± 4.2% |
| Bidirectional 14B diverse | 50% ± 14.4% |

Prose states matched VLAs on diverse data reach **0%** task progress (hover without contact). ar5iv HTML prints VLA cells as `50% ± 0.0%`, which conflicts with that sentence and is treated as a conversion misalignment; **prose 0% is canonical** until a PDF table is re-read. [DZ-PAPER, Table 4, Sec. 5.2 Q2]

AR and bidirectional means match; AR has lower SE and 3-4x faster inference via KV cache.

### 4.5 Systems files at the pinned commit

Mechanism blobs from GitHub tree JSON at `ab790c198fbce33503358efbbd4187ce9a89adf3`:

| Path | Bytes | Role |
|---|---:|---|
| `groot/vla/model/dreamzero/modules/wan_video_dit_action_casual_chunk.py` | 99864 | AR joint DiT |
| `groot/vla/model/dreamzero/action_head/wan_flow_matching_action_tf.py` | 66474 | action FM head |
| `groot/vla/model/dreamzero/modules/wan_video_dit.py` | 32363 | base DiT |
| `groot/vla/model/dreamzero/modules/wan_video_vae.py` | 47412 | frozen VAE wrapper |
| `groot/vla/model/dreamzero/transform/dreamzero_cotrain.py` | 29638 | video-only co-train |
| `groot/vla/data/schema/embodiment_tags.py` | 9163 | embodiment IDs |
| `groot/vla/configs/data/dreamzero/droid_relative.yaml` | 1526 | Franka adapter |
| `groot/vla/configs/data/dreamzero/agibot_relative.yaml` | 1658 | AgiBot adapter |
| `groot/vla/configs/data/dreamzero/yam_relative.yaml` | 1573 | YAM adapter |
| `socket_test_optimized_AR.py` | (server) | 2-GPU WebSocket |
| `eval_utils/run_sim_eval.py` | 8453 | external-API sim; not paper robots |

`groot/vla/model/n1_5/` is leftover GR00T-line code, not the WAM. README `max_steps=10` is not 100K. [DZ-CODE]

## 5. Limits

- WAM is embodiment-specific; AgiBot and DROID are separate pretrains; YAM uses adapters/play data.
- Task progress ≠ binary success except where both are reported (DROID 22.5%).
- Table 2 CIs overlap substantially.
- Table 4 VLA numeric row is not trusted from HTML.
- 7 Hz versus README 0.6-3 s must not be merged without flags.
- MolmoSpaces/RoboArena README claims are mutable leaderboards, not Table 1-4.
- No local train/infer in this KB.

## 6. Cosmos3 attachment map

| DreamZero mechanism | Cosmos3 surface | Not this surface |
|---|---|---|
| Joint video-action DiT | Generator FD/WAM | Reasoner text |
| GT visual cache after execute | closed-loop WAM | open-loop video only |
| Flash Beta(7,1) video times | few-step WAM sampler | Table 1 38x without flags |
| Embodiment YAML + play LoRA | domain adapters | universal Policy-DROID drop-in |
| Video-only co-train | unlabeled video FD mix | claiming zero-shot any robot |

DreamZero WAM is **not** a universal policy. AgiBot and DROID are separate pretrains. YAM uses `yam_relative.yaml` plus ~30 min play.

## 7. Latency surfaces (do not merge)

| Surface | Number | Flags |
|---|---|---|
| Table 1 Flash GB200 | 150 ms, 38x vs 5.7 s baseline | CFG parallel, DiT cache, compile, kernels, NVFP4, Flash |
| Table 3 Flash | 150 ms, 74% progress | table bussing, 1-step Flash vs 4-step 350 ms |
| README server | ~0.6 s GB200 / ~3 s H100 | `--enable-dit-cache` after warmup |
| Paper closed-loop Hz | 7 Hz | not the README server |

Record GPU SKU, cache, Flash, and TRT on every latency claim. [DZ-PAPER, Tables 1, 3; DZ-CODE README]

### 7.1 Data numbers (paper)

AgiBot: ~500 h, 7.2K episodes, 22 environments, mean 4.4 min / ~42 subtasks. Train 100K steps, global batch 128. Seen: 10 tasks x 8 rollouts x 4 robots = 80. Unseen: 10 tasks, 80 rollouts. Overlay on initial scene (Barreiros et al. 2025). DROID: public DROID only; 20 seen + 20 unseen verbs; 2 rollouts each; 80 rollouts/checkpoint; partial completion in `[0,1]`. Post-train: shirt 33 h, fruit 12 h, bussing 40 h; 50K steps; 10 rollouts/task. Cross-embodiment: 72 video-only trajectories of 9 unseen tasks; 20 min YAM / 12 min human; co-train 1:1 for 10K steps. Few-shot YAM: 55 play trajectories, 11 tasks, ~30 min. [DZ-PAPER, Sec. 4]

### 7.2 Inverse-dynamics reading

The paper's Q1 discussion treats video futures as a visual plan and actions as the motor realization. Failures are reported to track video errors more than action-head errors. That is a **hypothesis about this WAM**, not a proof that any video model is a universal policy. Keep embodiment adapters. [DZ-PAPER, Sec. 5 Q1]

### 7.3 Flash recipe (equations as used)

Video times: `t_video = 1 - eta` with `eta ~ Beta(7,1)`, so `E[t_video]=0.125`, while action times stay uniform; then 1-step inference. Action chunks are Savitzky-Golay smoothed at 2x upsample. DiT cache reuses velocities when cosine similarity is high (16 DiT steps -> 4 effective in the systems stack). CFG parallelism, torch.compile, CUDA graphs, kernels, and NVFP4 are cumulative in Table 1. [DZ-PAPER, Table 1, Sec. 3.2]

### 7.4 Frozen versus trainable

Trainable: DiT blocks, state encoder, action encoder, action decoder. Frozen: text encoder, image encoder, VAE. LoRA-only DiT was tried and called suboptimal for the main recipe. Default action: relative joint positions; idle frames filtered. [DZ-PAPER, Sec. 4.1]

Baselines GR00T N1.6 and π0.5 are trained from-scratch (VLM init, no robot data) and from-pretrained official weights, then continued on the **same** AgiBot 500 h or DROID mix. Compute matched on batch and steps. From-scratch VLAs are near zero on seen AgiBot. [DZ-PAPER, Sec. 4-5]

## Sources

- [DZ-PAPER] arXiv:2602.15922.
- [DZ-CODE] `dreamzero0/dreamzero@ab790c198fbce33503358efbbd4187ce9a89adf3`.
- [DZ-HF-DROID], [DZ-HF-AGIBOT] embodiment checkpoints.
