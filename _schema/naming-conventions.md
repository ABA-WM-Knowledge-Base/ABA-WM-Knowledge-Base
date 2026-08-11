---
id: world-model-kb.naming
title: Naming Conventions
kind: reference
status: maintained
last_updated: 2026-08-11
owners:
  - AIBuildAI world-model group
---

# Naming Conventions

## Paths

Use stable semantic paths in lowercase kebab-case. Do not encode display order, temporary status, author names, or dates in canonical topic paths.

The three content roots are fixed:

- `foundations/` for model-independent knowledge;
- `papers/` for paper-specific knowledge;
- `models/` for the active Cosmos3-Nano entry.

Use role names that expose knowledge scope. `optimization-playbook.md` owns experiment-design references; `research-queue.md` owns unresolved questions; `reproduction.md` owns local execution records. Do not use vague paths such as `misc.md`, `notes.md`, `thoughts.md`, or `relevance.md`.

## Page IDs

Use dot-separated stable IDs: `world-model-kb.<part>.<entity>.<topic>`. Preserve an ID when a file moves without changing semantic ownership. Change an ID only when the entity or canonical scope changes.

Examples:

- `world-model-kb.foundations.forward-dynamics`
- `world-model-kb.papers.dreamerv3.reproduction`
- `world-model-kb.models.cosmos3-nano.action-modeling`

## Product and implementation names

Preserve official capitalization and identifiers:

| Object | Canonical form |
|---|---|
| Model product | Cosmos3-Nano |
| Hugging Face checkpoint | `nvidia/Cosmos3-Nano` |
| Hosted Reasoner model | `nvidia/cosmos3-nano-reasoner` |
| Policy checkpoint | `nvidia/Cosmos3-Nano-Policy-DROID` |
| Prior-generation model | Cosmos-Predict2.5; never abbreviate it to Cosmos3 |

Distinguish a product family, downloadable checkpoint, hosted service ID, post-trained checkpoint, and local run. Similar names do not establish revision identity or behavioral equivalence.

## Terms and symbols

Expand an abbreviation at first use on a page. Preserve code symbols exactly. Define forward dynamics, inverse dynamics, world action model, policy, Reasoner, and Generator through their input/output contracts; do not substitute terms based on natural-language similarity.

Use `YYYY-MM-DD` for dates, full commit SHAs for code, and full revision hashes for model snapshots. Time-sensitive benchmark results must include the snapshot date. Experiment IDs should be stable and sortable, for example `c3n-policy-action-horizon-20260811-01`, while artifact filenames may additionally include a content hash.
