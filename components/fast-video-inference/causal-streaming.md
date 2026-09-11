---
id: world-model-kb.components.fast-video-inference.causal-streaming
title: Causal and Streaming Video Generation
kind: component
status: maintained
last_updated: 2026-09-11
owners:
  - AIBuildAI world-model group
---

# Causal and Streaming Video Generation

## Retrieval metadata

**Relevant queries:** causal video diffusion, streaming video, chunk autoregression, first-frame latency, time to first chunk, online condition updates, KV cache, rolling memory, exposure bias, Diffusion Forcing, CausVid, Self Forcing, StreamingT2V, SkyReels-V2, interactive world model.

**Knowledge provided:** Temporal factorization, output availability, history-state validity, training–inference mismatch, latency–quality trade-offs, implementation boundaries, and testable transfer hypotheses for action-conditioned prediction.

**Related pages:** [Autoregressive Modeling](../generative-modeling/autoregressive.md) owns generic sequence modeling; [Few-Step Distillation](few-step-distillation.md) owns learned denoising-step reduction; [Caching](caching.md) owns approximate intermediate reuse; [Efficient Attention](efficient-attention.md) owns interaction cost and linear-state alternatives; [Action-Conditioned Video](../generative-modeling/action-conditioned-video.md) and [World Model to Policy Interface](../wm-policy-interface/README.md) own action semantics and decision use. [Video Diffusion Quantization](quantization.md) owns reduced numerical precision, calibration, real-kernel versus simulated execution, and interactions with reuse and attention. [Parallel and Distributed Inference](parallel-distributed-inference.md) owns partition choices, communication, scaling, and topology-dependent trade-offs.

## Problem: when a prediction becomes usable

A full-clip denoiser jointly updates a fixed future horizon. If every output depends on the unfinished sequence, a consumer must wait before receiving finalized frames. Generating less total work can help, but streaming targets a different quantity: the delay until a useful prefix becomes available, followed by the rate and regularity of subsequent outputs.

Offline generation remains appropriate when the complete clip, global composition, or candidate rollout is needed before use. It can also be called repeatedly in a receding-horizon system. The limitation is not that feedback is impossible, but that a fixed invocation may have no mechanism for incorporating new observations or controls before it finishes.

Temporal causality, incremental output, long-duration generation, and real-time operation are separate properties. A model can satisfy one without the others. None establishes physically correct dynamics or executable robot control.

## Temporal semantics and output boundaries

### Causal, autoregressive, chunked, and streaming are not synonyms

Let \(z^{(i)}\) denote a latent video chunk and \(c_{\leq i}\) the conditions available when that chunk is committed. A block-autoregressive model can represent

\[
p_\theta(z^{(1:M)}\mid c)
=\prod_{i=1}^{M}p_\theta(z^{(i)}\mid z^{(<i)},c_{\leq i}).
\]

Each conditional can be modeled by categorical token prediction, diffusion, or rectified flow. Autoregression across video time does not require autoregressive decoding within a chunk or a discrete token vocabulary.

| Property | What it means | What it does not establish |
|---|---|---|
| Temporal causal attention | a current query cannot read later video blocks; it can read eligible earlier blocks | low latency, good dynamics, or a streaming API |
| Chunk autoregression | complete one block before conditioning the next on it | frame-level causality inside a block |
| Streaming output | expose usable results before the full requested horizon finishes | real-time throughput or bounded memory |
| Long-video extrapolation | continue beyond a training or native clip horizon | stable identity, calibrated uncertainty, or unlimited storage |
| Interactive generation | accept changing conditions with a defined effect on subsequent outputs | correct action consequences or closed-loop control success |

Block-causal attention typically permits bidirectional interaction inside the current block. Spatial tokens at the same video time can also interact freely. Thus, “no future access” must specify whether future means a later token, latent frame, chunk, or unavailable external observation.

Known future commands, a goal, or a supplied endpoint are legitimate conditions for conditional generation. They are not future observations secretly available to an online predictor. Evaluation distinguishes these settings: endpoint-conditioned interpolation is not an unconditioned forecast.

### Video time and denoising time

For latent frame \(i\), write \(z_i^{\tau_i}=\alpha(\tau_i)z_i^0+\sigma(\tau_i)\epsilon_i\). Video index \(i\) and noise level \(\tau_i\) are independent axes. A synchronous denoiser uses a common noise level across its current sequence. A staggered schedule can keep an earlier block cleaner while later blocks remain noisy.

Changing noise schedules alone does not impose causal attention or guarantee reusable history K/V. Conversely, a block-causal backbone can perform several denoising evaluations within each temporal block. The topology, noise schedule, and commit rule together determine what can be emitted and cached.

### A chunk is not necessarily a fixed number of RGB frames

Latent-to-pixel conversion depends on temporal compression, patching, initial-frame handling, and decoder context. A causal VAE can still need an initial buffer or a group of latents before emitting pixels. A noncausal decoder or overlapping refiner can add lookahead, delay finalization, or revise earlier frames.

The relevant boundaries are **latent ready**, **decoded frame ready**, and **consumer receives frame**. An implementation that concatenates all chunks and only then decodes or returns them provides internal autoregression, not necessarily incremental delivery.

## Memory and cache validity

### Reusable history is a semantic property

K/V reuse is exact relative to a reference execution only when cached states would be unchanged by recomputation. For a causal history this can hold because appending a later block does not change earlier states. Within a diffusion block, however, noisy activations change at every denoising step; their old K/V cannot automatically serve as finalized history.

CausVid's inference algorithm denoises a chunk and then performs a clean-context forward pass at noise level zero before committing its K/V. Its released Wan implementation also contains that refresh pass. Thus four sampling steps can imply additional network work; denoising-step count alone is not total NFE. [FVI-CAUSVID-PAPER, Algorithm 2; FVI-CAUSVID-CODE, causvid/models/wan/causal_inference.py: InferencePipeline.inference]

| State | Validity condition | Invalidation or approximation risk |
|---|---|---|
| Finalized visual-history K/V | matching weights, positions, visibility, context-noise convention, and conditioning | changing the prefix or condition-dependent representations |
| Current noisy-block K/V | matching current latent and denoising time | reuse after a noise update |
| Text/condition projections | identical encoder output and projection parameters | prompt, action, guidance branch, or adapter changes |
| Causal decoder state | identical decoded prefix and codec configuration | observation correction, restart, or codec replacement |
| Rolling or compressed memory | retention policy matches the intended model | forgotten detail, altered attention support, or untrained window boundaries |

This differs from TeaCache-style approximate reuse across changing denoising evaluations. A system can use both, but their correctness assumptions and approximation errors are separate.

### Bounded cache is not unlimited memory

For batch \(B\), \(L\) layers, \(H_{\mathrm{KV}}\) KV heads, \(N_h\) retained tokens, head width \(d\), and \(b\) bytes per element, ordinary K/V storage is approximately

\[
M_{\mathrm{KV}}=2BLH_{\mathrm{KV}}N_hdb.
\]

Guidance branches, padding, temporary states, and other modalities add storage. A fixed-size rolling window bounds this term, not the entire application: accumulated output tensors, decoded frames, and delivery queues can still grow.

Keeping only recent K/V bounds direct attention context. The retained representations may summarize older information, but this is not individually recoverable long-term memory. Anchors, attention sinks, recurrent summaries, and retrieved history provide different capacity–cost trade-offs. Reindexing a cache also needs compatible positional semantics; silently resetting absolute time changes the model input.

## Method evolution

The following six works expose complementary design choices, not a required progression or a ranking.

### VideoGPT: autoregression over compressed video

VideoGPT learns discrete spatiotemporal latents with a VQ-VAE, then trains a GPT-like prior over those codes. Its codec/prior ablations expose a compression–reconstruction–model-capacity trade-off. BAIR and action-conditioned ViZDoom experiments are historical prediction evidence, not modern real-time serving results. [FVI-VIDEOGPT-PAPER, Secs. 3–4]

The pinned VideoGPT.sample generates the code grid before VQ-VAE decoding. This is a concrete example of token-autoregressive modeling without a pixel-streaming return contract. Its repository also distinguishes the simplified implementation from the separate full-paper reproduction code. [FVI-VIDEOGPT-CODE, videogpt/gpt.py: sample; README]

### StreamingT2V: continuation with short- and long-term conditions

StreamingT2V extends short-video generation through a Conditional Attention Module carrying recent-frame features and an Appearance Preservation Module carrying an initial anchor. The first supports chunk transitions; the second preserves scene and object appearance. A later overlapping refinement stage uses shared noise and randomized blending. Its consistency and motion experiments do not establish real-time throughput. [FVI-STREAMINGT2V-PAPER, Secs. 4–5]

The release separates image_to_video, enhance_video, and interpolation. The image-to-video entry computes a required number of overlapping continuation calls and returns the assembled video. Method-stage latency and final enhanced-output latency are therefore different measurements. [FVI-STREAMINGT2V-CODE, code/inference_i2v.py]

### Diffusion Forcing: separate uncertainty from sequence position

Diffusion Forcing trains with independently sampled per-token noise levels. Its original causal RNN maintains a history state and supports sampling schedules over both sequence time and noise time. Stabilized rollout and future-guided planning are distinct uses of that flexibility. Minecraft/DMLab extrapolation and the paper's decision-making tasks provide evidence under their own observation and action contracts. [FVI-DF-PAPER, Secs. 3–4]

The maintained main branch replaces the original RNN with temporal attention; its README directs original-paper reproduction to the paper branch. The current scheduling code exposes full-sequence, autoregressive, pyramid, and trapezoid schedules. Those branch and scheduling differences affect memory and extrapolation behavior. [FVI-DF-CODE, README; algorithms/diffusion_forcing/df_base.py: _generate_scheduling_matrix]

### CausVid: a causal student from a bidirectional teacher

CausVid combines block-causal video attention, initialization from teacher ODE trajectories, asymmetric distribution-matching distillation, and committed-history K/V. Bidirectional within-block modeling remains possible while later blocks are excluded. The teacher can supervise complete training clips without granting the deployed student future-observation access. [FVI-CAUSVID-PAPER, Secs. 4.1–4.3]

The paper's four-step, CogVideoX-like experimental system is not the released Wan2.1-1.3B example. The pinned repository documents three-step inference and a small MixKit training example. Its standard inference path decodes after assembling the requested latents. A paper streaming result must not be assigned to that CLI without measuring its actual output path. [FVI-CAUSVID-CODE, README; configs/wan_causal_dmd.yaml; causvid/models/wan/causal_inference.py]

### SkyReels-V2: progressive noise and long-video continuation

SkyReels-V2 adapts a full-sequence flow model using non-decreasing frame-noise schedules and a scheduler spanning synchronous and asynchronous generation. The report separately describes optional context-causal fine-tuning for K/V reuse. These are distinct from merely assigning different noise levels to frames. [FVI-SKYREELS2-PAPER, Sec. 3.4.2]

The released pipeline exposes ar_step, causal_block_size, overlap_history, and condition noising. Its README explicitly warns that asynchronous generation takes more steps and can be slower than synchronous generation. Step/guidance-distilled weights remain unchecked on its release list. “Infinite-length” denotes extendability, not measured real-time speed or guaranteed long-horizon correctness. [FVI-SKYREELS2-CODE, README; skyreels_v2_infer/pipelines/diffusion_forcing_pipeline.py: generate_timestep_matrix, extend_video]

### Self Forcing: train on the model's own generated history

Self Forcing rolls out the few-step model during training and applies a sequence-level distribution-matching objective. Sampled truncation limits differentiation through denoising, and history K/V is detached. This addresses a mismatch that noisy ground-truth prefixes do not fully reproduce: deployment conditions on model-generated errors. [FVI-SELF-FORCING-PAPER, Secs. 3.2–3.3]

Its rolling cache evicts old history. Training also simulates losing the special first-image latent; otherwise eviction produces a new context distribution. This matters beyond cache capacity. [FVI-SELF-FORCING-PAPER, Sec. 3.4]

The release exposes training rollout, causal inference, and a separate interactive demo. The ordinary CausalInferencePipeline.inference still decodes the assembled output; demo optimizations such as an alternative VAE or FP8 are separate configurations, not the paper baseline. [FVI-SELF-FORCING-CODE, pipeline/self_forcing_training.py; pipeline/causal_inference.py; README]

## Experimental anchors and latency accounting

| Source-bound comparison | Reported setting and result | What the comparison establishes |
|---|---|---|
| CausVid paper | one H100, 640×352, 120 frames/10 s, four-step student; first-output latency 1.3 s, throughput 9.4 FPS; timing includes text encoder, denoiser, and VAE | low startup delay relative to its full-clip teacher; 9.4 FPS alone does not sustain 12 FPS playback. [FVI-CAUSVID-PAPER, Sec. 5, Table 3] |
| Self Forcing paper | Wan1.3B, 832×480, four-step DMD, one H100; chunk-wise 17.0 FPS/0.69 s, frame-wise 8.9 FPS/0.45 s | smaller blocks lower startup latency but need not improve throughput. [FVI-SELF-FORCING-PAPER, Sec. 4, Table 1] |

The Self Forcing paper also evaluates an official Wan-based CausVid implementation. That row is not the original CausVid paper system. Cross-paper speed ratios require matched checkpoints, resolutions, denoising schedules, precision, codecs, timing boundaries, and hardware.

For a serialized producer emitting \(q\) new RGB frames per chunk at playback rate \(f\), media duration is \(\Delta=q/f\). If generation plus required decoding/delivery takes \(t_{\mathrm{chunk}}\), sustained playback requires average production at least as fast as consumption. Under this simplified model, \(t_{\mathrm{chunk}}\leq\Delta\) is necessary in steady state; jitter can still cause stalls. Overlap frames and interpolation do not count as newly predicted transitions.

Time to first usable output includes queueing, condition preparation, warmup if applicable, first-block denoising, decoding, and delivery. Pipelining may overlap later stages, so summed stage timings need not equal the critical path. Report measured wall time and stage breakdown separately.

For interaction, **condition-to-effect latency** is the interval from accepting a new command or observation to the first delivered prediction reflecting it. Large blocks, queued outputs, and already committed frames can delay this response even when average FPS is high. Robot planning additionally pays for candidate rollouts and evaluation; display FPS is not control-loop frequency.

## Design judgments and failure diagnosis

These are cross-paper synthesis and optimization hypotheses, not an experiment schedule.

| Observed limitation | Controllable intervention | Trade-off or failure boundary | Informative comparison |
|---|---|---|---|
| First prediction arrives too late | smaller latent chunks; fewer denoising steps; incremental decoding | lower GPU utilization, more boundaries, or codec artifacts | first usable state/frame, steady throughput, and equal-horizon quality |
| Quality drifts during open-loop continuation | generated-prefix training; matched rollout and memory policies | more sequential training work; truncated gradients limit credit assignment | teacher-forced versus self-rollout errors by horizon |
| Identity disappears after eviction | longer history, anchor, retrieved state, or trained compressed memory | memory/latency increase; anchors can resist legitimate scene changes | occlusion and reappearance with actual scene changes |
| Motion stagnates | rebalance short-term/anchor conditioning or history noising | weakened continuity or new hallucinations | motion magnitude together with identity and transition error |
| Chunk seams or flicker | align overlap, positions, first-latent handling, and decoder state | extra overlap reduces useful throughput | matched decoded boundaries and cache-disabled reference |
| Updated action has delayed or no effect | condition timing, accepted-input boundary, queue depth, cache invalidation | rebuilding context costs time; stale rollout may need discarding | timestamped opposite-action intervention |
| Forecast improves visually but worsens decisions | action-sensitive data/objective or more informative state representation | visual quality may not track task utility | predicted-versus-real action ranking and task success |
| Memory grows despite a rolling cache | bound output accumulation, decoder buffers, and delivery queue | dropping/revising outputs changes service semantics | memory slope over duration, not only peak on a short clip |

An append-only stream and a corrected forecast have different contracts. After a new observation contradicts a prediction, a consumer may start a revised rollout from the observed state rather than treating imagined history as fact. The KB identifies this modeling requirement; the surrounding Agent or controller determines when to replan and which outputs to consume.

Few-step distillation reduces each block's iterative cost. Efficient attention reduces each evaluation's interaction cost. K/V caching avoids recomputing invariant history, while approximate denoising caches skip changing work. Combining them can change the rollout distribution and cache calibration. A combined improvement needs both component controls and measurements of the final interactive path.

## Engineering and evidence contract

### Implementation map

| Surface | Pinned official code to inspect | Boundary |
|---|---|---|
| Discrete AR foundation | VideoGPT: videogpt/gpt.py, sample and forward | code-grid generation precedes decoding |
| Memory-conditioned extension | StreamingT2V: code/inference_i2v.py | continuation, enhancement, and interpolation are separate stages |
| Noise/sequence schedule | Diffusion Forcing: algorithms/diffusion_forcing/df_base.py | main-branch temporal attention differs from original paper RNN |
| Distilled causal model | CausVid: causal_inference.py and wan_causal_dmd.yaml | clean-history refresh and paper/release step mismatch |
| Progressive continuation | SkyReels-V2: diffusion_forcing_pipeline.py | inspect noise scheduling, overlap, condition noising, and output assembly |
| Generated-prefix adaptation | Self Forcing: self_forcing_training.py, causal_inference.py, wan/modules/causal_model.py | gradient truncation, cache positions, local retention, and entrypoint selection |

Repositories are pinned in [sources.yaml](sources.yaml). These are source-inspected implementation surfaces; no local generation, latency benchmark, or closed-loop reproduction is recorded here.

### A comparable streaming record

```yaml
identity:
  checkpoint_code_and_configuration: exact_revisions
  release_vs_paper_variant: explicit
generation:
  task_and_available_conditions: t2v_i2v_action_or_observation_stream
  latent_and_rgb_chunk_shapes: include_initial_chunk_exception
  temporal_compression_fps_and_positions: explicit
  within_and_between_chunk_visibility: explicit
  denoising_schedule_steps_guidance_and_nfe: include_history_refresh
  generated_horizon_and_context_horizon: separate
memory:
  cache_object_dtype_capacity_and_retention: explicit
  context_noise_and_refresh_semantics: explicit
  prompt_action_observation_reset_policy: explicit
  codec_state_and_output_queue: explicit
delivery:
  entrypoint_and_commit_rule: latent_pixel_and_consumer_boundaries
  overlap_lookahead_refinement_and_interpolation: explicit
  condition_acceptance_and_effect_timestamps: logged
runtime:
  hardware_precision_batch_concurrency: exact
  cold_and_warm_first_output_latency: separate
  chunk_latency_p50_p95_and_stalls: measured
  native_prediction_fps_and_delivered_fps: separate
  end_to_end_wall_time_and_memory_growth: measured
quality:
  prompts_seeds_and_evaluator_revision: fixed_protocol
  visual_motion_identity_and_boundary_quality: by_horizon
  action_response_contact_and_transition_error: task_conditioned
  uncertainty_and_diversity: multi_rollout
  planning_or_control: fixed_deadline_candidate_budget_and_task_protocol
```

Implementation checks that resolve different risks are: perturb forbidden future inputs to test causal isolation; compare cached and recomputed eligible history to test cache semantics; test prompt/observation replacement to expose stale state; and run across window eviction and codec boundaries to measure drift. These checks are evidence patterns, not new AIBuildAI permissions or mandatory workflow stages.

## Cosmos3-Nano and world-model transfer

### What the pinned implementation establishes

Cosmos3-Nano's Reasoner uses autoregressive language modeling; Generator predicts continuous media/action outputs through rectified flow. Those objectives do not decide whether Generator video blocks may be generated autoregressively over time. The distinction is between temporal factorization and the within-block sampler. [Cosmos architecture](../../models/cosmos3-nano/architecture.md) owns the AR/DM visibility and modality contracts.

The pinned Framework contains concrete causal-related surfaces:

| Source-level evidence | Scope of the evidence |
|---|---|
| video_temporal_causal and causal_training_strategy in OmniMoTModel | configurable temporal-causal behavior; diffusion_forcing samples per-latent-frame noise rather than one scalar per clip |
| pack_supertokens_temporal_causal | interleaved action/vision packing, conditioning masks, and aligned positions for whole clips versus AR chunks |
| generate_transfer_sample and TransferDataOverrides | overlapping autoregressive continuation for the Transfer path; not a generic assertion about base Nano T2V or DROID |
| request-local text K/V in the Generator | reuse of semantic context is not itself a persistent video-history cache |

[C3-FW, cosmos_framework/model/generator/omni_mot_model.py; cosmos_framework/data/generator/sequence_packing/temporal_causal.py; cosmos_framework/inference/transfer.py; C3-FW-ARGS, TransferDataOverrides]

These symbols establish implementation hooks, not checkpoint compatibility, a ready-to-use streaming service, or a measured robot latency. The resolved checkpoint/configuration, training history, sampler, codec, and return interface still determine which path actually runs. Existing [reproduction](../../models/cosmos3-nano/reproduction.md) records remain authoritative for execution state.

### Transfer hypotheses

| Candidate | Concrete change surface | Required evidence and falsification |
|---|---|---|
| Reduce waiting for near-future predictions | compatible temporal-causal Generator, chunk sampler, incremental decoder | earlier usable predictions at matched transition quality; fails if codec or evaluation still waits for the full horizon |
| Improve repeated continuation | generated-prefix adaptation with the intended history window | lower open-loop drift without losing short-horizon fidelity or action response |
| Reuse a stable observed prefix across candidate actions | branch-specific visual/semantic cache and action-conditioned suffix | cached/recomputed agreement; prefix sharing fails where its representations already depend on candidate actions |
| Correct a rollout after receiving new observations | condition ingestion, temporal positions, and invalidation of affected history | rapid recovery from prediction error without leaking future observations |
| Preserve action timing across chunks | action/vision supertoken ordering and physical timestamps | action effects occur at the correct transition, including boundaries and delayed consequences |

Changing DM visibility must preserve the intended Reasoner/Generator information boundary unless the experiment explicitly changes the architecture. Streaming a textual Reasoner response is not streaming a generated world trajectory. A DROID action chunk is also not evidence of causal video serving.

For robotics, useful evidence combines deadline-aware prediction, physical transition accuracy, action counterfactuals, and downstream decision quality. [iVideoGPT](../../papers/ivideogpt/README.md) supplies a separate action-conditioned AR world-model case; [X-WAM](../../models/x-wam/README.md) owns its asynchronous world/action interface. Neither transfers its checkpoint capabilities or results to Nano.

## Open questions

Which horizon and chunk size improve decisions under a fixed deadline rather than merely increasing display FPS? What memory retains contact state and object identity after long occlusions? How can generated-prefix training accommodate frequent observation corrections? Which caches remain shareable across branching action hypotheses? Where does incremental decoding become the latency bottleneck? How should uncertainty and forecast revisions be represented to a downstream consumer?

## Sources

Primary papers: [FVI-VIDEOGPT-PAPER], [FVI-STREAMINGT2V-PAPER], [FVI-DF-PAPER], [FVI-CAUSVID-PAPER], [FVI-SKYREELS2-PAPER], and [FVI-SELF-FORCING-PAPER]. Corresponding implementation identities: [FVI-VIDEOGPT-CODE], [FVI-STREAMINGT2V-CODE], [FVI-DF-CODE], [FVI-CAUSVID-CODE], [FVI-SKYREELS2-CODE], and [FVI-SELF-FORCING-CODE]. Cosmos code facts reuse [C3-FW] and [C3-FW-ARGS] from the Model registry.
