---
id: world-model-kb.papers.dreamzero.optimization-transfer
title: DreamZero Transferable Optimization Knowledge
kind: guide
status: maintained
last_updated: 2026-08-14
owners:
  - AIBuildAI world-model group
---

# DreamZero Transferable Optimization Knowledge

## Retrieval metadata

**Relevant queries:** transfer DreamZero, WAM to Cosmos3, joint video action training, inverse-dynamics alignment, Flash distillation, Beta noise schedule, cross-embodiment adapter, DiT cache, or Generator FD/WAM optimization.

**Knowledge provided:** ten numbered falsifiable hypotheses for attaching DreamZero mechanisms to Cosmos3-Nano Generator FD/WAM surfaces, with source mechanism, target behavior, attachment, minimum experiment, expected movement, and falsification.

**Related pages:** [`paper.md`](paper.md); [world action models](../../foundations/definitions-and-taxonomy/world-action-model.md); [forward dynamics](../../foundations/problem-formulation/forward-dynamics.md); [Cosmos3-Nano generator](../../models/cosmos3-nano/generator.md); [Cosmos3-Nano optimization playbook](../../models/cosmos3-nano/optimization-playbook.md).

Foundation evidence anchor: [WAM-DREAMZERO-2026]. Each item below is a **hypothesis** until validated on the target model under controlled comparisons.

## 1. Transfer discipline

DreamZero demonstrates one 14B WAM with strong real-robot numbers under its protocol. Transfers apply only when Cosmos3-Nano exhibits a compatible failure mode (weak cross-task generalization, myopic actions, or insufficient closed-loop rate) and exposes a **Generator FD/WAM** attachment point—not the Reasoner text encoder unless a JEPA-style latent planner is the explicit target.

Do not universalize "zero-shot policy" or "WAM superiority over VLA" from DreamZero alone. [WAM-DREAMZERO-2026]

## 2. Intervention matrix

| ID | Target failure | Mechanism transferred | Attachment surface | Primary evidence | Principal risk |
|---|---|---|---|---|---|
| `DREAMZERO-XFER-01` | action-only FD ignores physical consequences | joint video+action flow matching | Generator FD/WAM | Eq. 1, >2x narrative | compute confound vs VLA |
| `DREAMZERO-XFER-02` | myopic contact / gripper timing | IDM-style action from predicted futures | action decoder after future tokens | Eq. 1 factorization | extra latency |
| `DREAMZERO-XFER-03` | AR error accumulation | replace generated prefix with GT in cache | closed-loop KV / history | Fig. 4 inference | not applicable offline |
| `DREAMZERO-XFER-04` | few-step action quality collapse | Flash decoupled Beta video noise | sampler training stage | Tables 1, 3 | video quality drop |
| `DREAMZERO-XFER-05` | repetitive demos overfit primitives | diverse non-repeated mixture | data sampler | Table 4 Q1 | coverage holes |
| `DREAMZERO-XFER-06` | small backbone hallucinates dynamics | scale joint WAM with video prior | Generator width | Table 4 Q2 | VLA may not scale same way |
| `DREAMZERO-XFER-07` | bidirectional chunk breaks FPS alignment | AR native-rate chunks + KV | temporal blocks | Table 4 Q3, Sec. 3.1 | AR exposure bias |
| `DREAMZERO-XFER-08` | no labels on target robot | video-only co-train | visual layers, freeze action adapter | Table 2 | action-scale mismatch |
| `DREAMZERO-XFER-09` | new embodiment needs hours of teleop | few-shot play-data LoRA | action decoder LoRA | Sec. 5 Q5 | morphology gap |
| `DREAMZERO-XFER-10` | CFG/DiT cost blocks Hz | 2-GPU CFG + DiT cache | inference kernels | Table 1 | cache stale velocities |

## 3. `DREAMZERO-XFER-01`: joint future-video and action denoising

**Source mechanism.** DreamZero jointly denoises video latents and actions with a shared flow-matching objective on a Wan2.1 I2V backbone. The paper attributes >2x task-progress generalization versus matched VLAs to this joint WAM rather than action-only imitation. [DZ-PAPER, Sec. 3.1, Eqs. 1-3; WAM-DREAMZERO-2026]

**Target behavior.** Improve held-out task/environment success when Cosmos3 Generator currently trains an action head on frozen or weakly coupled video features.

**Attachment.** Cosmos3-Nano **Generator FD/WAM** path: shared backbone predicts future visual tokens and action tokens from `(o, g, q)`. Analog in the pinned tree: `groot/vla/model/dreamzero/modules/wan_video_dit_action_casual_chunk.py` plus `wan_flow_matching_action_tf.py`. Do not attach to Reasoner.

**Minimum experiment.** Match parameter budget and optimizer steps against an action-only FD head on the same robot mixture. Report held-out success, action MSE, and video PSNR/FVD. Include a shuffled-future control that severs video-action alignment.

**Expected movement.** Higher held-out success and larger true-vs-shuffled action separation, with possible extra train FLOPs.

**Falsification.** Reject if action-only matches joint on success at equal compute, or if joint training improves offline video metrics without closed-loop gain.

## 4. `DREAMZERO-XFER-02`: inverse-dynamics alignment

**Source mechanism.** Joint prediction factorizes as video prediction times IDM; actions are trained to be recoverable from predicted visual futures, not only from the current frame. [DZ-PAPER, Eq. 1]

**Target behavior.** Reduce myopic grasps and mistimed contacts on contact-heavy tasks.

**Attachment.** After partial future latent prediction in the Generator, route future tokens through gated cross-attention into the action decoder (`groot/vla/model/dreamzero/action_head/wan_flow_matching_action_tf.py`) before executing the action head.

**Minimum experiment.** Ablate alignment path vs same model with actions from current-frame features only. Measure contact-phase success, gripper timing error, and latency.

**Expected movement.** Better contact timing; modest latency cost.

**Falsification.** Reject if the alignment path shows no improvement on contact-heavy tasks, or if latency exceeds budget without success gain.

## 5. `DREAMZERO-XFER-03`: ground-truth visual feedback into AR cache

**Source mechanism.** After each executed chunk, DreamZero writes real observations into the KV cache, eliminating compounding video error unique to closed-loop WAMs. [DZ-PAPER, Sec. 3.1, Fig. 4]

**Target behavior.** Stabilize long-horizon Generator rollouts used as a policy, not as an offline video sampler.

**Attachment.** Generator closed-loop history buffer: swap predicted visual tokens for encoded live frames at chunk boundaries. Offline imagination training should not silently inherit this trick.

**Minimum experiment.** Compare (a) generated-prefix AR, (b) GT-prefix replacement, (c) mixed scheduled sampling. Report error vs chunk index and closed-loop success.

**Expected movement.** Lower long-horizon drift in closed loop; little change to open-loop video scores.

**Falsification.** Reject if GT replacement does not beat generated-prefix beyond noise, or if the policy depends on cache hacks that cannot run on the robot.

## 6. `DREAMZERO-XFER-04`: Flash decoupled noise for few-step actions

**Source mechanism.** Shared `t` for video and action collapses 4-step table-bussing progress from 83% to 52% at 1 step. Flash uses `Beta(7,1)`-biased video noise and uniform action noise, recovering 74% at 150 ms. [DZ-PAPER, Fig. 5, Tables 1, 3]

**Target behavior.** Raise closed-loop Hz without collapsing action quality when Cosmos3 Generator uses few denoising steps.

**Attachment.** Final-stage Generator training: sample video times from a high-noise Beta while keeping action times uniform (or a declared alternative). Distill after a full shared-`t` stage, matching the paper's late Flash stage.

**Minimum experiment.** Stratify 1/4/8/16 steps for shared-`t` vs Flash on one closed-loop task. Predeclare Hz and success thresholds.

**Expected movement.** 1-step Flash close to 4-step shared-`t` success; naive 1-step far below.

**Falsification.** Reject if Flash matches naive 1-step, or if success drops more than the predeclared budget versus full sampling.

## 7. `DREAMZERO-XFER-05`: diverse non-repetitive robot data

**Source mechanism.** 500 h diverse vs 500 h repetitive demonstrations: 50% vs 33% on PnP Easy at matched 50K steps. WAMs are argued to need diverse state-action correspondences because video priors are inherited. [DZ-PAPER, Table 4]

**Target behavior.** Reduce overfitting to pick-and-place primitives on held-out verbs/layouts.

**Attachment.** Generator SFT mixture: increase unique scenes/skills at fixed hours, not more repeats of the same teleop script.

**Minimum experiment.** Hold hours and steps fixed; compare repetitive vs diverse. Evaluate seen vs unseen verbs and table layouts.

**Expected movement.** Unseen-task progress rises; seen-task may stay flat.

**Falsification.** Reject if coverage-matched repeats match diverse data, indicating hours not diversity.

## 8. `DREAMZERO-XFER-06`: WAM scale follows video quality

**Source mechanism.** 14B AR WAM 50% vs 5B AR 21% on the same diverse mix; matched VLAs both sit at 50% with no scale gap on that probe. The paper claims policy performance tracks video generation quality. [DZ-PAPER, Table 4 Q2]

**Target behavior.** When small Cosmos Generators hallucinate dynamics that the action head then executes.

**Attachment.** Scale the Generator FD/WAM, not the Reasoner, under a matched robot mixture.

**Minimum experiment.** 2B vs 14B-class Generator at matched steps and data. Report video hallucination rate, action error, and success.

**Expected movement.** Larger WAM reduces visual hallucination and raises success; a matched VLA scale sweep may be flatter.

**Falsification.** Reject if the small WAM matches the large one on control, or if scale only moves passive video metrics.

## 9. `DREAMZERO-XFER-07`: autoregressive native-rate chunks

**Source mechanism.** AR vs bidirectional means match (50%) but AR has lower variance (6.3 vs 14.4 SE). The paper prefers AR for KV cache, native FPS, and video-action alignment. [DZ-PAPER, Sec. 3.1, Table 4 Q3]

**Target behavior.** Smoother executed motion and tighter video-action alignment than subsampled bidirectional windows.

**Attachment.** Generator temporal loop: chunked AR over native-rate frames rather than a fixed bidirectional clip.

**Minimum experiment.** AR vs bidirectional at matched params and data. Measure action smoothness, alignment (video vs executed), and success.

**Expected movement.** Similar means, lower variance and better FPS-aligned control for AR.

**Falsification.** Reject if bidirectional dominates on success and smoothness, or if AR's exposure bias erases the alignment gain without GT cache (`DREAMZERO-XFER-03`).

## 10. `DREAMZERO-XFER-08`: video-only cross-embodiment co-training

**Source mechanism.** 10-20 minutes of video-only YAM or human data lift unseen-task progress from 38.3% to 55.4% / 54.3% without target actions. [DZ-PAPER, Table 2]

**Target behavior.** Improve target-robot generalization when action labels are absent.

**Attachment.** Finetune visual dynamics layers on passive target video; freeze action normalization until calibration. Mix 1:1 with source labeled data as in the paper.

**Minimum experiment.** Video-only FT vs no FT vs action-labeled FT upper bound on held-out target tasks.

**Expected movement.** Material relative gain from video-only; still below full action labels.

**Falsification.** Reject if video-only matches no-FT within noise, or if gains vanish after proprio/action calibration ablation (leakage).

## 11. `DREAMZERO-XFER-09`: few-shot play-data embodiment adapters

**Source mechanism.** AgiBot checkpoint + 30 min YAM play (55 trajectories, 11 tasks) yields language-following pick-and-place on novel objects. Both robots are bimanual parallel grippers. [DZ-PAPER, Sec. 5 Q5]

**Target behavior.** Adapt Cosmos3 Generator to a new robot without collecting a full teleop corpus.

**Attachment.** LoRA on action decoder and embodiment stats (`yam_relative.yaml`, `embodiment_tags.py`); keep visual backbone. Align the three camera views as in `docs/DATASET_TO_GEAR_AND_TRAIN.md`. This adapter is why DreamZero is not a universal policy.

**Minimum experiment.** 30-min play vs 30-min expert teleop vs no adapt. Eval language following and novel objects.

**Expected movement.** Play data enables basic language-conditioned pick-place when morphology is close.

**Falsification.** Reject if play data fails whenever morphology or camera layout differs, or if LoRA overfits the 11 training language strings.

## 12. `DREAMZERO-XFER-10`: CFG parallelism and DiT caching

**Source mechanism.** CFG across two GPUs plus velocity caching contributes the bulk of the ~5.5x systems speedup before Flash. [DZ-PAPER, Table 1; DZ-CODE, `--enable-dit-cache`]

**Target behavior.** Raise Generator closed-loop Hz at fixed weights.

**Attachment.** Inference graph only: split CFG, cache DiT velocities when cosine similarity exceeds a threshold (`socket_test_optimized_AR.py --enable-dit-cache`). Keep training weights frozen. Do not confuse README ~3 s H100 server time with Table 3 150 ms Flash.

**Minimum experiment.** Latency-stratified success with cache on/off and 1 vs 2 CFG GPUs. Record action delta vs uncached reference.

**Expected movement.** Large latency drop with small success change if the similarity threshold is conservative.

**Falsification.** Reject if cache changes executed actions enough to drop success, or if two-GPU CFG does not reduce step time (implementation bound).

## 13. Interaction map

- Joint WAM (`01`) is the parent of IDM alignment (`02`) and AR native-rate (`07`).
- GT cache (`03`) makes AR (`07`) safe in closed loop.
- Flash (`04`) and DiT cache (`10`) are complementary latency tools; ablate separately.
- Diversity (`05`) and scale (`06`) interact: small models on repetitive data fail twice.
- Video-only (`08`) and play-data (`09`) assume a working source WAM (`01`).

## 14. Invalid generalizations

- Do not attach DreamZero transfers to Cosmos3 **Reasoner** representation training; that is the V-JEPA line.
- Do not claim zero-shot deployment on new robots without action-space validation.
- Do not treat >2x VLA numbers as universal; they bind to [DZ-PAPER] baselines and task-progress.
- Do not equate attractive predicted video with safe executable actions.
- Do not mix README ~3 s H100 server latency with Table 3 150 ms Flash without matching flags (`DREAMZERO-GAP-03`).

## 15. Transfer record template

```text
Transfer ID: DREAMZERO-XFER-0N
Source mechanism and exact evidence:
Target failure signature:
Target-model attachment point (Generator FD/WAM):
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

- [WAM-DREAMZERO-2026] scoped WAM and evaluation claims.
- [DZ-PAPER] mechanisms, Tables 1-4, and experiment anchors.
- [DZ-CODE] implementation attachment hints.
- [Cosmos3-Nano action modeling](../../models/cosmos3-nano/action-modeling.md) target surface.
