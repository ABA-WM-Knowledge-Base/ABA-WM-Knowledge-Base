---
id: world-model-kb.models.x-wam
title: X-WAM Agent Knowledge Entry
kind: model
status: maintained
last_updated: 2026-08-24
owners:
  - AIBuildAI world-model group
---

# X-WAM Agent Knowledge Entry

## Retrieval metadata

**Relevant queries:** X-WAM checkpoint, architecture, RGB-D world prediction, policy inference, action representation, ANS, data, training, RoboCasa, RoboTwin, evaluation, reproduction, or optimization.

**Knowledge provided:** released model and artifact identities, implementation and interface contracts, public configs and datasets, protocol-bound results, execution state, and model-specific optimization levers.

**Related pages:** [`agent-index.yaml`](agent-index.yaml) provides advisory query associations; [`manifest.yaml`](manifest.yaml) fixes artifact and dependency revisions. The [X-WAM Paper entry](../../papers/x-wam/README.md) owns the proposed method and reported experiments. [Original RoboCasa](../../benchmarks/robocasa/README.md) owns benchmark semantics.

## Identity constraints

| Object | Correct identity | Invalid inference |
|---|---|---|
| X-WAM pretrained checkpoint | Cross-embodiment checkpoint trained before benchmark SFT | That it equals the RoboCasa or RoboTwin policy checkpoint |
| X-WAM RoboCasa SFT | Single-arm Original RoboCasa 24-task adapter/config and state file | RoboCasa365 compatibility or zero-shot RoboTwin control |
| X-WAM RoboTwin SFT | Dual-arm RoboTwin 2.0 adapter/config and state file | Single-arm RoboCasa action semantics |
| Wan2.2-TI2V-5B | Upstream visual base required in addition to X-WAM state | A self-contained X-WAM checkpoint download |
| Policy mode | Early-stopped state/action denoising with depth off and no video decode | Proof that RGB-D generation executed |
| Full world mode | 50-step multi-view RGB-D/state/action generation | A native persistent 3D simulator or safety-certified rollout |

[XWAM-HF-CHECKPOINTS; XWAM-WAN22-HF; XWAM-CODE-72CF]

## Released artifact graph

```text
Wan2.2-TI2V-5B base + UMT5-XXL tokenizer/encoder + Wan VAE
                        |
              X-WAM architecture/state
                        |
          pretrained checkpoint (5,873.9 h paper corpus)
                 /                         \
      RoboCasa SFT                    RoboTwin SFT
  24 single-arm tasks              50 dual-arm tasks
        |                                  |
RoboCasa broker/server/client      RoboTwin broker/server/client
```

All three X-WAM state files are about 38.89 GB each. The public snapshot does not bundle the Wan base into those state files, and its configs point to a separate `wan_checkpoint_dir`. [XWAM-HF-CHECKPOINTS]

## Capability boundary

One conditioning RGB frame per view, one current state, and one instruction condition a nine-frame sequence containing eight future RGB/depth frames, nine states including the initial state, and 32 future actions. The main branch can produce actions after 10 denoising calls; full video uses 50. Depth is a copied late branch and is disabled by the released policy server. Training-time depth supervision may shape shared features, but policy inference does not consume predicted depth. [XWAM-PAPER-V2, pp.4-6, 17; XWAM-CODE-72CF]

## Knowledge map

| Owner | Knowledge |
|---|---|
| [Architecture](architecture.md) | Released block, token, depth, and noise-flow computation |
| [Modalities and I/O](modalities-and-io.md) | RGB, depth, language, state, action, camera, and normalization contracts |
| [Data and training](data-and-training.md) | Pretraining mixture, public SFT data, objectives, and config conflicts |
| [Inference](inference.md) | Checkpoint assembly, asynchronous sampling, and broker/server/client execution |
| [Evaluation](evaluation.md) | Checkpoint-bound policy and world-generation evidence |
| [Codebase](codebase.md) | Fixed symbol and configuration map |
| [Limitations](limitations.md) | Model, artifact, protocol, and deployment boundaries |
| [Reproduction](reproduction.md) | Executed-state registry and acceptance contracts |
| [Optimization playbook](optimization-playbook.md) | Controllable levers and falsifiable experiments |
| [Research queue](research-queue.md) | Unresolved questions that can change an implementation decision |

These pages provide knowledge that may ground AIBuildAI decisions. They do not choose Agents, repositories, task order, schedules, permissions, or external actions.

## Sources

Artifact identities resolve through [`sources.yaml`](sources.yaml); paper and code sources resolve through the [paper registry](../../papers/x-wam/sources.yaml).
