---
id: world-model-kb.components.wm-policy-interface.offline-synthetic-trajectories
title: Offline Synthetic Trajectories
kind: component
status: draft
last_updated: 2026-08-20
owners:
  - AIBuildAI world-model group
---

# Offline Synthetic Trajectories

## Retrieval metadata

**Relevant queries:** neural trajectories, synthetic robot training data, world model data generation, DreamGen pipeline, latent trajectory transfer, generated data filtering.

**Knowledge provided:** The consumption mode that turns world-model rollouts into offline policy-training data: pipeline shapes, measured gains and compute costs, the pixel-versus-latent transfer evidence, and the curation step every verified pipeline omits.

**Related pages:** [Latent and pseudo-actions](../action-conditioning/latent-and-pseudo-actions.md) owns the action-labeling step; [data curation and filtering](../../foundations/data-and-evaluation/data-curation-and-filtering.md) owns the selection operator this mode is missing; [MimicGen](../../papers/mimicgen/README.md) owns the replay-based generation precedent and its measured coverage cost.

## Pipeline shape and measured gains

DreamGen is the largest verified instance: LoRA-finetune an image-to-video model on the target embodiment, generate videos from randomized initial frames and language instructions, infer pseudo-actions, then train policies on the result [DATA-DREAMGEN-2025, pp. 3-4]. At 300 real demonstrations per task, 240,000 neural trajectories raise GR00T N1 average RoboCasa success from 49.59% to 57.61%; synthetic-only training reaches 20.55% [DATA-DREAMGEN-2025, p. 17].

The cost side: generating the 240k RoboCasa set took 54 hours on 1,500 L40 GPUs, and initial frames were manually supplied [DATA-DREAMGEN-2025, pp. 9-10].

## Pixel versus latent transfer

World2Act transfers imagined trajectories as pre-decoding video-VAE latents through lightweight adapters instead of decoded pixels; decoding first raises pseudo-action MSE by 18% and MAE by 19% in its LIBERO measurement. The latent route lifts GR00T-N1.6 from 70.1% to 72.6% on its RoboCasa protocol, versus 70.5% for the DreamGen-style baseline [COMP-WPI-WORLD2ACT-2026, pp. 3-6, 25].

Caution: RoboCasa numbers in this mode are not cross-comparable. World2Act evaluates 50 trials per task over 5 seeds, a different protocol from both the Cosmos Policy three-seed and the X-WAM 100-episode conventions [COMP-WPI-WORLD2ACT-2026, p. 5].

## The missing curation step

Neither verified pipeline selects among its generated trajectories. DreamGen reports no rejection step anywhere and names generated-trajectory quality as its bottleneck [DATA-DREAMGEN-2025, pp. 2-4, 15]. World2Act reports no score or predicate over its roughly 3,000 imagined trajectories (its LLM-based cleaning acts on source demonstrations before world-model training, which is a different operator) [COMP-WPI-WORLD2ACT-2026, pp. 5, 20-21].

The consequences of adding a selection operator naively, and the stratification repair, are owned by [data curation and filtering](../../foundations/data-and-evaluation/data-curation-and-filtering.md). MimicGen's success-only acceptance is the measured precedent for what a single acceptance predicate costs in state-space coverage [MIMICGEN-PAPER-V1].

## Sources

- [DATA-DREAMGEN-2025] identifies DreamGen; it resolves through the foundations registry.
- [COMP-WPI-WORLD2ACT-2026] identifies World2Act; it resolves through the local [source registry](sources.yaml).
- [MIMICGEN-PAPER-V1] identifies MimicGen; it resolves through the MimicGen entry's registry.
