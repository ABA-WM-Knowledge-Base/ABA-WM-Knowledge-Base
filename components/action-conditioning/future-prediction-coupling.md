---
id: world-model-kb.components.action-conditioning.future-prediction-coupling
title: Future-Prediction Coupling
kind: component
status: draft
last_updated: 2026-08-20
owners:
  - AIBuildAI world-model group
---

# Future-Prediction Coupling

## Retrieval metadata

**Relevant queries:** future-state auxiliary supervision, action decoding depends on prediction, world model auxiliary loss, WAM failure attribution, action history conditioning gap.

**Knowledge provided:** The measured dependence of action decoding on predicted futures, the failure-attribution evidence pointing the same way, and the history-free gap shared by the strongest RoboCasa systems.

**Related pages:** [Latent-frame injection](latent-frame-injection.md) owns the representation this evidence was measured on; [comparison and optimization](comparison-and-optimization.md) owns the resulting selection guidance; the [WM-policy interface Component](../wm-policy-interface/README.md) owns how these coupled outputs are consumed.

## The auxiliary-supervision ablation

The strongest single number in this Component: removing future-state and value auxiliary supervision from Cosmos Policy's RoboCasa training reduces average success from 67.1% to 44.4% under the same 3,600-trial protocol and 50 demonstrations per task [P25-COSMOS-POLICY, pp. 7-8, 22].

Predicting the future is not an add-on to the action head. In this measurement it carries roughly a third of the performance, which means the "policy" and "world model" objectives inside a jointly trained system are not separable claims.

Boundary: this is one model on one benchmark. No independent replication of future-state auxiliary targets exists in the corpus; treat the effect as system evidence, not a component law.

## Failure attribution

DreamZero's analysis points the same direction from the failure side: WAM failures often follow erroneous video generation rather than action decoding [DZ-PAPER, p. 14].

Together the two results say the action interface cannot be audited in isolation. Action quality is downstream of predicted-future quality, so any curation, evaluation, or selection over action-conditioned rollouts must score the future prediction too. The consumption-side consequences are owned by the [WM-policy interface Component](../wm-policy-interface/rollout-selection-and-evaluation.md).

## The shared history-free gap

The two strongest RoboCasa systems both lack temporal history:

- Cosmos Policy uses observations only at times t and t+K, with no input history [P25-COSMOS-POLICY, p. 5].
- X-WAM has a fixed-length context without history conditioning or autoregressive rollout [COMP-ACT-XWAM-2026, p. 21].

No corpus paper measures what history-free action prediction costs on partially observed manipulation. The gap is shared, unpriced, and therefore a candidate optimization surface.

## Sources

- [P25-COSMOS-POLICY] identifies the Cosmos Policy paper; it resolves through the Cosmos Policy entry's registry.
- [DZ-PAPER] identifies DreamZero; it resolves through the DreamZero entry's registry.
- [COMP-ACT-XWAM-2026] identifies X-WAM; it resolves through the local [source registry](sources.yaml).
