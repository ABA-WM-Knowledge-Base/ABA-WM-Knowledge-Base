---
id: world-model-kb.papers
title: Part II — Representative Papers
kind: index
status: reserved
last_updated: 2026-08-11
owners:
  - AIBuildAI world-model group
---

# Part II — Representative Papers

## Retrieval metadata

**Relevant queries:** paper mechanism, ablation, benchmark result, implementation, reproduction, or transfer hypothesis.

**Knowledge provided:** the reserved scope and future paper-entry contract of Part II. This page currently contains no paper-specific facts.

**Related pages:** [Part I](../foundations/README.md) covers general concepts; [Part III](../models/README.md) covers model-specific knowledge.

## Canonical scope

Each paper entry will reconstruct one work as reusable optimization knowledge. It will separate the proposed mechanism, the implemented system, the reported experiments, the local reproduction state, and transfer hypotheses. It will not be a section-by-section summary or a narrative of the reading process.

No paper has been admitted into Part II. Candidate families or titles are not KB facts until their entries exist.

## Future entry contract

```text
papers/<paper-id>/
├── README.md                    # Entrypoint, identity, and canonical owners
├── paper.md                     # Mechanism, objectives, assumptions, and results
├── codebase.md                  # Implementation graph and change surfaces
├── reproduction.md              # Environment, commands, artifacts, failures, fixes
├── optimization-transfer.md     # Transferable levers and falsifiable adaptations
└── sources.yaml                 # Pinned primary sources and artifact identities
```

An entry is useful to an optimization agent only if it answers all of the following:

1. What behavior or limitation is the method designed to change?
2. What causal mechanism and training signal are proposed?
3. Which implementation and data surfaces realize that mechanism?
4. Which ablations isolate the claimed source of improvement?
5. Under what assumptions, compute regime, and evaluation protocol do the results hold?
6. Which intervention can transfer to a target model, where would it attach, and what would falsify the transfer hypothesis?
7. What has actually been reproduced, with which artifacts and deviations?

Use the [representative paper entry template](../_schema/paper-entry-template.md) when an entry is activated.
