---
id: world-model-kb.components.fast-video-inference.efficient-attention
title: Sparse, Local, and Linear Attention for Video Generation
kind: component
status: maintained
last_updated: 2026-09-11
owners:
  - AIBuildAI world-model group
---

# Sparse, Local, and Linear Attention for Video Generation

## Retrieval metadata

**Relevant queries:** efficient video attention, sparse attention, local attention, linear attention, hybrid attention, Video Swin, Sparse VideoGen, SVG2, Sliding Tile Attention, STA, Video Sparse Attention, VSA, SANA-Video, SANA-Video 2.0, attention density, top-k tiles, attention recall, long video, DiT latency, Cosmos attention.

**Knowledge provided:** Attention cost and information-flow trade-offs; local, dynamic sparse, and linear mechanisms; training and kernel requirements; controlled comparison criteria; failure diagnosis; and implementation-grounded transfer hypotheses for video world models.

**Related pages:** [Latent Diffusion and DiT](../generative-modeling/latent-diffusion-and-dit.md) owns codec and denoiser architecture; [Few-Step Distillation](few-step-distillation.md) owns learned sampling-step reduction; [Caching](caching.md) owns approximate reuse across denoising evaluations; [Cosmos3-Nano Architecture](../../models/cosmos3-nano/architecture.md) owns tower visibility, grouped-query attention, positions, and modality contracts. [Causal and Streaming Generation](causal-streaming.md) owns temporal factorization, history-state validity, incremental delivery, and interaction latency. [Video Diffusion Quantization](quantization.md) owns reduced numerical precision, calibration, real-kernel versus simulated execution, and interactions with reuse and attention. [Parallel and Distributed Inference](parallel-distributed-inference.md) owns partition choices, communication, scaling, and topology-dependent trade-offs.

## The bottleneck: interactions within a forward pass

Efficient attention reduces the cost of mixing tokens during a model evaluation. Sparse and local operators restrict query–key connections; linear operators change how information is aggregated. These interventions can affect both training and inference. Their update requirements range from replacing an inference kernel to training an altered backbone.

For a latent video of shape \((T_z,H_z,W_z)\) and transformer patch size \((p_t,p_h,p_w)\), the visual sequence length is

\[
N_v=
\left\lceil T_z/p_t\right\rceil
\left\lceil H_z/p_h\right\rceil
\left\lceil W_z/p_w\right\rceil,
\]

assuming padding to patch boundaries. Codec output shape comes first: raw frames and pixels are not the DiT token grid. Text, clean conditions, audio, actions, and padding can add tokens or create separate attention domains. Record \(N_q\) and \(N_k\) for the actual operator.

For one head, dense attention computes

\[
O=\operatorname{softmax}(QK^\top/\sqrt{d_k}+M)V.
\]

The score and value products cost \(O(N_qN_k(d_k+d_v))\); equal-length self-attention is quadratic in sequence length. QKV projections and FFNs have separate width-dependent costs. Doubling duration approximately doubles visual tokens and quadruples dense interaction work when the other dimensions stay fixed. Doubling both spatial dimensions approximately multiplies tokens by four and interaction work by sixteen.

A naive implementation stores a quadratic score matrix. FlashAttention instead tiles the computation and uses online softmax to avoid materializing that matrix in high-bandwidth memory. It preserves dense softmax semantics, up to floating-point effects, while reducing memory traffic; it does not remove the quadratic arithmetic. A sparse-mask comparison therefore needs a strong fused dense baseline. [FVI-FLASHATTN-PAPER, Secs. 2–3]

Attention becomes dominant at sufficiently long sequences, but the crossover depends on model width, codec, resolution, hardware, and kernels. If attention occupies fraction \(f\) of measured baseline latency and is accelerated by \(s\), the ideal overall speedup is

\[
S=\frac{1}{(1-f)+f/s}.
\]

Routing, permutation, padding, and synchronization increase the denominator. A large kernel gain can have little impact when FFNs, codecs, or communication dominate.

## What the different families preserve

Spatial proximity, continuity across frames, and concentrated attention weights motivate sparsity. They are empirical priors, not guarantees that background, distant frames, or low-weight tokens are dispensable. A small contact region can matter more to a downstream action than a large visually salient region.

| Family | Interaction rule | Main retained information | Main restriction | Typical update requirement |
|---|---|---|---|---|
| Exact fused dense | all permitted keys, tiled execution | original softmax interactions | quadratic arithmetic remains | none if backend semantics match |
| Local/window | a geometric neighborhood per query or tile | nearby spatial and temporal detail | distant information needs other layers or paths | native training, or calibrated retrofit with optional adaptation |
| Structured sparse | selected spatial, temporal, or other patterns | relationships represented by those patterns | pattern mismatch | training-free selection can be possible |
| Content-adaptive sparse | selected keys or blocks depend on activations | important nonlocal relationships | routing error and routing cost | either training-free routing or learned adaptation |
| Linear | aggregate keys and values into a fixed-width state | compressed global context | limited state capacity and changed operator | training or adaptation of the model |
| Hybrid | combine linear, sparse, local, or dense paths | complementary global and detailed interactions | mixed costs and coupling | architecture-dependent |

Local attention is a form of structured sparsity. Dynamic selection does not imply training: SVG and SVG2 select at runtime without updating model weights; VSA trains a coarse/fine combination. These are intersecting design axes, not a mandatory sequence in which one family supersedes another.

### Sparse attention changes support and normalization

For retained keys \(R_i\), a masked softmax operator computes

\[
\hat o_i=
\frac{\sum_{j\in R_i}\exp(s_{ij})v_j}
{\sum_{j\in R_i}\exp(s_{ij})},
\qquad s_{ij}=q_i^\top k_j/\sqrt{d_k}.
\]

All query outputs still exist. Sparsifying connections does not necessarily prune tokens from the residual stream or save their FFN computation. Applying a mask after a dense matrix multiplication also does not save that multiplication; a sparse kernel must skip excluded work.

Use **density** \(\rho=\text{retained valid pairs}/\text{baseline permitted pairs}\) and **removed fraction** \(1-\rho\). Papers and APIs sometimes call either quantity “sparsity.” Block counts only equal pair counts for equal-size, fully occupied blocks.

An algebraic diagnostic explains the limits of attention recall. If removed keys carry dense attention mass \(\delta_i\), then

\[
o_i-\hat o_i=\delta_i(\mu_{\mathrm{drop}}-\mu_{\mathrm{keep}}).
\]

Here the two means are value vectors normalized within the dropped and retained sets. For bounded values \(\|v_j\|\leq B\), the immediate error is at most \(2B\delta_i\). High retained mass can constrain one operator's error under that assumption. It does not bound amplification through later layers, denoising steps, or a discontinuous contact decision.

### Linear attention changes the operator

For a nonnegative feature map \(\phi:\mathbb{R}^{d_k}\rightarrow\mathbb{R}^{r}\), a normalized kernel-attention form is

\[
S=\sum_j\phi(k_j)v_j^\top,\quad
z=\sum_j\phi(k_j),\quad
o_i=\frac{\phi(q_i)^\top S}{\phi(q_i)^\top z+\epsilon}.
\]

Aggregation costs \(O(Nrd_v)\) with fixed head dimensions and feature-map cost. This reassociation is valid for the chosen kernel formulation; \(\operatorname{softmax}(QK^\top)V\) cannot generally be replaced by \(Q(K^\top V)\). Causal versions accumulate \(S\) and \(z\) over an eligible prefix. [FVI-LINEAR-TRANSFORMER-PAPER, Sec. 3]

The state contains a compressed history, not individually addressable copies of every past token. Constant state size does not imply perfect long-term recall. Normalization, feature maps, gates, positional transformations, and accumulation precision are part of the architecture.

If a fixed fraction \(\alpha>0\) of layers retains full attention, a hybrid stack still contains an \(O(\alpha N^2d)\) term. Likewise, fixed-density sparse attention remains quadratic, and a pooled coarse attention stage remains quadratic in its pooled sequence. Practical savings and asymptotic complexity are different claims.

## Method evolution and its evidence

### Video Swin: local computation with cross-window communication

Video Swin extends shifted windows into three dimensions. Consecutive transformer layers alternate regular and shifted partitions, allowing neighboring windows to exchange information. Hierarchical spatial merging reduces later-stage token counts. For fixed window volume \(W\), attention work scales as \(O(NWd)\). [FVI-VIDEO-SWIN-PAPER, Sec. 3, Figs. 1–3]

Its experiments concern video recognition on Kinetics and Something-Something, not diffusion generation. The transferable idea is locality plus communication across windows; recognition accuracy cannot establish denoising fidelity or physical rollout accuracy. Long-distance communication still depends on depth and partition geometry. The official WindowAttention3D, SwinTransformerBlock3D, and window_partition implementation exposes these choices. [FVI-VIDEO-SWIN-PAPER, Sec. 4; FVI-VIDEO-SWIN-CODE, mmaction/models/backbones/swin_transformer.py]

### Sparse VideoGen: select spatial or temporal patterns online

SVG observes different head behaviors: spatial patterns cover the same and neighboring frames, while temporal patterns connect spatially corresponding regions across frames. Text and first-frame tokens are retained in both patterns. A head's choice can change with prompt and denoising step. SVG samples query rows, compares candidate outputs against dense attention on those rows, and selects the lower-error pattern. Tensor permutation makes temporal accesses contiguous for block kernels. [FVI-SVG-PAPER, Secs. 3–4]

The finite candidate set limits adaptation: online selection can choose a better available pattern but cannot invent a missing motion-following connection. The paper's HunyuanVideo headline also includes an FP8 variant; Table 1 separates ordinary SVG from SVG plus quantization. Its full system includes normalization and rotary-position kernel optimizations, so its total speedup is not solely the effect of deleting attention edges. [FVI-SVG-PAPER, Table 1, Secs. 4.3 and 5.3]

### Sliding Tile Attention: align locality with GPU blocks

STA gives every query in a spatial–temporal tile the same neighborhood of key tiles. Tile-contiguous packing produces fully computed or fully skipped blocks, avoiding the partially masked blocks that make token-wise 3D sliding windows inefficient. “Sliding” describes the neighborhood changing with query-tile position; it does not describe moving windows between diffusion steps. [FVI-STA-PAPER, Secs. 2.2 and 3.1]

The training-free path profiles per-head windows and protects initial dense steps. A separate fine-tuning path uses stronger sparsity with attention-output, final-output, and flow-matching supervision. Both are paper methods; STA is not exclusively training-free. The experiments distinguish kernel timing from a generation timing region that excludes VAE and text-encoder work. [FVI-STA-PAPER, Secs. 3.2–4]

FastVideo retains STA kernels, but the pinned main-branch documentation directs full mask-search and inference integration to the sta_do_not_delete branch. The archive is pinned separately in the source registry. The maintainers' preference for VSA is a maintenance decision, not a controlled universal comparison. [FVI-FASTVIDEO-CODE, docs/attention/sta/index.md; FVI-STA-ARCHIVE-CODE]

### VSA: learn coarse global context and sparse fine interactions

VSA pools video cubes into coarse Q/K/V representations, computes global coarse attention, and selects top-\(k\) key cubes per query cube. A fine stage computes token-level attention within selected cubes. Gated coarse and fine outputs jointly form the result: the coarse stage carries global information as well as selecting blocks. [FVI-VSA-PAPER, Sec. 2.2]

Native training learns this operator directly. Dense-model adaptation starts with a zero coarse gate, an ungated fine path, and dense coverage, then increases sparsity during training. The paper's Sec. 2.3 prints \(k=B/L\) for initial dense coverage, although a sequence of \(L\) tokens with \(B\) tokens per block contains \(L/B\) blocks. The current compute_topk implementation returns all blocks at zero removed fraction, resolving the implementation choice. [FVI-VSA-PAPER, Sec. 2.3; FVI-FASTVIDEO-CODE, fastvideo/attention/backends/video_sparse_attn.py: compute_topk]

The fine-stage cost is approximately \(O(NkBd)\); coarse work is \(O((N/B)^2d)\), plus selection and memory traffic. Coarse FLOP fraction can be small while latency is material. Fine tiles trade localization accuracy against hardware utilization. [FVI-VSA-PAPER, Secs. 2.4 and 3.1]

### Sparse VideoGen2: group tokens by content before sparse execution

SVG2 changes how blocks are formed. It clusters queries and keys separately by activation similarity, permutes each cluster into contiguous storage, and moves values with their keys. Cluster-size-weighted centroid scores support top-\(p\) selection, while variable-size block kernels execute the selected interactions. Centroids from the preceding denoising step initialize clustering. [FVI-SVG2-PAPER, Sec. 4]

This addresses the case where geometric pooling mixes unrelated features or scatters important keys across mostly unimportant blocks. Permutation itself can preserve dense attention when positions, masks, and inverse ordering are handled consistently; selecting only some cluster pairs introduces approximation. Clustering and routing remain training-free but carry measurable overhead. A warm-started routing state also couples the implementation to the denoising schedule. [FVI-SVG2-PAPER, Secs. 4.1–4.3 and 5]

SVG and SVG2 share a repository but have different routing algorithms. Its Cosmos entrypoint defaults to nvidia/Cosmos-1.0-Diffusion-14B-Text2World; that integration is not a Cosmos3-Nano result. [FVI-SVG-CODE, cosmos_t2v_inference.py]

### SANA-Video: linear mixing with video-specific locality and state

The original SANA-Video adapts an image Linear DiT to video. Its ReLU-based attention applies 3D RoPE after the feature map in the numerator and uses unrotated nonnegative features in the denominator for stability. A temporal convolution in Mix-FFN restores local motion processing. Text conditioning remains a separate cross-attention path. [FVI-SANA-VIDEO-PAPER, Secs. 3.1–3.2; FVI-SANA-CODE, diffusion/model/nets/sana_multi_scale_video.py]

LongSANA adds block-causal generation, accumulated key/value summaries, and a previous-frame convolution cache. The prefix summary is updated after a block is denoised; training addresses causal operation and exposure bias. Its bounded history state is architecturally different from skipping a changing denoiser residual in TeaCache. [FVI-SANA-VIDEO-PAPER, Sec. 3.3, Algorithm 1]

Published system comparisons also change model size, codec, training, or sampling settings. They support efficient model design but do not isolate a drop-in attention replacement. The fixed-width history can lose detailed correspondence even while aggregating information from all past blocks.

### SANA-Video 2.0: periodically restore dense interactions

SANA-Video 2.0 uses gated bidirectional linear layers interleaved with dense softmax layers at a 3:1 ratio. Block Attention Residuals route representations across depth, carrying earlier dense-layer information into later layers. It trains the hybrid architecture from scratch and replaces the original temporal-convolution FFN with SwiGLU. This is a distinct follow-up to the original linear Video DiT. [FVI-SANA-VIDEO2-PAPER, Secs. 2–4]

The dense layers reduce the restrictions imposed by compressed linear states, but their quadratic term remains. The paper's matched backbone timings are stronger evidence for attention design than its separately optimized Sol-Engine pipeline, which combines several acceleration methods. [FVI-SANA-VIDEO2-PAPER, Secs. 5.4 and 6]

The pinned release exposes 5B reference configurations, training/inference code, and a 5B checkpoint; its 14B config/checkpoint release is still pending. There is also an equation-to-code distinction: paper Eq. 1 includes a ReLU normalization denominator, while the released GatedLinearAttention.forward omits that scalar before RMSNorm. These are distinct implementation records. [FVI-SANA-CODE, docs/sana_video2.md and diffusion/model/nets/sana_video2_blocks.py]

## Reading experimental results without mixing interventions

These selected records illustrate different evidence types. They are not a cross-paper ranking.

| Evidence | Declared setting and observation | Interpretation |
|---|---|---|
| SVG versus SVG + FP8 | HunyuanVideo T2V, paper-labeled 720p, 128 frames, H100-80GB; FA2 baseline 2,253 s, SVG 1,171 s, SVG + FP8 968 s | 1.92× and 2.33× are different precision/intervention settings. [FVI-SVG-PAPER, Table 1, Sec. 5.3] |
| STA kernel | BF16, 115.2K tokens, 24 heads, head dimension 128; 91% removed pairs; ThunderKittens dense 265.28 ms versus STA 25.38 ms | 10.45× is a kernel comparison. [FVI-STA-PAPER, Table 2] |
| STA generation | HunyuanVideo, 117 frames, 768×1280, H100; FA3 945 s versus training-free STA 501 s | 1.89× covers the paper's generation timing region, excluding VAE and text encoder. [FVI-STA-PAPER, Sec. 4] |
| VSA adaptation | Wan2.1-1.3B, 480p latent grid 16×28×52; compiled dense DiT 31 s versus VSA 18 s | The dense fine-tuning control matters: original, dense-fine-tuned, and VSA VBench totals are 82.56, 83.63, and 82.77. [FVI-VSA-PAPER, Sec. 3.3, Fig. 3] |
| Original SANA-Video system | T2V, BF16, batch 1, one H100, 480×832×81; SANA-Video 2B 60 s versus Wan2.1-1.3B 103 s | Models and default step counts differ; the ratio is not an isolated linear-attention gain. [FVI-SANA-VIDEO-PAPER, Table 4] |
| SANA-Video 2.0 backbone | Matched compiled DiT forward at the paper's 720p/60 s shape reports 3.2× over a full-softmax counterpart | A backbone comparison; separate from multi-method serving acceleration. [FVI-SANA-VIDEO2-PAPER, Sec. 5.4] |

An evidence row with omitted steps, batch, or timing boundaries is insufficient to reconstruct a run. The owning source supplies its full protocol; absent fields remain unknown. Aggregate VBench or paired PSNR does not establish equivalence on contact, action response, or long-term state.

## Design judgments for a new model

The following are cross-paper synthesis and optimization hypotheses. They identify useful controls without prescribing an Agent's task sequence.

| Observed bottleneck or task | Candidate and controllable variable | Expected benefit | Evidence that weakens the hypothesis |
|---|---|---|---|
| Short clips with stable local attention | profiled local tiles; window by head and layer | inexpensive routing with fewer interactions | remote correspondence or camera motion fails at useful density |
| Prompt-dependent spatial/temporal structure | online pattern selection; profile-row fraction and allowed patterns | adapt a frozen model to differing head behavior | the best candidate pattern still has high output error |
| Important keys scattered across geometric blocks | content-based clustering; cluster count and retained mass | concentrate useful computation | clustering/permutation costs exceed saved kernel time |
| Dense-to-sparse quality gap with adaptation data available | trainable coarse/fine attention; top-\(k\), gate initialization, tile size | recover quality while reducing training/inference cost | matched dense adaptation improves much more at similar compute |
| Long sequences dominated by pairwise mixing | linear or hybrid architecture; state width and dense-layer fraction | reduce interaction cost and retain global context | fine detail or retrieval degrades, or dense layers dominate scaling |
| Interactive rollout with bounded state | causal linear/local/hybrid design; history capacity and refresh mechanism | predictable memory and per-block latency | delayed action consequences or reappearing objects lose identity |

“Short clip” alone does not establish local sufficiency. Long video does not uniquely favor linear attention: coarse global paths, selected distant blocks, explicit memory, and dense layers offer alternative capacity–cost trade-offs. Interactive use additionally depends on first-output latency, block duration, observed-context availability, and causal correctness.

Training-free is a weight-update category, not a statement of zero calibration cost. Trainable sparsity needs a matching data and update-budget control. Architectural replacement also changes parameterization, so a pretrained softmax checkpoint cannot generally be loaded unchanged into a linear model.

## Failure diagnosis

| Symptom | Plausible mechanism | Controlled diagnostic |
|---|---|---|
| Object identity fails after occlusion | distant correspondence removed or compressed away | vary temporal reach or state capacity with identical occlusion cases |
| Fast motion fragments across tiles | geometric support no longer follows the object | widen temporal/spatial support independently; compare content routing |
| Small manipulated object disappears | coarse pooling or ranking misses a small region | region-level output error and contact/state probes |
| Prompt or action influence weakens | condition keys compete for a limited budget | preserve condition edges while sparsifying visual–visual edges |
| Seams or repeated spatial patterns | partition boundaries or positional ordering are wrong | dense execution after permutation, then inverse-permutation parity |
| Prediction appears to know future observations | causal or packed-sample mask was widened | perturb forbidden future/sample tokens and test output invariance |
| Linear path becomes unstable | normalization, positional transform, or accumulation precision | inspect denominator/state norms and compare stable-precision accumulation |
| Stronger sparsity destabilizes adaptation | checkpoint/operator mismatch or abrupt gate change | dense-start control and gradual support reduction |
| High pair sparsity gives little speedup | partial tiles, low occupancy, routing, or communication | split routing, layout, kernel, and collective timings |
| Combined caching and sparsity regress | cache proxy sees an altered attention/residual distribution | dense/no-cache, sparse-only, cache-only, and combined controls |

Increasing retained edges can diagnose missing information; it is not guaranteed to fix an incorrectly implemented mask or positional transform. A same-checkpoint dense-equivalence test with all eligible blocks retained can isolate layout and normalization errors before interpreting sparse quality.

## Evaluation contract

A comparable record identifies the attention operator, the model change around it, and the measured runtime region. The fields below describe evidence needed to interpret a result; thresholds and experiment scheduling belong to the consuming task.

```yaml
identity:
  checkpoint_and_code: exact_revisions
  task_and_condition: t2v_i2v_v2v_or_action_conditioned
  adaptation: none_or_data_objective_parameters_updates_and_compute
attention:
  baseline: operator_backend_and_version
  candidate: operator_backend_and_version
  scope: layers_heads_modalities_and_query_key_domains
  token_grid: latent_shape_patch_shape_padding_and_flattening
  lengths: valid_Nq_and_Nk
  geometry: windows_tiles_and_dilation_if_used
  routing: topk_topp_profile_or_clustering_configuration
  density: requested_and_achieved_valid_pair_density
  linear_or_hybrid: state_width_feature_map_gates_and_dense_fraction
  visibility: causal_packed_sample_and_condition_masks
generation:
  resolution_frames_fps: exact
  sampler_steps_guidance: exact
  prompts_conditions_and_seeds: matched_sets
runtime:
  accelerator_count_precision_batch_concurrency: exact
  compilation_warmup_and_synchronization: explicit
  attention_latency: routing_plus_layout_plus_kernel
  denoising_and_complete_pipeline_latency: separate
  first_output_and_throughput: separate_if_streaming
  peak_memory_and_persistent_state: measured
quality:
  attention_output_error_and_retained_mass: diagnostic
  paired_video_distance: same_seed_reference
  fvd_vbench_human_preference: evaluator_protocol_and_uncertainty
  temporal_identity_motion_and_condition: disaggregated
  diversity_and_horizon: multi_seed_and_length_strata
world_model:
  transition_contact_and_action_sensitivity: task_metrics
  downstream_ranking_or_control: task_protocol
```

Sparse adaptation benefits from three controls: original dense checkpoint, dense checkpoint adapted on the same data, and sparse checkpoint adapted with a comparable budget. This separates data improvement from attention preservation. Kernel comparisons additionally hold masks, head dimensions, dtype, and hardware fixed. Distillation, quantization, caching, codec changes, and serving optimizations each need an identified contribution when combined.

## Implementation map

| Surface | Pinned official implementation | Important boundary |
|---|---|---|
| Video Swin | mmaction/models/backbones/swin_transformer.py in [FVI-VIDEO-SWIN-CODE] | recognition backbone; learned relative positions, partitioning, and shifts |
| SVG / SVG2 | svg/ and model-specific entrypoints in [FVI-SVG-CODE] | separate pattern selection and semantic-permutation paths; inspect the selected method |
| STA workflow | examples/inference/sta_mask_search/inference_wan_sta.sh in [FVI-STA-ARCHIVE-CODE] | archive branch for complete search/inference; current kernels alone are not the workflow |
| VSA | fastvideo/attention/backends/video_sparse_attn.py, fastvideo-kernel/, and VSA fine-tuning configs in [FVI-FASTVIDEO-CODE] | block metadata, padding reversal, coarse gate weights, and sparse training configuration |
| SANA-Video / LongSANA | sana_multi_scale_video.py, sana_blocks.py, and diffusion/longsana/ in [FVI-SANA-CODE] | selected linear, causal, and FFN variants depend on configuration |
| SANA-Video 2.0 | sana_video2.py, sana_video2_blocks.py, configs/sana_video2/ in [FVI-SANA-CODE] | released 5B checkpoint/config surface differs from paper-wide architecture coverage |

These are inspected source surfaces. No local training, CUDA-kernel benchmark, or model-generation reproduction is recorded for this page.

Hardware compatibility is operator-specific. Tensor layout, valid-block lengths, head dimensions, grouped-query head mapping, forward/backward availability, and accelerator generation determine whether a kernel is usable. A kernel supporting dense equal-length Q/K is not automatically compatible with packed multimodal queries and keys of unequal length.

## Cosmos3-Nano and world-model transfer

Cosmos3-Nano has AR- and DM-specific projections with shared attention interaction. AR queries see AR states; DM queries can see AR and DM states. The model uses grouped-query attention, multimodal positions, and separate continuous conditions/targets. These properties make a generic rectangular video-only mask insufficient to describe the full computation. [C3-TR, pp. 9–14; C3-FW, cosmos_framework/model/generator/mot/attention.py: two_way_attention]

The pinned Framework already exposes two_way_attention, three_way_attention, and dispatch_attention. The three-way path separates Generator self-attention from semantic-context attention and supports NATTEN or FlexAttention metadata as well as dense self-attention. Actual neighborhood and causal semantics depend on the configured path and generated metadata. This is an existing implementation surface to inspect, not evidence that the methods on this page have been benchmarked on Nano. [C3-FW, cosmos_framework/model/generator/mot/attention.py: three_way_attention, dispatch_attention, build_packed_sequence]

| Transfer hypothesis | Concrete change surface | Condition for an informative test |
|---|---|---|
| Visual DM self-attention contains removable interactions | local or content-selected DM visual edges within the existing dispatch | preserve packed-sample isolation, clean/noisy roles, and AR visibility |
| Semantic or action conditioning needs denser access than visual background | exempt or separately budget condition keys | compare condition adherence and opposite-action rollouts at matched visual density |
| Local tiles miss delayed physical consequences | selected distant blocks, coarse global path, or periodic dense layers | evaluate occlusion, reappearance, contact, and delayed effects by horizon |
| Linear aggregation reduces long-context cost | Generator attention replacement with compatible multimodal state | adaptation evidence, state precision, positional treatment, and cross-modal retention |
| Existing neighborhood support is inefficiently configured | NATTEN metadata, window extent, layout, and backend | profile the actual loaded mode before attributing cost to full dense attention |

For an ordinary generation task, visual quality and prompt fidelity may be central. For an action-conditioned world model, the same attention change also needs transition accuracy, action counterfactual sensitivity, event timing, and downstream decision quality. There is no source-backed basis here to classify a visually quiet background as universally irrelevant: support surfaces, obstacles, and distant context can determine the outcome.

A useful candidate preserves high-value condition paths while testing narrower visual interaction budgets. The hypothesis fails if task utility falls outside the task's accepted tolerance despite acceptable visual metrics, or if routing and communication erase the latency gain. Choosing a different topology remains a model-design decision; this knowledge does not select Agents, schedule experiments, or modify AIBuildAI orchestration.

## Open questions

1. Which routing signal predicts physical or action relevance beyond attention mass?
2. How should density vary across noise levels, heads, modalities, and prediction horizons?
3. Can semantic clustering retain small contact features without excessive routing overhead?
4. What state capacity preserves delayed consequences and object reappearance in linear models?
5. Where should dense layers or protected global edges occur at a fixed inference budget?
6. How do sparse layouts interact with grouped-query attention, context parallelism, and changing conditions?
7. Which attention gains survive few-step distillation when routing overhead becomes proportionally larger?

## Sources

Paper versions and official code commits are registered in [sources.yaml](sources.yaml). The mathematical background uses [FVI-FLASHATTN-PAPER] and [FVI-LINEAR-TRANSFORMER-PAPER]. Method evidence uses [FVI-VIDEO-SWIN-PAPER], [FVI-SVG-PAPER], [FVI-STA-PAPER], [FVI-VSA-PAPER], [FVI-SVG2-PAPER], [FVI-SANA-VIDEO-PAPER], and [FVI-SANA-VIDEO2-PAPER]. Code identities are [FVI-VIDEO-SWIN-CODE], [FVI-SVG-CODE], [FVI-STA-ARCHIVE-CODE], [FVI-FASTVIDEO-CODE], and [FVI-SANA-CODE]. Cosmos facts reuse [C3-TR] and [C3-FW] from the owning Model registry.
