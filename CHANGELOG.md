---
id: world-model-kb.changelog
title: Knowledge Base Changelog
kind: record
status: maintained
last_updated: 2026-08-11
owners:
  - AIBuildAI world-model group
---

# Knowledge Base Changelog

This file records changes that affect retrieval metadata, canonical ownership, schemas, paths, or interpretation. It does not record reading progress or prose-only edits.

## 0.4.0 - 2026-08-11

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
