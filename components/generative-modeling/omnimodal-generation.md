---
id: world-model-kb.components.generative-modeling.omnimodal-generation
title: Omnimodal Generative World Models
kind: component
status: maintained
last_updated: 2026-08-19
owners:
  - AIBuildAI world-model group
---

# Omnimodal Generative World Models

## Retrieval metadata

**Relevant queries:** video foundation model generation, Cosmos-Predict2.5, clean prefix, Text2World, Image2World, Video2World, Cosmos 3 Generator, omnimodal generation, media action joint attention.

**Knowledge provided:** The Cosmos lineage from large-scale latent video flow to a Reasoner-coupled omnimodal Generator, including curricula, modality interfaces, action modes, and variant boundaries.

**Related pages:** [Flow matching](flow-matching-and-rectified-flow.md) owns the objective; [latent diffusion and DiT](latent-diffusion-and-dit.md) owns representation/backbone choices; [reasoning–generation integration](../reasoning/reasoning-generation-action.md) owns the semantic interface.

## From video generation to a world-foundation surface

A broad generative world model must handle more than one prompt-to-video task. It needs reusable conditioning, temporal continuation, data coverage, scalable resolution/duration, and post-training surfaces. Adding modalities increases both capability and ambiguity: every task must retain an exact input/output and checkpoint contract.

## Cosmos-Predict2.5

Cosmos-Predict2.5 combines:

- a causal video autoencoder with 4× temporal and 8×8 spatial compression;
- a Transformer continuous generator trained with flow matching;
- a Cosmos-Reason1 text encoder;
- Text2World, Image2World, and Video2World conditioning;
- progressive task and resolution training;
- named domain SFT, merge, reward-post-trained, distilled, and specialist variants.

[P25-TR, pp. 6–14]

### Clean-prefix conditioning

Conditioning frames remain clean in latent space while generated regions receive noise. This provides one task interface for image-conditioned and video-conditioned continuation without corrupting the observed prefix. It also creates a boundary at which abrupt transition artifacts can appear.

### Data and curriculum

The report describes filtering more than six billion candidate clips to roughly 200 million curated clips. Training progresses through Text2Image, Image2World/Video2World, higher resolutions, and Text2World. The curriculum changes task, resolution, and data distribution together, so a stage-to-stage gain cannot isolate one factor without an ablation. [P25-TR, pp. 8–13]

### Time-sampling intervention

The report states that placing 5% of training samples in the highest 2% of noise levels reduced abrupt condition-to-generation transitions. This is evidence for the specific failure and data distribution; the ratio is not a universal recipe. [P25-TR, pp. 8–10]

### Evidence and release boundary

Predict2.5 reports physical-AI video benchmarks and robot, driving, multiview, action-conditioned, and synthetic-data applications. Each belongs to a named specialist and protocol. Reward optimization, merging, distillation, and all specialists are not one released reproducible path. The [Paper entry](../../papers/cosmos-predict2-5/paper.md) owns exact results and code gaps.

## Cosmos 3

Cosmos 3 expands the interface from video foundation generation to an omnimodal model family. Its mixture-of-transformers architecture contains:

- an autoregressive stream for language and visual context;
- a diffusion stream for continuous vision, audio, and action latents;
- separate parameter sets for the two objectives;
- diffusion queries that attend to autoregressive and diffusion context;
- modality-specific masks and time variables.

The Nano checkpoint combines an approximately 8B Reasoner tower and approximately 8B Generator tower. [C3-TR, pp. 8–13]

### Output modes

| Mode | Input context | Generated output | Evidence boundary |
|---|---|---|---|
| Image/video generation | text and optional visual context | visual latent decoded to media | media benchmark only |
| Audio generation | compatible multimodal context | audio latent | not video/action evidence |
| Forward dynamics | history plus actions | future media/state | not a policy |
| Inverse dynamics | observed transition | action estimate | may be one-to-many |
| Joint WAM | history/goal | future media and actions | internal consistency is not control |
| Policy-DROID | robot observations and goal | DROID action chunk | separate post-trained checkpoint |

[C3-TR, pp. 31–69]

The model family demonstrates a common interface for multiple surfaces, not universal capability in every checkpoint/backend. Results must bind to base Nano, specialist action mode, or Policy-DROID as applicable.

## What changed across the lineage

| Axis | Cosmos-Predict2.5 | Cosmos 3 |
|---|---|---|
| Core continuous output | video latent | vision, audio, and action latents |
| Semantic encoder/context | Cosmos-Reason1 text encoder | native autoregressive Reasoner stream |
| Architecture | video DiT | paired AR/DM mixture of transformers |
| Condition interaction | text/clean visual prefix | AR context plus cross-DM attention |
| Action status | specialist applications | native FD/ID/WAM modes plus separate policy |
| Evidence unit | base/post-trained/specialist video checkpoints | Reasoner, Generator, action, and policy surfaces |

Weights and reported results are not interchangeable across the generations.

## Design surfaces

### Modality balance

Video, audio, action, and language differ in token count, entropy, temporal rate, and supervision. Loss masks, time distributions, and mixture sampling determine which modality dominates updates.

### Semantic conditioning

The AR stream may provide objects, relations, goals, or plans to the Generator. Condition swaps and structured-context ablations are needed to show the Generator uses this information.

### Cross-modal synchronization

Audio/video/action alignment errors can appear as model errors. Evaluation must verify timestamps, rates, interpolation, and missing channels.

### Specialist post-training

Domain adaptation can improve a target while narrowing coverage. Preserve exact base and specialist identities and run a regression matrix across modalities.

### Inference budget

Resolution, duration, solver steps, guidance, parallelism, and modality determine memory and latency. Report them for every comparison.

## Failure boundaries

- A realistic sample is not a physically correct future.
- A model that emits actions is not automatically a safe policy.
- Joint action/video agreement can be shared hallucination.
- A Reasoner text plan does not define actuator units or control rate.
- A Predict2.5 result does not establish Cosmos3-Nano performance.
- A specialist checkpoint result does not belong to base Nano.
- A documented mode does not establish successful local execution.

## Cosmos3-Nano attachment points

The target surfaces include codec preservation, modality/time sampling, semantic conditioning, solver efficiency, FD action sensitivity, and WAM consistency. Each belongs to the [comparison and optimization](comparison-and-optimization.md) matrix and the model-specific [optimization playbook](../../models/cosmos3-nano/optimization-playbook.md).

## Sources

- [P25-TR] identifies Cosmos-Predict2.5 report v2.
- [C3-TR] identifies Cosmos 3 report v4.
