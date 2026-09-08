---
id: world-model-kb.components.fast-video-inference.few-step-distillation
title: Few-Step and One-Step Video Distillation
kind: component
status: maintained
last_updated: 2026-09-08
owners:
  - AIBuildAI world-model group
---

# Few-Step and One-Step Video Distillation

## Retrieval metadata

**Relevant queries:** few-step video generation, one-step video generation, diffusion distillation, flow distillation, latent consistency model, distribution matching distillation, DMD2 video, rCM, Transition Matching Distillation, Phased DMD, DUET, sampling-step reduction, NFE, video-generation latency, Cosmos distillation.

**Knowledge provided:** A causal account of the main video-distillation paradigms and their evolution; normalized cost semantics; evidence-bound comparisons; failure diagnosis; implementation availability; and transfer hypotheses for video world models and Cosmos-family generators.

**Related pages:** [Diffusion and Flow Matching](../../foundations/learning-objectives/diffusion-and-flow-matching.md) owns the generic objectives; [Flow Matching and Rectified Flow](../generative-modeling/flow-matching-and-rectified-flow.md) owns path geometry and numerical solvers; [Generative Method Comparison](../generative-modeling/comparison-and-optimization.md) owns broader generator-family selection; [Cosmos-Predict2.5](../../papers/cosmos-predict2-5/README.md) owns its report-era rCM result and current code boundary; [Cosmos3-Nano Generator](../../models/cosmos3-nano/generator.md) owns the later target architecture.

## Scope and operating definition

Few-step distillation replaces an expensive teacher sampling process with a learned student process that reaches a useful output in fewer sequential transitions or less backbone computation. The teacher and student may share an architecture, but the student is a new post-trained model: reduced-step sampling of an unchanged teacher is a truncation baseline, not distillation.

Let a teacher move through states \(x_{t_K},\ldots,x_{t_0}\) with a denoiser or velocity model \(F_\psi\). A distilled student \(G_\theta\) learns one or more larger transitions,

\[
x_{t_{k-1}} = G_\theta(x_{t_k},t_k,t_{k-1},c),
\]

or directly predicts a clean endpoint. The training signal may match teacher trajectories, enforce consistency between noise levels, match teacher and student distributions, discriminate real from generated samples, optimize a reward, or combine these signals. The choice changes which teacher properties can be preserved and which failure modes are likely.

This page concerns learned reduction of video-generation cost. It does not own:

- generic diffusion or flow mathematics;
- training-free scheduler or solver changes;
- attention kernels, caching, quantization, parallel serving, or causal streaming;
- a named model's checkpoint and runtime contract;
- claims that media realism alone establishes a useful world model.

## Cost semantics: step, NFE, and latency are not synonyms

### Sampling step

A sampling step is one outer state transition in the declared schedule. Its meaning depends on the scheduler, solver order, parameterization, and whether an inner refinement loop is hidden inside the transition. Step count is interpretable only with that schedule.

### Neural-network evaluation

An NFE is one invocation of the counted neural network. For a simple first-order sampler with one conditional pass per transition, \(K\) steps may equal \(K\) NFE. This equality breaks in common cases:

- classifier-free guidance can evaluate conditional and unconditional branches, often doubling denoiser compute even when batched;
- predictor-corrector or second-order solvers can call the network more than once per outer step;
- Time Travel Sampler reports one outer step but two NFE;
- Transition Matching Distillation reuses a large backbone and applies several small flow-head updates, so its effective NFE is fractional relative to one full-network call;
- cascades and expert relays may use different networks in different time regions.

For a backbone with \(L\) layers, a transition head containing the final \(H\) layers, \(M\) outer transitions, and \(N\) head updates per transition, TMD defines:

\[
\operatorname{NFE}_{\mathrm{eff}}
=M\left(1+(N-1)\frac{H}{L}\right).
\]

This normalization is useful within the stated architecture but is not a hardware-independent FLOP or latency measure. [FVI-TMD-PAPER, Secs. 3–4]

### Denoising and end-to-end latency

For one generated sample,

\[
T_{\mathrm{e2e}}
=T_{\mathrm{condition}}
+T_{\mathrm{encode}}
+T_{\mathrm{denoise}}
+T_{\mathrm{decode}}
+T_{\mathrm{I/O}}.
\]

Distillation primarily reduces \(T_{\mathrm{denoise}}\). Text encoding, input encoding, VAE decoding, synchronization, data transfer, and launch overhead create an end-to-end floor. DOLLAR's timing decomposition illustrates this directly: its reported one-step denoising fraction is far smaller than its one-step end-to-end fraction because non-denoising work remains. [FVI-DOLLAR-PAPER, Sec. 4.4 and Table 4]

The corresponding ratios are distinct:

\[
S_{\mathrm{denoise}}=
\frac{T^{\mathrm{teacher}}_{\mathrm{denoise}}}
{T^{\mathrm{student}}_{\mathrm{denoise}}},
\qquad
S_{\mathrm{e2e}}=
\frac{T^{\mathrm{teacher}}_{\mathrm{e2e}}}
{T^{\mathrm{student}}_{\mathrm{e2e}}}.
\]

Latency also differs from throughput. A batched benchmark can improve samples per second while increasing time to the first completed video. Peak memory, model residency, compilation, warm-up, precision, and communication remain separate resource variables.

### Minimum identity of a speed claim

A reusable speed claim binds at least:

\[
\{\text{checkpoint, task, resolution, frames, fps, precision, hardware,
batch, scheduler, guidance, steps, NFE, measured region}\}.
\]

Ratios that omit these fields can describe a paper's local experiment but cannot support a cross-system ranking. A step ratio such as \(50/4=12.5\times\) is not automatically a latency ratio.

## Distillation paradigm map

| Paradigm | Training object | Main preservation pressure | Characteristic risk | Representative video use |
|---|---|---|---|---|
| Consistency or trajectory matching | outputs at two noise levels or a teacher transition | follow a compressed teacher path | smoothing, weak detail, teacher-path bias | VideoLCM, T2V-Turbo, MCM, OSV, DOLLAR |
| Distribution matching | student marginal distribution through real/teacher and fake score estimates | distribution-level fidelity without paired trajectories | reverse-KL mode dropping, unstable online fake score | video DMD2 implementations, TMD, Phased DMD, DUET low-noise expert |
| Adversarial matching | discriminator features or real/fake classification | local realism and high-frequency appearance | temporal shortcuts, instability, mode collapse | MCM, OSV, DMD2 hybrids |
| Reward-guided post-training | differentiable semantic, aesthetic, motion, or latent reward | optimize a chosen preference proxy | reward overoptimization and metric-specific regression | T2V-Turbo, DOLLAR, DUET+ |
| Score-regularized consistency | continuous-time consistency plus score/distribution regularizer | combine consistency diversity with high-quality distribution pressure | weighting and score-estimation sensitivity | rCM |
| Phased, expert, or architecture-aware transition matching | specialize time regions or reuse expensive representations | allocate capacity and computation by denoising role | relay mismatch, expert seams, non-equivalent NFE | Phased DMD, TMD, DUET |

These labels overlap. A system can combine consistency, adversarial, distribution, and reward terms. The useful comparison unit is the exact loss and sampling graph, not the method name alone.

## Historical and causal evolution

### VideoLCM: transfer image consistency distillation to latent video

**Limitation addressed.** A pretrained latent video diffusion model required many sequential denoising iterations, while direct large-step truncation degraded temporal structure and detail.

**Technical change.** VideoLCM distills a frozen video teacher into a latent consistency student with the teacher architecture as initialization. The teacher uses fixed classifier-free guidance during training; the student inference path does not require that guidance. The learned consistency map permits a small number of large transitions rather than replaying the teacher trajectory. [FVI-VIDEOLCM-PAPER, Secs. 3–4]

**Evidence.** The paper's A100, batch-eight timing table reports 16-frame \(256\times256\) generation decreasing from 60 seconds for its 50-step baseline to 10 seconds for four-step VideoLCM, and 16-frame \(448\times256\) generation decreasing from 104 to 16 seconds. Its step ablation reports visibly weak one-step output and substantially better four-to-six-step output. These are protocol-bound latency observations, not universal six-fold or 6.5-fold constants. [FVI-VIDEOLCM-PAPER, Table 1 and Fig. 6]

**Remaining failure.** One-step generation remains blurry and can lose temporal structure. The consistency objective inherits teacher limitations and does not independently enforce text alignment, appearance realism, motion amplitude, or distribution coverage.

**Implementation surface.** VGen exposes VideoLCM training and inference configurations and public checkpoint instructions at the pinned revision. This is an inspectable training surface, not a local reproduction record. [FVI-VIDEOLCM-CODE]

### T2V-Turbo: repair the quality and alignment ceiling with mixed rewards

**Limitation addressed.** Consistency distillation alone compressed the trajectory but left a quality and prompt-alignment gap. Optimizing only frame appearance could also neglect video-level semantics.

**Technical change.** T2V-Turbo adds differentiable image-text reward and video-text reward feedback to consistency distillation. The reward is applied to the student's one-step prediction during training, avoiding backpropagation through a full teacher sampling trajectory. Only LoRA parameters are trained and then merged, so the architecture's per-call cost remains close to that of its teacher. [FVI-T2V-TURBO-PAPER, Secs. 3–4]

**Evidence.** Four-step students distilled from VideoCrafter2 and ModelScopeT2V report VBench totals of 81.01 and 80.62, respectively, and the paper's human study prefers the four-step students to their corresponding 50-step teachers. The 12.5-fold step reduction does not by itself establish 12.5-fold end-to-end acceleration. [FVI-T2V-TURBO-PAPER, Tables 1–3]

**Remaining failure.** Reward models define a narrow proxy. Strong semantic or aesthetic reward can suppress motion, diversity, or behaviors outside the reward model's training distribution. The method also retains the underlying consistency teacher's trajectory bias.

**Implementation surface.** The official repository exposes training scripts, inference applications, and checkpoints for named variants. Current-repository variants must remain tied to their commands and weights rather than treated as one undifferentiated paper model. [FVI-T2V-TURBO-CODE]

### MCM: disentangle motion preservation from appearance sharpening

**Limitation addressed.** Video teachers may provide temporally coherent but visually imperfect training frames. A frame discriminator can improve appearance while disrupting motion, and purely generated student trajectories can collapse.

**Technical change.** Motion Consistency Model applies consistency distillation to a motion representation while an image discriminator supplies appearance supervision. Its mixed-trajectory training combines teacher/real-derived states with student-generated states, addressing both teacher-frame quality and the train–inference state mismatch. [FVI-MCM-PAPER, Secs. 3.2–3.4]

**Evidence.** For ModelScopeT2V on the paper's WebVid evaluation, the four-step consistency baseline reports FVD 603 and CLIPSIM 30.48, while MCM reports FVD 456 and CLIPSIM 30.55. On MSR-VTT, the corresponding values are 713/28.45 and 414/28.86. The paper also records approximately 5% all-black mode collapse under a generated-only trajectory variant, motivating the mixture rather than establishing it as universally optimal. [FVI-MCM-PAPER, Tables 1–3 and Sec. 4.3]

**Remaining failure.** Motion and appearance are only partially separable: a representation or discriminator can encode shortcuts, and image-level realism does not guarantee temporal causality. The published training run used substantial hardware, so student inference efficiency does not imply inexpensive post-training.

**Implementation surface.** The public repository contains LoRA training and inference paths for ModelScopeT2V and AnimateDiff, checkpoints, and explicit memory guidance. [FVI-MCM-CODE]

### OSV: make one-step image-to-video adversarial distillation feasible in latent space

**Limitation addressed.** One-step image-to-video generation loses detail and motion; pixel-space adversarial supervision incurs expensive VAE decoding and high memory.

**Technical change.** OSV first adapts an SVD student on real data with latent adversarial and reconstruction-style supervision, then applies adversarial consistency distillation on teacher data. A frozen DINOv2 feature discriminator consumes upsampled latent features, avoiding VAE decoding in the discriminator path. Time Travel Sampler adds a return-and-refine operation at inference. [FVI-OSV-PAPER, Secs. 3.2–3.5]

**Evidence.** The paper reports its latent discriminator reducing an iteration from 4.29 to 2.61 seconds and memory from 73.5 to 35.8 GB relative to the compared decode-based setup. On its table, one-step/one-NFE OSV has FVD 335.36; one outer step with TTS uses two NFE and reaches 171.15; ordinary two-step/two-NFE reaches 181.95; the 25-step SVD teacher uses 50 NFE and reaches 156.94. [FVI-OSV-PAPER, Tables 1 and 4]

**Remaining failure.** The paper identifies difficult hand motion and motion attenuation; four steps improve some fine motion. Image-to-video conditioning can make static input reconstruction an easy shortcut. Calling TTS a one-step sampler without its two-NFE qualifier hides material compute.

**Implementation surface.** No official public repository was linked from the checked paper, CVF page, or author-facing release surface as of 2026-09-08. This is an availability observation, not evidence that code cannot appear later. [FVI-OSV-PAPER]

### DOLLAR: combine distribution fidelity, consistency diversity, and latent reward

**Limitation addressed.** Variational score distillation can sharpen samples while dropping modes; consistency distillation can preserve coverage but smooth detail; direct reward backpropagation through a large reward network and VAE is expensive.

**Technical change.** DOLLAR combines VSD with generalized multi-teacher-step consistency distillation, then applies a learned latent reward model. The complementary losses target fidelity and diversity, while the latent reward avoids differentiating through the full external reward model and decoder at every update. [FVI-DOLLAR-PAPER, Secs. 3.2–3.4]

**Evidence.** The four-step model reports VBench total 82.57 under its HPSv2 configuration versus 80.25 for the 50-step teacher, alongside Vendi diversity measurements. For 128 frames at \(192\times320\) on one A100 80GB, the paper normalizes teacher end-to-end inference to 100% and reports 13.06%, 9.30%, and 7.45% for four-, two-, and one-step variants. The corresponding diffusion-only fractions are 5.88%, 2.16%, and 0.33%, exposing the non-denoising latency floor. [FVI-DOLLAR-PAPER, Tables 1, 3, and 4]

**Remaining failure.** The paper observes reward overoptimization and metric conflict; PickScore-oriented optimization can harm motion. Its results use a specific internal teacher, latent codec, frame count, resolution, and reward stack. The official project page exposed samples and the paper but no public distillation-training repository at the access date. [FVI-DOLLAR-PAPER, Sec. 4.5; FVI-DOLLAR-PROJECT]

### DMD and DMD2: move from paired trajectory imitation to distribution matching

**Limitation addressed.** A student trained only on paired teacher trajectories can overfit a prescribed path, while one-step generators need a signal that compares the student's entire output distribution with the teacher distribution.

**Technical change.** DMD estimates a distribution-matching gradient from a frozen real/teacher score and an online fake score trained on student samples. A regression loss on precomputed noise–image pairs stabilizes training and helps preserve modes. DMD is an image-generation result and supplies a conceptual mechanism, not direct video evidence. [FVI-DMD-PAPER, Secs. 3–4]

DMD2 removes the expensive regression-pair dataset, updates the fake score more frequently than the generator, adds a GAN term on real data to correct teacher-score imperfections, and supports multi-step students. Backward simulation exposes training to states closer to those encountered during student inference, directly addressing train–inference mismatch. [P25-DMD2, Secs. 3–4]

**Remaining failure.** Distribution matching relies on an accurately tracked fake score. Reverse-KL-like pressure can prefer a high-quality subset and lose modes; adversarial correction adds instability. The official DMD2 repository at the pinned revision implements ImageNet, Stable Diffusion, and SDXL paths, not video. [FVI-DMD2-CODE]

**Video implementation bridge.** FastVideo currently exposes a sparse-distillation recipe described as DMD plus Video Sparse Attention, with training configurations, checkpoints, and three-step FastWan variants. It operationalizes video distillation across supported backbones, but its current documentation and heterogeneous performance claims are not a controlled benchmark against the papers above. Its `real_score_guidance_scale` is an extra conditional scale; the documentation maps standard CFG to that value plus one, a convention that can silently invalidate a port. [FVI-FASTVIDEO-CODE]

### rCM and Cosmos-Predict2.5: regularize scalable consistency with score matching

**Limitation addressed.** Continuous-time consistency training scales well and tends to preserve coverage, but large few-step models can lose fine quality. Pure score-distribution pressure can improve quality while increasing mode-dropping risk.

**Technical change.** Score-Regularized Continuous-Time Consistency adds a DMD-like score regularizer to continuous-time consistency. Its implementation uses a FlashAttention-compatible Jacobian–vector product path to scale consistency training to large video models. The objective explicitly joins consistency's trajectory/coverage pressure with distribution matching's sample-quality pressure. [P25-RCM, Secs. 3–4]

**Evidence.** The rCM paper evaluates Cosmos-Predict2 and Wan2.1 systems up to 14B parameters and reports one-to-four-step models with sampling speedups in the 15–50-fold range under its own configurations. The Cosmos-Predict2.5 report separately gives the four-step 2B rCM student an overall Text2World score of 0.764 versus 0.768 for the base model and Image2World 0.816 versus 0.810. Those scores do not supply the missing absolute latency, memory, diversity, or long-horizon world-model measurements. [P25-RCM, Sec. 5; P25-TR, Tables 2–3]

**Version boundary.** The rCM repository now contains training, inference, checkpoints, and later causal-model extensions. Later code is not retroactive evidence for the paper's evaluated systems. More importantly, the current Cosmos-Predict2.5 release exposes DMD2/TrigFlow distillation code, while the report describes rCM. These are distinct method and release surfaces. [FVI-RCM-CODE; P25-CODE-CURRENT]

### Phased DMD: distribute capacity across SNR subintervals

**Limitation addressed.** A single one-step DMD student has limited capacity for complex motion. Naive multi-step DMD can degenerate toward one-step behavior and still lose diversity because every transition is trained against the same global distribution target.

**Technical change.** Phased DMD partitions the signal-to-noise trajectory into subintervals. Each phase matches the appropriate intermediate distribution and applies score matching within its subinterval, yielding a natural mixture-of-experts interpretation. Only one phase transition needs gradient recording at a time. [FVI-PHASED-DMD-PAPER, Sec. 3]

**Evidence.** In the reported Wan2.2 text-to-video setting, the 40-step, CFG-4 base has optical flow 10.26 and dynamic degree 79.55%; four-step DMD2 has 3.23 and 65.45%; four-step Phased DMD has 9.30 and 82.27%, with improved FID/FVD over the compared DMD2 variant. The image-to-video table shows the same direction. These figures establish a method-specific motion result, not a universal advantage over every DMD2 implementation. [FVI-PHASED-DMD-PAPER, Table 2]

**Remaining failure.** Phase boundaries add specialization and can introduce seams or duplicated capacity. The release repository exposes distilled checkpoints and inference configuration but no distillation-training implementation at the pinned revision, limiting independent method reproduction. [FVI-PHASED-DMD-PROJECT; FVI-PHASED-DMD-CODE]

### TMD: reuse expensive representations inside learned transitions

**Limitation addressed.** Counting every refinement as a full DiT evaluation ignores that early video-transformer layers build reusable semantic representations, while later layers perform more local flow prediction. Full-backbone calls dominate few-step latency.

**Technical change.** Transition Matching Distillation decomposes Wan2.1 into a large main backbone and a lightweight flow head formed from the final layers. A MeanFlow-style stage adapts the head to predict transitions; an improved DMD2 stage rolls out inner head updates and trains against those inference-like states. One backbone representation can therefore support multiple cheap refinements. [FVI-TMD-PAPER, Secs. 3.2–3.4]

**Evidence.** On the paper's 81-frame \(480\times832\) setting, the 14B model reports VBench 84.24 at effective NFE 1.38 versus 83.69 for its one-NFE DMD2-v comparator; the 1.3B model reports 83.80 at effective NFE 1.17 versus 83.24. Effective NFE is layer-normalized and must still be accompanied by measured latency. [FVI-TMD-PAPER, Tables 1–3]

**Remaining failure.** The method assumes a useful early/late layer decomposition and adds a transition-head design choice. It has been demonstrated on Wan2.1, not arbitrary multimodal or mixture-of-transformer architectures. The official project page marked code as “coming soon” on 2026-09-08, so the paper mechanism is not yet an executable public recipe in this KB. [FVI-TMD-PROJECT]

### DUET: assign diversity and quality to different time experts

**Limitation addressed.** At two NFE, consistency students preserve diversity but can lack detail, while DMD students improve quality but can collapse modes. A uniform hybrid loss asks one expert to resolve incompatible pressures across the entire trajectory.

**Technical change.** DUET uses a high-noise continuous-time-consistency expert to establish global structure and diversity, then a low-noise DMD expert to refine detail. DUET+ adds reward adaptation to the first expert and trains the second on the actual relay latents produced by that expert, reducing the distribution gap at the switch point. [FVI-DUET-PAPER, Secs. 3–4]

**Evidence.** In the paper's two-NFE Wan2.1-T2V-1.3B comparison, sCM has average diversity 0.1865 and quality 81.51; DMD has 0.0727 and 84.38; DUET has 0.1512 and 83.96; DUET+ has 0.1521 and 84.40. The result supports complementary time-region experts within this protocol. [FVI-DUET-PAPER, Table 1]

**Remaining failure.** Relay quality depends on the switch time and on matching the second expert's training distribution to the first expert's outputs. Evidence is currently limited to a recent August 2026 preprint and Wan2.1 1.3B; no official code link was located on the checked primary surfaces.

## Evidence-normalized comparison

| Method | Modality and teacher | Student budget | Guidance at student inference | Reported anchor | What the anchor does not establish |
|---|---|---:|---|---|---|
| VideoLCM | T2V, latent video diffusion | 1–8 steps; strongest stated range 4–6 | no CFG | 60 s to 10 s at 16×256², paper A100 batch-eight setup | equal latency on another resolution, model, or batch |
| T2V-Turbo | T2V, VideoCrafter2 or ModelScopeT2V | 4 steps | model-specific merged LoRA path | VBench 81.01/80.62 and teacher-preferred human study | that reward gains preserve motion or diversity everywhere |
| MCM | T2V, ModelScopeT2V or AnimateDiff | commonly 4 steps | configuration-specific | FVD 603 to 456 on its WebVid comparison | matched performance on other teachers or longer videos |
| OSV | I2V, SVD | 1 step/1 NFE; TTS 1 step/2 NFE | CFG removed | FVD 335.36 at 1 NFE, 171.15 at TTS 2 NFE | that “one step” always means one denoiser call |
| DOLLAR | T2V, internal CogVideoX-like teacher | 1, 2, or 4 steps | no CFG | four-step VBench 82.57; end-to-end 13.06% of teacher | public reproducibility or absolute cross-system latency |
| DMD2-style FastVideo | supported video flow backbones | current examples include 3 steps | recipe-specific | framework throughput and checkpoint claims | controlled method superiority across different hardware/models |
| rCM | Cosmos-Predict2 and Wan2.1, up to 14B | 1–4 steps | checkpoint-specific | report/paper quality near teacher and 15–50× sampling claims | absolute Cosmos3-Nano latency or decision utility |
| Phased DMD | Wan2.2 T2V/I2V | 4 steps, no CFG in release | no CFG | restores reported motion versus its DMD2 comparator | training-code reproducibility at the checked revision |
| TMD | Wan2.1 1.3B/14B | effective NFE 1.17–1.38 in cited rows | protocol-specific | VBench 83.80/84.24 | full-model-call equivalence or public execution |
| DUET+ | Wan2.1-T2V-1.3B | 2 NFE | protocol-specific | quality 84.40, diversity 0.1521 | generalization beyond one backbone and preprint protocol |

The rows are evidence anchors, not a leaderboard. Differences in modality, teacher, frame count, resolution, duration, guidance, evaluator version, precision, hardware, and batch prevent raw ranking.

## Cross-paper synthesis

### The bottleneck moved from step reduction to property preservation

VideoLCM established that a video teacher trajectory could be compressed to a few latent-consistency transitions. Later work increasingly targets what compression loses: T2V-Turbo adds alignment rewards; MCM separates motion and appearance pressure; OSV makes adversarial supervision practical in latent space; DOLLAR balances fidelity, diversity, and preference; rCM combines consistency and distribution regularization; Phased DMD, TMD, and DUET allocate capacity or computation by time region. The recurring problem is no longer only “how to reduce steps,” but “which teacher properties survive the reduction.”

### Diversity and local fidelity exert different optimization pressures

Consistency and forward-covering signals tend to retain broader support but can smooth detail. DMD/VSD and adversarial signals can sharpen samples while concentrating probability mass. Reward terms improve the rewarded projection and can regress unmeasured properties. MCM, DOLLAR, rCM, Phased DMD, and DUET use different structural answers to this conflict; none removes the need to measure both quality and coverage.

### High-noise and low-noise regions serve different semantic roles

High-noise transitions establish global layout, motion intent, and sample diversity; low-noise transitions refine texture and detail. Time-uniform objectives spend the same modeling structure on both roles. Phased DMD and DUET make the split explicit, while TMD makes a related computation split between representation-building backbone layers and transition-refinement layers. This pattern is a transferable hypothesis, not proof that a fixed split point works for another model.

### Training states must cover student inference states

Large student transitions move off the teacher trajectory. MCM mixed trajectories, DMD2 backward simulation, TMD inner rollouts, and DUET+ relay-latent training all address this exposure gap. A method that performs well under teacher-forced noisy inputs can still fail when its own early prediction becomes the next input.

### Guidance distillation can reduce more compute than step count suggests

If the teacher uses classifier-free guidance and the student internalizes that condition signal, the student may remove an unconditional denoiser branch in addition to reducing outer steps. The gain depends on whether branches are batched, memory-bound, or separately evaluated. Guidance conventions also differ across implementations; a numeric scale is not portable without its formula.

### Post-training cost and inference cost are separate axes

Some students need large synthetic datasets, online critics, discriminators, or hundreds to thousands of accelerator-hours. A method can be optimal for repeated deployment yet uneconomical for a small number of samples or frequent model updates. Public checkpoint availability changes deployment feasibility but does not reveal the cost of reproducing training.

## Failure diagnosis

| Observed failure | Plausible mechanisms | Discriminating probe | Relevant evidence families |
|---|---|---|---|
| Blurry frames or weak texture | consistency smoothing, codec ceiling, too-large final transition | compare VAE round trip, teacher truncation, and student by time region | VideoLCM, OSV, DOLLAR, rCM |
| Prompt or condition mismatch | reward gap, guidance mismatch, condition bypass | fixed-video semantic scoring plus prompt perturbation and negative controls | T2V-Turbo, DOLLAR |
| Motion attenuation or static-video collapse | input-image shortcut, frame reward dominance, insufficient high-noise capacity | optical flow, dynamic degree, action/state displacement, static-prompt controls | MCM, OSV, Phased DMD, DUET |
| Temporal flicker or identity drift | frame discriminator shortcut, weak temporal features, large local error | horizon-stratified identity and event consistency | MCM, OSV |
| Diversity collapse or mode dropping | reverse-KL pressure, discriminator imbalance, reward concentration | repeated-seed coverage, Vendi/LPIPS, rare-event recall, best-of-\(N\) saturation | DMD/DMD2, DOLLAR, rCM, DUET |
| Long-video degradation | short training horizon, local critic, accumulated transition error | metric and state error versus horizon at fixed FPS | all short-clip methods; no average short-video metric resolves it |
| Oscillation, black output, or divergence | fake-score lag, adversarial imbalance, generated-only exposure | critic/generator loss dynamics, fake-score lag, intermediate latent norms | MCM, DMD2 |
| Teacher bias retained | trajectory imitation or teacher-generated training distribution | compare against real held-out events, not only teacher agreement | VideoLCM, T2V-Turbo, rCM |
| One-step capacity ceiling | one map must represent multiple trajectory roles | matched one-, two-, and four-step capacity curve | VideoLCM, Phased DMD, DUET |
| Reward improves while motion/diversity falls | reward-model blind spot or exploitation | external metrics and human/event slices excluded from the reward | T2V-Turbo, DOLLAR, DUET+ |
| Good teacher-forced loss, poor rollout | training–inference state mismatch | evaluate from teacher noise states and student-generated intermediate states | MCM, DMD2, TMD, DUET+ |
| Nominal NFE gain, weak wall-clock gain | decoder floor, small-kernel overhead, communication, hidden extra calls | component-level synchronized timing with warm-up | OSV, DOLLAR, TMD |

The table maps signatures to hypotheses and probes. It does not identify a cause without the discriminating measurement.

## Evaluation contract

A comparison record is interpretable when it preserves the following fields:

~~~yaml
identity:
  method_and_version:
  teacher_checkpoint:
  student_checkpoint:
  student_initialization:
  code_revision:
task:
  modality: text-to-video | image-to-video | video-to-video | action-conditioned
  dataset_or_prompt_set:
  split_and_sample_count:
  resolution:
  frames:
  fps:
  duration_seconds:
sampling:
  teacher_scheduler_and_steps:
  student_scheduler_and_steps:
  denoiser_nfe:
  effective_nfe_definition:
  cfg_formula_and_scale:
  stochasticity_and_seed_policy:
runtime:
  hardware:
  accelerator_count:
  precision:
  batch_size:
  compile_and_kernel_state:
  warmup_runs:
  timed_region:
  denoising_latency_ms:
  decode_latency_ms:
  end_to_end_latency_ms:
  throughput:
  peak_memory_gb:
quality:
  visual_fidelity:
  temporal_consistency:
  motion_magnitude:
  prompt_or_condition_alignment:
  diversity_or_coverage:
world_model:
  state_and_event_accuracy:
  action_sensitivity:
  physical_constraint_violations:
  horizon_degradation:
  rollout_ranking_or_planning_utility:
uncertainty:
  repeated_runs:
  confidence_interval:
  missing_fields:
~~~

Three baselines isolate the source of a gain:

1. the teacher at its native schedule;
2. the unchanged teacher truncated to the student's schedule;
3. the distilled student at that same schedule.

The first-to-third comparison gives the deployed trade-off. The second-to-third comparison isolates learned distillation from merely using fewer steps. A multi-budget student curve reveals whether the checkpoint is specialized to one schedule.

Media evaluation needs complementary axes. FID/FVD or perceptual similarity does not replace motion, temporal, alignment, and diversity measures. Human preference should declare the question, raters, sampling, pair order, and uncertainty. World-model evaluation additionally needs state transitions, action consequences, physical events, horizon behavior, calibration, and downstream rollout utility.

## Public engineering surface

Availability was inspected at the pinned revisions on 2026-09-08. “Available” means that the named artifact exists in the official source; it does not mean it was executed in this KB.

| Method or release | Official training | Official inference | Official checkpoint | Backbone and material requirement | KB execution status |
|---|---|---|---|---|---|
| VideoLCM in VGen | yes; T2V entry/config | yes | linked through repository instructions | latent video diffusion; repository environment | source inspected only |
| T2V-Turbo | yes; variant-specific scripts | yes; variant-specific apps | yes | VideoCrafter2 and ModelScopeT2V variants | source inspected only |
| MCM | yes; LoRA paths | yes | yes | ModelScopeT2V and AnimateDiff; repository documents high-memory training | source inspected only |
| OSV | not located on checked official surfaces | not located | not located | SVD-based I2V in paper | paper evidence only |
| DOLLAR | not publicly linked from checked project page | not publicly linked | not publicly linked | internal CogVideoX-like latent DiT in paper | paper evidence only |
| DMD2 | yes | yes | model-dependent | released repository is image-only | source inspected; not video evidence |
| FastVideo sparse distillation | yes; DMD plus VSA recipes | yes | yes; named FastWan variants | supported Wan-family and other video backbones; large distributed recipes | source inspected only |
| rCM | yes | yes | yes | published Cosmos-Predict2 and Wan2.1 surfaces; later code is broader | source inspected only |
| Cosmos-Predict2.5 current distillation | yes; DMD2/TrigFlow path | yes | repository-dependent | rectified-flow teacher/student plus auxiliary critic | source inspected in owning Paper entry |
| Phased DMD release | no training path located | yes | yes | Wan2.2, four-step no-CFG release; documented large-memory inference | source inspected only |
| TMD | official page says coming soon | no public path on checked page | no public link on checked page | Wan2.1 1.3B/14B in paper | paper evidence only |
| DUET | no official link located | no official link located | no official link located | Wan2.1-T2V-1.3B in preprint | paper evidence only |

Implementation maturity and method evidence remain separate. A framework may be executable but not reproduce a paper's exact result; a complete paper may have no public training path; released checkpoints allow inference validation but not training reproduction.

## Cosmos and video-world-model transfer

### Direct evidence boundary

Cosmos-Predict2.5 supplies direct Cosmos-family evidence for four-step rCM in the report and a separate current DMD2/TrigFlow implementation surface. Cosmos3-Nano Generator is a later unified mixture-of-transformers system with continuous video, audio, and action latents, autoregressive semantic context, modality masks, and modality-specific diffusion times. No checked source establishes that a Predict2.5, Wan, or conventional video-DiT distillation recipe transfers unchanged to Cosmos3-Nano.

Consequently:

- shared rectified-flow lineage makes few-step post-training plausible;
- shared lineage does not establish compatible weights, latent distributions, time parameterization, attention graph, conditioning, guidance, or loss implementation;
- the approximately 8B Nano diffusion tower is not the 2B Predict2.5 student;
- a video-only student can damage audio/action synchronization or semantic conditioning even when video scores improve;
- a hosted Reasoner inference result says nothing about local Generator distillation.

[C3-TR, Secs. 3–4; P25-TR, Secs. 3.2–3.4; P25-CODE-CURRENT]

### Transfer surfaces and falsification

| Surface | Mechanism-informed hypothesis | Evidence that would support it | Result that would falsify the intended benefit |
|---|---|---|---|
| Consistency plus score regularization | rCM-like balance retains coverage while restoring few-step detail | matched diversity, event, and fidelity frontier versus pure consistency and pure DMD | quality gain with rare-event or action-response collapse |
| Time-phased experts | distinct experts preserve high-noise structure and low-noise detail | bucketed error and motion/detail gains localized to intended phases | no phase specialization or visible relay discontinuity |
| Transition head reuse | repeated lightweight refinement reduces full-tower calls | profiler-confirmed backbone reuse and lower synchronized latency | effective NFE falls but wall-clock or memory does not |
| Student-state exposure | mixed/backward/relay states reduce rollout compounding | lower error from student-generated intermediate states | teacher-forced improvement only |
| Guidance distillation | internalized conditioning removes unconditional passes | matched adherence/diversity with fewer denoiser calls | prompt/action sensitivity falls |
| Multimodal loss balancing | modality-specific consistency retains cross-modal synchrony | video–audio–action alignment at matched quality | video score gain with cross-modal desynchronization |
| Clean-prefix preservation | student respects exact conditioning frames and boundary dynamics | boundary error and condition-retention parity with teacher | prefix corruption or discontinuous first generated frames |

### World-model success criteria

For a video world model, fast generation is useful only if the compressed process preserves decision-relevant structure. In addition to media quality, relevant checks include:

- correct object state, contact, containment, and irreversible event transitions;
- changed futures under matched counterfactual actions;
- temporal alignment between action and effect;
- preservation of failure, recovery, and low-frequency outcomes;
- calibration and diversity across plausible futures rather than cosmetic variation;
- degradation versus rollout horizon;
- candidate ranking, planning regret, or realized policy outcome under a fixed downstream procedure.

A student that raises VBench or lowers FVD while erasing action consequences has improved video synthesis but failed the world-model acceleration objective.

## Method-selection knowledge

The following associations support diagnosis without imposing an experiment order:

| Evidence state | Most relevant mechanism family | Central confounder |
|---|---|---|
| Few-step structure is correct but detail is weak | adversarial, DMD, or score-regularized consistency | apparent detail may conceal temporal or diversity regression |
| Appearance improves while motion falls | motion-disentangled, phased, or high-noise/low-noise expert design | metric or discriminator may reward static sharpness |
| Diversity collapses under DMD | consistency regularization, phased DMD, or expert composition | seed variation may measure texture rather than semantic coverage |
| Teacher-forced validation is strong but free rollout fails | mixed trajectories, backward simulation, inner rollout, or relay-state matching | teacher and student state distributions differ |
| NFE is already low but latency remains high | backbone reuse or non-denoising optimization | VAE, conditioning, communication, and launch overhead |
| Prompt score improves but physical events regress | reward redesign and external event evaluation | reward model blind spots |
| One-step capacity saturates | two-to-four-step, phased, or expert student | extra steps may add calls without useful specialization |
| Cosmos transfer is under consideration | rCM and current Predict2.5 DMD2 are nearest lineage evidence | neither establishes Cosmos3-Nano compatibility |

## Open evidence questions

1. Which combination of consistency and distribution matching preserves rare physical outcomes at one to four NFE?
2. Does time-region specialization remain useful when modalities have independent noise times and masks?
3. Can a Cosmos3-style diffusion tower reuse semantic backbone states without violating its asymmetric AR-to-DM attention contract?
4. Which student-state sampling distribution best predicts long-horizon free-rollout failure?
5. How much of apparent acceleration remains after VAE decode, text/semantic conditioning, communication, and policy-loop overhead?
6. Which diversity metric distinguishes meaningful future alternatives from texture or camera variation?
7. Can action-conditioned distillation preserve counterfactual sensitivity without requiring a separate student per embodiment?
8. Does reward post-training before distillation preserve more physical utility than reward optimization of the distilled student?
9. How should a distillation critic treat generated failures that are rare in the teacher or training corpus?
10. At what deployment volume does post-training cost become preferable to training-free acceleration?

These are unresolved evidence gaps, not workflow priorities.

## Sources

Primary method evidence: [FVI-VIDEOLCM-PAPER], [FVI-T2V-TURBO-PAPER], [FVI-MCM-PAPER], [FVI-OSV-PAPER], [FVI-DOLLAR-PAPER], [FVI-DMD-PAPER], [P25-DMD2], [P25-RCM], [FVI-TMD-PAPER], [FVI-PHASED-DMD-PAPER], and [FVI-DUET-PAPER].

Public implementation and release evidence: [FVI-VIDEOLCM-CODE], [FVI-T2V-TURBO-CODE], [FVI-MCM-CODE], [FVI-DMD2-CODE], [FVI-FASTVIDEO-CODE], [FVI-RCM-CODE], [P25-CODE-CURRENT], [FVI-PHASED-DMD-PROJECT], [FVI-PHASED-DMD-CODE], [FVI-TMD-PROJECT], and [FVI-DOLLAR-PROJECT].
