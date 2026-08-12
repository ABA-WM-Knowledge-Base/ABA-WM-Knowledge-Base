---
id: world-model-kb.foundations.decision-making
title: Decision-Making with World Models
kind: index
status: maintained
last_updated: 2026-08-11
owners:
  - AIBuildAI world-model group
---

# Decision-Making with World Models

## Retrieval metadata

**Relevant queries:** planning, model predictive control, trajectory optimization, imagination, model-based reinforcement learning, uncertainty-aware control, replanning, or model exploitation.

**Knowledge provided:** model-independent methods and trade-offs for using learned predictions to compare actions, optimize policies, or update control decisions.

**Related pages:** [Problem formulation](../problem-formulation/README.md) owns dynamics and action variables; [embodied systems](../embodied-systems/README.md) owns physical execution interfaces; [evaluation](../data-and-evaluation/README.md) owns controlled evidence.

## Canonical boundary

This subpart owns the decision-time or policy-learning use of a world model, including objectives, horizons, uncertainty, replanning, and model bias. It does not own dynamics definitions, actuator mappings, safety policies, or model-specific deployment procedures.

## Topic map

| Topic | Canonical scope |
|---|---|
| [Planning and control](planning-and-control.md) | Search, sampling, optimization, model predictive control, receding horizons, uncertainty, and closed-loop correction |
| [Model-based reinforcement learning](model-based-rl.md) | Learned-model roles in policy and value learning, synthetic experience, exploration, and model-bias management |

These methods inform reasoning about candidate strategies while AIBuildAI retains authority over Agent selection and execution orchestration.
