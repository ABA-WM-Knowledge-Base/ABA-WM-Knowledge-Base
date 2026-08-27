---
id: world-model-kb.papers.vista
title: Vista Paper Knowledge Entry
kind: paper
status: maintained
last_updated: 2026-08-14
owners:
  - AIBuildAI world-model group
---

# Vista Paper Knowledge Entry

## Retrieval metadata

**Relevant queries:** Vista, driving world model, OpenDV, nuScenes FID 6.9, FVD 89.4, trajectory command steer goal, learned reward, SVD, NeurIPS 2024, vista.safetensors, triangular CFG, not Wayve GAIA.

**Knowledge provided:** identity, operational model, table anchors, implementation boundary, reproduction state, and Generator-oriented transfers.

**Related pages:** [forward dynamics](../../foundations/problem-formulation/forward-dynamics.md); [video world models](../../foundations/representations/video-world-model.md); [diffusion and flow matching](../../foundations/learning-objectives/diffusion-and-flow-matching.md); [observation-space state](../../components/world-representation/observation-space-state.md); [observation-space dynamics](../../components/dynamics-modeling/observation-space-dynamics.md); [Cosmos3-Nano generator](../../models/cosmos3-nano/generator.md); [action modeling](../../models/cosmos3-nano/action-modeling.md).

Demo page: [vista-demo.github.io](https://vista-demo.github.io/). Numbers bind to the paper, not the demo. [VISTA-PAPER]

## Identity and revision boundary

| Field | Canonical value | Consequence |
|---|---|---|
| Work | *Vista: A Generalizable Driving World Model with High Fidelity and Versatile Controllability* | NeurIPS 2024 driving world model. |
| Paper | arXiv:2405.17398 | Tables 2-5 and Eqs. 2-9. [VISTA-PAPER] |
| Code | `OpenDriveLab/Vista@cc9821b4253ca7987c32757613d2fc2448fa9f5d` | `train.py`, `sample.py`, `reward.py`, phase YAMLs. [VISTA-CODE] |
| Weights | `OpenDriveLab/Vista` **latest** `vista.safetensors` | An earlier Hub upload had an EMA merge error. [VISTA-HF] |
| Init | Stability `svd_xt.safetensors` | Ancestry is SVD, not a from-scratch UNet. |
| Data | OpenDV-YouTube ~1735 h (15 h filtered) plus nuScenes | Phase 1 unlabeled; Phase 2 collaborative. [VISTA-OPENDV] |
| Not this model | Wayve GAIA | Different organization, architecture, and artifact. Do not cite GAIA numbers as Vista. |

## Operational model boundary

Vista is a **front-view action-conditioned video world model** initialized from SVD (~2.5B total, ~1.6B UNet). It predicts 25-frame 10 Hz clips at up to `576 x 1024`, optionally chained with latent replacement. It is not a closed-loop planner and not a robot policy. Reward is ensemble uncertainty over futures, not L2 to expert actions.

```text
history frames (+ optional c in {traj, cmd, steer/speed, goal})
        -> SVD latent EDM UNet
        -> future RGB clip
optional: M noisy samples -> variance -> R(c, a)
```

| Surface | Inputs | Output or decision | Evidence boundary |
|---|---|---|---|
| Action-free prediction | history frames | future video | Table 2 FID/FVD; not causality |
| Controlled simulation | + trajectory / command / steer / goal | future video | Table 3 IDM L2; Waymo is unseen |
| Reward | condition + candidate action | unnormalized scalar | Table 4 gap is only 0.014 |
| Long rollout | `--n_rounds` | ~2.3 s extra per round | qualitative; triangular CFG |
| Human 2AFC | 60 scenes, 33 raters | preference % | 2640 answers; not FVD |

Do not project Vista onto Cosmos3 Reasoner text, Policy-DROID joints, or Wayve GAIA.

## Knowledge map

| Question | Page |
|---|---|
| Method, equations, tables, limits | [`paper.md`](paper.md) |
| Files, flags, EMA gap | [`codebase.md`](codebase.md) |
| Execution state and acceptance | [`reproduction.md`](reproduction.md) |
| Ten `DRIVE-XFER` hypotheses | [`optimization-transfer.md`](optimization-transfer.md) |
| Identities | [`sources.yaml`](sources.yaml) |

These associations support retrieval. They do not define Agent selection, task order, or AIBuildAI workflow.

## High-value evidence anchors

- **Table 2.** nuScenes val FID **6.9** / FVD **89.4** on 5369 clips versus GenAD 15.4 / 184.0 and Drive-WM 15.8 / 122.7. Baselines were **not rerun**. Distributional, not action-causal. [VISTA-PAPER, Table 2]
- **Human 2AFC.** 2640 answers, 33 people, 60 scenes from OpenDV-val, nuScenes, Waymo, and CODA. Vista preferred on visual quality and motion rationality versus web video generators given one condition frame. [VISTA-PAPER, Sec. 4.1]
- **Table 3 control.** nuScenes 3-prior trajectory difference `0.835` (trajectory) and `0.832` (angle/speed) versus `1.820` action-free. Waymo trajectory with 3 priors `1.140` versus GT-video floor `0.893`. More priors help. [VISTA-PAPER, Table 3]
- **Table 4 reward.** Waymo GT command `0.892` versus random `0.878`. Small numeric gap; Fig. 11 (1500 jittered cases) is the stronger qualitative trend. [VISTA-PAPER, Table 4]
- **Table 5 action independence.** With trajectory, stop-command subset FVD `132.3 -> 118.9`. [VISTA-PAPER, Table 5]
- **Train recipe.** Phase 1: 128 A100, 20K, 576x1024, OpenDV. Phase 2: LoRA r=16, 8 A100, 120K at 320x576 then 10K at 576x1024. [VISTA-PAPER, Appendix C.3; VISTA-CODE, `docs/TRAINING.md`]
- **Hub.** Use the **latest** `vista.safetensors`. No local sample or train run. [`reproduction.md`](reproduction.md)
- **Cosmos3.** Video/control mechanisms attach to **Generator FD/WAM** (AV specialists). Not Reasoner. [`optimization-transfer.md`](optimization-transfer.md)

## Failure modes and non-goals

- Vista is not Wayve GAIA. Do not cite GAIA code, weights, or numbers here.
- FID 6.9 / FVD 89.4 are distributional versus **reported** driving WMs, not rerun, not collision rates.
- Table 4 reward gap is **0.014**. Do not call it a calibrated safety filter.
- Front-view only. Surround-view consistency is a transfer hypothesis (`DRIVE-XFER-05`), not a Vista result.
- Earlier Hub `vista.safetensors` had an EMA merge error; only the latest file is in scope.
- `configs/example/nusc_train.yaml` is debug, not Phase 1 (128 A100, 20K).
- Do not attach driving LoRA to Policy-DROID joints.

## Evidence index

| Claim | Locator | Page |
|---|---|---|
| FID 6.9 / FVD 89.4 | Table 2, 5369 clips | [`paper.md`](paper.md) |
| Human 2AFC 2640 / 33 / 60 | Sec. 4.1 | paper |
| nuScenes 3-prior traj 0.835 vs AF 1.820 | Table 3 | paper |
| Waymo traj 1.140 vs GT 0.893 | Table 3 | paper |
| Reward 0.892 vs 0.878 | Table 4 | paper |
| Stop FVD 132.3 -> 118.9 | Table 5 | paper |
| Phase 1 128 A100 20K | Appendix C; TRAINING.md | paper / codebase |
| `sample.py --action` | SAMPLING.md | [`codebase.md`](codebase.md) |
| Latest `vista.safetensors` | Hub EMA fix | reproduction |
| Not GAIA | identity | this README |
| Ten AV FD hypotheses | `DRIVE-XFER-01..10` | [`optimization-transfer.md`](optimization-transfer.md) |
| EMA-merge fix | latest Hub file only | [`reproduction.md`](reproduction.md) |
| Phase YAML | `vista_phase*.yaml` not `nusc_train.yaml` | [`codebase.md`](codebase.md) |

Vista is a **controllable driving video world model**, not Wayve GAIA and not a robot policy. Reward GT-versus-random 0.014 stays labeled as a small gap.

## Sources

Identities in [`sources.yaml`](sources.yaml).
