---
id: world-model-kb.components.fast-video-inference
title: Fast Video Inference
kind: component
status: maintained
last_updated: 2026-09-09
owners:
  - AIBuildAI world-model group
---

# Fast Video Inference

## Retrieval metadata

**Relevant queries:** accelerate video generation, reduce diffusion or flow sampling cost, one-step video, few-step video, distillation, training-free caching, feature reuse, sparse attention, local attention, linear attention, inference latency, denoising NFE, real-time world-model rollout.

**Knowledge provided:** A compute-oriented map of learned step reduction, training-free intermediate reuse, and cheaper attention interactions, with explicit distinctions among sampling steps, neural-network evaluations, executed operator cost, denoising time, and end-to-end latency.

**Related pages:** [Generative Modeling](../generative-modeling/README.md) owns how future distributions are represented and learned; [Flow Matching and Rectified Flow](../generative-modeling/flow-matching-and-rectified-flow.md) owns continuous-transport mathematics and solver behavior; [Cosmos3-Nano Generator](../../models/cosmos3-nano/generator.md) owns the concrete target architecture and checkpoint boundaries; [Cosmos-Predict2.5](../../papers/cosmos-predict2-5/README.md) owns that work's rCM result and released-code mismatch.

## Component boundary

Fast Video Inference owns cross-paper knowledge about reducing the computation, memory traffic, or sequential depth required to produce video from an existing generative model. Its comparison surface includes latency, throughput, neural-network evaluations, memory, output quality, temporal behavior, diversity, conditioning fidelity, and downstream world-model utility.

This boundary is narrower than Generative Modeling. Diffusion, flow matching, latent compression, and autoregression define generative mechanisms; this Component studies how those mechanisms are executed more cheaply. A method may therefore belong to both knowledge surfaces without duplicating canonical explanations.

Few-step distillation is a post-training intervention: it learns new student weights, auxiliary scores, discriminators, reward models, experts, or transition heads. Training-free caching, attention optimization, quantization, solver replacement, causal streaming, and distributed serving are distinct acceleration families. Their effects can compose with distillation, but their evidence is not interchangeable.

## Knowledge map

The current entry contains three canonical syntheses:

| Page | Knowledge owned |
|---|---|
| [Few-Step and One-Step Distillation](few-step-distillation.md) | cost semantics; consistency, distribution-matching, adversarial, reward-guided, phased, expert, and transition-matching methods; historical evidence; failure diagnosis; evaluation contract; public implementation state; and Cosmos transfer boundaries |
| [Training-Free Caching](caching.md) | cross-timestep and cross-branch redundancy; cached objects, refresh policies, and correction; DeepCache-to-runtime-adaptive method evolution; failure diagnosis; evaluation contract; public implementations; and Cosmos transfer boundaries |
| [Sparse, Local, and Linear Attention](efficient-attention.md) | token-interaction cost; geometric, content-adaptive, linear, and hybrid mechanisms; training and kernel requirements; controlled speed/quality evidence; failure diagnosis; and Cosmos implementation and transfer boundaries |

Additional acceleration families can be added as independent owner pages when their evidence is curated. The entry does not assume that every future page must use the structure of the current distillation synthesis.

## Ownership and evidence boundary

| Knowledge object | Canonical owner |
|---|---|
| Generic diffusion, flow, latent, and autoregressive objectives | [Foundations](../../foundations/README.md) and [Generative Modeling](../generative-modeling/README.md) |
| One paper's complete architecture, experiments, and released-code interpretation | Its [Paper entry](../../papers/README.md), when present |
| Cross-paper acceleration mechanisms and matched comparison criteria | This Component |
| A named checkpoint, runtime interface, or observed execution | Its [Model entry](../../models/README.md) and `reproduction.md` |
| A versioned task, protocol, and evaluator | Its [Benchmark entry](../../benchmarks/README.md) |

Method claims in this entry are source-backed but not locally reproduced unless an owning reproduction record says otherwise. Retrieval of this knowledge can inform diagnosis and strategy selection; it does not define Agent selection, experiment scheduling, permissions, stopping, or any other AIBuildAI orchestration behavior.

## Sources

Primary papers, official project pages, and pinned official repositories used by this entry resolve through [`sources.yaml`](sources.yaml). Existing source identities from Cosmos-Predict2.5 are reused rather than duplicated.
