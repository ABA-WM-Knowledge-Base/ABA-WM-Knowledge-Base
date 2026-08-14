---
id: world-model-kb.papers.v-jepa-2.reproduction
title: V-JEPA 2 Reproduction State and Experiment Contracts
kind: record
status: maintained
last_updated: 2026-08-14
owners:
  - AIBuildAI world-model group
---

# V-JEPA 2 Reproduction State and Experiment Contracts

## Retrieval metadata

**Relevant queries:** V-JEPA 2 reproduced, pretrain status, AC DROID finetune, Franka CEM, SSv2 probe, vjepa_2_1, checkpoint download, or acceptance criteria.

**Knowledge provided:** all-not-attempted status, documented commands bound to real repo paths, variant-specific acceptance, and hardware boundaries. No training or inference was run for this entry.

**Related pages:** [`codebase.md`](codebase.md) owns the released call graph and gaps; [`paper.md`](paper.md) owns reported values; [evaluation methodology](../../foundations/data-and-evaluation/evaluation-methodology.md) owns comparison validity.

## 1. Current execution state

| Surface | Evidence state | Recorded evidence | Permitted claim |
|---|---|---|---|
| Paper / Foundation protocols | source inspected | [OBJ-VJEPA2-2025]; [VJ2-PAPER] | Documented paper evidence only. |
| Repository at pin | source inspected | [VJ2-CODE] `204698b45b3712590f06245fbfba32d3be539812` (2026-03-23) | Static graph documented, not executed. |
| V-JEPA 2 pretrain (1M+ h) | **not attempted** | none | No local encoder trained. |
| Frozen SSv2 / EK100 / K400 | **not attempted** | none | 77.3 / 39.7 remain paper evidence. |
| PerceptionTest 8B LLM align | **not attempted** | none | 84.0 remains paper evidence. |
| V-JEPA 2-AC DROID finetune | **not attempted** | none | No AC predictor trained locally. |
| Notebook CEM / Franka | **not attempted** | none | Tables 2-3 remain paper evidence. |
| V-JEPA 2.1 train / eval | **not attempted** | none | Release-note evidence only. |

Static inspection is not inference reproduction. No row may be promoted without an immutable run record.

## 2. Reproduction vocabulary

- **Documented:** a pinned paper or repository describes a behavior.
- **Source inspected:** paper pages or code paths were reconciled.
- **Artifact reachable / verified:** URL identity vs downloaded SHA256.
- **Executed:** a command completes with retained artifacts.
- **Metric reproduced:** pinned checkpoint + protocol within predeclared tolerance.
- **Paper result reproduced:** model, data, code, evaluator, CEM budget, and aggregation match the named table **and** the named variant.

Variant tag `{V-JEPA-2 | V-JEPA-2-AC | V-JEPA-2.1}` is mandatory on every record.

## 3. Artifact and environment boundary

Full action-free pretrain (VideoMix22M, 252K + cooldown; 64×384×384 counterfactual ~60 GPU-years) is outside local scope. Smoke evaluation should start from released ViT-g weights. AC post-train is <62 h DROID but still needs those videos and a Franka or authorized sim. Robot cells use **10 trials**; binomial CIs are wide. [VJ2-PAPER, Sec. 3-4, Tables 2-3]

Planner code is in **notebooks**, not a CLI. A reproduction that invents `eval_franka.py` is not executing author code. [VJ2-CODE, `VJEPA-GAP-01`]

## 4. Released commands: documented, not executed

### 4.1 Clone and pin

```bash
git clone https://github.com/facebookresearch/vjepa2.git
cd vjepa2
git checkout 204698b45b3712590f06245fbfba32d3be539812
# install per README; record a resolved lock externally
```

### 4.2 Action-free pretrain (documented; not a local target)

Entry: `app/vjepa/train.py` with:

- `configs/train/vitg16/pretrain-256px-16f.yaml`
- then `configs/train/vitg16/cooldown-384px-64f.yaml`

Exact CLI flags follow the README at this commit (typically a torchrun / submitit launcher wrapping `app/vjepa/train.py`). Record the resolved yaml merge. Do not claim Table 2 from this command. [VJ2-CODE]

### 4.3 Frozen understanding eval (documented)

Configs at this pin:

```text
configs/eval/vitg-384/ssv2.yaml
configs/eval/vitg-384/ek100.yaml
configs/eval/vitg-384/k400.yaml
```

Launchers live under `evals/video_classification_frozen/` and `evals/action_anticipation_frozen/`. **Executed** smoke: checkpoint loads; probe forward pass completes; metric finite. **Metric reproduced:** SSv2 top-1 within epsilon of **77.3**, EK100 recall-at-5 within epsilon of **39.7**, with the yaml's crop/frames. PerceptionTest **84.0** requires the 8B LLM alignment path, which is **not** these frozen yamls. [VJ2-PAPER, Sec. 4; VJ2-CODE, `VJEPA-GAP-07`]

### 4.4 V-JEPA 2-AC (documented)

```text
app/vjepa_droid/train.py
configs/train/vitg16/droid-256px-8f.yaml
src/models/ac_predictor.py
```

Bind frozen encoder SHA (V-JEPA 2 ViT-g, **not** 2.1 unless that is the question). Record DROID hours actually used versus the paper's **<62 h**. Acceptance: training loss decreases; held-out next-z error is finite. This is **not** Table 2. [VJ2-CODE]

### 4.5 Latent planning (documented notebook)

```text
notebooks/utils/mpc_utils.py
notebooks/utils/world_model_wrapper.py
```

Record CEM samples, iterations, horizon, goal-image encoding, camera, and trial IDs. Table 3's 800-sample / 16 s/action protocol is the 2-AC arm; the Cosmos video WM 80-sample / 10-iter / H=1 / 4 min/action arm is an **external** baseline, not a file in this repo. [VJ2-PAPER, Table 3; VJ2-CODE, `VJEPA-GAP-05`]

**Metric reproduced** for Table 2 only if variant is 2-AC, encoder is frozen ViT-g, objects/labs/trials match, and success is logged as raw 10-trial vectors (cup/box × reach/grasp/reach-with-object/pick-place).

### 4.6 V-JEPA 2.1 (documented; separate)

```text
app/vjepa_2_1/train.py
app/vjepa_2_1/models/vision_transformer.py
```

Do not compare 2.1 probe numbers to Table 2 robot cells. [VJ2-CODE]

## 5. Acceptance criteria summary

| Experiment | Variant | Executed | Metric reproduced |
|---|---|---|---|
| Frozen SSv2 / EK100 | V-JEPA 2 | checkpoint + eval yaml | 77.3 / 39.7 ± ε |
| PerceptionTest | V-JEPA 2 + 8B LLM align | alignment stack present | 84.0 ± ε |
| AC next-z | V-JEPA 2-AC | droid trainer completes | val error ≤ paper + ε |
| Franka Table 2 | V-JEPA 2-AC | 10 trials × cells logged | within predeclared CI of Table 2 |
| Table 3 latency | 2-AC vs video WM | timed CEM on 4090-class GPU | 16 s vs 4 min qualitative match |
| Pretrain from scratch | V-JEPA 2 | not required for smoke | out of local scope |
| 2.1 encoder | V-JEPA 2.1 | 2.1 trainer or eval | **not** Table 2 |

## 6. Hardware boundary

| Regime | Expectation |
|---|---|
| Frozen probe inference | 1× high-memory GPU |
| AC finetune (<62 h) | 1–8 GPUs depending on batch |
| 1M+ h pretrain + cooldown | large cluster; ~60 GPU-year full-res counterfactual |
| Table 3 timing | RTX 4090-class for latency claims |
| Franka eval | real hardware or authorized sim; two-lab protocol |

## 7. Mechanism reproduction (2-AC)

The minimum causal robot experiment is not “the encoder is good.” Compare:

| Variant | Encoder | Predictor | Planner |
|---|---|---|---|
| Action-free only | V-JEPA 2 | none | none — **no Franka number** |
| 2-AC released | frozen ViT-g | interleaved `(a,s,z)` | notebook CEM + image goals |
| 2-AC shuffled actions | same | same | shuffled a |
| 2.1 encoder + AC | 2.1 weights | 2-AC recipe | same CEM |
| Video WM baseline | n/a | n/a | Table 3 Cosmos protocol |

A transfer claim is falsified if pick-place is quoted from an action-free or 2.1 checkpoint, or if shuffled actions match planned actions.

## 8. Run-record template

```text
Experiment ID:
Variant tag: {V-JEPA-2 | V-JEPA-2-AC | V-JEPA-2.1}
Encoder SHA256 + recipe path:
AC predictor SHA256 (if any):
Config yaml hashes:
CEM samples / iters / horizon / ms-per-action:
Goal encoding (image sub-goal vs other):
Camera / lab / extrinsics:
Trials (raw vector, not only mean):
Metrics vs paper table:
Evidence conclusion:
```

No run is registered. Do not attribute Franka results to the action-free encoder. Log Lab 1 vs Lab 2 separately (box pick-place 80% vs 50% in Table 2) and record whether pick-place used three image sub-goals (4 / 10 / 4 steps). [VJ2-PAPER, Table 2, Sec. 4.2]

## Sources

- [OBJ-VJEPA2-2025]; [VJ2-PAPER]; [VJ2-CODE]; [VJ2-PROJECT].
