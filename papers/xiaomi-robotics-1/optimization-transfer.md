---
id: world-model-kb.papers.xiaomi-robotics-1.optimization-transfer
title: Xiaomi-Robotics-1 Transferable Optimization Knowledge
kind: guide
status: maintained
last_updated: 2026-08-21
owners:
  - AIBuildAI world-model group
---

# Xiaomi-Robotics-1 Transferable Optimization Knowledge

## Retrieval metadata

**Relevant queries:** transfer Xiaomi-Robotics-1, warm start from the benchmark fine-tune, scene-transition captions as supervision, choice branch, frequency loss, async prefix, minimal-data adaptation, scaling, embodiment alignment, VLABench intervention.

**Knowledge provided:** falsifiable intervention patterns derived from the report, their attachment surfaces on the released 5B for VLABench post-training, required controls, expected movement, and invalid generalizations.

**Related pages:** [`paper.md`](paper.md) owns evidence; [model optimization playbook](../../models/xiaomi-robotics-1/optimization-playbook.md) owns experiment discipline; [model action head](../../models/xiaomi-robotics-1/action-head.md) and [data](../../models/xiaomi-robotics-1/data.md) own surfaces; [ERVLA transfer](../ervla/optimization-transfer.md) owns CoT-specific interventions.

## 1. Transfer discipline

Every item is a **hypothesis**. The report publishes no ablations, so none of its components has a measured marginal contribution; the benchmark fine-tune recipes are undisclosed; the scaling evidence is open-loop MSE. Copying Table 4 onto a differently trained checkpoint is invalid.

## 2. Intervention matrix

| ID | Target failure | Mechanism transferred | Attachment surface | Primary evidence | Principal risk |
|---|---|---|---|---|---|
| `XIAOMI-XFER-01` | cold start wastes compute | warm start from the strongest benchmark fine-tune | `model.params.pretrained` = imported `-VLABench` + base choice heads | Table 4 anchor 59.1 | format/convention traps |
| `XIAOMI-XFER-02` | instruction-only supervision is thin | scene-transition-style captions as auxiliary text targets | CoT/NTP loss on VLM (ext `xr1_cot`) | Sec. 4 pre-training objective; Sec. 5.3 CoT at 50 % | self-generated labels; loss balance |
| `XIAOMI-XFER-03` | unimodal regression averages multi-modal demos | keep the best-of-K choice branch active | `loss_choice`, `loss_score` weights | Sec. 3 `L_Regression`; ERVLA ablation: removing the choice branch costs 3.1 (LIBERO-Plus) | extra memory; no XR-1 ablation |
| `XIAOMI-XFER-04` | jittery chunks | frequency-domain loss weight | `freq_coefficient` | Sec. 3 (implemented, unablated) | over-smoothing grasps |
| `XIAOMI-XFER-05` | latency at deployment | async prefix training | `async_train` | Xiaomi-Robotics-0 recipe | no effect on the synchronous benchmark client |
| `XIAOMI-XFER-06` | little task data | few-hour adaptation | full fine-tune from the post-trained base | Table 6 (75 % at < 10 h) | real-robot evidence, not sim |
| `XIAOMI-XFER-07` | cross-embodiment reuse | relative delta end-effector actions with aligned frames | data-path convention | Sec. 4 embodiment alignment | VLABench client integrates world-frame per-step deltas |
| `XIAOMI-XFER-08` | more data/model helps | scale pre-training or size | not available (no corpus/code; 5B only) | Sec. 6 curves | unactionable here |

## 3. `XIAOMI-XFER-01`: warm start from the benchmark fine-tune

**Source mechanism.** The report fine-tunes the post-trained base per benchmark; the VLABench fine-tune is released. [XR1-TR, Sec. 5; XR1-HF-VLABENCH]

**Attachment.** Import the HF weights plus the base's `*_choice` tensors into a trainer `model_states.pt`; keep the released `vlabench_choice` stats unless re-estimated deliberately.

**Minimum controlled experiment.** Export the untrained import and score it against the released checkpoint on identical configs and seed.

**Expected movement.** Zero difference. **Falsification.** Any systematic gap means the bridge or the conventions are wrong; stop before training.

## 4. `XIAOMI-XFER-02`: language targets as auxiliary supervision

**Source mechanism.** Pre-training pairs actions with scene-transition captions (0.1 NTP); the VLABench fine-tune adds ERVLA-style CoT at 50 %. [XR1-TR, Sec. 3-5]

**Attachment.** A next-token loss over a `<cot>...</cot>` span in the VLM sequence, mixed with probability `cot_prob`; content = grounded target/sub-goal/motion strings generated per keyframe.

**Minimum experiment.** `cot_prob` 0 vs 0.5 at equal steps and seed; paired L2 per track. **Expected movement.** Track 3/4 SR up by a few points (ERVLA's magnitudes), Track 1 unchanged. **Falsification.** No paired gain beyond ~6 pp on the language tracks after two seeds, or Track 1 regression.

## 5. `XIAOMI-XFER-03`: choice branch retained

**Source mechanism.** Best-of-K candidate regression plus a score head. [XR1-TR, Sec. 3]

**Minimum experiment.** Zero the choice/score weights vs default at equal steps. **Falsification.** Equal SR with the heads off (then drop them for memory).

## 6. `XIAOMI-XFER-04`: frequency loss weight

**Minimum experiment.** `freq_coefficient` 0 / 1 / 3, paired L2 and mean `consumed_step` on successes. **Falsification.** No change in SR and speed.

## 7. `XIAOMI-XFER-07`: action convention

**Source mechanism.** Embodiment alignment with relative delta poses. [XR1-TR, Sec. 4]

**Attachment.** For VLABench the client defines the convention (world-frame per-step position + Euler deltas, absolute gripper); the data path must match it exactly; a convention change requires a client change and is off-protocol.

**Falsification of a data path.** The untrained export (`XIAOMI-XFER-01`) scores like the released checkpoint.

## 8. Invalid generalizations

- Scaling curves do not license a claim about a 5B fine-tune's closed-loop success.
- Real-robot adaptation numbers do not transfer to simulation tracks.
- RoboCasa365's disclosed recipe (120k steps, batch 512) is not the VLABench recipe.

## Sources

[XR1-TR] Sec. 3-6, Tables 4 and 6; [XR1-HF-VLABENCH]; [XR1-ISSUE-4]; [XR0-TR]; [ERV-PAPER] design ablations.
