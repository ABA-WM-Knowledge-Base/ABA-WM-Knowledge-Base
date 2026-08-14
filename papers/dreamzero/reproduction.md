---
id: world-model-kb.papers.dreamzero.reproduction
title: DreamZero Reproduction State and Experiment Contracts
kind: record
status: maintained
last_updated: 2026-08-14
owners:
  - AIBuildAI world-model group
---

# DreamZero Reproduction State and Experiment Contracts

## Retrieval metadata

**Relevant queries:** DreamZero reproduced, socket_test_optimized_AR, DreamZero-DROID, Flash, 7 Hz, embodiment YAML, not attempted.

**Knowledge provided:** inspection-only state, documented multi-GPU commands, embodiment pin rules. No training or inference executed.

**Related pages:** [`codebase.md`](codebase.md); [`paper.md`](paper.md); [evaluation methodology](../../foundations/data-and-evaluation/evaluation-methodology.md).

## 1. Current execution state

| Surface | Evidence state | Recorded evidence | Permitted claim |
|---|---|---|---|
| Paper | source inspected | ar5iv HTML of arXiv:2602.15922; Tables 1-4 | Numbers inspected; Table 4 VLA cells flagged. |
| GitHub | source inspected | tree at `ab790c198fbce33503358efbbd4187ce9a89adf3`; README | Paths and flags real. |
| Hub DROID | metadata inspected | `GEAR-Dreams/DreamZero-DROID` | Inner hashes not registered. |
| Hub AgiBot | metadata inspected | `GEAR-Dreams/DreamZero-AgiBot` ~45 GB | Not interchangeable with DROID. |
| WebSocket server | not attempted | documented 2-GPU command | No MP4. |
| DROID training | not attempted | `max_steps=10` default noted | No 100K run. |
| Flash / TRT | not attempted | Table 1/3 documented | No 150 ms measurement. |
| Real-robot tables | not attempted | paper-only | 62.2% / 39.5% / 22.5% not reproduced. |

Never train or infer in this KB session. WAM weights are **not** a universal policy.

## 2. Reproduction vocabulary

- **Documented:** a pinned paper or repository describes a behavior.
- **Source inspected:** relevant pages or files were reconciled.
- **Executed:** a command completes with raw artifacts.
- **Metric reproduced:** pinned checkpoint, embodiment YAML, and protocol yield the declared metric within a predeclared tolerance.

## 3. Artifact and environment boundary

Minimum: 2 GPUs, Python 3.11, CUDA 12.9+, flash-attn. Optional Transformer Engine / TensorRT on GB200. DROID LeRobot dump ~131 GB. Wan2.1-I2V-14B-480P ~28 GB. AgiBot ckpt ~45 GB. First WebSocket calls warm up for minutes. [DZ-CODE README]

AgiBot 62.2/39.5 need the private 500 h mix and 4-robot eval site — **not reconstructable** from DROID Hub alone. Sanity `max_steps=10` is not the paper.

## 4. Commands documented, not executed

```bash
git clone https://github.com/dreamzero0/dreamzero.git
cd dreamzero
git checkout ab790c198fbce33503358efbbd4187ce9a89adf3
conda create -n dreamzero python=3.11
pip install -e . --extra-index-url https://download.pytorch.org/whl/cu129

hf download GEAR-Dreams/DreamZero-DROID --repo-type model --local-dir <ckpt>
CUDA_VISIBLE_DEVICES=0,1 python -m torch.distributed.run --standalone --nproc_per_node=2 \
  socket_test_optimized_AR.py --port 5000 --enable-dit-cache --model-path <ckpt>
python test_client_AR.py --port 5000
```

Training (paper-scale requires overriding `max_steps`):

```bash
bash scripts/train/droid_training.sh
# paper-closer DiT: scripts/train/droid_training_full_finetune_wan21.sh
# AgiBot / YAM: scripts/train/agibot_training.sh / yam_training.sh
```

Wan2.2 5B (`droid_training_wan22.sh`) is **not** the 14B paper agent. Sim eval via `eval_utils/run_sim_eval.py` needs an external API host; that is not the paper's real-robot protocol.

## 5. Minimum smoke contract

Pinned commit; Hub id (DROID **xor** AgiBot, not mixed); hashed weights; matching `*_relative.yaml`; 2-GPU server accepts one observation; writes MP4; logs latency and cache flag. Not Table 2/3.

## 6. Table contracts

**Table 1:** cumulative speedups; record GPU SKU, CFG parallel, DiT cache, compile, kernels, NVFP4, Flash. Do not merge README 0.6-3 s.

**Table 3:** table-bussing progress; 4-step 83%±6.1% at 350 ms versus naive 1-step 52%±10.2% versus Flash 74%±10.1% at 150 ms.

**Table 2:** 9 unseen tasks, video-only 10-20 min, no target actions; CIs overlap.

**Table 4:** diverse vs repetitive; 14B vs 5B; VLA row uses **prose 0%**, not ar5iv `50%±0.0%`.

Always record embodiment YAML and camera order (`exterior_image_1_left`, `exterior_image_2_left`, `wrist_image_left` on DROID).

## 7. Identity checklist

| Check | Required value | Status |
|---|---|---|
| Paper | arXiv:2602.15922 | source inspected |
| Commit | `ab790c198fbce33503358efbbd4187ce9a89adf3` | source inspected |
| Hub | DROID **xor** AgiBot | not executed |
| Embodiment YAML | matching robot | documented |
| `max_steps` | 100K for paper train | documented |
| Latency flags | cache / Flash / TRT / GPU | not executed |
| Not universal policy | adapters required | documented |

## 8. Run-record template

```text
Experiment ID:
Commit:
Hub id (DROID vs AgiBot vs YAM LoRA):
Embodiment YAML:
enable-dit-cache / Flash / TRT:
nproc:
Latency vs Table 1/3:
Success / task progress:
Evidence conclusion:
```

No run record is registered.

## 9. Non-goals for this KB session

No train, no infer, no GB200 job. Do not call DreamZero a universal policy. Do not mix AgiBot and DROID cameras.

## 10. Training and metric reproducibility boundary

| Regime | Publicly recoverable | Missing for exact reproduction |
|---|---|---|
| DROID WebSocket smoke | 2-GPU `socket_test_optimized_AR.py`, Hub DROID card | inner SHA256, YAML `droid_relative`, camera order |
| AgiBot Table seen/unseen | paper protocol 80 rollouts | private 500 h mix, 4-robot site, AgiBot Hub ~45 GB hash |
| Table 1 latency | Flash recipe flags | GB200 SKU, NVFP4, TRT engine hash; do not merge README 0.6–3 s |
| Table 3 table-bussing | 4-step 83%±6.1% vs Flash 74%±10.1% | 40 h post-train mix, 10 rollouts/task |
| Table 4 diverse vs repetitive | 14B vs 5B | VLA row uses **prose 0%**, not ar5iv `50%±0.0%` |
| Cross-embodiment | `yam_relative.yaml`, play LoRA | 72 video-only trajectories, 20/12 min mix |
| Default train script | `droid_training.sh` | **`max_steps=10` is sanity**, not 100K paper train |

DROID Hub weights cannot reconstruct AgiBot 62.2% / 39.5%. Mixing camera keys is a negative-transfer bug, not evidence against WAM.

## 11. Acceptance checks that must not be skipped

1. Hub id is DROID **xor** AgiBot, never both in one run record.
2. `max_steps=10` is labeled sanity if used.
3. Table 4 VLA diverse progress follows paper prose (0%), not the conflicting ar5iv cell.
4. 7 Hz closed-loop and README server latency remain separate surfaces.
5. Wan2.2 5B (`droid_training_wan22.sh`) is not the 14B paper agent.

## Sources

- [DZ-PAPER], [DZ-CODE], [DZ-HF-DROID], [DZ-HF-AGIBOT].
