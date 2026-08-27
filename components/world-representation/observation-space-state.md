---
id: world-model-kb.components.world-representation.observation-space-state
title: Observation-Space State
kind: component
status: maintained
last_updated: 2026-08-27
owners:
  - AIBuildAI world-model group
---

# Observation-Space State

## Retrieval metadata

**Relevant queries:** pixel-space world model, observation as state, video clip as state, DIAMOND visual details, Vista driving frames, perceptual fidelity versus task state.

**Knowledge provided:** When a world model treats RGB frames or video as the state variable itself, which information that choice preserves, and which control or dynamics claims it does not establish.

**Related pages:** [Video world models](../../foundations/representations/video-world-model.md) owns the generic observation-prediction surface; [diffusion generative modeling](../generative-modeling/diffusion.md) owns the DIAMOND sampler family; [observation-space dynamics](../dynamics-modeling/observation-space-dynamics.md) owns the next-frame transition; [comparison and optimization](comparison-and-optimization.md) compares this medium with latent states.

## Method definition

An observation-space world model uses decoded sensory variables as state:

\[
s_t = o_t \quad\text{or}\quad s_t = o_{t-L+1:t},
\]

and predicts future observations in that same space. No compact \(z_t\) is required for the state interface, although an internal codec may still exist for computation. The representation claim is that task-relevant world properties remain in the pixels (or a short frame stack) rather than in a learned embedding.

This choice preserves high-frequency appearance: scores, small objects, textures, and lighting. It also stores nuisance variation that a control latent might discard. Perceptual sharpness is therefore neither necessary nor sufficient for a useful world state. The discriminating test is whether the pixels retain the variables the downstream decision uses, and whether those variables change under interventions.

## DIAMOND: pixels as the imagination state

DIAMOND trains an image-space EDM world model and an actor–critic inside imagined RGB frames. The state is a stack of \(L=4\) Atari frames, not a VQ token or RSSM categorical. The paper's argument is that visual details discarded by heavier compression can change agent behavior. [DIASRC-PAPER, Sec. 3; REP-DIAMOND-2024]

On Atari 100k it reports mean human-normalized score 1.459 and IQM 0.641 over its protocol and 26-game suite. It is the strongest world-model-trained agent in that table, not a claim against model-free SOTA. A denoising-step ablation on a top-10 subset reports mean HNS 3.052 at three Euler steps versus 1.962 at one step on a single seed, so sampler budget can change the imagined state the policy sees. [DIASRC-PAPER, Tables 1, 4, and 7]

The CSGO branch and Appendix M FID/FVD cells are a separate qualitative surface. They must not inherit the Atari 100k scores, and they do not show that pixel state is required for driving or robot control. [DIASRC-PAPER, Appendix M]

## Vista: high-resolution driving frames as the predicted world

Vista predicts 25-frame, 10 Hz front-view clips at up to \(576\times 1024\), optionally chained by latent replacement. The operational state is the driving video itself, initialized from SVD, not an occupancy volume or a language plan. [VISTA-PAPER]

Table 2 reports nuScenes FID 6.9 and FVD 89.4 under the paper protocol. Those numbers measure distributional video quality. Table 3 IDM L2 tests whether controlled futures remain consistent with an independent motion model; they still do not establish a calibrated occupancy state or a closed-loop planner. Vista is not Wayve GAIA. [VISTA-PAPER, Tables 2–3]

A photorealistic driving clip can hide wrong depth, wrong other-agent intent, or camera-motion confused with scene dynamics. Observation-space state therefore requires geometric or intervention probes beyond FID/FVD.

## What observation-space state is not

IRASim, Predict2.5, and Cosmos Generator decode video, but their learned state lives in a codec latent during denoising. They instantiate reconstructive or multimodal latents, not this method. DreamerV3 decodes observations as a training head; its decision state is the RSSM latent. Treating every video world model as pixel-state collapses independent representation choices.

## Controllable surfaces

| Surface | Mechanism | Expected observable | Main confounder |
|---|---|---|---|
| Frame stack length | supplies velocity-like history in pixels | motion-sensitive control | extra compute and aliasing |
| Resolution and crop | retains or erases small objects and scores | task probes at matched policy | changed visual difficulty |
| Pixel versus latent training | trades detail for compression | downstream return at matched budget | capacity and sampler changes together |
| Denoising or sampling steps | alter the imagined observation the agent sees | policy score versus step count | one-seed or subset evaluations |
| Color, lighting, and overlay | nuisance capacity | reconstruction without control gain | decoder-only improvements |

## Evaluation and failure diagnosis

| Symptom | Plausible cause | Discriminating evidence |
|---|---|---|
| Sharp frames, weak policy | nuisance detail, missing game state | overlay, score, and object probes |
| Strong FID, ignored actions | continuation prior dominates | swapped-action pairs at fixed noise |
| Good short clip, identity drift | no persistent object state | horizon-conditioned identity metrics |
| Pixel WM wins one domain | domain-specific overlays | transfer to robot or driving pixels |
| Sampler change moves return | imagined state distribution shifted | matched-NFE comparison |

## Cosmos3-Nano connection

Cosmos3-Nano Generator does not use raw pixels as its diffusion state; it denoises codec latents. DIAMOND motivates testing whether Nano's codec erases small task-relevant structure, but Atari pixel results do not select Nano's latent resolution. Vista motivates driving-frame probes that are not equivalent to Generator FID. Exact codec and modality contracts remain on the [Generator](../../models/cosmos3-nano/generator.md) and [architecture](../../models/cosmos3-nano/architecture.md) pages.

## Sources

- [REP-DIAMOND-2024] and [DIASRC-PAPER] identify DIAMOND and its Atari 100k and denoising-step evidence.
- [VISTA-PAPER] identifies Vista's driving-video state and FID/FVD or IDM surfaces.
