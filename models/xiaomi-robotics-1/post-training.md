---
id: world-model-kb.models.xiaomi-robotics-1.post-training
title: Xiaomi-Robotics-1 Post-Training and Benchmark Fine-Tunes
kind: model
status: maintained
last_updated: 2026-08-21
owners:
  - AIBuildAI world-model group
---

# Xiaomi-Robotics-1 Post-Training and Benchmark Fine-Tunes

## Retrieval metadata

**Relevant queries:** post-training, fine-tune, warm start, benchmark checkpoint, VLABench fine-tune recipe, RoboCasa fine-tune, RoboCasa365, RoboDojo, real-robot adaptation, less than 10 hours per task, embodiment alignment, instruction alignment, importer, exporter.

**Knowledge provided:** the two post-training stages the report describes, the per-benchmark adaptation facts, the minimal-data real-robot adaptation evidence, and the format boundary between the trainer and the served checkpoints that any fine-tune must cross.

**Related pages:** [Training](training.md) owns defaults; [Data](data.md) owns mixtures; [Evaluation](evaluation.md) owns numbers; [Codebase](codebase.md) owns the importer/exporter surfaces; [Xiaomi-Robotics-1 paper entry](../../papers/xiaomi-robotics-1/paper.md) owns the report's evidence.

## 1. Select the branch before selecting a recipe

| Branch | Start from | Format | Notes |
|---|---|---|---|
| New embodiment / task (report's intended use) | `Xiaomi-Robotics-1-5B/model_states.pt` | trainer | `xr1/README.md` recipe: JSON episodes + stats in the data config, `RESOURCE_GPU=N bash scripts/train.sh` |
| VLABench campaign (aibuildai) | `Xiaomi-Robotics-1-VLABench` imported to trainer format with the 15 training-only tensors filled (12 choice-head tensors and the `<a_i>`/`<score>` embeddings from the base; the tied `lm_head` from the HF embedding) | trainer -> HF export | Keeps the 59.1 starting point; every node is compared to it |
| Reproduce the VLABench fine-tune from the base | `-5B` | trainer | Recipe undisclosed; expect to search steps/batch/lr |

[XR1-CODE-XR1-README; XR1-HF-5B; XR1-HF-VLABENCH]

## 2. The report's two-stage paradigm

Stage 1 pre-training (breadth) on embodiment-free UMI with scene-transition captions; Stage 2 post-training (alignment) on ~10K h of cross-embodiment data along two axes: embodiment alignment (map the generic action-generation ability onto real robots via relative delta end-effector poses and aligned frames) and instruction alignment (imperative instructions instead of transition descriptions). The released 5B is the output of Stage 2. [XR1-TR, Sec. 4]

## 3. Benchmark fine-tunes (state)

| Benchmark | Data | Disclosed recipe | Result | Checkpoint |
|---|---|---|---|---|
| RoboCasa | official 300 synthetic demos/task, 24 tasks | none | 74.5 avg SR (paper); 74.21 over 2,400 episodes (card) | `-RoboCasa`, `robocasa_mg`, crop 0.95 |
| RoboCasa365 | 32,043 trajectories, 300 task classes | 120k steps, batch 512, lr 3e-5, 4-frame history, 16-step chunks | 57.4 avg (80.2 atomic / 57.1 composite-seen / 32.1 composite-unseen) | `-RoboCasa365` |
| VLABench | official Track-1 set, 10 x 500 | CoT NTP at 50 %; rest undisclosed | 59.1 / 70.3 / 69.9 (SR/PS/IS) | `-VLABench`, `vlabench_choice` |
| RoboDojo | 3,500 official samples | 60k steps, batch 256, lr 1e-5, no history | 20.07 avg score / 13.93 % SR | none released |

[XR1-TR, Tables 2-5; XR1-ISSUE-4; XR1-HF-ROBOCASA; XR1-HF-VLABENCH]

## 4. Real-robot adaptation evidence

With < 10 h of demonstrations per task on average, XR-1 reaches 75 % success (90 % progress) across phone packing, printer refilling, laundry loading, and box packing, versus pi0.5 at 40 % (66 % progress); with < 40 h, 85 % versus 53 %. Out-of-the-box tasks (shoe storage, bag packing, table organization, sofa tidying) are reported qualitatively. [XR1-TR, Sec. 5.5 and Table 6]

## 5. Public post-training code surface

`xr1/`: Hydra configs (`data=`, `model=`, `trainer=`), `JsonDataset` (bimanual JSON + three mp4s), `CustomCollate` (packing), `BaseRunner` (strict load, FusedAdam groups), `XR1` module, `tools/weight_convert.py` (HF -> trainer `model_states.pt` by prefixing `model.`), `mibot/server/deploy.py` (serves `last.ckpt` with the data config's stats). Missing for VLABench: a dataset matching the served conventions, the CoT loss, and the trainer -> HF direction; the aibuildai deploy adds `mibot/ext/vlabench_data.py`, `mibot/ext/xr1_cot.py`, `import_hf_to_xr1.py`, `export_xr1_to_hf.py`. [XR1-CODE; deploy tree]

## 6. Domain-adaptation decision procedure

1. Fix the served conventions first (robot type, chunk, deltas, state frame, views) from the target client.
2. Choose the start checkpoint by format and heads (Section 1).
3. Build the data path to those conventions; verify by exporting an untrained copy and scoring it equals the released checkpoint's L2.
4. Measure s/step and memory in a 5-step smoke; size `max_steps` and `save_interval` together.
5. Export, serve, score; compare paired episodes against the anchor.

## 7. Controllable post-training levers

| Lever | Surface | Expected signal | Risk |
|---|---|---|---|
| Warm start choice (released fine-tune vs base) | `model.params.pretrained` | Start at 59.1 vs unknown | Base route needs the undisclosed recipe |
| CoT on/off | `cot_prob`, `cot_coefficient` | Track 3/4 | Label quality |
| Partial freezing (DiT-only, VLM-frozen) | `requires_grad_` | Speed; may cap language tracks | |
| Stats re-estimation | stats tool + processor export | Conditioning | Warm-start mismatch |

## Sources

[XR1-TR] Sec. 4-5, Tables 2-6; [XR1-CODE-XR1-README]; [XR1-CODE]; [XR1-ISSUE-4]; [XR1-HF-5B]; [XR1-HF-VLABENCH]; [XR1-HF-ROBOCASA].
