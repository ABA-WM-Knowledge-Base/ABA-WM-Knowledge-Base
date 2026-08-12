---
id: world-model-kb.models.cosmos3-nano.generator
title: Cosmos3-Nano Generator Optimization Reference
kind: reference
status: maintained
last_updated: 2026-08-11
owners:
  - AIBuildAI world-model group
---

# Cosmos3-Nano Generator Optimization Reference

## Retrieval metadata

**Relevant queries:** image, video, audiovisual, or continuous-modality generation; conditioning; temporal or physical rollout errors; sampler settings; or Generator action representations.

**Knowledge provided:** Generator mechanisms, task surfaces, condition and target semantics, sampling variables, training lineage, failure interpretations, and published evaluation anchors.

**Related pages:** [Reasoner](reasoner.md) covers text output; [Action modeling](action-modeling.md) covers action schemas; [Policy](policy.md) covers DROID control; [Reproduction](reproduction.md) records actual load and run outcomes. Foundation owners cover [video world models](../../foundations/representations/video-world-model.md), [autoregressive modeling](../../foundations/learning-objectives/autoregressive-modeling.md), and [diffusion and flow matching](../../foundations/learning-objectives/diffusion-and-flow-matching.md).

## Identity and strict boundaries

Cosmos3-Nano Generator is the approximately 8B diffusion tower within unified Nano. It performs rectified-flow denoising over continuous DM representations while consuming AR semantic context and optional clean DM conditions. It supports image, video, audiovisual, transfer, and action-related surfaces according to checkpoint, adapter, and mode.[C3-TR, pp.9-14, Figures 4-6]

Generator is not:

- the hosted Reasoner model `nvidia/cosmos3-nano-reasoner`;
- Wan2.2 itself, although it uses the frozen Wan2.2-TI2V-5B VAE;
- a single checkpoint that necessarily contains every post-trained T2I, I2V, transfer, or policy capability;
- `nvidia/Cosmos3-Nano-Policy-DROID`;
- a verified physical simulator merely because it produces plausible video.

Published results must remain attached to their checkpoint surface, task mode, resolution, frame count, prompt transformation, seed count, denoising settings, and evaluator.

## Canonical mechanisms and invariants

### Asymmetric conditioning

Generator has tower-specific projections, MLPs, and diffusion-time conditioning. DM queries can attend to AR and DM states, allowing language, visual-semantic tokens, and clean continuous conditions to guide denoising. AR queries do not read DM states.[C3-TR, pp.11-14, Figures 5-6]

This is a unified transformer interaction, not a loose pipeline in which a VLM writes a prompt for an unrelated video model. It is also not a bidirectional reasoning loop. A generated rollout must be decoded and re-encoded for later Reasoner critique.

### Visual latents

Image/video data uses a frozen Wan2.2-TI2V-5B VAE with approximately 4x temporal and 32x32 spatial compression. Generator learns a vector field in latent space; the VAE decoder recovers pixels.[C3-TR, pp.7-10, Figures 3-4]

The VAE path is distinct from Reasoner's ViT visual tokens. Small-object, contact, text-rendering, and high-frequency errors may originate in the frozen codec rather than the transformer. Before tuning Generator, run a VAE round-trip diagnostic on the exact task frames.

### Rectified flow

Generator predicts a continuous velocity field from noisy state toward data state and samples with ODE-style updates. `num_steps`, classifier-free `guidance`, and `flow_shift` jointly affect fidelity, motion, adherence, latency, and variance.[C3-TR, pp.27-30 and p.73, Table 21]

Fifty steps is a published task setting, not an architecture constant. Policy-DROID uses four steps for latency; do not transfer that setting to general video generation without an ablation.

### Audio latents

The frozen audio VAE operates on 48 kHz stereo with hop size 1,920, producing approximately 25 latent tokens per second. Audio is a DM modality and can be modeled jointly with visual latents. Current Reasoner-only interfaces do not accept audio.[C3-TR, pp.7-9, Figure 3; C3-REASONER-COOKBOOK]

### Actions and structured controls

Actions and controls such as edge, depth, or segmentation enter through dedicated projections or adapters as DM conditions or targets. Shared hidden size does not remove domain-specific shapes, units, normalization, time scale, or condition ordering.[C3-TR, pp.7-10; C3-FW-ARGS; C3-FW-ACTION]

## Task surfaces

| Surface | Conditions | Target | Optimization focus |
|---|---|---|---|
| T2I | text | image | semantic layout, text rendering, physical state, fidelity |
| T2V | text | video | motion, temporal coherence, prompt adherence |
| I2V | text and initial image | future video | initial-state preservation and plausible evolution |
| V2V | text and video/control | transformed or continued video | control adherence and temporal consistency |
| Audio-image-to-video | text, image, and audio configuration | synchronized media | audiovisual alignment and media quality |
| Forward dynamics | observation and action | future observation | action sensitivity and transition accuracy |
| Inverse dynamics | observed transition | action | feasible multimodal action recovery |
| WAM | observation/instruction | action and future visual state | self-consistency between proposal and rollout |

[C3-TR, pp.5-10 and pp.27-32; C3-FW-INFERENCE; C3-FW-ARGS]

General media generation and action-domain modeling require different adapters and evaluation. FD, ID, and WAM details are owned by [action-modeling.md](action-modeling.md); DROID-specific closed-loop behavior is owned by [policy.md](policy.md).

## Training lineage

### Generator pre-training

Generator starts from the trained Reasoner semantic path. During Generator pre-training, Reasoner is frozen while Generator learns rectified-flow objectives for image, video, and audio.[C3-TR, pp.27-30]

The report describes 256p, 480p, and 720p data at approximately 10-30 FPS. Nano pre-training processes approximately 31.05T packed tokens on 1,024 GB200 GPUs, followed by approximately 2.4T mid-training tokens on 1,024 GB200 GPUs.[C3-TR, pp.27-30] These numbers define the scale of the published full recipe; they do not define the minimum viable adaptation experiment.

### Action-inclusive mid-training

The reported mid-training mixture is:[C3-TR, p.30, Table 6]

| Data component | Share |
|---|---:|
| Image | 10% |
| Video | 32% |
| Video plus audio | 8% |
| Action | 25% |
| General transfer | 20% |
| Driving transfer | 5% |

This mixture explains how action and transfer surfaces enter base Nano. It does not imply equal domain coverage or a ready adapter for every robot.

### Task-specific post-training

T2I, I2V, DROID policy, LIBERO, and other task surfaces may use specialized post-training. Do not treat the best score from a specialized branch as zero-shot output from base `nvidia/Cosmos3-Nano`.[C3-TR, pp.30-32] Use [post-training.md](post-training.md) for checkpoint lineage and [training.md](training.md) for update/freeze rules.

## Sampling contract

Representative published defaults are:[C3-TR, p.73, Table 21]

| Task | Denoising steps | Guidance | Flow shift |
|---|---:|---:|---:|
| Nano audiovisual generation | 50 | 6 | 10 |
| Nano forward/inverse dynamics | 50 | 1 | 5 |
| Policy-DROID | 4 | 3 | 5 |
| Transfer | 50 | text 3 / control 1.5 | 10 |

Do not copy these settings across tasks without a sweep. Prompt upsampling is another system variable: it expands a short prompt with subject, scene, action, camera, and style details. Hold it fixed or ablate it in checkpoint comparisons.[C3-TR, pp.73-75]

The fixed Framework caps generated length by resolution: 256p up to 400 frames, 480p up to 300, 704/720/768p up to 200, and 1080p image-only. These runtime limits differ from the report's training envelope and must be taken from the pinned code for each run.[C3-FW-ARGS; C3-FW-FAQ; C3-TR, pp.27-30]

## Optimization objectives

Do not optimize a single visual-preference score when the desired behavior is world modeling. Use a metric stack:

| Objective | Direct measurement | Failure hidden by generic visual quality |
|---|---|---|
| Codec fidelity | VAE round-trip PSNR/LPIPS plus task-state preservation | information already lost before Generator |
| Visual fidelity | artifact, blur, texture, and perceptual metrics | physically wrong but attractive motion |
| Condition adherence | entity, action, control, and initial-state consistency | unconditional continuation |
| Temporal consistency | identity, geometry, occlusion, state persistence | frame-wise quality with drift |
| Physical plausibility | contact, support, collision, penetration, gravity, conservation proxies | visually plausible physical violation |
| Action sensitivity | divergence under controlled action counterfactuals | rollout ignores action |
| Transition accuracy | object/state/pose error against real transition | plausible but inaccurate future |
| Calibration and diversity | per-seed variance, coverage, selector gain | best-of-N hides unreliable single samples |
| Task utility | candidate-ranking or downstream-control gain | accurate-looking rollout that does not improve decisions |

For action-conditioned world modeling, task-state metrics should dominate purely pixel-level metrics. For media generation, keep condition adherence and temporal/physical scores separate from aesthetic quality.

## Optimization levers

### Select the bottleneck

| Failure signature | First lever | Escalation | Required control |
|---|---|---|---|
| Initial image details disappear | VAE preprocessing, condition index, DM projection | visual projection or Generator tuning | VAE round trip and valid/shuffled/no-condition comparison |
| Motion is weak or frozen | prompt detail, guidance, shift, motion data mix | temporal Generator tuning | fixed-seed sampler grid |
| Long-horizon identity drifts | horizon curriculum, temporal positions, receding-window strategy | selective tower tuning | matched duration sweep |
| Contact or containment is wrong | contact-rich data, state/contact auxiliary losses | Generator adaptation | annotated single-contact counterfactuals |
| Action has little effect | action normalization, projection, sequence-plan position, loss weight | action-inclusive tuning | opposite-action pairs with identical seed |
| Audio-video timing drifts | timestamp conversion and joint sampling | cross-modal training | event-onset alignment |
| Text rendering fails | VAE bottleneck and T2I data | specialized post-training | OCR metrics and codec diagnostic |
| Best-of-N gain is large | high sample variance or strong external selector | distribution or consistency training | report N, selector, cost, and single-sample mean |

### Adapter and objective changes

Prefer the narrowest intervention that can affect the diagnosed error:

1. correct I/O, condition ordering, timestamps, and sampling;
2. tune modality projection or domain adapter;
3. adjust data mixture and loss weights;
4. add task-state, contact, or action-consistency auxiliary targets;
5. selectively unfreeze Generator blocks;
6. change the codec or architecture only when round-trip and frozen-backbone tests show the need.

If a new loss rewards state accuracy, test whether it degrades visual quality or diversity. If Reasoner is unfrozen, include Reasoner retention probes because AR context is a conditioning source.

### Candidate generation and selection

Best-of-N can improve outcomes but changes the system. Report:

- N and seed policy;
- selector model, checkpoint, and input information;
- single-sample mean and distribution;
- best-of-N score and total generation cost;
- selector accuracy against real transitions;
- latency and throughput.

A useful early application is offline counterfactual ranking: generate candidate rollouts for proposed actions, measure state/contact outcomes, and compare rankings with true environment transitions. Only move online after calibration and latency are adequate.

## Diagnostics and failure signatures

| Signature | Likely cause | Minimum diagnostic |
|---|---|---|
| Weak or static motion | short prompt, sampler mismatch, initial image dominance | prompt-upsampling and sampler grid with fixed seeds |
| Geometry or identity drifts over time | accumulated latent error or insufficient long-range state | windowed identity, object-count, and pose metrics |
| Objects penetrate or jump after contact | contact-data or objective deficiency | frame-level contact labels and constraint-violation metrics |
| I2V ignores first-frame details | codec compression, condition index, or guidance | verify preprocessing and compare VAE reconstruction |
| Audio and visual events are offset | time-base or joint-sampling mismatch | onset-time error for paired events |
| Text is malformed | codec and data limitation | OCR evaluation isolated from overall image score |
| Output length is clipped or run OOMs | resolution cap or memory | validate legal frame count and record peak memory |
| Guardrail blur or rejection appears as model failure | system post-processing | preserve raw/filtered distinction and guardrail state |
| Rollout looks good but ranks actions incorrectly | weak action sensitivity or wrong transition | compare predicted versus real counterfactual ordering |
| FD changes when prompt changes but not when action changes | language dominates action condition | prompt/action factorial ablation |

Prior Cosmos generations reported risks in object permanence, contact dynamics, gravity, lighting, and fluids. Use them to prioritize probes, not as claims that Cosmos3-Nano has already failed those tests.[C1-TR, p.58]

## Published evaluation anchors

Published values provide protocol anchors, not universal optimization targets.

### Text-to-image

Nano reports UniGenBench All 84.61, UniGenBench Physics 82.12, GNED text rendering 24.23, PNED text rendering 26.53, and HPS 8.99.[C3-TR, p.55, Table 11] These metrics have different scales and directions and must not be averaged into one quality score.

### Text/image-to-video

| Evaluation | Mode | Nano result | Protocol note |
|---|---|---:|---|
| PAIBench | T2V | 79.4 | 720p, 16:9, 189 frames, 5 seeds |
| PAIBench | I2V | 82.7 | related Physical AI video protocol |
| RBench | video | 58.4% | 720p, 121 frames, 1 seed |

[C3-TR, p.57, Table 12]

The authors state that the public PAIBench judge result was not reproducible and used Qwen2.5-VL-72B as judge. Preserve this evaluator change when comparing results.[C3-TR, p.57, Table 12 footnote]

### Physics and sample selection

Physics-IQ reports Nano direct I2V 40.2 and V2V 50.2; best-of-N increases them to 43.8 and 57.7.[C3-TR, p.58, Table 13] The best-of-N rows include sampling and selection capability and are not single-generation scores.

### Human and audiovisual evaluation

HUE Table 14 reports T2V 87.6 and I2V 88.6, with HWB 66.9. Nearby prose states I2V 88.5; preserve the 0.1 internal inconsistency and use the table value as the table record.[C3-TR, p.59, Table 14]

For audiovisual generation, Nano reports AVQ 7.34, SAV 8.35, SA 8.33, AVAlign 8.16, and PQ 6.32; the report identifies low-level audio fidelity as an improvement area.[C3-TR, pp.61-62, Table 15]

See [evaluation.md](evaluation.md) for full baselines, metric directions, and transfer protocols.

## Serving and resource diagnostics

Generator deployment includes PyTorch and vLLM-Omni paths, with context/KV caching, classifier-free guidance, and context parallelism. Throughput depends on GPU count, concurrency, resolution, and frames. Adjacent report descriptions on pp.45-46 differ in GPU-count wording; do not extract a throughput number without the full configuration.[C3-TR, pp.45-49]

Framework entry is `python -m cosmos_framework.scripts.inference`, with `model_mode` selecting the task. Resolved argument priority is CLI over input file over mode defaults.[C3-FW-AGENTS; C3-FW-INFERENCE; C3-FW-FAQ]

A Reasoner-only load filters Generator, audio, and action parameters. Media generation requires the Generator path, modality projections, and codecs.[C3-REASONER-COOKBOOK; C3-FW-MODEL]

## Experiment guidance

Each Generator experiment must record:

- checkpoint ID, revision, and base/mid/post-trained lineage;
- code commit, backend, loaded codecs, and enabled modality flags;
- mode, raw and upsampled prompts, conditions, condition indices, media hashes, resolution, frame count, FPS, and timestamps;
- seed list, steps, guidance, flow shift, precision, and guardrail state;
- trainable/frozen modules, data mixture, loss weights, and initialization;
- codec, condition, temporal, physical, action, calibration, and task metrics;
- resource use and total cost, including best-of-N selection.

Minimum ablation set for an action-conditioned rollout:

1. VAE reconstruction upper bound;
2. valid action versus zero action;
3. valid action versus opposite action;
4. valid action versus temporally shuffled action;
5. matched-seed prediction versus real transition;
6. short- versus long-horizon error;
7. state/contact metrics versus pixel metrics;
8. single sample versus best-of-N.

Persist real outcomes in [reproduction.md](reproduction.md). Promote repeatable, decision-relevant patterns to [optimization-playbook.md](optimization-playbook.md). Queue unresolved questions about codec bottlenecks, branch identity, and rollout utility in [research-queue.md](research-queue.md).

## Related knowledge

- Architecture and attention direction: [architecture.md](architecture.md)
- External I/O contracts: [modalities-and-io.md](modalities-and-io.md)
- Action representation and objectives: [action-modeling.md](action-modeling.md)
- Policy-DROID: [policy.md](policy.md)
- Data, training, and checkpoint lineage: [data.md](data.md), [training.md](training.md), [post-training.md](post-training.md)
- Published evaluation and limitations: [evaluation.md](evaluation.md), [limitations.md](limitations.md)
- Source registry: [sources.yaml](sources.yaml)
