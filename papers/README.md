---
id: world-model-kb.papers
title: Part II - Representative Papers
kind: index
status: maintained
last_updated: 2026-08-13
owners:
  - AIBuildAI world-model group
---

# Part II - Representative Papers

## Retrieval metadata

**Relevant queries:** paper mechanism, ablation, benchmark result, implementation, reproduction, or transfer hypothesis.

**Knowledge provided:** the canonical scope of Part II, its active paper entries, and the entry contract that converts one work into reusable optimization knowledge.

**Related pages:** [Part I](../foundations/README.md) owns model-independent concepts and formalisms; [Part III](../models/README.md) owns model-specific knowledge. Individual paper entries connect mechanisms and transfer claims to the applicable Foundation owners without imposing a reading order.

## Canonical scope

Each paper entry reconstructs one work as reusable optimization knowledge. It separates the proposed mechanism, the implemented system, the reported experiments, the local reproduction state, and transfer hypotheses. It is not a section-by-section summary or a narrative of the reading process.

Paper-specific evidence remains canonical in its entry. When a mechanism, formal assumption, evaluation principle, or transfer claim depends on a model-independent concept, the entry links to that concept's Foundation page instead of redefining it. These links express knowledge ownership and dependencies; they do not prescribe task sequencing or AIBuildAI workflow orchestration.

## Active entries

| Paper entry | World-model family | Knowledge coverage |
|---|---|---|
| [Cosmos-Predict2.5](cosmos-predict2-5/README.md) | Video-based latent world foundation model | Flow-based video prediction, curation, conditional-frame curriculum, post-training, action conditioning, implementation boundary, reproduction contract, and transferable interventions |
| [IRASim](irasim/README.md) | Action-conditioned visual forward model for robot manipulation | Trajectory-to-video diffusion, frame-level action alignment, failure-rollout data, policy evaluation, model-based planning, released-code boundary, and transferable interventions |

An active entry is evidence about that named work, not a claim that its findings generalize to every model. Candidate families or titles are not KB facts until their entries exist.

## Entry contract

```text
papers/<paper-id>/
├── README.md                    # Entrypoint, identity, and canonical owners
├── paper.md                     # Mechanism, objectives, assumptions, and results
├── codebase.md                  # Implementation graph and change surfaces
├── reproduction.md              # Environment, commands, artifacts, failures, fixes
├── optimization-transfer.md     # Transferable levers, Foundation links, and falsifiable adaptations
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
