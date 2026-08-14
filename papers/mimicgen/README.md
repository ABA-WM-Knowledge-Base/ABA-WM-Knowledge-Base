---
id: world-model-kb.papers.mimicgen
title: MimicGen Paper Knowledge Entry
kind: paper
status: draft
last_updated: 2026-08-13
owners:
  - AIBuildAI world-model group
---

# MimicGen Paper Knowledge Entry

## Retrieval metadata

**Relevant queries:** MimicGen, synthetic demonstrations, demonstration generation from few human demos, replay-based data generation, success-only filtering, data generation rate, source demonstration selection, imitation learning data scaling, robosuite demonstration datasets.

**Knowledge provided:** entry point and page map for the MimicGen system: paper identity and pinned artifacts, mechanism and evidence reconstruction, released-implementation graph, local execution state, and falsifiable transfer hypotheses for synthetic-demonstration pipelines.

**Related pages:** [Data curation and filtering](../../foundations/data-and-evaluation/data-curation-and-filtering.md) owns the selection-operator taxonomy this system instantiates; [datasets and supervision](../../foundations/data-and-evaluation/datasets-and-supervision.md) owns composition principles; [evaluation methodology](../../foundations/data-and-evaluation/evaluation-methodology.md) owns protocol validity; [robotics and embodied AI](../../foundations/embodied-systems/robotics-and-embodied-ai.md) owns embodiment interfaces.

## Identity

- **Work:** MimicGen: A Data Generation System for Scalable Robot Learning using Human Demonstrations; Mandlekar et al. (NVIDIA and UT Austin); CoRL 2023. Canonical experimental version for this entry: arXiv:2310.17596v1 (26 Oct 2023). [MIMICGEN-PAPER-V1]
- **Family and task boundary:** a demonstration-generation system for imitation learning. It contains no learned model: generation is deterministic replay of object-frame-transformed source segments with an action-noise scale, filtered by per-task binary success predicates. It is not a world model, not a policy, and not a score-ranking curator; policy training is delegated to robomimic BC-RNN.
- **Official artifacts:** code at `NVlabs/mimicgen`, pinned at commit `72bd767c` (NVIDIA License; full generation code released 2024-07-09, nine months after the paper) [MIMICGEN-CODE-CURRENT]; released datasets (12 tasks, 48K+ demonstrations, CC-BY 4.0) on Hugging Face [MIMICGEN-DATASETS-HF]; project and documentation site [MIMICGEN-PROJECT].
- **Release boundary:** the paper's Factory (Isaac Gym) tasks and real-robot stack are not in the public release; see [`codebase.md`](codebase.md).

## Why this entry exists

MimicGen is the reference mechanism for the synthetic-demonstration scaling strategy used by current RoboCasa-era pipelines, and it is the only such system whose acceptance-step bias is measured in its own appendix (initial-state support coverage down to 43.5 percent on measured variants). That makes it both the baseline generator and the primary evidence anchor for curation-aware filtering work.

## Page map

| Page | Owns |
|---|---|
| [`paper.md`](paper.md) | problem, assumptions, pipeline, protocols, main results, ablations, DGR-success decoupling, measured bias, evidence boundaries |
| [`codebase.md`](codebase.md) | pinned revision, mechanism-to-symbol map, call chain, contracts, paper/code boundaries |
| [`reproduction.md`](reproduction.md) | observed execution state (inspection-only at present), environment boundary, record contract |
| [`optimization-transfer.md`](optimization-transfer.md) | `MG-XFER-01..04`: stratified acceptance, DGR-as-signal prohibition, source composition control, interpolation hygiene |
| [`sources.yaml`](sources.yaml) | resolvable identities for the paper, code revision, datasets, and project site |

## Sources

- [MIMICGEN-PAPER-V1] paper identity (CoRL 2023, arXiv:2310.17596v1).
- [MIMICGEN-CODE-CURRENT] pinned official repository revision.
- [MIMICGEN-DATASETS-HF] official dataset release identity.
- [MIMICGEN-PROJECT] project and documentation site.

All resolve through this entry's [`sources.yaml`](sources.yaml).
