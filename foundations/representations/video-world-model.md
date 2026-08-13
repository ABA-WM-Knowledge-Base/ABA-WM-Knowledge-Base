---
id: world-model-kb.foundations.representations.video-world-model
title: Video World Models
kind: concept
status: maintained
last_updated: 2026-08-13
owners:
  - AIBuildAI world-model group
---

# Video World Models

## Retrieval metadata

**Relevant queries:** video world model, future frame prediction, action-conditioned video, stochastic video prediction, long-horizon generation, visual dynamics, or pixel-space simulation.

**Knowledge provided:** the conditional distribution represented by video world models, major representation and conditioning families, optimization trade-offs, and tests that separate visual plausibility from usable dynamics.

**Related pages:** [World models](../definitions-and-taxonomy/world-model.md) defines the broader category; [actions and interventions](../problem-formulation/actions-and-interventions.md) owns control semantics; [autoregressive modeling](../learning-objectives/autoregressive-modeling.md) and [diffusion and flow matching](../learning-objectives/diffusion-and-flow-matching.md) own objective families.

## Definition and formalism

A video world model predicts a distribution over future observations, commonly

```text
p_theta(o[t+1:t+H] | o[<=t], a[t:t+H-1], c),
```

where actions `a` and context `c` are optional. The predicted variables may be pixels, compressed video latents, or discrete visual tokens; `video` describes the decoded observation surface, not necessarily the internal representation.

Action-free video prediction estimates likely continuation under the behavior implicit in its data. Action-conditioned prediction estimates a family of continuations indexed by a specified control signal. These are different query surfaces. A model trained on passive video can learn regularities and latent controls, but it does not thereby identify the consequences of calibrated robot commands.

## Assumptions and scope

Video preserves dense evidence about geometry, appearance, motion, contacts, agents, and camera behavior without requiring a hand-designed state. It also entangles those factors with sensor noise, occlusion, lighting, rendering, and viewpoint. The model may therefore allocate substantial capacity to visually likely detail that is irrelevant to control while missing small task-critical state changes.

For multimodal futures, a deterministic squared-error predictor estimates a conditional mean under its assumptions; averaging incompatible futures often appears as blur. Stochastic latent variables, autoregressive tokens, adversarial losses, diffusion, or flow objectives represent alternatives differently, but none guarantees physical or action consistency. [REP-MATHIEU-2016; REP-VIDEO-PREDICTION-2016]

## Representation and mechanism families

| Family | Predictive unit | Characteristic advantage | Characteristic cost |
|---|---|---|---|
| Direct pixel predictor | RGB or sensor values | no learned codec bottleneck | expensive and sensitive to nuisance detail |
| Transformation-based predictor | pixels moved by kernels, flow, or masks | strong local motion bias | struggles with disocclusion and new content |
| Continuous latent video model | compressed spatiotemporal features | lower rollout cost | decoder and latent can omit task detail |
| Discrete-token video model | learned visual code sequence | scalable sequence modeling | tokenizer distortion and serial generation |
| Diffusion or flow video model | noisy/interpolated video latent | multimodal high-fidelity samples | iterative sampling and temporal consistency burden |
| Hierarchical/temporal model | coarse dynamics plus local detail | longer context at reduced cost | cross-scale synchronization errors |

Action-conditioned Atari prediction established that deep visual models could learn controllable frame dynamics. Transformation-based robot video prediction modeled object motion and enabled visual foresight. TECO targeted long sequences using temporal abstraction; DIAMOND showed that a generative world model can support agent learning while also demonstrating that seemingly small missing details can be behaviorally important. [FND-OH-VIDEO-2015; REP-VIDEO-PREDICTION-2016; REP-TECO-2023; REP-DIAMOND-2024]

## Design implications and trade-offs

Codec resolution, temporal stride, conditioning history, horizon curriculum, action injection, camera/pose signals, stochastic capacity, and sampling budget determine what changes the model can represent. More compression reduces memory and compute but raises the risk that gripper state, contact, small objects, or text disappear. Longer horizons increase strategic coverage while amplifying identity loss and off-manifold rollout.

The training and deployment modes should match the query. A model trained with ground-truth frames at every step may look strong under teacher forcing yet drift when its own samples become context. Action conditioning should be tested for use rather than presence: conditioning tokens can be ignored when scene and behavior correlations already predict average motion.

## Evaluation and falsification

Useful evaluation separates:

1. **Conditional fidelity:** likelihood or reconstruction under the stated conditioning.
2. **Temporal consistency:** identity, geometry, contact, and object permanence across horizon.
3. **Action sensitivity:** outcome changes under matched feasible action perturbations.
4. **Distribution quality:** coverage and calibration of alternative futures, not one best-looking sample.
5. **Downstream utility:** planning, policy learning, or reasoning using generated rollouts.
6. **Compute:** latency, memory, and sample count at the achieved quality.

Independent environment replay is stronger evidence than action-video self-consistency. Horizon-stratified metrics and rare-event slices reveal errors hidden by aggregate perceptual scores. A physical-simulation claim is weakened when camera motion is correct but contacts, conservation constraints, or intervention effects are not. A planning claim is falsified when an agent exploits visual-model artifacts despite improved PSNR, FVD, or preference scores.

## Failure modes

- **Photorealism-physics substitution:** attractive frames contain incorrect contacts or consequences.
- **Exposure drift:** generated frames move outside the training context distribution.
- **Identity and permanence loss:** entities merge, switch identity, vanish, or reappear inconsistently.
- **Conditional collapse:** samples ignore actions, goals, or rare context.
- **Codec erasure:** compression removes small but decision-relevant evidence.
- **Camera-world confounding:** viewpoint change is mistaken for object or scene dynamics.
- **Metric mismatch:** perceptual similarity improves without action sensitivity or task success.
- **Best-of-N inflation:** quality gains arise from increased sampling rather than a better conditional model.

## Cross-part instantiations

- [Cosmos3-Nano Generator](../../models/cosmos3-nano/generator.md) owns the checkpoint-specific video generation process and objective.
- [Modalities and I/O](../../models/cosmos3-nano/modalities-and-io.md) specifies frame, context, action, and temporal contracts.
- [Action modeling](../../models/cosmos3-nano/action-modeling.md) distinguishes passive continuation from forward and joint action-conditioned generation.
- [Evaluation](../../models/cosmos3-nano/evaluation.md) and [limitations](../../models/cosmos3-nano/limitations.md) contain model-specific evidence; generic video quality should not be projected onto untested control regimes.
- [Paper entries](../../papers/README.md) preserve exact protocols for representative video world models.
- [Cosmos-Predict2.5](../../papers/cosmos-predict2-5/paper.md) instantiates latent rectified-flow video prediction, clean visual prefixes, and a Bridge action-conditioned specialist; its paper entry preserves exact protocols and evidence limits.
- [IRASim](../../papers/irasim/paper.md) instantiates SDXL-latent trajectory-to-video diffusion with a clean historical prefix, per-frame action modulation, autoregressive clip chaining, and downstream candidate ranking.

## Sources

- [FND-OH-VIDEO-2015] Oh et al., *Action-Conditional Video Prediction using Deep Networks in Atari Games*, NeurIPS 2015.
- [REP-MATHIEU-2016] Mathieu, Couprie, and LeCun, *Deep Multi-Scale Video Prediction Beyond Mean Square Error*, ICLR 2016, arXiv:1511.05440.
- [REP-VIDEO-PREDICTION-2016] Finn, Goodfellow, and Levine, *Unsupervised Learning for Physical Interaction through Video Prediction*, NeurIPS 2016, arXiv:1605.07157.
- [REP-TECO-2023] Yan et al., *Temporally Consistent Transformers for Video Generation*, ICML 2023, PMLR 202.
- [REP-DIAMOND-2024] Alonso et al., *Diffusion for World Modeling: Visual Details Matter in Atari*, NeurIPS 2024, DOI:10.52202/079017-1873.
- [OBJ-VIDEO-DIFFUSION-2022] Ho et al., *Video Diffusion Models*, NeurIPS 2022, arXiv:2204.03458.
- [WFM-GENIE-2024] Bruce et al., *Genie: Generative Interactive Environments*, ICML 2024, arXiv:2402.15391.
