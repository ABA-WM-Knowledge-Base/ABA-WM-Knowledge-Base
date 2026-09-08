---
id: world-model-kb.models.cosmos3-nano.post-training
title: Cosmos3-Nano Post-Training and Domain Adaptation
kind: guide
status: maintained
last_updated: 2026-09-08
owners:
  - AIBuildAI world-model group
---

# Cosmos3-Nano Post-Training and Domain Adaptation

## Retrieval metadata

**Relevant queries:** adaptation branch, public SFT recipe, action-interface adaptation, checkpoint conversion or export, specialist training, distillation, or domain-specific post-training.

**Knowledge provided:** checkpoint branch boundaries, published specialist recipes, trainable groups, conversion paths, adaptation variables, and comparison confounders.

**Related pages:** [Training](training.md) contains foundation objectives; [Data](data.md) contains dataset state; [Policy](policy.md) contains serving I/O; [Evaluation](evaluation.md) contains reported results; [Reproduction](reproduction.md) contains execution state. [Datasets and supervision](../../foundations/data-and-evaluation/datasets-and-supervision.md) owns the model-independent data principles used to assess adaptation recipes; [Few-Step and One-Step Video Distillation](../../components/fast-video-inference/few-step-distillation.md) owns cross-paper acceleration methods whose direct Cosmos3-Nano compatibility remains unverified.

## 1. Select the branch before selecting a recipe

Cosmos 3 post-training is not one shared stage. Three specialists fork independently from mid-trained checkpoints:

| Source | Specialist output | Scale | Valid use for Nano optimization |
|---|---|---|---|
| Cosmos3-Super mid-trained | `Cosmos3-Super-Text2Image` | Super | Method reference only; not a Nano checkpoint or baseline |
| Cosmos3-Super mid-trained | `Cosmos3-Super-Image2Video` | Super | Method reference only; not a Nano checkpoint or baseline |
| Cosmos3-Nano mid-trained | `Cosmos3-Nano-Policy-DROID` | Nano | Direct Nano adaptation branch; distinct from base Nano |

The branches retain their source architecture scale but use different data, objectives, and checkpoints. Artificial Analysis T2I and I2V results belong to the two Super specialists, not base Cosmos3-Nano. [C3-TR, pp.20, 30–32, 55–60, Figure 8]

Use the following names precisely:

- `Cosmos3-Nano`: mid-trained base omnimodal checkpoint; valid MT-init.
- `Cosmos3-Nano Reasoner`: autoregressive visual-understanding/text-output path; it does not emit DROID joint commands.
- `Cosmos3-Nano-Policy-DROID`: DROID-specialized policy checkpoint initialized from MT-init.
- `Cosmos3-Nano (PT-init)`: paper control initialized before action mid-training and then adapted; not an alias for public base Nano.
- `Cosmos3-Super-Text2Image` and `Cosmos3-Super-Image2Video`: Super-scale specialists.
- Action-CoT: Reasoner supervision for text, points, or waypoints; not diffusion action tokens.

## 2. Super T2I specialization as an adaptation pattern

This branch demonstrates a broad-SFT-then-preference-refinement pattern. Its weights and scores cannot be attributed to Nano. [C3-TR, pp.30–31]

### 2.1 Stage 1: broad high-quality SFT

- 20,000 steps.
- Mixture: 45% high-quality real images, 40% synthetic images, 15% text-rendering-only images.
- Base learning rate `1e-4`; 2,000-step warmup followed by linear decay; remaining hyperparameters follow Generator mid-training.
- Images above 720p only; fixed 70K-token context.

The stage balances visual fidelity, caption alignment, and text retention. Figure 8 labels the overall T2I post-training data as 8M, but the prose does not divide that count between stages. Do not infer sample count from steps and an unstated batch size. [C3-TR, pp.20, 30–31, Figure 8]

### 2.2 Stage 2: preference-oriented refinement

- Continue from Stage 1 for 2,000 steps.
- 470K ultra-high-quality image-caption pairs.
- Optimize aesthetics, prompt following, text rendering, and human preference while retaining the resolution and 70K-context constraints. [C3-TR, p.31]

The specialist scores 91.36 on UniGenBench All versus 84.61 for base Nano. CVTG-500L GNED/PNED is 80.88/89.08 versus 24.23/26.53 for base Nano. This demonstrates a large capability-profile shift under specialization; it does not identify which stage or data component caused the gain. [C3-TR, p.55, Table 11]

**Transferable hypothesis:** use a broad, quality-filtered domain SFT stage to establish coverage, then a short preference or hard-example stage to sharpen the target capability. Gate both stages with general-retention metrics; do not begin with narrow preference data unless broad competence is already adequate.

## 3. Super I2V specialization as an adaptation pattern

The I2V specialist starts from mid-trained Super. Every video uses I2V formulation, while 20% T2I image tokens preserve semantic alignment. [C3-TR, p.31]

| Component | Function | Known scale |
|---|---|---:|
| Strictly filtered, topic-balanced pre-training videos | Broad prior and distribution regularization | not disclosed |
| Agentic weakness retrieval | Retrieve examples matched to diagnosed failures | not disclosed |
| Human-curated videos | Direct high-quality supervision | 1,000 |
| Synthetic videos | Rare subjects and motion patterns | about 20K; about 6% of total tokens |
| T2I image tokens | Protect text-semantic alignment | 20% of mixture tokens |

Training targets 480p, 189 frames, approximately 24 FPS and 8 seconds; it runs 10,000 iterations at learning rate `1e-5` for about 50B tokens. Figure 8 labels I2V post-training as 20K, while prose also includes filtered pre-training videos, 1,000 curated videos, and T2I tokens. Interpret 20K as the specialist synthetic-data label, not a complete sample count. [C3-TR, pp.20, 31, Figure 8]

The specialist ranked first among open-weight models and 22nd overall in the Artificial Analysis I2V (No Audio) snapshot dated 2026-05-28. The result is checkpoint-, protocol-, and date-specific. [C3-TR, pp.59–60, Figure 19]

**Transferable hypothesis:** failure-conditioned retrieval plus a small curated anchor can improve a narrow mode more efficiently than undirected scaling; retain a replay modality to prevent semantic collapse.

## 4. Nano Policy-DROID adaptation state

### 4.1 Data contract

Policy-DROID restores the mid-trained Cosmos3-Nano checkpoint. Raw DROID scale is reported as 76K trajectories, 350 hours, 86 tasks, and 564 scenes. Training ingests 360×640 source images and applies community idle-frame filtering, failure-demonstration removal, and random image augmentation. [C3-TR, pp.31–32]

Figure 8 labels policy post-training with 58K samples, while prose reports 76K raw trajectories. A plausible interpretation is processed versus raw scale, but the report does not define the mapping. Do not attribute the 18K difference entirely to idle/failure filtering without the actual manifest. [C3-TR, pp.20, 31, Figure 8]

### 4.2 Parameter and observation contract

The MT-init backbone is restored, while the action encoder, action-decoding MLP, and action embedding tokens are randomly initialized. These action-specific groups use a `5x` learning-rate multiplier relative to the main rate. [C3-TR, pp.31–32]

One observation combines current proprioception, the official DROID short task instruction, and a fixed three-view canvas:

```text
┌──────────────────────────────────────────┐
│ wrist view: 360 × 640                    │
├────────────────────┬─────────────────────┤
│ external 1:        │ external 2:         │
│ 180 × 320          │ 180 × 320           │
└────────────────────┴─────────────────────┘
final canvas: 540 × 640
```

View order, resize, and canvas geometry are model inputs, not presentation details. Changing them creates a distribution shift. [C3-TR, p.32]

### 4.3 Output and optimization state

The policy predicts 32 future absolute joint-position actions at 15 Hz and auxiliary RGB future frames. One action chunk spans about 2.13 seconds. It is neither a delta end-effector policy nor a Reasoner waypoint output. [C3-TR, p.32]

| Field | Reported state |
|---|---|
| Source | Cosmos3-Nano mid-trained checkpoint / MT-init |
| New groups | action encoder, decoding MLP, embedding tokens |
| Base learning rate | `2e-4` |
| Action-group multiplier | `5x` |
| Other optimizer settings | inherited from mid-training |
| Action target | 32 absolute joint-position steps at 15 Hz |
| Auxiliary target | multiview RGB future frames |

The report does not disclose batch size, iterations, total tokens, GPU-hours, train/validation split, augmentation parameters, action-versus-RGB loss weights, or whether `2e-4 × 5` is the actual peak for new action groups. Resolve these from a fixed recipe/config before claiming an exact reimplementation. [C3-TR, pp.31–32]

## 5. Public post-training code surface

The fixed Framework exposes SFT/post-training tooling rather than complete foundation-training manifests. Official documentation includes Nano vision SFT, LLaVA-OneVision Reasoner alignment, VideoPhy2 Reasoner SFT, and DROID/LIBERO action-policy recipes. These validate data contracts, checkpoint conversion, configuration parsing, distributed training, resume, and export. [C3-FW-TRAINING]

```text
prepare public dataset / structured JSONL
  → choose examples/toml/sft_config/<recipe>.toml
  → convert source checkpoint when required
      Generator/action: convert_model_to_dcp
      Nano Reasoner: convert_model_to_vlm_safetensors
  → launch_sft_<recipe>.sh
      → cosmos_framework.scripts.train --sft-toml=<recipe>
  → resolved config + DCP iter_<N> checkpoints + RNG state
  → cosmos_framework.scripts.export_model
  → optional convert_model_to_diffusers
```

Paired launch scripts enter the common training path through `_sft_launcher_common.sh`. `SFTExperimentConfig` validates the recipe TOML and rejects unknown fields before launch. Direct `torchrun -m cosmos_framework.scripts.train` is possible, but the caller must resolve `DATASET_PATH`, `BASE_CHECKPOINT_PATH`, and `WAN_VAE_PATH`. Resume from `checkpoints/iter_<N>/`; an exported inference safetensors file does not contain recoverable optimizer, scheduler, data-position, or RNG state. [C3-FW-TRAINING]

The canonical training artifact set includes resolved `config.yaml`, DCP checkpoint, `latest_checkpoint.txt`, iteration, per-rank RNG state, data revision, recipe TOML, and launch environment. `export_model` converts DCP plus configuration to Framework inference safetensors. Diffusers conversion is a separate layout. Never interchange DCP, Framework safetensors, and Diffusers layouts by filename alone. [C3-FW-TRAINING]

## 6. Domain-adaptation decision procedure

1. **Name the target surface:** Reasoner text/grounding, Generator media, forward dynamics, inverse dynamics, or policy. Do not combine surfaces before a single-surface baseline exists.
2. **Select the source checkpoint:** compare PT-init and action-inclusive MT-init for control tasks; compare base and specialist only under matched architecture and protocol.
3. **Freeze the target contract:** observation views/order, proprioception fields, instruction template, action type, units, coordinate frame, rate, horizon, gripper convention, and future-visual target.
4. **Build a versioned manifest:** episode split, success/failure/idle policy, synchronization, normalization statistics, language distribution, augmentation, and leakage checks.
5. **Choose parameter scope:** begin with new interface modules or adapters; expand unfreezing only when a capacity or representation bottleneck is demonstrated.
6. **Create control arms:** source-checkpoint baseline, action-only versus action+future-RGB, target-only versus replay mixture, and at least one frozen-backbone condition.
7. **Run learning curves:** evaluate early and late checkpoints; MT-init's benefit may be convergence speed rather than final asymptote.
8. **Export reproducibly:** preserve the resumable DCP state and separately hash each inference export.

## 7. Controllable post-training levers

| Lever | Primary question | Measurement | Guardrail |
|---|---|---|---|
| Source checkpoint | Does world/action mid-training improve adaptation? | Compute-matched learning curve | Same architecture, data, steps, optimizer |
| Trainable scope | Is interface-only adaptation sufficient? | Target metric plus forgetting | Log exact parameter set and gradients |
| New-module LR multiplier | Are random modules learning too slowly/quickly? | Module gradient norm and target metric | Bound divergence and backbone drift |
| Replay ratio | How much general prior must be retained? | Target/general Pareto frontier | Freeze total tokens |
| Hard-example retrieval | Do diagnosed failures respond to targeted examples? | Failure-bucket recall and global regression | Hold evaluator and retrieval pool fixed |
| Curated versus synthetic | Is quality or coverage limiting? | Per-source ablation | Require real-domain anchor |
| Action horizon/rate | Is temporal chunking mismatched to control? | Open-loop error, closed-loop success, latency | Equalize real-time horizon or report both |
| Auxiliary future RGB | Does world prediction regularize policy learning? | Policy success and video-action consistency | Action-only control arm |
| Canvas/layout augmentation | Is visual topology brittle? | Per-view occlusion/layout stress tests | Preserve canonical view identity |
| Failure/idle treatment | Is recovery or no-op calibration missing? | Recovery and false-idle metrics | Document class and sampling weights |

## Candidate intervention patterns (not live queue items)

The following entries are reusable hypothesis templates, not active or prioritized experiments. Before execution, instantiate the selected pattern as a stable `RQ-*` item in [research-queue.md](research-queue.md) with explicit state, dependencies, experiment contract, and closure rule.

- **ADAPT-H01 — MT-init for sample efficiency:** action-aware MT-init should provide the largest advantage at early checkpoints; evaluate the entire curve and cost-to-threshold.
- **ADAPT-H02 — Interface-first adaptation:** high-LR random action modules with a frozen or low-LR backbone should reduce catastrophic forgetting; unfreeze progressively when validation plateaus.
- **ADAPT-H03 — Auxiliary world prediction:** future-RGB supervision should improve action-state consistency and regularize small policy datasets, but may compete with action accuracy if loss scales are unbalanced.
- **ADAPT-H04 — Replay-protected specialization:** a target-heavy mixture with general and cross-embodiment replay should dominate target-only SFT on the target/retention Pareto frontier.
- **ADAPT-H05 — Failure-conditioned retrieval:** retrieving training segments that match clustered rollout failures should be more efficient than uniformly adding demonstrations.
- **ADAPT-H06 — Recovery-aware data:** retaining a controlled subset of failures with explicit recovery targets may outperform blanket failure removal for long-horizon tasks.
- **ADAPT-H07 — Rate-aware action representation:** an invertible representation that includes rate and controller metadata should transfer more reliably than raw state differences across embodiments.
- **ADAPT-H08 — Two-stage policy adaptation:** broad target-domain behavior cloning followed by short hard-case or preference refinement should mirror the successful specialist pattern without collapsing broad task coverage.

Only instantiated `RQ-*` records may carry dependency impact, evidence state, dependencies, or closure status in [research-queue.md](research-queue.md); reusable procedures belong in [optimization-playbook.md](optimization-playbook.md).

## 9. Experiment-record fields

An adaptation claim is easier to interpret when its record includes:

1. exact source checkpoint and code hashes, branch identity, checkpoint layout, and conversion command;
2. immutable recipe TOML plus fully resolved configuration;
3. dataset snapshot, split keys, sample unit, success/failure/idle handling, leakage test, and license;
4. observation/action schemas, canvas geometry, units, coordinate frames, rate, horizon, normalization statistics, and invertibility test;
5. initialized/restored/frozen parameter list, per-group optimizer values, loss weights, batch/steps/tokens, precision, hardware, and seed;
6. unchanged baseline and one-factor ablations with equal data and compute budgets;
7. target capability, general retention, per-domain/embodiment regressions, safety metrics, and system latency;
8. raw outputs and failure taxonomy at scheduled checkpoints, not only the best checkpoint;
9. resumable DCP artifact with optimizer/scheduler/RNG state and separately hashed Framework/Diffusers exports;
10. declared acceptance threshold, regression budget, compute budget, and termination reason.

## 10. Attribution-risk signals

An adaptation claim is weak or invalid when:

- the source checkpoint scale or stage is misidentified;
- DCP, Framework safetensors, and Diffusers layouts are mixed without a validated conversion;
- view order, resize, action semantics, unit, frame, rate, or normalization is ambiguous;
- new-module gradients explode, remain near zero, or cause immediate backbone forgetting;
- target improvement is attributable to a changed prompt, judge, seed budget, rollout budget, or checkpoint-selection rule;
- target-only improvement violates a predeclared general, embodiment, safety, or latency guardrail;
- future-RGB quality improves while action or closed-loop metrics regress beyond budget;
- data leakage, scene overlap, or trajectory duplication is unresolved;
- resumed training cannot reproduce the previous state because optimizer, scheduler, data position, or RNG is missing;
- repeated checkpoints show no meaningful improvement before the compute cap.

## 11. Related knowledge ownership

- Foundation objectives, packing, optimizer defaults, and mid-training mixtures are owned by [training.md](training.md).
- Dataset filtering, captions, action normalization, and manifests are owned by [data.md](data.md).
- Policy observation/action interfaces, serving, receding horizon, and safety wrappers are owned by [policy.md](policy.md).
- Metrics, learning curves, checkpoint selection, and comparison validity are owned by [evaluation.md](evaluation.md).
- Model risks and deployment limits are owned by [limitations.md](limitations.md).
- Unresolved research questions are registered in [research-queue.md](research-queue.md), while reusable experiment strategies are owned by [optimization-playbook.md](optimization-playbook.md).
- Actual run state and produced artifacts are owned by [reproduction.md](reproduction.md).
- Source IDs and fixed revisions resolve through [sources.yaml](sources.yaml).
