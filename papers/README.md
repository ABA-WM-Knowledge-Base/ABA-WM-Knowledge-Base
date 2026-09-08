---
id: world-model-kb.papers
title: Representative Paper Entries
kind: index
status: maintained
last_updated: 2026-09-08
owners:
  - AIBuildAI world-model group
---

# Representative Paper Entries

## Retrieval metadata

**Relevant queries:** paper mechanism, ablation, benchmark result, implementation, reproduction, or transfer hypothesis.

**Knowledge provided:** the canonical Paper scope, its active entries, and the entry contract that converts one work into reusable optimization knowledge.

**Related pages:** [Foundations](../foundations/README.md) owns model-independent concepts and formalisms; [Models](../models/README.md) owns model-specific knowledge; [Components](../components/README.md) contains independently scoped component knowledge; [Benchmarks](../benchmarks/README.md) owns versioned evaluation systems. Individual paper entries connect mechanisms and transfer claims to the applicable owners without imposing a reading order.

## Canonical scope

Each paper entry reconstructs one work as reusable optimization knowledge. It separates the proposed mechanism, the implemented system, the reported experiments, the local reproduction state, and transfer hypotheses. The main `paper.md` follows the source paper's logical order when that makes the architecture and evidence easier to reconstruct, but it remains a claim-aware synthesis rather than a reading diary or paragraph-by-paragraph summary.

Paper-specific evidence remains canonical in its entry. When a mechanism, formal assumption, evaluation principle, or transfer claim depends on a model-independent concept, the entry links to that concept's Foundation page instead of redefining it. These links express knowledge ownership and dependencies; they do not prescribe task sequencing or AIBuildAI workflow orchestration.

The seven current Components synthesize representation, dynamics, reasoning, generation, fast-video-inference, action-conditioning, and world-model–policy-interface mechanisms across several Paper entries, but each source paper's exact architecture, protocol, results, code, and reproduction state remain canonical here. Future Components may declare a different scope.

## Active entries

| Paper entry | World-model family | Knowledge coverage |
|---|---|---|
| [Cosmos-Predict2.5](cosmos-predict2-5/README.md) | Video-based latent world foundation model | Flow-based video prediction, curation, conditional-frame curriculum, post-training, Transfer2.5 and specialist applications, implementation boundary, reproduction contract, and transferable interventions |
| [IRASim](irasim/README.md) | Action-conditioned visual forward model for robot manipulation | Trajectory-to-video diffusion, frame-level action alignment, failure-rollout data, policy evaluation, model-based planning, released-code boundary, and transferable interventions |
| [MimicGen](mimicgen/README.md) | Demonstration-generation system for imitation learning (data layer, not a world model) | Object-centric segment replay and transform, success-only acceptance and its measured initial-state bias, generation-rate/policy-success decoupling, selection-strategy ablations, released-code boundary, reproduction contract, and transferable curation interventions |
| [Cosmos Policy](cosmos-policy/README.md) | Video world model post-trained as a visuomotor policy | Predict2-2B latent-frame injection, joint policy/world-model/value training, LIBERO/RoboCasa/ALOHA, dual planning checkpoint, and the Predict2 versus Predict2.5 code-tree split |
| [DreamZero](dreamzero/README.md) | World action model | Joint video-action prediction evaluated as a closed-loop policy, DROID/AgiBot 14B checkpoints, and scoped zero-shot language |
| [LAPA](lapa/README.md) | Latent-action pretraining | Unlabeled-video latent-action quantization, remapping to robot actions, Open-X finetuning; not a Genie-style interactive environment generator |
| [iVideoGPT](ivideogpt/README.md) | Interactive autoregressive video world model | Compressive VQ plus GPT-style multimodal prediction on OXE, with results bound to named action-free versus action-conditioned checkpoints |
| [DreamerV3](dreamerv3/README.md) | Compact latent MBRL | Nature RSSM imagination agent, fixed-hyperparameter cross-domain evidence, and a public DreamerV2-based reimplementation boundary |
| [TD-MPC2](td-mpc2/README.md) | Decoder-free latent planning | Temporal-difference latent dynamics with MPPI, 104-task single-hyperparameter claims, and post-paper Q-ensemble initialization fixes |
| [V-JEPA 2](v-jepa-2/README.md) | Non-generative predictive representation | Strict separation of V-JEPA 2, 2-AC, and 2.1, plus latent-planning evidence that must not leak across variants |
| [DIAMOND](diamond/README.md) | Pixel-space diffusion world model | Atari 100k MBRL inside an image-space diffusion model, with the CSGO branch kept as a separate qualitative surface |
| [OccWorld](occworld/README.md) | 3D occupancy driving world model | Occupancy-token forecasting plus ego-trajectory prediction on nuScenes, including license and variant boundaries |
| [Vista](vista/README.md) | Controllable driving video world model | OpenDV control modes and official weights; not Wayve GAIA; high-VRAM sampling is not locally attempted |
| [X-WAM](x-wam/README.md) | Unified RGB-D world action model | Wan2.2-based multi-view RGB/depth/state/action denoising, copied depth branch, asynchronous noise scheduling and inference, cross-embodiment pretraining, RoboCasa/RoboTwin evidence, released-code boundary, and transferable interventions |
| [Xiaomi-Robotics-1](xiaomi-robotics-1/README.md) | Vision-language-action model | Qwen3-VL backbone, flow-matching DiT action head, heterogeneous robot pretraining, VLABench adaptation, and released implementation boundaries |
| [VLABench](vlabench/README.md) | Language-conditioned manipulation benchmark paper | Long-horizon task construction, evaluator and metric implementation, benchmark defects, and protocol constraints |
| [ERVLA](ervla/README.md) | Reasoning-augmented vision-language-action model | Embodied chain-of-thought, reasoning dropout, action generation, and reported robot evaluation |

An active entry is evidence about that named work, not a claim that its findings generalize to every model. Candidate families or titles are not KB facts until their entries exist.

## Entry contract

```text
papers/<paper-id>/
|-- README.md                    # Entrypoint, identity, and canonical owners
|-- paper.md                     # Method, architecture, training, experiments, and evidence limits
|-- codebase.md                  # Implementation graph and change surfaces
|-- reproduction.md              # Environment, commands, artifacts, failures, fixes
|-- optimization-transfer.md     # Transferable levers, Foundation links, and falsifiable adaptations
`-- sources.yaml                 # Pinned primary sources and artifact identities
```

An entry is useful to an optimization agent only if it answers all of the following:

1. What behavior or limitation is the method designed to change?
2. What causal mechanism and training signal are proposed?
3. Which implementation and data surfaces realize that mechanism?
4. Which ablations isolate the claimed source of improvement?
5. Under what assumptions, compute regime, and evaluation protocol do the results hold?
6. Which intervention can transfer to a target model, where would it attach, and what would falsify the transfer hypothesis?
7. What has actually been reproduced, with which artifacts and deviations?

Use the [representative paper entry template](../_schema/paper-entry-template.md) when an entry is activated.
