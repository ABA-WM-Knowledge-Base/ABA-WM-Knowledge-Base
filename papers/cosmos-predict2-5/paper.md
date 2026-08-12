---
id: world-model-kb.papers.cosmos-predict2-5.paper
title: Cosmos-Predict2.5 Mechanisms and Experimental Evidence
kind: paper
status: maintained
last_updated: 2026-08-12
owners:
  - AIBuildAI world-model group
---

# Cosmos-Predict2.5 Mechanisms and Experimental Evidence

## Retrieval metadata

**Relevant queries:** Predict2.5 objective, latent video architecture, conditional-frame training, video curation, domain SFT, model soup, diffusion reinforcement learning, rCM, PAI-Bench, action-conditioned video, or reported ablation.

**Knowledge provided:** a causal reconstruction of the model, data and optimization pipeline, exact result surfaces, isolated ablations, negative interactions, and the limits of the paper's evidence.

**Related pages:** [Video world models](../../foundations/representations/video-world-model.md) owns the generic predictive surface; [latent world models](../../foundations/representations/latent-world-model.md) owns codec bottlenecks; [diffusion and flow matching](../../foundations/learning-objectives/diffusion-and-flow-matching.md) owns the objective family; [evaluation methodology](../../foundations/data-and-evaluation/evaluation-methodology.md) owns comparison validity.

## 1. Decision model

### 1.1 Target behavior

The work targets prompt-aligned, temporally coherent, high-resolution future-observation generation for Physical AI. It treats video as the external world-state surface and aims to make one backbone reusable across text-only generation, image-grounded prediction, video continuation, domain specialization, multiview rendering, and action-conditioned robot prediction. The paper's central design chain is:

```text
large, filtered, semantically structured video data
  + compressed latent observation representation
  + one conditional rectified-flow DiT
  + progressive resolution and conditioning curriculum
  + domain SFT, weight merging, reward post-training, and distillation
  -> higher visual/conditional benchmark scores and adaptable specialists
```

This chain supports a video-based world model claim. It does not establish that the base checkpoint estimates environment state, action causality, reward, termination, or policy value. The `robot/action-cond` specialist is the paper's clearest interventional forward-model surface because its generated future is indexed by calibrated Bridge action chunks. [P25-TR, pp.3-4, 8-15, 33-35]

### 1.2 Conditional distributions

The base family can be represented as one parameterized model with a variable clean prefix:

```text
Text2World:  p_theta(o[1:H] | text)
Image2World: p_theta(o[2:H] | o[1], text)
Video2World: p_theta(o[K+1:H] | o[1:K], text)
```

The clean image or video prefix is encoded into the same visual latent sequence as the prediction target, but prefix locations are marked and replaced during denoising. The action specialist changes the query to:

```text
p_theta(o[t+1:t+K] | o[t], a[t:t+K-1])
```

and rolls forward by reusing the final generated frame as the next chunk's visual condition. This converts passive continuation into an action-conditioned observation predictor under one dataset-specific action convention. [P25-TR, pp.9-10, 33-34]

### 1.3 Assumptions

- The WAN2.1 causal VAE preserves the visual state necessary for the target evaluation while compressing time, height, and width by `4 x 8 x 8`.
- Caption-conditioned internet and Physical AI video provide useful statistical regularities even where physical state and actions are not observed.
- Clean-prefix masking is sufficient for unifying generation and continuation without separate architectures.
- Higher-noise training coverage improves recovery from weak correlation and reduces temporal transition artifacts.
- VideoAlign reward dimensions are aligned enough with human preference to guide post-training without excessive reward exploitation when diffusion loss anchors the update.
- PAI-Bench quality and VQA-derived domain scores are useful evidence for conditional video generation, but not substitutes for environment-grounded closed-loop evaluation.

## 2. Data system

### 2.1 General curation pipeline

The report describes more than 200 million raw videos totaling approximately 35 million hours. Shot segmentation yields more than 6 billion clips between 5 and 60 seconds; the report says approximately 4% survive to form about 200 million training clips. These rounded statements are not arithmetically exact: `200M / 6B = 3.33%`, and the `more than 6B` denominator would imply an even lower ratio. Treat 4% as the authors' approximate retention claim, not a recomputable statistic, unless unrounded counts are supplied. The seven stages are shot-aware splitting, GPU transcoding, crop cleanup, filtering, captioning, semantic deduplication, and sharding. [P25-TR, pp.4-6, Figure 1]

Filtering is staged from cheaper to more expensive signals: aesthetic score, motion, OCR/text overlay, perceptual quality, semantic-artifact detection, and a final VLM rejection pass. A content classifier removes games, animation, and other physically unrealistic categories. Captioning divides a clip into five-second windows, uses Qwen2.5-VL-7B, and produces short, medium, and long descriptions. Semantic deduplication and a 26-type classifier support mixture construction and domain-specific retrieval. [P25-TR, pp.4-6]

The disclosed counts establish scale and selection pressure, not data reproducibility. The source URLs, exact mixture weights, filter models and thresholds, deduplication radius, train/test decontamination procedure, and retained clip manifest are not released in the report.

### 2.2 Domain data

Five domain pipelines add robotics, autonomous driving, smart spaces, human dynamics, and physics data. The robotics table reports view-specific retained clip counts rather than interchangeable trajectory counts:

| Dataset | Central/wrist | Left | Right |
|---|---:|---:|---:|
| AgiBot-Beta | 194K | 30K | 30K |
| Bridge | 36K | - | - |
| DROID | 39K wrist | 51K | 51K |
| GR00T | 3K | - | - |
| 1X | 17K | - | - |
| OpenX | 500 | - | - |
| RoboMIND | 16K | 6K | 7K |

The driving set contains 3.1 million proprietary 20-second clips from seven synchronized cameras; smart-space post-training uses approximately 40K clips. Dataset-aware captions normalize viewpoint and embodiment while emphasizing task, actions, objects, and state changes. Counts in this table cannot be summed with trajectory-level dataset statistics without resolving units. [P25-TR, pp.6-8, Table 2]

### 2.3 Post-training partitions

An InternVideo2-based multi-head classifier assigns high-quality video to five specialist sets, plus a separate 4K cooldown set:

| Domain | Videos |
|---|---:|
| Object permanence | 10.4M |
| High motion | 1.0M |
| Complex scenes | 1.6M |
| Driving | 3.1M |
| Robotic manipulation | 730K |
| 4K cooldown | 388K |

The classifier creates an explicit intervention surface: domain boundaries, confidence thresholds, sampling weights, and caption style can change what each specialist learns. The paper does not disclose the classifier training set, accuracy, overlap policy, or whether a clip may enter multiple domains. [P25-TR, p.11, Table 5]

## 3. Representation and architecture

### 3.1 Latent observation path

The causal WAN2.1 VAE maps a 93-frame, 16 FPS video to 24 latent frames using `4 x 8 x 8` compression. A `1 x 2 x 2` patchification then forms DiT tokens. The standard output is therefore approximately 5.8 seconds of decoded observation, and the codec determines which small objects, contact events, text, or gripper-state details can influence the denoiser. [P25-TR, p.9]

The DiT uses repeated self-attention, text cross-attention, and feed-forward blocks modulated by time-dependent adaptive layer normalization. Absolute position embeddings are removed while 3D RoPE is retained to improve reuse across unseen resolution or sequence length. The report lists the following configurations: [P25-TR, p.9, Table 3]

| Field | 2B | 14B |
|---|---:|---:|
| Reported layers | 32 | 36 |
| Model width | 2,048 | 5,120 |
| FFN width | 8,192 | 20,480 |
| AdaLN-LoRA rank | 256 | 256 |
| Attention heads | 16 | 40 |
| Head dimension | 128 | 128 |
| Activation / position | GELU / 3D RoPE | GELU / 3D RoPE |

The current 2B model card reports 2,059,174,912 parameters and the current 14B card reports 14,368,048,004. These are checkpoint-repository facts at current revisions, not a guarantee that every reported evaluation used byte-identical assets. [P25-HF-2B; P25-HF-14B]

### 3.2 Text representation

Cosmos-Reason1 replaces the earlier T5 text encoder. Rather than use one final hidden state per token, the pipeline concatenates activations from multiple Reason1 blocks and projects them to 1,024 dimensions before DiT cross-attention. This changes both representation capacity and pretraining provenance, so reported prompt-alignment improvement cannot be assigned solely to the projection without a matched encoder ablation. The Reason1 vision encoder is not used by this paper's base conditioning path; visual input through that encoder is named as future work. [P25-TR, pp.9-10]

### 3.3 Clean-prefix unification

Image2World and Video2World replace the leading noisy latent frames with encoded conditions and concatenate a binary mask channel identifying conditional positions. Loss applies only to target frames. The reusable insight is not merely multi-task training: training and inference share an explicit positional contract for which latent frames are evidence and which are predictions. Misalignment in the number of conditional frames, latent temporal stride, or mask semantics can silently change the task. [P25-TR, pp.9-11]

## 4. Learning system

### 4.1 Rectified-flow objective

For clean visual latent `x`, Gaussian noise `epsilon`, and interpolation time `t`:

```text
x_t = (1 - t) * x + t * epsilon
v_target = epsilon - x
L_flow = E ||u_theta(x_t, t, c) - v_target||^2
```

The model predicts a velocity field conditioned on text and optional clean frames. A shifted logit-normal time sampler moves more probability toward high noise as resolution increases. This objective represents multimodal video futures through sampling but does not impose physical conservation, action sensitivity, or calibrated uncertainty. [P25-TR, pp.8-9]

### 4.2 Progressive curriculum

| Stage | Tasks | Resolution | Pixel frames |
|---|---|---:|---:|
| 1 | Text2Image | `320 x 192` | 1 |
| 2 | Text2Image + Video2World | 256p | 1 or 93 |
| 3 | Text2Image + Video2World | `832 x 480` | 1 or 93 |
| 4 | Text2Image + Video2World | `1280 x 704` | 1 or 93 |
| 5 | Text2Image + Video2World + Text2World | `1280 x 704` | 1 or 93 |

Early video stages sample one or five clean frames and predict the remaining 92 or 88 frames. The final stage samples zero, one, or two clean frames with probabilities `0.5`, `0.25`, and `0.25`. The timestep shift increases from `beta=1` at 256p to `beta=5` at 720p. Five percent of samples are explicitly drawn from the top two percent of the noise distribution; the report attributes fewer abrupt transitions to this intervention but publishes no controlled numeric delta. [P25-TR, pp.10-11, Table 4]

AdamW uses betas `(0.9, 0.999)`, weight decay `0.001`, 2,000 warmup iterations, and linear decay. Peak learning rates are `3e-5` for 2B and `1.3e-5` for 14B. The report omits stage iteration counts, total tokens, batch sizes for base pre-training, wall-clock duration, precision, and total training compute. [P25-TR, p.11]

### 4.3 Specialist SFT and merging

One model is trained per domain for 30K iterations at global batch 256 using the last pre-training stage's hyperparameters. Human pairwise results show target-domain SFT wins over base at 42.6%-72.6%, with base wins at 19.0%-23.3% and ties at 8.3%-35.4%; the report omits prompt count, raters, aggregation, and uncertainty. [P25-TR, pp.11-12, Figure 3]

A separate 4K cooldown linearly decays learning rate to zero. Model soup, TIES, DARE-Linear, and DARE-TIES are swept to create more than 20 merged candidates. Selection first uses a small hand-picked challenge set, then a larger human evaluation. Model soup is selected; Figure 4 shows DARE-Linear as the exception to otherwise comparable merges. The exact coefficients, candidate grid, challenge-set size, and final evaluation sample size are not disclosed, so the final merged result is not exactly reproducible from the report. [P25-TR, pp.12-13, Figure 4]

### 4.4 Reward post-training

VideoAlign supplies text-alignment, motion-quality, and visual-quality rewards. Each condition produces a group of eight samples using 20 diffusion steps; rewards are normalized within the group in a GRPO-like advantage. The implementation computes gradients for two transition probabilities at a time and accumulates ten such pieces per update. Training runs 256 steps at batch 32. Standard diffusion loss on fine-tuning data regularizes the policy against reward hacking. [P25-TR, pp.13-14; P25-VIDEOALIGN; P25-DDRL]

| Starting 2B state | Mode | Reward sum before | Reward sum after |
|---|---|---:|---:|
| Pre-trained | Text2World | 1.08 | 1.69 |
| Merged | Text2World | 1.23 | 1.74 |
| Pre-trained | Image2World | 0.23 | 0.42 |
| Merged | Image2World | 0.24 | 0.45 |

Human votes favor the RL model over its starting state 40.0% versus 18.9% for pre-trained and 46.7% versus 16.3% for merged; ties are 41.1% and 37.0%. Missing judge counts and sampling details limit confidence intervals and attribution. Reward increases are partly circular because the same reward family guides training and evaluation; human comparison is the independent check, but its protocol is under-specified. [P25-TR, pp.13-14, Table 6 and Figure 5]

### 4.5 Timestep distillation and infrastructure

The paper reports rCM, a joint consistency/distribution-matching method, producing four-step 2B samples. Text2World overall score changes `0.768 -> 0.764`; Image2World changes `0.810 -> 0.816`. These results support substantial step reduction with similar aggregate benchmark quality, but they do not report latency, throughput, VRAM, diversity, or long-horizon consistency. The public repository's documented trainable distillation path is DMD2 rather than rCM; that release mismatch is owned by [`codebase.md`](codebase.md). [P25-TR, pp.14-15, Tables 7-8; P25-RCM; P25-DMD2]

Training infrastructure combines FSDP2 hybrid sharding, Ulysses context parallelism, selective activation checkpointing, and an elastic decoded-latent reward service. At 720p and 93 frames on 4,096 H100 GPUs, the report lists `36.49%` MFU for 2B with context parallelism 2 and `33.08%` for 14B with context parallelism 8. Total tokens and iteration count are absent, so the table cannot be converted into total training cost. [P25-TR, pp.14-15, Table 9]

## 5. Main generation evidence

PAI-Bench Predict defines `Overall = (Domain + Quality) / 2`. Domain is VQA-derived across seven Physical AI domains; Quality aggregates eight adapted video metrics. It is a composite conditional-generation benchmark, not a direct measurement of physical state accuracy or control utility. [P25-TR, pp.15-16; P25-PAIBENCH]

### 5.1 Text2World

| Model | Domain | Quality | Overall |
|---|---:|---:|---:|
| Predict2.5-2B pre-trained | 0.782 | 0.720 | 0.751 |
| Predict2.5-2B post-trained | 0.804 | 0.732 | 0.768 |
| Predict2.5-14B pre-trained | 0.791 | 0.722 | 0.757 |
| Predict2.5-14B post-trained | 0.803 | 0.732 | 0.768 |
| Wan2.2-5B | 0.797 | 0.730 | 0.764 |
| Wan2.2-27B-A14B | 0.810 | 0.728 | 0.769 |

Post-training raises overall score by `+0.017` for 2B and `+0.011` for 14B. The 2B and 14B post-trained variants tie at 0.768 despite different component scores; scale does not improve this aggregate surface. [P25-TR, p.16, Table 10]

### 5.2 Image2World

| Model | Domain | Quality | Overall |
|---|---:|---:|---:|
| Predict2.5-2B pre-trained | 0.824 | 0.775 | 0.799 |
| Predict2.5-2B post-trained | 0.840 | 0.779 | 0.810 |
| Predict2.5-14B pre-trained | 0.835 | 0.777 | 0.806 |
| Predict2.5-14B post-trained | 0.838 | 0.781 | 0.810 |
| Wan2.2-5B | 0.834 | 0.774 | 0.804 |
| Wan2.2-27B-A14B | 0.841 | 0.772 | 0.806 |

Post-training raises overall score by `+0.011` for 2B and `+0.004` for 14B. Again, both post-trained scales tie at 0.810. Human comparison exposes a scale effect not visible in the aggregate: 2B versus Wan2.1-14B is `33.0%/34.8%/32.2%` Predict/Wan/tie, whereas 14B versus the same baseline is `48.6%/31.8%/19.6%`. The paper does not report sample sizes or significance. [P25-TR, pp.16-17, Table 11 and Figures 6-7]

## 6. Specialist evidence with transfer value

### 6.1 Action-conditioned forward prediction

Bridge experiments use approximately 20K episodes at `320 x 256`, 5 FPS. Each frame has a seven-dimensional relative gripper action: three translations, three rotations, and a gripper scalar. The paper calls the final value `GripperWidth`, while the released loader describes a binary current open/close state; [`codebase.md`](codebase.md) preserves this interface discrepancy. One hundred official test episodes are sampled. [P25-TR, pp.33-34; P25-CODE-PAPER]

| Model | PSNR up | SSIM up | Latent L2 down | FVD down |
|---|---:|---:|---:|---:|
| Predict1-7B action-conditioned baseline | 21.14 | 0.82 | 0.32 | 190 |
| Predict2.5-2B `robot/action-cond` | 24.95 | 0.85 | 0.28 | 146 |

The architecture ablation holds backbone and task family closer than the cross-generation baselines:

| Action injection | PSNR up | SSIM up | Latent L2 down | FVD down |
|---|---:|---:|---:|---:|
| Time embedding | 24.95 | 0.85 | 0.28 | 146 |
| Cross-attention | 24.41 | 0.84 | 0.28 | 159 |
| Channel concatenation | 23.11 | 0.78 | 0.35 | 267 |

Time-embedding injection is the best tested interface for this fixed Bridge setup. It does not prove that global action modulation is optimal for other action dimensionalities, variable horizons, multimodal actions, or architectures with native action tokens. No action-counterfactual, feasibility, or closed-loop task-success metric is reported. [P25-TR, pp.34-35, Tables 19-20]

### 6.2 Multiview representation reuse

The driving specialist concatenates seven views along the latent temporal axis, independently encodes and decodes each view, adds a seven-dimensional learned view embedding, and constructs 3D RoPE separately per view. It trains for two epochs on 1.5M 20-second, seven-camera clips at batch 64 and context parallelism 8; evaluation uses 1,000 disjoint clips. This is a compute-efficient reuse of a temporal DiT, but temporal/view-axis aliasing and cross-view attention are coupled. [P25-TR, pp.24-28]

The robot multiview branch adds Plucker raymaps and updates only self-attention plus camera projection. On 80 in-the-wild videos across 16 camera trajectories, multiview leaves translation error at 0.08, worsens rotation error `0.19 -> 0.20`, and improves Sampson error `26.61 -> 19.73`. The negative rotation interaction must be retained: cross-view synchronization improved without uniform camera-pose improvement. [P25-TR, pp.28-31, Table 17]

### 6.3 Synthetic VLA data

The paper post-trains a 14B robot-video specialist, generates instruction-conditioned demonstrations, and proposes recovering pseudo-actions using a latent action or inverse-dynamics model. DreamGen automated judges show improvement on several object, behavior, and environment instruction-following slices. This establishes conditional-video adaptability, not that recovered actions are correct or that a downstream policy improves. The latter requires an independent IDM/action-fidelity check and policy evaluation. [P25-TR, pp.31-34, Table 18]

Transfer2.5 also generates five synthetic variants per each of 100 demonstrations while retaining original joint/action labels; a real-robot study reports `24/30` successes versus `5/30` with standard augmentation and `1/30` without augmentation. This is evidence for a Transfer2.5-controlled augmentation pipeline, not a direct base Predict2.5 effect, and the small 30-trial protocol limits scenario-level uncertainty. [P25-TR, pp.20-24]

## 7. Evidence boundaries and unresolved attribution

| Claim surface | Evidence available | Missing discriminator |
|---|---|---|
| `CP25-PAPER-GAP-01`: final curation retention | report states `>6B` candidates, `~200M` retained, and `~4%` retention | unrounded candidate/retained counts and the exact denominator used for the percentage |
| Better prompt/video quality | PAI-Bench, VideoAlign, pairwise preferences | fixed original checkpoint hashes, evaluator versions, seeds, sample counts, confidence intervals |
| Better physics | VQA/perceptual composites and qualitative samples | object-state/contact trajectories, counterfactual interventions, environment replay |
| High-noise tail fixes transitions | report observation | isolated metric, exact scheduler implementation, matched compute |
| Reason1 improves grounding | final architecture and aggregate results | matched T5 versus Reason1 ablation |
| Domain SFT plus merging avoids forgetting | domain preferences and merged comparisons | exact coefficients, candidate grid, held-out selection protocol |
| RL improves human preference | reward and pairwise votes | complete run details, sample size, diversity/calibration, reward-model independence |
| Four-step distillation preserves quality | PAI-Bench teacher/student tables | released rCM recipe, latency, diversity, long-horizon drift |
| Action specialist models controllable dynamics | held-out video similarity and injection ablation | matched action counterfactuals, action calibration, closed-loop outcome |
| Multiview is geometrically consistent | pose proxy and Sampson error | persistent scene geometry, occlusion correctness, causal camera calibration |

The paper combines data scale, architecture changes, text representation, curriculum, SFT, merge selection, reward optimization, and possibly updated checkpoint assets. Final model comparisons therefore support the composition, not an independent causal effect for every component. Transfer hypotheses should begin from the few isolated interventions rather than treating the whole system as one portable recipe.

## Sources

Primary identities are registered in [`sources.yaml`](sources.yaml). General mechanisms and evaluation principles are canonical in the linked Foundation pages.
