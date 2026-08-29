---
id: world-model-kb.models.xiaomi-robotics-1.policy
title: Xiaomi-Robotics-1 Closed-Loop Policy Interface on VLABench
kind: model
status: maintained
last_updated: 2026-08-21
owners:
  - AIBuildAI world-model group
---

# Xiaomi-Robotics-1 Closed-Loop Policy Interface on VLABench

## Retrieval metadata

**Relevant queries:** closed-loop evaluation, eval client, VLABenchPolicy, dispatch.py, replan steps, plan horizon, gripper threshold, position offset, IK, get_qpos_from_ee_pos, episode cap, max_episode_length, server port, retry forever.

**Knowledge provided:** how the released client turns a chunk into simulator steps, the fixed client parameters behind the reported numbers, and the closed-loop failure signatures that are interface faults rather than policy faults.

**Related pages:** [Action modeling](action-modeling.md) owns action semantics; [Inference](inference.md) owns serving; [Evaluation](evaluation.md) owns the protocol; [VLABench codebase](../../papers/vlabench/codebase.md) owns the evaluator; [planning and control](../../foundations/decision-making/planning-and-control.md) owns receding-horizon concepts.

## Canonical identity and lineage

The policy surface is `eval_vlabench/main.py:VLABenchPolicy`, a `VLABench.evaluation.model.policy.base.Policy` in end-effector control mode, driven by `VLABench.evaluation.evaluator.Evaluator` with the official track configs, one persistent `deploy/client.py:Client` per worker. [XR1-CODE-EVAL-VLABENCH]

## Observation and action contract

### Input

- `obs["rgb"]` has four 480x480 views; the client uses `[2]` (front) as Ego, `[0]` (second) as Base, `[3]` (wrist) as Left-Wrist, resized to `image_size=480`.
- `obs["ee_state"]` = `[xyz, quaternion, gripper]`; state = `[xyz - (0, -0.4, 0.78), euler(quaternion) wrapped, gripper]`, zero-padded to 60.
- Instruction = `env.task.get_instruction()`.
- Prompt = the three titled views + "Generate robot actions for the task:\n{instruction} /no_cot" + pre-filled `<cot></cot>`.

### Output and execution

- Request returns `(10, 60)`; the client keeps `[:, :7]` and the first `replan_steps=5` rows.
- For each row: `current[:6] += action[:6]`; Euler wrapped; gripper state = `0.04` (open) on both fingers if `action[6] >= 0.2` else `0.0`.
- The evaluator converts the target pose to joints through the benchmark's IK (`get_qpos_from_ee_pos`) and steps once per policy step (`max_substeps=1`).
- Episode cap 200 steps (100 for `select_poker` / `select_painting`, 300 for `add_condiment`); success ends the episode early. [XR1-CODE-EVAL-VLABENCH; VLAB-CODE, `evaluator/base.py`, `configs/task_config.json`]

### Fixed inference defaults behind the reported numbers

`robot_type=vlabench_choice`, `state_dim=60`, `action_dim=7`, `action_chunk_size=10`, `replan_steps=5`, `image_size=480`, `cot=False`, `gripper_threshold=0.2`, `gripper_open_value=0.04`, `request_seed=42`, `position_offset=(0, -0.4, 0.78)`. [XR1-CODE-EVAL-VLABENCH, `VLABenchPolicyArgs`]

## Official server semantics

`deploy/server.py` loads the HF model with `trust_remote_code=True`, flash-attention 2, bf16, binds one port, and serves one pickle-framed request at a time; `deploy.sh` starts `num_ports` servers round-robin over `num_gpus` inside a tmux session. The client reconnects forever on refusal. There is no health endpoint; readiness = TCP accept. [XR1-CODE, `deploy/server.py`, `scripts/deploy.sh`, `deploy/client.py`]

## Canonical closed-loop pattern

```text
for each (track, task, episode config):
  env = load_env(task, episode_config, random_init=False, eval=False, run_mode="eval")
  plan = []
  while step < cap and not success:
     if plan empty: chunk = server(obs) ; plan = integrate(chunk[:5])
     pos, euler, gripper = plan.popleft()
     qpos = IK(pos, euler) ; env.step([qpos, gripper])
  record success, consumed_step, intention_score, progress_score
```

[XR1-CODE-EVAL-VLABENCH; VLAB-CODE]

## Diagnostics and failure signatures

| Symptom | Likely cause | Where |
|---|---|---|
| Every episode ends at `consumed_step` 0 with an exception | dead server, processor mismatch, missing `VLABENCH_ROOT` | serving chain |
| Robot drifts while commanded to hold | IK/controller behaviour under a null delta (open upstream issue) | simulator [VLAB-ISSUE-80] |
| `Failed to converge after 99 steps` warnings | unreachable commanded pose | policy output, benign per maintainers |
| IS = 0 on a successful episode | evaluator defect, not policy | [VLAB-ISSUE-82] |
| Gripper logic inverted | state bit polarity (1 = closed in the observation) versus action bit (1 = open) | [VLAB-ISSUE-88] |

## Safety boundary

Simulation only; no real-robot deployment surface is part of this entry. The runtime client for real robots (`mibot/server/runtime/client.py`) is a different protocol and out of scope for VLABench claims.

## Sources

[XR1-CODE-EVAL-VLABENCH] `eval_vlabench/main.py`, `eval_vlabench/dispatch.py`; [XR1-CODE] `deploy/server.py`, `deploy/client.py`, `scripts/deploy.sh`; [VLAB-CODE] `VLABench/evaluation/evaluator/base.py`; [VLAB-ISSUE-80]; [VLAB-ISSUE-82]; [VLAB-ISSUE-88].
