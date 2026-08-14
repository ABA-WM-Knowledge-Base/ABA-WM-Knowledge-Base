---
id: world-model-kb.papers.lapa
title: LAPA Paper Knowledge Entry
kind: paper
status: maintained
last_updated: 2026-08-14
owners:
  - AIBuildAI world-model group
---

# LAPA Paper Knowledge Entry

## Retrieval metadata

**Relevant queries:** LAPA, latent action pretraining, LAQ, Language Table, Open-X 50.1, ICLR 2025, LAPA7B-openx, WAM ID head, not Genie.

**Knowledge provided:** identity, three-stage operational model, table anchors, Hub naming, reproduction state, WAM/ID transfers.

**Related pages:** [inverse dynamics](../../foundations/problem-formulation/inverse-dynamics.md); [latent world models](../../foundations/representations/latent-world-model.md); [Cosmos3-Nano action modeling](../../models/cosmos3-nano/action-modeling.md).

Project page: [latentactionpretraining.github.io](https://latentactionpretraining.github.io/). [LAPA-PROJECT]

## Identity and revision boundary

| Field | Canonical value | Consequence |
|---|---|---|
| Work | *LAPA: Latent Action Pretraining from Videos* | ICLR 2025 / arXiv:2410.11758. [LAPA-PAPER] |
| Code | `LatentActionPretraining/LAPA@46aca51d7faebcec02d7d323bbb3820c2df07bc6` | Three-stage scripts plus vendored SimplerEnv. [LAPA-CODE] |
| Weights | [LAPA-HF] cited as `LAPA7B-openx` | Download `tokenizer.model`, `vqgan`, `params`; LAQ `laq_openx.pt`. Never write the hyphenated Hub slug in running text. |
| Backbone lineage | [LAPA-LWM] LWM-Chat-1M-Jax | Required for latent pretrain; not interchangeable raw LAPA weights. |
| Not this work | Genie interactive environments | Different paper class. |

CoRL 2024 LangRob Best Paper is a workshop award, not a substitute for ICLR tables.

## Operational model boundary

LAPA predicts **latent actions** from video plus language, then maps them to joints in Stage 3. Pretrained Hub inference is not a robot policy. Cosmos3 attachment is **WAM/ID**, not Reasoner text and not Policy-DROID continuous serving without a discrete-to-continuous adapter.

```text
Stage 1 LAQ: (o_t, o_{t+H}) -> quantized a~     (inference README: space 8^4)
Stage 2 latent VLA: (o_t, instruction) -> a~
Stage 3: a~ -> real end-effector / gripper via finetune
optional decoder WM: (o_t, a~) -> imagined o_{t+1}   (Fig. 7 qualitative)
```

| Surface | Inputs | Output | Invalid projection |
|---|---|---|---|
| LAQ | frame pair | discrete code | executable joints |
| Latent VLA | image + instruction | latent code | Policy-DROID 9D |
| Stage 3 deploy | latent + csv scales | robot action | unlabeled Hub demo |
| Decoder WM | image + latent | imagined frame | Table 2 success |
| SIMPLER | WidowX tasks, 100 finetune traj | success | Language Table numbers |

## Knowledge map

| Question | Page |
|---|---|
| Method and tables | [`paper.md`](paper.md) |
| Files and stages | [`codebase.md`](codebase.md) |
| Execution state | [`reproduction.md`](reproduction.md) |
| Ten `LA-XFER` hypotheses | [`optimization-transfer.md`](optimization-transfer.md) |
| Identities | [`sources.yaml`](sources.yaml) |

These associations support retrieval. They do not define Agent selection or workflow.

## Operational surfaces (do not merge)

| Surface | What it measures | Not evidence of |
|---|---|---|
| Language Table Table 1 | sim success ± SE | Franka Table 2 |
| Real-world Table 2 n=54 | partial success + paired wins | SIMPLER WidowX |
| Hub `inference` | `8^4` latents | executable joints |
| `deploy.py` | Stage 3 joints | unlabeled Open-X policy |
| Fig. 7 decoder | qualitative rollouts | Table 2 AVG 50.1 |

## High-value evidence anchors

- **Language Table (Table 1).** In-domain LAPA **62.0±8.7** versus Scratch **15.6±9.2** after 181k unlabeled + 1k labeled (0.5%). ActionVLA still leads several cells (**77.0±3.5** in-domain). Cross-env LAPA 33.6 versus Scratch 15.6. [LAPA-PAPER, Table 1]
- **Real-world (Table 2).** Open-X LAPA AVG **50.1** versus OpenVLA **43.9**. Unseen combo **57.8**. Paired win rate **65.4%** excluding ties (31.5 / 16.7 / 51.9 tie). n=54 rollouts per model. [LAPA-PAPER, Table 2, Fig. 11]
- **Human video.** SSv2 AVG **34.0** versus Scratch 21.2; still beats OpenVLA-Bridge 30.8 on average. [LAPA-PAPER, Table 2, Fig. 4]
- **Efficiency.** Authors report >30x pretrain efficiency versus conventional VLA; 8xH100 ~34 h; ~70K steps at batch 256 is "enough" for decent finetune. [LAPA-PAPER; LAPA-CODE README]
- **Hub.** [LAPA-HF] / `LAPA7B-openx` emits **latents**, not joints, until Stage 3. No local run. [`reproduction.md`](reproduction.md)
- **Cosmos3.** LAQ and latent VLA attach to **Generator WAM/ID**, not Reasoner. [`optimization-transfer.md`](optimization-transfer.md)

## Failure modes and non-goals

- Cite Hub weights as [LAPA-HF] / `LAPA7B-openx`. Do not paste the hyphenated Hub slug into running text.
- Pretrained inference emits latents (`8^4`), not Franka joints.
- ActionVLA still leads several Language Table cells (Table 1).
- Real-world n=54; 51.9% ties versus OpenVLA in the paired protocol.
- Decoder WM (Fig. 7) is qualitative, not Table 2.
- This work is not Genie.
- SIMPLER WidowX is a different embodiment than Franka Table 2.

## Evidence index

| Claim | Locator | Page |
|---|---|---|
| Language Table in-domain 62.0±8.7 vs Scratch 15.6 | Table 1 | [`paper.md`](paper.md) |
| ActionVLA still leads several cells | Table 1 | paper |
| Real-world Open-X AVG 50.1 vs OpenVLA 43.9 | Table 2 | paper |
| Win rate 65.4% excluding ties | Fig. 11 | paper |
| Human SSv2 AVG 34.0 | Table 2 | paper |
| Alphabet `8^4`; latents not joints | README | [`codebase.md`](codebase.md) |
| Cite [LAPA-HF] / `LAPA7B-openx` | Hub | this README |
| Ten WAM/ID hypotheses | `LA-XFER-01..10` | [`optimization-transfer.md`](optimization-transfer.md) |
| Not Genie | identity | this README |

## Sources

Identities in [`sources.yaml`](sources.yaml).
