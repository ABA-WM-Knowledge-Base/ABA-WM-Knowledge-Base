---
id: world-model-kb.models.cosmos3-nano.data
title: Cosmos3-Nano Data and Curriculum Control Surface
kind: reference
status: maintained
last_updated: 2026-08-11
owners:
  - AIBuildAI world-model group
---

# Cosmos3-Nano Data and Curriculum Control Surface

## Retrieval metadata

**Relevant queries:** adaptation data, dataset composition, sampling mixture, coverage, contamination, leakage, action normalization, counting units, or data-induced regression.

**Knowledge provided:** published data state, mixture semantics, counting boundaries, controllable data variables, confounders, and reusable data-intervention hypotheses.

**Related pages:** [Training](training.md) covers objectives and optimizers; [Post-training](post-training.md) covers public recipes; [Evaluation](evaluation.md) covers protocols; [Modality contracts](modalities-and-io.md) covers I/O; [Reproduction](reproduction.md) covers executed state. [Datasets and supervision](../../foundations/data-and-evaluation/datasets-and-supervision.md) owns the model-independent data principles.

## 1. Data model: keep counting units and stages separate

Cosmos 3 uses two sequential curricula with incompatible counting units. Reasoner pre-training and SFT are reported as media samples or conversations. Generator stages are reported as images, clips, episodes, hours, samples, or tokens. A video may contribute visual, audio, action, and transfer supervision, and later stages may resample earlier pools. Never sum rows across stages into a unique-example total. [C3-TR, pp.15, 20, Figures 7–8 and Table 3]

The fixed Hugging Face model card separately reports `1.3B data points` and `393 dataset entries`, collected during 2024–2026. It does not define cross-stage or cross-modality deduplication for either term. Preserve this product-level count separately from the paper's stage-specific counts. [C3-HF, "Training, Testing, and Evaluation Datasets"]

| Curriculum | Stage | Reported scale | Primary capability pressure |
|---|---|---:|---|
| Reasoner | Multimodal pre-training | 22,002,013 samples | OCR, grounding, VQA, general vision-language reasoning, lightweight video priors |
| Reasoner | Physical AI SFT | 2,171,673 samples | Spatial-temporal reasoning, robotics, driving, infrastructure, prompt upsampling |
| Generator | Pre-training | 767M images; 347.7M videos; 138.9M usable-audio clips | General image, video, and audio priors |
| Generator | Mid-training | 15.6M images; 74.7M videos; 18.8M audio clips; 8.4M action episodes; about 4M transfer samples | Physical-AI tails, causal action interfaces, native controls |
| Specialist branches | Post-training | T2I Figure 8 label: 8M; I2V: about 20K synthetic clips plus other pools; policy Figure 8 label: 58K | T2I, I2V, or DROID specialization |

The approximate 4M transfer total combines 3M general control videos with 1.1M MADS samples; it is not a deduplicated exact count. Figure 8 summaries and prose component counts use different granularities and must remain distinct. [C3-TR, pp.20–22, Figure 8]

## 2. Reasoner data state

### 2.1 Mixture and capability distribution

Reasoner pre-training contains 18,814,952 image-text samples, 1,016,299 video-text samples, and 2,170,762 text-only conversations. SFT contains 1,051,513 image-text, 1,079,200 video-text, and 40,960 text-only samples. Media rows and conversation rows do not imply equal token budgets. [C3-TR, p.15, Table 3]

| Capability category | Pre-training share | SFT share | Optimization interpretation |
|---|---:|---:|---|
| OCR | 42.9% | — | Strong reading/layout prior; may dominate general image coverage |
| 2D grounding | 16.5% | 16.0% | Persistent localization supervision |
| Visual QA | 11.3% | 15.0% | General image reasoning retention |
| Image reasoning | 7.5% | — | Broad visual reasoning prior |
| Text QA / instruction | 6.1% / 3.7% | — | Language reasoning and instruction following |
| Image caption / visual instruction | 5.9% / 1.5% | 1.5% / — | Visual description and instruction grounding |
| Video QA | 4.5% | 21.4% | Strong SFT shift toward temporal understanding |
| Video caption / reasoning | 0.05% / 0.05% | 12.7% / 22.7% | Temporal reasoning becomes a core SFT objective |
| Prompt upsampling | — | 10.7% | Produces structured Generator-compatible scene descriptions |

Percentages are rounded Figure 7 values and need not sum to exactly 100%. Of the pre-training data, 19.7M samples were selected from the Nemotron Nano 2 collection and 2.3M supplemented mathematics, video, spatial grounding, and instruction following. [C3-TR, pp.15–17, Figure 7]

### 2.2 Deduplication and quality filtering

Treat the whole media-instruction-answer conversation as the deduplication unit; visually identical media paired with materially different tasks need not be duplicates.

1. Image-text and text-only samples use Qwen3-VL-Embedding-8B; video-text uses PE-Core-G14-448. Media and instruction-answer representations form a joint embedding.
2. Each modality is K-means clustered, with cosine near-duplicate detection restricted to a cluster. A `0.95` threshold removes 4.23%.
3. Gemma-4-31B-it scores faithfulness, completeness, and correctness from 1 to 5. A sample is retained only when every dimension meets the threshold; the score is not averaged.
4. Pre-training uses threshold 2 and retains about 78%; SFT uses threshold 5 and retains about 46%. The lower pre-training threshold preserves breadth; the SFT threshold favors high-confidence supervision. [C3-TR, pp.15–17]

The report does not expose the full source list, judge prompt, per-source errors, or filtering code. A compatible pipeline is possible; a data-equivalent reconstruction is not established.

### 2.3 Physical-AI SFT interfaces

| Stream | Reported scale or format | Capability trained |
|---|---|---|
| 2D/3D grounding | Points/boxes normalized to JSON; 3D boxes use camera-relative center, dimensions, orientation | Referring localization, free-space points, metric geometry, cross-view correspondence |
| Simulator-grounded spatial reasoning | Camera, pose/box, depth, mask, visibility, feasible regions; programmatic and VLM checks | Reference frames, affordances, metric geometry, viewpoint changes |
| Temporal event understanding | 55K videos, 2.6K hours, 743K `(t_start,t_end,caption)` triplets; atomic actions average 1.8 s | Event enumeration and temporal localization |
| Physics plausibility | 13.5K human-graded tuples from 1K generated videos; VideoPhy2: 3.4K videos, 200 actions, 1–5 score | Collision, gravity, causality, spatial constraints, visual stability |
| AV Action-CoT | 10K+ human driving videos; about 1.1M internal videos auto-annotated | Decision moments, critical objects, ego behavior, causal chains |
| AV temporal / 3D grounding | Nexar 24K+ clips; MADS multiview scenario maps and visible-vehicle 3D boxes | Collision timing and metric vehicle grounding |
| Robot Action-CoT | Qwen3-VL-72B reasoning, Molmo-7B localization, MolmoAct or DROID motion targets | Instruction-to-task-locations, 2D points, waypoints |
| Embodied reasoning | MimicGen 3.6K rerendered videos across 6 tasks; 60 held out; BEHAVIOR-1K 83K samples; ERQA | Subtask decomposition, long-horizon planning, affordances, failure detection |
| Robotic surgery | 398K multi-turn conversations over 2.2M images | Tool/state/phase reasoning, scene graphs, monitor OCR |
| Warehouse | 44 scene collections, 40 views; balanced 80K from 93K RGB-D images and 873K QA | Counting, metric distance, grounding, spatial relations |
| Dense pedestrian | 208K images, 44 scenes, 5.6M human boxes; identifiable information blurred | Dense fixed-camera localization |
| Traffic/anomaly | CARLA collision queries 3.4K; TAR 3.6K videos/26 h/44K annotations; 1K tailgating clips | Anomaly, temporal localization, causality, summaries |

Action-CoT produces inspectable text, points, and pixel-space waypoints. It is not the continuous joint-action interface used by Policy-DROID. [C3-TR, pp.17–19]

## 3. Generator visual data state

### 3.1 Raw-to-pre-training pipeline

The reported raw pool is 7.8B images and 3B source videos, reduced to 767M images and 347.7M clips. Videos are cut at scene changes with TransNetV2, black borders are removed with `ffmpeg cropdetect`, and media is uniformly encoded. Qwen3-VL-Embedding-8B handles images and Cosmos-Embed1-448p handles video. The authors sampled 147M images and 400M clips and built 20,000 cuML K-means clusters per modality for near-duplicate detection and concept balancing. [C3-TR, pp.20–21]

An internal VLM maps visual data to a 47-level category hierarchy. Images require an aesthetic threshold and reject collage, watermark, white background, and NSFW content; synthetic images not intended for text rendering also require a photorealism threshold. Videos use 0–9 DOVER aesthetic, DOVER technical, and VTSS suitability scores plus about 100 artifact tags. Major artifacts such as split-screen, rotation, and static video cause rejection; minor artifacts such as text overlay, motion blur, and compression noise are retained but tagged in pre-training. Thresholds and classifier weights are not public. [C3-TR, p.21]

Source-resolution shares are not batch-sampling shares. For images, 720p/480p/1080p+ represent 26.8%/26.0%/25.2%; for videos, 36.4%/30.8%/12.2%. A 16:9 aspect ratio covers 52.0% of images and 97.3% of videos; 1:1 is the second-most common image ratio at 25.2%. [C3-TR, p.20]

### 3.2 Mid-training rebalance and synthetic data

The 15.6M-image mid-training mixture samples 60% real, 36% synthetic, and 4% text-rendering data. The 74.7M-video mixture comprises 46.0% strictly filtered high-quality pre-training video, 43.9% domain data such as robotics, driving, human activity, and egocentric interaction, and 10.1% hard cases such as complex motion and fine manipulation. [C3-TR, pp.21, 29]

| Synthetic subset | Coverage target | Primary optimization use |
|---|---|---|
| SDG-PhyxSim | Rigid collision, articulation, deformables, fluids, optics | Physical interactions |
| SDG-RobotSim | Manipulation and locomotion for 6–8 embodiments | Robot coverage |
| SDG-DriveSim | Routine and corner-case driving | Safety-critical traffic dynamics |
| SDG-SynHuman | Human dynamics, camera motion, multi-person interaction | Human motion |
| SDG-Warehouse | Human-forklift interaction and warehouse safety | Industrial safety |

These sources occupy pre-training distribution tails. SDG-All improves the PAIBench-G overall score by `+0.10` with positive movement on 8/9 metrics, but Human decreases by `-0.47`; single-source mixtures cause larger cross-domain regressions. Treat synthetic data as a targeted intervention that requires real-data regularization and per-domain regression gates. [C3-TR, pp.104–105, Figures 35–36 and Tables 25–26]

### 3.3 Transfer controls and captions

General transfer uses 3M high-quality Physical-AI videos. Edge and blur controls are generated online with random parameters; depth and segmentation are precomputed with Video Depth Anything and SAMv2. Driving transfer uses 1.1M MADS samples with seven synchronized camera views, 30 FPS video, and a world-scenario-map per camera across 14 regions and 25 country-duration partitions. Controls enter Cosmos 3 as native input tokens, not separate per-control ControlNets. [C3-TR, pp.21–22, 63; T1-TR, pp.4–8]

All stages use structured JSON captions. Fields cover subject, background, lighting, aesthetics, and cinematography; video adds actions, state changes, physical interactions, camera motion, and segment-level temporal descriptions. Separate fine-tuned Qwen3-VL-8B models caption images and videos. Caption evaluation atomizes assertions: precision checks faithfulness against media and recall checks coverage against human assertions. The report does not expose a complete independently reproducible label set. [C3-TR, pp.22–23]

## 4. Audio and action data contracts

### 4.1 Audio

Pre-training uses 138.9M clips with usable tracks; 62.5M clips are under 30 seconds and receive Qwen3-Omni-Captioner descriptions. The broad pool may contain diegetic sound, voice-over, music, ambience, and speech. Mid-training narrows to 18.8M clips: 12.8M non-speech plus 6.0M visible-face synchronized speech. [C3-TR, pp.23–24]

The processing contract is part of the target distribution:

- SAM-Audio separates speech and residual stems. SyncNet requires `has_face=True` and `lip_sync_confidence>=3.0` for synchronized-speech candidates.
- FireRedASR2S estimates speech and music ratios. `music_ratio>=0.1` marks high music; Qwen3-VL checks visible instruments to avoid deleting performances.
- After background-music removal, speech requires `speech_ratio>=0.05` and `music_ratio=0`. After vocal removal, non-speech requires `speech_ratio<0.05`.
- Processed audio must satisfy `max_abs>=0.007`, `p50_db>=-80`, and `active_ratio>=0.2`.
- Any waveform modification triggers recaptioning. Synchronized speech uses Qwen3-ASR transcription, merged with acoustic descriptions by GPT-OSS-120B. [C3-TR, pp.23–24]

Source separation, ASR, lip-sync, and captioning errors compose. Do not optimize only final training loss without auditing intermediate precision and recall.

### 4.2 Action

Action mid-training comprises 8.4M episodes and 61.3K hours. [C3-TR, pp.24–25, Figure 9]

| Pillar | Hours / share | Source contract |
|---|---:|---|
| Egocentric motion | 41.3K / 67.4% | 1.7M proprietary episodes; head RGB/pose and 21 three-dimensional keypoints per hand |
| Autonomous vehicle | 10.0K / 16.3% | Internal Hyperion logs; vehicle-frame trajectories converted to front-wide-camera coordinates |
| Robotics | 5.4K / 8.7% | 516.7K episodes, 90.4K task labels; successes and failures retained |
| Camera motion | 4.6K / 7.5% | 1.9M clips after ViPE + DepthAnything3 metric-pose estimation and jitter/intrinsics filtering |

Robotics includes AgiBot 239.4K episodes/4.37K h, Franka Panda 76.3K/442 h, Google Robot 87.2K/351 h, WidowX-250 50.4K/100.1 h, UMI 38.3K/67 h, and UR 25.0K/35 h. The reported 90.4K tasks are source-defined labels, not necessarily semantically unique natural-language tasks. [C3-TR, p.25, Table 4]

Cross-embodiment unification uses state differences as pseudo-actions, per-dimension normalization to approximately `[-1,1]`, multiview canvas packing with layout metadata, and explicit idle-step counts for sampler balancing. This removes controller-private details but does not equalize control frequency, latency, compliance, or actuator dynamics. Preserve the raw action, transformed action, coordinate frame, rate, normalization statistics, and transform code in every adaptation manifest. [C3-TR, p.25]

## 5. Controllable data levers

| Lever | Change only when | Primary measurement | Required guardrail |
|---|---|---|---|
| Domain sampling weights | Target errors cluster by domain or embodiment | Target metric and per-domain regression matrix | Freeze total examples/tokens and optimizer budget |
| Real:synthetic ratio | Real coverage is sparse or tail events dominate | Tail capability plus visual-domain quality | Keep a real-data anchor; reject aggregate-only wins |
| Quality threshold | Label noise or artifacts are causal suspects | Retention curve, label audit, downstream score | Report coverage loss by domain/language |
| Failure/idle sampling | Policy lacks recovery or overpredicts no-op | Recovery success, false no-op rate | Do not silently remove hard negatives |
| Caption schema/detail | Prompt following or temporal semantics fail | Assertion precision/recall and generation score | Freeze captioner version and schema |
| Sequence/window length | Long-horizon failures dominate | Horizon-stratified metric | Match token and compute budgets |
| Action normalization/frame | Cross-embodiment transfer fails | Denormalized action error and closed-loop success | Validate units, bounds, rate, and invertibility |
| Multiview layout | Cross-view correspondence fails | Per-view and fused-view metrics | Freeze view order, resize, masking, timestamps |
| Control corruption parameters | Control robustness is inadequate | Control-fidelity curve versus corruption | Do not change target media concurrently |
| Audio filtering/synchrony | AV alignment or sound quality fails | AV lag, semantic score, low-level audio quality | Audit every filter stage, not only survivors |

## Candidate intervention patterns (not live queue items)

The following entries are reusable hypothesis templates, not active or prioritized experiments. Before execution, instantiate the selected pattern as a stable `RQ-*` item in [research-queue.md](research-queue.md) with explicit state, dependencies, experiment contract, and closure rule.

- **DATA-H01 — Targeted real-data rebalance:** increasing target-domain real samples while retaining a general replay anchor should improve Physical-AI domain scores with less forgetting than target-only SFT.
- **DATA-H02 — Mixture-matrix search:** action-domain pairs have non-monotonic transfer; pairwise and leave-one-domain-out searches should outperform an unexamined all-domain mixture.
- **DATA-H03 — Failure-aware policy data:** retaining and explicitly labeling failures should improve recovery and reduce confidently repeated failure, provided successful demonstrations remain dominant enough to identify the goal policy.
- **DATA-H04 — Temporal hard-negative curriculum:** near-identical clips with different event order or contact outcome should improve causal and temporal discrimination more efficiently than generic video scaling.
- **DATA-H05 — Caption consistency:** programmatically validated structured captions should improve prompt adherence without increasing hallucinated scene attributes; assertion-level precision is the gate.
- **DATA-H06 — Cross-embodiment canonicalization:** adding embodiment metadata, rate-aware deltas, and invertible normalization should reduce transfer interference versus state-difference vectors alone.
- **DATA-H07 — Synthetic-tail plus real anchor:** synthetic data should be introduced by capability deficit and gated by domain regressions; SDG-All is a precedent for balanced benefit, not proof that a larger synthetic share is better.
- **DATA-H08 — Uncertainty-preserving futures:** where multiple futures are valid, preserving multimodal outcomes or using trajectory-aware objectives should outperform pruning all but one deterministic target.

Only instantiated `RQ-*` records may carry dependency impact, evidence state, dependencies, or closure status in [research-queue.md](research-queue.md); reusable procedures belong in [optimization-playbook.md](optimization-playbook.md).

## 7. Experiment-record fields

A data-intervention claim is easier to interpret when its record includes:

1. source checkpoint and code revisions;
2. immutable dataset snapshot/hash and licenses;
3. counting unit for every row: image, clip, episode, conversation, hour, sample, or token;
4. source domain, embodiment, language, success/failure/idle labels, and train/validation/test split keys;
5. exact deduplication representation, clustering rule, similarity threshold, and cross-split leakage result;
6. filter/caption/judge versions, prompts, thresholds, retention rates, and a human-audited sample;
7. sampling weights before and after resampling, total examples/tokens, sequence buckets, media resolution/FPS, and action rate/frame;
8. transformation code and invertible statistics for audio, canvas packing, controls, and actions;
9. unchanged optimizer/steps/compute for data-only ablations;
10. target metrics plus general, domain, safety, and contamination guardrails over at least three seeds when stochasticity is material.

Use one-factor or factorial designs that expose interactions. A dataset change and an optimizer change in the same comparison do not identify a data effect.

## 8. Attribution-risk signals

A data-intervention claim is weak or invalid when any of the following holds:

- train/test identity, scene, trajectory, or near-duplicate leakage is unresolved;
- the counting unit or resampling denominator is unknown;
- normalization cannot be inverted exactly enough to reconstruct valid physical commands;
- a gain appears only under a changed judge, prompt rewriter, sampling budget, or checkpoint;
- aggregate improvement masks a predeclared regression in a safety-critical domain, embodiment, language, or long-horizon bucket;
- synthetic data improves in-domain fidelity but causes persistent real-domain regression beyond the guardrail;
- a filter removes a disproportionate subgroup without an audited task-quality justification;
- action timestamps, camera timestamps, or control frames are misaligned;
- failure or idle handling is undocumented;
- repeated scaling yields no statistically or practically meaningful gain under a fixed protocol.

## 9. Related knowledge ownership

- Loss functions, optimizer groups, packing, and stage schedules are owned by [training.md](training.md).
- Specialist checkpoint adaptation and public recipe execution are owned by [post-training.md](post-training.md).
- Metric definitions, baselines, seeds, judges, and comparison rules are owned by [evaluation.md](evaluation.md).
- Model-level failure modes and safety evidence are owned by [limitations.md](limitations.md).
- Executable policy I/O and canvas/action contracts are owned by [policy.md](policy.md).
- Unresolved research questions are registered in [research-queue.md](research-queue.md).
- Actual run state, artifacts, and reproduction claims are owned by [reproduction.md](reproduction.md).
- Source IDs and fixed revisions resolve through [sources.yaml](sources.yaml).
