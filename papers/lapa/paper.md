---
id: world-model-kb.papers.lapa.paper
title: LAPA Method, Architecture, and Experimental Evidence
kind: paper
status: maintained
last_updated: 2026-08-14
owners:
  - AIBuildAI world-model group
---

# LAPA Method, Architecture, and Experimental Evidence

## Retrieval metadata

**Relevant queries:** LAPA, latent action quantization, LAQ, latent VLA, Language Table 62.0, Open-X 50.1, human video SSv2, ICLR 2025, LAPA7B-openx, not Genie.

**Knowledge provided:** three-stage method, Language Table and real-robot tables, codebook scaling, decoder-as-world-model qualitative, and Hub naming (`LAPA7B-openx` / [LAPA-HF]).

**Related pages:** [`README.md`](README.md); [`codebase.md`](codebase.md); [inverse dynamics](../../foundations/problem-formulation/inverse-dynamics.md); [latent world models](../../foundations/representations/latent-world-model.md).

This work is **not** Genie and not a generative interactive environment. [LAPA-PAPER]

## 1. Problem statement

LAPA learns a **discrete latent action** from unlabeled videos, pretrains a vision-language model to predict those codes from (image, instruction), then finetunes a small action decoder to real robot joints. Ground-truth actions are unused in stages 1-2. The released 7B Open-X bundle is cited as [LAPA-HF] / `LAPA7B-openx`. [LAPA-PAPER, Abstract; LAPA-HF]

```text
Stage 1 LAQ: (o_t, o_{t+1}) -> quantized latent a~  (space 8^4 in the inference README)
Stage 2 latent VLA: (o_t, instruction) -> a~
Stage 3: map a~ -> real end-effector / gripper via finetune
optional: LAQ decoder (o_t, a~) -> imagined o_{t+1}
```

Output of the pretrained VLA is **latent action**, not executable joints, until Stage 3. [LAPA-CODE README]

## 2. Architecture

### 2.1 Latent action quantizer (LAQ)

Vector-quantized inverse dynamics on frame pairs. Window `H` is chosen so the next frame is ~0.6 s ahead for robot video (Bridgev2 5 Hz => default `H=3`) and ~2.4 s for slower human video. Ablations show robustness to `H` except very large windows. Codebook/sequence length scale in Fig. 5 and Fig. 16. [LAPA-PAPER, Sec. 3, Fig. 15-16]

Implementation: `laq/laq_model/latent_action_quantization.py`, `laq/train_sthv2.py`. Released LAQ weights: `laq_openx.pt` on [LAPA-HF].

### 2.2 Latent VLA backbone

JAX Large World Model lineage (`LWM-Chat-1M-Jax` / [LAPA-LWM]). Files: `latent_pretraining/llama.py`, `vision_llama.py`, `delta_llama_action.py`. Pretrain script `scripts/latent_pretrain_openx.sh`. Authors report 8xH100 ~34 hours and that ~70K steps at batch 256 is enough for decent finetune. [LAPA-PAPER; LAPA-CODE README]

### 2.3 Robot finetune and decoder WM

`data/finetune_preprocess.py` discretizes real actions into jsonl/csv. `scripts/finetune_real.sh` / `finetune_simpler.sh`. Deploy: `python -m latent_pretraining.deploy`. Decoder rollouts (Fig. 7) condition LAQ's decoder on `(x_1, predicted latent)` without Stage 3 — qualitative broccoli-from-pot example, not a control success table. [LAPA-PAPER, Sec. 5]

## 3. Language Table (Table 1)

Average success % ± SE. Fine-tune trajectory counts in headers. 50 rollouts per task category in appendix (250 per model per table). [LAPA-PAPER, Table 1]

| Method | In-domain 1k seen | In-domain unseen | Cross-task 7k seen | Cross-task unseen | Cross-env 1k seen | Cross-env unseen |
|---|---:|---:|---:|---:|---:|---:|
| Scratch | 15.6±9.2 | 15.2±8.3 | 27.2±13.6 | 22.4±11.0 | 15.6±9.2 | 15.2±8.3 |
| UniPi | 22.0±12.5 | 13.2±7.7 | 20.8±12.0 | 16.0±9.1 | 13.6±8.6 | 12.0±7.5 |
| Vpt | 44.0±7.5 | 32.8±4.6 | 72.0±6.8 | **60.8±6.6** | 18.0±7.7 | 18.4±9.7 |
| LAPA | 62.0±8.7 | 49.6±9.5 | 73.2±6.8 | 54.8±9.1 | 33.6±12.7 | 29.6±12.0 |
| ActionVLA | **77.0±3.5** | **58.8±6.6** | **77.0±3.5** | 58.8±6.6 | **64.8±5.2** | **54.0±7.0** |

In-domain: pretrain 181k, finetune 1k (0.5% labels). Cross-env: pretrain 440k real, finetune 1k sim. ActionVLA remains the labeled-action upper bound on most Language Table slices; LAPA beats Scratch/UniPi/Vpt without using those labels in pretrain. [LAPA-PAPER, Sec. 4.3]

## 4. Real-world tabletop (Table 2)

54 rollouts per model (3 tasks x 3 generalization types x 6). Partial success. Franka 7 DoF. [LAPA-PAPER, Table 2, Fig. 3]

| Method | Unseen combo | Unseen obj | Unseen instr | AVG |
|---|---:|---:|---:|---:|
| Scratch | 18.0 | 20.3 | 25.4 | 21.2 |
| ActionVLA (Bridge) | 38.3 | 31.8 | 27.7 | 32.6 |
| OpenVLA (Bridge) | 35.6 | 34.6 | 22.1 | 30.8 |
| LAPA (Bridge) | 43.4 | 31.4 | 35.6 | 36.8 |
| OpenVLA (Open-X) | 46.2 | 42.1 | 43.4 | 43.9 |
| LAPA (Open-X) | **57.8** | **43.9** | **48.5** | **50.1** |
| LAPA (Human videos) | 36.5 | 37.4 | 28.1 | 34.0 |

Paired win rate LAPA (Open-X) vs OpenVLA (Open-X): **65.4%** excluding ties; with ties, 31.5% / 16.7% / 51.9% tie. Identical object initial poses. [LAPA-PAPER, Fig. 11]

SIMPLER: 4 WidowX tasks, 100 finetune trajectories (25 successful filtered rollouts x 4), 24 eval rollouts/task. Human-video pretrain still beats Scratch/UniPi/Vpt (Fig. 4a). [LAPA-PAPER, Sec. 4.1, Fig. 4]

### 4.1 Stage-1 LAQ details

Vector-quantized inverse dynamics on frame pairs. Implementation: `laq/laq_model/latent_action_quantization.py` (11046 B), NSVQ in `laq/laq_model/nsvq.py` (15065 B), trainer `laq/laq_model/laq_trainer.py` (10533 B). Window `H`: Bridgev2 5 Hz default `H=3` (~0.6 s); human video ~2.4 s. Ablations (Fig. 15) are robust except very large windows. Inference alphabet documented as space size `8^4`. Released LAQ weights: `laq_openx.pt` on [LAPA-HF]. Data loader assumes SSv2-style trajectory folders (`laq/laq_model/data.py`). [LAPA-PAPER, Sec. 3; LAPA-CODE]

### 4.2 Stage-2 latent VLA details

JAX LWM lineage (`latent_pretraining/llama.py` 57233 B, `vision_llama.py` 34190 B, `delta_llama_action.py` 38590 B, `train.py` 38141 B). Pretrain script `scripts/latent_pretrain_openx.sh`. Dataset jsonl advertised on [LAPA-HF]. Authors: 8xH100 ~34 hours; ~70K steps at batch 256 is enough for decent finetune. Output is **latent codes**, not joints. [LAPA-CODE README]

### 4.3 Stage-3 and SIMPLER files

`data/finetune_preprocess.py` discretizes 7-DoF Franka actions into jsonl/csv. `scripts/finetune_real.sh` / `finetune_simpler.sh`. Deploy: `python -m latent_pretraining.deploy`. SIMPLER glue (vendored): `SimplerEnv/scripts/lapa_bridge.sh`, `SimplerEnv/simpler_env/main_inference_lapa.py`, `SimplerEnv/simpler_env/policies/lapa/lapa_model.py`. Do not treat the entire SimplerEnv subtree as LAPA-authored.

## 5. Scaling and human video

Fig. 5: scale LAQ size, Bridgev2 data fraction, latent sequence length, vocab size on SIMPLER. Fig. 16: Language Table prefers vocab growth over sequence length. Table 12 (appendix): 10% vs 100% SSv2 helps SIMPLER (exact cells not fully recovered in the HTML extract). [LAPA-PAPER, Fig. 5, 16]

## 6. Limits

- ActionVLA still leads several Language Table cells.
- Real-world n=54; many ties vs OpenVLA.
- Decoder WM is qualitative.
- Stage 3 is embodiment-specific; latent space is not a universal joint interface.
- Hub inference without finetune does **not** emit robot actions.
- Training/inference not executed here.

## 7. Cosmos3 attachment map

| LAPA mechanism | Cosmos3 surface | Not this surface |
|---|---|---|
| LAQ from video | Generator WAM/ID quantizer | Reasoner planner ID |
| Instruction-conditioned codes | multimodal WAM tokens | Policy-DROID 9D serving |
| Stage-3 adapter | small domain decoder | unlabeled Hub demo as joints |
| LAQ decoder WM | coarse FD | Table 2 success |
| Human SSv2 | unlabeled video mix | claiming Open-X 50.1 without robot adapter |

Never write the hyphenated Hub slug in running text. Cite [LAPA-HF] / `LAPA7B-openx`.

## 8. Table 1 remainder (ActionVLA still leads)

Cross-task seen: LAPA 73.2±6.8 versus ActionVLA **77.0±3.5** versus Vpt 72.0±6.8. Cross-task unseen: LAPA 54.8±9.1 versus Vpt **60.8±6.6**. Cross-env seen: LAPA 33.6±12.7 versus ActionVLA **64.8±5.2**. Cross-env unseen: LAPA 29.6±12.0 versus ActionVLA **54.0±7.0**. These cells prevent a "LAPA dominates Language Table" slogan. [LAPA-PAPER, Table 1]

### 8.1 Real-world Table 2 remainder

Unseen object: LAPA Open-X **43.9** versus OpenVLA Open-X 42.1 versus LAPA Bridge 31.4. Unseen instruction: 48.5 versus 43.4 versus 35.6. Human-video AVG 34.0 sits between Scratch 21.2 and OpenVLA Open-X 43.9. Paired protocol: 31.5% LAPA wins / 16.7% OpenVLA wins / 51.9% tie; 65.4% excluding ties. Identical object initial poses. [LAPA-PAPER, Table 2, Fig. 11]

### 8.2 Intended equations (Stage 1-2)

```text
a~ = Q( E_id(o_t, o_{t+H}) )          # discrete latent action
a~_hat = VLA(o_t, instruction)        # Stage 2 prediction
o_hat_{t+H} = D_laq(o_t, a~_hat)      # optional decoder WM
a_robot = Dec_adapter(a~_hat; csv)    # Stage 3 only
```

`H` matches ~0.6 s on Bridgev2 (`H=3` at 5 Hz). Alphabet documented as `8^4`. Ground-truth joints unused until Stage 3. [LAPA-PAPER, Sec. 3; LAPA-CODE]

### 8.3 Compute and data (documented)

Open-X latent pretrain: 8xH100 ~34 hours. Authors observe ~70K steps at batch 256 can be enough for decent finetune. Real finetune: 4x80GB A100. Language Table in-domain uses 181k unlabeled + 1k labeled (0.5%). Cross-env: 440k real unlabeled + 1k sim labeled. Human SSv2 is unlabeled human video, then the same robot adapter. SIMPLER: 100 finetune trajectories (25 successful filtered x 4 tasks), 24 eval rollouts/task. [LAPA-PAPER, Sec. 4; LAPA-CODE README]

### 8.4 What this model is not

Not Genie. Not OpenVLA until Stage 3. Not a Cosmos3 Reasoner. Not Policy-DROID continuous serving without a discrete-to-continuous adapter. Hub [LAPA-HF] / `LAPA7B-openx` without `deploy.py` is a latent VLA demo.

## Sources

- [LAPA-PAPER] arXiv:2410.11758 ICLR 2025.
- [LAPA-CODE] `LatentActionPretraining/LAPA@46aca51d7faebcec02d7d323bbb3820c2df07bc6`.
- [LAPA-HF] `LAPA7B-openx` bundle.
