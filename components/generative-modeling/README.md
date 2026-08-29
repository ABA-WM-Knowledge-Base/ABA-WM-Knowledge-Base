---
id: world-model-kb.components.generative-modeling
title: Generative Modeling for World Models
kind: component
status: maintained
last_updated: 2026-08-24
owners:
  - AIBuildAI world-model group
---

# Generative Modeling for World Models

## Retrieval metadata

**Relevant queries:** generative world-model method, autoregressive prediction, diffusion world model, latent diffusion, DiT, flow matching, action-conditioned video, omnimodal generator.

**Knowledge provided:** A method-oriented map of generative world-model families, their interfaces and evidence boundaries, and the comparison and optimization knowledge that connects them.

**Related pages:** [Video world models](../../foundations/representations/video-world-model.md) owns the general prediction surface; [latent world models](../../foundations/representations/latent-world-model.md) owns representation choices; [Cosmos3-Nano Generator](../../models/cosmos3-nano/generator.md) owns the concrete target-model implementation.

## Component boundary

A generative world model learns a conditional distribution over future environment-relevant variables:

\[
p_\theta(y_{t+1:t+H}\mid h_t,u_{t:t+H-1},c).
\]

History \(h_t\) may include observations, latent state, language, audio, or proprioception. Control \(u\) may be an action, camera trajectory, goal, or other intervention. Output \(y\) may be pixels, video latents, audio, actions, rewards, occupancy, or a joint output.

Distribution fit, dynamics validity, and decision utility are different properties. An image generator may model a data distribution without representing transitions. A realistic video can violate state or intervention effects. A physically plausible rollout can still be too slow or poorly calibrated for control.

## Method map

The multi-page layout below is specific to this Generative Modeling Component.

| Method page | Canonical knowledge owned |
|---|---|
| [Autoregressive and recurrent modeling](autoregressive.md) | causal factorization, recurrent latent prediction, discrete video tokens, teacher forcing, serial rollout, World Models and iVideoGPT |
| [Diffusion modeling](diffusion.md) | DDPM denoising, iterative sampling, multimodal futures, pixel-space world models, and DIAMOND |
| [Latent diffusion and DiT](latent-diffusion-and-dit.md) | codec rate–distortion, latent denoising, cross-attention conditioning, Transformer scaling, LDM and DiT evidence |
| [Flow matching and rectified flow](flow-matching-and-rectified-flow.md) | continuous transport fields, path geometry, solvers, few-step claims, and Cosmos flow objectives |
| [Mean Flow and Pixel Mean Flow](mean-flow-and-pixel-mean-flow.md) | average-velocity prediction, Improved MeanFlow stability and guidance, Pixel MeanFlow output parameterization, and world-model transfer tests |
| [Action-conditioned video modeling](action-conditioned-video.md) | action timing and semantics across UniSim, iVideoGPT, IRASim, and DIAMOND; planning and model-exploitation boundaries |
| [Omnimodal generation](omnimodal-generation.md) | Cosmos-Predict2.5 and Cosmos 3 lineage, clean-prefix curricula, multimodal latent streams, and action modes |
| [Comparison and optimization](comparison-and-optimization.md) | method selection axes, supported patterns, failure diagnosis, Cosmos3-Nano attachment points, and open questions |

The pages are compositional. A model may use a latent codec, Transformer backbone, rectified-flow objective, clean-prefix condition, and action-conditioned video interface simultaneously. The map identifies the canonical owner of each mechanism instead of forcing one exclusive category.

## Evidence ownership

Individual system details remain in the [iVideoGPT](../../papers/ivideogpt/README.md), [IRASim](../../papers/irasim/README.md), [DIAMOND](../../papers/diamond/README.md), [Cosmos-Predict2.5](../../papers/cosmos-predict2-5/README.md), and [X-WAM](../../papers/x-wam/README.md) Paper entries. Concrete Cosmos 3 and X-WAM implementation and execution facts remain in their [Model entries](../../models/README.md). The local [source registry](sources.yaml) owns only latent diffusion and DiT identities not already registered elsewhere.

This method decomposition belongs to the current Generative Modeling entry. It is not a structure requirement for other Components.
