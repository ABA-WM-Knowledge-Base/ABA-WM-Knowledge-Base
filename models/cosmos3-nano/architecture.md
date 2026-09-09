---
id: world-model-kb.models.cosmos3-nano.architecture
title: Cosmos3-Nano Architecture and Computation Semantics
kind: reference
status: maintained
last_updated: 2026-09-09
owners:
  - AIBuildAI world-model group
---

# Cosmos3-Nano Architecture and Computation Semantics

## Retrieval metadata

**Relevant queries:** tower structure, Mixture-of-Transformers, attention, sequence layout, positional computation, modality information flow, parameter lineage, or freezing surfaces.

**Knowledge provided:** computation-graph invariants, tower and frontend boundaries, parameter groups, compatibility considerations, implementation anchors, and architecture-level experiment variables.

**Related pages:** [Inference](inference.md) contains runtime references; [Reproduction](reproduction.md) contains observed execution state; [Policy](policy.md) owns the specialized policy interface; [Research registry](research-queue.md) records unresolved architecture questions. Model-independent owners include [latent world models](../../foundations/representations/latent-world-model.md), [representation learning and JEPA](../../foundations/representations/representation-learning-and-jepa.md), [autoregressive modeling](../../foundations/learning-objectives/autoregressive-modeling.md), and [diffusion and flow matching](../../foundations/learning-objectives/diffusion-and-flow-matching.md). Cross-paper method context is owned by [latent diffusion and DiT](../../components/generative-modeling/latent-diffusion-and-dit.md), [flow matching and rectified flow](../../components/generative-modeling/flow-matching-and-rectified-flow.md), [reasoning–generation–action integration](../../components/reasoning/reasoning-generation-action.md), and [sparse, local, and linear attention](../../components/fast-video-inference/efficient-attention.md).

## Canonical model boundaries

Cosmos3-Nano is an approximately 16B-parameter unified omnimodal world model. Each decoder layer contains paired AR- and DM-specific parameter sets; stacked across all layers, these form an approximately 8B **Reasoner tower** and an approximately 8B **Generator tower**. The Reasoner performs autoregressive next-token modeling, while the Generator performs continuous rectified-flow denoising. Both operate inside one transformer computation graph, but they do not have symmetric information flow.[C3-TR, pp.11-14, Figure 5 and Table 2]

Never collapse the following surfaces into one object:

| Surface | Canonical identity | Native objective | Native output |
|---|---|---|---|
| Base unified checkpoint | `nvidia/Cosmos3-Nano` | AR and DM objectives across the two towers | text and supported continuous modalities, subject to mode and frontend availability |
| Reasoner component | AR tower extracted from the unified weights | causal next-token prediction | text |
| Generator component | DM tower plus required modality projections and decoders | rectified-flow velocity prediction | image, video, audio, or action representations, depending on mode |
| Policy-DROID | `nvidia/Cosmos3-Nano-Policy-DROID` | DROID-specific action generation with auxiliary future RGB | 32-step DROID action chunks |

Do not attribute Policy-DROID control results to base Nano. Do not interpret a Reasoner-only deployment as a unified Nano deployment. Do not call a natural-language plan an action tensor.

## Transformer specification

The technical report gives the following base Nano transformer specification.[C3-TR, pp.12-14, Table 2]

| Property | Value |
|---|---:|
| Total parameter scale | approximately 16B |
| Nominal scale per tower | approximately 8B |
| Decoder layers | 36 |
| Hidden size | 4,096 |
| Attention heads | 32 |
| KV heads | 8 |
| Head dimension | 128 |
| Feed-forward hidden size | 12,288 |

The phrases "16B Nano" and "8B tower" describe different accounting surfaces. They must not be converted into memory requirements. Runtime memory also depends on which tower and frontends are loaded, precision, KV cache, visual-token count, batch size, and backend.[C3-HF; C3-FW-FAQ]

## Core mechanisms and invariants

### Dual-tower Mixture-of-Transformers

Each decoder layer contains tower-specific projections, feed-forward parameters, and modality mappings. The design is better understood as a Mixture-of-Transformers than as a top-k routed Mixture-of-Experts: the report does not define an expert gate that chooses among interchangeable experts for each token.[C3-TR, pp.11-12, Figure 5]

```text
AR subsequence -> Reasoner projections and MLP --+
                                                   +-> shared attention interaction
DM subsequence -> Generator projections and MLP --+
```

In the fixed framework implementation, `Cosmos3VFMNetwork`, modality enablement flags, and mappings such as `action2llm`, `sound2llm`, and `vae2llm` expose this separation.[C3-FW-MODEL; C3-FW-OMNI-MOT]

Optimization invariant: a change to a modality projection is not equivalent to changing the shared transformer state distribution, and a change to one tower does not automatically update the other tower's task objective.

### AR and DM subsequences

The unified sequence contains two classes of subsequence:[C3-TR, pp.9-10, Figure 4]

- **AR subsequences** contain language tokens and optional ViT visual tokens. They are processed by the Reasoner tower under causal next-token prediction.
- **DM subsequences** contain visual VAE latents, audio latents, action representations, and continuous control conditions. They are processed by the Generator tower under rectified-flow denoising.

Clean DM conditions precede noisy DM targets in the sequence plan. This ordering determines whether a continuous modality is observed context or a prediction target. The sequence plan is therefore necessary evidence for interpreting loss changes or determining whether a supplied tensor is consumed as a condition.

### Asymmetric attention visibility

The principal architecture invariant is asymmetric visibility:[C3-TR, pp.11-12, Figure 5]

| Query source | Visible key/value states | Consequence |
|---|---|---|
| AR / Reasoner | AR only | The reasoning state is not rewritten by the current diffusion trajectory |
| DM / Generator | AR and DM | Continuous generation can consume language and visual-semantic context plus continuous conditions |

Three operational consequences follow:

1. Generator states can be conditioned by Reasoner states, but a denoised rollout does not revise the Reasoner state within the same forward process.
2. A rollout-critique loop requires an external cycle: decode the generated media, re-encode it as a new observation, and invoke Reasoner again.
3. A Reasoner-only backend may omit Generator, audio, action, and VAE parameters; it therefore cannot recover media generation by changing the prompt.[C3-REASONER-COOKBOOK]

Any intervention that allows AR queries to attend to noisy DM states changes this invariant and should be treated as an architecture experiment, not a routine fine-tuning change.

The pinned implementation distinguishes joint two-way attention from a three-way path that separates Generator self-attention and semantic-context attention. In `cosmos_framework/model/generator/mot/attention.py`, `three_way_attention` accepts NATTEN or FlexAttention metadata, or uses dense self-attention; `dispatch_attention` and `build_packed_sequence` determine the selected path and its metadata. Neighborhood, causal, and packed-sample semantics therefore depend on the resolved configuration, not only on the model name. These code surfaces do not establish a measured sparsity or speedup for a particular Nano checkpoint.[C3-FW, three_way_attention, dispatch_attention, build_packed_sequence]

### Spatial and temporal positions

Cosmos 3 uses 3D MRoPE for spatial coordinates and absolute time in visual and temporal tokens. The report describes a base video scale of 24 FPS and 4x VAE temporal compression, yielding approximately 6 latent time steps per second. AR and DM position domains are separated by an offset of 15,000.[C3-TR, pp.12-14, Figure 6]

Absolute time is part of the model contract. Replacing frame sampling, action rate, or audio alignment without updating timestamps changes the implied dynamics. Array index equality is not sufficient for multimodal temporal alignment.

Generator denoising time enters through diffusion-time modulation. Reasoner does not use the same noise-time state. Shared attention does not imply shared normalization, feed-forward, or timestep-modulation parameters.[C3-TR, pp.12-14, Figure 6; C3-FW-OMNI-MOT]

## Modality frontends

Different modalities retain specialized frontends and are projected into a common hidden space.[C3-TR, pp.7-10, Figures 3-4]

| Modality role | Frontend | Subsequence | Update or use rule |
|---|---|---|---|
| Text | tokenizer and embeddings | AR | instruction, semantic condition, and text output |
| Image/video understanding | Qwen3-VL-style ViT; 16x16 patches with 2x2 token merge | AR | jointly updated during Reasoner training |
| Image/video generation | frozen Wan2.2-TI2V-5B VAE | DM | approximately 4x temporal and 32x32 spatial compression |
| Audio | frozen 48 kHz stereo audio VAE | DM | hop 1,920; approximately 25 latent tokens per second |
| Action | domain-specific encoder, projection, and decoder | DM | continuous condition or generation target |

The same RGB observation has two distinct computational meanings. A VQA input uses the ViT/AR path; an I2V or forward-dynamics condition uses the VAE/DM path. Do not reuse token budgets, preprocessing assumptions, or learned adapters across those paths without an explicit compatibility test. The full I/O contract is in [modalities-and-io.md](modalities-and-io.md).

## Parameter lineage and update scope

The architecture is trained through staged parameter flow rather than one end-to-end run from random initialization:[C3-TR, pp.25-32]

1. Initialize and train the Reasoner from Qwen3-VL-8B.
2. Use the trained Reasoner as the semantic path of unified Nano.
3. Freeze Reasoner while pre-training Generator for image, video, and audio generation.
4. Add action and transfer tasks during mid-training.
5. Apply task-specific post-training for surfaces such as T2I, I2V, DROID policy, or LIBERO.

Shared hidden width does not imply that all parameters are jointly updated in every stage. When proposing an optimization, state whether it modifies:

- a frozen modality codec;
- a trainable modality connector or projection;
- the Reasoner tower;
- the Generator tower;
- an action-domain adapter;
- a post-trained task head or checkpoint;
- the external inference or selection loop.

Use [training.md](training.md) for stage-level optimizer and freeze rules and [post-training.md](post-training.md) for checkpoint lineage.

## Optimization levers

### Select the narrowest compatible intervention

| Observed deficit | First parameter surface to test | Parameters to hold fixed in the first ablation | Required control |
|---|---|---|---|
| Incorrect object, relation, or instruction parsing | ViT connector or Reasoner adaptation | Generator and action adapters | text-only and image-conditioned paired probes |
| Correct semantics but poor visual condition adherence | DM visual projection, condition ordering, or Generator adaptation | Reasoner and codec | identical seed with and without the condition |
| Dynamics ignore action | action projection, sequence plan, or action-conditioned Generator loss | Reasoner and visual codec | opposite-action counterfactual pair |
| Correct action direction but wrong magnitude | domain normalization or output decoder | backbone towers | single-axis calibrated trajectories |
| Long-horizon drift | temporal encoding, training horizon, or external receding-horizon loop | short-horizon adapter | matched short- versus long-horizon evaluation |
| Policy fails after successful offline dynamics probes | policy post-training or controller contract | base Nano representation | replay, shadow, and closed-loop stages |

Start with adapters, projections, data mixture, or external selection when the base representation is not yet shown to be the bottleneck. Unfreezing a full tower is justified only after frozen-backbone diagnostics plateau and the experiment has enough data to measure regression on retained capabilities.

### Preserve cross-surface capability

For tower updates, define a retention set from an unaffected surface. Examples:

- Reasoner tuning: retain general multimodal and temporal-understanding probes.
- Generator tuning: retain condition adherence and short-horizon visual quality.
- Action mid-training: retain action-free image/video generation and cross-domain action probes.
- Policy post-training: retain offline inverse/forward-dynamics diagnostics and action-domain calibration.

If the optimization changes shared embeddings or attention state distributions, test both towers even when only one task loss is optimized.

### Exploit the external loop before changing attention

For planning with imagined futures, the canonical baseline is:

```text
Reasoner proposal
  -> Generator or WAM rollout
  -> decode predicted observation
  -> re-encode as a new Reasoner input
  -> critique or replan
```

Measure whether this loop improves candidate ranking before attempting bidirectional AR-DM attention. If it fails, separate rollout inaccuracy, re-encoding loss, critique quality, and selection policy.

## Diagnostics and failure signatures

| Failure signature | Likely contract violation or bottleneck | Diagnostic action |
|---|---|---|
| Model is described as either 8B or 16B without qualification | overall and tower accounting were mixed | record overall, loaded component, and runtime memory separately |
| Text plan is treated as a controller action | AR text and DM action objectives were conflated | verify action decoder, domain adapter, units, and controller path |
| Generated rollout never changes the current textual answer | asymmetric attention was misunderstood | inspect whether an external decode/re-encode loop exists |
| VQA receives VAE latents or generation receives ViT tokens | visual frontend was selected by file type instead of task semantics | log frontend, subsequence type, and sequence plan |
| Reasoner-only load is asked to generate video | required Generator and codec weights are absent | audit loaded tensor namespaces and modality flags |
| Motion speed changes after FPS adjustment | timestamps or latent-time scale are inconsistent | log source timestamps, sampled frame indices, latent rate, and action rate |
| DROID result is reported for base Nano | checkpoint lineage is missing | bind every result row to checkpoint ID and revision |
| One tower improves while the other regresses | shared-state distribution shifted | run cross-tower retention probes and inspect connector updates |

Architecture-level ambiguities that require new tests belong in [research-queue.md](research-queue.md). Do not record them as observed defects until an execution artifact exists in [reproduction.md](reproduction.md).

## Experiment guidance

Every architecture experiment should include:

1. **Surface identity:** checkpoint ID and revision, loaded towers, enabled frontends, backend, and code commit.
2. **Intervention scope:** exact trainable parameter patterns, frozen modules, initialization, and optimizer groups.
3. **Sequence contract:** AR/DM role, condition/target ordering, attention mask, timestamps, and token or latent budget.
4. **Matched control:** same data, seed set, preprocessing, and evaluation with the intervention disabled.
5. **Target metric:** a metric directly tied to the hypothesized mechanism, plus retention metrics on unaffected capabilities.
6. **Falsification rule:** the result that would reject the mechanism claim rather than merely reject one hyperparameter.
7. **Resource record:** batch size, precision, GPU type/count, peak memory, throughput, and wall time.

Recommended experiment order:

```text
schema and preprocessing validation
  -> frozen-backbone adapter baseline
  -> data-mixture or objective ablation
  -> selective projection/tower unfreezing
  -> broader architecture change
  -> closed-loop validation
```

Convert accepted optimization choices into [optimization-playbook.md](optimization-playbook.md). Keep unresolved questions and proposed discriminating tests in [research-queue.md](research-queue.md). Keep actual command outcomes and artifacts in [reproduction.md](reproduction.md).

## Code anchors

| Architecture concept | Fixed-source anchor | Agent use |
|---|---|---|
| Unified wrapper and weight mapping | `C3-FW-MODEL` | trace loaded components and Diffusers-to-framework names |
| Omni MoT network | `C3-FW-OMNI-MOT` | inspect tower construction, modality projections, domains, and sequence processing |
| Mode and argument validation | `C3-FW-ARGS` | verify legal modality combinations and runtime limits |
| Public inference path | `C3-FW-INFERENCE` | map external mode to execution path and artifacts |

[C3-FW-MODEL; C3-FW-OMNI-MOT; C3-FW-ARGS; C3-FW-INFERENCE]

Capability flags such as `vision_gen`, `sound_gen`, and `action_gen` describe enabled paths. They are not independent models that can be combined without matching weights, projections, checkpoint lineage, and mode validation.

## Related knowledge

- Representation and external contracts: [modalities-and-io.md](modalities-and-io.md)
- Autoregressive tower: [reasoner.md](reasoner.md)
- Diffusion tower: [generator.md](generator.md)
- Action objectives: [action-modeling.md](action-modeling.md)
- DROID policy checkpoint: [policy.md](policy.md)
- Data and optimization stages: [data.md](data.md), [training.md](training.md), [post-training.md](post-training.md)
- Evaluation and known limitations: [evaluation.md](evaluation.md), [limitations.md](limitations.md)
- Source registry: [sources.yaml](sources.yaml)
