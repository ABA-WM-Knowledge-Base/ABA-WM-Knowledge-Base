---
id: world-model-kb.foundations.embodied-systems
title: Embodied World-Model Systems
kind: index
status: maintained
last_updated: 2026-08-11
owners:
  - AIBuildAI world-model group
---

# Embodied World-Model Systems

## Retrieval metadata

**Relevant queries:** robotics, embodied AI, observation stacks, action spaces, controller semantics, closed-loop deployment, latency, contact, safety, or sim-to-real transfer.

**Knowledge provided:** interface and deployment principles that connect abstract world-model variables to sensors, actions, controllers, environments, and physical consequences.

**Related pages:** [Actions and dynamics](../problem-formulation/README.md) owns general formal semantics; [decision-making](../decision-making/README.md) owns planning and policy use; [Cosmos3-Nano policy](../../models/cosmos3-nano/policy.md) owns the model-specific interface.

## Canonical boundary

This subpart owns embodiment-specific observation, action, timing, controller, interaction, safety, and distribution-shift consequences. It does not redefine generic state-transition notation or claim that open-loop prediction establishes closed-loop competence.

## Topic map

| Topic | Canonical scope |
|---|---|
| [Robotics and embodied AI](robotics-and-embodied-ai.md) | Sensor and action contracts, embodiment transfer, control frequency, contact, closed-loop feedback, sim-to-real gaps, and deployment evidence |

Embodiment knowledge can change how an Agent evaluates a design, but it does not grant execution permissions or replace AIBuildAI orchestration and safety policies.
