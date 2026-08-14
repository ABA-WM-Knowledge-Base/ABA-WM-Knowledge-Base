---
id: world-model-kb.papers.cosmos-policy.codebase
title: Cosmos Policy Released Implementation Graph
kind: reference
status: maintained
last_updated: 2026-08-14
owners:
  - AIBuildAI world-model group
---

# Cosmos Policy Released Implementation Graph

## Retrieval metadata

**Relevant queries:** cosmos-policy GitHub, PolicyEvalConfig, get_action, policy_video2world_model, hybrid_edm_sde, wan2pt1 tokenizer, libero_dataset, cosmos_predict2_2b_480p, Predict2 versus Predict2.5 cookbook, or train.py.

**Knowledge provided:** the pinned Predict2 repository call graph, configuration surfaces, tensor and checkpoint contracts, paper-code mismatches, and the Cookbook Predict2.5 split.

**Related pages:** [`paper.md`](paper.md) owns method claims; [`reproduction.md`](reproduction.md) owns execution state; [Cosmos-Predict2.5 codebase](../cosmos-predict2-5/codebase.md) owns the later video-model tree.

## 1. Revision policy

All file mappings below use `NVlabs/cosmos-policy@18a2accadf4e7a3531e56754102af5a24d2316da` (2026-01-23). The Cookbook documents a second tree: clone `NVlabs/cosmos-policy` for Predict2, or use `nvidia-cosmos/cosmos-predict2.5` in-tree `cosmos_policy` for Predict2.5. Those trees must not be merged when attributing Tables 1-5. [CPOL-CODE; CPOL-COOKBOOK]

The repository vendors a large Predict2 / Imaginaire / Reason1 subtree under `cosmos_policy/_src/`. Policy-specific surfaces live under `cosmos_policy/{datasets,experiments,models,modules,tokenizers,scripts,config}`. Mapping the vendored video stack as if it were Cosmos-Predict2.5 or Cosmos3-Nano is invalid. [CPOL-CODE]

## 2. Released surface versus paper surface

| Capability | Paper | Pinned Predict2 repo | Consequence |
|---|---|---|---|
| LIBERO train/eval | Table 1, 6000 trials | `LIBERO.md`, `run_libero_eval.py`, `libero_dataset.py`, `regenerate_libero_dataset.py` | primary public eval surface |
| RoboCasa train/eval | Table 2, 3600 trials | `ROBOCASA.md`, `run_robocasa_eval.py`, `robocasa_dataset.py` | separate checkpoint and data |
| ALOHA train/eval | Table 3, 101 states | `ALOHA.md`, `deploy.py`, `run_aloha_eval.py`; real hardware required | documented, not reconstructable without the robot |
| Latent frame injection | Sec. 4.1 | `policy_video2world_model.py`, `tokenizers/wan2pt1.py`, experiment configs | released core mechanism |
| Hybrid EDM / `sigma_min=4` | Appendix A.2.1 | `modules/hybrid_edm_sde.py`, `modules/cosmos_sampler.py` | sampling contract is code-owned |
| Joint 50/25/25 masks | Fig. 12 | `config/experiment/cosmos_policy_experiment_configs.py`, trainer masks | confirm mask names against paper fractions before attributing Table 4-5 |
| Predict2.5 post-training | Cookbook only | not this commit's scientific identity | later path |
| Cosmos3-Nano Policy-DROID | Cosmos 3 docs | absent | different product |

## 3. Configuration resolution

Documented Docker + `uv run --extra cu128 --group libero --python 3.10 python` after `SETUP.md`. Domain docs are first-class: `LIBERO.md`, `ROBOCASA.md`, `ALOHA.md`. [CPOL-CODE]

Training entry: `cosmos_policy/scripts/train.py` plus `cosmos_policy/config/experiment/cosmos_policy_experiment_configs.py`. Inference configs are named `cosmos_predict2_2b_480p_<domain>__inference_only` (LIBERO example `cosmos_predict2_2b_480p_libero__inference_only`). `ckpt_path` defaults to the matching Hugging Face repo. [CPOL-CODE]

LIBERO-only `flip_images=True`. Wrist image, proprio normalization, and JPEG augmentation are config fields, not silent preprocessing. Denoising-step split in the README example: actions 5, future state 1, value 1 for a direct-policy snippet; paper Appendix A.3.1 uses 5 (LIBERO/RoboCasa) or 10 (ALOHA) parallel steps for the published tables, and 10/5/5 autoregressive steps for planning. Do not mix the README snippet with Table 1 protocol. [P25-COSMOS-POLICY, Appendix A.3.1; CPOL-CODE]

## 4. Model construction and tensor contract

```text
run_libero_eval.PolicyEvalConfig
  -> cosmos_utils.load_dataset_stats
  -> cosmos_utils.init_t5_text_embeddings_cache
  -> cosmos_utils.get_model
  -> cosmos_utils.get_action
       -> policy_video2world_model (EDM DiT)
       -> wan2pt1 tokenizer on RGB only
       -> tiled proprio / action / value latent frames
       -> cosmos_sampler / hybrid_edm_sde
```

Released policy modules:

| Symbol | Path | Role |
|---|---|---|
| `get_action` | `experiments/robot/cosmos_utils.py` | observation dict -> action chunk |
| `PolicyEvalConfig` | `experiments/robot/libero/run_libero_eval.py` | LIBERO eval dataclass |
| `policy_video2world_model` | `models/policy_video2world_model.py` | Predict2 Video2World adapted for policy latents |
| `policy_text2world_model` | `models/policy_text2world_model.py` | text2world sibling; not the Table 1 identity |
| `hybrid_edm_sde` | `modules/hybrid_edm_sde.py` | paper hybrid noise schedule |
| `cosmos_sampler` | `modules/cosmos_sampler.py` | `sigma_min` / step budget |
| `wan2pt1` | `tokenizers/wan2pt1.py` | image VAE; non-image modalities are tiled, not VAE-encoded |
| loaders | `datasets/{libero,robocasa,aloha}_dataset.py` | domain tensors and T5 caches |

Expected layout for a two-camera + wrist robot: eleven latent frames as in [`paper.md`](paper.md) Sec. 2.1. Action chunk length is domain-specific (16 / 32 / 50). A hosted model ID does not reveal evaluated SHA. [CPOL-CODE; P25-COSMOS-POLICY, Fig. 2]

## 5. Dataset and embedding caches

T5 caches are first-class artifacts: `datasets/save_{libero,robocasa,aloha}_t5_text_embeddings.py` and `t5_embedding_utils.py`. Hugging Face LIBERO weights ship `libero_dataset_statistics.json` and `libero_t5_embeddings.pkl`. Regeneration scripts (`regenerate_libero_dataset.py`, `regenerate_robocasa_dataset.py`) are preprocessing, not Table 1/2 reproduction. [CPOL-HF-LIBERO; CPOL-DATA-LIBERO; CPOL-CODE]

## 6. Training call graph

```text
scripts/train.py
  -> trainer.py / config_v2.py
  -> policy_video2world_model
  -> dataset_common + domain loader
  -> mask split: policy / world-model / value
  -> EDM loss on noised target frames
  -> full-backbone Adam-style update (paper: all Predict2-2B weights)
```

Paper step counts (40K / 45K / 50K) and global batches (1920 / 800 / 200) must be recovered from the resolved experiment config, not assumed from filenames. [P25-COSMOS-POLICY, Appendix A.2; CPOL-CODE]

## 7. Inference VRAM and latency (documented, not measured here)

README VRAM: direct policy 6.8 GB LIBERO, 8.9 GB RoboCasa, 6.0 GB ALOHA; planning 10.0 GB serial or N GPUs parallel. Paper latency on one H100: 0.61 s at 5 steps, 0.95 s at 10 steps, 0.16 s at 1 step; planning 4.9 s for N=8 on 8 H100s. [CPOL-CODE; P25-COSMOS-POLICY, Appendix A.4.2]

## 8. Static defects and mismatch ledger

| ID | Evidence | Effect | Minimal repair boundary |
|---|---|---|---|
| `POLICY-CODE-GAP-01` | Cookbook Predict2.5 in-tree `cosmos_policy` vs this repo | following the wrong clone silently changes initialization | pin `NVlabs/cosmos-policy` for Tables 1-5 |
| `POLICY-CODE-GAP-02` | README denoising split (5/1/1) vs Appendix A.3.1 table protocol (5 or 10 parallel steps) | copied snippet is not Table 1 protocol | record resolved step counts in any executed run |
| `POLICY-CODE-GAP-03` | `policy_text2world_model.py` exists beside video2world | wrong constructor can be selected | use video2world configs named `cosmos_predict2_2b_480p_*` |
| `POLICY-CODE-GAP-04` | Hugging Face `ckpt_path` has no inner SHA | hosted ID != evaluated snapshot | log revision or file hash on execution |
| `POLICY-CODE-GAP-05` | ALOHA eval requires matched hardware and 101-state protocol | public code cannot reconstruct Table 3 | treat as paper-only without hardware identity |
| `POLICY-CODE-GAP-06` | T5 embedding pickle must already exist or be generated | missing cache blocks `get_action` | run the matching `save_*_t5_text_embeddings` script and pin the pickle hash |
| `POLICY-CODE-GAP-07` | Vendored `_src/predict2` and `_src/reason1` trees | easy to cite Cosmos3 Reasoner by accident | policy claims attach only to `policy_video2world_model` |

## 9. Change surfaces for optimization

| Intervention | Primary code surface | Controlled variables to retain |
|---|---|---|
| Latent-frame versus new action head | `policy_video2world_model.py`, tokenizer tiling | backbone, data, sampler, eval protocol |
| Auxiliary future/value losses | experiment mask / loss keys | step count, batch mix 50/25/25 |
| `V(s')` versus `Q(s,a)` | value-frame conditioning mask | rollout set, N, majority-mean rule |
| Hybrid noise / `sigma_min` | `hybrid_edm_sde.py`, `cosmos_sampler.py` | train schedule versus eval `sigma_min` |
| JPEG / flip augmentations | LIBERO dataloader flags | eval-only tricks versus train-time augment |
| Best-of-N | planning loop around `get_action` | dual checkpoints, GPU count, full-chunk execution |

## Sources

[CPOL-CODE; CPOL-COOKBOOK; CPOL-HF-LIBERO; CPOL-DATA-LIBERO; P25-COSMOS-POLICY]
