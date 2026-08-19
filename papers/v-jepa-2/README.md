---
id: world-model-kb.papers.v-jepa-2
title: V-JEPA 2 Paper Knowledge Entry
kind: paper
status: maintained
last_updated: 2026-08-19
owners:
  - AIBuildAI world-model group
---

# V-JEPA 2 Paper Knowledge Entry

## Retrieval metadata

**Relevant queries:** V-JEPA 2, V-JEPA 2-AC, V-JEPA 2.1, VideoMix22M, ViT-g, SSv2 77.3, DROID <62 h, Franka pick-place, latent CEM, or Reasoner representation.

**Knowledge provided:** strict separation of action-free pretraining versus action-conditioned control versus 2.1, released code and checkpoint boundaries, reproduction state, and falsifiable transfers toward Cosmos3-Nano Reasoner representation and latent planning — not Generator pixels.

**Related pages:** [Representation learning and JEPA](../../foundations/representations/representation-learning-and-jepa.md); [latent world models](../../foundations/representations/latent-world-model.md); [planning and control](../../foundations/decision-making/planning-and-control.md); [Reasoning Component](../../components/reasoning/README.md); [Cosmos3-Nano reasoner](../../models/cosmos3-nano/reasoner.md); [forward dynamics](../../foundations/problem-formulation/forward-dynamics.md); [Cosmos3-Nano action modeling](../../models/cosmos3-nano/action-modeling.md) for FD/WAM contrast.

Foundation bibliographic identity: [OBJ-VJEPA2-2025] for *V-JEPA 2: Self-Supervised Video Models Enable Understanding, Prediction and Planning* (`arXiv:2506.09985`). This entry adds variant boundaries and code mapping without re-registering that Foundation ID. [VJ2-PAPER; VJ2-PROJECT]

## Identity and revision boundary

| Field | Canonical value | Consequence |
|---|---|---|
| Work | *V-JEPA 2: Self-Supervised Video Models Enable Understanding, Prediction and Planning* | Primary evidence for video JEPA plus a **separate** 2-AC stack. |
| Paper snapshot | `arXiv:2506.09985` | Tag every number with 2 vs 2-AC vs 2.1. [VJ2-PAPER] |
| Foundation identity | [OBJ-VJEPA2-2025] | Cross-entry citations; not in [`sources.yaml`](sources.yaml). |
| Official code | `facebookresearch/vjepa2@204698b45b3712590f06245fbfba32d3be539812` | Pin dated **2026-03-23**. [VJ2-CODE] |
| 2.1 in tree | `app/vjepa_2_1/` | Incremental recipe; **not** Table 2/3. |
| Project / blog | [VJ2-PROJECT] | Mutable presentation; numbers bind to the paper. |

## Variant boundary (mandatory)

| Variant | Training data | Action in model | Primary capability | Robot evidence |
|---|---|---|---|---|
| **V-JEPA 2** | **1M+ hours**, VideoMix22M, **action-free** | none | SSv2 **77.3**, EK100 **39.7**, PerceptionTest **84.0** (8B LLM align) | **none** |
| **V-JEPA 2-AC** | **<62 h** DROID, frozen ViT-g | yes, interleaved `(a,s,z)` | latent CEM on Franka + RobotiQ | Table 2 / Table 3 only |
| **V-JEPA 2.1** | repo later recipe | per card | incremental encoder | verify against 2.1 card, never assumed |

Action-free encoder quality does not imply robot planning. 2-AC adds an action-conditioned predictor and a notebook CEM loop. [OBJ-VJEPA2-2025; VJ2-PAPER, Tables 2-3]

## Operational model boundary

**V-JEPA 2** learns representations by predicting target block embeddings — no pixel decoder, no actions. **V-JEPA 2-AC** freezes ViT-g (**16×16×1408** at 256 px), trains teacher-forcing next-z on DROID, and plans in latent space. Neither is a pixel-generative world model. Transfers target **Reasoner / latent planning**, not Cosmos3 Generator FD/WAM. Table 3's Cosmos video WM is a published **baseline**. [VJ2-PAPER, Sec. 3-4, Table 3]

```text
V-JEPA 2:     context blocks -> Enc -> Pred -> latent targets
V-JEPA 2-AC:  (a_k, s_k, z_k) -> AC predictor -> next z; CEM in z
```

| Surface | Inputs | Output | Evidence boundary |
|---|---|---|---|
| Action-free pretrain | video clips, 3-D block masks | encoder + predictor | 252K @ 16f/256 then cooldown 64f/384; ~60 GPU-year full-res counterfactual |
| Frozen probes | SSv2 / EK100 / K400 yamls | classification / anticipation | not Franka |
| LLM-aligned PerceptionTest | encoder + 8B LLM | 84.0 | not a frozen-only number |
| 2-AC post-train | DROID RGB + 7-D action + state | next-z predictor | <62 h; encoder frozen |
| Latent CEM | image sub-goals, CEM samples | executed Franka action | 10 trials, two labs; sub-goals required for pick-place |
| Video WM baseline | Cosmos video planner | same robot cells | 4 min/action, H=1, 80 samples — external to this repo |

## Documented launchers (not executed)

Pretrain and DROID AC use `app/vjepa/train.py` and `app/vjepa_droid/train.py` with `configs/train/vitg16/pretrain-256px-16f.yaml`, `cooldown-384px-64f.yaml`, and `droid-256px-8f.yaml`. Frozen probes use `evals/video_classification_frozen/` and `evals/action_anticipation_frozen/` with `configs/eval/vitg-384/{ssv2,ek100,k400}.yaml`. Robot CEM is `notebooks/utils/mpc_utils.py` plus `world_model_wrapper.py`. V-JEPA 2.1 is `app/vjepa_2_1/train.py`. [`codebase.md`](codebase.md); [`reproduction.md`](reproduction.md)

## Knowledge map

| Question | Canonical page |
|---|---|
| Architecture, data, tables, ablations, limits? | [`paper.md`](paper.md) |
| Pinned commit, 2 vs 2-AC vs 2.1 files, tensor contracts? | [`codebase.md`](codebase.md) |
| Execution state and contracts? | [`reproduction.md`](reproduction.md) |
| Transfers to Cosmos3 Reasoner / latent planning? | [`optimization-transfer.md`](optimization-transfer.md) |
| Source IDs (VJ2- prefix)? | [`sources.yaml`](sources.yaml) |

## High-value evidence anchors

- **Scale:** 1M+ hours, VideoMix22M, ViT-L ~300M to ViT-g ~1B, predictor ~ViT-small. Scaling vs ViT-L/16: data +1.0, model +1.5, 90K→252K +0.8, 256→384 and 16→64 frames to **88.2%** (**+4.0** cumulative). [VJ2-PAPER, Sec. 3-4]
- **Progressive compute:** 252K at 16f/256 then cooldown 64f/384; up to **8x** vs full-res; 64×384×384 would be ~**60 GPU-years**. [VJ2-PAPER, Sec. 3]
- **Understanding:** SSv2 **77.3** top-1; EK100 **39.7** recall-at-5; PerceptionTest **84.0** after **8B** LLM align. [VJ2-PAPER, Sec. 4]
- **2-AC Table 2 averages (10 trials, two labs):** Reach 100%; Grasp cup **65%** box **25%**; Reach-with-object cup **75%** box **75%**; Pick-place cup **80%** box **65%**. [VJ2-PAPER, Table 2]
- **Table 3 Lab2 4090:** Cosmos video WM 80 samples / 10 iter / H=1 / **4 min/action** → Reach 80%, grasp 0%/20%, P&P 0%/0%. V-JEPA 2-AC **800** samples / **16 s/action** → Reach 100%, grasp 60%/20%, P&P 80%/50%. [VJ2-PAPER, Table 3]
- **Limits:** camera-pose sensitivity (implicit action axis from monocular RGB); long-horizon accumulation; image sub-goals required for pick-place. [VJ2-PAPER, Sec. 5]
- **Code:** AC interleave in `src/models/ac_predictor.py`; CEM in `notebooks/utils/mpc_utils.py`; 2.1 in `app/vjepa_2_1/`. [`codebase.md`](codebase.md)
- **Execution:** all training and inference **not attempted**. [`reproduction.md`](reproduction.md)

## Limits that change retrieval

- Table 2 averages hide Lab 1 vs Lab 2: box pick-place is **80% vs 50%**. Camera pose is a first-class failure mode. [VJ2-PAPER, Table 2]
- Pick-place uses **three** image sub-goals (4 / 10 / 4 steps), not a language goal. [VJ2-PAPER, Sec. 4.2]
- PerceptionTest **84.0** requires 8B-class LLM alignment; frozen SSv2 **77.3** is a different stack. [VJ2-PAPER, Tables 4-6]
- Table 3 Cosmos video WM is **external** to `facebookresearch/vjepa2`. Notebook CEM is not a Table 2 rerun. [`codebase.md`](codebase.md)
- An **88.2%** scaling number must name the ViT-L/16 baseline and probe; Table 4’s six-task average is **85.1**. [VJ2-PAPER, Table 4, Fig. 5]
- 10 trials per cell: do not treat grasp-box **25%** as a precise rate.
- Transfers attach to **Cosmos3-Nano Reasoner**, not Generator FD/WAM. Table 3 is a baseline. [`optimization-transfer.md`](optimization-transfer.md)

## Sources

[`sources.yaml`](sources.yaml) owns VJ2-* IDs. Foundation: [OBJ-VJEPA2-2025].
