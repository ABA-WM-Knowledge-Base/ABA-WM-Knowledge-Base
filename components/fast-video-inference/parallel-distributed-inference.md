---
id: world-model-kb.components.fast-video-inference.parallel-distributed-inference
title: Parallel and Distributed Video Inference
kind: component
status: maintained
last_updated: 2026-09-11
owners:
  - AIBuildAI world-model group
---

# Parallel and Distributed Video Inference

## Retrieval metadata

**Relevant queries:** multi-GPU video generation, distributed DiT inference, data parallelism, tensor parallelism, sequence parallelism, context parallelism, Ulysses, Ring Attention, USP, pipeline parallelism, displaced patch parallelism, PipeFusion, CFG parallelism, xDiT, HunyuanVideo, NVLink, PCIe, inter-node communication, parallel efficiency, FSDP inference.

**Knowledge provided:** What to partition across devices, which tensors remain replicated, how communication and stale features affect correctness, and how model size, token length, topology, and workload determine useful parallel configurations. Includes source-backed implementation surfaces and Cosmos-specific boundaries.

**Related pages:** [Fast Video Inference](README.md) owns the acceleration map; [Few-Step Distillation](few-step-distillation.md) owns sampling-work reduction; [Caching](caching.md) owns reuse and refresh; [Efficient Attention](efficient-attention.md) owns cheaper token interactions; [Causal and Streaming Generation](causal-streaming.md) owns incremental output and history validity; [Quantization](quantization.md) owns numerical representation; [Cosmos3-Nano Inference](../../models/cosmos3-nano/inference.md) owns the concrete runtime.

## 1. The optimization target and cost model

Distributed inference can make a model fit, reduce one sample's latency, or increase completed samples per second. These objectives can favor different allocations of the same GPUs. Replicating a complete model across independent requests improves aggregate capacity but does not divide the computation of one video. Sharding a model can enable a previously impossible request while still adding latency.

For a matched request, a useful accounting model is

$$
T_P=T_{\mathrm{fixed}}+T_{\mathrm{compute},P}
+T_{\mathrm{comm,exposed},P}+T_{\mathrm{idle},P}.
$$

Here `P` is the participating GPU count. Exposed communication is the portion on the execution critical path after overlap; idle time includes pipeline bubbles and imbalance. These terms form a non-overlapping accounting convention, not a sum of every kernel and communication duration in a trace. Communication can contend with computation even when their timelines overlap.

If the same workload fits on one GPU, define speedup `S_P = T_1/T_P` and parallel efficiency `E_P = S_P/P`. GPU-seconds per request, `P T_P`, expose the resource cost of lower latency. If the single-GPU baseline is OOM, its speedup is undefined; report capacity and scaling from the smallest feasible configuration. Fixed-workload scaling differs from increasing resolution, frames, or batch size along with GPU count.

**Systems synthesis:** Parallelism redistributes work and storage while adding coordination. Its benefit depends on how much execution remains local, how much communication is exposed, and whether the requested quality and output contract are preserved.

## 2. Partition choices and communication

The sequence length is the number of latent patches plus conditioning tokens actually entering the Transformer. Codec compression, temporal patching, packing, and resolution determine it. Dense attention has quadratic interaction count in that length; neither raw pixel count nor the word “video” specifies the distributed workload.

| Strategy | Partition and memory ownership | Communication and useful operating condition |
|---|---|---|
| Data parallel inference | Independent requests or samples; model replicated per serving group | Little model-internal communication between groups. Useful for many requests; queueing latency may improve without accelerating an isolated request. |
| Tensor parallelism | Matrix dimensions and attention heads; portions of weights distributed | Per-layer collectives combine partial results. Useful for parameter capacity or large matrix operations when interconnect cost is acceptable. |
| Sequence/context parallelism | Token states partitioned; weights usually replicated unless separately sharded | Attention exchanges remote K/V or redistributes tokens and heads. Useful when long sequences dominate activations and compute. |
| Conventional pipeline parallelism | Consecutive model stages on different devices; stage weights distributed | Stage-boundary transfers; a single microbatch leaves stages idle. Multiple requests or patches can fill the pipeline if dependencies permit. |
| CFG parallelism | Conditional and unconditional evaluations of the same latent on separate groups | Combine predictions each denoising step. Two-way CFG commonly provides degree two; embedded/distilled guidance need not perform two forwards. |
| Hybrid parallelism | Multiple process-group dimensions | Groups must satisfy layout, shape, and model-adapter constraints. A valid degree product alone does not establish implementation support. |
| Weight sharding, such as FSDP inference | Weights stored in shards and materialized for computation | Weight gathering reduces persistent residency but introduces transfers and transient buffers. This differs from splitting every matrix operation with tensor parallelism. |

[Mechanism context: FVI-USP-PAPER, ``2–4; FVI-XDIT-PAPER, `4; concrete FSDP inference: C3-FW-INFERENCE, Parallelism Arguments, in the [Cosmos source registry](../../models/cosmos3-nano/sources.yaml).]

“Sequence parallelism” is overloaded: Ring/Ulysses attention distribution and the activation-saving sequence partition associated with Megatron tensor parallelism have different communication and ownership. Likewise, distributed attention can retain the full mathematical attention operation, whereas stale-feature execution intentionally approximates it. Floating-point reduction order can still change results in an otherwise exact partition.

## 3. Method development and its evidence

### 3.1 DistriFusion: overlap communication across denoising steps

Synchronous patch splitting waits for remote features; independent patches lose global interaction. DistriFusion replaces that wait with current local activations and remote activations from the preceding denoising step. Asynchronous AllGather prepares the next step's context while computation proceeds. Initial synchronous execution supplies the first valid state; corrected asynchronous GroupNorm addresses spatial statistics in its U-Net setting.

The original evidence is high-resolution image diffusion, primarily SDXL, rather than video DiT deployment. Full model replication and stored remote activations remain memory costs. Quality depends on the approximation across steps, so fewer steps, changed conditions, or a new backbone require renewed comparison. [FVI-DISTRIFUSION-PAPER, `4, ``5.1–5.3.]

The pinned `DistriSelfAttentionPP._forward` selects synchronous gathering during warmup, then replaces the local slice in buffered K/V and enqueues communication. Its warmup counter is distinct from benchmark warmup runs. This distinction matters when reproducing both latency and numerical behavior. [FVI-DISTRIFUSION-CODE, `distrifuser/modules/pp/attn.py`.]

### 3.2 USP: combine token-to-head exchange with a ring

Ulysses uses All-to-All to turn sequence-sharded Q/K/V into head-sharded attention inputs; a reverse exchange restores the output layout. Ring Attention keeps local queries and circulates K/V blocks, combining their softmax contributions. This can overlap transfers with attention, but smaller blocks can reduce kernel efficiency.

USP arranges orthogonal Ulysses and ring groups, with `P_SP = P_U × P_R`. The Ulysses dimension remains constrained by compatible head counts; the ring dimension permits additional sequence partitioning. GQA/MQA, head replication, and tensor parallelism change those constraints. Positional information and causal masks must follow any token reordering.

The report compares attention and language-model training workloads. Its training MFU is not a video inference speedup. In its forward attention benchmarks, the preferred split differs between PCIe L20 and NVLink A100 systems, supporting topology-dependent selection rather than a universal ratio. [FVI-USP-PAPER, ``2–3, `5.1, Tables 3–4.]

The released `LongContextAttention.forward` performs All-to-All, the selected ring attention, then the inverse exchange. Backend and layout selection are part of the implementation contract. [FVI-USP-CODE, `yunchang/hybrid/attn_layer.py`.]

### 3.3 PipeFusion: pipeline patches through sharded layers

PipeFusion partitions both latent patches and model stages. Each GPU owns a consecutive layer group and processes different patches over successive microsteps. Previous-step context allows a stage to proceed before every current patch arrives, while fresh context accumulates. Communication moves stage-boundary activations rather than exchanging every layer's full K/V across all devices.

This also shards parameters, but each stage retains context for its own layers. Patch count and stage count are separate variables. Small patches reduce kernel efficiency; unbalanced stages and synchronous warmup reduce utilization. The long denoising horizon used to amortize startup may disappear after few-step distillation.

The paper evaluates image DiTs including PixArt, SD3, and Flux on PCIe-connected L40 GPUs. Its performance section excludes VAE decoding and searches patch counts; it does not establish arbitrary video-model support or an end-to-end world-model speedup. [FVI-PIPEFUSION-PAPER, `4, `5, Appendix B.]

PipeFusion's stale context is an inference approximation. Its numerical agreement needs evaluation independently of the benefits of merely distributing weights.

### 3.4 xDiT: compose methods with compatible state

xDiT combines sequence, patch-pipeline, CFG, and data parallelism. A substantive integration problem is keeping PipeFusion's K/V buffers consistent when sequence parallelism updates only local shards. The paper captures intermediate K/V from sequence-parallel communication so participating ranks update the appropriate shared context.

Its experiments span image DiTs on PCIe/Ethernet and NVLink systems; the preferred combination changes with workload and topology. Skip connections can add non-adjacent stage transfers, and conditioning tokens can unbalance patches. A separate parallel VAE addresses a different pipeline phase. [FVI-XDIT-PAPER, ``4.1–4.3, ``5.1–5.4.]

For the pinned implementation, `ParallelConfig.__post_init__` checks `DP × CFG × SP × TP × PP = dit_parallel_size`. Separate VAE resources need their own accounting. The familiar `2 SP × 2 PP × 2 CFG = 8` example is a valid factorization, contingent on the selected model supporting those paths. [FVI-XDIT-CODE, `xfuser/config/config.py`.]

The available framework methods are broader than any one adapter's support. Legacy APIs and current wrappers also differ; a framework feature list cannot prove that every video model supports PipeFusion, tensor parallelism, and their combinations.

### 3.5 HunyuanVideo: a concrete video integration

The pinned HunyuanVideo implementation divides latent height or width when patch-grid divisibility permits, shards rotary-position tensors consistently, installs distributed attention in both double- and single-stream blocks, and gathers output shards. This is a specific USP adapter, not a generic split along arbitrary video frames. [FVI-HUNYUAN-T2V-CODE, `hyvideo/inference.py: parallelize_transformer`.]

The T2V README supplies an eight-GPU example with 1280×720 output, 129 frames, 50 steps, and Ulysses/ring degrees 8/1. The I2V repository documents the same parallel family and a resize option for incompatible spatial grids. Its implementation tests whether `ALLOW_RESIZE_FOR_SP` exists; the intended documented enabling value is `1`. Resizing changes the workload and image conditioning, so the resolved shape belongs in a matched comparison. [FVI-HUNYUAN-T2V-CODE, README; FVI-HUNYUAN-I2V-CODE, README, `hyvideo/inference.py`.]

## 4. What the reported scaling establishes

| Source and workload | Reported observation | Evidence boundary |
|---|---|---|
| DistriFusion, SDXL, 3840×3840, 50-step DDIM, A100 GPUs | 1.8× / 3.4× / 6.1× at 2 / 4 / 8 GPUs | Image result. Repository benchmark instructions use latent output; preserve timing scope before calling this full image delivery. [FVI-DISTRIFUSION-CODE, README: Performance, Latency] |
| PipeFusion, image DiTs, 8×L40 PCIe Gen4 | Searches patch counts 2–32; averages five runs; one synchronous warmup step | DiT timing excludes VAE. The search procedure and warmup are part of the result. [FVI-PIPEFUSION-PAPER, `5] |
| HunyuanVideo official README, 1280×720, 129 frames, 50 steps | Scaling table below | The table does not specify GPU model, interconnect, repeat count, or precise timing boundary. These remain missing metadata. [FVI-HUNYUAN-T2V-CODE, README: Parallel Inference] |

| GPUs | Reported latency, seconds | Speedup from listed latency | Parallel efficiency |
|---|---:|---:|---:|
| 1 | 1904.08 | 1.00× | 100.0% |
| 2 | 934.09 | 2.04× | 101.9% |
| 4 | 514.08 | 3.70× | 92.6% |
| 8 | 337.58 | 5.64× | 70.5% |

The derived columns use the displayed times. Efficiency slightly above 100% can arise from execution changes or measurement variation; it does not prove a particular cause. The same timing values appear in the I2V README, so they are not independent replications of scaling. The eight-GPU result also consumes about 1.42× the single-GPU GPU-seconds per request. Without traces, the scaling gap cannot be apportioned among communication, imbalance, and fixed overhead.

## 5. Choosing a strategy from the bottleneck

**Cross-source synthesis:** The following mappings identify candidate interventions and evidence that would support them. They leave experiment choice and scheduling to the consuming Agent.

| Observed bottleneck | Candidate and rationale | Condition that changes the choice |
|---|---|---|
| Weights alone exceed device capacity | Tensor/stage/weight sharding distributes persistent parameters; PipeFusion additionally pipelines patches | Replicated sequence parallelism alone cannot solve parameter residency. Gather buffers, activations, and non-DiT modules may still OOM. |
| Long-token activations or attention dominate | USP distributes token work; vary Ulysses/ring split within compatible head and grid layouts | Short local sequences, communication, or head replication can remove the gain. |
| Many independent prompts or candidate rollouts | Replicated serving groups distribute samples | A single model may first require sharding; compare total throughput at the same GPU budget and latency target. |
| Two guidance forwards dominate | CFG groups compute branches concurrently | Embedded guidance or a distilled one-forward path offers no two-branch opportunity. |
| Weak inter-node links dominate | Keep frequent collectives within faster groups; consider stage boundaries or CFG across slower links | Actual message sizes, stage imbalance, topology, and model support can reverse the expected benefit. |
| Large weights and long video coexist | Hybrid weight/stage and sequence partitioning addresses different memory terms | Process groups may overlap or conflict; use the runtime's actual mesh semantics rather than blindly multiplying every exposed flag. |
| Denoiser improves but complete requests do not | Inspect text encoding, VAE decoding, transfers, and output assembly | Parallel image VAE code does not establish correct distributed temporal decoding for a video codec. |

A measured speed benefit can disappear after another optimization. Fewer denoising steps make synchronous startup a larger fraction; caching and sparse attention reduce computation available to hide communication; quantized weights do not automatically reduce activation-transfer bytes. Causal streaming introduces mask, cache, and first-output constraints that differ from full-clip throughput. These interactions motivate paired ablations rather than multiplying published speedup ratios.

## 6. Failure diagnosis and evaluation

| Symptom | Plausible cause | Discriminating evidence |
|---|---|---|
| More GPUs increase latency | Exposed collectives, small local kernels, topology crossings | Matched-shape operator/communication trace and alternate rank placement |
| Pipeline stages spend time idle | Startup, stage imbalance, too few patches, condition-heavy stages | Per-stage compute and wait time while varying patch count |
| OOM persists or moves to another stage | Replicated weights, full-context buffers, gathered outputs, VAE peak | Maximum per-rank memory by phase, including transient buffers |
| Seams, temporal drift, or alignment loss | Stale context, wrong token order, mismatched RoPE/masks | Synchronous distributed reference and controlled stale-context comparison |
| Hang at a collective | Divergent rank control flow, inconsistent shapes/groups, failed peer | First rank error and collective sequence; connectivity tests alone do not establish program correctness |
| Only certain frame counts or resolutions fail | Patch-grid divisibility or backend layout constraints | Resolved latent shape, head counts, padding, mask and positional metadata |
| Latency improves but interactive control worsens | Queueing, output assembly, stale conditioning, delayed first chunk | Condition timestamps, first usable output, and action-response measurement |

An interpretable experiment retains model and code revisions, checkpoint identity, input/seed set, actual resolution and frame count, codec, precision, sampler/NFE, guidance behavior, caching, attention backend, compilation, and offload state. Hardware records include GPU model/count/memory, nodes, rank-to-device mapping, NVLink/PCIe and inter-node fabric, software versions, and process-group degrees.

Performance reporting separates initialization/compilation from steady requests, algorithmic synchronous warmup from benchmark warmup, denoiser from full-pipeline latency, and throughput from one-sample latency. Repeats and dispersion accompany timing; per-rank memory, exposed communication, collective sizes, and compute overlap explain scaling. Idle ranks and dedicated VAE devices remain part of the resource budget.

For a numerically exact partition, paired output and metric checks expose layout or implementation errors without demanding bitwise equality. Stale-feature methods additionally need quality tolerances for appearance, alignment, temporal consistency, and task-relevant dynamics. When one configuration changes shape, steps, precision, or caching, it measures a combined intervention rather than parallelism alone.

## 7. Engineering entry points

These are inspected source surfaces, not locally executed multi-GPU reproductions. Immutable revisions resolve through [sources.yaml](sources.yaml).

| Implementation | Relevant entry point | Reproduction boundary |
|---|---|---|
| DistriFusion | `scripts/run_sdxl.py`; `distrifuser/modules/pp/attn.py` | SDXL patch execution and synchronous/asynchronous comparison; benchmark output type affects scope. |
| USP / YunChang | `yunchang/hybrid/attn_layer.py`; `test/test_hybrid_attn.py` | Attention primitive and layout tests, not an entire video pipeline. |
| PipeFusion / xDiT | `xfuser/config/config.py`; `xfuser/core/long_ctx_attention/hybrid/attn_layer.py`; model-specific examples | Cache-enabled ring support and sparse-backend combinations have explicit restrictions. |
| HunyuanVideo T2V | `sample_video.py`; `hyvideo/inference.py` | Official USP example; README specifies `xfuser==0.4.0`, distinct from the separately inspected xDiT HEAD. |
| HunyuanVideo I2V | `hyvideo/inference.py` and README parallel example | Conditioning/resizing and loading differ from T2V; retain its own checkpoint and dependency identities. |

One concrete reference command, run from the pinned HunyuanVideo checkout after its documented environment and checkpoint setup, is:

```bash
torchrun --nproc_per_node=8 sample_video.py \
  --video-size 1280 720 --video-length 129 --infer-steps 50 \
  --prompt "A cat walks on the grass, realistic style." \
  --flow-reverse --seed 42 --ulysses-degree 8 --ring-degree 1 \
  --save-path ./results
```

The command identifies an official deployment surface, not evidence of successful execution in this KB. A new reproduction records the resolved environment and checkpoint rather than substituting the newest dependency releases.

## 8. Cosmos and world-model transfer

Cosmos already exposes relevant parallel mechanisms. The canonical [runtime page](../../models/cosmos3-nano/inference.md#distributed-framework-configuration) owns its concrete configuration evidence. At the pinned Framework revision, the inference guide distinguishes FSDP weight sharding from latency-oriented context/CFG parallelism; the Omni argument builder suppresses tensor parallelism at size one. Context-parallel code explicitly handles modality-packed sequences and head redistribution. [C3-FW-INFERENCE; C3-FW-ARGS; C3-FW, `parallelize_unified_mot.py`, `context_parallel_utils.py`.]

**Optimization hypotheses:** For long Generator sequences, the existing context-parallel path offers a concrete baseline for varying device count and comparing compute against exposed communication. For parameter-bound requests, weight sharding offers a capacity baseline with separate transient-memory and latency costs. Neither establishes xDiT/PipeFusion compatibility or measured Nano speedup.

The [architecture](../../models/cosmos3-nano/architecture.md) uses modality-specific Transformer paths and asymmetric AR/DM visibility. MoT alone does not imply a top-k expert router or justify ordinary MoE expert dispatch. Any tower/stage partition requires evidence about cross-tower attention, residual connections, parameter placement, modality packing, and cached state. Reasoner and Generator may also use different runtimes, so their distributed configurations need separate ownership.

World-model evaluation adds action-response and physical-consistency constraints to video quality. Parallel generation of independent candidate futures can increase planning throughput, but interactive usefulness also depends on observation-to-output delay and whether those futures use current conditions.

Open transfer questions concern the best mesh for a particular Nano task and topology, preservation of packed-mask/cache semantics under a new backend, sensitivity to stale features after few-step adaptation, and the fraction of complete request time spent in the video decoder. These are experimentally answerable questions, not assumed support.

## Sources

Paper and official-code identities resolve through [sources.yaml](sources.yaml). Existing Cosmos identities remain in the [model registry](../../models/cosmos3-nano/sources.yaml). Reported measurements, inspected implementations, and proposed interventions retain separate provenance.
