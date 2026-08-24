---
id: world-model-kb.models.x-wam.inference
title: X-WAM Inference and Serving Semantics
kind: model
status: maintained
last_updated: 2026-08-24
owners:
  - AIBuildAI world-model group
---

# X-WAM Inference and Serving Semantics

## Retrieval metadata

**Relevant queries:** run X-WAM, load checkpoint, action-only inference, full RGB-D generation, asynchronous denoising, early stop, policy server, broker, client, CFG, latency, memory, or sampling steps.

**Knowledge provided:** checkpoint assembly, mode-specific sampling behavior, public serving topology, effective configuration surfaces, and the evidence required to distinguish a load test, open-loop output, and closed-loop policy run.

**Related pages:** [Modalities and I/O](modalities-and-io.md) owns tensor and adapter semantics; [codebase](codebase.md) maps the runtime symbols; [reproduction](reproduction.md) records what has actually run; [Original RoboCasa protocol](../../benchmarks/robocasa/protocol-and-metrics.md) owns benchmark evaluation semantics.

## Checkpoint assembly

An X-WAM state file is not a standalone model directory. The released runner expects:

1. the official X-WAM source tree at the fixed commit;
2. the original-format Wan2.2-TI2V-5B directory for base model structure, VAE, and text-encoder assets;
3. one X-WAM DeepSpeed-style model-state file;
4. the matching serialized X-WAM config and normalization statistics;
5. benchmark-specific simulator submodules and adapter code for closed-loop control.

The pinned identities are in [`manifest.yaml`](manifest.yaml). The public state files are each about 38.89 GB, before the separate Wan assets and runtime allocations. Disk availability, host RAM, GPU memory, transfer time, and file integrity should be assessed independently. [XWAM-HF-CHECKPOINTS; XWAM-WAN22-HF; XWAM-CODE-72CF]

`XWAMRunner` constructs `XWAMModel`, Wan VAE/text components, independent video and action schedulers, and decoding utilities. Configuration precedence matters: serialized checkpoint configuration, selected YAML, command-line overrides, and hard-coded evaluation defaults can disagree. A reproducible invocation retains the fully resolved configuration after all overrides rather than only a shell command. [XWAM-CODE-72CF, `runners/xwam_runner.py`, `scripts/train_sft.py`]

## Sampling state machine

Inference begins with one clean RGB frame per view and one clean state. Future video, future state, and all action slots are initialized from noise. Video and action/state have separate scheduler indices.

```text
condition frame + condition state + language
                 |
        joint denoising calls
          /              \
 action/state complete   video still noisy
          |                    |
 decode 32 actions       optionally continue video
          |                    |
 policy early stop       RGB and optional depth decode
```

The released policy path uses 10 action steps, stops before completing the 50-step video schedule, disables the depth branch, and decodes actions/states without VAE video output. The full world-prediction path continues video denoising, can hold decoded action/state clean, runs depth when requested, and decodes future RGB-D. Therefore, policy latency cannot be used as full RGB-D generation latency, and a successful action response does not test the depth head or VAE decoder. [XWAM-PAPER-V2, pp.5-6; XWAM-CODE-72CF, `XWAMRunner.inference`]

## Classifier-free guidance semantics

The paper reports classifier-free guidance scale 1. The released code's default `cfg_scale=0` uses one conditional pass, whereas a nonzero value computes conditional and unconditional passes and combines them. At scale 1, the combination reduces to the conditional prediction, so `0` and `1` are intended to produce the same conditional estimate while `0` avoids duplicate compute. This is a code-semantic equivalence, not proof of bitwise equality under every distributed or mixed-precision runtime. Values above 1 change both output and model-call cost. [XWAM-PAPER-V2, p.17; XWAM-CODE-72CF, `XWAMRunner`]

## Public serving topology

The repository separates model execution from simulator processes:

```text
environment client <-> message broker <-> policy server <-> X-WAM runner
```

RoboCasa and RoboTwin clients format observations, send them through the broker, receive a 32-step canonical action chunk, transform it back into environment coordinates, and execute a configured portion before replanning. The server owns checkpoint loading, image/state preprocessing, instruction embedding, inference, denormalization, and response serialization. [XWAM-CODE-72CF, `evaluation/`]

This topology is useful for isolating GPU state and simulator dependencies, but it introduces protocol and timing variables. Broker address, ports, request identifiers, timeouts, action age, queueing, retry behavior, environment step rate, and actions executed per prediction must be captured for a closed-loop result. A server response with a valid shape is an open-loop interface observation, not task success.

## Mode contracts

| Claim surface | Minimum execution | Required retained evidence |
|---|---|---|
| importable implementation | import fixed source and dependencies | revisions, environment lock, import output |
| checkpoint load | assemble Wan and X-WAM assets and restore state | resolved paths/revisions, missing/unexpected keys, device/precision, peak memory |
| action-only inference | fixed RGB/state/language fixture through early-stop path | exact fixture, normalized inputs, raw and denormalized actions, step count, seed, latency |
| full world prediction | run all video steps with depth enabled and decode outputs | RGB-D/state/action tensors, media, scheduler trace, VAE/depth settings, resources |
| RoboCasa rollout | compatible simulator client and fixed Original RoboCasa protocol | task/config/seeds, adapter trace, actions executed, videos, success and failure labels |

Each higher row depends on lower-level contracts but adds new evidence. A media sample does not establish policy control, and a rollout does not establish benchmark comparability unless its evaluation contract matches.

## Determinism and measurement

Record Python, PyTorch, CUDA, driver, attention kernel, DeepSpeed, precision, GPU topology, and random seeds. Separate first-load time, warm inference latency, model-call count, VAE decode time, broker overhead, and simulator time. For asynchronous denoising, report both action-decision latency and full-generation latency. Peak allocated, reserved, and device-reported memory answer different questions and should not be merged into one number.

Numerical checks should include finite tensors, condition-mask preservation, action/state mask adherence, valid denormalization, gripper sign, and identical shape/order at each network boundary. A deterministic golden fixture is preferable to an ad hoc live observation for diagnosing loading or preprocessing changes.

## Resource boundary

The release supplies multi-GPU-oriented training code and large model artifacts but does not publish a universal minimum inference-VRAM figure. Hardware feasibility must be measured for the chosen mode, precision, attention backend, parallelism, image dimensions, view count, and decoding path. The paper's 1,033 ms action latency is a reported experimental value under its setup, not a portable service-level guarantee. [XWAM-PAPER-V2, Table 4]

## Sources

Runtime facts use `XWAM-CODE-72CF`, `XWAM-PAPER-V2`, `XWAM-HF-CHECKPOINTS`, and `XWAM-WAN22-HF`.
