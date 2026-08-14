---
id: world-model-kb.papers.lapa.codebase
title: LAPA Released Implementation Graph
kind: reference
status: maintained
last_updated: 2026-08-14
owners:
  - AIBuildAI world-model group
---

# LAPA Released Implementation Graph

## Retrieval metadata

**Relevant queries:** LatentActionPretraining LAPA, laq_model, latent_pretraining.inference, finetune_real.sh, SimplerEnv main_inference_lapa, LAPA7B-openx.

**Knowledge provided:** pinned paths, three-stage scripts, Hub files (`tokenizer.model`, `vqgan`, `params`, `laq_openx.pt`), and gaps.

**Related pages:** [`paper.md`](paper.md); [`reproduction.md`](reproduction.md).

## 1. Revision

`LatentActionPretraining/LAPA@46aca51d7faebcec02d7d323bbb3820c2df07bc6` (2025-01-22), MIT. Vendored `SimplerEnv/` is a large subtree. [LAPA-CODE]

Hub bundle [LAPA-HF]: download `tokenizer.model`, `vqgan`, `params` into `lapa_checkpoints/`. LAQ: `laq_openx.pt`. Cite as [LAPA-HF] / `LAPA7B-openx`.

## 2. Tree (LAPA-owned, not all of SimplerEnv)

```text
laq/train_sthv2.py
laq/inference_sthv2.py
laq/laq_model/latent_action_quantization.py
laq/laq_model/laq_trainer.py
laq/laq_model/nsvq.py
latent_pretraining/train.py
latent_pretraining/inference.py
latent_pretraining/deploy.py
latent_pretraining/llama.py
latent_pretraining/llama_action.py
latent_pretraining/vision_llama.py
latent_pretraining/delta_llama_action.py
latent_pretraining/vqgan.py
latent_pretraining/data.py
data/finetune_preprocess.py
scripts/latent_pretrain_openx.sh
scripts/finetune_real.sh
scripts/finetune_simpler.sh
SimplerEnv/scripts/lapa_bridge.sh
SimplerEnv/simpler_env/main_inference_lapa.py
SimplerEnv/simpler_env/policies/lapa/lapa_model.py
```

## 3. Stage graphs

**LAQ**

```text
conda activate laq
cd laq && pip install -e .
accelerate launch train_sthv2.py
python inference_sthv2.py   # needs jsonl with VQGAN vision tokens
```

SSv2-style folders (trajectory/image). Custom data requires a loader change.

**Latent pretrain**

```text
# LWM-Chat-1M-Jax under lwm_checkpoints
# pretrain jsonl under data/
./scripts/latent_pretrain_openx.sh
```

**Inference of latents (not joints)**

```text
python -m latent_pretraining.inference
```

**Finetune to real actions**

```text
python data/finetune_preprocess.py --input_path ... --output_filename data/real_finetune.jsonl --csv_filename data/real_finetune.csv
./scripts/finetune_real.sh
python -m latent_pretraining.deploy --load_checkpoint "params::/path" --action_scale_file data/real_finetune.csv
```

`--mesh_dim` second index = GPU count (paper: 4x80GB A100). SIMPLER: `./scripts/finetune_simpler.sh` then `SimplerEnv/scripts/lapa_bridge.sh`.

Pinned-commit LAPA-owned blobs (excluding vendored `SimplerEnv/`; 41 owned blobs of 770 total):

| Path | Bytes | Role |
|---|---:|---|
| `laq/laq_model/latent_action_quantization.py` | 11046 | LAQ |
| `laq/laq_model/nsvq.py` | 15065 | NSVQ codebook |
| `laq/laq_model/laq_trainer.py` | 10533 | LAQ train |
| `laq/train_sthv2.py` | 665 | accelerate entry |
| `laq/inference_sthv2.py` | 5900 | dump latent jsonl |
| `latent_pretraining/llama.py` | 57233 | LWM backbone |
| `latent_pretraining/vision_llama.py` | 34190 | vision tower |
| `latent_pretraining/delta_llama_action.py` | 38590 | action-delta LLaMA |
| `latent_pretraining/train.py` | 38141 | Stage 2 |
| `latent_pretraining/inference.py` | 3609 | latent smoke |
| `latent_pretraining/deploy.py` | 6576 | Stage 3 joints |
| `latent_pretraining/data.py` | 111758 | jsonl loader |
| `latent_pretraining/vqgan.py` | 12723 | vision tokens |
| `data/finetune_preprocess.py` | 3436 | discretize actions |
| `scripts/latent_pretrain_openx.sh` | 3432 | 8-GPU pretrain |
| `scripts/finetune_real.sh` | 3817 | real adapter |
| `scripts/finetune_simpler.sh` | 3606 | SIMPLER adapter |

Cite Hub weights as [LAPA-HF] / `LAPA7B-openx`. Inference without `deploy.py` emits codes in alphabet `8^4`, not Franka joints.

## 4. Gap ledger

| ID | Evidence | Effect | Repair |
|---|---|---|---|
| `LA-CODE-GAP-01` | inference emits latent codes | not a robot policy until deploy | always run Stage 3 for joints |
| `LA-CODE-GAP-02` | SSv2 folder assumption | custom LAQ data fails | rewrite `laq_model/data.py` |
| `LA-CODE-GAP-03` | LWM backbone extra download | pretrain blocked | [LAPA-LWM] |
| `LA-CODE-GAP-04` | SimplerEnv vendored | version drift vs upstream | pin this commit |
| `LA-CODE-GAP-05` | `--mesh_dim` GPU count | wrong shard | match physical GPUs |
| `LA-CODE-GAP-06` | no lockfile | env drift | external lock |

## 5. Change surfaces

| Intervention | Files |
|---|---|
| Codebook / NSVQ | `latent_action_quantization.py`, `nsvq.py` |
| Window H | LAQ trainer args |
| Latent VLA | `delta_llama_action.py`, `sampler_latent_action_pretrain.py` |
| ID decoder to joints | `deploy.py`, csv scale file |
| SIMPLER policy | `policies/lapa/lapa_model.py` |

Attachment for Cosmos3 is **WAM/ID**, not Reasoner, not Policy-DROID continuous serving without a discrete-to-continuous adapter.

## 6. Hub files versus scripts

| Artifact | Role | Stage |
|---|---|---|
| `tokenizer.model` | LWM tokenizer | 2-3 |
| `vqgan` | vision tokens | 2-3 |
| `params` | 7B latent VLA | 2 smoke / 3 init |
| `laq_openx.pt` | LAQ | 1 / decoder WM |
| `latent_action_pretraining_openx.jsonl` | Stage 2 data | 2 |
| LWM-Chat-1M-Jax | backbone init | 2 retrain |

Cite the bundle as [LAPA-HF] / `LAPA7B-openx`. `python -m latent_pretraining.inference` is Stage 2 smoke. Joints require `deploy.py` plus csv scales from `finetune_preprocess.py`.

Also LAPA-owned: `latent_pretraining/llama_action.py` (35905), `delta_llama.py` (35731), `ring_attention.py` (73217), samplers `sampler_action_pretrain.py` / `sampler_latent_action_pretrain.py` / `sampler_latent_pretrain.py`, `laq/laq_model/attention.py` (9901), `laq/laq_model/t5.py`. Vendored SimplerEnv is 729 of 770 blobs — do not treat those paths as LAPA-authored except `lapa_bridge.sh` and `policies/lapa/`.

## 7. Paper versus code

| Paper stage | Released entry | Invalid use |
|---|---|---|
| Stage 1 LAQ | `laq/train_sthv2.py`, `laq_openx.pt` | treat as joints |
| Stage 2 latent VLA | `latent_pretraining/inference.py`, Hub `params` | Table 2 success |
| Stage 3 adapter | `deploy.py` + csv | unlabeled Hub demo |
| SIMPLER | `SimplerEnv/scripts/lapa_bridge.sh` | merge with Franka Table 2 |
| Decoder WM | Fig. 7 qualitative | Table 2 metric |

`--mesh_dim` second index must equal physical GPU count. `requirements.txt` is not a lockfile. [LAPA-CODE]

## Sources

- [LAPA-CODE], [LAPA-HF], [LAPA-LWM].
