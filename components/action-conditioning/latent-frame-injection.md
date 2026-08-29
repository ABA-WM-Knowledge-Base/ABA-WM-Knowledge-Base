---
id: world-model-kb.components.action-conditioning.latent-frame-injection
title: Latent-Frame Injection
kind: component
status: draft
last_updated: 2026-08-20
owners:
  - AIBuildAI world-model group
---

# Latent-Frame Injection

## Retrieval metadata

**Relevant queries:** actions as latent frames, robot modality injection, video diffusion policy, proprioception conditioning, value prediction in video latents, Cosmos Policy action representation.

**Knowledge provided:** The mechanism that represents low-dimensional robot modalities as latent frames inside a pretrained video diffusion sequence, its normalization contract, its training-mix evidence, and its measured limits.

**Related pages:** [Joint denoising and schedules](joint-denoising-and-schedules.md) owns the noise-timestep choices for such sequences; [future-prediction coupling](future-prediction-coupling.md) owns the auxiliary-supervision evidence; the [Cosmos Policy Paper entry](../../papers/cosmos-policy/README.md) owns full system details.

## Mechanism

Cosmos Policy fully fine-tunes a pretrained latent video diffusion model while representing every robot modality as additional latent frames, with no architectural changes [P25-COSMOS-POLICY, pp. 1-5]:

- Robot proprioception, action chunks, future proprioception, future multi-view images, and values are interleaved into the video latent sequence [P25-COSMOS-POLICY, pp. 4-5].
- Low-dimensional modalities are normalized to [-1, 1], flattened, and duplicated to fill latent volumes, then learned through the unchanged denoising objective [P25-COSMOS-POLICY, pp. 5, 15].
- The ordered sequence represents (s, a, s', V(s')); observations enter only at times t and t+K, with no input history [P25-COSMOS-POLICY, p. 5].

The design premise is that a pretrained video model's spatiotemporal prior transfers to action prediction if actions are made to look like the data the model already models.

## Training-mix evidence

Initial training splits every batch 50/25/25 among policy, world-model, and value-function objectives; the optional rollout-refinement stage changes the mix to 10/45/45 before best-of-N planning [P25-COSMOS-POLICY, pp. 5-6, 20-21].

Under this representation the model reaches 67.1% average RoboCasa success over the 3,600-trial protocol with 50 demonstrations per task [P25-COSMOS-POLICY, pp. 7-8]. The auxiliary-supervision ablation that carries a third of that number is owned by [future-prediction coupling](future-prediction-coupling.md).

## Contract and limits

- The injection contract (normalization ranges, flattening order, duplication factor) is part of the model identity; a checkpoint cannot be evaluated without it.
- No input history: the representation sees only the current and the K-step-ahead state. Partially observed tasks have no mechanism to disambiguate [P25-COSMOS-POLICY, p. 5].
- Planning over this representation costs about five seconds per action chunk with a one-layer search, which bounds its use for dynamic manipulation [P25-COSMOS-POLICY, p. 11].
- This is generator-line evidence (Predict2 base, no reasoner tower); it cannot be cited as reasoner evidence [P25-COSMOS-POLICY, pp. 1-3].

## Sources

- [P25-COSMOS-POLICY] identifies the Cosmos Policy paper; it resolves through the Cosmos Policy entry's registry.
