---
id: world-model-kb.foundations.problem-formulation
title: Problem Formulation and Dynamics
kind: index
status: maintained
last_updated: 2026-08-11
owners:
  - AIBuildAI world-model group
---

# Problem Formulation and Dynamics

## Retrieval metadata

**Relevant queries:** predictive problem definition, state and observation semantics, belief state, actions, interventions, forward dynamics, inverse dynamics, stochasticity, or identifiability.

**Knowledge provided:** model-independent variables, conditional distributions, assumptions, and prediction directions used to state a world-model problem precisely.

**Related pages:** [Definitions](../definitions-and-taxonomy/README.md) owns terminology; [decision-making](../decision-making/README.md) owns how predictions guide action; [embodied systems](../embodied-systems/README.md) owns physical interface constraints.

## Canonical boundary

This subpart owns the mathematical contract of the modeled process: variables, time indices, observability, transition and observation structure, action semantics, conditioning, and identifiability. It does not own planner algorithms, training-objective families, or embodiment-specific controller mappings.

## Topic map

| Topic | Canonical scope |
|---|---|
| [Problem formulation](problem-formulation.md) | Unified deterministic, stochastic, partially observed, controlled, and learned-model notation |
| [State, observation, and belief](state-observation-and-belief.md) | Latent state sufficiency, observations, histories, belief updates, and partial observability |
| [Actions and interventions](actions-and-interventions.md) | Action variables, interventions, exogenous inputs, coordinate contracts, and causal limitations |
| [Forward dynamics](forward-dynamics.md) | Predicting future state or observation conditional on current information and optional action |
| [Inverse dynamics](inverse-dynamics.md) | Inferring actions or controls from transitions, including ambiguity and identifiability limits |

The formulations ground modeling judgments but do not determine which AIBuildAI Agent, repository, or execution step is selected.
