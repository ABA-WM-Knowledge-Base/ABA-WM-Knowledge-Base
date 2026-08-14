---
id: world-model-kb.papers.dreamerv3
title: DreamerV3 Paper Knowledge Entry
kind: paper
status: maintained
last_updated: 2026-08-14
owners:
  - AIBuildAI world-model group
---

# DreamerV3 Paper Knowledge Entry

## Retrieval metadata

**Relevant queries:** DreamerV3, Nature 2025, Mastering diverse control tasks, RSSM, Minecraft diamonds, symlog, danijar reimplementation, arXiv 2301.04104 old title.

**Knowledge provided:** Nature-canonical identity, robustness mechanisms, eight-domain protocol, public-code boundary, reproduction state, FD/WAM transfers.

**Related pages:** [model-based RL](../../foundations/decision-making/model-based-rl.md); [latent world models](../../foundations/representations/latent-world-model.md); [Cosmos3-Nano action modeling](../../models/cosmos3-nano/action-modeling.md); [Cosmos3-Nano generator](../../models/cosmos3-nano/generator.md).

Foundation: [MBRL-DREAMERV3-2025]. Website: [danijar.com/dreamerv3](https://danijar.com/dreamerv3). Do not duplicate the Foundation ID in [`sources.yaml`](sources.yaml).

## Identity and revision boundary

| Field | Canonical value | Consequence |
|---|---|---|
| Work | *Mastering diverse control tasks through world models* | Nature 640:647-653 (2025). [DV3SRC-PAPER-NATURE] |
| DOI | 10.1038/s41586-025-08744-2 | Peer-reviewed evidence surface. |
| Preprint | arXiv:2301.04104, former title *Mastering Diverse Domains through World Models* | Old title; ar5iv HTML conversion **failed**; **not** the canonical result surface. [DV3SRC-PAPER-ARXIV] |
| Public code | `danijar/dreamerv3@e3f02248693a79dc8b0ebd62c93683888ddaccfe` | Reimplementation from open DreamerV2 code; README: **unrelated to Google or DeepMind**. [DV3SRC-CODE-CURRENT] |

Nature prose claims (Minecraft diamonds, eight-domain protocol, robustness list) are canonical. Public `dreamerv3/configs.yaml` keys are an **implementation analog**, not a Nature table. Extended Data Table 1 numeric cells were **not recovered** from Nature/PMC HTML (placeholder "Open in a new tab"). Do not invent those aggregates.

## Operational model boundary

DreamerV3 is a **latent MBRL agent**: encode observations into categorical RSSM states, predict future states/rewards/continue flags, train actor-critic from imagined latents. It outputs actions for control. It is not a pixel-diffusion showcase WM (that class includes DIAMOND) and not Cosmos3 Generator FID.

```text
replay (x, a, r, c)
  -> RSSM q(z|h,x), p(zhat|h), decode, reward, continue
  -> imagine imag_length steps
  -> actor-critic on imagined latents
  -> act in real env
```

| Surface | Inputs | Output | Invalid projection |
|---|---|---|---|
| World model | x, a | z, r, continue, decode | Cosmos3 Generator FID / Vista FVD |
| Actor-critic | imagined z | policy | DIAMOND Atari 100k HNS 1.459 |
| Minecraft | MineRL actions, sparse item rewards | diamonds in **all** seeds at 100M | VPT contractor data / Voyager MineFlayer |
| Public train | `python dreamerv3/main.py` | reimplementation returns | Nature internal binary replica |
| Atari100k public config | `sticky: False`, 64x64, 1.1e5 steps | public analog | Nature Atari100k table cells (unextracted) |

## Knowledge map

| Question | Page |
|---|---|
| Method and Nature claims | [`paper.md`](paper.md) |
| Public files and config keys | [`codebase.md`](codebase.md) |
| Execution state | [`reproduction.md`](reproduction.md) |
| Ten `DREAMERV3-XFER` hypotheses | [`optimization-transfer.md`](optimization-transfer.md) |
| Identities | [`sources.yaml`](sources.yaml) |

These associations support retrieval. They do not define Agent selection or workflow.

## High-value evidence anchors

- **Fixed hyperparameters** across 8 domains / 150+ tasks; 1 A100; default 200M size; replay ratio chosen to fit each budget. [DV3SRC-PAPER-NATURE, Benchmarks]
- **Minecraft Diamond.** First reported diamonds from scratch without human data or curricula; **all** seeds collect diamonds at 100M steps. Episodes up to 36,000; faster block break; VPT comparison is 720 GPUs / 9 days versus 1 GPU / 9 days in the Nature paragraph. [DV3SRC-PAPER-NATURE, Minecraft]
- **Robustness stack.** Observation symlog; KL free bits 1 nat; 1% unimix; percentile return normalization; symexp two-hot reward/critic; block GRU; AGC; LaProp. Public keys: `free_nats: 1.0`, `unimix: 0.01`, `imag_length: 15`. [DV3SRC-PAPER-NATURE; DV3SRC-CODE-CURRENT, `dreamerv3/configs.yaml`]
- **Extended Data Table 1 numeric cells not extracted.** Do not fabricate mean/IQM aggregates.
- **Public README disclaimer:** not Google/DeepMind internal. Citation in the public README already uses the Nature title. No local run. [`reproduction.md`](reproduction.md)
- **Cosmos3.** RSSM robustness (symlog, free bits, unimix, two-hot) attaches to **latent WAM/ID or compact planner** surfaces; pixel decode is not the primary Generator video recipe. [`optimization-transfer.md`](optimization-transfer.md)

## Failure modes and non-goals

- Canonical title is *Mastering diverse control tasks through world models* (Nature 2025). The arXiv 2301.04104 title *Mastering Diverse Domains through World Models* is preprint-only.
- `danijar/dreamerv3` is a reimplementation, unrelated to Google or DeepMind.
- Extended Data Table 1 numeric cells were not recovered from HTML. Do not invent aggregates.
- Do not mix DIAMOND Atari 100k HNS 1.459 into this entry.
- Minecraft uses abstract crafting and accelerated breaking; not keyboard-mouse VPT; not Voyager MineFlayer.
- `debug` config is not a paper run.

## Evidence index

| Claim | Locator | Page |
|---|---|---|
| Nature title / DOI | 640:647-653; 10.1038/s41586-025-08744-2 | [`paper.md`](paper.md) |
| Preprint old title | arXiv:2301.04104 | paper |
| 8 domains / 150+ tasks / 1 A100 | Benchmarks | paper |
| Minecraft all seeds diamonds @ 100M | Minecraft section | paper |
| Extended Data Table 1 cells | **not recovered** | paper / reproduction |
| Public reimplementation | README disclaimer | [`codebase.md`](codebase.md) |
| `free_nats 1.0`, `unimix 0.01` | `configs.yaml` | codebase |
| Ten latent-WAM hypotheses | `DREAMERV3-XFER-01..10` | [`optimization-transfer.md`](optimization-transfer.md) |
| Not DIAMOND HNS 1.459 | identity | this README |
| Public `configs.yaml` keys | `free_nats`, `unimix`, `imag_length` | [`codebase.md`](codebase.md) |
| Smoke vs Nature | crafter/dummy allowed; aggregates blocked | [`reproduction.md`](reproduction.md) |

Nature is the result surface. The public tree is the attachment surface. Mixing those identities is a documentation error, not a new scientific claim.

## Sources

Identities in [`sources.yaml`](sources.yaml).
