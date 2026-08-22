---
id: world-model-kb.models.xiaomi-robotics-1.limitations
title: Xiaomi-Robotics-1 Failure Modes and Optimization Guardrails
kind: model
status: maintained
last_updated: 2026-08-21
owners:
  - AIBuildAI world-model group
---

# Xiaomi-Robotics-1 Failure Modes and Optimization Guardrails

## Retrieval metadata

**Relevant queries:** limitation, undisclosed recipe, capability boundary, evaluator defect, train/eval asymmetry, gripper polarity, checkpoint format trap, transformers pin, deployment risk, what must not be inferred.

**Knowledge provided:** documented and structurally inferred boundaries, claims that must be rejected, confounders in the evaluation chain, and deployment risks specific to post-training this model on VLABench.

**Related pages:** [Evaluation](evaluation.md) owns scores; [Training](training.md) owns recipes; [Reproduction](reproduction.md) owns execution observations; [open problems](../../foundations/research-frontiers/open-problems.md) owns field-level unknowns.

## 1. Model-card failure envelope

The technical report has no standalone limitations section and the model cards list none; boundaries below are inferred from the protocols, the code, and upstream issues, and are labelled as such. [XR1-TR; XR1-HF-VLABENCH]

## 2. Capability-boundary register

| Surface | Known boundary | Claim that must be rejected |
|---|---|---|
| VLABench generalization | cross-category 53.0, common-sense 48.4 versus in-distribution 75.6 | "XR-1 solves VLABench" [XR1-TR, Table 4] |
| Recipe | VLABench fine-tune steps/batch/lr undisclosed | "The framework defaults are the recipe" [XR1-TR; XR1-CODE] |
| Ablations | none published | "The choice heads / frequency loss / CoT contribute X points" |
| Inference CoT | the HF model generates no text | "/cot at inference adds reasoning" [XR1-HF-VLABENCH] |
| Scaling | validation action MSE, not closed-loop success | "10B would score higher on VLABench" [XR1-TR, Sec. 6] |
| Real-robot adaptation | 4 tasks, < 10 h each, in-house robots | Transfer to any embodiment without post-training |
| Released sizes | 5B only | 2B/10B behaviour |

## 3. Data and supervision risks

- Scripted demonstrations: the VLABench training set is motion-planned, low-diversity per task (500 episodes, templated instructions, 128 strings); semantic-instruction generalization must come from the backbone, not the data. [VLAB-PAPER; VLAB-DATA-LEROBOT]
- Self-generated CoT labels (aibuildai) are unvalidated; ERVLA shows that the wrong CoT content (abstract goal/plan fields, bounding boxes in their setting) can reduce success. [ERV-PAPER, Table 1]
- Gripper bit polarity differs between observation state and action in the benchmark's own data; "fixing" one side breaks train/serve consistency. [VLAB-ISSUE-88]

## 4. Evaluation confounders

- Evaluator defects: IS = 0 on successes, PS formula drift, null-action drift. [VLAB-ISSUE-82; VLAB-ISSUE-55; VLAB-ISSUE-80]
- Train/eval image-resolution asymmetry (160k px jittered at training, 90k px at serving) is part of the released pipeline; changing one side alone is an intervention, not a fix. [XR1-CODE]
- Episode-count drift: "2,500" in prose vs 2,460 executable. [XR1-TR; VLAB-CODE]
- Unpinned VLABench commit in Xiaomi's README; this entry pins `cf588fe6…`. [XR1-CODE-EVAL-VLABENCH; VLAB-CODE]
- Seed-dependent sampling (request seed 42, applied per request by `torch.manual_seed` in the HF modeling code); a different seed is a different protocol. Even at a fixed seed two runs differ by GPU kernel nondeterminism: measured 1/50 success flips and 8/50 step-count differences on track 1 on one host; across hosts (A100 PCIe/driver 550 vs A100 SXM4/driver 570) 14/250 episodes flipped while the 5-track average moved 0.8 pp. Compare candidates on the same host type.
- Normalization stats are load-bearing at the 1e-7 level: an export whose mean/std passed through float32 and 6-decimal rounding flipped 8/50 track-1 episodes against bit-identical weights. Carry the processor stats verbatim in float64.

## 5. Training, system, and deployment risks

- **Format trap:** HF fine-tunes are not loadable by the strict trainer (15 training-only tensors missing: choice heads, `<a_i>`/`<score>` embeddings, untied `lm_head`); trainer outputs are not servable by the HF eval path; two different servers and wire protocols exist. [XR1-CODE; XR1-HF-VLABENCH; XR1-HF-5B]
- **Convention trap:** the public `JsonDataset` conventions differ from the VLABench checkpoint's (joint state vs pose state; EE-frame axis-angle vs world-frame Euler deltas; gripper delta vs absolute). [XR1-CODE; XR1-CODE-EVAL-VLABENCH]
- **Clipping trap:** the trainer's state quantile normalizer clips to [-1, 1]; Euler angles in (-pi, pi] would fold; the served model receives raw state. [XR1-CODE, `io.py:normalize_quantile`]
- **Packing trap:** `MAX_LENGTH` silently drops samples. [XR1-CODE]
- **Save trap:** Lightning saves at `save_interval` multiples and once at the end of a fit that reaches `max_steps` (`save_last=True`; measured: a 5-step smoke with `save_interval` 1,000,000 still wrote a 64 GB `last.ckpt/`); no save on SIGTERM or budget kill. [XR1-CODE, `tools/train.py`; smoke 2026-08-21]
- **Pin trap:** `transformers==4.57.1` exactly; flash-attn 2 required. [XR1-CODE-XR1-README]
- **Client trap:** the eval client retries a dead port forever. [XR1-CODE, `deploy/client.py`]
- **Memory:** ~13 GB VRAM per server; training at batch 48 per rank x 8 ranks (ZeRO-2, bf16, gradient checkpointing) runs at ~7 s/step on A100-80GB without OOM (batch 32: ~5 s/step); nvidia-smi shows ~80 GB reserved at both batches because the caching allocator grows to the card, so the real headroom at batch 48 is unmeasured (`max_memory_allocated` was not captured). [XR1-ISSUE-12; smoke `xr1-smoke-lambda-20260821-01`]

## 6. Lineage boundaries

Xiaomi-Robotics-0 is a different model (its numbers do not transfer); Qwen3-VL-4B-Instruct's own VQA capabilities are not policy capabilities; ERVLA shares the backbone family and the choice-branch idea but is a different system with a different training set. [XR0-TR; ERV-PAPER]

## Sources

[XR1-TR]; [XR1-CODE]; [XR1-CODE-EVAL-VLABENCH]; [XR1-CODE-XR1-README]; [XR1-HF-VLABENCH]; [XR1-ISSUE-12]; [VLAB-CODE]; [VLAB-PAPER]; [VLAB-DATA-LEROBOT]; [VLAB-ISSUE-55]; [VLAB-ISSUE-80]; [VLAB-ISSUE-82]; [VLAB-ISSUE-88]; [ERV-PAPER]; [XR0-TR].
