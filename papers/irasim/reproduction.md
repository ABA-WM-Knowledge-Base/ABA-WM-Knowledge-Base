---
id: world-model-kb.papers.irasim.reproduction
title: IRASim Reproduction State and Experiment Contracts
kind: record
status: maintained
last_updated: 2026-08-13
owners:
  - AIBuildAI world-model group
---

# IRASim Reproduction State and Experiment Contracts

## Retrieval metadata

**Relevant queries:** IRASim reproduced, execution status, inference command, checkpoint download, archive size, hardware, environment, syntax failure, minimal patch, metric reproduction, policy evaluation reproduction, planning reproduction, or acceptance criteria.

**Knowledge provided:** immutable source-inspection evidence, current local execution boundaries, released reference commands, known blockers and code defects, and minimum contracts for inference, metrics, policy evaluation, and planning.

**Related pages:** [`codebase.md`](codebase.md) owns the released call graph and defects; [`paper.md`](paper.md) owns reported values; [evaluation methodology](../../foundations/data-and-evaluation/evaluation-methodology.md) owns comparison validity; [Cosmos3-Nano reproduction](../../models/cosmos3-nano/reproduction.md) is a separate model's execution registry.

## 1. Current execution state

| Surface | Evidence state | Recorded evidence | Permitted claim |
|---|---|---|---|
| ICCV-v2 paper identity and content | source inspected | 28-page PDF SHA256 plus full text extraction and representative rendered-page review | The equations, tables, figures, and contradictions recorded in this entry were inspected. |
| Official repository identity | source inspected | clean clone at pinned full commit; file hashes and Git metadata | The released implementation graph and static gaps were inspected. |
| Public bundle identity and availability | metadata/HTTP inspected | immutable HF revision; 820 GB tree; original RT-1 train archive returned HTTP 200 and `91,805,315,122` bytes; first checkpoint split returned HTTP 200 and `2,147,483,648` bytes | The public outer artifacts were reachable at inspection time; no inner checkpoint has been downloaded or hashed. |
| Python syntax surface | executed static check | `python -m py_compile` over 28 tracked Python files | 26 parsed; the two recorded duplicate-`if` scripts failed with `IndentationError`. |
| Checkpoint load and short inference | not attempted | none | No official IRASim video has been locally generated. |
| Long inference or interactive application | not attempted | static syntax blockers identified | No long rollout, keyboard control, or VR control is reproduced. |
| Paper Table 1/3 metrics | not attempted | none | All numerical values remain reported paper evidence. |
| Training | not attempted | none | No optimizer step, loss curve, model checkpoint, or scaling result is local evidence. |
| LIBERO, Push-T, or real-robot planning | not reconstructable from the public tree and not attempted | paper-only protocol inspection | No decision-use experiment has been reproduced. |

Static inspection is not inference reproduction. Source availability is not checkpoint integrity. No row may be promoted to executed inference or metric reproduction without an immutable run record containing inputs, resolved configuration, logs, outputs, environment, and hashes.

## 2. Reproduction vocabulary

- **Documented:** a pinned paper or repository describes a behavior.
- **Source inspected:** the relevant paper pages or code paths were reconciled.
- **Artifact reachable:** an immutable URL responds and its advertised outer identity is recorded.
- **Artifact verified:** the complete downloaded file has a retained SHA256 and expected archive structure.
- **Executed:** a command completes in a recorded environment with raw artifacts.
- **Metric reproduced:** a pinned checkpoint and protocol yield the declared metric within a predeclared tolerance.
- **Paper result reproduced:** model, data, code, evaluator, sampling, and aggregation identities are sufficiently matched to support the named table or figure.

These terms describe evidence only. They do not prescribe AIBuildAI workflow, task order, permissions, or experiment priority.

## 3. Artifact and environment boundary

The most storage-efficient released smoke surface is Language-Table, but it is still large: the README advertises approximately 200 GB training, 194 GB evaluation, and 34 GB checkpoint archives. RT-1 advertises 86/100/29 GB and Bridge 31/63/32 GB. The pinned Hugging Face tree is approximately 820 GB because it contains all split archives. A valid smoke run need not download all domains; it must, however, reconstruct and hash every selected archive and preserve enough official evaluation data to validate the output. [IRASRC-CODE-CURRENT; IRASRC-HF-BUNDLE]

The official install script specifies PyTorch wheels for CUDA 11.8 and Diffusers 0.24.0, but leaves Python, PyTorch, torchvision, transformers, TensorFlow, Deepspeed, and most other packages unpinned. It includes optional FlashAttention and assumes Linux tools. This is an installation hint, not an environment lock. [IRASRC-CODE-CURRENT, `scripts/install.sh`]

The inspected workstation has Windows, Python 3.12.13, and one RTX 4060 Laptop GPU with 8,188 MiB. The paper reports that 16-frame inference uses 8 GB on an A100, but this is not a guarantee that the released XL checkpoint plus CUDA context, VAE, and scheduler fit an 8 GB consumer GPU. No checkpoint was loaded, and local sufficiency remains unresolved. [IRASRC-PAPER-V2, pp.21-22]

The paper reports training with 32 A800/A100 GPUs and thousands of GPU hours per domain. Complete training reproduction is outside the current local resource envelope even before the 300K/3M-step conflict and missing dependency/data identities are resolved.

## 4. Released commands: documented, not executed

### 4.1 Environment and selected archive

```bash
git clone https://github.com/bytedance/IRASim.git
cd IRASim
git checkout c72b6dade6fcd65971e0aa8ab49ea39b15108c90
bash scripts/install.sh
```

The installer should be replaced by a recorded, resolved dependency lock for a real replication. The public data can be obtained from the original tar URLs or `fangqi/IRASim@dfcbf85c27b2c5d041dbf5df3df272111e758b48`; the Hugging Face files must be merged before extraction. Retain split-part identities, merged archive SHA256, extracted-manifest hash, and inner checkpoint SHA256. [IRASRC-CODE-CURRENT; IRASRC-HF-BUNDLE]

### 4.2 Short Frame-Ada inference

The released interface can be launched in the following explicit one-process form:

```bash
torchrun --nproc_per_node 1 --nnodes 1 --node_rank 0 \
  --rdzv_endpoint 127.0.0.1:29400 --rdzv_id irasim-smoke \
  --rdzv_backend c10d main.py \
  --config configs/evaluation/languagetable/frame_ada.yaml
```

This explicit one-process launch avoids the fallback's hard-coded CUDA device 1. Before execution, set `configs/base/data.yaml` paths to the actual extracted bundle and provision the SDXL VAE at the resolved path. The official config evaluates an entire test split; a bounded smoke test requires an explicitly recorded config derivative rather than an undocumented edit. [IRASRC-CODE-CURRENT; IRASRC-SDXL-VAE]

Do not reuse the RT-1 or LanguageTable training config unchanged for a training claim. Both set `debug: True`; the released dataset factory then substitutes the validation split for the training split, and the dataset implementation truncates non-evaluation debug data to ten samples. A training replication must set `debug: False` in a retained derivative, then record resolved train/validation manifests and observed sample counts before optimization. [IRASRC-CODE-CURRENT, `IRA-CODE-GAP-10`]

### 4.3 Metric script

The correct released filename is:

```bash
python evaluate/evaluate_short_script.py
```

The README's `evaluation_short_script.py` spelling does not exist. The script itself is not parameterized and currently hard-codes Bridge/Frame-Ada and a date-specific result directory; a metric replication must patch it into a declarative CLI or retain the exact code diff and resolved paths. Its FVD command requires eight GPUs and uses vendored evaluator code. [IRASRC-CODE-CURRENT]

### 4.4 Long rollout

The documented workflow generates per-process commands and invokes `sample/sample_autoregressive.py`. At the pinned commit this file fails to parse because of a duplicated conditional. Removing the duplicate line is the minimal syntax repair, but any resulting output is a **patched-code replication** and must bind the patch hash. [IRASRC-CODE-CURRENT, `IRA-CODE-GAP-01`]

## 5. Minimum short-inference contract

### 5.1 Identity

Record:

- code commit and patch diff;
- Hugging Face outer revision, split-part list, reconstructed archive SHA256, inner checkpoint SHA256, and checkpoint key selected (`ema` or raw mapping);
- SDXL repository revision and local VAE file hashes;
- dataset, split, episode/clip IDs, annotation hashes, raw video or latent hashes;
- action units, previous-frame coordinate convention, Euler order, gripper semantics, seven-component scale vector, frame rate, frame/action timestamps, resize, normalization, and pre-encoding path;
- model variant, `extras`, `final_frame_ada`, history count, frames, sampler, inference steps, guidance, seed or generator state, dtype, and device;
- OS, kernel, Python, full lock, PyTorch/CUDA/driver, GPU/VRAM, CPU, RAM, and storage.

### 5.2 Outputs

Retain stdout/stderr, resolved merged config, checkpoint-load key coverage, generated latent tensor, decoded MP4 and frame sequence, generation wall time, peak GPU and host memory, and SHA256 for every output. Decode the MP4 and verify actual shape, frame count, FPS, and non-empty content.

### 5.3 Acceptance

A short inference is **executed** only when a pinned official Frame-Ada checkpoint loads, one official clip's one-history-plus-actions contract completes, the 16-frame output decodes, action count and output count align, and raw artifacts are retained. It is **not** a Table 1 reproduction, physical-correctness result, or planning result.

## 6. Table 1 and Table 3 metric contract

For a protocol-aligned reconstruction:

1. use the paper's exact train/validation/test split and Table 7 clip counts;
2. preserve one history frame, 15 actions, output resize, latent codec, and validation/test interval 16;
3. bind Frame-Ada, Video-Ada, LVDM, and VDM checkpoint hashes and generation budgets;
4. compute PSNR, SSIM, latent L2, FID, and FVD with fixed evaluator code, versions, features, and aggregation;
5. ignore the initial frame as the paper specifies;
6. for long rollouts, preserve the exact episode identities, average lengths, segment overlap, final-frame chaining, and horizon-stratified metrics;
7. add action-sensitive tests even though they are not in the paper: zero, shuffled, sign-flipped, magnitude-binned, and matched feasible alternatives with fixed observation and noise.

An exact Table 1/3 claim remains blocked by unpublished paper-era environment and inner artifact identities unless those are recovered. A replication can still be scientifically useful if deviations are explicit.

## 7. Frame-Ada mechanism reproduction

The minimum causal experiment is not simply “Frame-Ada beats Video-Ada.” Compare under matched backbone, parameter budget, data order, optimizer, and sampling:

| Variant | Spatial block action condition | Temporal block action condition | Final-layer action condition |
|---|---|---|---|
| Video-Ada released | global trajectory | global trajectory | global trajectory |
| Frame-Ada released-compatible | per-frame | none explicit | none explicit |
| Frame-Ada paper-faithful | per-frame | global trajectory | per-frame or explicitly specified |
| Frame-Ada repaired-final | per-frame | released behavior | per-frame |

Measure primary reconstruction metrics, frame-indexed end-effector/object error, action-shuffle sensitivity, contact/state events, and latency. A transfer claim is falsified if per-frame modulation improves pixel similarity without stronger matched-action separation or task-state fidelity.

## 8. Decision-use reproduction contracts

### 8.1 LIBERO policy evaluation

Bind LIBERO revision, exact task, scene initialization distribution, expert demonstrations, four diffusion-policy checkpoints and training updates, post-trained rollout manifest with success/failure labels, OpenSora initialization, IRASim patch and checkpoint, 50-run seed sets, rollout sampling parameters, and human judgment UI/instructions. Report binomial uncertainty for each success rate and uncertainty on rank/Pearson correlation. [IRASRC-PAPER-V2, pp.9-10, Table 4]

The public repository lacks this stack; an independent implementation must be labeled a reconstruction, not an execution of released author code.

### 8.2 Push-T planning

Bind the 200 expert demonstrations, diffusion-policy checkpoint, `P in {0,100,200,500,1000}` rollout manifests, success/failure distribution, OpenSora/IRASim identity, ResNet50 value checkpoint and split, `K in {1,5,10,50}`, 100 trial seeds, candidate sampler, execution horizon, and IoU implementation. Preserve every predicted rollout, predicted value, selected action, realized IoU, and ranking regret. [IRASRC-PAPER-V2, pp.10-13, Table 5; IRASRC-GPC]

Predeclare two acceptance checks: reproduce the harmful `P=0, K=50` regime rather than hiding it, and show that any larger-`K` gain persists under a value model evaluated on held-out rollout data. Search that improves predicted value while reducing realized IoU is model/evaluator exploitation.

### 8.3 Real-robot planning

Bind robot/controller, calibration, control rate, circle radius, trajectory interpolation, 50 proposals, goal image, MSE/ResNet evaluator, top-five execution semantics, reset protocol, three repeats, intervention and safety policies, and all training-task overlap. Report success counts rather than rounded proportions alone. The private dataset and weights are absent, so exact reproduction is currently unattainable from public artifacts. [IRASRC-PAPER-V2, pp.12-13, 22-23, Table 6]

## 9. Training reproducibility boundary

| Regime | Publicly recoverable | Missing for exact reproduction |
|---|---|---|
| RT-1/Bridge/Language-Table base | architecture, core loss, official configs, split archive, checkpoints, optimizer summary, outer data counts | fully pinned environment, paper-era VAE files, inner archive/checkpoint hashes until downloaded, seeds, exact data transforms/provenance, 300K/3M resolution |
| RoboNet | paper action contract, counts, resolution, metrics | code, config, split processing, checkpoint, compute, environment |
| LIBERO evaluator | task sentence, 50-run protocol, four rates, OpenSora initialization concept | code, manifests, model revisions, hyperparameters, reward/success labeling artifacts |
| Push-T planning | expert count, `P/K` grid, reward type, results | complete training and planning code, model/data/value identities, seeds, inference budget |
| Real-robot planning | proposal/cost description and aggregate rates | dataset, robot/controller configuration, model, code, raw trials, safety log |

## 10. Run-record template

```text
Experiment ID:
Timestamp:
Question and predeclared acceptance criterion:
Paper, code, data, checkpoint, VAE, and evaluator identities:
Patch identity and rationale:
Environment and hardware:
Input, annotation, preprocessing, and action-contract hashes:
Exact command and resolved configuration:
Seeds, episodes, clips, or rollout IDs:
Baseline and intervention:
Controlled variables:
Raw output/log paths and SHA256:
Metrics, aggregation, and uncertainty:
Failure, root cause, and minimal fix:
Remaining deviation:
Evidence conclusion:
```

No inference run record is registered. When one exists, store immutable artifacts in an external artifact store or a declared entry-local artifact directory and register the summary through [`sources.yaml`](sources.yaml).

## Sources

- [IRASRC-PAPER-V2] paper protocols, metrics, compute, and limitations.
- [IRASRC-CODE-CURRENT] commands, configs, code defects, and released structure.
- [IRASRC-HF-BUNDLE] immutable outer archive identity.
- [IRASRC-SDXL-VAE] current external VAE repository identity; exact paper-era files unresolved.
