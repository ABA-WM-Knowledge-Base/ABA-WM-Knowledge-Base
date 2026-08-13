---
id: world-model-kb.papers.irasim.paper
title: IRASim Method, Architecture, and Experimental Evidence
kind: paper
status: maintained
last_updated: 2026-08-13
owners:
  - AIBuildAI world-model group
---

# IRASim Method, Architecture, and Experimental Evidence

## Retrieval metadata

**Relevant queries:** IRASim architecture, trajectory-to-video equation, latent diffusion, spatial-temporal DiT, clean historical frames, Frame-Ada, Video-Ada, action-frame alignment, RT-1, Bridge, Language-Table, RoboNet, policy evaluation, Push-T planning, real-robot planning, scaling, or ablation.

**Knowledge provided:** the paper's problem formulation, complete input-to-output architecture, data and training protocol, trajectory-prediction experiments, downstream decision experiments, and the limits of each claim.

**Related pages:** [Actions and interventions](../../foundations/problem-formulation/actions-and-interventions.md) owns action semantics; [forward dynamics](../../foundations/problem-formulation/forward-dynamics.md) owns rollout prediction; [video world models](../../foundations/representations/video-world-model.md) owns observation-space trade-offs; [latent world models](../../foundations/representations/latent-world-model.md) owns representation sufficiency; [diffusion and flow matching](../../foundations/learning-objectives/diffusion-and-flow-matching.md) owns the generic objective; [evaluation methodology](../../foundations/data-and-evaluation/evaluation-methodology.md) owns evidence-layer distinctions.

## 1. Problem statement

### 1.1 Prediction task

IRASim is an action-conditioned visual forward model, not a policy. Given historical observations and a future robot action trajectory, it predicts the video that should result:

```text
I[t+1:t+n+1] = f(I[t-h:t], a[t:t+n]),   a[i] in R^d
```

`h` is the number of historical frames, `n` is the number of actions, and each action is intended to govern the transition to one predicted frame. The model outputs future observations; it does not output an action, reward, value, success probability, or safety decision. Those quantities are supplied by separate components in the downstream experiments. [IRASRC-PAPER-V2, pp.4-6, Eq.1]

### 1.2 Design problem

The paper identifies three requirements:

1. preserve consistency with the observed historical frames;
2. make every generated frame adhere to its corresponding action rather than only to a pooled trajectory summary;
3. keep video diffusion computationally tractable.

The principal hypothesis concerns conditioning granularity. A single embedding for the whole action chunk can describe overall motion but erases explicit action-to-frame identity. IRASim's Frame-Ada variant keeps that identity in the spatial transformer path while retaining a trajectory-level condition in the temporal path. [IRASRC-PAPER-V2, pp.5-6, Fig.2]

## 2. Method and architecture

### 2.1 End-to-end data flow

The architecture in Figure 2 can be reconstructed as the following pipeline:

```text
historical RGB frames I[t-h:t]             future RGB frames I[t+1:t+n+1]
              |                                        |
              +------------- frozen SDXL VAE ----------+
              |                                        |
       clean history latents                 clean future latents x_0
                                                       |
                                               add diffusion noise
                                                       |
                                            noisy future latents x_t
              |                                        |
              +---- concatenate along video time ------+
                               |
                         patchify each latent
                               |
              repeated spatial-attention block
              repeated temporal-attention block
                 ^                         ^
                 |                         |
       frame-indexed action AdaLN     trajectory-level AdaLN
                 \_________________________/
                         diffusion timestep
                               |
                   linear projection + unpatchify
                               |
                    predicted future-frame noise
                               |
                   iterative reverse diffusion
                               |
                      predicted future latents
                               |
                       frozen VAE decoder
                               |
                    predicted future RGB video
```

Only future latents are noised and supervised. Clean historical latents remain in the token sequence so predicted tokens can attend to observed evidence. This data flow is the paper-described architecture; [`codebase.md`](codebase.md) owns differences in the released implementation. [IRASRC-PAPER-V2, pp.4-6, Fig.2]

### 2.2 Frozen latent representation

Each RGB frame is encoded independently by the frozen Stable Diffusion XL VAE:

```text
z[i] = Enc(I[i])
I[i] = Dec(z[i])
```

Diffusion operates on the future latent sequence `x_0 = z[t+1:t+n+1]`, not directly on pixels. The frozen codec reduces spatial cost and supplies a strong image prior, but it also fixes the information bottleneck: small contact, gripper, or object-state details discarded by the VAE cannot be recovered by a better dynamics model. The paper does not include a codec ablation. [IRASRC-PAPER-V2, pp.4-6]

### 2.3 Diffusion objective and clean-history conditioning

For a sampled diffusion step, Gaussian noise is added only to future-frame latents. Historical latents remain clean, and the noise-prediction loss is evaluated only at future positions:

```text
x_t = sqrt(alpha_bar_t) * x_0 + sqrt(1 - alpha_bar_t) * epsilon
L_simple = E ||epsilon_theta(x_t, t, c) - epsilon||^2
```

The condition `c` contains the clean historical latent prefix and the action trajectory. At inference, future positions begin from Gaussian noise and are iteratively denoised; the resulting future latents are decoded to RGB frames. The paper uses DDPM epsilon prediction and reports PNDM with 50 steps for evaluation. [IRASRC-PAPER-V2, pp.4-6, Eqs.2-3; pp.21-22]

### 2.4 Spatial-temporal DiT backbone

IRASim patchifies the concatenated latent sequence and alternates two factorized transformer operations:

- a **spatial block** applies attention among patches within each frame, using token shape `(N, P, D)`;
- a **temporal block** reshapes tokens to `(P, N, D)` and applies attention along time for each spatial position.

Here `N` is frame count, `P` is patches per frame, and `D` is hidden width. This avoids the quadratic cost of one attention operation over every spatiotemporal token. Fixed 2-D spatial and 1-D temporal sinusoidal embeddings provide position information. [IRASRC-PAPER-V2, pp.4-6, Fig.2; pp.20-21]

The main XL model has 28 transformer layers, width 1,152, 16 heads, patch size 2, dropout 0.1, and approximately 679M parameters. The scaling study also defines S, B, and L variants: [IRASRC-PAPER-V2, pp.21-24, Tables 10-11]

| Variant | Layers x width | Heads | Parameters |
|---|---:|---:|---:|
| S | `12 x 384` | 6 | 33M |
| B | `12 x 768` | 12 | 132M |
| L | `24 x 1024` | 16 | 461M |
| XL | `28 x 1152` | 16 | 679M |

### 2.5 Action conditioning: Video-Ada versus Frame-Ada

Both variants use adaptive layer normalization to convert the diffusion timestep and action information into residual gates, scales, and shifts.

**Video-Ada** encodes the complete action trajectory into one vector. That vector is combined with the diffusion-timestep embedding and modulates every spatial and temporal block. Every frame therefore receives the same action summary. [IRASRC-PAPER-V2, pp.5-6, 20, Eqs.4-7]

**Frame-Ada** separates the spatial and temporal conditions:

- for frame `i`, action `a[i]` is embedded separately and combined with the diffusion timestep to modulate that frame's spatial attention and feed-forward operations;
- temporal blocks still use one embedding derived from the complete trajectory, allowing coordination across the generated sequence;
- the historical position has no corresponding future action; the released implementation represents that slot with a learned placeholder, while the paper describes the generated-frame alignment at the method level.

Conceptually:

```text
spatial condition for frame i = time_embedding + action_embedding(a[i])
temporal condition            = time_embedding + trajectory_embedding(a[t:t+n])
```

Frame-Ada therefore does not replace global temporal reasoning. It adds explicit local action-frame alignment to spatial processing while preserving chunk-level temporal context. The paper does not report a no-action, shuffled-action, or parameter-matched control, so its main ablation demonstrates an effective conditioning design rather than a complete causal decomposition. The paper-described global temporal action condition is absent from the released Frame-Ada path; [`codebase.md`](codebase.md) owns that material paper-code mismatch. [IRASRC-PAPER-V2, pp.5-6, 20-21, Eqs.8-9; IRASRC-CODE-CURRENT]

### 2.6 Output and inference

After the repeated spatial-temporal blocks, a linear output layer and unpatchification produce predicted noise for future-frame latents. Reverse diffusion yields the future latent sequence, which the frozen VAE decodes. Short prediction generates all future frames in one denoising process. Long prediction chains clips autoregressively by using the last generated frame as the next history frame. [IRASRC-PAPER-V2, pp.5-8]

## 3. Experimental setup

### 3.1 Datasets and action interfaces

| Dataset | History -> future | Resolution | Action representation | Train episodes / clips | Validation | Test |
|---|---|---|---|---:|---:|---:|
| RT-1 | `1 -> 15` | `256 x 320` | 7-D relative XYZ, Euler rotation, next gripper joint angle | `82,069 / 2,314,893` | `2,167 / 4,810` | `2,167 / 4,799` |
| Bridge | `1 -> 15` | `480 x 640` resized to `256 x 320` | same 7-D contract | `25,460 / 482,701` | `1,737 / 2,905` | `1,738 / 2,946` |
| Language-Table | `1 -> 15` | `360 x 640` resized to `288 x 512` | 2-D relative XY | `170,256 / 1,483,133` | `4,446 / 5,119` | `4,562 / 5,243` |
| RoboNet | `2 -> 10` | `256 x 256` | universal 5-D delta XYZ, yaw, gripper; missing platform dimensions are zero-padded | `162,161 / 2,540,500` | none | `256 / 407` |

For the first three datasets, a 16-frame clip represents approximately four seconds at the paper's nominal 4 FPS. Training uses overlapping sliding windows; validation and test windows advance by a full clip. Episode and clip counts are distinct units and must not be summed or compared as if interchangeable. Coordinate frames, normalization statistics, synchronization tolerance, and complete platform masks remain under-specified. [IRASRC-PAPER-V2, pp.6-7, 19-20, Table 7]

### 3.2 Baselines and metrics

The main comparison includes pixel-space VDM, latent-space LVDM, Video-Ada, and Frame-Ada. VDM and LVDM use a pooled trajectory condition; LVDM shares the SDXL VAE and training setting with IRASim. RoboNet uses published iVideoGPT and MaskViT numbers rather than one rerun implementation. [IRASRC-PAPER-V2, pp.6-9, 20-21]

The paper prioritizes paired PSNR and latent L2 for short and long prediction. It also reports SSIM, FID, FVD, and human preference for short clips. These measure different properties: FID/FVD are distribution metrics and do not directly establish action fidelity, contact correctness, or control utility.

### 3.3 Training and inference configuration

The main models are trained from scratch with AdamW, constant learning rate `1e-4`, batch 64, gradient clipping 0.1, EMA 0.9999, and no weight decay. Evaluation uses 50 PNDM steps. The paper reports 32 concurrent GPUs and about 2,369-2,381 GPU hours for each of RT-1, Bridge, and Language-Table. [IRASRC-PAPER-V2, pp.21-24, Tables 10-12]

The step count is internally inconsistent: Appendix E says 300K, released configs and checkpoint names use 300K, while Table 10 prints 3M. The implementation-aligned value is 300K, but the contradiction must remain visible in a reproduction record. A 16-frame sample reportedly takes about 30 seconds and 8 GB on one A100; this does not guarantee the same memory use on another accelerator or software stack. [IRASRC-PAPER-V2, pp.21-24; IRASRC-CODE-CURRENT]

## 4. Trajectory-conditioned video prediction

### 4.1 Short-horizon prediction

Frame-Ada is best on both paper-declared primary metrics across the three main datasets: [IRASRC-PAPER-V2, pp.7-9, Table 1]

| Dataset | LVDM PSNR / latent L2 | Video-Ada | Frame-Ada | Main reading |
|---|---:|---:|---:|---|
| RT-1 | `25.041 / 0.2244` | `25.446 / 0.2191` | `26.048 / 0.2099` | fine-grained conditioning improves paired reconstruction |
| Bridge | `23.546 / 0.2155` | `24.733 / 0.2021` | `25.275 / 0.1947` | same direction under another 7-D domain |
| Language-Table | `28.254 / 0.1704` | `23.893 / 0.2028` | `28.818 / 0.1660` | pooled Video-Ada degrades sharply; Frame-Ada recovers |

Frame-Ada does not dominate every auxiliary metric: LVDM has slightly better Language-Table SSIM and FVD, and LVDM or Video-Ada has lower FID on RT-1 and Bridge. The supported claim is improved paired prediction on the stated primary metrics, not universal visual-metric superiority.

On RoboNet, IRASim reports PSNR `24.6` and SSIM `81.1`, compared with `23.8/80.8` for iVideoGPT and `20.4/67.1` for MaskViT. The baseline numbers are imported, tokenizer pretraining differs, and this is not an isolated architecture ablation. [IRASRC-PAPER-V2, pp.8, 20-21, Table 2]

### 4.2 Long-horizon prediction

For long rollouts, the final generated frame of one clip conditions the next clip. Mean evaluated lengths are 42.5 frames for RT-1, 33.4 for Bridge, and 23.7 for Language-Table. Frame-Ada has the best PSNR and latent L2 among VDM, LVDM, Video-Ada, and Frame-Ada on all three datasets. The paper omits horizon-conditioned error curves, physical-state metrics, and calibrated uncertainty, so qualitative sequences longer than 150 frames do not establish stable long-horizon dynamics. [IRASRC-PAPER-V2, pp.6-8, 22, Table 3]

### 4.3 Human preference

Five participants each judge 90 randomized pairs, producing 450 judgments. Ground truth is visible and ties are allowed. [IRASRC-PAPER-V2, pp.9, 23-24, Fig.4]

| Frame-Ada comparison | RT-1 win/tie/loss | Bridge | Language-Table |
|---|---:|---:|---:|
| versus VDM | `100/0/0` | `100/0/0` | `100/0/0` |
| versus LVDM | `60/12/28` | `72/16/12` | `68/10/22` |
| versus Video-Ada | `38/32/30` | `36/30/34` | `66/20/14` |

The study strongly separates Frame-Ada from VDM and favors it over LVDM. It weakly separates Frame-Ada from Video-Ada on RT-1 and Bridge; confidence intervals, inter-rater agreement, and participant expertise are not reported.

### 4.4 Scaling

The S, B, L, and XL Frame-Ada variants are compared at 150K and 300K steps. Larger tested variants have lower latent L2 on the plotted RT-1, Bridge, and Language-Table curves. This supports a monotonic trend within those four architectures and two checkpoints, not a general scaling law or a compute-optimal conclusion. [IRASRC-PAPER-V2, pp.9, 23-24, Fig.5]

## 5. Policy evaluation

The paper evaluates four diffusion-policy checkpoints on one LIBERO task. Each checkpoint receives 50 MuJoCo trials and 50 IRASim rollouts; humans label success in generated videos. [IRASRC-PAPER-V2, pp.9-10, Table 4]

| Policy checkpoint | 1 | 2 | 3 | 4 |
|---|---:|---:|---:|---:|
| MuJoCo success | 0.18 | 0.50 | 0.80 | 1.00 |
| IRASim success | 0.28 | 0.48 | 0.74 | 0.96 |

The reported Pearson correlation is `0.99`, showing preserved ordering for four checkpoints in this task. It is not a general simulator-calibration result: the correlation has four paired points, one task, one policy family, and human labels, with no confidence interval or held-out-task test.

## 6. Model-based planning

### 6.1 Push-T candidate ranking

A diffusion policy proposes `K` action trajectories. IRASim predicts the resulting videos, a separate ResNet50 estimates terminal IoU from the final predicted frame, and the highest-scoring action sequence is executed. The policy is trained from 200 expert demonstrations. `P` is the number of additional successful and failed policy rollouts used to adapt IRASim. [IRASRC-PAPER-V2, pp.10-13, Table 5; IRASRC-GPC]

| World-model data | `K=1` | `K=5` | `K=10` | `K=50` |
|---|---:|---:|---:|---:|
| IRASim, `P=0` | 0.637 | 0.679 | 0.572 | 0.418 |
| IRASim, `P=100` | 0.637 | 0.847 | 0.878 | 0.888 |
| IRASim, `P=200` | 0.637 | 0.866 | 0.916 | 0.912 |
| IRASim, `P=500` | 0.637 | 0.907 | 0.906 | 0.938 |
| IRASim, `P=1000` | 0.637 | 0.886 | 0.945 | 0.961 |

The important interaction is between data support and search. With no post-trained rollout data, increasing candidate count eventually reduces realized IoU, consistent with model or evaluator exploitation. After exposing the model to policy successes and failures, search becomes useful. The table does not support the paper prose's strict monotonicity claim for every `P>0`: small reversals occur for `P=200` and `P=500`.

### 6.2 Real-robot goal-image planning

For each of three tasks, the system samples 50 end-effector trajectories, predicts 50 videos, ranks final frames against a goal image, and executes the top five. Each task is repeated three times. [IRASRC-PAPER-V2, pp.12-13, 22-23, Table 6]

| Ranking method | Close drawer | Mandarin to green plate | Mandarin to red plate |
|---|---:|---:|---:|
| random proposal | 0.20 | 0.07 | 0.13 |
| IRASim + ResNet50 cosine | 0.60 | 0.73 | 0.60 |
| IRASim + pixel MSE | 0.87 | 0.80 | 0.87 |

Pixel MSE outperforms the learned ResNet50 cost on all three tasks, showing that evaluator choice is an independent optimization variable. All tasks come from the training dataset, the execution count is small, and the paper does not report held-out scenes, safety events, latency, or the full public planning stack.

## 7. Flexible action controllability

Keyboard and VR demonstrations send user-defined or out-of-distribution actions to IRASim and visualize the predicted response. These examples show that the conditioning interface can respond beyond replayed expert trajectories. They do not quantify counterfactual accuracy or safety. A qualitative example in which the model appears to avoid moving through a table is not evidence of a verified constraint model. [IRASRC-PAPER-V2, pp.13-14, 19, 28]

## 8. Conclusions and evidence boundaries

The paper's strongest architecture evidence is that frame-indexed spatial conditioning improves the declared paired-prediction metrics over a pooled trajectory condition while retaining trajectory-level temporal modulation. Its strongest decision-use evidence is the `P x K` interaction: world-model data must cover policy failures before larger candidate search is reliable.

The following claims remain unsupported or narrowly supported:

- no shuffled, zeroed, sign-flipped, or matched-counterfactual action test isolates causal action sensitivity;
- no contact, collision, object-pose, grasp-state, or constraint metric measures physical fidelity directly;
- no calibrated uncertainty separates multimodal futures from model error;
- the LIBERO correlation covers four checkpoints on one task;
- real-robot planning uses three training-set tasks and few executions;
- exact paper-era SDXL and OpenSora revisions, complete preprocessing, seeds, and inner checkpoint hashes are unresolved;
- the public repository covers the original RT-1/Bridge/Language-Table surface, not the complete ICCV-v2 decision stack.

These limits narrow the evidence; they do not negate the reported trajectory-prediction or planning experiments. [`reproduction.md`](reproduction.md) owns executed-state claims, and [`codebase.md`](codebase.md) owns paper-code mismatches.

## Sources

- [IRASRC-PAPER-V2] *IRASim: A Fine-Grained World Model for Robot Manipulation*, arXiv:2406.14540v2 / ICCV 2025.
- [IRASRC-CODE-CURRENT] ByteDance IRASim public repository at the pinned commit.
- [IRASRC-GPC] *Strengthening Generative Robot Policies through Predictive World Modeling*, used to identify the Push-T comparison family.
