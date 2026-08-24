---
id: world-model-kb.models.x-wam.architecture
title: X-WAM Released Architecture
kind: model
status: maintained
last_updated: 2026-08-24
owners:
  - AIBuildAI world-model group
---

# X-WAM Released Architecture

## Retrieval metadata

**Relevant queries:** X-WAM architecture, Wan2.2 backbone, token sequence, view embedding, depth branch, extra blocks, unilateral attention, flow matching, parameter initialization, or branch-off policy mode.

**Knowledge provided:** the concrete released computation graph, parameter groups, information-flow asymmetry, and architecture levers whose effects can be tested without confusing them with data or protocol changes.

**Related pages:** The [Paper method](../../papers/x-wam/paper.md) owns equations and experiments; [modalities and I/O](modalities-and-io.md) owns shapes; [codebase](codebase.md) maps symbols; [optimization playbook](optimization-playbook.md) owns model-specific experiments.

## Backbone and parameter groups

`XWAMModel` is a 32-block, hidden-size 2,048, 16-head DiT initialized from Wan2.2-TI2V-5B. Its main video path retains a 3D convolutional patch embedder, 3D RoPE, UMT5 context projection, Transformer blocks, and a video head. X-WAM adds learned view embeddings, action and state MLP encoders/decoders, per-token modality timesteps, and one extra depth branch consisting of copies of the final 10 main blocks plus a separate head. [XWAM-CODE-72CF, `modules/wan_model.py::XWAMModel`; XWAM-HF-CHECKPOINTS]

The public model snapshot does not state a post-modification total parameter count. “5B” identifies the Wan base, not the exact X-WAM parameter total after copying 10 blocks. Parameter reporting should therefore use “Wan2.2-TI2V-5B base plus the released X-WAM additions” unless measured from the loaded state.

## Unified main sequence

Video latents are patchified per view and rearranged into frame-major view/spatial order. Learned view embeddings mark camera identity. Action and proprioceptive vectors pass through two-layer MLP encoders. The model concatenates video, action, and state tokens, constructs compatible temporal/spatial frequency embeddings, adds independent video and action/state timestep embeddings, and processes the sequence with full bidirectional self-attention plus text cross-attention. [XWAM-CODE-72CF, `XWAMModel._forward_single`]

```text
video tokens [T × V × H' × W']
  + action tokens [32]
  + state tokens [9]
  -> one attention sequence
  -> split by original lengths
  -> video head, action MLP decoder, state MLP decoder
```

The conditioning video frame and initial state are copied into noisy tensors with masks and remain clean. Future video, state, and action begin from noise at inference. Full attention allows generated modalities to exchange information during the joint phase; this is not a causal autoregressive rollout.

## Depth information flow

When `run_depth=True`, the first 22 blocks are shared. The hidden video portion initializes the depth stream. For each of the final 10 layers, the main block produces a key/value cache while updating the full main sequence; the corresponding copied depth block updates depth tokens while reading that main cache. Main queries never attend to depth keys/values in those layers. A separate head predicts depth-latent output. [XWAM-CODE-72CF, `XWAMModel._forward_single`]

`init_from_wan_checkpoint` copies the original final main-block weights into each depth block, giving a visual prior before geometry post-training. The main branch can execute all 32 blocks without allocating depth computation when `run_depth=False`. Policy serving uses that path.

The asymmetry has two optimization consequences. First, direct depth-output changes can be localized to copied blocks and head, but depth loss can still update shared blocks unless frozen. Second, action benefits cannot come from reading predicted depth at inference; they must come from training-induced shared representation changes or correlated data/optimization effects.

## Noise and objective architecture

Video and action/state share the model but receive different timestep sequences. Training supports synchronous sampling, independent decoupled sampling, and the released joint ANS mixture through `use_decoupled_sampling`, `use_joint_distribution`, and `clean_action_ratio`. Inference maintains separate UniPC schedulers and can stop action/state before video. This schedule is part of the model's functional architecture because it determines which noisy joint states the network visits. [XWAM-CODE-72CF, `runners/xwam_runner.py`]

The default objective sums video, action, state, and depth MSE terms at unit weights. An optional frequency-domain DCT-like action loss is implemented through an FFT difference but has default weight `0.0`; it is an available code surface, not part of the reported baseline. [XWAM-CODE-72CF, `XWAMRunner.training_step`]

## Architecture levers and confounders

| Lever | Direct surface | Primary measure | Required regression |
|---|---|---|---|
| `num_extra_layers` | copied blocks and depth compute | depth/point-cloud metrics, precision-task success | parameter count, memory, RGB/action quality |
| Freeze/shared gradient policy | optimizer parameter groups | action benefit attributable to shared geometry learning | depth accuracy and convergence |
| Depth-to-main connectivity | attention graph | policy success and geometric consistency | pretrained RGB fidelity, latency |
| View embedding and view shuffle | embedding/data loader | cross-view robustness | calibrated fixed-order baseline |
| Action/state token placement | sequence construction and RoPE | action error and success | video quality and compute |
| Main/depth branch disable | `run_depth` | policy latency and output equality | full generation remains valid |

Changing layer count also changes parameter count; changing concatenation changes sequence cost; changing connectivity can destroy the main pretrained manifold. Controls must distinguish geometry information from capacity and compute.

## Sources

Architecture is grounded in `XWAM-CODE-72CF` and `XWAM-PAPER-V2`; artifact configuration uses `XWAM-HF-CHECKPOINTS`.
