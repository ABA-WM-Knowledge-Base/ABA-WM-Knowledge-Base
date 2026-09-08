---
id: world-model-kb.components.fast-video-inference.caching
title: Training-Free Caching for Video Diffusion and Flow Models
kind: component
status: maintained
last_updated: 2026-09-08
owners:
  - AIBuildAI world-model group
---

# Training-Free Caching for Video Diffusion and Flow Models

## Retrieval metadata

**Relevant queries:** video diffusion caching, DiT cache, feature reuse, residual cache, attention broadcast, PAB, FasterCache, CFG cache, TeaCache, AdaCache, MagCache, EasyCache, DeepCache, training-free acceleration, denoising latency, cache interval, cache threshold, temporal artifacts, Cosmos caching.

**Knowledge provided:** A mechanism-centered account of cross-timestep and cross-branch redundancy; a taxonomy of cached objects, refresh policies, and error correction; evidence-bound method comparisons; compatibility and failure diagnosis; an evaluation contract; and transfer hypotheses for video world models and Cosmos-family generators.

**Related pages:** [Few-Step and One-Step Video Distillation](few-step-distillation.md) owns learned step reduction; [Diffusion and Flow Matching](../../foundations/learning-objectives/diffusion-and-flow-matching.md) owns generic iterative-generation objectives; [Flow Matching and Rectified Flow](../generative-modeling/flow-matching-and-rectified-flow.md) owns path and solver behavior; [Cosmos3-Nano Generator](../../models/cosmos3-nano/generator.md) owns the target architecture, checkpoints, and sampling contract.

## Scope and operating definition

Caching accelerates an iterative generator by reusing an intermediate result instead of recomputing the corresponding operation at every denoising or flow step. It normally leaves model weights unchanged and reduces the cost of selected network evaluations rather than reducing the declared number of sampling transitions.

For a sampler with (K) states and model cost (C_k) at state (k), the uncached denoising cost is approximately

\[
C_{\mathrm{base}}=\sum_{k=1}^{K} C_k.
\]

If a cache policy executes only a subset of expensive operations and adds proxy, correction, storage, and transfer overhead, its useful cost is

\[
C_{\mathrm{cache}}=
\sum_{k=1}^{K}
\left(C^{\mathrm{executed}}_k+C^{\mathrm{policy}}_k+C^{\mathrm{memory}}_k\right).
\]

The saved FLOPs matter only when they exceed policy evaluation, cache reads and writes, device communication, synchronization, and lost kernel efficiency. The generated sample is generally approximate, not bitwise identical to the uncached baseline.

This page does not own:

- learned student weights or few-step post-training;
- scheduler or ODE-solver replacement without intermediate reuse;
- token pruning, sparse attention, quantization, compilation, or distributed execution except where they interact with cache behavior;
- autoregressive KV caching, which reuses an exact prefix under different dependency assumptions;
- a named model's checkpoint or observed runtime state.

## Where reusable computation occurs

### Adjacent denoising states

Neighboring noise levels often produce similar block inputs, residual outputs, or attention outputs. The similarity is not uniform over the trajectory. Early steps can establish global layout and motion; late steps can repair detail; transition regions can change rapidly. A single fixed interval therefore creates different approximation error at different timesteps.

### Heterogeneous blocks and operators

Spatial attention, temporal attention, cross-attention, MLP residuals, and full transformer blocks need not change at the same rate. PAB reports a U-shaped attention-difference profile and different stability across spatial, temporal, and cross-modal attention, motivating operator-specific broadcast ranges rather than one global interval. [FVI-PAB-PAPER]

### Conditional and unconditional branches

Classifier-free guidance commonly evaluates conditional and unconditional predictions at the same state. FasterCache identifies similarity between these branches as a second redundancy axis, distinct from reuse across timesteps. Eliminating a branch call can be valuable, but naive substitution can suppress high-frequency detail or change the guidance vector. [FVI-FASTERCACHE-PAPER]

### Sample and motion heterogeneity

The safe reuse duration depends on the generated sample. Static scenes, slow motion, camera cuts, contact events, fine texture, and large viewpoint changes impose different error budgets. AdaCache makes the next refresh content-dependent and uses motion regularization to allocate more computation to motion-heavy video. [FVI-ADACACHE-PAPER]

### Architecture-level hierarchy

U-Net features at different resolutions carry different information and costs. DeepCache reuses expensive high-level features while updating low-level features, establishing an architectural feature-cache baseline. Its original paper evaluates image diffusion; video support in the current repository is a later implementation surface and not original-paper video evidence. [FVI-DEEPCACHE-PAPER; FVI-DEEPCACHE-CODE]

## Cache-policy model

A cache design can be represented by five coupled decisions:

| Decision | Question | Typical choices |
|---|---|---|
| Object | What is stored? | attention output, MLP residual, block residual, high-level U-Net feature, full branch output, transformation vector |
| Location | Which operators are bypassed? | selected layers, block ranges, attention types, conditional or unconditional branch |
| Refresh | When is the object recomputed? | fixed interval, timestep schedule, feature-distance threshold, accumulated-error threshold, motion-aware rule |
| Reuse transform | How is a stale object adapted? | direct copy, extrapolation, difference correction, magnitude scaling, low/high-frequency correction |
| Protection | Where is reuse disabled or shortened? | early/late steps, high-change regions, scene transitions, modality changes, numerical-instability regions |

Let (h_k) be the expensive output at step (k), (hat h_k) its reused approximation, and (r_k\in\{0,1\}) the refresh decision. A generic policy is

\[
\hat h_k=
\begin{cases}
h_k, & r_k=1,\\
T(\hat h_j,p_k), & r_k=0,
\end{cases}
\]

where (j) is the last refresh, (p_k) is a cheap change proxy, and (T) is an optional correction. A fixed interval defines (r_k) from the step index. An adaptive policy estimates whether accumulated approximation error exceeds a budget:

\[
E_k=E_{k-1}+g(p_k), \qquad r_k=\mathbb{1}[E_k>\tau_k].
\]

The proxy, calibration, threshold, reset rule, and protected regions jointly define the method. Reporting only a cache ratio or interval omits the effective algorithm.

## Method evolution

### DeepCache: reuse architecture-level features

**Problem exposed.** Full U-Net execution repeats similar hierarchical features at adjacent denoising steps.

**Mechanism.** DeepCache selects a branch boundary, reuses high-level features from a previous step, and recomputes cheaper low-level features. The method is training-free and compatible with the original sampling schedule. [FVI-DEEPCACHE-PAPER]

**Evidence boundary.** The paper reports 2.3-fold acceleration for Stable Diffusion v1.5 with a 0.05 CLIP-score decrease and 4.1-fold acceleration for LDM-4-G with a 0.22 FID increase under its image-generation protocols. The pinned repository later includes Stable Video Diffusion and Text2Video-Zero integrations; those additions establish code availability, not paper-era video benchmarks. [FVI-DEEPCACHE-PAPER; FVI-DEEPCACHE-CODE]

**Residual risk.** A U-Net branch boundary does not transfer directly to a flat or joint-attention DiT. Fixed refresh choices remain insensitive to prompt, motion, and local trajectory change.

### PAB: cache attention according to operator-specific temporal redundancy

**Problem exposed.** Video DiTs spend heavily on attention, while attention-output differences across denoising steps are nonuniform and operator-dependent.

**Mechanism.** Pyramid Attention Broadcast computes an attention output at one step and broadcasts it to subsequent steps. Spatial, temporal, and cross-attention receive different broadcast ranges, reflecting their measured change rates. High-change portions of the trajectory receive denser computation. [FVI-PAB-PAPER]

**Evidence boundary.** PAB is training-free and reports cache-only single-device gains in the approximate 1.26–1.32-fold range across evaluated models. Its headline real-time and up-to-10.5-fold results combine PAB with broadcast sequence parallel and differing device counts; they are not cache-only speedups. [FVI-PAB-PAPER; FVI-PAB-CODE]

**Residual risk.** A schedule derived from aggregate attention statistics can misallocate compute for an individual prompt or motion pattern. Reusing attention alone also leaves MLP and other residual computation untouched.

### FasterCache: correct stale features and exploit CFG redundancy

**Problem exposed.** Directly copying adjacent-step features removes small but consequential changes, while standard classifier-free guidance performs two highly related branch evaluations.

**Mechanism.** Dynamic Feature Reuse estimates and restores the difference between reused and current features instead of treating the cached tensor as exact. CFG-Cache reuses information across conditional and unconditional branches and applies frequency-aware correction to preserve detail. [FVI-FASTERCACHE-PAPER]

**Evidence boundary.** Under the paper's declared configurations, FasterCache reports 1.67-fold speedup on Vchitect-2.0 and appendix results of 1.63-fold on CogVideoX-5B, 1.74-fold on Mochi, and 1.52-fold on DynamiCrafter I2V. These ratios bind to their respective hardware, frames, resolution, steps, guidance, and measured region. [FVI-FASTERCACHE-PAPER]

**Residual risk.** CFG reuse is irrelevant when guidance is absent or already distilled. Long CFG cache intervals can degrade fidelity; the paper observes visible degradation beyond an interval of five in its tested setting. Correction itself adds state and computation.

### TeaCache: predict when output reuse is safe

**Problem exposed.** Uniform cache intervals ignore the fluctuating difference between model outputs over timesteps. Computing the true output difference would erase the saving.

**Mechanism.** Timestep Embedding Aware Cache modulates the noisy model input with the timestep embedding and uses its relative change as a cheap proxy for output change. A calibrated polynomial rescales the proxy; accumulated change triggers a fresh model computation when it exceeds a threshold. Because the modulated input depends on the sample, the schedule can vary by prompt, unlike a timestep-only rule. [FVI-TEACACHE-PAPER]

**Evidence boundary.** The paper reports up to 4.41-fold acceleration on Open-Sora-Plan with a 0.07% relative VBench decrease under its selected threshold and benchmark configuration. The repository contains integrations for multiple image and video generators, including a Cosmos-family path; repository support does not establish the same ratio on every model or direct Cosmos3-Nano compatibility. [FVI-TEACACHE-PAPER; FVI-TEACACHE-CODE]

**Residual risk.** The proxy-to-output mapping requires calibration and can change with model, scheduler, resolution, guidance, precision, or modality. A scalar accumulated distance can hide localized motion or contact errors.

### AdaCache: adapt the schedule to video content and motion

**Problem exposed.** Two videos generated by the same model and schedule can have different temporal complexity, making one global cache policy inefficient or unsafe.

**Mechanism.** AdaCache stores residual computation from selected DiT blocks and chooses the next recomputation distance from representation change. Motion Regularization shortens reuse when motion content indicates a greater need for fresh computation. [FVI-ADACACHE-PAPER]

**Evidence boundary.** On the official Open-Sora 720p, two-second, single-A100 comparison, the project reports 419.60 seconds for baseline, 252.72 seconds for PAB, and 160.69 seconds for AdaCache, corresponding to 1.66-fold and 2.61-fold speedups. At a more aggressive policy, motion regularization changes 4.69-fold to 4.49-fold while repairing temporal artifacts. These are one project's matched settings, not universal rankings. [FVI-ADACACHE-PAPER; FVI-ADACACHE-CODE]

**Residual risk.** Motion estimates can be noisy before the video is well formed. Global motion magnitude may not identify a small but task-critical state transition.

### MagCache: model residual magnitude and accumulated skip error

**Problem exposed.** Prompt-curated calibration can overfit a reuse schedule, and residual direction similarity alone does not recover changing residual magnitude.

**Mechanism.** MagCache observes that successive residual outputs remain directionally similar while their magnitude ratio follows a comparatively stable trajectory across prompts and several video models. It estimates skipped residuals with magnitude scaling and accumulates multiplicative approximation error to decide refresh. The paper protects high-variation trajectory regions and uses one calibration sample rather than a curated prompt set. [FVI-MAGCACHE-PAPER]

**Evidence boundary.** The paper reports 2.10–2.68-fold acceleration across Open-Sora, CogVideoX, Wan2.1, and HunyuanVideo while comparing LPIPS, SSIM, and PSNR under similar compute budgets. These paired reconstruction-style metrics compare cached output with the same-seed baseline; they do not alone establish semantic, motion, or physical equivalence. [FVI-MAGCACHE-PAPER]

**Residual risk.** A shared magnitude law can fail after architecture, scheduler, guidance, or modality changes. Directional similarity in a high-dimensional residual does not guarantee preservation of rare localized events.

### EasyCache: remove offline profiling from adaptive reuse

**Problem exposed.** Calibration tables and offline profiling complicate deployment and can become stale after runtime configuration changes.

**Mechanism.** EasyCache reuses transformation vectors and decides at runtime when reuse is sufficient, without offline profiling, precomputation, or extensive parameter tuning. [FVI-EASYCACHE-PAPER]

**Evidence boundary.** The paper evaluates OpenSora, Wan2.1, and HunyuanVideo and reports 2.1–3.3-fold baseline acceleration with fidelity comparisons. Its claimed PSNR advantage is relative to prior caching methods under the paper protocol, not a universal output-quality gain over uncached generation. [FVI-EASYCACHE-PAPER; FVI-EASYCACHE-CODE]

**Residual risk.** Runtime adaptation still relies on a proxy and threshold. Eliminating offline calibration does not eliminate model-specific hook placement, state management, or validation.

## Cross-method synthesis

### Cache safety is a prediction problem

Feature similarity is an observation; a useful policy must predict whether skipping the next operation will keep downstream error within a task-relevant budget. Fixed schedules encode this prediction in timestep tables. TeaCache, AdaCache, MagCache, and EasyCache move it toward online evidence. None can infer physical importance from tensor similarity alone.

### What, when, where, and how are inseparable

The cached object determines both the saving and the error surface. Full-block residual reuse saves more than attention-only reuse but can erase more change. A refresh rule that works for one cached object cannot be transferred unchanged to another. Correction methods can extend reuse, but their own cost and approximation assumptions enter the budget.

### Protecting high-change regions dominates average similarity

PAB's U-shaped observation, AdaCache's content adaptation, and MagCache's stage-aware policy all imply that average redundancy is insufficient. Early layout or motion formation, late detail repair, cuts, contacts, and modality transitions can deserve dense execution even when most steps are redundant.

### CFG caching is an independent axis

Cross-timestep reuse and conditional–unconditional reuse can compose, but their errors enter different quantities. A stale denoiser residual perturbs the trajectory; a stale unconditional branch perturbs the guidance direction. Removing guidance through distillation also removes the branch opportunity and changes the cache design.

### Fewer steps reduce the available reuse horizon

Caching can compose with few-step distillation, quantization, efficient attention, and parallelism. Composition is not multiplicative by default. A four-step student offers fewer adjacent states, and each step can carry more trajectory change; cache-policy overhead becomes a larger fraction of runtime. The combined system therefore needs its own uncached-student control.

### Memory behavior can reverse a theoretical win

Cached video tensors are large. Peak memory, allocator behavior, read/write bandwidth, sharding, host transfers, and synchronization can erase FLOP savings or reduce admissible batch size. A valid comparison includes end-to-end latency and peak memory in addition to skipped operations.

## Architecture and runtime compatibility

| System property | Cache implication | Evidence needed before transfer |
|---|---|---|
| U-Net hierarchy | branch-level high-resolution/low-resolution reuse is natural | exact skip topology and cached tensor shapes |
| Factorized video DiT | spatial, temporal, cross-attention, and MLP may use separate policies | per-operator change and latency profile |
| Joint-attention or mixture-of-transformers | attention states mix modalities and may not expose PAB-style boundaries | direction of attention, modality masks, tower ownership, static versus changing context |
| Rectified-flow sampler | adjacent-time redundancy can exist, but published diffusion thresholds do not transfer automatically | time parameterization, solver, shift, step schedule, proxy calibration |
| Classifier-free guidance | branch caching can remove a substantial call | actual guidance implementation, batching, scales, conditional/unconditional distance |
| Clean-prefix or inpainting condition | clean tokens may be stable while generated tokens change | mask invariance and whether cached outputs mix both token groups |
| Multi-GPU sharding | cached tensors have an owner and communication path | sharding layout, collective count, cache replication, synchronization cost |
| Compiled or fused runtime | Python hooks can break graphs or fusion | graph count, recompilation, kernel trace, end-to-end timing |

## Failure diagnosis

| Observed regression | Likely cache mechanism | Discriminating probe |
|---|---|---|
| Global composition changes | refresh too sparse in high-noise or early trajectory region | disable caching for an expanding early-step window |
| Texture, text, or small objects degrade | late-step reuse or missing high-frequency correction | protect final steps; compare block and CFG caches separately |
| Motion becomes weak or frozen | temporal residuals reused too long | shorten temporal/block interval while holding spatial policy fixed |
| Flicker or identity drift increases | stale features accumulate inconsistent temporal updates | compare accumulated-error trace with per-frame feature and identity error |
| Contact, grasp, or collision changes | global proxy misses a localized event | event-centered state metric and region-aware refresh ablation |
| Prompt or control adherence drops | stale cross-attention or conditional branch | recompute cross-attention/conditional path while caching self-attention only |
| Guidance artifacts appear | conditional–unconditional correction is inaccurate | run full CFG with the same cross-timestep policy |
| Quality varies strongly by prompt | static schedule or calibration overfit | stratify by motion, camera change, texture, entities, and event density |
| Speedup disappears | policy and memory overhead dominate | operator-level trace plus cache bytes, hit rate, and synchronization time |
| Out-of-memory appears | retained activations exceed baseline peak | tensor-lifetime and peak-memory trace by cached object |
| First run is much slower | compilation or graph specialization | separate cold, compile, warm-up, and steady-state timing |

## Evaluation contract

The strongest cache comparison uses the same weights, seed, prompt or condition, initial noise, sampler, step schedule, precision, and runtime backend for uncached and cached paths. It measures both deviation from that paired baseline and independent generation quality.

```yaml
identity:
  model: repo_and_checkpoint_revision
  task: t2v_i2v_v2v_fd_id_or_wam
  cache_method: name_and_code_revision
sampling:
  resolution: [height, width]
  frames: integer
  fps: number
  scheduler: name_and_configuration
  steps: integer
  guidance: implementation_and_scales
  seed_set: explicit
cache_policy:
  cached_objects: explicit
  layer_or_branch_scope: explicit
  refresh_rule: interval_schedule_or_proxy
  threshold_and_calibration: explicit
  protected_regions: explicit
  correction_rule: explicit
runtime:
  hardware: accelerator_count_and_model
  precision: explicit
  batch_and_concurrency: explicit
  backend_and_compilation: explicit
  warmup_and_timing_boundary: explicit
efficiency:
  denoising_latency: baseline_and_cached
  end_to_end_latency: baseline_and_cached
  throughput: baseline_and_cached
  cache_hit_rate: by_object_and_stage
  policy_overhead: time
  cache_traffic: bytes_if_available
  peak_memory: baseline_and_cached
quality:
  paired_output_distance: lpips_ssim_psnr_or_latent_error
  generic_video_quality: declared_fvd_vbench_or_human_protocol
  temporal_and_motion: declared_metrics
  condition_adherence: declared_metrics
  diversity: multi_seed_distribution
world_model_utility:
  state_transition_error: task_specific
  action_counterfactual_sensitivity: task_specific
  contact_and_event_accuracy: task_specific
  downstream_ranking_or_control: task_specific
```

A cache method can remain visually close while changing the predicted state that controls a downstream decision. For world models, paired pixel or latent distance is diagnostic, not the final objective. Report distributional video metrics and task-state metrics separately.

## Public implementation surface

| Method | Official code at pinned source | Primary integration surface | Reproduction status in this KB |
|---|---|---|---|
| DeepCache | yes | diffusers-style U-Net pipelines; later SVD/T2V-Zero paths | source inspected only |
| PAB | yes, through VideoSys | Open-Sora, Latte, Open-Sora-Plan and distributed video inference | source inspected only |
| FasterCache | yes | Vchitect-2.0, CogVideoX, Mochi, DynamiCrafter adaptations | source inspected only |
| TeaCache | yes | multiple DiT image/video pipelines through model-specific patches | source inspected only |
| AdaCache | yes | Open-Sora residual caching and MoReg | source inspected only |
| MagCache | yes | Open-Sora, CogVideoX, Wan, HunyuanVideo and related pipelines | source inspected only |
| EasyCache | yes | OpenSora, Wan2.1, and HunyuanVideo | source inspected only |

Code availability does not establish identical semantics across integrations. A model-specific patch can change the cached tensor, layer range, CFG behavior, threshold scale, or sampling loop while retaining the same method label.

## Cosmos3-Nano transfer boundary

Cosmos3-Nano Generator is a unified mixture-of-transformers system: its approximately 8B diffusion tower predicts rectified-flow velocity for continuous video, audio, or action representations, while DM queries can attend to AR semantic context and DM states. It has modality-specific projections, diffusion-time conditioning, masks, and task-dependent sampling settings. [C3-TR, pp.7-14 and pp.27-32]

No checked source establishes a published caching result for Cosmos3-Nano. The Cosmos integration named in the TeaCache repository targets a different Cosmos release surface and must not be treated as evidence of Cosmos3 compatibility. The following are transfer hypotheses, not reproduced capabilities:

| Candidate | Why reuse may exist | Main invalidation risk |
|---|---|---|
| Diffusion-tower block residuals | adjacent flow times can yield similar residual computation | rectified-flow schedule and joint modality state alter proxy scale |
| Selected DM self-attention or MLP outputs | large continuous-token blocks dominate denoising cost | cached outputs can freeze motion, action response, or audio events |
| AR-derived semantic context | encoded prompt/context may be constant across denoising steps | mixed attention output also depends on changing DM queries and cannot be assumed static |
| Clean-condition projections | clean prefix or control tokens may remain fixed | masks and attention mix clean and generated tokens inside later layers |
| Conditional–unconditional branch features | applicable when a mode executes CFG | policy modes with guidance 1 may expose no branch redundancy |
| Modality-specific cache policy | video, audio, and action changes have different time scales | asynchronous noise times and cross-modal synchronization require coordinated invalidation |

The minimum useful Cosmos profile separates AR-tower, DM-tower, attention, MLP, codec, CFG, and communication time; measures feature change by layer, modality, and flow time; and tests whether a cheap proxy predicts task-state error. A visually oriented threshold is insufficient for action-conditioned rollout. Contact events, action counterfactuals, temporal synchronization, and candidate-ranking stability are relevant validation signals in addition to VBench or perceptual distance.

Cosmos3-Nano Policy-DROID already uses four denoising steps in the published configuration. That surface may have little cross-step redundancy and a high cost per approximation error. General audiovisual or forward-dynamics paths reported with fifty steps present a larger theoretical reuse horizon, but their multimodal coupling creates a stricter invalidation problem. [C3-TR, p.73, Table 21]

## Open questions

1. Which cheap proxy best predicts task-state error rather than global feature distance?
2. Can cache thresholds be normalized across schedulers, flow shifts, resolutions, and guidance scales?
3. Should temporal, spatial, action, and audio residuals maintain independent accumulated-error budgets?
4. Can event or contact detectors protect sparse but decision-critical trajectory regions without erasing speed gains?
5. How should a cache be invalidated when a clean prefix, control stream, or modality mask changes during generation?
6. Does residual correction preserve counterfactual action sensitivity when direct feature distance remains small?
7. Which cached object gives the best latency–memory trade-off under context parallelism and compiled execution?
8. How much acceleration remains after combining caching with a four-step distilled student?
9. Can an online controller learn a refresh policy without becoming a hidden post-trained model or destabilizing deterministic evaluation?

## Sources

Primary paper and pinned official-code identities resolve through [`sources.yaml`](sources.yaml): [FVI-DEEPCACHE-PAPER] [FVI-DEEPCACHE-CODE] [FVI-PAB-PAPER] [FVI-PAB-CODE] [FVI-FASTERCACHE-PAPER] [FVI-FASTERCACHE-CODE] [FVI-TEACACHE-PAPER] [FVI-TEACACHE-CODE] [FVI-ADACACHE-PAPER] [FVI-ADACACHE-CODE] [FVI-MAGCACHE-PAPER] [FVI-MAGCACHE-CODE] [FVI-EASYCACHE-PAPER] [FVI-EASYCACHE-CODE]. Cosmos architecture claims reuse the canonical identities from the Cosmos3-Nano source registry.
