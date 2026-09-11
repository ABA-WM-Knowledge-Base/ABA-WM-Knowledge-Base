---
id: world-model-kb.components.fast-video-inference.quantization
title: Video Diffusion Quantization
kind: component
status: maintained
last_updated: 2026-09-11
owners:
  - AIBuildAI world-model group
---

# Video Diffusion Quantization

## Retrieval metadata

**Relevant queries:** video DiT quantization, PTQ, QAT, W8A8, W4A8, W4A6, W3A6, INT8, INT4, FP8, NVFP4, calibration data, activation outliers, mixed precision, temporal quantization error, ViDiT-Q, Q-VDiT, S2Q-VDiT, QuantSparse, 6Bit-Diffusion, packed weights, low-bit kernels.

**Knowledge provided:** How reduced numerical precision changes video generation cost and errors; five method families addressing distribution variation, temporal reconstruction, calibration selection, sparse attention, and cached residuals; implementation evidence and controlled transfer to world models.

**Related pages:** [Fast Video Inference](README.md) owns the acceleration map; [Few-Step Distillation](few-step-distillation.md) owns learned sampling-step reduction; [Caching](caching.md) owns reuse and refresh; [Efficient Attention](efficient-attention.md) owns interaction sparsity and kernel cost; [Causal and Streaming Generation](causal-streaming.md) owns historical K/V and incremental output; [Cosmos3-Nano Generator](../../models/cosmos3-nano/generator.md) owns the target architecture; [Inference](../../models/cosmos3-nano/inference.md) owns runtime and precision boundaries. [Parallel and Distributed Inference](parallel-distributed-inference.md) owns partition choices, communication, scaling, and topology-dependent trade-offs.

## 1. What quantization changes

Quantization changes numerical representation, not necessarily network size, sampling steps, or the attention pattern. For an integer quantizer, a useful abstraction is

$$
q=\mathrm{clip}(\mathrm{round}(x/s)+z,q_{\min},q_{\max}),
\qquad \hat{x}=s(q-z),
$$

where `s` is a scale and `z` a zero point. Scale granularity, clipping, rounding, and the tensors sharing a scale determine the approximation. This formula describes integer quantization; floating-point formats have different representable values.

| Decision | Meaning and consequence |
|---|---|
| Quantized object | Weight-only compression differs from quantizing linear-layer activations, attention Q/K/V, stored history, residual caches, or the VAE. Reducing one object's precision does not reduce every memory allocation. |
| Bit-width notation | W8A8, W4A8, W4A6, and W3A6 describe nominal weight/activation precision for selected operators. Exceptions, scales, accumulators, and stored versus executed precision remain separate fields. |
| Numerical format | INT4 and FP4 are not interchangeable. FP8 also needs an exact format, such as E4M3 or E5M2. NVFP4 uses E2M1 values, block scaling, and an additional tensor scale; its native hardware path is associated with Blackwell. |
| Adaptation | PTQ calibrates an existing model and may optimize scales, rounding, or small corrections with gradients. QAT updates model parameters while modeling quantization during training; the label alone establishes neither quality nor deployment speed. |
| Adaptivity | Static scales, online scales, fixed mixed-bit assignments, and runtime precision routing are different axes. Dynamic activation scaling does not imply dynamically changing the bit width. |

[Numerical-format reference: FVI-NVIDIA-NVFP4-DOC, format and two-level scaling description. Concrete calibration implementations: FVI-VIDITQ-CODE, `quant_utils/qdiff`; FVI-QVDIT-CODE, `qdiff/optimization/block_recon.py`.]

A nominal `P × b / 8` bytes for `P` weights at `b` bits excludes scaling metadata, alignment, high-precision exceptions, adapters, temporary conversions, and runtime state. Packed checkpoint bytes, resident model memory, peak inference memory, and latency therefore answer different questions. A fake-quantized floating-point computation can estimate numerical damage without saving either storage or execution time.

## 2. Why video calibration is difficult

Video denoising revisits a network with changing noise levels and conditioning. Rare activation magnitudes can dominate a scale; shrinking the range can instead clip important features. More frames or finer latent patches enlarge the token population and calibration footprint. Token count depends on the codec and patching contract, not simply the number of raw pixels.

The relevant error is not only layer reconstruction error. Small feature changes can alter attention allocation, conditional alignment, motion, or identity across a generated sequence. Evaluation on nearly static clips may conceal this damage. Calibration coverage is consequently a distributional assumption: prompts, image/action conditions, noise levels, guidance branches, frame counts, and resolutions define where the approximation has evidence.

**Cross-paper synthesis:** The five works below address different error sources rather than a universal sequence of replacements. Online scaling and mixed precision already appear in ViDiT-Q; later methods add particular correction, calibration, or composition mechanisms. Improvements on another backbone do not establish the same sensitivity ordering in a unified world model.

## 3. Method evolution: from local error to coupled execution

### 3.1 ViDiT-Q: distribution-aware linear quantization

ViDiT-Q combines per-channel weight and per-token activation quantization with online activation scales. Channel balancing and Hadamard rotation reduce outlier concentration; mixed precision protects layer types and denoising stages whose errors affect different quality dimensions. Thus it is not a purely static, uniform-bit baseline.

The important engineering distinction is between making quantization accurate and making its transformations cheap. An invertible change of basis can preserve an unquantized linear map, but finite-precision rounding and runtime transforms still matter. Lower weight precision need not provide the fastest implementation: the paper's A100 hardware study reports greater memory savings but less acceleration for mixed W4A8 than W8A8. The reported stage/type allocation is architecture- and metric-dependent, not a universal list of layers to protect. [FVI-VIDITQ-PAPER, ``4.1–4.3, 5.3, Figure 7.]

### 3.2 Q-VDiT: compensate errors while preserving temporal relations

Q-VDiT's Temporal Quantization Error correction combines a low-rank correction with temporal-token scaling. Temporal Maintenance Distillation adds alignment of inter-frame correlation distributions to output reconstruction. The rationale is that a small average feature error can still damage relationships between frames.

This is calibration-time correction, not distillation into fewer denoising steps. Its abbreviation TMD is distinct from Transition Matching Distillation in the [step-reduction synthesis](few-step-distillation.md). The paper evaluates OpenSora and Latte at aggressive precisions including W3A6; better results than quantization baselines do not mean equivalence to full precision. On OpenSora, W3A6 scene consistency remains 23.40 versus 39.61 for full precision under the paper's VBench protocol. Auxiliary corrections also create a deployment question: a correction that is cheap mathematically needs a fused or otherwise efficient executed path. [FVI-QVDIT-PAPER, ``3.2–3.3, 4.1, Table 1, Appendix F.]

### 3.3 S²Q-VDiT: improve which calibration evidence receives attention

S²Q-VDiT addresses limited calibration data through two selections. Sample salience combines denoising change with quantization sensitivity, favoring states informative on both axes. Sparse Token Distillation weights reconstruction by attention-derived token importance instead of treating every token equally.

Here “sparse” describes the calibration supervision; it does not establish a sparse-attention inference kernel. The resulting method retains per-channel weights, dynamic per-token activations, scaling, and rotation while changing calibration emphasis. Its experiments cover CogVideoX and HunyuanVideo at W4A6/W4A4. Better scores than other quantizers still leave regressions relative to full precision: for CogVideoX-5B W4A6, dynamic degree is 58.33 versus 72.22 in Table 1. Salience learned from a small candidate pool cannot establish coverage of conditions absent from that pool. [FVI-S2QVDIT-PAPER, ``3.2–3.3, 4.1, Tables 1 and 5.]

### 3.4 QuantSparse: calibrate quantization and sparsity together

QuantSparse treats sparse attention and quantization as coupled perturbations. Multi-Scale Salient Attention Distillation aligns pooled global attention and selected high-resolution attention during calibration, avoiding full-resolution supervision everywhere. At inference, SVD-based second-order residual correction and periodic dense refresh address drift in the difference between dense and quantized sparse outputs.

The mechanism depends on residual stability across denoising steps; it is not a guarantee for arbitrary sparsity, schedules, or conditions. Calibration supervision and runtime correction solve different parts of the error. The paper tests Wan2.1 and HunyuanVideo with 50 sampling steps; its density/refresh ablations expose a quality–speed trade-off rather than a free combination. Attention density is a fraction of retained interactions, not an equal fraction of total pipeline work. [FVI-QUANTSPARSE-PAPER, ``3.2–3.4, 4.1, Tables 4–5.]

### 3.5 6Bit-Diffusion: route precision jointly with cache refresh

6Bit-Diffusion predicts layer quantization sensitivity from the preceding step's block input/output change. It stores weights in NVFP4 and routes activations between NVFP4 and INT8, casting weights for the INT8 path. Temporal Delta Cache reuses block residuals; Purified Delta Refresh protects cache writes through outlier-aware higher precision and an INT8 fallback after skipped computation leaves the routing statistic unavailable.

“6Bit” is not a native six-bit dtype: Table 2's average activation accounting includes skipped blocks as zero-bit work. That accounting is not resident memory. The reported custom kernels are also material to acceleration. The paper's CogVideoX experiments use an RTX 5090, 50 DDIM steps, and CFG 6; its full system combines quantization and caching, so the full speedup cannot be attributed to precision reduction alone. [FVI-6BIT-PAPER, ``4.1–4.3, 5.1–5.3, Table 2.]

## 4. Reading the efficiency evidence

The following are within-paper observations, not a cross-paper leaderboard. Different models, output shapes, baselines, and hardware prevent ranking the methods by these ratios. Shape details and repeat counts not transcribed here remain in the cited protocol, not implied matched controls.

| Evidence | Reported measurement | Decision supported |
|---|---|---|
| ViDiT-Q, A100, batch 1, 20-step hardware profile | W8A8: 1.71× speed, 1.99× peak-memory reduction; mixed W4A8: 1.38×, 2.42× | More compression can be slower. [FVI-VIDITQ-PAPER, `5.3, Figure 7] |
| S²Q-VDiT, CogVideoX-5B W4A6, A800, batch 1 | Storage 10.375 → 2.633 GB; inference memory 15.801 → 10.145 GB; latency 259.2 → 203.2 s | Storage, live memory, and time are separate gains. [FVI-S2QVDIT-PAPER, `4.5, Table 5] |
| QuantSparse, Wan2.1-14B, A800 80 GB, CUDA 12.4, 15% attention density | 3.80× storage compression; 1.51× memory saving; 1.74× end-to-end acceleration | Coupled optimizations need component ablations. [FVI-QUANTSPARSE-PAPER, `4.4, Table 4] |
| 6Bit-Diffusion, CogVideoX comparison, RTX 5090 | 1.36× precision routing alone versus 1.92× full system | Cache savings are not quantization-only savings. [FVI-6BIT-PAPER, Table 2] |

## 5. Released implementation versus proposed mechanism

Release observations below bind to the commits in [sources.yaml](sources.yaml), accessed 2026-09-10. They do not imply local execution.

| Work | Verified release surface | Implementation consequence |
|---|---|---|
| ViDiT-Q | README separates simulation from the CUDA-extension pipeline for OpenSora1.2/PixArt-Sigma. `ViDiTQuantizedLinear.forward` applies scales/rotation and then floating-point `F.linear` to dequantized tensors. | Running the simulation path is not evidence of native low-bit acceleration. Hardware configuration and extension dispatch are separate. [FVI-VIDITQ-CODE, README, `quant_utils/qdiff/viditq/viditq_quant_layer.py`, `kernels/README.md`] |
| Q-VDiT | README currently scopes support to OpenSora v1.0. `QuantLayer` contains rank-32 and rank-1 correction branches; temporal layers apply a learned token mask. Reconstruction selectively enables correction/quantizer parameters. | The inspected forward path dequantizes and calls floating-point linear operations; paper-level low-bit speed is not demonstrated by this path. The released parameterization is richer than a rank-1-only summary. [FVI-QVDIT-CODE, README, `qdiff/models/quant_layer.py`, `qdiff/models/stdit_quant_layer.py`, `qdiff/optimization/block_recon.py`] |
| S²Q-VDiT | Pinned repository contains README/assets and announces forthcoming code. | Paper evidence, not an available calibration or inference implementation. [FVI-S2QVDIT-CODE, README, repository tree] |
| QuantSparse | Pinned repository likewise contains README/assets with code announced but not released. | Runtime residual correction and kernels cannot be reproduced from that snapshot alone. [FVI-QUANTSPARSE-CODE, README, repository tree] |
| 6Bit-Diffusion | No official implementation link identified in the inspected paper and title-based official-code search. | Custom-kernel performance remains paper-reported; code availability is unresolved, not asserted nonexistent. [FVI-6BIT-PAPER, `5.3] |

Both released ViDiT-Q and Q-VDiT examples support precomputed text embeddings. Removing a text encoder from GPU residency changes the baseline independently of quantization; matching that choice is essential when interpreting memory or timing. [FVI-VIDITQ-CODE, README; FVI-QVDIT-CODE, README.]

## 6. Diagnosis and controlled comparisons

**Optimization synthesis:** A useful comparison isolates the representation change before attributing benefits to sparsity, caching, or fewer steps. This is experimental reasoning, not a prescribed Agent execution order.

| Observation | Plausible explanation | Discriminating comparison |
|---|---|---|
| Smaller checkpoint, little peak-memory reduction | Activations, VAE, conditions, caches, or temporary unpacking dominate | Separate resident weights, peak allocated/reserved memory, and each pipeline phase. |
| Numerically acceptable output, slower inference | Fake quantization, unsupported matrix shapes, conversion/rotation overhead, or fallback kernels | Match shapes and inspect executed operators; compare complete requests as well as GEMMs. |
| Prompt alignment fails before appearance | A conditioning-sensitive projection is poorly calibrated | Restore that projection's precision with sampler and calibration pool fixed; test held-out conditions. |
| Flicker or subject drift increases | Temporal relations suffer despite small local error | Compare reconstruction-only versus temporal-aware correction; inspect motion and identity jointly. |
| Stable static clips but weak action response | Calibration or quality metrics underrepresent motion/control | Evaluate matched action changes and moving-object cases, not only temporal smoothness. |
| Quantization and caching each work, combination fails | Reused residuals carry persistent quantization error | Compare quantization-only, cache-only, combined, and protected-refresh variants at matched settings. |
| Low-bit and sparse attention interact badly | Perturbed attention scores change retained interactions and residuals | Compare dense quantized, sparse high-precision, naive combined, and jointly calibrated paths. |

A quantization result is interpretable with the following compact record. Acceptance tolerances are task-specific experiment choices, not fixed by this KB.

| Record | Necessary interpretation |
|---|---|
| Identity and numerical contract | Model/checkpoint/code revisions; changed modules; stored and executed W/A formats; scale granularity; accumulators; high-precision exceptions; correction parameters; packed versus simulated execution. |
| Calibration | Data identity and held-out split; prompts/conditions; noise levels and sampler; sample/token selection; CFG branches; optimization objective, updated parameters, steps, memory, and time. |
| Matched generation | Inputs, seeds, output shape, frame count, batch size, scheduler/NFE, guidance, text encoding, codec, attention backend, caching, offload, and compilation. |
| Systems measurement | GPU/software versions; cold versus warm calls; synchronization and repeat count; dispersion; kernel, denoiser, and end-to-end latency; checkpoint bytes and peak memory. Dynamic routing additionally needs format/skip/fallback frequencies. |
| Quality and utility | Baseline deltas with uncertainty; appearance, alignment, identity, motion, diversity, and task-specific control/physical outcomes. A better aesthetic score cannot establish preserved world dynamics. |

## 7. Cosmos and world-model transfer

The [Cosmos3-Nano Generator](../../models/cosmos3-nano/generator.md) combines diffusion-side computation with AR semantic context and modality-specific interfaces. The paper backbones above do not establish a drop-in Nano implementation. The [inference precision boundary](../../models/cosmos3-nano/inference.md) remains BF16 as the tested checkpoint precision; neither a hosted Reasoner response nor a generic low-bit library validates quantized Generator behavior.

**Optimization hypotheses:** Diffusion-side linear projections are candidate weight/activation surfaces when their measured share of memory or time warrants intervention. Separate precision for semantic-context paths, modulation, output heads, and attention is an ablation choice, not an assumed sensitivity ranking. Calibration for image-conditioned or action-conditioned rollout needs those actual conditions; text-only calibration does not demonstrate preservation of contact, action response, or continuous outputs.

A task-relevant benefit would be lower latency or memory within a declared quality tolerance at the same rollout contract. The hypothesis fails if conversion overhead removes the gain, if altered precision changes control-relevant behavior beyond that tolerance, or if gains depend on unmatched offloading, shapes, or sampling steps. For combinations, quantized residual refresh belongs with [caching](caching.md), quantized attention scores with [efficient attention](efficient-attention.md), and stored K/V precision with the history-validity contract in [causal/streaming generation](causal-streaming.md).

## Sources

Source identities and immutable code revisions resolve through [sources.yaml](sources.yaml). Paper results, inspected code behavior, and the transfer hypotheses above remain distinct evidence classes.
