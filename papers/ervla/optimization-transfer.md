---
id: world-model-kb.papers.ervla.optimization-transfer
title: ERVLA Transferable Optimization Knowledge
kind: guide
status: maintained
last_updated: 2026-08-21
owners:
  - AIBuildAI world-model group
---

# ERVLA Transferable Optimization Knowledge

## Retrieval metadata

**Relevant queries:** transfer ERVLA, add CoT to a VLA, reasoning dropout, which CoT content, grounded motion cues, point trajectory, drop bounding boxes, cot probability, choice branch, knowledge truncation, language-track generalization.

**Knowledge provided:** falsifiable intervention patterns from ERVLA, attachment surfaces on Xiaomi-Robotics-1's xr1 stack, required controls, expected movement, and invalid generalizations.

**Related pages:** [`paper.md`](paper.md) owns evidence; [`codebase.md`](codebase.md) owns surfaces; [Xiaomi-Robotics-1 VLM backbone](../../models/xiaomi-robotics-1/vlm-backbone.md) and [optimization playbook](../../models/xiaomi-robotics-1/optimization-playbook.md) own the target; [autoregressive modeling](../../foundations/learning-objectives/autoregressive-modeling.md) owns the objective family.

## 1. Transfer discipline

ERVLA's ablations were run on a different base training set (Bridge pre-training for Table 1; a 2,592-hour mix for the main model) with an unreleased annotation pipeline. Magnitudes (+4 to +7 points) are ERVLA-setting facts; on a checkpoint already trained with CoT (Xiaomi-Robotics-1-VLABench) the marginal effect of more CoT is unknown and may be zero.

## 2. Intervention matrix

| ID | Target failure | Mechanism | Attachment surface | Primary evidence | Principal risk |
|---|---|---|---|---|---|
| `ECOT-XFER-01` | weak instruction/commonsense grounding | reasoning dropout: train with CoT text at probability p, act without it | data path `cot_prob`; `xr1_cot` next-token loss | design ablation: no-CoT 77.4 vs 86.9 (LIBERO-Plus) | label noise; already-trained checkpoint |
| `ECOT-XFER-02` | abstract reasoning distracts | grounded, action-oriented CoT content (movement, point trajectory, gripper) | label generator prompt | Table 1: movement +4.1, point trajectory +4.8; bounding box -3.2 | our VLM cannot replay the simulator for exact positions |
| `ECOT-XFER-03` | multimodal demo averaging | choice policy branch | present in `xr1` (`loss_choice`, `loss_score`) | 83.8 -> 86.9 | memory |
| `ECOT-XFER-04` | DiT distracted by reasoning tokens | knowledge truncation (DiT reads the semantic prefix only) | `action_vlm_condition_segments` in the collate | 84.7 -> 86.9 | already implemented in xr1's packing |
| `ECOT-XFER-05` | inference latency from reasoning | test-time reasoning dropout | serving path (no text generation) | stated mechanism | none on this stack |

## 3. `ECOT-XFER-01`: reasoning dropout

**Source mechanism.** Samples rendered `/cot` with probability `p_cot` carry the reasoning text as a next-token target; `/no_cot` samples do not; inference uses `/no_cot`. [ERV-PAPER, Sec. 3]

**Attachment.** `cot_prob` in the VLABench data path selects the rendering per sample and emits labels over the `<cot>` span; `xr1_cot` adds `cot_coefficient x CE`. The prompt suffix flips with the rendering, so `/no_cot` samples are byte-identical to the released recipe.

**Minimum controlled experiment.** `cot_prob` 0 vs 0.5, same warm start, steps, seed, data order; paired 250-episode L2; per-track deltas.

**Expected movement.** Tracks 3/4 up; Track 1 flat. **Falsification.** No paired gain beyond ~6 pp on Tracks 3/4 over two seeds, or a Track-1 drop.

## 4. `ECOT-XFER-02`: content selection

**Source mechanism.** Action-related fields help; semantic-only fields hurt; bounding boxes hurt in their setting. [ERV-PAPER, Table 1]

**Attachment.** The label generator's prompt: ask for target object + relative position + sub-goal + next motion direction; omit pixel boxes and long plans.

**Minimum experiment.** Motion-only vs full vs abstract-only label sets at `cot_prob` 0.5. **Falsification.** Abstract-only is not worse than motion-only.

## 5. `ECOT-XFER-03`/`04`: heads and truncation

Both already exist in the xr1 trainer; the transferable decision is to keep them on. **Minimum experiment.** Zero the choice/score weights; compare. **Falsification.** Equal SR with the heads off.

## 6. Invalid generalizations

- ERVLA magnitudes are not priors for a checkpoint already trained with CoT.
- "CoT at inference" is not a lever on the released XR-1 serving path.
- LIBERO-Plus perturbation results do not transfer to VLABench tracks.

## Sources

[ERV-PAPER] Sec. 3, Table 1, Table 4, design ablation; [XR1-TR] Sec. 5.3; [XR1-CODE].
