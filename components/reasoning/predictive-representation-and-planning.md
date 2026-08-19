---
id: world-model-kb.components.reasoning.predictive-representation-and-planning
title: Predictive Representation and Latent Planning
kind: component
status: maintained
last_updated: 2026-08-19
owners:
  - AIBuildAI world-model group
---

# Predictive Representation and Latent Planning

## Retrieval metadata

**Relevant queries:** JEPA, V-JEPA 2, V-JEPA 2-AC, masked latent prediction, reconstruction-free world model, frozen video encoder, action-conditioned latent predictor, CEM image-goal planning.

**Knowledge provided:** How predictive embedding objectives separate broad video representation learning from action grounding, how V-JEPA 2-AC turns latent prediction into planning, and which results and limitations bound the transfer.

**Related pages:** [Representation learning and JEPA](../../foundations/representations/representation-learning-and-jepa.md) owns the general objective; [planning and control](../../foundations/decision-making/planning-and-control.md) owns search; the [V-JEPA 2 Paper entry](../../papers/v-jepa-2/README.md) owns variant-specific evidence; [comparison and optimization](comparison-and-optimization.md) compares reasoning families.

## Method definition

A joint-embedding predictive architecture predicts a target representation rather than reconstructing every target pixel:

\[
z_x=f_\theta(x_{\text{context}}),\qquad
z_y=\operatorname{sg}(f_{\bar{\theta}}(y_{\text{target}})),\qquad
\hat z_y=g_\phi(z_x,m,a),
\]

where \(m\) identifies the masked target region or time interval and \(a\) is optional action context. The loss compares \(\hat z_y\) with \(z_y\). The target encoder is commonly stop-gradient and updated as an exponential-moving average.

This approach moves the information-selection problem into the representation. It can ignore lighting, texture, or sensor noise that is hard to predict but irrelevant to a task. It can also discard small contact, pose, or object-state details that later control requires. Predictive abstraction is therefore neither automatically a calibrated belief nor automatically decision-sufficient.

## V-JEPA 2: large-scale action-free predictive learning

V-JEPA 2 pretrains a video encoder and predictor through masked latent prediction on more than one million hours of video and one million images. Visible spatiotemporal context passes through the context encoder; the predictor estimates target embeddings produced by an EMA target encoder. No RGB decoder is required by the training objective. [OBJ-VJEPA2-2025; VJ2-PAPER, Sec. 3]

The largest reported model reached 77.3% on Something-Something-v2 and 39.7 recall@5 on Epic-Kitchens-100 under the paper's evaluation. These results support transferable motion and activity representation. They do not establish action-conditioned dynamics because the pretraining data do not provide a unified physical action interface. [VJ2-PAPER, Tables 1–2]

The useful design boundary is explicit: passive-video predictive learning can produce a broad perceptual representation, but intervention semantics require an additional model or supervision.

## V-JEPA 2-AC: action grounding after frozen representation learning

V-JEPA 2-AC freezes the pretrained visual encoder and trains a separate 300M-parameter action-conditioned predictor on fewer than 62 hours of DROID interaction data. The predictor uses block-causal context to estimate future latent frames under candidate robot actions. At inference, cross-entropy-method search samples and refines action sequences whose predicted terminal representation approaches an image-goal representation. [VJ2-PAPER, Secs. 4–5]

Freezing the encoder creates a useful attribution boundary:

- broad visual structure comes from passive video and images;
- action effects come from the interaction-trained predictor;
- action selection comes from the external search loop;
- execution still uses a robot-specific action contract.

The paper reports 100% average reach success across its two laboratory setups, with lower and task-dependent grasp and pick-place success. In the Lab 2 comparison, V-JEPA 2-AC used 800 candidates and reported 16 seconds per action, while the compared Cosmos video world model used 80 samples, horizon one, and about four minutes per action. This suggests computational promise in the reported setup, but the comparison is not matched in model, objective, candidate count, or horizon. [VJ2-PAPER, Table 3 and Sec. 5]

## Design surfaces

| Surface | Mechanism | Evidence of benefit | Failure risk |
|---|---|---|---|
| Mask geometry and temporal extent | determines which invariances and dynamics must be predicted | transfer and prediction across motion scales | shortcut through visible overlap |
| Target-encoder update | stabilizes the representation target | non-collapsed features and consistent training | stale or overly coupled targets |
| Predictor capacity | controls dynamics complexity without changing encoder | lower latent rollout error | memorization of embodiment data |
| Frozen versus adapted encoder | trades attribution and broad transfer against target fit | sample-efficiency comparison | catastrophic loss of broad features |
| Action horizon and chunk | sets temporal abstraction | terminal-goal progress | search explosion and compounding drift |
| Candidate count and CEM iterations | improve search coverage | lower ranking regret | latency and unfair baseline budget |
| Goal representation | defines what “close to target” means | task-stage success | visual similarity without feasibility |

The minimum controlled transfer comparison is pretrained-frozen, pretrained-adapted, and from-scratch action predictors under the same interaction data, model capacity, search budget, and robot protocol.

## Evaluation boundaries

Representation quality, prediction quality, and planning quality require different tests:

1. **Representation:** held-out recognition, motion, state, and controllability probes.
2. **Prediction:** horizon-conditioned latent error and matched action counterfactuals.
3. **Search:** candidate-ranking regret against realized outcomes.
4. **Control:** stage and task success, latency, interventions, and recovery.
5. **Transfer:** held-out scenes, objects, tasks, viewpoints, and embodiments.

Camera sensitivity, image-goal ambiguity, autoregressive latent drift, and horizon-dependent search cost remain reported limitations. A strong linear probe is not evidence that candidate actions produce the correct future latent.

## Cosmos3-Nano connection

The relevant transfer hypothesis is not to replace Cosmos3-Nano generation with JEPA, but to test whether an auxiliary predictive embedding objective improves action-sensitive state while reducing pressure to reconstruct nuisance detail. Candidate attachment points include the Reasoner visual representation, Generator conditioning latents, or a separate action-conditioned predictor on frozen Cosmos features.

The hypothesis fails if representation probes improve but FD/WAM action sensitivity, candidate ranking, or closed-loop outcome does not. The [Reasoner](../../models/cosmos3-nano/reasoner.md), [Generator](../../models/cosmos3-nano/generator.md), and [action-modeling](../../models/cosmos3-nano/action-modeling.md) pages own the concrete target interfaces.

## Sources

- [OBJ-VJEPA2-2025] identifies the Foundation-level preprint.
- [VJ2-PAPER] identifies the Paper-entry snapshot and owns V-JEPA 2 versus 2-AC variant boundaries.
