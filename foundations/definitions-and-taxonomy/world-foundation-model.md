---
id: world-model-kb.foundations.definitions-and-taxonomy.world-foundation-model
title: World Foundation Models
kind: reference
status: maintained
last_updated: 2026-08-12
owners:
  - AIBuildAI world-model group
---

# World Foundation Models

## Retrieval metadata

**Relevant queries:** world foundation model, WFM, general-purpose world model, pretrained simulator, interactive environment, physical-AI backbone, transfer, specialization, post-training, or scaling.

**Knowledge provided:** an attributed definition of world foundation models, a comparison of major mechanism families, adaptation and optimization variables, and evidence boundaries for claims of generality or physical competence.

**Related pages:** [World action models](world-action-model.md) covers joint future-and-action generation; [planning and control](../decision-making/planning-and-control.md) covers model use in decisions; [datasets and supervision](../data-and-evaluation/datasets-and-supervision.md) and [evaluation methodology](../data-and-evaluation/evaluation-methodology.md) cover evidence needed to establish transfer.

## Definition and formalism

`World foundation model` is an emerging, source-dependent label rather than a settled mathematical class. NVIDIA positions a WFM as a general-purpose world model pretrained on large, diverse video data and adaptable to downstream Physical-AI settings through post-training. Genie describes an 11B model trained from unlabeled Internet video as a foundation world model because one tokenizer, latent-action model, and dynamics model can generate many action-controllable environments. UniSim uses the related term *interactive real-world simulator* for a conditional video model learned from heterogeneous interaction data. These definitions overlap in reuse and conditional prediction, but differ in domain, supervision, action semantics, and intended deployment. [C1-TR; WFM-GENIE-2024; WFM-UNISIM-2024]

A useful common abstraction is a reusable conditional sequence model

```text
p_theta(x[t+1:t+H] | x[<=t], u[t:t+H-1], c, m)
```

where `x` is an observable or latent world state, `u` is an optional control representation, `c` is semantic or task context, and `m` identifies modalities, views, domains, or embodiments. The model can expose only a subset of these variables. A text-to-video generator with no action channel, an action-conditioned interactive model, and a latent dynamics model can therefore share a family resemblance without having interchangeable decision interfaces.

Foundation status describes breadth, reuse, and adaptation intent. It does not by itself establish causal identification, general physical laws, calibrated uncertainty, an executable policy, or safe closed-loop behavior.

## Assumptions and scope

The foundation-model hypothesis is that shared structure learned across large and diverse experience reduces the target-domain data or compute needed for useful specialization. The hypothesis has three separable components:

1. **Representation transfer:** pretrained perceptual and temporal features remain useful in a new domain.
2. **Dynamics transfer:** learned regularities about change, interaction, or control improve future prediction under a target distribution.
3. **Interface transfer:** the model can ingest the target conditions and emit outputs with usable semantics after adaptation.

A reported gain on one component is not evidence for all three. For example, a pretrained video model can improve visual features while its action interface remains incompatible with a new robot. Likewise, an interactive model can respond to latent controls without mapping those controls to physical units.

The scope excludes a universal claim that more parameters or more video necessarily improves decision utility. Data coverage, tokenization, supervision, inference budget, and target interface can dominate scale. Cosmos, Genie, and UniSim provide concrete instances, not a proof that one architecture or objective is universally optimal.

## Mechanism families

| Family | Predictive interface | Typical supervision | Reusable strength | Structural limitation |
|---|---|---|---|---|
| Unconditional or semantic video foundation model | future media from media and text | large video and captions | appearance, motion, semantic composition | no identified physical action channel |
| Explicit action-conditioned simulator | future observations from current context and controls | video aligned with language, camera, robot, or game actions | counterfactual rollouts under known controls | action schemas differ across domains |
| Latent-action interactive model | future tokens from inferred discrete/latent actions | unlabeled video plus learned inverse/latent action objective | interaction learning without recorded controls | latent actions need not match physical commands |
| Omnimodal world model | flexible combinations of text, media, audio, and action | mixed autoregressive and generative objectives | shared backbone and cross-modal transfer | capabilities remain objective-, adapter-, and checkpoint-specific |
| Decision-relevant latent model | latent transition, reward, value, or policy predictions | interaction and task signals | compact planning state and efficient rollouts | may omit photorealistic or task-irrelevant world detail |

Genie is evidence that an inferred latent action space can support controllable generated environments in its evaluated domains. UniSim is evidence that heterogeneous controls can be mapped into a common conditional video interface and used in its demonstrated simulator-to-real experiments. Neither result establishes physical action calibration outside the tested settings. [WFM-GENIE-2024; WFM-UNISIM-2024]

## Design implications and trade-offs

The following implications synthesize the cited mechanisms; they are not universal empirical laws.

| Lever | Mechanistic rationale | Expected benefit | Competing risk | Discriminating evidence |
|---|---|---|---|---|
| Data-domain mixture | shared temporal structure can transfer across domains | broader representations and tail coverage | negative transfer or shortcut learning between fragmented datasets | held-out domain matrix at fixed token and compute budget |
| Temporal tokenizer and compression | determines which motion and contact events remain representable | longer context or cheaper rollouts | short contacts and high-frequency control can be aliased | event accuracy and control sensitivity by timescale |
| Conditioning vocabulary | connects text, trajectories, camera motion, or physical actions to futures | controllability and reuse | semantically similar controls can carry incompatible units | matched counterfactual response under frozen context |
| Latent versus recorded actions | latent actions permit learning from unlabeled video | greater data scale | latent codes may be non-identifiable or non-executable | alignment with recorded controls and downstream adaptation cost |
| Domain post-training | specializes a shared prior to target observations and dynamics | target fidelity with less target data | catastrophic loss of broad capability | target gain plus general-domain regression matrix |
| Multi-view and temporal alignment | preserves common events across sensors | stronger geometry and interaction evidence | view-order or timestamp shortcuts | shuffled-view, offset-time, and held-out-layout tests |
| Candidate sampling or search | explores multiple plausible futures at inference | coverage of multimodal outcomes | higher compute can masquerade as a model gain | quality and utility curves against equalized compute |

An optimization hypothesis is well specified when it names the target transfer deficit, the WFM component responsible for that deficit, the changed variable, a matched baseline, and both target and retention measurements. “Scale the WFM” is not a causal hypothesis until scale is separated from data, steps, and inference budget.

## Evaluation and falsification

A WFM claim can be decomposed into independent evidence layers:

| Claim | Supporting measurement | Evidence that falsifies or narrows it |
|---|---|---|
| Broad generative prior | quality and coverage across held-out domains and conditions | gains restricted to near-duplicate training domains |
| Controllable simulation | response to matched control counterfactuals | visually plausible futures invariant to controls |
| Physical prediction | object, state, contact, trajectory, and event metrics over increasing horizon | perceptual quality rises while physical event accuracy does not |
| Transferable foundation | target performance versus target-data and compute curves | training from scratch matches the pretrained model at equal resources |
| Efficient specialization | target gain per sample, update, and FLOP | gain disappears when adaptation budget is equalized |
| Decision utility | planning return, policy improvement, or task success in the real evaluator | improved video score with no downstream decision gain |

Cross-model comparisons retain checkpoint identity, training-data scope, adaptation method, target data, sampling budget, horizon, evaluator, and compute. A benchmark average cannot establish a universal simulator because benchmark coverage is finite and often omits intervention, embodiment shift, or long-horizon recovery.

## Failure modes

- **Visual prior mistaken for dynamics:** generated motion is coherent but insensitive to action or violates object state and contact.
- **Latent-action ambiguity:** a controllable latent code has no stable mapping to a physical controller or changes meaning across scenes.
- **Mixture shortcut:** dataset or embodiment identity predicts the target more easily than the intended causal condition.
- **Temporal aliasing:** compression removes events that determine control outcomes, such as grasp closure or collision onset.
- **Autoregressive drift:** small prediction errors compound as generated states re-enter the model context.
- **Adaptation forgetting:** target post-training improves one domain while degrading broader capabilities or other control interfaces.
- **Evaluation leakage:** near-duplicate clips, scenes, or trajectories inflate apparent transfer.
- **Compute confounding:** a result attributed to model quality is produced by more candidates, steps, resolution, or context.

These are diagnostic categories. Their relevance depends on the model surface and target task.

## Cross-part instantiations

- [Cosmos-Predict2.5](../../papers/cosmos-predict2-5/README.md) is a video-based latent world foundation model whose base and action-conditioned specialist surfaces must be distinguished when inferring intervention or control capability.

- [Cosmos3-Nano architecture](../../models/cosmos3-nano/architecture.md) instantiates an omnimodal mixture-of-transformers design with distinct autoregressive and diffusion computation.
- [Cosmos3-Nano Generator](../../models/cosmos3-nano/generator.md) owns media and continuous-modality generation details; [Reasoner](../../models/cosmos3-nano/reasoner.md) owns language prediction and physical reasoning.
- [Cosmos3-Nano data](../../models/cosmos3-nano/data.md) and [post-training](../../models/cosmos3-nano/post-training.md) expose concrete mixture and specialization variables.
- [Cosmos3-Nano evaluation](../../models/cosmos3-nano/evaluation.md) records model-specific metrics; those results inherit the evidence boundaries above.
- [Paper entries](../../papers/README.md) can preserve the experiment-specific mechanisms and results of Cosmos-Predict1, Genie, UniSim, and other WFM systems without duplicating the model-independent definition here.

## Sources

- [C1-TR] NVIDIA et al., *Cosmos World Foundation Model Platform for Physical AI*, arXiv:2501.03575; official NVIDIA report registered by the Cosmos3-Nano entry.
- [WFM-GENIE-2024] Bruce et al., *Genie: Generative Interactive Environments*, ICML 2024, PMLR 235:4603-4623.
- [WFM-UNISIM-2024] Yang et al., *Learning Interactive Real-World Simulators*, ICLR 2024 oral.
- [C3-TR] NVIDIA, *Cosmos 3: Omnimodal World Models for Physical AI*, arXiv:2606.02800.
