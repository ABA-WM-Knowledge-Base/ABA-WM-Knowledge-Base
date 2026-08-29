---
id: world-model-kb.components.world-representation.reconstructive-latents
title: Reconstructive Latents
kind: component
status: maintained
last_updated: 2026-08-27
owners:
  - AIBuildAI world-model group
---

# Reconstructive Latents

## Retrieval metadata

**Relevant queries:** VAE world-model state, RSSM observation head, reconstructive latent, codec latent as state, DreamerV3 categorical latent, Predict2.5 tokenizer, IRASim SDXL latent.

**Knowledge provided:** How decoder-backed compression defines a world state, which rate–distortion and control-state tests apply, and how codec latents used for generation differ from RSSM decision latents.

**Related pages:** [Latent world models](../../foundations/representations/latent-world-model.md) owns the generic formalism; [latent diffusion and DiT](../generative-modeling/latent-diffusion-and-dit.md) owns the generative use of a codec; [recurrent latent dynamics](../dynamics-modeling/recurrent-latent-dynamics.md) owns RSSM transitions; [latent simulation and imagination](../reasoning/latent-simulation-and-imagination.md) owns decision use of those latents.

## Method definition

A reconstructive latent maps observations to a compact code that can regenerate sensory variables:

\[
z_t = e_\theta(o_{\leq t}, a_{<t}), \qquad
\hat o_t = d_\phi(z_t)\ \text{or}\ d_\phi(h_t,z_t).
\]

The decoder may be a VAE, a discrete codebook, or an RSSM observation head. The representation claim is that \(z_t\) is a sufficient statistic of the history for the model's prediction and decision heads. Reconstruction loss is a training signal, not the definition of sufficiency.

Two non-equivalent reconstructive states appear in current entries:

1. **Decision latent:** a compact \(z_t\) from which an actor, critic, or planner acts, as in World Models and DreamerV3.
2. **Codec latent:** a spatially organized code in which a video generator denoises, as in Predict2.5, IRASim, and Cosmos3-Nano Generator.

Sharing a decoder does not make these the same state. A codec can reconstruct pixels while remaining a poor planning embedding; an RSSM can support control while reconstructing poorly on textures.

## World Models: a frame VAE as state

World Models compressed each frame with a variational autoencoder \(V\) into \(z_t\), then ran an MDN-RNN on that code. The VAE is the representation component; the recurrent mixture is the dynamics component. On CarRacing, a controller on \([z_t,h_t]\) outperformed \(V\)-only baselines, which supports using the compressed code as a control state under that setup rather than proving that reconstruction quality selected the latent. [FND-WORLD-MODELS-2018, Secs. 2–4, Table 1; COMP-REASONING-WORLD-MODELS-PROJECT]

## DreamerV3: categorical RSSM state with an observation head

DreamerV3 infers categorical latent states, predicts rewards and continuation, and decodes observations. The actor–critic trains from imagined latents, so the canonical state for decisions is \(z\), not the decoded image. Nature reports a robustness stack (symlog, two-hot, KL balancing, free bits, percentile return normalization) that stabilized this latent across more than 150 tasks in eight domains. Figure 6 on a 14-task ablation set shows that removing reconstruction gradients and removing reward/value gradients hurt different task subsets, so reconstruction is complementary rather than universally dominant. [MBRL-DREAMERV3-2025, pp. 648–650, Figs. 4 and 6; DV3SRC-PAPER-NATURE, Methods and Fig. 6]

Extended Data Table 1 numeric aggregates were not recovered from the public HTML surfaces. Do not invent those cells. The public `danijar/dreamerv3` repository is a DreamerV2-based reimplementation and is not the Nature training code. [DV3SRC-PAPER-NATURE; DV3SRC-CODE-CURRENT]

## Video codecs as generative state, not RSSM state

Cosmos-Predict2.5 and IRASim denoise in a learned video or image latent and decode to pixels. Predict2.5 is a latent rectified-flow transformer over visual prefixes; IRASim uses an SDXL-latent trajectory-to-video transformer with frame-level action modulation. Those latents are the computational state of generation. They are not shown to be interchangeable with Dreamer categorical states or TD-MPC2 SimNorm vectors. [P25-TR, pp. 8–11; IRASRC-PAPER-V2, pp. 4–6]

IRASim's public implementation, training-step, and planning-code gaps remain in the [IRASim Paper entry](../../papers/irasim/README.md). Codec identity must not be collapsed with released-code completeness.

## Controllable surfaces

| Surface | Mechanism | Expected observable | Main confounder |
|---|---|---|---|
| Latent dimension / codebook size | rate–distortion | recon versus forecast or return | overfitting a larger codebook |
| Stochasticity (categorical, Gaussian) | uncertainty in \(z\) | calibration and exploration | decoder ignoring \(z\) |
| Reconstruction weight | texture versus task state | probe and policy jointly | texture-only gains |
| KL balance / free bits | prior–posterior use of \(z\) | stable latent usage | replay ratio interaction |
| Spatial codec stride | small-object retention | contact and overlay probes | extra DiT tokens |

## Evaluation and failure diagnosis

| Symptom | Plausible cause | Discriminating evidence |
|---|---|---|
| High PSNR, weak control | nuisance capacity | reward/object probes at matched \(z\) size |
| Strong policy, poor decode | decision-aware compression | keep policy, ablate decoder |
| Posterior rollout works, prior fails | inference uses future frames | posterior-versus-prior comparison |
| Codec change moves FVD only | perceptual latent, not task state | action counterfactuals and ranking |
| RSSM and DiT codec treated as equal | naming collision | interface: who reads \(z\) |

## Cosmos3-Nano connection

Nano Generator state is a diffusion subsequence over VAE visual tokens, audio latents, and action representations, not an RSSM categorical. DreamerV3 reconstruction-versus-reward complementarity is a hypothesis for Nano loss weighting, not a transferred coefficient. Exact token layouts belong to [architecture](../../models/cosmos3-nano/architecture.md) and [Generator](../../models/cosmos3-nano/generator.md).

## Sources

- [FND-WORLD-MODELS-2018] and [COMP-REASONING-WORLD-MODELS-PROJECT] identify World Models \(V\).
- [MBRL-DREAMERV3-2025] and [DV3SRC-PAPER-NATURE] identify DreamerV3 RSSM state.
- [P25-TR] and [IRASRC-PAPER-V2] identify video codec latents used as generative state.
