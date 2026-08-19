---
id: world-model-kb.papers.ivideogpt
title: iVideoGPT Paper Knowledge Entry
kind: paper
status: maintained
last_updated: 2026-08-19
owners:
  - AIBuildAI world-model group
---

# iVideoGPT Paper Knowledge Entry

## Retrieval metadata

**Relevant queries:** iVideoGPT, compressive VQGAN, OXE, BAIR FVD, RoboNet, VP2, MBPO, ivideogpt-oxe-64-act-free, NeurIPS 2024, not RLVR-World.

**Knowledge provided:** identity, architecture, tables, named checkpoints, reproduction state, Generator FD/WAM transfers.

**Related pages:** [autoregressive modeling](../../foundations/learning-objectives/autoregressive-modeling.md); [forward dynamics](../../foundations/problem-formulation/forward-dynamics.md); [model-based RL](../../foundations/decision-making/model-based-rl.md); [autoregressive and recurrent generation](../../components/generative-modeling/autoregressive.md); [action-conditioned video modeling](../../components/generative-modeling/action-conditioned-video.md); [Cosmos3-Nano action modeling](../../models/cosmos3-nano/action-modeling.md); [Cosmos3-Nano generator](../../models/cosmos3-nano/generator.md).

Project page: [thuml.github.io/iVideoGPT](https://thuml.github.io/iVideoGPT/). Numbers bind to v3. [IVG-PAPER; IVG-PROJECT]

## Identity and revision boundary

| Field | Canonical value | Consequence |
|---|---|---|
| Work | *iVideoGPT: Interactive VideoGPTs are Scalable World Models* | NeurIPS 2024 camera-ready. |
| Paper | arXiv:2405.15223 **v3** (2024-11-01) | Tables 1, 2, 6-8. [IVG-PAPER] |
| Code | `thuml/iVideoGPT@d601d5cac9e96c6aa0c17cb37ed6a7c7ca1fb210` | `train_tokenizer.py`, `train_gpt.py`, `inference/predict.py`. [IVG-CODE] |
| OXE act-free 64 | `thuml/ivideogpt-oxe-64-act-free` | 114M tokenizer + 138M transformer. Primary Hub smoke. [IVG-HF-OXE-64-ACT-FREE] |
| OXE medium | README `ivideogpt-oxe-64-act-free-medium`; YAML title `ivideogpt-oxe-medium` | 436M transformer. [IVG-HF-OXE-MEDIUM] |
| OXE goal | `thuml/ivideogpt-oxe-64-goal-cond` | Goal-conditioned card, still action-free OXE. [IVG-HF-OXE-64-GOAL-COND] |
| OXE 256 | README `ivideogpt-oxe-256-act-free`; YAML title `ivideogpt-oxe-256` | Undertrained starting point per README. [IVG-HF-OXE-256] |
| OXE act-cond 64 | YAML lists `thuml/ivideogpt-oxe-64-act-cond` | Named identity. OXE **pretrain** is action-free because action spaces are heterogeneous. Do not treat this card as Table 1 OXE pretrain. [IVG-HF-OXE-64-ACT-COND] |
| Not this work | RLVR-World NeurIPS 2025 (`thuml/RLVR-World`) | Later reward-finetuning method that can *use* iVideoGPT. Not an iVideoGPT table. |

Public 256x256 RoboNet checkpoints were deleted accidentally; paper Table 1 256 numbers remain. [IVG-CODE README]

## Operational model boundary

iVideoGPT is a **compressive tokenizer plus autoregressive transformer world model**. Action-free OXE pretrain, then optional action/goal finetune. It outputs future video tokens (and optional reward tokens), not a universal robot policy.

```text
context frames -> E_c
future frames  -> E_p (4x4 bottleneck, cross-attends to E_c)
tokens + optional action/goal/reward -> LLaMA-style AR
decode with D_p conditioned on context features
```

| Surface | Inputs | Output | Invalid projection |
|---|---|---|---|
| Act-free prediction | context frames | future video | OXE act-cond Hub as pretrain |
| Act-cond finetune | + actions (BAIR/RoboNet/VP2) | future video | RLVR-World scores |
| Goal-cond | + goal frame | future video | Reasoner text plan |
| MBPO | imagination + DrQ-v2 | Meta-World policy | DreamerV3 Nature tables |
| VP2 planning | action-cond WM | success rate | Table 1 FVD |

## Knowledge map

| Question | Page |
|---|---|
| Method and tables | [`paper.md`](paper.md) |
| Files and Hub names | [`codebase.md`](codebase.md) |
| Execution state | [`reproduction.md`](reproduction.md) |
| Ten `IVIDEO-XFER` hypotheses | [`optimization-transfer.md`](optimization-transfer.md) |
| Identities | [`sources.yaml`](sources.yaml) |

These associations support retrieval. They do not define Agent selection or workflow.

## High-value evidence anchors

- **Table 1 BAIR.** Act-free FVD `75.0±0.20` versus MAGVIT `62.0` (MAGVIT wins FVD); PSNR `20.4` / SSIM `82.3` / LPIPS `9.5` beat MAGVIT. Act-cond FVD **60.8±0.08**. [IVG-PAPER, Table 1]
- **Table 1 RoboNet.** 64x64 act-cond FVD `63.2` versus FitVid **62.5** (FitVid wins FVD/PSNR/LPIPS). 256x256 PSNR **23.8** / SSIM **80.8** versus MaskViT 20.4 / 67.1. [IVG-PAPER, Table 1]
- **Tokenizer efficiency.** Independent `16x16` tokens OOM at the paper AR setting. Compressive generation 1.11 s versus 22.5 s on 4090. [IVG-PAPER, Tables 7-8]
- **VP2 mixed.** Push `0.7833`, open-slide **0.1611** (weaker than SVG′ `0.5733`). [IVG-PAPER, Table 6]
- **Scale.** Tokenizer 114M/310M, transformer 138M/436M; ~1.4M trajectories; OXE ~5 TB. [IVG-PAPER, Tables 2-4]
- **Cosmos3.** Compressive tokens and action/goal AR attach to **Generator FD/WAM**, not Reasoner. [`optimization-transfer.md`](optimization-transfer.md)
- No local inference. [`reproduction.md`](reproduction.md)

## Failure modes and non-goals

- MAGVIT wins BAIR action-free FVD (`62.0` vs `75.0`). FitVid wins RoboNet 64 FVD/PSNR/LPIPS.
- There is **no** public OXE action-conditioned pretrain. YAML title `ivideogpt-oxe-64-act-cond` is not Table 1 OXE pretrain.
- RLVR-World 2025 is a different repository and must not appear in iVideoGPT metric rows.
- 256x256 RoboNet Hub checkpoints were deleted; paper numbers remain.
- VP2 open-slide `0.1611` is a known weak cell.
- Meta-World MBRL lives in figures, not a single HTML success table.
- Attach tokens to **Generator FD/WAM**, not Reasoner.

## Evidence index

| Claim | Locator | Page |
|---|---|---|
| BAIR AF FVD 75.0±0.20; MAGVIT 62.0 | Table 1 | [`paper.md`](paper.md) |
| BAIR AC FVD 60.8±0.08 | Table 1 | paper |
| RoboNet 64 FVD 63.2 vs FitVid 62.5 | Table 1 | paper |
| RoboNet 256 PSNR 23.8 | Table 1 | paper |
| VP2 open-slide 0.1611 | Table 6 | paper |
| Compressive 1.11 s vs 16x16 22.5 s | Tables 7-8 | paper |
| Named OXE Hub cards | README | [`codebase.md`](codebase.md) |
| No OXE act-cond pretrain | README | codebase |
| Not RLVR-World | 2025 other repo | this README |
| Ten FD/WAM hypotheses | `IVIDEO-XFER-01..10` | [`optimization-transfer.md`](optimization-transfer.md) |
| Act-cond Hub card | named identity only | [IVG-HF-OXE-64-ACT-COND] |
| 256-context card | not RoboNet-256 Table 1 | [IVG-HF-OXE-256] |

`predict.py` on fractal npz is smoke. Table 1 needs I3D, best-of-100, and the named Hub file. RLVR-World remains a different 2025 project.

## Sources

Identities in [`sources.yaml`](sources.yaml).
