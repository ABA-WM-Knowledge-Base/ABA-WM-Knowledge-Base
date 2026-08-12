---
id: world-model-kb.papers.cosmos-predict2-5.reproduction
title: Cosmos-Predict2.5 Reproduction State and Experiment Contracts
kind: record
status: maintained
last_updated: 2026-08-12
owners:
  - AIBuildAI world-model group
---

# Cosmos-Predict2.5 Reproduction State and Experiment Contracts

## Retrieval metadata

**Relevant queries:** Predict2.5 reproduced, local run, inference command, hardware requirement, benchmark reproduction, training reproduction, missing artifact, or acceptance criteria.

**Knowledge provided:** the current executed-state boundary, documented but unexecuted reference commands, artifact requirements, minimum inference and action-model reproduction contracts, and conditions that prevent an exact paper reproduction claim.

**Related pages:** [`codebase.md`](codebase.md) owns the released call graph and paper-code mismatches; [`paper.md`](paper.md) owns reported metrics; [evaluation methodology](../../foundations/data-and-evaluation/evaluation-methodology.md) owns comparison validity; [Cosmos3-Nano reproduction](../../models/cosmos3-nano/reproduction.md) is a different model's execution registry.

## 1. Current execution state

| Surface | KB state | Evidence retained | Claim permitted |
|---|---|---|---|
| Paper PDF identity and page layout | verified by source inspection | 44-page local PDF hash and selected rendered-page review | The v2 paper claims and locators in this entry were inspected. |
| Official code identity and static call graph | verified by source inspection | clean local clone at current commit plus immutable Git history | Released modules and documented commands were inspected. |
| Checkpoint repository identity | verified by metadata inspection | current Hugging Face repository SHAs | Current repository trees can be named; exact evaluated weight identity remains unresolved. |
| Base 2B inference | not attempted | none | No local Predict2.5 output has been reproduced. |
| Base 14B inference | not attempted | none | No 14B load, output, latency, or memory claim is local evidence. |
| Action-conditioned inference | not attempted | none | No Bridge rollout has been reproduced. |
| PAI-Bench evaluation | not attempted | none | Paper scores are reported results only. |
| SFT, RL, merge, or distillation | not attempted | none | No training result has been reproduced. |

Static inspection is not an inference reproduction. No command in this page is marked successful unless an immutable run record with environment, resolved config, logs, inputs, outputs, and hashes is later added.

## 2. Reproduction-level vocabulary

- **Documented:** a paper, model card, or pinned code snapshot describes the capability.
- **Source inspected:** the relevant paper pages or code path were opened and reconciled.
- **Executed:** a command completed in a recorded environment and retained raw artifacts.
- **Metric reproduced:** the same metric implementation and protocol produced an acceptance-compatible result from a pinned checkpoint.
- **Paper result reproduced:** checkpoint, data, evaluator, generation budget, and aggregation are sufficiently matched to support the named table or figure.

Only the first two levels currently apply. This vocabulary describes evidence, not workflow permissions or task scheduling.

## 3. Documented environment boundary

Use commit `a24ac3df55d55f87deff7067907afcaf961045f1` for a paper-era execution attempt: it preserves the v1.5.0 feature set plus the intervening release hotfix. Commit `f2146f47a07abf72459c92a9958484ff447ed37d` remains useful for isolating where the release functionality entered the codebase, but omits that hotfix. A run on current main is a maintained-code replication and must not be labeled an exact paper-era environment. [P25-CODE-PAPER; P25-CODE-REPORT-UPDATE; P25-CODE-CURRENT]

The report-date setup guide requires Linux x86-64, glibc at least 2.35, an Ampere-or-newer NVIDIA GPU, and a driver compatible with CUDA 12.8.1. It documents a `uv` environment with the `cu128` extra and Docker with NVIDIA Container Toolkit; it also exposes a CUDA 13.0 dependency variant. Checkpoint access requires a Hugging Face token and acceptance of applicable NVIDIA model/guardrail licenses. [P25-CODE-REPORT-UPDATE, `docs/setup.md`]

The base inference guide documents single-process and eight-process commands but does not publish minimum per-GPU memory for base 2B/14B. CPU offload flags exist for the denoiser, tokenizer, text encoder, and guardrail models; using them changes latency and host-memory conditions. Auto multiview is separately documented at a minimum of eight 80 GB GPUs. Action-conditioned inference does not support multi-GPU in the public guide. [P25-CODE-CURRENT, `docs/inference.md`, `docs/inference_auto_multiview.md`, `docs/inference_robot_action_cond.md`]

Because the local workstation has not loaded a Predict2.5 checkpoint, hardware sufficiency is unresolved for the base model in this entry. A memory estimate derived from parameter count is not an observed peak-memory result.

## 4. Reference commands: documented, not executed

### 4.1 Base Video2World smoke test

```bash
python examples/inference.py \
  -i assets/base/robot_pouring.json \
  -o outputs/base_video2world \
  --inference-type=video2world \
  --model=2B/post-trained
```

The public interface may resolve values from both JSON and CLI, with CLI overrides taking precedence. A valid record must retain the input JSON, input media, `output/config.yaml`, serialized sample arguments, output MP4, stdout/stderr, and hashes. [P25-CODE-PAPER, `docs/inference.md`, `examples/inference.py`]

### 4.2 Action-conditioned smoke test

```bash
python examples/action_conditioned.py \
  -i assets/action_conditioned/basic/inference_params.json \
  -o outputs/action_conditioned/basic \
  --model=2B/robot/action-cond
```

Keep the explicit model key. At the pinned commit, the guide describes `robot/multiview` as the default, but `ActionConditionedSetupArguments` fixes the executable default and accepted model literal to `robot/action-cond`. The bundled JSON and high-level config encode output at 20 FPS, the paper's Bridge protocol is 5 FPS, and older low-level examples show 4 FPS; these values describe different stages and must not be silently equated. Confirm the resolved CLI with `--help`, and retain original robot state/action annotations, processed action tensors, coordinate-frame and normalization settings, source/action/generated time intervals, output playback FPS, chunk size, seed sequence, generated chunk MP4, and concatenated rollout. [P25-CODE-PAPER, `docs/inference_robot_action_cond.md`, `cosmos_predict2/action_conditioned_config.py`, `assets/action_conditioned/basic/inference_params.json`, `examples/action_conditioned.py`]

### 4.3 Post-training interface probe

```bash
torchrun --nproc_per_node=8 scripts/train.py \
  --config=cosmos_predict2/_src/predict2/configs/video2world/config.py -- \
  experiment=predict2_video2world_training_2b_cosmos_nemo_assets
```

This command exercises the released SFT interface on Cosmos-NeMo-Assets; it is not a reproduction of foundation pre-training or the paper's five specialist runs. A later inference record must bind the converted `model_ema_bf16.pt` hash and original DCP checkpoint identity. [P25-CODE-PAPER, `docs/post-training_video2world_cosmos_nemo_assets.md`]

## 5. Minimum base-inference experiment contract

### 5.1 Identity

Record:

- code commit and any patch diff;
- outer Hugging Face repository revision and inner checkpoint identifier;
- exact input media SHA256 and prompt text;
- model key, generation mode, output resolution/FPS/frames, conditional latent frames, denoising steps, guidance, negative prompt, seed, guardrail state, offload flags, and context-parallel size;
- OS, kernel, Python, dependency lock, PyTorch/CUDA/driver, GPU model/count/VRAM, CPU, host RAM, and storage.

### 5.2 Outputs

Retain raw MP4, argument JSON, resolved config, complete log, wall time, peak per-GPU memory, host peak memory, and output SHA256. Decode the MP4 and record actual frame count, dimensions, FPS, duration, and whether any guardrail altered or rejected output.

### 5.3 Acceptance

A base smoke test is **executed** only if the pinned checkpoint loads, generation exits successfully, the MP4 decodes, output properties match the resolved task contract, and the output is non-empty. It is **not** a PAI-Bench or physical-correctness reproduction. A deterministic hash match is not required unless the backend and deterministic-kernel conditions are also fixed; visual comparison alone is insufficient for numerical equivalence.

## 6. Minimum action-conditioned experiment contract

The action specialist requires stronger controls than a base video sample:

1. Preserve the official Bridge train/test split and identify every evaluated episode.
2. Bind raw state, camera stream, action extraction code, coordinate frame, translation/rotation units, Euler/quaternion convention, gripper polarity and scale, temporal downsampling, resize/crop, and chunk length.
3. Generate with the same initial observation and action chunks as ground truth; distinguish teacher-forced single chunks from autoregressive rollouts.
4. Compute PSNR, SSIM, latent L2, and FVD with fixed libraries and aggregation. Report horizon-stratified results in addition to the paper aggregate.
5. Add matched feasible action counterfactuals and an action-sensitivity measure. A model that ignores actions can look plausible on behaviorally narrow data.
6. If the model is used to guide decisions, replay or environment-grounded closed-loop evaluation is required; generated-video agreement with its own actions is not independent validation.

A claim that Table 19 or Table 20 was reproduced additionally requires the same 100 official test episodes, baseline checkpoint, evaluator features, sampling budget, and injection variants. These identities are not fully disclosed by the paper, so an exact result may remain unattainable even after a controlled replication.

## 7. Benchmark reproduction contract

For PAI-Bench, bind the benchmark revision, prompt set, input images, evaluator checkpoints, VQA templates, all eight Quality metrics, seven domain categories, generation resolution/duration/FPS, sample count per condition, seed set, candidate-selection policy, and formula `Overall=(Domain+Quality)/2`. Preserve per-example model outputs and evaluator judgments. [P25-PAIBENCH; P25-TR, pp.15-17]

The paper does not publish the exact evaluated checkpoint SHA, all generation parameters, evaluator revisions, seeds, or human-evaluation sample counts. A run can therefore be a protocol-aligned replication without being an exact paper-table reproduction. That deviation must remain explicit.

## 8. Training reproducibility boundary

| Training stage | Publicly reconstructable elements | Missing elements blocking exact reproduction |
|---|---|---|
| Foundation pre-training | objective, architecture summary, stage order, LR/optimizer, conditional-frame mixture | 200M-clip manifest, source access, mixture weights, all stage steps/batches, exact code/config, total compute |
| Domain SFT | five domain counts, 30K steps, batch 256, high-level data classifier | datasets/manifests, classifier, thresholds, prompts, exact starting checkpoint and configs |
| 4K cooldown + merge | 388K count, LR decay, candidate methods, final model-soup choice | data, coefficients, sweep, selection set, judge protocol, scripts |
| RL | VideoAlign dimensions, group 8, 20 steps, batch 32, 256 updates, diffusion regularizer | released end-to-end code/config, reward revision, prompt set, optimizer/LR, seeds, full infrastructure |
| rCM | method identity, four-step result tables, high-level infrastructure | public recipe/config/checkpoint lineage matching Tables 7-8 |
| Public SFT/DMD2 alternatives | code, examples, checkpoint lifecycle | equivalence to paper's proprietary stages and evaluated students |

Accordingly, this entry may support mechanism replication, released-checkpoint evaluation, and new adaptation studies. It cannot currently support a claim of complete training reproduction.

## 9. Run-record template

```text
Experiment ID:
Timestamp / operator-independent clock:
Question and predeclared acceptance criterion:
Paper/code/model/data/evaluator revisions:
Patch identity:
Environment and hardware:
Input and preprocessing hashes:
Exact command:
Resolved configuration:
Seeds or rollout IDs:
Baseline and intervention:
Controlled variables:
Raw output/log paths and SHA256:
Metrics and aggregation:
Failure, root cause, and minimal fix:
Remaining deviation:
Evidence conclusion:
```

No run record is registered yet. When a run exists, store its immutable artifacts in an entry-local artifact directory or external artifact store and register the summary through [`sources.yaml`](sources.yaml).

## Sources

Documented commands and requirements resolve through [`sources.yaml`](sources.yaml); no local execution artifact is currently registered.
