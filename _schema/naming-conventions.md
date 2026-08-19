---
id: world-model-kb.naming
title: Naming Conventions
kind: reference
status: maintained
last_updated: 2026-08-19
owners:
  - AIBuildAI world-model group
---

# Naming Conventions

## Paths

Use stable semantic paths in lowercase kebab-case. Do not encode display order, temporary status, author names, or dates in canonical topic paths.

The four content roots are fixed:

- `foundations/` for model-independent knowledge;
- `papers/` for paper-specific knowledge;
- `components/` for cross-paper capability evolution and recurring mechanism syntheses;
- `models/` for the active Cosmos3-Nano entry.

Foundation concepts use a two-level semantic path:

```text
foundations/<subpart>/<topic>.md
```

The stable subparts are `definitions-and-taxonomy`, `problem-formulation`, `representations`, `learning-objectives`, `decision-making`, `embodied-systems`, `data-and-evaluation`, and `research-frontiers`. Subpart `README.md` files are discovery indexes; they do not duplicate the complete concept explanation. The part-level `retrieval-index.yaml` contains advisory query-to-knowledge associations, and the part-level `sources.yaml` owns shared Foundation source identities.

Component entries use one semantic directory per capability:

```text
components/<component-id>/README.md
components/<component-id>/sources.yaml
```

The entry ID is `world-model-kb.components.<component-id>`. A Component follows one capability across papers; it must not be named after a single work or model.

Use role names that expose knowledge scope. `optimization-playbook.md` owns experiment-design references; `research-queue.md` owns unresolved questions; `reproduction.md` owns local execution records. Do not use vague paths such as `misc.md`, `notes.md`, `thoughts.md`, or `relevance.md`.

## Page IDs

Use dot-separated stable IDs. Foundation concepts use `world-model-kb.foundations.<subpart>.<topic>`; Component entries use `world-model-kb.components.<component-id>`; Paper and Model entries use `world-model-kb.<part>.<entity>.<topic>`. Preserve an ID when a file moves without changing semantic ownership. Change an ID only when the entity or canonical scope changes.

Examples:

- `world-model-kb.foundations.problem-formulation.forward-dynamics`
- `world-model-kb.foundations.learning-objectives.diffusion-and-flow-matching`
- `world-model-kb.papers.dreamerv3.reproduction`
- `world-model-kb.papers.cosmos-predict2-5.optimization-transfer`
- `world-model-kb.components.reasoning`
- `world-model-kb.models.cosmos3-nano.action-modeling`

## Source registries and cross-part references

Resolve a source through the nearest owning registry: `foundations/sources.yaml` for model-independent concepts, `papers/<paper-id>/sources.yaml` for one work, `components/<component-id>/sources.yaml` for source objects unique to a cross-paper synthesis, and `models/<model-id>/sources.yaml` for one model entry. Use repository-wide unique source IDs and do not copy an identity into several registries.

Cross-part Markdown links may connect a Foundation concept, paper mechanism, and model instantiation. They express knowledge relationships, not required reading order, task priority, or workflow control. Relative paths must remain inside the repository.

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
