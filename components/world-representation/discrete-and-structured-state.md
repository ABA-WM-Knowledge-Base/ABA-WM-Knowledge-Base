---
id: world-model-kb.components.world-representation.discrete-and-structured-state
title: Discrete and Structured State
kind: component
status: maintained
last_updated: 2026-08-27
owners:
  - AIBuildAI world-model group
---

# Discrete and Structured State

## Retrieval metadata

**Relevant queries:** VQ world-model state, occupancy token, iVideoGPT compressive tokenizer, OccWorld VQ-VAE, codebook collapse, reconstruction versus forecast.

**Knowledge provided:** How discrete tokens and geometric occupancy codes serve as world state, which tokenizer ablations change forecasting rather than reconstruction, and where object-centric evidence is still a gap.

**Related pages:** [Latent world models](../../foundations/representations/latent-world-model.md) owns discrete-latent formalism; [3D and 4D world models](../../foundations/representations/3d-and-4d-world-model.md) owns geometric state; [structured occupancy dynamics](../dynamics-modeling/structured-occupancy-dynamics.md) owns occupancy forecasting; [autoregressive generation](../generative-modeling/autoregressive.md) owns GPT-style token dynamics.

## Method definition

A discrete or structured world state replaces a continuous vector with a codebook or a geometrically typed grid:

\[
z_t = \operatorname{Quantize}(e_\theta(o_t)) \in \{1,\ldots,K\}^{N},
\]

or, for occupancy,

\[
z_t = \operatorname{VQ}(\operatorname{occ}_t) \in \{1,\ldots,K\}^{H\times W}.
\]

The representation claim is that the codes preserve the entities the transition and planner need: objects, free space, semantics, or ego pose. Reconstruction of the tokenizer input is not the same claim as useful multi-step state.

Object-centric slot or keypoint states are a neighboring family. Current Paper entries do not supply a peer-reviewed object-centric world-model table at IRASim depth, so that family is recorded as a gap rather than a third instantiated method.

## iVideoGPT: compressive VQ as video state

iVideoGPT encodes context frames with \(E_c\) and future frames with a 4x4-bottleneck \(E_p\) that cross-attends to context, then models tokens with a LLaMA-style transformer. The tokenizer plus transformer is the state interface for video prediction. Action-free OXE pretraining (for example `thuml/ivideogpt-oxe-64-act-free`) is not an action-conditioned state. Heterogeneous Open-X action spaces are why pretraining remains action-free. [IVG-PAPER; IVG-HF-OXE-64-ACT-FREE]

On BAIR, named action-conditioned variants change FVD from 75.0 to 60.8 under the paper tables. That supports adding action information to an already tokenized video state in that setting. It does not make the OXE tokenizer a universal robot state, and RLVR-World is a later separate paper. [IVG-PAPER, Tables 1–2]

Public 256x256 RoboNet checkpoints were deleted; paper Table 1 256 numbers remain paper evidence, not a Hub-reproducible state. [IVG-CODE]

## OccWorld: occupancy tokens as driving state

OccWorld tokenizes semantic 3D occupancy with a VQ-VAE (default \((50^2, 128, 512)\)) and treats those tokens as the scene state for forecasting and planning. OccWorld-O uses occupancy ground truth; it is not unlabeled video. OccWorld-S is camera-only and is a negative control (forecast mIoU 0.26), not an occupancy world model. [OCCSRC-PAPER, Tables 1–2]

Tokenizer Table 3 is the representation result: \((100^2, 128, 512)\) raises reconstruction mIoU to 78.12 but lowers forecast mIoU to 12.38 versus 17.14 for the default code. A 1024-way codebook overfits. Reconstruction-maximizing state is therefore not the forecasting-maximizing state. [OCCSRC-PAPER, Table 3]

nuScenes, Occ3D, and Tsinghua pickle licenses gate local execution. Variant letters O/D/T/S must stay bound to their input supervision. [OCCSRC-NUSCENES; OCCSRC-PAPER]

## Invalid equivalences

- Discrete video tokens are not occupancy tokens.
- Occupancy GT tokens are not camera-only scene understanding.
- VQ world state is not latent-action quantization (LAPA).
- X-WAM RGB-D latents are continuous multimodal state, not this codebook method; see [multimodal state](multimodal-state.md).

## Controllable surfaces

| Surface | Mechanism | Expected observable | Main confounder |
|---|---|---|---|
| Spatial grid / bottleneck | what geometry fits in \(N\) codes | small-object and lane retention | extra transformer length |
| Codebook size \(K\) | capacity versus collapse | usage entropy and forecast | recon-only selection |
| Semantic versus geometry labels | which classes occupy the code | class-wise IoU | GT occupancy leakage |
| Context-conditioned tokenizer | whether \(E_p\) sees history | identity across time | copied pixels |
| Two-stage train | freeze tokenizer then forecast | Table 3 versus Table 1 | joint finetune of both |

## Evaluation and failure diagnosis

| Symptom | Plausible cause | Discriminating evidence |
|---|---|---|
| High recon, low forecast | tokenizer selected on appearance | hold recon, change forecast loss |
| Codebook collapse | unused entries | usage histogram |
| OccWorld-O scores on camera model | variant leakage | bind O/D/T/S |
| Token WM called 3D | decoded RGB only | occupancy or depth metrics |
| Object-centric claim without slots | naming | require entity-level probes |

## Cosmos3-Nano connection

Nano does not publish an OccWorld-style occupancy codebook as Generator state. A parallel geometric head beside video latents is a transfer hypothesis in the OccWorld Paper entry, not an implemented Nano component. iVideoGPT-style compressive tokens are also not Nano's VAE visual tokens. Do not substitute one discrete state for the other. [OCCSRC-PAPER; C3-TR, pp. 9–14]

## Sources

- [IVG-PAPER] and [IVG-HF-OXE-64-ACT-FREE] identify iVideoGPT token state and checkpoint scope.
- [OCCSRC-PAPER] and [OCCSRC-NUSCENES] identify occupancy-token state, Table 3, and the license gate.
- [REP-VQVAE-2017] identifies the discrete VQ mechanism family used by both tokenizers.
