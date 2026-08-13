---
id: world-model-kb.papers.cosmos-predict2-5.paper
title: Cosmos-Predict2.5 Method, Architecture, and Experimental Evidence
kind: paper
status: maintained
last_updated: 2026-08-13
owners:
  - AIBuildAI world-model group
---

# Cosmos-Predict2.5 Method, Architecture, and Experimental Evidence

## Retrieval metadata

**Relevant queries:** Cosmos-Predict2.5 architecture, Text2World, Image2World, Video2World, video curation, WAN2.1 VAE, Cosmos-Reason1 text encoder, rectified flow, clean-prefix conditioning, progressive pretraining, domain SFT, model merging, diffusion RL, rCM distillation, PAI-Bench, Transfer2.5, robot augmentation, driving simulation, camera-controlled multiview generation, synthetic VLA data, or action-conditioned generation.

**Knowledge provided:** the paper's data pipeline, complete input-to-output architecture, training and post-training sequence, base-model evidence, application-specific extensions, ablations, and claim boundaries.

**Related pages:** [Video world models](../../foundations/representations/video-world-model.md) owns the generic predictive surface; [latent world models](../../foundations/representations/latent-world-model.md) owns codec bottlenecks; [diffusion and flow matching](../../foundations/learning-objectives/diffusion-and-flow-matching.md) owns the objective family; [actions and interventions](../../foundations/problem-formulation/actions-and-interventions.md) owns causal action semantics; [evaluation methodology](../../foundations/data-and-evaluation/evaluation-methodology.md) owns comparison validity.

## 1. Scope and model family

### 1.1 Paper scope

The report presents two connected families:

- **Cosmos-Predict2.5** is a latent video world foundation model with Text2World, Image2World, and Video2World generation surfaces.
- **Cosmos-Transfer2.5** adds spatial control branches for blur, edge, depth, segmentation, world-scenario maps, and related conditional generation.

The report also adapts these backbones into robot, driving, multiview, synthetic-data, and action-conditioned specialists. A specialist result establishes that adaptation surface; it is not automatically a capability of the base checkpoint. [P25-TR, pp.3, 8-10, 17-35]

### 1.2 Predictive surfaces

The base family can be written as one conditional video distribution with a variable clean prefix:

```text
Text2World:  p_theta(o[1:H]   | text)
Image2World: p_theta(o[2:H]   | o[1], text)
Video2World: p_theta(o[K+1:H] | o[1:K], text)
```

The action-conditioned robot specialist changes the query to:

```text
p_theta(o[t+1:t+K] | o[t], a[t:t+K-1])
```

Base text/image/video conditioning models observational futures. Only the specialist with calibrated action inputs provides an explicit interventional forward-model surface. None of these surfaces directly produces reward, value, termination, or a control policy. [P25-TR, pp.8-11, 33-35]

## 2. Data system

### 2.1 General video curation

The report begins with more than 200 million raw videos totaling about 35 million hours. Shot segmentation creates more than 6 billion clips of 5-60 seconds. The pipeline then applies:

```text
shot-aware splitting
  -> GPU transcoding
  -> crop and border cleanup
  -> staged quality/content filtering
  -> multi-granularity captioning
  -> semantic deduplication
  -> domain-aware sharding and mixture construction
```

Filtering proceeds from cheaper to more expensive checks: aesthetics, motion, OCR/text overlay, perceptual quality, semantic artifacts, category filtering, and a final VLM rejection pass. Captions are generated in five-second windows by Qwen2.5-VL-7B at short, medium, and long granularity. A 26-type classifier and semantic deduplication support mixture design and domain retrieval. [P25-TR, pp.4-6, Fig.1]

The report says about 4% of candidates survive and also reports roughly 200M retained from more than 6B clips. The rounded ratio is at most 3.33%, so 4% must be preserved as an approximate author statement rather than recomputed as exact. Exact URLs, thresholds, filter checkpoints, deduplication radius, retained manifests, mixture weights, and benchmark decontamination are not disclosed.

### 2.2 Physical-AI domain data

Five pipelines add robotics, autonomous driving, smart spaces, human dynamics, and physics. Robotics statistics are view-specific clip counts rather than interchangeable trajectory counts: [P25-TR, pp.6-8, Table 2]

| Dataset | Central or wrist | Left | Right |
|---|---:|---:|---:|
| AgiBot-Beta | 194K | 30K | 30K |
| Bridge | 36K | - | - |
| DROID | 39K wrist | 51K | 51K |
| GR00T | 3K | - | - |
| 1X | 17K | - | - |
| OpenX | 500 | - | - |
| RoboMIND | 16K | 6K | 7K |

Driving uses 3.1M proprietary 20-second clips from seven synchronized cameras; smart-space post-training uses about 40K clips. Dataset-aware captions describe viewpoint, embodiment, task, actions, objects, and state changes. These counts establish data scale and selection pressure, not a reproducible mixture.

### 2.3 Post-training partitions

A multi-head classifier over InternVideo2 features builds five specialist partitions and a separate 4K cooldown set: [P25-TR, p.11, Table 5]

| Partition | Videos |
|---|---:|
| object permanence | 10.4M |
| high motion | 1.0M |
| complex scenes | 1.6M |
| driving | 3.1M |
| robotic manipulation | 730K |
| 4K cooldown | 388K |

The classifier dataset, accuracy, thresholding, overlap policy, and exact sampling weights are not reported.

## 3. Base method and architecture

### 3.1 End-to-end data flow

Figure 2 and Sections 3.1-3.2 define this pipeline:

```text
text prompt
  -> tokenizer
  -> Cosmos-Reason1 hidden states from multiple transformer layers
  -> concatenate selected layer activations
  -> project each text token to 1,024 dimensions
  -> text embeddings for DiT cross-attention

RGB image/video target or visual prefix
  -> causal WAN2.1 VAE (time x height x width compression = 4 x 8 x 8)
  -> latent sequence
  -> 1 x 2 x 2 patchification
  -> clean prefix tokens + noisy target tokens + binary condition mask
  -> repeated DiT blocks:
       timestep-modulated self-attention
       text cross-attention
       timestep-modulated feed-forward network
       3D RoPE positions
  -> velocity prediction
  -> numerical flow integration from noise to clean latent
  -> unpatchify + VAE decoder
  -> 93-frame, 16-FPS RGB video
```

Text2World has no clean visual prefix; Image2World has an image prefix; Video2World has multiple clean video frames. The same denoising backbone handles all three through prefix replacement and the binary mask rather than separate networks. [P25-TR, pp.8-11, Fig.2]

### 3.2 Visual tokenizer and token geometry

The causal WAN2.1 VAE compresses time, height, and width by `4 x 8 x 8`. A 93-frame video becomes 24 latent frames; patchification further groups `1 x 2 x 2` latent positions. At 16 FPS, the decoded output is about 5.8 seconds. The codec determines whether small objects, contact, text, gripper state, and other task-relevant details remain available to the transformer. [P25-TR, p.9]

### 3.3 Text conditioning

Cosmos-Reason1 replaces the earlier T5 encoder. Instead of using only one final transformer layer, the pipeline concatenates activations from several Reason1 blocks and projects them to 1,024 dimensions before DiT cross-attention. This mixes local and global language features. The report does not provide a matched T5-versus-Reason1 ablation, so final prompt-alignment gains cannot be assigned to this encoder change alone. Reason1's vision input path is shown as future work, not as a base Predict2.5 visual-conditioning mechanism. [P25-TR, pp.9-10, Fig.2]

### 3.4 DiT denoiser

Each block contains self-attention, text cross-attention, and a feed-forward network. Timestep-conditioned adaptive layer normalization supplies scale, shift, and residual gates. The model removes absolute positional embeddings but retains 3D RoPE, aiming to generalize across resolution and sequence length. [P25-TR, pp.9-10]

| Configuration | 2B | 14B |
|---|---:|---:|
| reported layers | 32 | 36 |
| model width | 2,048 | 5,120 |
| FFN width | 8,192 | 20,480 |
| AdaLN-LoRA dimension | 256 | 256 |
| attention heads | 16 | 40 |
| head dimension | 128 | 128 |
| activation / position | GELU / 3D RoPE | GELU / 3D RoPE |

The paper's 32-layer 2B description conflicts with the released 2B configuration exposing 28 transformer blocks; [`codebase.md`](codebase.md) owns that implementation mismatch. Current model cards report approximately 2.059B and 14.368B parameters, but their current revisions are not asserted to be the exact evaluation artifacts. [P25-TR, p.9, Table 3; P25-HF-2B; P25-HF-14B]

### 3.5 Rectified-flow objective

For clean latent `x`, Gaussian noise `epsilon`, condition `c`, and interpolation time `t`:

```text
x_t      = (1 - t) * x + t * epsilon
v_target = epsilon - x
L_flow   = E ||u_theta(x_t, t, c) - v_target||^2
```

At inference, the learned velocity field transports a noise sample toward a clean latent video. The stochastic generator can represent multiple futures, but the objective does not itself impose conservation laws, action sensitivity, or calibrated uncertainty. [P25-TR, pp.8-9]

### 3.6 Clean-prefix task unification

For Image2World and Video2World, clean encoded prefix frames replace the corresponding noisy frames throughout denoising. A binary mask channel marks which positions are conditions, and loss is applied only to target positions. This positional contract is central: frame count, temporal codec stride, token alignment, and mask semantics determine the task presented to the model. [P25-TR, pp.9-11]

## 4. Training

### 4.1 Progressive pretraining

Training increases both resolution and task diversity: [P25-TR, pp.10-11, Table 4]

| Stage | Tasks | Resolution | Pixel frames |
|---|---|---:|---:|
| 1 | Text2Image | `320 x 192` | 1 |
| 2 | Text2Image + Video2World | 256p | 1 or 93 |
| 3 | Text2Image + Video2World | `832 x 480` | 1 or 93 |
| 4 | Text2Image + Video2World | `1280 x 704` | 1 or 93 |
| 5 | Text2Image + Video2World + Text2World | `1280 x 704` | 1 or 93 |

Early video stages provide one or five clean frames and predict the remaining 92 or 88. The final stage samples zero, one, or two clean frames with probabilities `0.5`, `0.25`, and `0.25`. The logit-normal timestep shift grows from `beta=1` at 256p to `beta=5` at 720p. Five percent of samples are drawn explicitly from the highest two percent of noise because the authors observed abrupt transitions under weaker high-noise coverage; no isolated numeric ablation is reported.

AdamW uses betas `(0.9, 0.999)`, weight decay `0.001`, 2,000 warmup iterations, and linear decay. Peak learning rates are `3e-5` for 2B and `1.3e-5` for 14B. Stage steps, global pretraining batch size, total tokens, total compute, and precision are omitted. [P25-TR, p.11]

### 4.2 Domain SFT, cooldown, and merging

Five domain models are fine-tuned separately for 30K iterations at global batch 256. Human preference shows each specialist beating the base in its target category, with SFT wins ranging from 42.6% to 72.6%. The report omits sample counts, raters, aggregation, and uncertainty. [P25-TR, pp.11-12, Fig.3]

A 4K cooldown model decays learning rate to zero. More than 20 merged candidates are constructed with model soup, TIES, DARE-Linear, and DARE-TIES. Candidate selection uses a small hand-picked challenge set and then a larger human evaluation; model soup is selected. Exact coefficients, grid, set sizes, and prompt identities are not disclosed, so the merge cannot be reconstructed exactly. [P25-TR, pp.12-13, Fig.4]

### 4.3 Reward post-training

VideoAlign provides text-alignment, motion-quality, and visual-quality rewards. Each condition produces eight samples with 20 denoising steps; rewards are normalized within each group. Gradients are accumulated over transition-probability pieces, and a diffusion loss on fine-tuning data regularizes the update against reward exploitation. Training runs 256 updates at batch 32. [P25-TR, pp.13-14; P25-VIDEOALIGN; P25-DDRL]

| 2B starting state | Task | Reward sum before | After |
|---|---|---:|---:|
| pre-trained | Text2World | 1.08 | 1.69 |
| merged | Text2World | 1.23 | 1.74 |
| pre-trained | Image2World | 0.23 | 0.42 |
| merged | Image2World | 0.24 | 0.45 |

Human pairwise votes independently favor the RL model over its start, but judge counts and sampling details are missing. Reward improvement is partly circular because the reward family also trains the model; human evaluation is the independent check.

### 4.4 Timestep distillation

The report applies rCM and evaluates a four-step 2B student. Text2World overall changes `0.768 -> 0.764`; Image2World changes `0.810 -> 0.816`. This supports large denoising-step reduction at similar aggregate benchmark score, but latency, throughput, VRAM, diversity, and long-horizon drift are not reported. The public training code exposes DMD2 rather than the report's rCM path. [P25-TR, pp.14-15, Tables 7-8; P25-RCM; P25-DMD2]

### 4.5 Training infrastructure

The stack combines FSDP2 hybrid sharding, Ulysses context parallelism, selective activation checkpointing, asynchronous checkpointing, and an elastic reward service that decodes latents and computes reward models in a producer-consumer pipeline. At 720p and 93 frames on 4,096 H100 GPUs, the report gives 36.49% MFU for 2B with context parallelism 2 and 33.08% for 14B with context parallelism 8. Missing iteration and token counts prevent conversion to total training cost. [P25-TR, pp.14-15, Table 9]

## 5. Base-model results

PAI-Bench Predict defines `Overall = (Domain + Quality) / 2`. Domain is a VQA-derived score across seven Physical-AI domains; Quality aggregates eight adapted video metrics. It measures conditional generation, not physical state error or closed-loop utility. [P25-TR, pp.15-16; P25-PAIBENCH]

### 5.1 Text2World

| Model | Domain | Quality | Overall |
|---|---:|---:|---:|
| 2B pre-trained | 0.782 | 0.720 | 0.751 |
| 2B post-trained | 0.804 | 0.732 | 0.768 |
| 14B pre-trained | 0.791 | 0.722 | 0.757 |
| 14B post-trained | 0.803 | 0.732 | 0.768 |
| Wan2.2-5B | 0.797 | 0.730 | 0.764 |
| Wan2.2-27B-A14B | 0.810 | 0.728 | 0.769 |

Post-training adds 0.017 for 2B and 0.011 for 14B. Both post-trained scales score 0.768, so this aggregate does not show a scale gain. [P25-TR, p.16, Table 10]

### 5.2 Image2World and human preference

| Model | Domain | Quality | Overall |
|---|---:|---:|---:|
| 2B pre-trained | 0.824 | 0.775 | 0.799 |
| 2B post-trained | 0.840 | 0.779 | 0.810 |
| 14B pre-trained | 0.835 | 0.777 | 0.806 |
| 14B post-trained | 0.838 | 0.781 | 0.810 |
| Wan2.2-5B | 0.834 | 0.774 | 0.804 |
| Wan2.2-27B-A14B | 0.841 | 0.772 | 0.806 |

Post-training adds 0.011 for 2B and 0.004 for 14B. Both finish at 0.810. Human comparison reveals a scale difference hidden by the aggregate: 2B versus Wan2.1-14B is `33.0/34.8/32.2` Predict/Wan/tie, while 14B versus the same baseline is `48.6/31.8/19.6`. Prompt count, judge count, and significance are not reported. [P25-TR, pp.16-17, Table 11, Figs.6-7]

## 6. Applications and specialist extensions

The following subsections follow the report's Section 6 order. Each extension changes the conditional interface, data, or trainable modules; its evidence must remain attached to that named specialist.

### 6.1 Cosmos-Transfer2.5 spatial control

Cosmos-Transfer2.5-2B adds four control blocks to the Predict2.5-2B main branch. Unlike Transfer1, which places four blocks near the start, Transfer2.5 inserts one after every seven main blocks, distributing control through depth. Separate branches are trained for blur, edge, depth, and segmentation. Training data includes 14M edge/blur videos, 10M depth videos, and 3M segmentation videos; each control branch trains for 100K iterations at effective batch 64. [P25-TR, pp.17-19]

PAI-Bench Transfer contains 600 videos. Single-control and uniform four-control variants are evaluated for alignment and overall quality. The uniform Transfer2.5 model improves overall quality from 9.24 for Transfer1 to 9.31; per-modality specialists reach higher alignment for their own condition. In autoregressive 93-frame chunks, normalized relative DOVER curves remain more stable than Transfer1 for the tested controls, but this metric is still a perceptual proxy rather than environment-state verification. [P25-TR, pp.18-20, Table 12, Figs.9-10]

### 6.2 Real2Real augmentation for robot policy learning

A dual-arm robot collects 100 teleoperated demonstrations at 10 FPS. Transfer2.5 generates five visually modified versions of each demonstration while retaining the original actions and joint states. A diffusion policy is trained on these augmented observations and evaluated in the base setting plus nine object/environment variations, three trials each. [P25-TR, pp.20-24]

| Policy training data | Total successes |
|---|---:|
| original demonstrations only | `1/30` |
| standard image augmentation | `5/30` |
| Transfer2.5 video augmentation | `24/30` |

This is evidence for label-preserving Transfer2.5 augmentation under the stated setup. It is not a direct base Predict2.5 result, and the small per-scenario sample leaves wide uncertainty. The validity of retaining actions depends on the generated visual edit not changing task-relevant geometry or action semantics.

### 6.3 Driving simulation

The driving model concatenates up to seven independently encoded 720p views along the latent temporal axis, adds a learned seven-way view embedding, and constructs 3D RoPE separately for each view. Predict2.5-auto/multiview trains for two epochs on 1.5M 20-second, seven-camera clips at global batch 64 and context parallelism 8. Transfer2.5-auto/multiview adds per-view world-scenario-map controls built from HD maps and projected dynamic objects and trains on 140K controlled scenes. Evaluation uses 1,000 disjoint clips. [P25-TR, pp.25-28]

Compared with Predict1-7B-Sample-AV, Predict2.5-2B-auto/multiview improves FVD StyleGAN `63.685 -> 23.060`, FVD I3D `69.613 -> 25.308`, and FID `25.341 -> 12.095`; temporal and cross-camera Sampson errors are mixed relative to real-video references. Transfer2.5 improves several lane and cuboid detection metrics over Transfer1, but not every temporal/cross-view metric. Repurposing the time axis is efficient, yet it couples view ordering with temporal representation and does not create an explicit persistent 3D state. [P25-TR, pp.25-28, Tables 14-15]

### 6.4 Camera-controlled robot multiview generation

The robot extension takes a source video plus target camera trajectories and predicts multiple target views. Source and target video tokens are concatenated along time; camera intrinsics/extrinsics are sampled at the VAE's temporal stride, converted to Plucker raymaps, patchified, and projected into the DiT. The report describes updating self-attention and the camera projection while freezing other components. [P25-TR, pp.28-31]

On 80 in-the-wild manipulation videos and 16 camera trajectories, multiview leaves translation error at 0.08, changes rotation error from `0.19` to `0.20`, and improves cross-view Sampson error from `26.61` to `19.73`. Synchronization improves without uniform camera-pose improvement; that negative rotation interaction must be retained. [P25-TR, pp.30-31, Table 17]

### 6.5 Synthetic video for VLA training

A 14B robot specialist generates instruction-conditioned demonstration videos. The proposed pipeline then recovers pseudo-actions with a latent-action or inverse-dynamics model to form vision-language-action training samples. On DreamGen GR1, the Predict2.5 specialist improves several object, behavior, and environment instruction-following scores over earlier video generators. [P25-TR, pp.31-34, Table 18]

These results establish instruction-conditioned video adaptability. The report does not validate the recovered pseudo-actions or show downstream policy improvement from the generated samples, so the complete VLA-data claim requires an independent action-fidelity and policy experiment.

### 6.6 Action-conditioned robot world generation

The Bridge specialist receives one image and a sequence of seven-dimensional relative gripper actions at 5 FPS, embeds each action with an MLP, and adds the resulting action tensor to DiT timestep embeddings. It generates a future chunk, then autoregressively conditions the next chunk on the last generated frame. About 20K Bridge episodes are used; evaluation samples 100 official test episodes. [P25-TR, pp.33-35]

| Model | PSNR up | SSIM up | Latent L2 down | FVD down |
|---|---:|---:|---:|---:|
| Predict1-7B action baseline | 21.14 | 0.82 | 0.32 | 190 |
| Predict2.5-2B action specialist | 24.95 | 0.85 | 0.28 | 146 |

The action-injection ablation is the report's strongest direct specialist-architecture comparison: [P25-TR, pp.34-35, Tables 19-20]

| Injection | PSNR | SSIM | Latent L2 | FVD |
|---|---:|---:|---:|---:|
| timestep embedding | 24.95 | 0.85 | 0.28 | 146 |
| cross-attention | 24.41 | 0.84 | 0.28 | 159 |
| channel concatenation | 23.11 | 0.78 | 0.35 | 267 |

Timestep injection is best for this fixed Bridge setting. The experiment does not establish universality across embodiments, horizons, action dimensions, or architectures with native action tokens; it also lacks matched action-counterfactual and closed-loop evaluation.

## 7. Conclusions and evidence boundaries

The report supports a coherent system claim: large filtered video data, a latent flow DiT, clean-prefix task unification, progressive training, domain adaptation, merge selection, reward optimization, and specialist post-training form a reusable Physical-AI video platform. It does not isolate the causal contribution of every component.

| Claim surface | Available evidence | Missing discriminator |
|---|---|---|
| final curation retention | `>6B`, `~200M`, and `~4%` statements | unrounded counts and denominator |
| stronger physical simulation | PAI-Bench composites, human votes, qualitative videos | object/contact trajectories and environment replay |
| high-noise sampling removes transition artifacts | author observation | isolated numeric ablation and scheduler identity |
| Reason1 improves prompt grounding | final architecture and aggregate results | matched encoder ablation |
| SFT and merging retain generality | specialist preferences and merged comparisons | coefficients, candidate grid, selection-set identities |
| reward post-training improves preference | reward and pairwise gains | full judge protocol, independent reward, diversity/calibration |
| four-step rCM preserves quality | aggregate teacher/student tables | released rCM code, latency, diversity, long-horizon drift |
| multiview specialists model geometry | pose and cross-view proxy metrics | persistent scene state, occlusion correctness, calibrated geometry |
| action specialist models controllable dynamics | logged-action video metrics and injection ablation | action counterfactuals, feasibility, closed-loop task outcome |

Transfer2.5, driving, multiview, VLA-data, and action-conditioned results belong to their named extensions. [`codebase.md`](codebase.md) owns release mismatches; [`reproduction.md`](reproduction.md) owns what was actually executed; [`optimization-transfer.md`](optimization-transfer.md) turns only evidence-backed mechanisms into falsifiable transfer hypotheses.

## Sources

Primary identities are registered in [`sources.yaml`](sources.yaml). General mechanisms and evaluation principles are canonical in the linked Foundation pages.
