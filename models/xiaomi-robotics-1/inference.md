---
id: world-model-kb.models.xiaomi-robotics-1.inference
title: Xiaomi-Robotics-1 Inference and Serving Guide
kind: guide
status: maintained
last_updated: 2026-08-21
owners:
  - AIBuildAI world-model group
---

# Xiaomi-Robotics-1 Inference and Serving Guide

## Retrieval metadata

**Relevant queries:** serve Xiaomi-Robotics-1, deploy/server.py, ports 10086, num_ports num_gpus, tmux model_servers, VRAM 13 GB, latency 70 ms, flash-attn 2.8.3, torch 2.8.0 cu128, transformers 4.57.1, EGL, MUJOCO_GL, eval wall clock, dead server, TCP probe.

**Knowledge provided:** the environments and commands that serve a checkpoint for benchmark evaluation, resource references, the failure classifier for serving and evaluation, and the reproducibility fields to record.

**Related pages:** [Codebase](codebase.md) owns file locations; [Policy](policy.md) owns the client loop; [Reproduction](reproduction.md) owns executed runs; [Evaluation](evaluation.md) owns protocols.

## Backend capability map

| Backend | Checkpoint | Used for | Text output |
|---|---|---|---|
| HF `deploy/server.py` (env `mibot`) | HF-format dir (released fine-tunes or an export) | RoboCasa / RoboCasa365 / VLABench evals | none |
| Trainer runtime `mibot/server/deploy.py` (env with `xr1` installed) | `last.ckpt/` + `config.py` | real-robot runtime with action prefix | none |

[XR1-CODE]

## Environment isolation (documented)

- `mibot` (serving): Python 3.12, `torch==2.8.0 torchvision==0.23.0 torchaudio==2.8.0` (cu128), `transformers==4.57.1`, `flash-attn==2.8.3`; `apt: libegl1 libgl1 libgles2`. [XR1-CODE, `docs/DEPLOYMENT.md`]
- `vlabench` (client + simulator): Python 3.10, VLABench `-e . --no-deps` after `requirements.txt`, `mujoco==3.2.2 mujoco-mjx==3.2.2 dm_control==1.0.22` force-reinstalled, `torch==2.8.0` cu128, `transformers==4.57.1 tyro tqdm pillow openai`, `rrt-algorithms@e51d95ee…`; `MUJOCO_GL=egl PYOPENGL_PLATFORM=egl MUJOCO_EGL_DEVICE_ID=0 TOKENIZERS_PARALLELISM=false`; `VLABENCH_ROOT` exported. [XR1-CODE-EVAL-VLABENCH]
- Both environments must read the same model directory (the client loads the processor from it).

## Route A: HF server for benchmark evaluation

```bash
hf download XiaomiRobotics/Xiaomi-Robotics-1-VLABench --local-dir "$MODEL_PATH"
bash scripts/deploy.sh "$MODEL_PATH" 8 8          # 8 servers on ports 10086-10093, round-robin over 8 GPUs, tmux session model_servers
# client, other terminal, env vlabench:
bash scripts/launch_vlabench.sh 8 ./eval_vlabench/eval_logs "$MODEL_PATH"
```

Per-server: one model copy (~13 GB VRAM), single-threaded request loop, ~70 ms per request on an RTX 4090. Readiness: the port accepts a TCP connection; startup = flash-attn import + a 10 GB load (about a minute on local NVMe). A server can be started directly without tmux: `CUDA_VISIBLE_DEVICES=<i> python deploy/server.py --model <dir> --port <p>`; inside the process the device is `cuda:0`. [XR1-CODE, `scripts/deploy.sh`, `deploy/server.py`; XR1-ISSUE-12; XR1-CODE-EVAL-VLABENCH]

Smoke: `NUM_EVAL_EPISODES=1 bash scripts/launch_vlabench.sh 1 ./eval_logs_smoke "$MODEL_PATH"` (one worker, one episode per task). [XR1-CODE-EVAL-VLABENCH]

## Route B: trainer runtime server

`bash xr1/scripts/deploy.sh <run dir> <num_ports> <num_gpus>` serves `last.ckpt`; state normalization and action denormalization use the data config's stats; requests carry the real-robot state dict and an optional `(N, 60)` prefix. Not used by any benchmark client. [XR1-CODE, `xr1/scripts/deploy.sh`, `mibot/server/runtime/*.py`]

## Platform and resource considerations

| Item | Reference |
|---|---|
| VRAM per server | ~13 GB (maintainer) |
| Latency | ~70 ms per request on RTX 4090; ~300 ms end-to-end tolerated on the real robot with async inference |
| Episode wall clock (VLABench) | dominated by MuJoCo + IK + rendering; VLABench's README: 30 min to 1 h per task (50 episodes) per process, i.e. roughly 40-70 s per episode; model time about 3 s per episode at 5 replans of 10 |
| Full protocol | 2,460 episodes: about 4-5 h on 8 workers (estimate) |
| Rendering | EGL on the GPU; CPU (osmesa) rendering was 2.4x slower on a comparable MuJoCo benchmark |

[XR1-ISSUE-12; VLAB-CODE, README]

## Failure classifier

| Observation | Class | Action |
|---|---|---|
| Client hangs at "connecting" | dead/late server (client retries forever) | probe ports before dispatch; read the server log |
| `KeyError: Robot type ... not found` | wrong model dir for the processor | serve and load the same dir |
| `Decoded action horizon ... smaller than plan horizon` | processor stats with K < 5 | fix `action_config` |
| `VLABENCH_ROOT is not set` | env | export it in the client env |
| All episodes `consumed_step` 0 with errors | serving chain or sim env | not a policy zero |
| IK convergence warnings | unreachable commanded pose | benign, policy-quality signal |
| CPU fallback (slow, 0 % GPU) | wrong CUDA device under `CUDA_VISIBLE_DEVICES` | assert `is_cuda` after load |

## Reproducibility artifact fields

model dir + revision (or export provenance), VLABench commit, track, episodes per task, client args (chunk, replan, image size, cot, seed), server count, per-track `metrics.json`, per-task `detail_info.json`, `dispatch_manifest.json`, wall clock, GPU type.

## Sources

[XR1-CODE] `docs/DEPLOYMENT.md`, `scripts/deploy.sh`, `deploy/server.py`; [XR1-CODE-EVAL-VLABENCH]; [XR1-ISSUE-12]; [VLAB-CODE] README.
