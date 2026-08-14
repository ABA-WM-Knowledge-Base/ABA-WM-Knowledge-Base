---
id: world-model-kb.papers.vista.optimization-transfer
title: Vista Transferable Optimization Knowledge
kind: guide
status: maintained
last_updated: 2026-08-14
owners:
  - AIBuildAI world-model group
---

# Vista Transferable Optimization Knowledge

## Retrieval metadata

**Relevant queries:** transfer Vista, driving world model, multi-mode control, dynamic priors, learned reward without GT actions, triangular CFG, LoRA control phase, Cosmos3 Generator AV, not Policy-DROID.

**Knowledge provided:** ten falsifiable hypotheses, Cosmos3 Generator / AV specialist attachment, controls, expected movement, falsification. Not Policy-DROID. Not Wayve GAIA.

**Related pages:** [`paper.md`](paper.md); [forward dynamics](../../foundations/problem-formulation/forward-dynamics.md); [Cosmos3-Nano generator](../../models/cosmos3-nano/generator.md); [action modeling](../../models/cosmos3-nano/action-modeling.md); [optimization playbook](../../models/cosmos3-nano/optimization-playbook.md).

## 1. Transfer discipline

Vista evidence supports **high-fidelity action-conditioned driving video**, **factorized control encoders**, **latent-replacement long rollouts**, and **ensemble reward without GT actions**. Attach on **Generator FD/WAM for AV/multiview specialists**, not Reasoner text plans and not robot Policy-DROID joints.

Wayve GAIA is not an implementation reference for these transfers.

## 2. Intervention matrix

| ID | Target failure | Mechanism | Attachment | Evidence | Risk |
|---|---|---|---|---|---|
| `DRIVE-XFER-01` | bland unconditional video | multi-mode control encoders | AV action adapters | Table 3 | mode coverage gap |
| `DRIVE-XFER-02` | short horizon only | latent replacement / priors | Generator temporal loop | Table 3 priors | drift |
| `DRIVE-XFER-03` | weak counterfactuals | fixed-context control sweeps | FD eval protocol | Sec. 4.2 | camera confound |
| `DRIVE-XFER-04` | no reward without actions | ensemble uncertainty reward | auxiliary reward | Table 4; Fig. 11 | tiny 0.014 delta |
| `DRIVE-XFER-05` | front-view-only bias | multiview consistency | multiview specialist | paper limitation | sync errors |
| `DRIVE-XFER-06` | VRAM blocks long clips | low-VRAM sampling | inference kernels | `--low_vram` | quality regression |
| `DRIVE-XFER-07` | geography overfit | OpenDV-scale mixture | training mixture | 1735 h; Waymo zero-shot | license/storage |
| `DRIVE-XFER-08` | 9D AV action too coarse | factorized interfaces | per-mode encoders | Table 3 angle vs command | adapter sprawl |
| `DRIVE-XFER-09` | static scene, mushy objects | dynamics + structure losses | FD auxiliary losses | Fig. 12; `lambda_2=0.1` | metric gaming |
| `DRIVE-XFER-10` | CFG saturates AR rollouts | triangular guidance / LoRA phase | sampler + control SFT | Eq. 9; Table 5 | over-guidance |

## 3. `DRIVE-XFER-01`: versatile driving control encoders

**Source mechanism.** Vista conditions on trajectory, command, steering/speed, and goal via one interface. On nuScenes with 3 priors, trajectory difference is `0.835` (trajectory) and `0.832` (angle & speed) versus `1.820` action-free. [VISTA-PAPER, Table 3]

**Target behavior.** Generator FD that currently ignores planner-style commands or goal points.

**Attachment.** Mode-specific encoder branches on Cosmos3-Nano **Generator** AV action adapters, not one pooled 9D vector. Not Reasoner.

**Minimum controlled experiment.** Single 9D vector versus factorized encoders; hold backbone, data, sampler, and CFG. Report IDM trajectory error, shuffled-control gap, and FVD on the same 537-clip protocol analog.

**Expected movement.** Lower trajectory difference on held-out commands without FVD collapse. Low-level modes (traj / angle-speed) should move Table 3-style L2 more than command/goal.

**Falsification.** Reject if factorized encoders match the single vector on control metrics, if shuffled commands match GT commands, or if FVD improves while IDM L2 stays at the action-free baseline (`1.820` nuScenes 3-prior analog).

## 4. `DRIVE-XFER-02`: dynamic priors / generated-prefix replacement

**Source mechanism.** Increasing condition frames from 1 to 3 cuts nuScenes action-free trajectory difference `3.785 -> 2.597 -> 1.820`. Training samples prior order with probabilities `1/15, 2/15, 4/15, 8/15` for 0-3 condition frames. Decode uses 3-frame overlap averaging. [VISTA-PAPER, Table 3, Appendix C.4]

**Target behavior.** Long AV rollouts that forget history after one clip.

**Attachment.** Train Generator FD with variable clean/generated prefix length; inference latent replacement. Not Reasoner memory.

**Minimum controlled experiment.** 0/1/3 priors at matched steps; lane/trajectory error versus horizon; last-frame copy baseline.

**Expected movement.** Lower long-horizon drift; modest one-step FD change.

**Falsification.** Reject if extra priors help long metrics but destroy one-step FD, or if they only copy the last frame.

## 5. `DRIVE-XFER-03`: counterfactual control evaluation

**Source mechanism.** Table 3 and Fig. 8 fix context and vary control modality, including Waymo (unseen). [VISTA-PAPER, Sec. 4.2]

**Target behavior.** FVD-only AV eval that cannot detect ignored steering.

**Attachment.** Standard AV FD eval: fixed context, sweep command/traj/steer, plus shuffle.

**Minimum controlled experiment.** Hold the condition frame and sampler seed; compare GT control, shuffled control, and opposite-turn control. Report IDM trajectory L2, lane-keep, and FVD. Do not retune CFG per arm.

**Expected movement.** Models with better control show larger true-versus-shuffle separation.

**Falsification.** Reject a "Vista transfer" if FVD improves while all control sweeps are identical.

## 6. `DRIVE-XFER-04`: learned reward without GT actions

**Source mechanism.** Ensemble disagreement yields a scalar reward. Waymo GT commands `0.892` versus random `0.878`. Fig. 11 shows reward falling as trajectory L2 jitter grows (1500 cases). [VISTA-PAPER, Table 4, Sec. 4.3]

**Target behavior.** Rank AV proposals when expert actions are missing.

**Attachment.** Auxiliary ensemble-uncertainty head on Generator futures for route ranking — not Policy-DROID.

**Minimum controlled experiment.** Rule-based collision cost versus ensemble reward versus L2-to-expert, on held-out routes with independent collision labels.

**Expected movement.** Better ranking of unsafe jittered trajectories.

**Falsification.** Reject if the 0.014 command gap does not replicate, or if reward tracks L2-to-expert while missing collisions that L2 also misses.

## 7. `DRIVE-XFER-05`: multiview consistency for specialists

**Source mechanism.** Vista is front-view by design (data scaling, camera-count heterogeneity). Surround-view is listed as future work. [VISTA-PAPER, Appendix discussion]

**Target behavior.** Cosmos3 multiview driving specialists that diverge across cameras.

**Attachment.** Cross-camera consistency losses on Generator outputs for AV specialists.

**Minimum controlled experiment.** Front-only versus two-view with cycle consistency; collision and lane metrics.

**Expected movement.** Lower cross-view geometric contradiction.

**Falsification.** Reject if extra views do not change collision rate (paper cites NAVSIM 1.1% as an external statistic, not a Vista number).

## 8. `DRIVE-XFER-06`: memory-efficient long sampling

**Source mechanism.** Released `--low_vram` targets <80 GB; docs suggest ≥32 GB. [VISTA-CODE, `docs/SAMPLING.md`]

**Target behavior.** 1024p rollouts that OOM on specialist inference boxes.

**Attachment.** Cosmos3 inference tiling/offload analogous to `--low_vram`.

**Minimum controlled experiment.** Full versus low-VRAM on the same seeds; FVD, trajectory difference, latency.

**Expected movement.** Enable sampling with bounded FVD delta.

**Falsification.** Reject if low-VRAM changes control metrics more than visual metrics, silently invalidating Table 3-style tests.

## 9. `DRIVE-XFER-07`: geographically diverse unlabeled video

**Source mechanism.** Phase 1 trains on ~1735 h filtered OpenDV-YouTube; controllability is then mixed 1:1 with nuScenes. Waymo appears in Table 3 as unseen. [VISTA-PAPER, Appendix C.2, Table 3]

**Target behavior.** nuScenes-only FD that fails outside Boston/Singapore-like scenes.

**Attachment.** Scale unlabeled driving video in Generator pretraining; keep labeled control as a second phase.

**Minimum controlled experiment.** nuScenes-only versus OpenDV-scale unlabeled mix, then the same control finetune. Evaluate Waymo-like OOD.

**Expected movement.** Better OOD FVD and control transfer.

**Falsification.** Reject if unlabeled hours do not move OOD control after a matched control phase.

## 10. `DRIVE-XFER-08`: factor low-level versus high-level actions

**Source mechanism.** Angle/speed and trajectory beat command/goal on Table 3 (nuScenes 3-prior: `0.832`/`0.835` vs `1.593`/`1.585`). [VISTA-PAPER, Table 3]

**Target behavior.** A single 9D AV action that cannot express discrete commands and dense waypoints together.

**Attachment.** Separate encoders with independent dropout (paper 15% per mode).

**Minimum controlled experiment.** Pooled 9D versus factored modes; drop each mode at eval.

**Expected movement.** Low-level modes dominate trajectory error; commands help discrete maneuvers.

**Falsification.** Reject if one pooled vector matches all modes, or if command-only training matches trajectory-conditioned error.

## 11. `DRIVE-XFER-09`: dynamics and structure auxiliary losses

**Source mechanism.** Dynamics enhancement and structure preservation (`lambda_2=0.1`) are qualitative ablations in Fig. 12; they are not a full FID table. [VISTA-PAPER, Sec. 3.1, Fig. 12, Appendix C.3]

**Target behavior.** Other agents frozen while ego moves, or melted object boundaries.

**Attachment.** Auxiliary FD losses on Cosmos3 Generator video tokens.

**Minimum controlled experiment.** EDM-only versus +dynamics versus +structure versus both, 10K steps analog to the paper's 8-GPU ablation.

**Expected movement.** Better independent object motion and edges; FVD may move less than human motion ratings.

**Falsification.** Reject if losses improve FID while IDM trajectory error worsens.

## 12. `DRIVE-XFER-10`: triangular CFG and LoRA control phase

**Source mechanism.** Linear SVD CFG saturates long AR driving video. Triangular `s_min=1.0`, `s_max=2.5` is the paper's fix. Control is a LoRA phase, not from-scratch. Action independence improves subset FVD (stop `132.3 -> 118.9` with trajectory). [VISTA-PAPER, Eq. 9, Table 5; Appendix D.4]

**Target behavior.** Saturated colors on long Cosmos3 AV rollouts, or control finetunes that destroy Phase-1 fidelity.

**Attachment.** Time-varying guidance on Generator sampling; LoRA on attention for control SFT.

**Minimum controlled experiment.** Linear versus triangular CFG at matched `s_max`; full finetune versus LoRA r=16.

**Expected movement.** Longer usable rollouts; control metrics with preserved FID.

**Falsification.** Reject if triangular CFG only reduces saturation while trajectory difference stays at the action-free baseline.

## 13. Invalid generalizations

- Do not cite Wayve GAIA as Vista, as an implementation template, or as a Table 2 baseline rerun.
- Do not treat FID 6.9 / FVD 89.4 as a planning success rate, collision rate, or closed-loop NAVSIM score.
- Do not attach driving LoRA or Fourier command encoders to Policy-DROID joints.
- Do not treat Table 4's 0.014 reward gap as a calibrated safety filter or as a substitute for a collision label.
- Do not bind `--low_vram` quality to Table 2 without an ablation.
- Do not attach these mechanisms to Cosmos3 Reasoner text; they belong on Generator FD/WAM for AV specialists.

## 14. Transfer record template

```text
Hypothesis ID (DRIVE-XFER-NN):
Target model surface (Generator FD/WAM AV, not Reasoner, not Policy-DROID):
Source table/equation:
Attachment files:
Controls held fixed:
Metrics (IDM L2, FVD, shuffle gap):
Decision (accept / reject / inconclusive):
```

No transfer experiment is registered in this KB.

Phase-1 unlabeled OpenDV (~1735 h) and Phase-2 LoRA control are sequential; do not collapse them into one "Vista finetune" when attaching to Cosmos3 Generator AV specialists.

## Sources

- [VISTA-PAPER] tables and recipes.
- [VISTA-CODE] `sample.py`, `guiders.py`, training YAMLs.
