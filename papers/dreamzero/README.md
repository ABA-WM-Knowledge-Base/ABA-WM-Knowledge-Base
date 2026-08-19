---
id: world-model-kb.papers.dreamzero
title: DreamZero Paper Knowledge Entry
kind: paper
status: maintained
last_updated: 2026-08-19
owners:
  - AIBuildAI world-model group
---

# DreamZero Paper Knowledge Entry

## Retrieval metadata

**Relevant queries:** DreamZero, World Action Model, Wan2.1 14B, Flash, AgiBot 62.2, DROID 22.5 success, embodiment adapter, GEAR-Dreams, not universal policy.

**Knowledge provided:** identity, WAM operational model, table anchors, embodiment-specific checkpoints, reproduction state, Generator FD/WAM transfers.

**Related pages:** [world action models](../../foundations/definitions-and-taxonomy/world-action-model.md); [forward dynamics](../../foundations/problem-formulation/forward-dynamics.md); [action-conditioned video modeling](../../components/generative-modeling/action-conditioned-video.md); [reasoning–generation–action integration](../../components/reasoning/reasoning-generation-action.md); [Cosmos3-Nano generator](../../models/cosmos3-nano/generator.md); [action modeling](../../models/cosmos3-nano/action-modeling.md).

Foundation identity: [WAM-DREAMZERO-2026]. Do not duplicate that ID in [`sources.yaml`](sources.yaml). Project page: [dreamzero0.github.io](https://dreamzero0.github.io/). [DZ-PROJECT]

## Identity and revision boundary

| Field | Canonical value | Consequence |
|---|---|---|
| Work | *World Action Models are Zero-shot Policies* | Preprint arXiv:2602.15922. [DZ-PAPER] |
| Code | `dreamzero0/dreamzero@ab790c198fbce33503358efbbd4187ce9a89adf3` | Apache-2.0. Server `socket_test_optimized_AR.py`. [DZ-CODE] |
| DROID ckpt | `GEAR-Dreams/DreamZero-DROID` | Franka/DROID cameras and joints only. [DZ-HF-DROID] |
| AgiBot ckpt | `GEAR-Dreams/DreamZero-AgiBot` | Post-train starting point; **not** Franka. [DZ-HF-AGIBOT] |
| Backbone | Wan2.1-I2V-14B-480P | Frozen VAE, text encoder, image encoder. Ablations use 5B. |
| Policy type | Embodiment-specific WAM | **Not** a universal zero-shot policy. YAML adapters required. |

README `max_steps=10` is a sanity default, not the paper's 100K training. README latency (~0.6 s GB200 / ~3 s H100 with DiT cache) is a **different measurement surface** from Table 1 38x / 150 ms Flash. [DZ-CODE README; DZ-PAPER, Table 1]

## Operational model boundary

DreamZero jointly denoises future video and motor actions on a pretrained I2V DiT. Closed loop writes **real** observations into the AR KV cache after each executed chunk. Flash samples video times from `Beta(7,1)` while action times stay uniform, enabling 1-step control. Changing robots requires `*_relative.yaml` adapters and, in the YAM experiment, ~30 minutes of play data.

```text
views + language + proprio
  -> Wan DiT joint video/action denoising (AR chunks)
  -> execute action chunk
  -> replace generated visual tokens with GT frames in cache
```

| Surface | Inputs | Output | Invalid projection |
|---|---|---|---|
| DROID inference | 3 DROID views + language | action chunk + video | AgiBot joints / Cosmos3 Reasoner |
| AgiBot eval | AgiBot cameras + language | task progress | DROID Hub weights |
| Flash 1-step | same | faster actions | Table 1 38x without GB200/Flash flags |
| Video-only co-train | human/YAM video, no target actions | better unseen progress | action-free universal robot |
| YAM few-shot | 55 play trajectories | adapter LoRA | zero-shot any embodiment |

## Knowledge map

| Question | Page |
|---|---|
| Method and tables | [`paper.md`](paper.md) |
| Files and adapters | [`codebase.md`](codebase.md) |
| Execution state | [`reproduction.md`](reproduction.md) |
| Ten `DREAMZERO-XFER` hypotheses | [`optimization-transfer.md`](optimization-transfer.md) |
| Identities | [`sources.yaml`](sources.yaml) |

These associations support retrieval. They do not define Agent selection or workflow.

## High-value evidence anchors

- **AgiBot.** Seen **62.2%** average task progress versus best pretrained VLA **27.4%**. Unseen verbs **39.5%** versus **16.3%**; from-scratch VLAs near zero / `<1%`. [DZ-PAPER, Sec. 5 Q1-Q2, Fig. 8-9]
- **DROID-Franka.** Unseen **49%** progress / **22.5%** success versus GR00T N1.6 31% / 12.5% and π0.5 33% / 7.5%. [DZ-PAPER, Sec. 5 Q2]
- **Table 2.** 38.3%±7.6% -> **55.4%±9.5%** (20 min YAM video) / **54.3%±10.4%** (12 min human). No target actions. CIs overlap. [DZ-PAPER, Table 2]
- **Table 3.** 4-step 83%±6.1% at 350 ms; naive 1-step 52%±10.2%; Flash **74%±10.1%** at 150 ms. [DZ-PAPER, Table 3]
- **Table 1.** Cumulative 38x on GB200 including Flash (5.7 s -> 150 ms). Do not merge with README 0.6-3 s. [DZ-PAPER, Table 1]
- **Table 4.** Diverse 50%±6.3% versus repetitive 33%±4.2%; 14B versus 5B: 50% versus 21%. Prose: matched VLAs on diverse data reach **0%** progress. ar5iv VLA cells conflict; prose 0% is canonical until PDF re-read. [DZ-PAPER, Table 4]
- Keep embodiment adapters. No local train/infer. [`reproduction.md`](reproduction.md)
- **Cosmos3.** Joint video-action denoising attaches to **Generator FD/WAM**, not Reasoner, and not a universal Policy-DROID drop-in. [`optimization-transfer.md`](optimization-transfer.md)

## Failure modes and non-goals

- WAM is embodiment-specific. Do not load AgiBot weights on Franka.
- Task progress ≠ binary success except where both are reported (DROID 22.5% success).
- Table 2 CIs overlap; 10-20 min video-only is an early signal.
- Table 4 VLA HTML cells conflict with prose 0%; prose is canonical until PDF re-read.
- README `max_steps=10` is not 100K paper training.
- README ~0.6-3 s latency is not Table 1 150 ms / 38x.
- MolmoSpaces/RoboArena leaderboards are mutable, not Tables 1-4.

## Evidence index

| Claim | Locator | Page |
|---|---|---|
| AgiBot seen 62.2% vs VLA 27.4% | Sec. 5 Q1 | [`paper.md`](paper.md) |
| AgiBot unseen 39.5% vs 16.3% | Sec. 5 Q2 | paper |
| DROID 49% / 22.5% success | Sec. 5 Q2 | paper |
| Table 2 38.3 -> 55.4 / 54.3 | Table 2 | paper |
| Table 3 Flash 74% @ 150 ms | Table 3 | paper |
| Table 1 38x GB200 | Table 1 | paper |
| Diverse 50% vs repetitive 33% | Table 4 | paper |
| VLA diverse 0% (prose) | Table 4 conflict | paper |
| Adapters required | YAML + Hub split | [`codebase.md`](codebase.md) |
| Ten WAM hypotheses | `DREAMZERO-XFER-01..10` | [`optimization-transfer.md`](optimization-transfer.md) |
| DROID vs AgiBot Hub | not interchangeable | [`codebase.md`](codebase.md) |
| `max_steps=10` | sanity script | [`reproduction.md`](reproduction.md) |

DreamZero WAM is **not** a universal policy. Camera order and embodiment YAML are part of the identity. Table 4 VLA diverse progress follows paper prose (0%).

## Sources

Identities in [`sources.yaml`](sources.yaml). Cross-entry: [WAM-DREAMZERO-2026].
