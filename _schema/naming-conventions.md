---
id: world-model-kb.naming
title: Naming Conventions
kind: reference
status: maintained
last_updated: 2026-08-24
owners:
  - AIBuildAI world-model group
---

# Naming Conventions

## Paths

Use stable semantic paths in lowercase kebab-case. Do not encode display order, temporary status, author names, or dates in canonical topic paths.

The five content roots are fixed:

- `foundations/` for model-independent knowledge;
- `papers/` for paper-specific knowledge;
- `components/` for independently scoped component knowledge;
- `models/` for named model implementations and artifacts;
- `benchmarks/` for versioned evaluation systems.

Foundation concepts use a two-level semantic path:

```text
foundations/<subpart>/<topic>.md
```

The stable subparts are `definitions-and-taxonomy`, `problem-formulation`, `representations`, `learning-objectives`, `decision-making`, `embodied-systems`, `data-and-evaluation`, and `research-frontiers`. Subpart `README.md` files are discovery indexes; they do not duplicate the complete concept explanation. The part-level `retrieval-index.yaml` contains advisory query-to-knowledge associations, and the part-level `sources.yaml` owns shared Foundation source identities.

Component authors choose their own stable semantic substructure under `components/`. A Component may use one page or several pages and may choose whether a local source registry or machine-readable retrieval artifact is useful. Its public entrypoint must be linked from the Component knowledge map or global index, but neither filename nor internal depth is fixed.

Model entries use `models/<model-id>/`; Benchmark entries use `benchmarks/<benchmark-id>/`. Use role names that expose knowledge scope. `optimization-playbook.md` owns model experiment-design references; `optimization-reference.md` may own benchmark-side measurement and slice knowledge; `research-queue.md` owns unresolved questions; `reproduction.md` owns local execution records. Do not use vague paths such as `misc.md`, `notes.md`, `thoughts.md`, or `relevance.md`.

## Page IDs

Use dot-separated stable IDs. Foundation concepts use `world-model-kb.foundations.<subpart>.<topic>`; Component pages use the `world-model-kb.components` namespace without a prescribed internal depth; Paper, Model, and Benchmark entries use `world-model-kb.<part>.<entity>.<topic>`. Preserve an ID when a file moves without changing semantic ownership. Change an ID only when the entity or canonical scope changes.

Examples:

- `world-model-kb.foundations.problem-formulation.forward-dynamics`
- `world-model-kb.foundations.learning-objectives.diffusion-and-flow-matching`
- `world-model-kb.papers.dreamerv3.reproduction`
- `world-model-kb.papers.cosmos-predict2-5.optimization-transfer`
- `world-model-kb.components.reasoning`
- `world-model-kb.models.cosmos3-nano.action-modeling`
- `world-model-kb.models.x-wam.architecture`
- `world-model-kb.benchmarks.robocasa.protocol-and-metrics`

## Source registries and cross-part references

Resolve a source through the nearest owning registry: `foundations/sources.yaml` for model-independent concepts, `papers/<paper-id>/sources.yaml` for one work, `models/<model-id>/sources.yaml` for one model entry, and `benchmarks/<benchmark-id>/sources.yaml` for one benchmark version family. A Component may reuse these IDs or place an optional `sources.yaml` in a directory chosen by its author. Use repository-wide unique source IDs and do not copy an identity into several registries.

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
| Unified world action model | X-WAM |
| Benchmark entry | Original RoboCasa or RoboCasa; explicitly exclude RoboCasa365 when referring to the v0.2 entry |

Distinguish a product family, downloadable checkpoint, hosted service ID, post-trained checkpoint, and local run. Similar names do not establish revision identity or behavioral equivalence.

## Terms and symbols

Expand an abbreviation at first use on a page. Preserve code symbols exactly. Define forward dynamics, inverse dynamics, world action model, policy, Reasoner, and Generator through their input/output contracts; do not substitute terms based on natural-language similarity.

Use `YYYY-MM-DD` for dates, full commit SHAs for code, and full revision hashes for model snapshots. Time-sensitive benchmark results must include the snapshot date. Experiment IDs should be stable and sortable, for example `c3n-policy-action-horizon-20260811-01`, while artifact filenames may additionally include a content hash.
