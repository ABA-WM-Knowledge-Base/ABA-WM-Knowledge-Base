---
id: world-model-kb.models.xiaomi-robotics-1.action-modeling
title: Xiaomi-Robotics-1 Action Representation and VLABench Conventions
kind: model
status: maintained
last_updated: 2026-08-21
owners:
  - AIBuildAI world-model group
---

# Xiaomi-Robotics-1 Action Representation and VLABench Conventions

## Retrieval metadata

**Relevant queries:** action representation, relative delta end-effector pose, per-step delta, chunk-cumulative delta, Euler delta, axis-angle, gripper absolute, action mask, mean std broadcast, vlabench_choice stats, JsonDataset convention, embodiment alignment.

**Knowledge provided:** the action semantics the model was trained and served with per checkpoint, the evidence that the VLABench checkpoint uses per-step world-frame position and Euler deltas with an absolute gripper, and the mismatch with the public trainer's real-robot convention.

**Related pages:** [Modality contracts](modalities-and-io.md) owns tensor layouts; [Policy](policy.md) owns the closed-loop integration; [Data](data.md) owns dataset fields; [actions and interventions](../../foundations/problem-formulation/actions-and-interventions.md) owns the model-independent action formalism.

## Strict task boundaries

Every Xiaomi-Robotics-1 checkpoint outputs a `(K, 60)` chunk in a normalized space defined by its robot type's mean/std. The meaning of each slot is fixed by the data path that trained the checkpoint and by the client that integrates it; two checkpoints with the same slot layout can still encode incompatible semantics. [XR1-CODE, `io.py`]

## Canonical action representation

### Report-level statement

Embodiment alignment in post-training unifies arm action spaces as "relative delta end-effector poses" with aligned frame orientations; this is the abstraction the pre-trained model shares across embodiments. [XR1-TR, Sec. 4]

### Real-robot trainer convention (`JsonDataset`)

Per arm: position delta `R_t^T (p_target - p_t)` in the current end-effector frame, rotation delta `rotm2aa(R_t^T R_target)` as axis-angle, gripper delta `g_target - g_t`; waist delta and base velocity in slots 16..19; K = 30 by default. The runtime client recovers targets with `recover_action`. [XR1-CODE, `json_dataset.py:_arm_action`, `io.py:recover_action`]

### VLABench checkpoint convention (served)

The eval client integrates each returned row cumulatively in the world (robot) frame: `current[:6] += action[:6]`, wraps Euler to (-pi, pi], and thresholds `action[6] >= 0.2` as "open". Therefore slot 0..2 = world-frame position step, 3..5 = Euler-angle step, 6 = absolute gripper command; K = 10, 5 executed per query. The released `vlabench_choice` stats are identical on all 10 rows with mean ~0 and gripper mean 0.54 / std 0.50, consistent with per-step deltas and a binary absolute gripper; roll/yaw std (0.19 / 0.22) is ~10x pitch std (0.02), consistent with unwrapped Euler differences in the producing pipeline. [XR1-CODE-EVAL-VLABENCH, `main.py:predict`; XR1-HF-VLABENCH, `preprocessor_config.json`]

Consequence: the public `JsonDataset` cannot train a checkpoint that the public VLABench client scores correctly; a VLABench data path must emit world-frame per-step deltas (k = 0 against the current state), wrapped Euler, absolute gripper.

### RoboCasa365 convention

Per the maintainers: 12-D actions (end-effector delta position and delta axis-angle, gripper, four mobile-base commands, a control-mode indicator), 16-step chunks all executed before replanning, 14-D state with relative end-effector pose, two gripper positions, and base pose. Different from both conventions above. [XR1-ISSUE-4]

## Required adapter schema (VLABench)

| Field | Source | Transform |
|---|---|---|
| state slots 0..6 | dataset `state` `[x, y, z, roll, pitch, yaw, gripper]` (robot frame) | none (raw) |
| action slots 0..2 | `actions[t+k][:3] - prev[:3]`, prev = state at k = 0 else `actions[t+k-1]` | per-step |
| action slots 3..5 | same difference on Euler, wrapped to (-pi, pi] | per-step |
| action slot 6 | `actions[t+k][6]` | absolute |
| slots 7..59 | 0 | masked by std 0 |
| normalization | `(a - mean) / (std + 1e-6)` with `(K, 60)` stats broadcast | released stats or re-estimated |

[VLAB-DATA-LEROBOT; XR1-CODE-EVAL-VLABENCH]

## Optimization levers

| Lever | Surface | Expected signal | Risk | Validation |
|---|---|---|---|---|
| Re-estimate stats with wrapped Euler deltas | stats tool | Better-conditioned roll/yaw targets | Warm start trained under the released stats | Paired L2 with both stat sets |
| Chunk-cumulative deltas instead of per-step | data path + client | Not allowed with the released client (it integrates per step) | Silent scoring of garbage | Never without changing the client |
| Gripper as delta | data path | Matches the trainer's real-robot convention | Client thresholds an absolute value | Invalid for the released protocol |
| Chunk length K = 16/30 | stats + processor export | Fewer queries per episode | Released recipe K = 10; client executes 5 | Paired L2 |

## Diagnostics and failure signatures

- Policy overshoots and oscillates within a 5-step window: chunk-cumulative targets integrated as per-step deltas.
- Gripper never opens: slot 6 trained as a delta near 0, thresholded against 0.2.
- Roll/yaw spikes of ~2 pi in decoded actions: unwrapped Euler differences in the data path.

## Sources

[XR1-TR] Sec. 4; [XR1-CODE] `xr1/mibot/data/datasets/json_dataset.py`, `xr1/mibot/utils/io.py`, `eval_vlabench/main.py`; [XR1-HF-VLABENCH] `preprocessor_config.json`; [XR1-ISSUE-4]; [VLAB-DATA-LEROBOT].
