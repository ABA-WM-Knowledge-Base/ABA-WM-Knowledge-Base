---
id: world-model-kb.foundations.definitions-and-taxonomy.world-action-model
title: World Action Models
kind: reference
status: maintained
last_updated: 2026-08-14
owners:
  - AIBuildAI world-model group
---

# World Action Models

## Retrieval metadata

**Relevant queries:** world action model, WAM, joint action and video generation, future-conditioned action, action decoder, zero-shot policy, VLA versus WAM, or action-video consistency.

**Knowledge provided:** a scoped definition of the emerging WAM category, probability factorizations that distinguish it from forward dynamics, inverse dynamics, and direct policies, and evidence criteria for policy and transfer claims.

**Related pages:** [Forward dynamics](../problem-formulation/forward-dynamics.md) and [inverse dynamics](../problem-formulation/inverse-dynamics.md) own the component objectives; [planning and control](../decision-making/planning-and-control.md) owns closed-loop model use; [robotics and embodied AI](../embodied-systems/robotics-and-embodied-ai.md) owns embodiment contracts.

## Definition and formalism

`World action model` is an emerging research label rather than a standardized architecture. Cosmos 3 uses WAM for a mode that jointly predicts action and a corresponding visual future. DreamZero describes a WAM as a robot model that jointly models future video and action, and evaluates one such system as a closed-loop policy. The shared property is a learned joint distribution over what the agent does and how the observed world changes. [C3-TR; WAM-DREAMZERO-2026]

For current observation history `o`, goal or instruction `g`, future action sequence `a`, and future observation sequence `y`, a joint WAM can be written as

```text
p_theta(a[t:t+H-1], y[t+1:t+H] | o[<=t], g).
```

The joint can be factorized in different ways:

```text
action first:  p(a | o,g) p(y | o,g,a)
future first:  p(y | o,g) p(a | o,g,y)
interleaved:   product_k p(a[k], y[k+1] | shared history)
```

The factorization changes information flow, training targets, sampling cost, and how errors couple. A shared denoising or sequence model does not guarantee that its action and future branches use each other causally.

## Assumptions and scope

The category is most useful when contrasted with adjacent interfaces:

| Model surface | Conditional distribution | Native product |
|---|---|---|
| Direct policy or VLA | `p(a | o,g)` | action |
| Forward dynamics | `p(y | o,a,g)` | future state or observation |
| Inverse dynamics | `p(a | o,y,g)` | action explaining a transition |
| Joint WAM | `p(a,y | o,g)` | action and corresponding future |
| Planner using a world model | search over `a` with `p(y | o,a)` and an objective | selected action |

These classes can share modules or training data. The distinction concerns the modeled conditional, not product branding. A WAM becomes an executable policy only when its action output has an embodiment-specific decoder and can operate inside a stable observation-action loop at the required rate. A WAM trained with future prediction can also omit future generation at deployment; in that case, evidence is needed to determine whether the future objective supplies causal world knowledge, representation regularization, or another training effect.

The phrase `zero-shot policy` remains source- and protocol-specific. DreamZero reports zero-shot and few-shot transfer under its own training mixture, robot embodiments, tasks, and evaluation definitions. That result does not establish that every joint world-action model is zero-shot, nor that an unadapted action schema transfers safely to a new robot. [WAM-DREAMZERO-2026]

## Mechanism families

| Family | Computation | Potential advantage | Main ambiguity |
|---|---|---|---|
| Shared backbone, separate action and video heads | common features feed modality-specific decoders | efficient shared representation | video branch may act only as auxiliary regularization |
| Joint diffusion or flow model | action and future latents denoised in a shared process | multimodal joint samples | loss scale and token count can privilege one modality |
| Cascaded future-then-action model | generate or encode a desired future, then infer action | uses visual outcomes as dense goals | generated future may be infeasible or action-agnostic |
| Cascaded action-then-future model | propose action, then predict consequence | explicit counterfactual interpretation | sequential sampling adds latency and compounds error |
| Interleaved autoregressive model | alternate action and observation tokens | temporal coupling and variable horizons | exposure bias and slow token-by-token control |
| Policy with future-prediction auxiliary | future target present only during training | no rollout cost during deployment | downstream gain may not imply usable simulation |

Cosmos3-Nano exposes a base WAM generation surface and a separately post-trained DROID policy checkpoint. These are distinct evidence objects: a base joint output does not inherit closed-loop DROID policy results. [C3-TR]

## Design implications and trade-offs

The entries below are cross-paper synthesis or explicit hypotheses rather than established universal findings.

| Lever | Hypothesized mechanism | Expected signal | Regression risk | Informative comparison |
|---|---|---|---|---|
| Action-video loss ratio | changes how shared capacity represents control versus appearance | action feasibility and conditional future accuracy | attractive rollouts with weak actions, or accurate actions with collapsed futures | gradient norms and both branch metrics at fixed data/steps |
| Action chunk and visual horizon | sets temporal abstraction and prediction burden | longer skill coverage | latency, drift, or endpoint averaging | horizon-stratified closed-loop success and rollout error |
| Future branch at inference | exposes explicit imagined outcome for ranking | better candidate selection | extra sampling cost and shared hallucination | current-only versus joint decoding under equal wall-clock budget |
| Embodiment adapter | isolates units, frames, joints, and control rate | transfer with fewer target samples | semantic mismatch hidden by tensor compatibility | per-axis calibration and target-domain learning curve |
| Multi-sample generation | represents alternative actions and outcomes | best-feasible coverage | compute-driven gain or unsafe tail samples | success/coverage curves against sample count |
| Cross-embodiment video | transfers visual dynamics without source actions | improved motion prior | appearance or morphology shortcuts | held-out environment/task tests with source ablations |
| Real-time distillation or caching | reduces repeated backbone or future computation | higher control frequency | stale context or lost multimodality | success-latency Pareto curve |

Internal action-future consistency is a useful diagnostic but not sufficient evidence: both outputs can agree on the same incorrect transition. Replaying the decoded action in an independent simulator or real environment separates joint self-consistency from causal accuracy.

## Evaluation and falsification

A WAM evaluation separates five claims:

1. **Action quality:** task success, stage progress, feasibility, calibration, and constraint violations.
2. **Future quality:** state, contact, geometry, trajectory, perceptual quality, and diversity.
3. **Coupling:** whether matched action changes produce the corresponding predicted changes.
4. **Closed-loop operation:** control rate, end-to-end latency, recovery, and performance under observation shift.
5. **Transfer:** held-out task, scene, object, embodiment, and action-space adaptation curves.

Matched counterfactuals are especially discriminating: hold observation, instruction, seed policy, and sampling budget fixed; vary one action dimension or action proposal; compare both predicted and observed transitions. A joint model is weakly coupled when futures remain invariant, actions do not match the generated future, or the correlation disappears in independent replay.

Claims that the future branch improves actions are falsified when current-only and joint training/deployment variants match under equal parameters, data, compute, and seeds. Claims of zero-shot embodiment transfer are narrowed when success requires target action demonstrations, calibration, or controller-specific tuning not included in the stated zero-shot protocol.

## Failure modes

- **Shared hallucination:** the generated action and video agree internally but disagree with real dynamics.
- **Action marginal collapse:** future diversity is preserved while the action decoder emits a conditional mean or repeated chunk.
- **Future marginal collapse:** actions vary but the visual branch ignores them.
- **Semantic adapter mismatch:** units, frames, gripper signs, rates, or absolute/delta semantics differ across embodiments.
- **Loss imbalance:** high-dimensional visual tokens dominate action learning or action loss degrades generative structure.
- **Open-loop overstatement:** a successful offline sample is interpreted as stable closed-loop control.
- **Latency mismatch:** a model is accurate offline but cannot refresh actions at the target control rate.
- **Recovery blind spot:** training contains successful trajectories but insufficient disturbances, failures, or corrective behavior.
- **Evaluation coupling:** the same model or generated future supplies both prediction and judgment, concealing error.

## Cross-part instantiations

- [Cosmos3-Nano action modeling](../../models/cosmos3-nano/action-modeling.md) defines its FD, ID, and WAM surfaces, action adapters, and H-actions/H+1-states contract.
- [Cosmos3-Nano Policy-DROID](../../models/cosmos3-nano/policy.md) is a specialized checkpoint with a concrete observation/action and serving contract; it is not the base WAM identity.
- [Cosmos3-Nano Generator](../../models/cosmos3-nano/generator.md) owns diffusion/flow computation, while [modalities and I/O](../../models/cosmos3-nano/modalities-and-io.md) owns typed modality contracts.
- [Cosmos3-Nano evaluation](../../models/cosmos3-nano/evaluation.md) and [limitations](../../models/cosmos3-nano/limitations.md) record checkpoint-specific evidence and missing conditions.
- [DreamZero](../../papers/dreamzero/paper.md) instantiates a joint video-action WAM evaluated as a closed-loop robot policy; its entry preserves 14B checkpoint, DROID/AgiBot, and scoped zero-shot language boundaries.
- [Cosmos Policy](../../papers/cosmos-policy/paper.md) instantiates Predict2-2B latent-frame injection as a visuomotor policy with optional best-of-N planning; it is not Cosmos3-Nano Policy-DROID and does not inherit Predict2.5 video scores.
- [Paper entries](../../papers/README.md) can preserve DreamZero and Cosmos 3 architectures, datasets, and protocols without treating their terminology as a universal definition.

## Sources

- [C3-TR] NVIDIA, *Cosmos 3: Omnimodal World Models for Physical AI*, arXiv:2606.02800.
- [WAM-DREAMZERO-2026] Ye et al., *World Action Models are Zero-shot Policies*, arXiv:2602.15922. Primary preprint; peer-review status is not established by the source.
- [DYN-POKE-2016] Agrawal et al., *Learning to Poke by Poking: Experiential Learning of Intuitive Physics*, NeurIPS 2016.
- [PLAN-VISUAL-FORESIGHT-2017] Finn and Levine, *Deep Visual Foresight for Planning Robot Motion*, ICRA 2017, DOI:10.1109/ICRA.2017.7989324.
