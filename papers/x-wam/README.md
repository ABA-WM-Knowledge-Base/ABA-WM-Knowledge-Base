---
id: world-model-kb.papers.x-wam
title: X-WAM Representative Paper Entry
kind: paper
status: maintained
last_updated: 2026-08-24
owners:
  - AIBuildAI world-model group
---

# X-WAM Representative Paper Entry

## Retrieval metadata

**Relevant queries:** X-WAM, Unified 4D World Action Modeling, multi-view RGB-D prediction, depth branch, unilateral attention, Asynchronous Noise Sampling, asynchronous denoising, Wan2.2-TI2V-5B, RoboCasa, RoboTwin 2.0, world action model, or policy latency.

**Knowledge provided:** the paper's formal model, architecture, learning objective, data, evaluation and ablations; its fixed code implementation; reproduction state; and falsifiable transfer hypotheses.

**Related pages:** [X-WAM Model](../../models/x-wam/README.md) owns released checkpoint, configuration, inference, and model-optimization facts. [Original RoboCasa](../../benchmarks/robocasa/README.md) owns the benchmark definition. Foundations own [world action models](../../foundations/definitions-and-taxonomy/world-action-model.md), [3D/4D world models](../../foundations/representations/3d-and-4d-world-model.md), [video world models](../../foundations/representations/video-world-model.md), and [diffusion/flow matching](../../foundations/learning-objectives/diffusion-and-flow-matching.md). Component method pages own [multimodal state](../../components/world-representation/multimodal-state.md) and [joint multimodal dynamics](../../components/dynamics-modeling/joint-multimodal-dynamics.md).

## Paper identity and scope

| Field | Fixed identity |
|---|---|
| Work | *Unified 4D World Action Modeling from Video Priors with Asynchronous Denoising* |
| Paper | `arXiv:2604.26694v2`, 7 May 2026, 21 pages |
| Official code | `sharinka0715/X-WAM`, commit `72cfb86b33fc5060963ef63412f16439fcfa472f` |
| Base video model | Wan2.2-TI2V-5B |
| Released model family | Pretrained, RoboCasa SFT, and RoboTwin SFT checkpoints |
| Core claim surface | Joint future RGB, depth, proprioceptive-state, and action generation with early action availability |

[XWAM-PAPER-V2; XWAM-CODE-72CF]

The paper calls X-WAM a unified 4D World Action Model because one flow-matching DiT predicts multi-view RGB-D futures, states, and actions. “4D” here means time-varying multi-view RGB-D outputs lifted into 3D using static camera calibration and predicted end-effector pose; the network does not natively evolve a persistent 3D scene representation. The official project page is the qualitative and artifact landing surface linked by the authors. [XWAM-PROJECT]

## Knowledge map

| File | Canonical paper-specific knowledge |
|---|---|
| [Paper](paper.md) | Problem, end-to-end architecture, equations, pretraining, evaluation, ablations, real deployment, and evidence limits |
| [Codebase](codebase.md) | Fixed implementation graph, tensor and call paths, submodule pins, and paper/release mismatches |
| [Reproduction](reproduction.md) | Source-inspection and execution state with acceptance contracts |
| [Optimization transfer](optimization-transfer.md) | Mechanism-grounded transfers to other WAMs and controlled tests |
| [`sources.yaml`](sources.yaml) | Paper, code, project, and pinned dependency identities |

## Canonical ownership boundary

This Paper entry owns what the work proposes and reports. The Model entry owns the concrete public snapshot: HF revisions, three large checkpoint files, released config values, supported broker/server/client runtime, and open execution questions. Where the paper and released artifacts disagree, [Codebase](codebase.md) records both; neither is silently chosen as the other's value.

## Evidence summary

The strongest paper result is 79.2% mean success across 24 RoboCasa manipulation tasks, versus 67.1% for the strongest listed baseline, and 89.8%/90.7% on RoboTwin 2.0 Clean/Randomized. The same paper reports superior RGB, depth, and point-cloud metrics. Its controlled depth/ANS ablations are fine-tuned directly from Wan2.2 without the 5,873.9-hour pretraining stage and reach 67.8%, so they support mechanism direction under that regime but do not decompose the final 79.2% checkpoint. [XWAM-PAPER-V2, pp.7-9, Tables 1-4]

## Sources

Paper-local sources resolve through [`sources.yaml`](sources.yaml). Released artifact identities resolve through the [X-WAM Model registry](../../models/x-wam/sources.yaml).
