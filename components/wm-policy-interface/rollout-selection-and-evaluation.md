---
id: world-model-kb.components.wm-policy-interface.rollout-selection-and-evaluation
title: Rollout Selection and Evaluation
kind: component
status: draft
last_updated: 2026-08-20
owners:
  - AIBuildAI world-model group
---

# Rollout Selection and Evaluation

## Retrieval metadata

**Relevant queries:** test-time candidate selection, consistency consensus, best-of-N action selection, world model policy evaluator, WMBench, action-faithful rollout, evaluator validity.

**Knowledge provided:** The consumption mode that scores world-model futures to pick candidates or evaluate policies: the verified selection mechanism, the evaluator-validity criterion, and the known failure modes of both.

**Related pages:** [Action-conditioned video modeling](../generative-modeling/action-conditioned-video.md) owns generic planning-use reporting rules; [future-prediction coupling](../action-conditioning/future-prediction-coupling.md) owns why action scores cannot be separated from future-prediction scores; [evaluation methodology](../../foundations/data-and-evaluation/evaluation-methodology.md) owns general evidence rules.

## Test-time candidate selection

Consistency-Consensus is the verified training-free instance: sample N = 8 future-action branches, average their predicted futures, score each branch by exp(-alpha * d) agreement with that mean (latent-space MSE, alpha = 0.1), and execute the highest-scoring branch winner-takes-all. On its reimplemented Cosmos Policy baseline this moves RoboCasa success from 66.6% to 67.3% [COMP-WPI-CONSISTENCY-2026, pp. 3, 7-8].

Evidence boundaries that must travel with the number:

- The same table reports Value-Prediction at 67.4 and Consistency-Exploring at 68.0; Exploring requires environment access at inference and is called an upper bound [COMP-WPI-CONSISTENCY-2026, p. 8].
- The comparison baseline is the paper's own reimplementation (66.6), not the original 67.1; the protocol is 1,200 rollouts by arithmetic, with no stated seed count [COMP-WPI-CONSISTENCY-2026, p. 8].
- Known failure: static collapsed futures can appear consistent through background agreement, and selection cannot eliminate them [COMP-WPI-CONSISTENCY-2026, pp. 5, 19].

## World models as policy evaluators

GigaWorld-1 states the validity criterion verbatim: evaluator quality is "dominated by long-horizon, action-faithful rollout consistency rather than short-term visual realism". Its WMBench measurement base is 2,989 paired trajectories and 324,000 human-annotated rollout segments; short-horizon generators degrade over 40-second rollouts [COMP-WPI-GIGAWORLD-2026, pp. 1, 5, 9].

The criterion generalizes across this Component: whether futures are scored to select actions (above) or to evaluate policies, visual realism is not the load-bearing property, action-faithful consistency over the full horizon is.

## Selection is not a substitute for model quality

Both mechanisms rank futures produced by the same model they are trying to protect against. A selector inherits the model's blind spots: the consensus mean is only meaningful if the model's future distribution surrounds reality, and an evaluator trained or anchored on the same generator family shares its failure modes. Independent grounding (environment replay, human annotation, or a separately trained value model) is what distinguishes the verified instances from circular self-scoring.

## Sources

- [COMP-WPI-CONSISTENCY-2026] identifies the Consistency-Consensus paper; it resolves through the local [source registry](sources.yaml).
- [COMP-WPI-GIGAWORLD-2026] identifies GigaWorld-1; it resolves through the local [source registry](sources.yaml).
