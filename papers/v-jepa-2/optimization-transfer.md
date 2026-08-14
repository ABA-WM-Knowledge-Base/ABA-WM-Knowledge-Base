---
id: world-model-kb.papers.v-jepa-2.optimization-transfer
title: V-JEPA 2 Transferable Optimization Knowledge
kind: guide
status: maintained
last_updated: 2026-08-14
owners:
  - AIBuildAI world-model group
---

# V-JEPA 2 Transferable Optimization Knowledge

## Retrieval metadata

**Relevant queries:** transfer V-JEPA 2, JEPA to Cosmos3 Reasoner, latent CEM, action-conditioned predictor, VideoMix22M, progressive cooldown, camera-pose sensitivity, or avoid pixel Generator transfer.

**Knowledge provided:** falsifiable intervention patterns derived from V-JEPA 2 / 2-AC, their Reasoner attachment points, required controls, expected evidence, compute and regression risks, and invalid generalizations.

**Related pages:** [`paper.md`](paper.md) owns V-JEPA evidence; [`codebase.md`](codebase.md) owns implementation details; [representation learning and JEPA](../../foundations/representations/representation-learning-and-jepa.md) owns the generic objective; [planning and control](../../foundations/decision-making/planning-and-control.md) owns search; [Cosmos3-Nano reasoner](../../models/cosmos3-nano/reasoner.md) owns the target; [Cosmos3-Nano action modeling](../../models/cosmos3-nano/action-modeling.md) owns FD/WAM contrast (not the V-JEPA attachment).

## 1. Transfer discipline

Separate evidence lanes and never mix numbers:

1. **V-JEPA 2:** action-free semantics at 1M+ hours / VideoMix22M (SSv2 77.3, EK100 39.7, PerceptionTest 84.0 after 8B LLM align).
2. **V-JEPA 2-AC:** frozen ViT-g, <62 h DROID, Tables 2-3 Franka success and latency.
3. **V-JEPA 2.1:** repository recipe only until a 2.1 card repeats a table.

Attach to **Cosmos3-Nano Reasoner** representation and latent planning. Do **not** attach to Generator pixels. A Generator FD/WAM video planner is a valid **baseline** (as in paper Table 3), not a V-JEPA mechanism transfer.

Every item below is a **hypothesis** until a controlled target-model experiment separates it from data, compute, encoder freeze, CEM budget, and goal specification.

## 2. Intervention matrix

| ID | Target failure | Mechanism transferred | Attachment surface | Primary evidence | Principal risk |
|---|---|---|---|---|---|
| `VJEPA-XFER-01` | Reasoner visual tokens lack physical structure | action-free JEPA block prediction | Reasoner ViT, no pixel decode | SSv2 77.3; scaling +4.0 | probe gains without robot transfer |
| `VJEPA-XFER-02` | video MPC too slow for control | frozen encoder + small AC predictor | Reasoner tokens + latent CEM | Table 3: 16 s vs 4 min | contact tasks need pixels |
| `VJEPA-XFER-03` | actions poorly aligned to visual tokens | interleave `(a_k, s_k, z_k)` | AC predictor input layout | `ac_predictor.py` forward | wrong action contract |
| `VJEPA-XFER-04` | closed-loop drift after teacher-forcing | rollout / prefix training vs next-z | AC training loop | paper limit: error accumulation | one-step regression |
| `VJEPA-XFER-05` | full-res video pretrain is unaffordable | 16f/256 then 64f/384 cooldown | Reasoner pretrain schedule | 8x vs full-res; 60 GPU-year counterfactual | cooldown mismatch at AC |
| `VJEPA-XFER-06` | under-scaled encoder | data/model/steps/resolution levers | Reasoner backbone | +1.0/+1.5/+0.8/+4.0 | diminishing 317M-style tails |
| `VJEPA-XFER-07` | language goals for pick-place | image sub-goal encoding | planner scorer | paper: sub-goals required | eval leakage via easy goals |
| `VJEPA-XFER-08` | camera move breaks latent MPC | extrinsics / pose robustness | AC `use_extrinsics` | paper camera-pose limit | overfit lab cameras |
| `VJEPA-XFER-09` | 2.1 weights silently replace 2 | explicit variant lock | checkpoint registry | 2.1 is a separate tree | Table 2 contamination |
| `VJEPA-XFER-10` | DROID-scale data ignored | <62 h AC on a frozen 1B encoder | freeze early Reasoner | Table 2; 65%/80% pick-place | scratch matches pretrain |

## 3. `VJEPA-XFER-01`: action-free JEPA for Reasoner tokens

**Source mechanism.** V-JEPA 2 predicts masked target embeddings from context with a ViT-g encoder and a small predictor, trained on 1M+ hours / VideoMix22M. SSv2 top-1 is **77.3**; EK100 recall-at-5 is **39.7**. [VJ2-PAPER, Sec. 3-4]

**Target behavior.** Improve Reasoner physical/temporal probes without Generator reconstruction.

**Attachment.** Replace or distill the Reasoner visual tower with a JEPA block-prediction objective on Cosmos video shards. Do not add this loss to Generator FD/WAM.

**Minimum controlled experiment.** Frozen probes (classification, anticipation) vs the current Reasoner pretrain at matched iterations. Then a small downstream policy or AC finetune with a **fixed** budget.

**Expected movement.** Higher frozen probes; downstream robot metrics move only if the AC-style head is also present.

**Falsification.** Reject if probe gains do not transfer to any downstream control metric within the fixed finetune budget, or if a pixel-reconstruction pretrain matches probes at equal compute.

## 4. `VJEPA-XFER-02`: latent CEM instead of video MPC

**Source mechanism.** Table 3, Lab 2, RTX 4090: Cosmos video WM with 80 samples, 10 iterations, **H=1** takes **4 min/action** (Reach 80%, grasp 0%/20%, pick-place 0%/0%). V-JEPA 2-AC with **800** samples takes **16 s/action** (Reach 100%, grasp 60%/20%, pick-place 80%/50%). [VJ2-PAPER, Table 3]

**Hypothesis.** For this embodiment, latent search is the Pareto improvement: more samples *and* lower latency. Video WM H=1 is a latency constraint, not an architectural preference.

**Attachment.** Reasoner latent planner. Generator FD/WAM video MPC is the timed baseline only.

**Experiment.** Same Franka/sim task, same action contract. Cross planner type × sample count × wall-clock cap. Report success, ms/action, and grasp-box (the shared weak cell).

**Expected movement.** Latent CEM matches or beats video MPC under a 20 s/action cap.

**Falsification.** Reject if Generator FD/WAM Pareto-dominates success at equal latency, or if latent success fails an action-shuffle probe.

## 5. `VJEPA-XFER-03`: interleaved action-state-latent tokens

**Source mechanism.** AC predictor interleaves `(a_k, s_k, z_k)` (optional extrinsics) and uses causal action-block attention. Feature maps are **16×16×1408** for frozen ViT-g at 256 px. [VJ2-PAPER, Sec. 4; VJ2-CODE, `src/models/ac_predictor.py`]

**Hypothesis.** Frame-aligned action tokens preserve identity better than a pooled trajectory vector added once.

**Attachment.** On Reasoner tokens whose time index matches predicted `z_{k+1}`, prepend learned action and proprio tokens. Keep encoder frozen in the first run.

**Experiment.** Cross `{pooled action, per-frame concat, interleaved (a,s,z)}` with a shuffled-action control. Match predictor parameter count.

**Expected movement.** Lower next-z error and larger true-vs-shuffled action separation.

**Falsification.** Reject if shuffled alignment matches true alignment, or if gains disappear under parameter matching.

## 6. `VJEPA-XFER-04`: train for closed-loop prefixes

**Source mechanism.** Training is teacher-forcing next-z. The paper lists **long-horizon error accumulation** as a limit. [VJ2-PAPER, Sec. 5]

**Hypothesis.** Feeding detached predicted z back as context during AC training should reduce CEM horizon error without changing the frozen encoder.

**Attachment.** `app/vjepa_droid/train.py`-style loop on Reasoner tokens: curriculum from 1-step TF to K-step rollout.

**Experiment.** TF-only vs mixed rollout at matched AC steps. Report one-step z error, H-step z error, and pick-place with image goals.

**Expected movement.** Better H-step error and pick-place; possible one-step regression.

**Falsification.** Reject if long-horizon metrics do not improve beyond noise augmentation, or if one-step collapse erases downstream benefit.

## 7. `VJEPA-XFER-05`: progressive resolution cooldown

**Source mechanism.** 252K iterations at 16 frames / 256 px, then cooldown at 64 frames / 384 px; up to **8x** cheaper than full-res. Full 64×384×384 is ~**60 GPU-years**. [VJ2-PAPER, Sec. 3]

**Hypothesis.** Reasoner video pretrain should copy the two-stage schedule rather than native high-res from step 0.

**Attachment.** Reasoner visual tower configs analogous to `pretrain-256px-16f.yaml` then `cooldown-384px-64f.yaml`.

**Experiment.** Matched total GPU-hours: (i) 256/16 only, (ii) progressive cooldown, (iii) native 384/64. Report probes and a small AC transfer.

**Expected movement.** Cooldown matches or beats native high-res at far less compute.

**Falsification.** Reject if native high-res dominates at equal GPU-hours, or if cooldown encoder tokens are incompatible with the 256-px AC head and no adapter is provided (`VJEPA-GAP-04`).

## 8. `VJEPA-XFER-06`: scale along four measured levers

**Source mechanism.** 2M→22M videos **+1.0**; ViT-L→g **+1.5**; 90K→252K **+0.8**; 256→384 and 16→64 frames to **88.2%** (**+4.0** vs ViT-L/16). [VJ2-PAPER, scaling]

**Hypothesis.** Reasoner gains should be attributed per lever. Jumping to 1B weights without data/step/resolution is not “V-JEPA scaling.”

**Attachment.** Reasoner backbone sweep with one lever varied at a time.

**Experiment.** 2×2×2 on data subset, width, and iterations, plus one cooldown arm. Report the same probe as the paper's 88.2% task analog.

**Expected movement.** Monotone gains in the same order of magnitude as the paper's deltas.

**Falsification.** Reject if only parameter count moves the probe while data and iterations do not, or if 88.2% is quoted without the baseline.

## 9. `VJEPA-XFER-07`: image sub-goals for pick-place

**Source mechanism.** Pick-place in Tables 2-3 uses **image sub-goals**. The paper lists this as a limit, not a solved language-planning result. Table 2 pick-place is **80% / 65%** (cup/box). [VJ2-PAPER, Table 2, Sec. 5]

**Hypothesis.** Latent CEM needs a goal embedding in the same encoder space as `z`. Language goals require an extra Reasoner text map that Table 2 does not provide.

**Attachment.** Encode a goal image with the frozen Reasoner/ViT encoder; score terminal predicted z by cosine or L2. Keep language-only as a separate arm.

**Experiment.** Goal modes: image sub-goal, language only, proprio target. Same CEM budget.

**Expected movement.** Image goals retain pick-place; language-only drops unless extra alignment data are added.

**Falsification.** Reject if language-only matches image goals with no extra data (task too easy or leakage), or if image goals succeed while action-shuffle also succeeds (scorer ignores dynamics).

## 10. `VJEPA-XFER-08`: camera-pose / implicit action-axis robustness

**Source mechanism.** Monocular RGB makes the action axis implicit in camera extrinsics. The paper flags **camera pose sensitivity**. Code optionally adds an extrinsics token (`use_extrinsics`). [VJ2-PAPER, Sec. 5; VJ2-CODE, `ac_predictor.py`]

**Hypothesis.** Without an explicit camera/action-frame adapter, latent MPC overfits lab cameras. Two-lab Table 2 is not a random camera sample.

**Attachment.** Reasoner AC head: domain camera ID, extrinsics token, or action-frame adapter. Do not hide the issue in Generator pixel augmentation.

**Experiment.** Train on Lab 1 cameras, eval on Lab 2 or a perturbed extrinsics sweep. Cross extrinsics token on/off.

**Expected movement.** Extrinsics or adapters reduce the cross-camera drop, especially on grasp/pick-place.

**Falsification.** Reject if pose perturbation is a no-op (task not actually camera-sensitive here) or if adapters help Lab 1 while hurting Lab 2 without a coverage story.

## 11. `VJEPA-XFER-09`: lock 2 vs 2-AC vs 2.1

**Source mechanism.** 2.1 lives in `app/vjepa_2_1/`. Paper Tables 2-3 are 2-AC with a frozen V-JEPA 2 ViT-g. [VJ2-CODE; VJ2-PAPER, Tables 2-3]

**Hypothesis.** Dropping 2.1 weights into a 2-AC predictor without a new eval is a silent protocol change.

**Attachment.** Checkpoint registry: encoder SHA, recipe name, AC head SHA. Reasoner experiments must log the triple.

**Experiment.** A/B: paper 2 encoder + AC vs 2.1 encoder + same AC recipe on the same DROID hours and CEM.

**Expected movement.** 2.1 may help probes; robot success is an empirical question.

**Falsification.** Reject “2.1 is a free upgrade” if robot success drops, and reject quoting Table 2 for a 2.1 run.

## 12. `VJEPA-XFER-10`: small robot data on a frozen 1B encoder

**Source mechanism.** DROID **<62 h**, frozen ViT-g, Table 2 grasp 65%/25% and pick-place 80%/65% with 10 trials. [VJ2-PAPER, Table 2]

**Hypothesis.** Most of the sample efficiency comes from freezing the action-free encoder. Full finetune of 1B on 62 h should overfit.

**Attachment.** Freeze Reasoner visual blocks; train only the AC predictor (and optionally last encoder blocks as a second arm).

**Experiment.** Scratch AC (random encoder) vs frozen pretrained vs full finetune, same 62 h analog. Report learning curves and grasp-box (the hard object).

**Expected movement.** Frozen pretrained dominates scratch at this data scale; full finetune may hurt grasp-box.

**Falsification.** Reject if scratch matches pretrained at 62 h (pretrain unused), or if unfreezing always wins without a held-out object split.

## 13. Interaction map

- JEPA pretrain (`01`) is the initializer for frozen AC (`10`) and interleaved tokens (`03`).
- Latent vs video MPC (`02`) is only fair if goal spec (`07`) and camera (`08`) match.
- Cooldown (`05`) and scale levers (`06`) change token shapes; AC heads must follow (`VJEPA-GAP-04`).
- Prefix training (`04`) changes the state distribution that CEM (`02`) searches.
- Variant lock (`09`) is a logging constraint on every other transfer.

This KB does not schedule experiments.

## 14. Invalid generalizations

- Do not assign Table 2/3 Franka numbers to action-free V-JEPA 2 or to V-JEPA 2.1.
- Do not use these transfers to justify Generator pixel or FD/WAM changes; Table 3 is a baseline, not an attachment.
- Do not treat PerceptionTest **84.0** (8B LLM align) as a frozen ViT-g number.
- Do not treat 10 trials as a tight CI, especially grasp-box 25%/20%.
- Do not claim language-goal planning from Table 2.
- Do not assume 1M+ hour pretrain is reproducible; start from released checkpoints.

## 15. Transfer record template

```text
Transfer ID:
Source mechanism and exact evidence (variant tag required):
Target failure signature:
Target-model attachment point (Reasoner / latent planner, not Generator):
Required data/action/evaluator changes:
Baseline and matched controls:
Trainable parameters and initialization:
Compute and inference-budget change:
Primary and regression metrics:
Expected movement and mechanism probe:
Confounders and interaction risks:
Minimum experiment:
Falsification result:
Observed artifact or run record:
```

## Sources

- [VJ2-PAPER] mechanism, experiments, and numerical evidence.
- [VJ2-CODE] released attachment points and 2.1 split.
- [OBJ-VJEPA2-2025] variant discipline.
