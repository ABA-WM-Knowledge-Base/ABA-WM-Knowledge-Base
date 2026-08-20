---
id: world-model-kb.components.action-conditioning.joint-denoising-and-schedules
title: Joint Denoising and Schedules
kind: component
status: draft
last_updated: 2026-08-20
owners:
  - AIBuildAI world-model group
---

# Joint Denoising and Schedules

## Retrieval metadata

**Relevant queries:** joint video action denoising, shared noise timestep, asynchronous noise sampling, action-first decoding, KV-cache observation replacement, world action model latency.

**Knowledge provided:** The schedule choices available when actions are a jointly denoised output modality, and the measured success and latency effects of synchronous versus asynchronous designs.

**Related pages:** [Latent-frame injection](latent-frame-injection.md) owns the modality representation; [diffusion modeling](../generative-modeling/diffusion.md) and [flow matching](../generative-modeling/flow-matching-and-rectified-flow.md) own the underlying objectives; the [DreamZero Paper entry](../../papers/dreamzero/README.md) owns full system details.

## Synchronous joint denoising

DreamZero jointly predicts future video and actions with shared video/action denoising timesteps and chunk-wise teacher forcing; the design decomposes as autoregressive video prediction plus an implicit inverse-dynamics model [DZ-PAPER, pp. 6-7]. X-WAM places RGB, state, and action latents in one bidirectionally attended denoising sequence [COMP-ACT-XWAM-2026, p. 5].

Synchronous schedules are the simplest contract, but they force actions to wait for the full video denoising budget at inference.

## Asynchronous scheduling

X-WAM's Asynchronous Noise Sampling trains with video noise timestep t_O greater than or equal to the action timestep t_a, matching an inference regime where actions finish denoising before video. In the benchmark-only ablation this raises RoboCasa success from 66.4% to 67.8% and cuts action-chunk latency from 4,665 ms to 1,033 ms [COMP-ACT-XWAM-2026, pp. 6, 9, 17]. Benchmark inference then uses 10 action denoising steps against 50 video steps [COMP-ACT-XWAM-2026, p. 18].

The transferable principle: when actions and video share one denoising process, the noise schedule is an interface decision, not a training detail. Train-test schedule mismatch is a silent correctness risk, and the schedule directly sets control latency.

## Closed-loop context replacement

DreamZero replaces generated frames with executed observations in the KV cache during closed-loop execution, limiting autoregressive error accumulation at the action-video boundary [DZ-PAPER, p. 8]. This is the joint-denoising counterpart of replanning: the model's own futures are used for decoding, but reality re-anchors the context.

## Boundary notes

- X-WAM's headline 79.2% RoboCasa result confounds this mechanism with 1.49M-episode pretraining; the schedule effect is only isolated in the benchmark-only ablation cited above [COMP-ACT-XWAM-2026, pp. 7, 9, 16].
- DreamZero's 7 Hz control rate requires two GB200 GPUs [DZ-PAPER, p. 18]; schedule improvements do not remove the underlying generation cost, which is owned by the [WM-policy interface Component](../wm-policy-interface/deployment-boundaries.md).

## Sources

- [DZ-PAPER] identifies DreamZero; it resolves through the DreamZero entry's registry.
- [COMP-ACT-XWAM-2026] identifies X-WAM; it resolves through the local [source registry](sources.yaml).
