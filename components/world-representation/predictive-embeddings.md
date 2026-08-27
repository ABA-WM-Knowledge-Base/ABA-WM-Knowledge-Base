---
id: world-model-kb.components.world-representation.predictive-embeddings
title: Predictive Embeddings as State
kind: component
status: maintained
last_updated: 2026-08-27
owners:
  - AIBuildAI world-model group
---

# Predictive Embeddings as State

## Retrieval metadata

**Relevant queries:** JEPA world state, reconstruction-free representation, V-JEPA 2 encoder as state, frozen ViT-g, action-free embedding, control-detail erasure.

**Knowledge provided:** What a predictive embedding retains or discards when used as world state, which V-JEPA 2 results speak to representation quality, and why planning results must not leak from V-JEPA 2-AC.

**Related pages:** [Representation learning and JEPA](../../foundations/representations/representation-learning-and-jepa.md) owns the objective family; [predictive representation and latent planning](../reasoning/predictive-representation-and-planning.md) owns CEM and 2-AC action grounding; [V-JEPA 2 Paper](../../papers/v-jepa-2/README.md) owns variant tables; [comparison and optimization](comparison-and-optimization.md) compares embeddings with reconstructive latents.

## Method definition

A predictive-embedding world state is a feature \(z_t = f_\theta(o_{\leq t})\) trained to predict another representation rather than pixels:

\[
z_x = f_\theta(x_{\text{context}}),\qquad
z_y = \operatorname{sg}(f_{\bar\theta}(y_{\text{target}})),\qquad
\hat z_y = g_\phi(z_x, m).
\]

No RGB decoder is required. The state is whatever information survives in \(z\) after the predictor can match target embeddings. Lighting and texture that are hard to predict may be dropped; small contacts and gripper-object geometry may be dropped as well. Abstraction is therefore not automatically decision-sufficient.

This page owns the representation: what \(z\) is, how it is trained without actions, and which probes measure it. Using \(z\) for latent planning is a reasoning method and remains on the Reasoning Component.

## V-JEPA 2: action-free video embeddings

V-JEPA 2 pretrains a video encoder and predictor with masked latent prediction on more than one million hours of video (VideoMix22M) and one million images. Visible spatiotemporal context passes through the context encoder; the predictor estimates EMA target-encoder embeddings. The largest reported model reached 77.3% on Something-Something-v2 and 39.7 recall@5 on Epic-Kitchens-100. PerceptionTest 84.0 uses an 8B LLM alignment and is not a frozen-encoder-only number. [OBJ-VJEPA2-2025; VJ2-PAPER, Secs. 3–4, Tables 1–2]

Scaling notes in the paper (data, model size, steps, resolution, and frame count to 88.2% on a reported cumulative path) support that the embedding improves under more compute. They do not show that the embedding contains a unified physical action interface, because pretraining is action-free. [VJ2-PAPER, Secs. 3–4]

V-JEPA 2.1 is a later in-tree recipe and must not inherit Table 2/3 numbers. [VJ2-CODE]

## What the embedding is not

V-JEPA 2-AC freezes ViT-g (\(16\times 16\times 1408\) at 256 px) and trains an action-conditioned next-\(z\) predictor on fewer than 62 hours of DROID. Robot CEM success is evidence about that post-trained predictor and planner, not about the action-free embedding alone. Table 3's Cosmos video-WM baseline is an external planner comparison, not a Generator-pixel result for Nano. [VJ2-PAPER, Secs. 3–5, Tables 2–3]

Do not treat a linear probe or SSv2 score as proof of forward dynamics. Do not treat latent-action quantization from unlabeled video (LAPA) as this method; that is an action code, not a world embedding.

## Controllable surfaces

| Surface | Mechanism | Expected observable | Main confounder |
|---|---|---|---|
| Mask geometry and duration | what must be predicted | motion versus static shortcuts | camera and background cues |
| Target EMA rate | stability versus lag | downstream probe after freeze | encoder jointly finetuned |
| Feature dimension / patch size | spatial granularity | small-object and contact probes | compute and video length |
| Action-free versus AC data | whether \(z\) sees interventions | action-conditioned latent error | unfreezing the encoder |
| Probe task | what \(z\) linearly contains | classification versus control | probe capacity |

## Evaluation and failure diagnosis

| Symptom | Plausible cause | Discriminating evidence |
|---|---|---|
| Strong SSv2, failed robot | missing action and contact detail | frozen versus AC comparison |
| Collapse to low-rank \(z\) | weak variance or shortcut | feature rank and mask difficulty |
| Probe success, planning fail | separable features, no dynamics | next-\(z\) error under actions |
| 2 and 2-AC numbers mixed | variant leakage | bind every cell to the variant |
| LLM-aligned score used as encoder quality | extra language stack | report frozen-only probes |

## Cosmos3-Nano connection

A predictive embedding is a candidate Reasoner visual state, not a Generator denoising state. A testable hypothesis is that an auxiliary future-feature loss on Reasoner visual tokens improves physical probes without replacing rectified-flow generation. Exact Reasoner objectives remain on [reasoner.md](../../models/cosmos3-nano/reasoner.md) and [training.md](../../models/cosmos3-nano/training.md). Reduced DROID data need after a frozen encoder is a 2-AC result, not a Nano measurement.

## Sources

- [OBJ-VJEPA2-2025] and [VJ2-PAPER] identify V-JEPA 2 representation evidence.
- [VJ2-CODE] identifies the 2 / 2-AC / 2.1 implementation split.
