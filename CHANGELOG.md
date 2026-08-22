---
id: world-model-kb.changelog
title: Knowledge Base Changelog
kind: record
status: maintained
last_updated: 2026-08-19
owners:
  - AIBuildAI world-model group
---

# Knowledge Base Changelog

This file records changes that affect retrieval metadata, canonical ownership, schemas, paths, or interpretation. It does not record reading progress or prose-only edits.

## 1.2.0 - 2026-08-22

- Second model entry `models/xiaomi-robotics-1/` (routes: reasoner -> vlm-backbone.md, generator -> action-head.md).
- Paper entries `xiaomi-robotics-1`, `vlabench`, `ervla`; source prefixes XR1|XR0|QWEN3VL|VLAB|ERV.
- Validator generalized: every `models/*/manifest.yaml` is validated; per-entry required files moved to `model_required_files`.

## 1.1.0 - 2026-08-19

- Replaced the single long page in each current Component with method-oriented pages so retrieval can target a mechanism directly instead of loading a broad review.
- Split Reasoning into latent simulation and imagination, predictive representation and planning, explicit physical reasoning, reasoning–generation–action integration, and cross-method comparison.
- Split Generative Modeling into autoregressive modeling, diffusion, latent diffusion and DiT, flow matching and rectified flow, action-conditioned video, omnimodal generation, and cross-method comparison.
- Reduced each Component `README.md` to a concise boundary and method map, while retaining the existing local source registries and evidence ownership.
- Updated applicable Foundation, Paper, and Cosmos3-Nano links to point to the method-level owner pages. The multi-page organization remains local to these two Components and does not constrain future Component designs or AIBuildAI orchestration.

## 1.0.1 - 2026-08-19

- Scoped the historical bottleneck–intervention–mechanism–evidence structure to the Reasoning and Generative Modeling entries that chose it; it is no longer represented as a rule for all Components.
- Reframed `components/` as an extension space whose future authors choose their own content structure, file layout, directory depth, source-registry placement, and retrieval representation.
- Removed the shared Component entry template, universal `README.md`/`sources.yaml` inventory, path-derived Component ID check, required Component retrieval fields, minimum Component page length, registered-directory allowlist, and rejection of extra Component files or nested directories.
- Kept only repository-wide interoperability properties: discoverable entrypoints, stable page metadata, resolvable links, globally unique source IDs when sources are registered, and the existing AIBuildAI orchestration boundary.
- Advanced the metadata contract to schema version 7, made Component counts dynamically discovered, and made registered source references discoverable without requiring a predeclared Component-specific ID prefix.

## 1.0.0 - 2026-08-19

- Activated `components/` as the fourth peer content part, with Reasoning for World Models and Generative Modeling as its first two entries.
- Defined Component ownership as cross-paper capability evolution, recurring mechanism patterns, evidence boundaries, and unresolved component gaps; Foundations retain general concepts, Papers retain individual-work evidence, and Models retain concrete implementations and execution state.
- Reconstructed the Reasoning lineage from stochastic latent simulation through Dreamer imagination, DreamerV3 robustness, V-JEPA 2 predictive representation, Cosmos-Reason1 explicit physical reasoning, and Cosmos 3 reasoning–generation coupling.
- Reconstructed the Generative Modeling lineage from recurrent/autoregressive prediction through DDPM, latent diffusion, DiT, flow matching, rectified flow, interactive and action-conditioned video models, Cosmos-Predict2.5, and Cosmos 3.
- Added Component-local primary-source identities for the World Models companion article, latent diffusion, and DiT while reusing existing globally unique Foundation, Paper, and Model source IDs; pinned the reused Cosmos-Reason1 report identity to arXiv v3 because earlier revisions describe a different model/training surface.
- Added a Component entry template, metadata-schema version 6 contract, path/ID/provenance conventions, writing guidance, reciprocal cross-part links, and four-part structural validation.
- Kept Component retrieval advisory and page-based at the current scale; no task router, Agent selector, required reading order, execution schedule, or other AIBuildAI orchestration authority was introduced.

## 0.9.0 - 2026-08-14

- Activated ten additional representative-paper entries with official code (and, where released, official weights): Cosmos Policy, DreamZero, LAPA, iVideoGPT, DreamerV3, TD-MPC2, V-JEPA 2, DIAMOND, OccWorld, and Vista.
- Registered the new directories in `paper_entry.active_entries` and extended `SOURCE_REFERENCE` prefixes with `CPOL`, `DZ`, `LAPA`, `IVG`, `DV3`/`DV3SRC`, `TDMPC2`, `VJ2`, `DIA`/`DIASRC`, `OCC`/`OCCSRC`, and `VISTA`.
- Kept Cosmos Policy paper identity on existing `P25-COSMOS-POLICY`; the new entry owns only Predict2 code, Cookbook Predict2.5-path documentation, and named Hugging Face checkpoints.
- Preserved identity boundaries that affect retrieval: Predict2 versus Predict2.5 for Cosmos Policy; WAM zero-shot language for DreamZero; Nature versus arXiv titles and the public reimplementation for DreamerV3; V-JEPA 2 versus 2-AC versus 2.1; DIAMOND Atari versus CSGO; LAPA versus Genie; iVideoGPT versus later RLVR-World; Vista versus Wayve GAIA; OccWorld nuScenes license.
- Linked the new entries from applicable Foundation Cross-part instantiations without rewriting Foundation definitions, and without pushing the local KB copy to GitHub.
- Honored documented `local_path_policy`: a missing workstation PDF or reproduction path is a warning when `portable_identity` is set; relative links that point outside this checkout are not treated as KB-internal broken links.

## 0.8.1 - 2026-08-13

- Added `foundations/data-and-evaluation/data-curation-and-filtering.md` as the canonical owner for candidate-pool selection operators: quality top-k, outcome predicates, influence, diversity, redundancy removal, supervised quotas, and label-free stratification. Registered the supporting `DATA-*` sources and retrieval-index associations.
- Added MimicGen as a representative-paper entry for demonstration generation and data curation: paper evidence with page locators, the official implementation pinned at `NVlabs/mimicgen` commit `72bd767c`, inspection-only reproduction state, and `MG-XFER-01` through `MG-XFER-04` transfer hypotheses. Registered the `MIMICGEN-*` sources and extended the source-reference prefix whitelist.

## 0.8.0 - 2026-08-13

- Rebuilt both representative-paper `paper.md` pages around the source papers' section order: research problem, complete end-to-end architecture, data and training protocol, experimental setup, results, applications, and evidence boundaries.
- Added explicit input-to-output architecture flows for Cosmos-Predict2.5 and IRASim so retrieval does not require reconstructing the model from scattered mechanism fragments.
- Restored the Cosmos-Predict2.5 report's omitted Transfer2.5, Real2Real policy augmentation, driving-simulation, multiview, synthetic-VLA, and action-conditioned application sequence while keeping every result bound to its named specialist.
- Reconciled the Cosmos-Predict2.5 entry scope with the expanded paper page; execution ownership remains in each entry's `reproduction.md`.

## 0.7.0 - 2026-08-13

- Added IRASim as a standalone representative-paper entry using the peer-reviewed ICCV 2025/arXiv-v2 paper while preserving the 2024 predecessor and narrower public implementation boundary.
- Added canonical mechanism/experiment, released-code, reproduction, optimization-transfer, and source-registry pages for trajectory-to-video diffusion, frame-level action alignment, policy evaluation, and model-based planning.
- Pinned the paper hash, official code commit, public 820 GB archive/checkpoint repository revision, SDXL VAE dependency revision, project page, and GPC comparison identity.
- Preserved material evidence conflicts and gaps: 300K versus 3M training steps, paper-described temporal conditioning versus released Frame-Ada code, legacy unconditioned final layer, non-monotonic Push-T cells, v1 README citation error, training configs that default to debug/validation data, absent v2 planning/evaluation code, and two syntax-invalid public scripts.
- Linked IRASim to canonical Foundation and Cosmos3-Nano owners without adding task routing or workflow authority, and extended Paper-entry validation to require the new directory.

## 0.6.0 - 2026-08-12

- Activated Part II with a standalone Cosmos-Predict2.5 entry classified as a video-based latent world foundation model.
- Added canonical pages for the paper's mechanisms and experiments, released implementation graph, execution/reproduction state, and falsifiable optimization-transfer knowledge.
- Pinned report v2, paper-aligned and current code commits, current 2B/14B checkpoint repository revisions, related benchmark and method papers, and the local PDF hash.
- Preserved paper/code, protocol, and version boundaries: feature-release versus report-date code trees, 2B 32-layer versus 28-block descriptions, the rounded retention-rate mismatch, paper rCM versus released DMD2 distillation, unreleased RL/merge paths, action model/default/FPS conflicts, the current mutable release tag, and the later separate Cosmos Policy extension.
- Connected Predict2.5 evidence to applicable Foundation owners and Cosmos3-Nano lineage pages without creating a mandatory retrieval order or workflow route.
- Extended schema and validation contracts to require exact, complete Paper entries, enforce path-derived Paper IDs and retrieval metadata, and report Paper entry/page counts.

## 0.5.0 - 2026-08-11

- Activated Part I with 22 canonical World Model Foundation topics grouped into eight semantic subparts: definitions and taxonomy, problem formulation, representations, learning objectives, decision-making, embodied systems, data and evaluation, and research frontiers.
- Added `problem-formulation.md` and `actions-and-interventions.md` as explicit owners for mathematical task contracts and causal action semantics.
- Added an advisory Foundation retrieval index that maps query themes to knowledge without defining Agent selection, repository selection, task order, context budgets, stopping, retries, permissions, or execution policy.
- Added a Foundation source registry of primary papers, conference proceedings, datasets, and benchmarks, with globally unique IDs and explicit source discrepancies where official records differ.
- Added a Foundation-specific canonical page template and extended naming, style, metadata, and source-registry contracts for nested topic ownership.
- Connected Cosmos3-Nano mechanism, data, evaluation, optimization, and limitation pages to applicable Foundation owners; paper-entry contracts now require reciprocal conceptual links without a mandatory reading sequence.
- Generalized validation from one Cosmos source registry to all part- and entry-local registries, added global source-ID uniqueness, nested Foundation link and metadata checks, safe retrieval-index path containment, and canonical Foundation path-to-ID validation.
- Updated the repository architecture diagram and global index so Foundations, Papers, and Models remain peer, non-exclusive knowledge inputs; Cosmos3-Nano is a model entry rather than the universal first retrieval path.

## 0.4.0 - 2026-08-11

- Corrected the repository architecture to represent Foundations, Papers, and Models as non-exclusive peer knowledge inputs rather than forcing every task through Cosmos3-Nano.
- Standardized cross-page references as canonical knowledge ownership instead of task routing or experiment prioritization.
- Defined the KB as a knowledge-guidance and evidence layer that shapes reasoning and strategy without overriding AIBuildAI orchestration, configuration, permissions, or policies.
- Replaced control-plane task routes with dynamic-retrieval profiles based on query themes and document associations.
- Removed route priority, exclusions, context budgets, mandatory bundles, global stop rules, and expected-Agent-output fields.
- Replaced page-level `Agent routing` sections with descriptive `Retrieval metadata`.
- Reframed experiment stop, rollback, and scheduling language as evidence quality, attribution risk, or unresolved-dependency information.
- Rewrote the repository README as a concise reader guide to the architecture, authority boundary, and navigation model.
- Superseded the workflow-control aspects introduced in 0.3.0 while preserving its content, provenance, and canonical-ownership improvements.

## 0.3.0 - 2026-08-11

- Changed the KB interface from a human-facing research summary to an Agent-oriented retrieval and optimization reference.
- Required English for canonical pages and removed progress narration and generic project-justification sections.
- Added machine-readable Cosmos3-Nano retrieval metadata through `agent-index.yaml`.
- Replaced broad modality sets in `manifest.yaml` with mode-, component-, checkpoint-, and backend-scoped I/O contracts.
- Removed mutable execution-state mirrors from `manifest.yaml`; it now points to the sole registry in `reproduction.md`.
- Registered immutable summaries for both hosted HTTP-404 attempts and defined raw-run-status to KB-state mapping.
- Replaced `project-relevance.md` with `optimization-playbook.md`.
- Replaced `open-questions.md` with `research-queue.md`.
- Preserved Parts I and II as content-empty boundaries and kept Cosmos3-Nano in Part III.

### Historical path migration

| Removed path | Replacement | Semantic change |
|---|---|---|
| `models/cosmos3-nano/project-relevance.md` | `models/cosmos3-nano/optimization-playbook.md` | Project narrative to model-improvement evidence |
| `models/cosmos3-nano/open-questions.md` | `models/cosmos3-nano/research-queue.md` | General unknowns to a structured research registry |

## 0.2.0 - 2026-08-09

- Established the three-part boundary: foundations, representative papers, and Cosmos3-Nano.
- Reserved Parts I and II without content pages.
- Split the Cosmos3-Nano entry into canonical topic pages with a manifest and source registry.
- Removed model-centric top-level categories that conflated Cosmos3-Nano with the full world-model field.

## 0.1.0 - 2026-08-09

- Created the initial Cosmos3-Nano research structure. Superseded by the three-part architecture in 0.2.0.
