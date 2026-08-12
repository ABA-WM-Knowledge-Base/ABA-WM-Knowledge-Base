---
id: world-model-kb.foundations.representations.representation-learning-and-jepa
title: Representation Learning and JEPA
kind: concept
status: maintained
last_updated: 2026-08-11
owners:
  - AIBuildAI world-model group
---

# Representation Learning and JEPA

## Retrieval metadata

**Relevant queries:** JEPA, joint embedding predictive architecture, I-JEPA, V-JEPA, V-JEPA 2, feature prediction, masked representation learning, collapse prevention, or action-conditioned latent predictor.

**Knowledge provided:** feature-space predictive objectives, their distinction from pixel generation, collapse and shortcut risks, and conditions under which learned representations can support world modeling or action-conditioned prediction.

**Related pages:** [Latent world models](latent-world-model.md) covers transition models over learned state; [actions and interventions](../problem-formulation/actions-and-interventions.md) owns action semantics; [video world models](video-world-model.md) covers decoded future generation.

## Definition and formalism

A Joint-Embedding Predictive Architecture predicts a representation of a target from a representation of visible context rather than reconstructing every target pixel or token. A generic masked objective is

```text
z_x       = f_theta(x_context),
z_y       = stop_gradient(f_target(y_target)),
z_hat_y   = g_phi(z_x, mask, optional_action),
L_JEPA    = sum_targets d(z_hat_y, z_y).
```

The target encoder is commonly an exponential-moving-average copy or otherwise protected from direct gradient collapse. The mask determines what spatial or temporal information must be predicted. The distance `d` and representation normalization determine invariances and feature scale.

JEPA is a design family, not one loss. LeCun's JEPA proposal is a position and architecture paper; I-JEPA and V-JEPA provide concrete image and video instantiations. Predicting features does not automatically provide a decoder, likelihood, calibrated uncertainty, action model, or executable policy. [OBJ-LECUN-JEPA-2022; OBJ-IJEPA-2023; OBJ-VJEPA-2024]

## Assumptions and scope

Feature prediction assumes that the target encoder preserves information useful for downstream tasks while discarding unpredictable nuisance detail. This can make learning more efficient than pixel reconstruction, but the desired invariances are task-dependent. A representation invariant to color, small objects, or precise motion may help recognition and harm manipulation.

An action-free video JEPA models predictable temporal structure under observed behavior. It becomes an action-conditioned world-model component only when actions enter the predictor with validated timing and intervention semantics. V-JEPA 2's action-conditioned predictor illustrates this bridge by combining a video representation with interaction data; the representation pretraining and action model remain distinct evidence objects. [OBJ-VJEPA2-2025]

## Representation and objective families

| Family | Prediction target | Collapse control | Main use |
|---|---|---|---|
| Contrastive embedding | positive relative to negatives | negatives and normalization | invariant representation |
| Variance/covariance regularized | paired embeddings | variance floor and decorrelation | non-contrastive representation |
| Image JEPA | masked target-block features | target encoder and asymmetric masking | semantic image features |
| Video JEPA | masked spatiotemporal features | target encoder and temporal masks | motion-aware video features |
| Action-conditioned JEPA predictor | future features given state/action | interaction data and predictive loss | latent forward dynamics |
| Generative latent predictor | distribution over target features | stochastic latent/objective | multimodal feature futures |

VICReg makes collapse controls explicit through invariance, per-dimension variance, and covariance regularization. JEPA implementations may use different mechanisms; absence of negatives does not mean absence of anti-collapse design. [OBJ-VICREG-2022]

## Design implications and trade-offs

Mask size and geometry set the conditional prediction task: small local masks can permit texture shortcuts, while large blocks require semantics but may erase fine dynamics. Target-encoder momentum controls stability and lag. Predictor capacity determines whether context features must carry predictive structure or the predictor can absorb it. Temporal stride and horizon determine which motions are visible.

For world-model use, action/proprioception injection, multi-step prediction, stochastic targets, and state-update rules are separate levers. Variance and covariance regularizers can prevent numerical collapse while representations still collapse semantically onto nuisance cues. Freezing a strong encoder reduces adaptation cost but may preserve invariances incompatible with control; end-to-end adaptation can improve task detail while degrading general representation quality.

## Evaluation and falsification

- Monitor feature variance, covariance spectrum, effective rank, and constant-output baselines.
- Probe both semantic variables and fine control variables such as pose, velocity, contact, and small-object state.
- Test masks, temporal stride, and horizon for shortcut sensitivity.
- Evaluate prior-only multi-step feature rollout, not only one-step targets computed from real future frames.
- For action-conditioned variants, use matched action perturbations and independent environment outcomes.
- Compare linear probes, full fine-tuning, retrieval, prediction, and closed-loop control; none substitutes for the others.

A world-model claim is weakened when the predictor has no autonomous state update, when target features require future observations at deployment, or when action-free representation quality is used as evidence of interventional dynamics. A non-collapse claim is insufficient if effective feature rank remains high but all task-critical variables are absent.

## Failure modes

- **Representational collapse:** constant or low-rank features minimize the predictive objective.
- **Shortcut prediction:** positional, camera, or background cues solve masks without modeling dynamics.
- **Control-detail invariance:** semantic features discard contact, geometry, or small actions.
- **Target lag:** a slowly updated encoder stabilizes training but delays useful adaptation.
- **Action-free overclaim:** temporal prediction is interpreted as controllable transition knowledge.
- **Future-target dependence:** evaluation uses target encodings unavailable in autonomous rollout.
- **Probe substitution:** a strong linear probe is treated as evidence of generation, planning, or closed-loop control.
- **Deterministic averaging:** one target feature suppresses genuinely multimodal futures.

## Cross-part instantiations

- [Cosmos3-Nano training](../../models/cosmos3-nano/training.md) owns the documented objectives; JEPA should be treated as an alternative or auxiliary hypothesis unless the source specifies it.
- [Generator](../../models/cosmos3-nano/generator.md) uses a generative objective and should not be redescribed as JEPA based only on latent prediction.
- [Action modeling](../../models/cosmos3-nano/action-modeling.md) supplies the model-specific intervention interface required for an action-conditioned representation claim.
- [Optimization playbook](../../models/cosmos3-nano/optimization-playbook.md) can compare feature-predictive auxiliaries against documented autoregressive or flow objectives with task and regression metrics.

## Sources

- [OBJ-LECUN-JEPA-2022] LeCun, *A Path Towards Autonomous Machine Intelligence*, OpenReview, 2022, forum:BZ5a1r-kVsf.
- [OBJ-IJEPA-2023] Assran et al., *Self-Supervised Learning from Images with a Joint-Embedding Predictive Architecture*, CVPR 2023, DOI:10.1109/CVPR52729.2023.01519.
- [OBJ-VJEPA-2024] Bardes et al., *V-JEPA: Latent Video Prediction for Visual Representation Learning*, OpenReview ICLR 2024 submission; related arXiv:2404.08471.
- [OBJ-VICREG-2022] Bardes, Ponce, and LeCun, *VICReg: Variance-Invariance-Covariance Regularization for Self-Supervised Learning*, ICLR 2022, OpenReview:xm6YD62D1Ub.
- [OBJ-VJEPA2-2025] Assran et al., *V-JEPA 2: Self-Supervised Video Models Enable Understanding, Prediction and Planning*, arXiv:2506.09985, 2025.
