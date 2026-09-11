---
id: world-model-kb.changelog
title: Knowledge Base Changelog
kind: record
status: maintained
last_updated: 2026-09-11
owners:
  - AIBuildAI world-model group
---

# Knowledge Base Changelog

This file records changes that affect retrieval metadata, canonical ownership, schemas, paths, or interpretation. It does not record reading progress or prose-only edits.

## 1.10.0 - 2026-09-11

- Added Parallel and Distributed Inference as the sixth Fast Video Inference owner page, covering partition choices, diffusion-specific stale context, hybrid process groups, topology-based selection, diagnostic comparisons, and scaling interpretation.
- Registered four paper versions and five pinned official repositories. Preserved image-versus-video evidence, algorithmic versus benchmark warmup, missing hardware metadata in the HunyuanVideo scaling table, and model-specific adapter support.
- Documented the existing Cosmos Framework FSDP, context/CFG parallel interfaces and Omni tensor-parallel boundary; updated reciprocal retrieval links without introducing Agent orchestration rules. Included the quantization formula's rendering compatibility fix.

## 1.9.0 - 2026-09-10

- Added Video Diffusion Quantization as the fifth Fast Video Inference owner page, covering numerical formats, calibration, five method families, error diagnosis, deployment evidence, and world-model transfer hypotheses.
- Registered five paper identities, four pinned official repositories, and NVIDIA format documentation. Distinguished simulated quantization from native execution, placeholder repositories from released implementations, and mixed-format average-bit accounting from a native six-bit format.
- Updated retrieval maps and reciprocal acceleration/Cosmos links while preserving the existing BF16 checkpoint boundary and AIBuildAI orchestration ownership.

## 1.8.0 - 2026-09-09

- Added Causal and Streaming Video Generation as the fourth Fast Video Inference owner page: temporal factorization, noise schedules, chunk boundaries, history-state validity, rollout training, latency accounting, failure diagnosis, and action-conditioned transfer hypotheses.
- Registered six primary-paper and six pinned official-code identities for VideoGPT, StreamingT2V, Diffusion Forcing, CausVid, SkyReels-V2, and Self Forcing. Preserved paper/release differences and distinguished internal autoregression from incremental output and measured real-time performance.
- Updated Component and global retrieval maps plus reciprocal acceleration and Cosmos links. Corrected the implication that rectified-flow sampling excludes temporal autoregression; documented existing Framework causal-training, sequence-packing, and Transfer-continuation hooks without claiming Nano streaming reproduction or changing AIBuildAI orchestration.

## 1.7.0 - 2026-09-09

- Added Sparse, Local, and Linear Attention as the third Fast Video Inference owner page, covering interaction cost, local and dynamic sparse routing, linear and hybrid architectures, training requirements, kernel constraints, controlled comparison evidence, failure diagnosis, and world-model transfer hypotheses.
- Registered primary paper and pinned official-code identities for the mathematical background, Video Swin, SVG, STA, VSA, SVG2, SANA-Video, and SANA-Video 2.0. Preserved training-free versus adapted variants, kernel versus pipeline timing, archived STA integration, and paper-to-code differences rather than merging them into a single recipe.
- Updated global and Component maps plus reciprocal distillation, caching, DiT, and Cosmos3-Nano links. Documented the existing Cosmos attention-dispatch surface separately from untested transfer hypotheses; no model execution or workflow-orchestration change is implied.

## 1.6.0 - 2026-09-08

- Added Training-Free Caching as the second Fast Video Inference owner page, covering cross-timestep, operator, and classifier-free-guidance redundancy; cache-object, refresh, correction, and protection choices; method evolution from DeepCache and PAB through adaptive runtime policies; failure diagnosis; and a cache-specific evaluation contract.
- Registered primary paper and pinned official-code identities for DeepCache, PAB, FasterCache, TeaCache, AdaCache, MagCache, and EasyCache. Speed claims remain bound to their original model, hardware, sampling, and timing conditions.
- Added reciprocal links from diffusion, flow matching, few-step distillation, and Cosmos3-Nano runtime pages. Cosmos caching remains an explicit transfer hypothesis rather than a reproduced capability, and the new knowledge does not alter AIBuildAI workflow orchestration.

## 1.5.0 - 2026-09-08

- Added Fast Video Inference as the seventh independently scoped Component and defined its boundary as reducing the inference cost of an already defined video generator, distinct from the generative objective owned by Generative Modeling and from AIBuildAI workflow orchestration.
- Added the Few-Step and One-Step Video Distillation owner page. It separates sampling steps, NFE, denoising latency, and end-to-end latency; synthesizes VideoLCM, T2V-Turbo, MCM, OSV, DOLLAR, DMD/DMD2, FastVideo, rCM, Phased DMD, TMD, and DUET; and records failure diagnosis, a structured evaluation contract, public implementation status, and Cosmos transfer boundaries.
- Registered primary paper, official project, and pinned repository identities under the `FVI-*` source family while reusing the existing `P25-DMD2`, `P25-RCM`, and Cosmos-Predict2.5 source identities.
- Updated global and Component knowledge maps plus reciprocal Generative Modeling, Cosmos3-Nano, and Cosmos-Predict2.5 links. Corrected the stale Components page reference from four to five peer content parts.
- Extended source-reference validation to recognize the `FVI-*` family without imposing an internal layout or retrieval contract on this or future Components.

## 1.4.0 - 2026-08-29

- Integrated all active contribution branches into `main`, retaining the complete inventories of seventeen Paper entries, six Component entries, three Model entries, and one Benchmark entry across five peer knowledge parts.
- Added MeanFlow, Improved MeanFlow, and Pixel MeanFlow knowledge to Generative Modeling while preserving the existing flow-matching, action-conditioning, and omnimodal pages.
- Unified the independent model-contract changes: the generic manifest and retrieval-index validator now covers Cosmos3-Nano, X-WAM, and Xiaomi-Robotics-1 while retaining Benchmark validation and all registered source-ID families.
- Reconciled global maps, architecture diagrams, canonical-ownership language, and retrieval documentation so every active contribution is discoverable without introducing workflow-orchestration authority.
- Advanced the metadata schema to version 9 for the merged three-model inventory and retained model manifest schema version 4.

## 1.3.0 - 2026-08-27

- Added World Representation and Dynamics Modeling as Component entries, using the same local method-map design as Reasoning and Generative Modeling without making that layout a part-wide template.
- World Representation owns how systems choose and compress world state (observation-space, reconstructive latents, predictive embeddings, discrete/occupancy tokens, multimodal streams). It does not own generative samplers, imagination/planning loops, or latent-action codes.
- Dynamics Modeling owns learned transitions \(p(s_{t+1}\mid s_t,a_t)\) across recurrent latent, decoder-free latent, observation-space, occupancy/ego, and joint multimodal families. It excludes inverse dynamics and world-model–policy interfaces, which remain with their applicable Foundation and WM-Policy Interface owners.
- Linked the new method pages from the Component map, global index, applicable Foundation Cross-part instantiations, and Paper Related pages. Existing Reasoning and Generative Modeling ownership is unchanged.

## 1.2.0 - 2026-08-24

- Activated `benchmarks/` as the fifth peer knowledge part. Benchmark entries own versioned tasks, environments, datasets, observation/action contracts, protocols, evaluators, baseline context, limitations, and execution state without controlling AIBuildAI workflow orchestration.
- Added Original RoboCasa as the first Benchmark entry, pinned to paper `arXiv:2406.02523v1` and official `v0.2` commit `756598a5be52e052339bb2d957426e39015c2afb`. The entry explicitly excludes RoboCasa365 `v1.0+` semantics and preserves the original task, scene, dataset, protocol, result, code, and reproduction boundaries.
- Added X-WAM as the fourteenth Paper entry and second Model entry. The Paper entry owns the proposed RGB-D/state/action mechanism, asynchronous noise scheduling, experiments, paper-to-code mapping, reproduction scope, and transfer hypotheses; the Model entry owns pinned public checkpoints and data, released interfaces, runtime semantics, checkpoint-bound evaluation, execution state, and falsifiable optimization knowledge.
- Pinned X-WAM code at `72cfb86b33fc5060963ef63412f16439fcfa472f`, checkpoint metadata at HF revision `bb6fd1643cfa8bdc751612a7ace0bd8062a8917a`, both released SFT dataset revisions, the Wan2.2 base, UMT5 tokenizer, and benchmark submodules. Source inspection and remote metadata inspection remain distinct from checkpoint download or execution.
- Preserved paper-to-release conflicts for pretraining batch per GPU, SFT learning rate, RoboTwin step count, and CFG execution semantics instead of merging them into one synthetic recipe.
- Added generic multi-model manifest/index validation plus Benchmark schema, template, retrieval-index, source, path, metadata, and document-map validation. Advanced the metadata schema to version 8 and the model manifest schema to version 4.
- Updated the repository architecture, global maps, Foundation retrieval associations, schema guidance, and cross-part links for five non-exclusive parts. Migrated the existing RoboCasa paper source identity from the Foundation registry to the canonical Original RoboCasa registry.
- Added the `models/xiaomi-robotics-1/` entry, with distinct retrieval owners for its Qwen3-VL backbone, DiT action head, action modeling, policy, training, evaluation, released checkpoints, and reproduction state.
- Added the Xiaomi-Robotics-1, VLABench, and ERVLA Paper entries and registered their XR1, XR0, QWEN3VL, VLAB, and ERV source identities.
- Extended the generic model-entry contract and validation to the Xiaomi-Robotics-1 file inventory without removing the existing Cosmos3-Nano, X-WAM, or Benchmark checks.

## 1.1.1 - 2026-08-20

- Added components/action-conditioning and components/wm-policy-interface (six-component split, topics 3 and 6): action representation routes, denoising schedules, future-prediction coupling; five WM-to-policy consumption modes, deployment boundaries, and the reasoner-to-policy evidence gap. Registered six new component source identities (X-WAM, World2Act, Consistency-Consensus, GigaWorld-1, the WAM-versus-VLA robustness study, and LaWAM).

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
