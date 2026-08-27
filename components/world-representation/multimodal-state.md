---
id: world-model-kb.components.world-representation.multimodal-state
title: Multimodal State
kind: component
status: maintained
last_updated: 2026-08-27
owners:
  - AIBuildAI world-model group
---

# Multimodal State

## Retrieval metadata

**Relevant queries:** multimodal world state, AR semantic tokens versus diffusion latents, Cosmos3-Nano state streams, X-WAM RGB-D state, language is not world state, heterogeneous latent.

**Knowledge provided:** How systems keep several non-equivalent state streams, which stream is executable world state, and why Reasoner text is not a substitute for Generator or WAM latents.

**Related pages:** [Cosmos3-Nano architecture](../../models/cosmos3-nano/architecture.md) owns Nano token layouts; [reasoning–generation–action integration](../reasoning/reasoning-generation-action.md) owns directional coupling; [joint multimodal dynamics](../dynamics-modeling/joint-multimodal-dynamics.md) owns joint transitions; [X-WAM Paper](../../papers/x-wam/README.md) and [X-WAM Model](../../models/x-wam/README.md) own RGB-D/state artifacts.

## Method definition

A multimodal world state is a tuple of typed streams that are not interchangeable:

\[
s_t = (s_t^{\text{sem}}, s_t^{\text{vis}}, s_t^{\text{act}}, s_t^{\text{prop}}, \ldots).
\]

Each stream has its own encoder, loss, and admissible reader. Concatenating names in one checkpoint does not create a single sufficient statistic. The representation questions are: which stream may attend to which other stream, which stream is decoded to pixels or actions, and which measurement shows that information crossed the interface.

Language output from a Reasoner is a semantic description. It is not occupancy, not a video latent, and not a typed robot action. Treating a text plan as world state is an invalid equivalence.

## Cosmos3-Nano: paired AR and diffusion states

Cosmos3-Nano stores an approximately 8B autoregressive Reasoner tower and an approximately 8B diffusion Generator tower in one checkpoint. Autoregressive tokens represent language and ViT visual context. Diffusion subsequences represent VAE visual tokens, audio latents, action representations, and control conditions. Diffusion queries may attend to autoregressive context; autoregressive queries do not consume diffusion state in the same denoising pass. [C3-TR, pp. 9–14, Figures 4–6]

Consequences for representation:

- Reasoner hidden state is not Generator world state.
- Generator media latents are not Policy-DROID action chunks.
- Hosted `nvidia/cosmos3-nano-reasoner` is a Reasoner surface, not the unified state tensor.
- Super T2I/I2V checkpoints are specialist branches, not the base Nano state.

[C3-TR; C3-HF; C3-REASONER-COOKBOOK]

A reason–generate–inspect–revise loop that updated AR state from the current diffusion rollout would require an extra interface; the documented attention rule does not provide it. That coupling question is owned by Reasoning integration, not by claiming a unified state.

## X-WAM: RGB, depth, proprioception, and action as joint state

X-WAM predicts multi-view RGB, depth-like latents, proprioceptive state, and actions with one flow-matching DiT on Wan2.2-TI2V-5B. “4D” in the paper means time-varying multi-view RGB-D lifted with camera calibration and predicted end-effector pose. The network does not maintain a native persistent 3D scene representation. [XWAM-PAPER-V2; XWAM-CODE-72CF]

Policy mode early-stops state/action denoising with depth off and no video decode. Full world mode runs multi-view RGB-D/state/action generation. Those modes are different state surfaces. Pretrained, RoboCasa SFT, and RoboTwin SFT checkpoints are not interchangeable embodiments. [XWAM-HF-CHECKPOINTS]

X-WAM has no separate autoregressive reasoning tower. Language conditions generation; it does not implement Cosmos Reasoner state.

## DreamZero as a boundary, not a second Nano

DreamZero jointly denoises video and motor actions on Wan2.1 with embodiment-specific adapters (DROID versus AgiBot). The operational state includes views, language, and proprioception, but checkpoints are not a universal robot state. That system informs joint video–action representation; closed-loop policy claims belong to a future World Model–Policy Interface Component. [DZ-PAPER; DZ-HF-DROID; DZ-HF-AGIBOT]

## Controllable surfaces

| Surface | Mechanism | Expected observable | Main confounder |
|---|---|---|---|
| Which streams exist | typed I/O contract | missing-modality failures | loading the wrong tower |
| Attention direction | who can read whom | frozen-tower ablations | shared-checkpoint naming |
| Loss weights across streams | video dominating action/state | per-modality error | global FVD only |
| Policy versus world mode | which latents are decoded | latency versus RGB-D metrics | mixing checkpoint files |
| Embodiment adapter | camera/joint schema | cross-robot collapse | language-only transfer |

## Evaluation and failure diagnosis

| Symptom | Plausible cause | Discriminating evidence |
|---|---|---|
| Coherent text, wrong video | AR state unused by Generator | freeze Generator, swap AR context |
| Sharp video, dead actions | visual residual dominates | action-component error |
| RGB-D called persistent 3D | lifted depth, no scene memory | occluded-object persistence |
| Reasoner scores on WAM | surface leakage | bind tower and checkpoint |
| One SFT used on another robot | embodiment state mismatch | adapter YAML and joint layout |

## Cosmos3-Nano connection

This method is already Nano's native representation split. Transfer tests should name the stream under change (Reasoner tokens, visual VAE tokens, action latents) and keep the other stream's revision fixed. Exact serving IDs and mode flags remain in [manifest.yaml](../../models/cosmos3-nano/manifest.yaml) and [modalities-and-io.md](../../models/cosmos3-nano/modalities-and-io.md).

## Sources

- [C3-TR], [C3-HF], and [C3-REASONER-COOKBOOK] identify Nano stream identities.
- [XWAM-PAPER-V2], [XWAM-CODE-72CF], and [XWAM-HF-CHECKPOINTS] identify X-WAM RGB-D/state surfaces.
- [DZ-PAPER], [DZ-HF-DROID], and [DZ-HF-AGIBOT] identify embodiment-specific joint video–action state.
