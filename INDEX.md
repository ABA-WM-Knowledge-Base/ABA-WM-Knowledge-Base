---
id: world-model-kb.index
title: Knowledge Base Topic Index
kind: index
status: maintained
last_updated: 2026-08-19
owners:
  - AIBuildAI world-model group
---

# Knowledge Base Topic Index

This index is a non-exclusive topic map. AIBuildAI may retrieve from multiple content areas for the same task and use the resulting knowledge to ground reasoning and strategy. The index does not prescribe Agent selection, repository selection, task order, execution scheduling, permissions, or external actions.

## Content areas

| Knowledge area | Entry point | Current scope |
|---|---|---|
| Model-independent concepts | [Foundations](foundations/README.md) | Active; eight semantic subparts and advisory retrieval metadata |
| Representative methods and papers | [Papers](papers/README.md) | Thirteen active entries spanning video WM, WAM, latent-action, MBRL, JEPA, occupancy, and driving |
| Cross-paper capability evolution | [Components](components/README.md) | Reasoning and Generative Modeling |
| Cosmos3-Nano model knowledge | [Cosmos3-Nano](models/cosmos3-nano/README.md) | Active model entry |
| KB representation and provenance | [Schema reference](_schema/README.md) | Metadata, naming, sources, and authoring conventions |
| Structural history | [Changelog](CHANGELOG.md) | Schema, path, and ownership changes |

## Foundation topic map

The Foundation subparts are compositional rather than mutually exclusive. A modeling question may need a formal problem definition, a representation choice, a learning objective, and an evaluation contract at the same time.

| Subpart | Knowledge scope | Entry point |
|---|---|---|
| Definitions and taxonomy | Operational definitions, historical lineages, world foundation models, and world action models | [Index](foundations/definitions-and-taxonomy/README.md) |
| Problem formulation | Sequential prediction, state, observation, belief, action, intervention, forward dynamics, and inverse dynamics | [Index](foundations/problem-formulation/README.md) |
| Representations | Video, latent, object-centric, geometric 3D/4D, and joint-embedding predictive representations | [Index](foundations/representations/README.md) |
| Learning objectives | Autoregressive, diffusion, rectified-flow, and flow-matching objectives | [Index](foundations/learning-objectives/README.md) |
| Decision-making | Planning, model predictive control, and model-based reinforcement learning | [Index](foundations/decision-making/README.md) |
| Embodied systems | Observation, action, controller, timing, safety, and sim-to-real interfaces | [Index](foundations/embodied-systems/README.md) |
| Data and evaluation | Dataset units, supervision, splits, metrics, falsification, and comparison protocols | [Index](foundations/data-and-evaluation/README.md) |
| Research frontiers | Evidence-backed unresolved problems and discriminating measurements | [Index](foundations/research-frontiers/README.md) |

[`foundations/retrieval-index.yaml`](foundations/retrieval-index.yaml) associates query themes with these canonical owners. It provides knowledge-discovery metadata only; it does not define Agent selection, task order, context budgets, stopping, retries, permissions, or execution policy.

## Component map

Components reconstruct how one capability changed across several works. They connect earlier bottlenecks, technical interventions, evidence, and remaining gaps without duplicating the general definitions in Foundations or the complete facts of each Paper or Model entry.

| Component | Knowledge scope | Entry point |
|---|---|---|
| Reasoning for World Models | Latent simulation, imagined behavior learning, predictive representation, explicit physical reasoning, and reasoning–generation coupling | [Entry](components/reasoning/README.md) |
| Generative Modeling | Autoregressive prediction, diffusion, latent compression, Transformer scaling, flow matching, interactive video, action conditioning, and omnimodal generation | [Entry](components/generative-modeling/README.md) |

The Component map is advisory and non-exclusive. A task can retrieve either or both Components together with the applicable Foundation, Paper, and Model owners.

## Representative paper map

| Paper | Family | Mechanisms and evidence | Entry point |
|---|---|---|---|
| Cosmos-Predict2.5 | Video-based latent world foundation model | Video curation, rectified-flow DiT, clean-prefix task unification, domain SFT and merging, reward post-training, distillation, Transfer2.5, robot/driving/multiview applications, and action-conditioned specialists | [Entry](papers/cosmos-predict2-5/README.md) |
| IRASim | Action-conditioned visual forward model for robot manipulation | Latent diffusion transformer, frame-level action conditioning, trajectory prediction, failure-rollout adaptation, policy evaluation, model-based planning, and implementation/reproduction boundaries | [Entry](papers/irasim/README.md) |
| MimicGen | Demonstration-generation system for imitation learning | Object-centric segment replay, success-only acceptance and its measured initial-state bias, generation-rate/policy-success decoupling, selection-strategy ablations, and stratified-acceptance transfer hypotheses | [Entry](papers/mimicgen/README.md) |
| Cosmos Policy | Video WM post-trained as a visuomotor policy | Predict2-2B latent-frame injection, joint policy/world-model/value training, LIBERO/RoboCasa/ALOHA, dual planning checkpoint, Predict2 versus Predict2.5 code split | [Entry](papers/cosmos-policy/README.md) |
| DreamZero | World action model | Joint video-action WAM, DROID/AgiBot 14B checkpoints, scoped zero-shot policy language, H100/GB200 inference not locally executed | [Entry](papers/dreamzero/README.md) |
| LAPA | Latent-action pretraining | Unlabeled-video latent-action quantization, robot-action remapping, Open-X finetuning; not Genie | [Entry](papers/lapa/README.md) |
| iVideoGPT | Interactive autoregressive video world model | Compressive VQ plus GPT-style OXE pretraining; results bound to named action-free versus action-conditioned checkpoints | [Entry](papers/ivideogpt/README.md) |
| DreamerV3 | Compact latent MBRL | Nature RSSM imagination agent; public repository is a DreamerV2-based reimplementation | [Entry](papers/dreamerv3/README.md) |
| TD-MPC2 | Decoder-free latent planning | TD latent dynamics with MPPI, 104-task single-hyperparameter claims, post-paper Q-ensemble init fix | [Entry](papers/td-mpc2/README.md) |
| V-JEPA 2 | Non-generative predictive representation | V-JEPA 2 versus 2-AC versus 2.1 split; latent planning evidence must not leak across variants | [Entry](papers/v-jepa-2/README.md) |
| DIAMOND | Pixel-space diffusion world model | Atari 100k MBRL inside an image-space diffusion model; CSGO branch is a separate qualitative surface | [Entry](papers/diamond/README.md) |
| OccWorld | 3D occupancy driving world model | Occupancy-token forecasting plus ego-trajectory prediction; nuScenes license and variant boundaries | [Entry](papers/occworld/README.md) |
| Vista | Controllable driving video world model | OpenDV control modes and official `vista.safetensors`; not Wayve GAIA; high-VRAM sampling not attempted | [Entry](papers/vista/README.md) |

Paper entries link their mechanisms to Foundation owners and target-model implications where applicable. Those links express knowledge dependencies, not a required retrieval sequence.

## Cross-part ownership

- Foundations owns reusable concepts, formalisms, mechanism families, trade-offs, and evaluation principles.
- Papers owns the claims, implementations, experiments, limitations, reproduction state, and transfer hypotheses of individual works.
- Components owns cross-paper capability evolution, recurring mechanism patterns, and component-level unresolved gaps.
- Models owns concrete architecture, checkpoint, interface, training, result, code, and execution facts for a named model.

A page in one part links to the relevant canonical owner in another part instead of duplicating its full explanation.

## Cosmos3-Nano retrieval metadata

[`models/cosmos3-nano/agent-index.yaml`](models/cosmos3-nano/agent-index.yaml) associates model-specific query themes with knowledge that can ground design and implementation decisions. It can be combined with Foundation concepts, representative Paper entries, and cross-paper Components; it is not the mandatory first knowledge path. The index is not a task router or orchestration control plane. AIBuildAI and its Agent architecture remain authoritative over Agent selection, repository selection, task sequencing, execution scheduling, and external actions.

## Metadata and maintenance references

| Knowledge change | Reference |
|---|---|
| Add or revise a canonical page | [Foundation template](_schema/foundation-page-template.md), [model template](_schema/page-template.md), and [style guide](_schema/style-guide.md) |
| Add a representative paper entry | [Paper entry template](_schema/paper-entry-template.md) |
| Add a cross-paper capability synthesis | [Component entry template](_schema/component-entry-template.md) |
| Add or rename a page ID or path | [Naming conventions](_schema/naming-conventions.md) |
| Change model identity, revisions, interfaces, or the execution-state pointer | [Manifest schema](_schema/manifest.schema.yaml); mutable states remain in [Reproduction](models/cosmos3-nano/reproduction.md) |
| Add or update a source | [Source schema](_schema/sources.schema.yaml) |
| Change required files or page metadata | [Metadata schema](_schema/metadata.schema.yaml) |
