---
id: world-model-kb.models.cosmos3-nano.evaluation
title: Cosmos3-Nano Evaluation and Optimization Decision Rules
kind: reference
status: maintained
last_updated: 2026-08-11
owners:
  - AIBuildAI world-model group
---

# Cosmos3-Nano Evaluation and Optimization Decision Rules

## Retrieval metadata

**Relevant queries:** benchmark, metric, baseline, reported result, evaluator, regression, ablation, protocol conflict, leaderboard, or comparison validity.

**Knowledge provided:** checkpoint- and protocol-bound published results, evaluator conditions, aggregation rules, confounders, capability slices, and comparison-validity criteria.

**Related pages:** [Training](training.md) contains learning configuration; [Post-training](post-training.md) contains adaptation recipes; [Inference](inference.md) contains runtime references; [Limitations](limitations.md) contains risk boundaries; [Reproduction](reproduction.md) contains local results. [Evaluation methodology](../../foundations/data-and-evaluation/evaluation-methodology.md) owns the model-independent evidence and comparison principles.

## 1. Comparison key and score grammar

The minimum identity of a Cosmos 3 result is:

```text
checkpoint hash + code revision + task mode + dataset/split
+ prompt rewriter/template + generation/sampling config + seeds/rollouts
+ resolution/FPS/frames + evaluator/judge version + aggregation rule + run date
```

If any identity field differs, label the result as a new protocol rather than an improved model. Official infrastructure separates generation from scoring and records checkpoint, code, generation settings, and benchmark parameters; the paper does not expose every run manifest. Reasoner evaluation uses VLMEvalKit with a vLLM endpoint. [C3-TR, pp.49–50]

Apply these invariants before comparison:

1. Base Nano, standalone Nano Reasoner, PT-init, MT-init, and Policy-DROID are different checkpoints.
2. Artificial Analysis T2I/I2V results use Super specialist checkpoints, not base Nano.
3. Generator benchmarks commonly rewrite raw prompts into structured JSON; raw-prompt and rewritten-prompt systems are different systems.
4. Direct sampling, best-of-N plus reranking, and dynamic leaderboard snapshots use different inference budgets.
5. An automatic proxy, a human preference score, physical consistency, and closed-loop success are not interchangeable. [C3-TR, pp.53–60, 68–73]

For optimization, retain a metric vector with at least target capability, general retention, domain/embodiment slices, physical or safety validity, latency/compute, and failure severity. Do not select checkpoints by a single aggregate unless the deployment objective explicitly equals that aggregate.

## 2. Reasoner baseline state

The Reasoner is evaluated on 48 benchmarks through VLMEvalKit + vLLM: General 19, Robotics 17, Smart Infrastructure 9, and Driving 3. Relative to Qwen3-VL-8B, Nano's reported gains concentrate in Physical AI. [C3-TR, pp.51–53, Table 10]

| Group | Cosmos3-Nano | Qwen3-VL-8B | Delta | Interpretation boundary |
|---|---:|---:|---:|---|
| General | 69.6 | 68.9 | +0.7 | Broad VQA/OCR/spatial/video/logical capability is mostly retained, not transformed |
| Robotics | 55.1 | 48.5 | +6.6 | Affordance, task reasoning, grounding, geometry, cross-view, surgery |
| Smart infrastructure | 61.0 | 52.7 | +8.3 | VANTAGE and TAR fixed-camera spatial-temporal tasks |
| Driving | 76.0 | 46.4 | +29.6 | LingoQA plus two small NVIDIA internal safety classifiers; only three benchmarks |

General includes MMBench-Dev, RealWorldQA, CVBench, VideoPhy2, CausalVQA, MVBench/MVPBench, CountBenchQA, AI2D, DocVQA, InfoVQA, OCRBench-v2, LogicVista, MMMU-Pro, HallusionBench, IFBench, BlinkSpatial/Depth, and RefCOCO. Nano remains below Gemini 3.1 Pro on the reported General aggregate and slightly below it on Robotics; do not claim universal leadership. [C3-TR, pp.51–53]

Smart Infrastructure includes 3,346 VANTAGE assets and 35,027 expert annotations plus TAR. Driving's AVSpecialCollisionBench contains 100 videos in each of collision/near-collision/no-collision; AVSpecialStopBehaviorBench contains 10 videos in each of five classes. Do not extrapolate the `+29.6` group delta to unrestricted driving understanding. [C3-TR, p.53]

**Optimization use:** diagnose by subgroup and task family. A Robotics gain accompanied by General regression suggests specialization/forgetting; a Driving gain restricted to internal classifiers suggests evaluator or distribution dependence; a temporal gain with grounding loss suggests mixture or representation interference.

## 3. Base Nano image-generation baseline

T2I evaluation generates 1024×1024 images. Claude Opus 4.7 rewrites prompts to structured format; open baselines use recommended parameters and negative prompts. [C3-TR, pp.53–55]

| Benchmark | Nano | Protocol and optimization signal |
|---|---:|---|
| UniGenBench All | 84.61 | 600 original + 570 Physical-AI prompts; Gemini 3.1 Pro binary judge; aggregate semantic testpoint accuracy |
| UniGenBench Original / Physical AI | 87.32 / 82.12 | Physical-AI semantics are the harder slice |
| CVTG-500L GNED / PNED | 24.23 / 26.53 | 500 English dense-text prompts; OCR + Hungarian matching; strong text-rendering deficit |
| CVTG-102ch GNED / PNED | 4.63 / 9.70 | 102 Chinese scene-text prompts; not reliable Chinese text rendering |
| Aesthetic v2 / HPSv3 | 5.76 / 8.99 | Prompt-independent aesthetics versus prompt-aware preference; not substitutes |

High UniGenBench semantic alignment does not cancel low scene-text accuracy. The Super-Text2Image score 91.36 and its leaderboard state belong to a specialist. [C3-TR, pp.54–56, Table 11 and Figure 18]

**Optimization use:** separate semantic alignment, typography/OCR, aesthetics, and prompt-conditioned preference. A typography intervention must gate UniGenBench and general visual quality; a semantic intervention must not claim text-rendering progress from aggregate gains.

## 4. Base Nano video and physics baseline

Video benchmarks use Claude Opus 4.6 structured prompt rewriting. [C3-TR, p.56]

### 4.1 PAIBench-G and RBench

PAIBench-G prose reports 1,044 image-text pairs: Human 299, AV 239, Common Sense 174, Robotics 107, Physics 107, Industry 107. These categories sum to 1,033, leaving an unresolved difference of 11. Quality aggregates frame consistency, motion smoothness, aesthetics, and video-text alignment. Domain is a VLM binary judge. `Overall = 0.5*Quality + 0.5*Domain`. Each prompt uses five seeds at 720p, 16:9, 189 frames. [C3-TR, pp.56–57]

| Mode | Overall | Domain | Quality |
|---|---:|---:|---:|
| Nano T2V | 79.4 | 85.8 | 73.0 |
| Nano I2V | 82.7 | 87.2 | 78.1 |

The public PAIBench-G I2V leaderboard uses Qwen3-VL-235B-A22B; the paper table uses Qwen2.5-VL-72B-Instruct because the authors could not reproduce public results. Bind 79.4/82.7 to the paper's judge and never merge them directly with public scores. [C3-TR, p.57, footnote 2]

RBench uses 650 robotics I2V cases: 250 task-oriented and 400 embodiment-specific. Task Completion and Visual Quality are equally weighted. Nano uses one seed, 720p, 16:9, 121 frames and scores 58.4%. Its seed and horizon differ from PAIBench-G. [C3-TR, p.57, Table 12]

### 4.2 Physics-IQ

Physics-IQ contains 396 real scenes spanning solid mechanics, fluids, optics, thermodynamics, and magnetism under three fixed views. I2V predicts after a switch frame; V2V receives three seconds and predicts five. Scoring combines spatial overlap, temporal alignment, magnitude-weighted agreement, and pixel error, normalized by a real-versus-real upper bound. [C3-TR, pp.57–58]

| Nano mode | Direct | WMReward + best-of-N |
|---|---:|---:|
| I2V | 40.2 | 43.8 |
| V2V | 50.2 | 57.7 |

Best-of-N includes extra generation and reranking. The report does not state Nano's `N` in this section, so compute cannot be reconstructed from Table 13 alone. [C3-TR, p.58, Table 13]

### 4.3 Human evaluation

Cosmos-HUE samples 100 fixed PAIBench-G prompts according to the original domain distribution, five seeds per model and prompt, for 500 videos. GPT 5.2 powers Domain Strategist, Scene Parser, and Auditor stages that generate up to 20 atomic Yes/No/Unclear questions. Two annotators score independently; a reviewer resolves disagreement. Dimensions are Semantic Alignment, Physical Laws, Geometric Reasoning, and Visual Integrity. `Unclear` remains in the denominator as a failure. [C3-TR, pp.58–59, 110]

Nano HUE T2V is 87.6. Table 14 gives I2V 88.6 while adjacent prose gives 88.5; preserve both values. HWB uses 180 EgoVerse egocentric manipulation samples and averages instruction-following and physical-plausibility pass rates; Nano scores 66.9. [C3-TR, pp.59–60, Table 14]

Human evaluation expands failure coverage but remains dependent on question generation, sample selection, seed, reviewer, and rubric. HUE is not a direct probability that a rollout obeys physics.

## 5. Audio-video and native-control baselines

### 5.1 Audio-video

Cosmos-SoundBench uses 144 non-speech FoleyBench prompts and five seeds each. Claude Opus 4.7, Gemini 3.1 Pro, and GPT 5.5 majority-vote to construct auditory and visual checklists; Gemini 3.1 Pro Preview observes visuals without the prompt; semantic scoring is repeated three times and averaged. [C3-TR, pp.61–62]

`SAV = 0.60*SA + 0.30*AVAlign + 0.10*VisualSupport`; `AVQ = 0.5*SAV + 0.5*PQ`. Nano reports AVQ 7.34, SAV 8.35, SA 8.33, AVAlign 8.16, Visual Support 9.10, and PQ 6.32. Strong semantics and synchronization coexist with weaker production quality. [C3-TR, pp.61–62, Table 15]

### 5.2 General spatial controls

PAIBench-C contains 600 clips: 200 each from AgiBot, OpenDV, and Ego-Exo-4D. Each run provides exactly one of blur, edge, segmentation, or depth; the corresponding signal is re-extracted from generated video and compared with reference. [C3-TR, p.63]

| Metric | Nano | Direction |
|---|---:|---|
| DOVER | 10.39 | higher is better |
| Segmentation mIoU | 0.72 | higher is better |
| Blur SSIM | 0.91 | higher is better |
| Edge F1 | 0.49 | higher is better |
| Depth si-RMSE | 0.62 | lower is better |

This demonstrates competitive single-control fidelity with native control tokens. It does not test arbitrary combinations of controls. [C3-TR, p.63, Table 16]

### 5.3 Driving world-scenario-map

AVBench-C contains 486 single-view driving clips. Automated metrics cover ego drift, dynamic/static object correspondence, and environment VLM score; humans rate video quality and lane fidelity on 1–3 scales. Nano reports ego drift 0.003, dynamic object 0.67, static object 0.41, environment 0.90, video quality 2.82, and lane line 2.50. Internal data and evaluators are involved; small differences such as Nano 2.50 versus Super 2.45 lane score do not establish general driving superiority. [C3-TR, pp.63–64, Table 17]

## 6. Action and policy baselines

### 6.1 PT-init versus MT-init

The report holds architecture scale, downstream data, recipe, and compute budget constant and changes whether initialization includes cross-domain action mid-training. [C3-TR, p.65]

| Interface | Nano PT-init | Nano MT-init | Measurement boundary |
|---|---:|---:|---|
| AV inverse dynamics | RRE .249 / RTE .017 / ATE 1.20 | .211 / .014 / .98 | Internal 6 s, 10 FPS clips; lower is better |
| Camera forward dynamics | .172 / .034 / 1.61 | .147 / .029 / 1.24 | 100 five-second clips; DepthAnything3 estimates generated-camera trajectory |
| Egocentric forward dynamics | 15.22 dB | 16.12 dB | HWB action annotations; PSNR |
| Robotics forward dynamics | 23.24 dB | 25.52 dB | DROID; initial frame + 16 actions → 16 frames |

PSNR compares a generated future to one recorded future. Multiple futures may be valid; high PSNR does not imply policy success, and low PSNR need not imply invalid action effects. [C3-TR, pp.65–67, Table 18]

### 6.2 Closed-loop policy

RoboLab-120 runs ten rollouts per task. Policy-DROID vague/default/specific success is 20.6%/36.8%/39.7%; PT-init control is 16.7%/28.1%/30.2%. Under specific instructions, simple/moderate/complex success is 42.0%/40.3%/29.4%. [C3-TR, pp.67–68, Table 19]

RoboArena rank one is a 2026-05-30 14:40 snapshot. MolmoSpaces rank one is dated 2026-06-20, with All Combined oracle success 39.0%. Preserve dates and protocols for dynamic leaderboards. [C3-TR, pp.68–70, Figures 26–27]

LIBERO-10 uses ten validation tasks and 500 rollouts per checkpoint. At 500/1,000/1,500/2,000 iterations, MT-init scores 24.6/91.4/95.8/97.4 and PT-init 0.0/73.8/93.4/95.2. MT-init's strongest advantage is early adaptation; the final difference is 2.2 points. [C3-TR, pp.69–70, Table 20]

**Optimization use:** report cost-to-threshold, area under the learning curve, and final success. A source checkpoint can be valuable through sample efficiency even when asymptotic scores converge.

## 7. Causal ablation state

| Hypothesis | Controlled setup | Result | Valid inference / boundary |
|---|---|---|---|
| Synthetic data improves Physical AI | Same Nano pre-trained baseline; individual SDG or SDG-All; PAIBench-G T2V | SDG-All Overall `+0.10`, 8/9 positive; Human `-0.47`; larger single-source regressions | Balanced synthetic mixtures can help; more synthetic data is not monotonically better [C3-TR, pp.104–105, Table 26] |
| Reasoner initialization helps Generator | Generator from scratch; Qwen3-VL-8B versus Nano Reasoner; 90K iter, 256 GPUs | T2V Domain `73.7→75.7`, Robot `+4.8`; Quality flat | Physical-AI representation benefit, not universal visual-quality gain [C3-TR, p.107, Table 28] |
| Text and MRoPE FPS control are complementary | Four models; 130K iter, 128 GPUs; 10/15/24/30 FPS; about 100 videos × 3 seeds | composite `8.51→9.28→9.63→9.81` | Gain is primarily motion fidelity [C3-TR, pp.107–108, Table 29] |
| Audio pre-training harms video | Same checkpoint; 20K iter, 128 GPUs; with/without audio | T2V `78.6→79.1`; I2V `81.7→82.2` | No harm in this short ablation; does not explain final audio quality [C3-TR, pp.108–109, Table 30] |
| Action modes share representations | PushT + Cosmos3-Edge; 2K steps per single mode, 6K joint | ID MSE `-72%`; policy coverage `74.1→77.3`; FD PSNR `27.13→26.22` | Sharing plus interference; not Nano-DROID magnitude [C3-TR, p.109, Table 31] |
| Policy video and action outputs agree | Policy-DROID trained only on DROID; held-out RoboLab | left 23.19 dB; wrist 17.33 dB | Short-term stream consistency; not success or safety [C3-TR, pp.109–110, Figure 37] |

Pairwise action-domain matrices show both positive transfer and interference. Camera motion often benefits from robot/AV domains; WidowX and Google Robot combinations are frequently positive; small Franka subsets may saturate or interfere. Egocentric warmup improves AgiBot FD PSNR at every measured step. Use mixture matrices and leave-one-domain-out experiments, not only all-data versus single-domain comparisons. [C3-TR, pp.70–72, Figures 28–29]

## 8. System-performance baselines

The fixed `NVIDIA/cosmos` commit publishes an engine/hardware inference matrix distinct from capability evaluation. [C3-INFERENCE-BENCHMARKS]

| Surface | Workload and metrics | Variables required for comparison |
|---|---|---|
| Nano Generator | T2I/T2V/I2V via PyTorch, vLLM-Omni, Diffusers, NIM | precision, batch, sampler, prompt, seed; timing boundary differs across engines and NIM uses an FP8 profile |
| Nano Reasoner | vLLM text/image/video serving | input/output tokens, video FPS, TTFT, request latency, request/output throughput, client concurrency |
| Action/policy | forward dynamics, inverse dynamics, policy generation | action dimension, frames, denoising steps, visual decode, GPU count |

For Nano Reasoner on RTX PRO 6000 Blackwell with `Input 50 / Output 1 / Video 1 FPS`, concurrency 1→256 changes request latency 187.59→19,541.84 ms and throughput 5.29→9.89 requests/s. This is a queueing throughput/tail-latency trade-off, not a model-quality score. [C3-INFERENCE-BENCHMARKS, "Cosmos3-Nano Reasoner"]

Blank official cells mean unmeasured, not unsupported. Record engine/container, precision, GPU, parallelism, resolution/FPS/frames, warmup, timing boundary, and concurrency. Command references are owned by [inference.md](inference.md).

## 9. Known protocol conflicts

| Item | Preserve exactly | Decision rule |
|---|---|---|
| PAIBench-G count | prose total 1,044; listed categories sum to 1,033 | Retain unresolved difference of 11; do not redistribute |
| HUE Nano I2V | Table 14: 88.6; prose: 88.5 | Cite both or the table value with conflict note |
| PAIBench-G judge | public: Qwen3-VL-235B-A22B; paper: Qwen2.5-VL-72B | Never compare naked scores across judges |
| Artificial Analysis | Super T2I/I2V specialists; snapshot 2026-05-28 | Never attribute to base Nano |
| RoboArena / MolmoSpaces | snapshots 2026-05-30 / 2026-06-20 | Never encode rank as permanent property |
| Physics-IQ best-of-N | reranked score reported; Nano `N` unstated in that section | Separate direct and reranked; mark budget unknown |
| Throughput GPU count | p.45: 1,024/2,048; Table 8 caption: 2,048/4,096 | Preserve both; do not resolve by assumption [C3-TR, pp.45–46] |

## 10. Optimization decision framework

Map an observed deficit to the smallest causal intervention:

| Failure pattern | First controlled hypothesis | Required metrics | Reject if |
|---|---|---|---|
| Physical-AI Reasoner gain with general loss | Replay ratio or selective unfreezing | target groups + General 19 | target gain vanishes under fixed judge or general regression exceeds gate |
| Strong semantics, poor text rendering | text-rendering data/refinement | CVTG plus UniGenBench and aesthetics | OCR improves only through prompt rewrite or broad quality collapses |
| High video quality, low domain score | structured captions or domain mixture | PAIBench-G Domain + Quality slices | aggregate gain hides domain regressions |
| Good direct physics, weak long horizon | temporal curriculum or candidate reranking | Physics-IQ direct, fixed-N, horizon buckets | gain requires unreported extra inference budget |
| Strong AV alignment, weak PQ | audio preprocessing/decoder objective | AVAlign, SAV, PQ, artifact taxonomy | semantic metrics rise while PQ or sync regresses |
| Control fidelity differs by modality | control-specific data or token balance | each PAIBench-C metric + DOVER | improvement changes re-extractor/evaluator |
| MT-init early gain, same final score | use MT-init for efficiency, not asymptotic claim | cost-to-threshold + final success | compute accounting is unmatched |
| ID/policy improve while FD declines | objective/gradient balancing | all three task metrics + gradient norms | one task exceeds regression budget |
| Offline action improves, rollout does not | observation/action mismatch or compounding error | offline error + closed-loop success + latency | no invariant I/O validation exists |

Register new hypotheses and closure criteria in [research-queue.md](research-queue.md); reusable optimization procedures are owned by [optimization-playbook.md](optimization-playbook.md).

## 11. Experiment-record fields

An improvement claim is easier to compare when its record preserves:

1. immutable checkpoint/code/data/evaluator identities and raw configuration;
2. an unchanged baseline executed in the same environment and time window;
3. exact prompt before and after rewriting, template/rewriter version, negative prompt, CFG/sampler/steps, seed list, and best-of-N budget;
4. output resolution, aspect ratio, FPS, frame count, condition length, action horizon/rate, and rollout count;
5. judge model/version/prompt/temperature, human rubric and disagreement process, metric implementation hash, and aggregation formula;
6. raw outputs, per-example scores, failures, evaluator responses, and not only aggregates;
7. target metric, general-retention gate, domain/embodiment slices, safety/physics gate, latency/compute, and practical effect threshold;
8. confidence interval or seed/rollout distribution; use paired examples whenever possible;
9. learning curves and predeclared checkpoint-selection rule for training comparisons;
10. one-factor attribution, termination reason, and explicit statement of unresolved confounders.

## 12. Evaluation-invalidity signals

An evaluation cannot support its intended claim when:

- checkpoint identity, benchmark split, evaluator, or prompt-rewriting path is unknown;
- baseline and candidate differ in seeds, outputs per prompt, reranking budget, resolution, horizon, or rollout budget;
- train/evaluation leakage or scene/trajectory duplication is unresolved;
- a dynamic leaderboard is cited without date and submission identity;
- an automatic proxy is used as a substitute for closed-loop success or physical safety;
- aggregate improvement hides a predeclared critical regression;
- judge changes reverse the result or evaluator variance exceeds the effect size;
- only the best checkpoint/seed is retained while failed runs are discarded;
- the effect is smaller than the practical threshold or repeated trials do not reproduce direction;
- cost or latency exceeds the declared deployment budget even when quality improves.

## 13. Related knowledge ownership

- Objectives, optimizer state, schedules, and trainable groups are owned by [training.md](training.md).
- Adaptation branches and public recipes are owned by [post-training.md](post-training.md).
- Data mixtures, filtering, leakage, and action normalization are owned by [data.md](data.md).
- Model-card limitations, safety risks, and deployment evidence are owned by [limitations.md](limitations.md).
- Inference commands and engine configuration are owned by [inference.md](inference.md).
- Unresolved research questions are registered in [research-queue.md](research-queue.md), while reusable experiment strategies are owned by [optimization-playbook.md](optimization-playbook.md).
- Actual run state and artifacts are owned by [reproduction.md](reproduction.md).
- Source IDs and fixed revisions resolve through [sources.yaml](sources.yaml).
