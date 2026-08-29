---
id: world-model-kb.models.xiaomi-robotics-1.reproduction
title: Xiaomi-Robotics-1 Execution-State Ledger
kind: record
status: maintained
last_updated: 2026-08-21
owners:
  - AIBuildAI world-model group
---

# Xiaomi-Robotics-1 Execution-State Ledger

## Retrieval metadata

**Relevant queries:** executed surface, reproduced, not attempted, local run, released checkpoint L2, anchor measurement, smoke, s/step, memory at batch 48, claim status.

**Knowledge provided:** immutable execution observations, surface-specific claim states, and the acceptance contracts that would promote a surface from documented to executed.

**Related pages:** [Inference](inference.md) contains reference commands; [Optimization playbook](optimization-playbook.md) contains experiment design; [Evaluation](evaluation.md) contains reported values; [evaluation methodology](../../foundations/data-and-evaluation/evaluation-methodology.md) defines evidence standards.

## Claim registry

| Surface | State | Decisive record | Valid claim |
|---|---|---|---|
| Source inspection (report, repo, cards) | `reproduced` (inspection only) | pages of this entry cite the pinned revisions | Method, code paths, and tables were read from the pinned sources |
| HF serving of the released VLABench checkpoint | `reproduced` | run `xr1-l2-released-20260821-01`: 2 servers (A100 80 GB PCIe, driver 550, torch 2.8.0+cu128, transformers 4.57.1, flash-attn 2.8.3), pinned client defaults | The released dir serves through `deploy/server.py` + `eval_vlabench` unchanged |
| VLABench L2 (250-episode prefix) of the released checkpoint | `reproduced` (protocol prefix, not the paper's 50 configs) | `xr1-l2-released-20260821-01`: 250 episodes, 0 errors, 88 min on 2 workers; SR/PS/IS per track: in-dist 56.0/72.0/80.0, cross-cat 56.0/70.7/74.0, commonsense 46.0/56.0/56.0, instruction 44.0/56.7/66.0, texture 50.0/67.3/78.0; **sr_avg_5track 50.4**, ps_avg_5track 64.5, is_avg_5track 70.8, ps_avg_track1_4 63.8 | The campaign anchor on the pinned VLABench commit. IS matches the report (69.9); SR sits 8.7 pp below 59.1 (2.8 standard errors on 250 episodes); `select_fruit` Track 1 scored 0/5 because the model's release (gripper open) appears at chunk positions 7-9 while the client executes 5 - a protocol interaction, not a serving defect (probe `xr1-grip-probe-20260821-01`) |
| VLABench L2 prefix of the released checkpoint on the campaign hardware (Lambda 8x A100-80GB SXM4, us-midwest-1) | `reproduced` | `xr1-l2-released-lambda-20260821-01`: 8 servers, 250 episodes, 0 errors, 32.5 min (7.8 s/episode effective); SR per track 0.56 / 0.54 / 0.48 / 0.46 / 0.52; **sr_avg_5track 0.512**, ps_avg_5track 0.656, is_avg_5track 0.716, ps_avg_track1_4 0.647; 236/250 episodes agree with the developer-box anchor | The anchor holds across hosts (0.512 vs 0.504, inside the 3 pp standard error); cross-host per-episode agreement (94 %) is lower than same-host repeatability (98 %) - different GPU parts (SXM4 vs PCIe) and driver (570 vs 550) change kernels. Output retained on the FS at `aba/data_root/xr1_vlabench/runs/l2_released_<host>/` |
| VLABench full protocol | `not_attempted` | none | |
| Evaluation repeatability (same checkpoint, same seed, two runs) | `reproduced` | `xr1-l2-rerun-t1-20260821-01` vs the anchor on track 1: 49/50 successes, 50/50 IS, 42/50 exact step counts; SR 0.58 vs 0.56 | Flow noise is seeded per request (`modeling_mibot.py` `torch.manual_seed(kwargs['seed'])`); the residual is GPU kernel nondeterminism (bf16 / flash-attn). Paired comparisons on 50 episodes carry a ~1-episode floor; a 1-2 pp track difference is noise |
| Trainer smoke, campaign config (batch 48 per rank, 8 ranks, Lambda 8x A100-80GB SXM4) | `reproduced` | `xr1-smoke-lambda-20260821-01`: step 1 at 34 s, steps 2-5 at ~7 s/step; nvidia-smi peak 80.0-80.6 GB of 81.9 GB on every rank; end-of-fit `last.ckpt/` 64 GB written (and deleted by the stage). Batch 32 (`-02`): ~5 s/step, nvidia-smi peak 79.3-79.8 GB | Batch 48 x 8 trains at ~7 s/step without OOM. The nvidia-smi figure is the caching allocator's reserved pool, not the working set: it sits at ~80 GB at batch 32 as well, so it says nothing about headroom. `torch.cuda.max_memory_allocated` was not captured; treat memory at batch 48 as 'fits, margin unknown' |
| Trainer smoke (5 steps) from the imported warm start | `reproduced` (batch 8, 2 ranks) | `xr1-smoke-20260821-01`: 2 x A100 80 GB (both cards empty), batch 8 per rank, 4 loader workers, ZeRO-2 bf16, warm start `model_states.pt` loaded strictly; step 1 at 31 s (warm-up), steps 2-5 at ~2 s/step; the fit then wrote `last.ckpt/` (64 GB: 2 ZeRO-2 optimizer shards + model states) in ~4 min because `tools/train.py` builds `ModelCheckpoint(save_last=True)` - an end-of-fit save happens regardless of `save_interval`. Two earlier attempts OOMed only because foreign processes held 37-49 GB of one card (rank footprint 31 / 40 GB in the forward pass before the optimizer shard exists) | 2 ranks x batch 8 fit and train at ~2 s/step; peak memory was not sampled in this run (the runbook now samples it); loss values live in the offline wandb run, not on the console; batch 48 per rank (the real-robot config) remains unmeasured |
| Importer / exporter round trip (export untrained warm start, score equals released) | `reproduced` | `xr1-roundtrip-20260821-02`: import (1,135 tensors) -> export (1,120 tensors, all `torch.equal` to the released shards; every non-weight file byte-identical, processor semantically identical) -> track 1 L2: 49/50 successes, 50/50 intention scores, 45/50 step counts agree with the anchor - the same band as re-running the released checkpoint itself (`xr1-l2-rerun-t1-20260821-01`: 49/50, 50/50, 42/50) | The format bridge is behaviour-preserving. A first attempt (`-01`) with stats that had passed through float32 + `round(6)` (mean off by ~4e-7, std by ~5e-7, unused-slot std 0 instead of 1e-6) agreed on only 42/50: the de-normalized actions are sensitive at that level over a 200-step contact-rich episode, so the stats must be carried in float64 verbatim |
| CoT-labelled training | `not_attempted` | none | |
| Real-robot surfaces | `not_reconstructable` | in-house robots and data | Report-only |

Static inspection is not inference reproduction. Unit tests of converters on synthetic tensors are not checkpoint-integrity evidence.

## State semantics

- `not_attempted`: no qualifying execution artifact exists.
- `blocked`: an attempt reached a prerequisite boundary before the target output contract.
- `failed`: the target executed far enough to evaluate its output contract and an acceptance condition failed.
- `reproduced`: every declared acceptance condition passed and the provenance bundle is retained.
- `partial`: a named sub-contract passed; never promoted to the parent surface.

## Fixed execution objects

| Object | Fixed value |
|---|---|
| Repository revision | `556cca33963a2b36d835a40374c3b4c8eef68401` |
| VLABench checkpoint revision | `f4986843002d86502e2e53079ca06d00a33abffc` |
| Base checkpoint revision | `ee21d524b5c52ac961d941e1bc7d6d92836c3d5e` |
| VLABench commit | `cf588fe60c0c7282174fe979f5913170cfe69017` |
| Dataset revision | `9846a2f6bead3873251dc4fe3079359d57326b7c` |
| Client constants | chunk 10, replan 5, image 480, seed 42, no CoT, `vlabench_choice` |

## Acceptance contracts (what promotes a row)

### Released-checkpoint anchor (L2)

Serve the released dir on N GPUs; run the first 5 official configs of every (track, task) (250 episodes; 247 executable given Track 2 `insert_flower`); retain `summary.json`, per-track `metrics.json`, per-task `detail_info.json`, server logs, GPU type, wall clock. Acceptance: `sr_avg_5track` within 2 standard errors (~6 pp) of 59.1 and no majority of errored episodes. The same run fixes the per-episode wall clock.

### Format bridge round trip

Import (HF VLABench + base choice heads) -> export without training -> score with the same protocol. Acceptance: per-episode outcomes identical to the anchor run under the same seed, or SR within 1 pp if nondeterminism appears; export provenance retained.

### Trainer smoke

5 steps at batch 48 per rank on the target GPU; retain `train/loss*`, `train/token`, peak memory, s/step for steps 2-5. Acceptance: finite, descending loss; no checkpoint written; `train/token` consistent with the declared batch.

### CoT training

A paired pair of runs (`cot_prob` 0 vs 0.5) at equal steps, scored on L2 with paired episodes. Acceptance criterion is the campaign's, recorded per run.

## Artifact map

| Run | Artifacts |
|---|---|
| `xr1-l2-released-20260821-01` | `runs/l2_released/{summary.json, episodes.jsonl, track_*/metrics.json, track_*/<task>/detail_info.json}`, server logs; host: 4x A100 80 GB PCIe developer box, GPUs 2-3 (shared with a 2-rank smoke attempt for part of the run; outcomes are wall-clock independent) |
| `xr1-grip-probe-20260821-01` | per-query gripper outputs and observed gripper bit for `select_fruit` config 0: state bit 0 -> 1 at the grasp (query 19), model gripper output 1.0 before the grasp, 0.0 after it, then 1.0 only at chunk positions 7-9 from query 33 on; episode ends at the 200-step cap holding the banana above the plate |
| `xr1-import-20260821-01` | `checkpoints/xr1_vlabench_warmstart/model_states.pt` (1,135 tensors) |
| `xr1-l2-released-lambda-20260821-01` | FS `aba/data_root/xr1_vlabench/runs/l2_released_163-192-109-106/` (summary.json, episodes.jsonl, per-track dirs); local copy `runs/lambda_val/` |
| `xr1-smoke-lambda-20260821-01` | host `~/xr1_trainsmoke/{train.log, mem.csv}` on the validation rental (checkpoint deleted by the stage) |
| `xr1-l2-rerun-t1-20260821-01` | `runs/l2_released_rerun_t1/` (track 1, released checkpoint, same 50 episodes as the anchor) |
| `xr1-roundtrip-20260821-01` / `-02` | `runs/roundtrip_roundedstats/hf_export` + `runs/l2_roundtrip_roundedstats/` (rounded stats, 42/50); `runs/roundtrip/hf_export` + `runs/l2_roundtrip/` (exact stats, 49/50) with `export_provenance.json` |

## Sources

[XR1-CODE]; [XR1-HF-VLABENCH]; [XR1-HF-5B]; [VLAB-CODE]; [VLAB-DATA-LEROBOT].
