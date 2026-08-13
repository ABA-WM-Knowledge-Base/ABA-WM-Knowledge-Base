---
id: world-model-kb.papers.mimicgen.reproduction
title: MimicGen Reproduction State and Experiment Contracts
kind: record
status: draft
last_updated: 2026-08-13
owners:
  - AIBuildAI world-model group
---

# MimicGen Reproduction State and Experiment Contracts

## Retrieval metadata

**Relevant queries:** mimicgen reproduction, local execution state, generation smoke run, dataset download state, robosuite environment setup, mimicgen run record.

**Knowledge provided:** the current observed execution state for this entry (inspection-only), the environment boundary that constrains local execution, and the immutable record contract that future runs must satisfy.

**Related pages:** [`codebase.md`](codebase.md) owns the pinned implementation graph; [`paper.md`](paper.md) owns the paper's reported protocols; [`optimization-transfer.md`](optimization-transfer.md) owns the interventions whose experiments would create records here.

## 1. Execution state

A documented command is not an observed run. Current state per surface:

| Surface | State | Evidence |
|---|---|---|
| Repository inspection | **done** | local clone pinned at `72bd767c` and read at symbol level (see [`codebase.md`](codebase.md)) [MIMICGEN-CODE-CURRENT] |
| Dependency installation (robosuite, MuJoCo, robomimic) | not attempted | no local environment built for this entry |
| Official dataset download | not attempted | Hugging Face identity recorded, nothing retrieved [MIMICGEN-DATASETS-HF] |
| Data generation (any task) | **not run** | no run records exist |
| Policy training (BC-RNN on generated data) | **not run** | no run records exist |
| Paper-number reproduction (any table) | **not run** | no run records exist |

No claim in this entry's pages rests on local execution; every number is paper-sourced with page locators or code-sourced at the pinned revision.

## 2. Environment boundary

The inspecting workstation runs Windows 11 with Python 3.12 and a CPU-only PyTorch installation (RTX 5090 incompatible with the available cu124 wheels at inspection time). MimicGen's generation stack requires robosuite with a MuJoCo backend, and policy training requires robomimic; neither has been installed or verified on this machine, and local sufficiency (simulator licensing, headless rendering, wall-clock feasibility on CPU) is unresolved. Meaningful generation and training throughput is expected to require the lab's Linux GPU environment, access to which is pending. These are boundary facts, not blockers created by the release itself.

## 3. Record contract for future runs

Each future run or logically atomic run group appends one immutable record with:

- experiment ID and timestamp;
- `NVlabs/mimicgen` revision, robosuite/robomimic/MuJoCo versions, Python and driver/CUDA identity;
- hardware (GPU model, CPU count, memory);
- dataset identity (source hdf5 name and hash, or generation config) and preprocessing;
- exact command and resolved configuration (the JSON template plus overrides);
- baseline, intervention, controlled variables, seed set or attempt count;
- raw and aggregated metrics (attempts, successes, DGR, policy success where applicable), artifact and log locations;
- failures, root cause, minimal fix, patch identity, remaining deviation;
- acceptance or rejection against a predeclared criterion.

Execution status is tracked separately for generation, dataset handling, and training.

## 4. Planned first records

1. **Toolchain smoke run** (first record to be created): environment build plus a short `generate_dataset.py` run on one released task config (e.g. Stack D0) with a small attempt budget, to validate the stack end to end. A smoke run validates plumbing only; it will not be cited as scientific evidence.
2. **Stratified-acceptance pilot** (`MG-XFER-01` in [`optimization-transfer.md`](optimization-transfer.md)): the registered two-task, budget-matched pilot, conditional on lab GPU access; its records will live here with the preregistered protocol referenced.

## Sources

- [MIMICGEN-CODE-CURRENT] `NVlabs/mimicgen` at commit `72bd767c255545f462e7ccfb2731f2e5d4c1d9bb`, local clone inspected 2026-08-13.
- [MIMICGEN-DATASETS-HF] Official dataset release identity on Hugging Face; recorded, not retrieved.
