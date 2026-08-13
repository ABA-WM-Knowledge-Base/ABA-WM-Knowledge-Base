---
id: world-model-kb.papers.irasim.optimization-transfer
title: IRASim Transferable Optimization Knowledge
kind: guide
status: maintained
last_updated: 2026-08-13
owners:
  - AIBuildAI world-model group
---

# IRASim Transferable Optimization Knowledge

## Retrieval metadata

**Relevant queries:** transfer IRASim, optimize action-conditioned world model, action-frame alignment, failure-rollout mixture, model-based planning, test-time scaling, reward model, long-horizon rollout, contact fidelity, frame conditioning, or Cosmos3-Nano WAM improvement.

**Knowledge provided:** falsifiable intervention patterns derived from IRASim, their attachment points, required controls, expected evidence, compute and regression risks, and invalid generalizations.

**Related pages:** [`paper.md`](paper.md) owns IRASim evidence; [`codebase.md`](codebase.md) owns implementation details; [forward dynamics](../../foundations/problem-formulation/forward-dynamics.md) owns causal prediction; [planning and control](../../foundations/decision-making/planning-and-control.md) owns search/evaluator interactions; [datasets and supervision](../../foundations/data-and-evaluation/datasets-and-supervision.md) owns trajectory mixture validity; [Cosmos3-Nano optimization playbook](../../models/cosmos3-nano/optimization-playbook.md) owns target-model intervention discipline.

## 1. Transfer discipline

IRASim supplies paper-specific mechanisms and experiments, not universal prescriptions. A transfer is justified only when the target model has the same relevant failure mode and a compatible attachment surface. Every proposed intervention below is a **hypothesis** until a controlled target-model experiment separates it from data, compute, parameter-count, sampler, and evaluator changes.

The paper contains three evidence strengths:

1. **direct architecture comparison:** Frame-Ada versus Video-Ada under the original prediction benchmark;
2. **coupled system evidence:** expert plus failure-rollout data, OpenSora initialization, world-model adaptation, reward learning, and candidate search in LIBERO/Push-T;
3. **qualitative scope probes:** keyboard/VR actions, very long rollouts, and physically implausible commands.

Do not assign causal confidence from level 2 or 3 to one component without reproducing the missing ablation.

## 2. Intervention matrix

| ID | Target failure | Mechanism transferred | Attachment surface | Primary evidence | Principal risk |
|---|---|---|---|---|---|
| `IRA-XFER-01` | future frames lag or ignore action timing | per-frame action modulation | spatial/video latent blocks | Frame-Ada primary metrics and preference | parameter or optimization confound |
| `IRA-XFER-02` | temporal blocks underuse chunk shape | hybrid local/global conditioning | spatial and temporal blocks separately | paper design versus released-code gap | stronger condition can overfit embodiment |
| `IRA-XFER-03` | output head erases action information | action-aware final projection | final normalization/output head | released legacy-bug comment | breaks checkpoint compatibility |
| `IRA-XFER-04` | planner exploits expert-only model | success/failure rollout mixture | data sampler and domain SFT | Push-T `P=0` versus `P>0` | policy-dependent coverage and unsafe collection |
| `IRA-XFER-05` | larger search does not improve realized return | co-scale model support with candidate count | data plus inference search | Push-T `P x K` grid | compute magnifies evaluator error |
| `IRA-XFER-06` | rollout realism disconnected from task value | external value/cost model | candidate-ranking layer | Push-T and real-robot cost comparison | reward misspecification |
| `IRA-XFER-07` | long rollout drifts after each chunk | generated-prefix robustness training | horizon curriculum and prefix corruption | autoregressive long-video protocol | degraded one-step detail |
| `IRA-XFER-08` | pixel metrics hide contact failures | state/contact and counterfactual probes | evaluator and auxiliary heads | limitations of reported metrics | additional labels and evaluator leakage |
| `IRA-XFER-09` | cross-embodiment action semantics collide | explicit domain action adapters | action schema registry and projections | four dataset-specific action spaces | false sharing or adapter undercapacity |
| `IRA-XFER-10` | action conditioning harms unconditional generation | stochastic condition masking and balanced regularization | action-conditioning path | released 10% condition drop | condition neglect if drop is too high |

## 3. `IRA-XFER-01`: per-frame action modulation

**Source mechanism.** IRASim maps action `a_i` to the adaptive-normalization parameters of spatial transformer operations for frame `i`, instead of compressing `a_{1:N}` into one video-level vector. Frame-Ada improves PSNR and latent L2 over Video-Ada on RT-1, Bridge, and Language-Table. [IRASRC-PAPER-V2, pp.5-9, Tables 1-3]

**Target behavior.** Improve temporal alignment of end-effector motion, gripper change, object contact, and state transition under a known action chunk.

**Attachment.** In a DiT or mixture-of-transformers Generator, embed canonical action token `a_i` and inject it into visual blocks whose token time index corresponds to predicted observation `o_{i+1}`. Prefer gated AdaLN or residual modulation over appending a low-amplitude condition once at the input. For [Cosmos3-Nano action modeling](../../models/cosmos3-nano/action-modeling.md), the relevant target is the Generator FD/WAM path, not the Reasoner text tower.

**Minimum controlled experiment.** Compare global chunk condition, per-frame condition, per-frame with matched parameter count, and shuffled frame-action alignment. Hold backbone, initialized weights, train clips, optimization, latent codec, sampler, and inference seeds fixed. Report per-frame end-effector/object trajectories, contact/state events, action sensitivity, PSNR/latent loss, and compute.

**Expected movement.** Lower frame-indexed state error and larger separation between true and shuffled/opposite actions, with no material regression in passive video quality.

**Falsification.** Reject the mechanism as the source of improvement if gains disappear under parameter matching, if shuffled action alignment performs equally, or if video metrics improve while task-state/contact fidelity does not.

## 4. `IRA-XFER-02`: hybrid local and global trajectory conditioning

The ICCV paper describes per-frame conditions in spatial blocks and a shared trajectory condition in temporal blocks. The public Frame-Ada code lacks explicit action input in temporal blocks. This mismatch creates a valuable target ablation rather than a fact to normalize away. [IRASRC-PAPER-V2, pp.5-6, 20-21; IRASRC-CODE-CURRENT]

**Hypothesis.** Local conditions are suited to frame-specific geometry, while a global trajectory representation helps temporal blocks anticipate later turns, contacts, and gripper events. The combination should reduce delayed response without destroying whole-chunk coherence.

**Experiment.** Cross `spatial in {global, per-frame}` with `temporal in {none, global, per-frame/cross-attention}`. Match projection parameters where feasible. Slice results by straight motion, reversals, contact onset, gripper transition, and long chunks. Test action permutation and future-action truncation to detect temporal leakage or overreliance.

**Falsification.** A global temporal condition is not useful if it changes neither long-horizon error nor counterfactual response, or if it improves logged trajectories while degrading unseen chunk shapes.

## 5. `IRA-XFER-03`: preserve action information through the output head

The released Frame-Ada checkpoints omit action conditioning from the final AdaLN and label this a legacy bug. [IRASRC-CODE-CURRENT, `models/irasim.py:434-441`]

**Hypothesis.** Conditioning only internal blocks permits the last shared projection to attenuate small action-dependent differences. A gated per-frame condition at the output head may strengthen precise deltas with a low parameter cost.

**Attachment and risk.** Add a zero-initialized action modulation to the final normalization/projection. For an existing checkpoint, train only this new adapter first; directly switching the branch changes the function and invalidates checkpoint equivalence.

**Evidence.** Measure action Jacobian/sensitivity, matched-action state error, output variance, and passive-video regressions. Reject if the head merely amplifies motion or creates artifacts without improving correct-direction and contact metrics.

## 6. `IRA-XFER-04`: train on policy failures, not expert demonstrations alone

IRASim's strongest decision-use lesson is distributional. Expert demonstrations contain successful, narrow trajectories; a world model used to compare policy proposals must also predict failed, off-nominal, and recovery transitions. The paper collects policy rollouts containing both successes and failures for LIBERO and Push-T. [IRASRC-PAPER-V2, pp.9-13]

**Attachment.** Introduce a versioned rollout mixture with strata for success, failure type, contact event, action magnitude, task stage, and uncertainty. Retain expert data as an anchor and make policy/checkpoint provenance explicit. In offline settings, mine failed and low-return trajectories rather than generating unsafe real-world exploration by default.

**Minimum experiment.** Hold total optimizer updates fixed and compare expert-only, expert plus equal-count successful rollouts, expert plus success/failure rollouts, and a mixture matched by state/action coverage. Evaluate candidate ranking and closed-loop result on held-out rollouts from a different policy checkpoint.

**Expected movement.** Better ranking calibration and reduced regret under bad proposals; pixel metrics may stay flat.

**Falsification.** Reject “failure labels” as the cause if coverage-matched successful data gives the same gain, or if improvements vanish on another proposal policy. Record unsafe data-collection constraints separately from model quality.

## 7. `IRA-XFER-05`: co-scale model data and test-time candidate search

Push-T provides a direct caution against search-only scaling. With no post-trained rollouts, `K=50` degrades average IoU to `0.418` from the `K=1` baseline `0.637`; with 1,000 post-trained rollouts, `K=50` reaches `0.961`. [IRASRC-PAPER-V2, pp.11-13, Table 5]

**Hypothesis.** Larger `K` samples farther into the proposal distribution and exposes unsupported regions of the learned dynamics and value model. More rollout coverage can expand the trustworthy search region, but only if it matches the candidate policy.

**Experiment contract.** Build a two-dimensional grid over data coverage `P` and candidate count `K`, with fixed proposal policy, value model training budget, and wall-time reporting. Record predicted value, realized value, top-1 ranking accuracy, regret, uncertainty, and candidate action distance from data support. Include `P=0` and large `K`; otherwise exploitation cannot be detected.

**Decision rule.** Increase candidate compute only inside a regime where realized outcome improves or remains statistically stable and calibration does not worsen. This is an evidence criterion, not a workflow scheduler.

**Falsification.** Predicted score rises while realized task value falls, or the gain disappears under fixed wall-clock budget.

## 8. `IRA-XFER-06`: separate world model from value model

IRASim predicts observations. Push-T uses a ResNet50 IoU estimator; real-robot planning compares a ResNet50 feature cost with pixel MSE, and MSE wins all three tasks. [IRASRC-PAPER-V2, pp.10-13, 22-23, Tables 5-6]

**Implication.** A better visual model does not determine the best action if the evaluator ranks outcomes incorrectly. Treat dynamics and value as separate components with separate validation sets, uncertainty, and failure slices.

**Experiment.** Cross at least two world-model checkpoints with two or more value functions. Evaluate value accuracy on ground-truth frames, on generated frames, and on adversarial or off-support generated artifacts. Then compare candidate ranking against realized outcomes. A value function that works on real frames may exploit generator artifacts.

**Falsification.** If planning gains follow the evaluator rather than the world-model improvement, assign the intervention to value learning. If all value functions fail on generated frames, improving dynamics metrics alone is insufficient.

## 9. `IRA-XFER-07`: train for generated-prefix robustness

Long IRASim rollouts chain the final generated frame into the next clip. Training, however, uses clean historical frames. This creates a prefix-distribution gap analogous to exposure bias. [IRASRC-PAPER-V2, pp.6-8, 22]

**Intervention.** During adaptation, replace some clean history latents with detached model-generated, codec-degraded, or calibrated corrupted prefixes while preserving the ground-truth action chunk and target. Curriculum probability and prefix error magnitude are controllable variables.

**Evaluation.** Report error versus chunk index, object identity/state persistence, contact errors, and decision ranking at matched rollout length. Maintain a clean-prefix short-video regression suite.

**Falsification.** Reject if long-horizon robustness does not improve beyond simple noise augmentation or if one-step fidelity regresses enough to erase downstream benefit.

## 10. `IRA-XFER-08`: action-sensitive physical evaluation

IRASim's primary metrics reward paired reconstruction, but they do not prove action use or physical correctness. Build an evaluation layer that pairs the same observation and generative seed with true, zero, shuffled, opposite, and feasible alternative actions. [IRASRC-PAPER-V2, pp.7-9, 14]

Measure:

- end-effector and object pose trajectories;
- gripper/contact event timing;
- collision and penetration violations;
- task relations such as inside/on/open/closed;
- prediction separation calibrated by action magnitude;
- candidate-ranking accuracy and realized result.

For stochastic models, use multiple samples and coverage/calibration rather than one reconstruction. A claim of improved dynamics is falsified if predictions are action-insensitive or move in the wrong direction even when PSNR improves.

## 11. `IRA-XFER-09`: explicit action adapters across embodiments

IRASim trains separate models with 2-D, 5-D, and 7-D action contracts. It does not demonstrate one universal action space. A target multi-domain model should preserve raw domain semantics and map them through explicit adapters rather than interpreting zero padding as shared physical meaning. [IRASRC-PAPER-V2, pp.19-20]

**Attachment.** Store domain/embodiment ID, raw dimension, units, coordinate frame, absolute/delta semantics, control rate, gripper convention, validity mask, and invertible normalization. Project into a shared width only after contract validation.

**Experiment.** Compare domain-specific adapters, shared adapter plus domain embedding, and naive padded sharing. Include per-axis sign/unit calibration and held-out action magnitude/rate. Evaluate transfer and negative interference per domain.

**Falsification.** Shared representation is not beneficial if one domain improves by exploiting padding artifacts while another loses calibrated directional response.

## 12. `IRA-XFER-10`: condition masking as a controllability regularizer

The released code drops the action condition for 10% of training batches. This can support an unconditional branch and prevent overdependence, but the paper does not ablate it. [IRASRC-CODE-CURRENT]

**Hypothesis.** A small condition-drop probability preserves general video priors while the conditioned branch learns action effects. Too much drop encourages action neglect, especially when observation history predicts common behavior.

**Experiment.** Sweep drop probability with a matched guidance policy and report action-shuffle separation, passive-video quality, diversity, and decision metrics. If classifier-free guidance is used, verify action tensor duplication and tune guidance separately from training drop.

**Falsification.** Dropout is harmful if action sensitivity falls without a compensating robustness or quality benefit.

## 13. Interaction map

The interventions are not independent:

- Per-frame modulation (`01`) is interpretable only after action contract calibration (`09`).
- Hybrid block conditioning (`02`) and output conditioning (`03`) change condition capacity; compare them before attributing gains to granularity.
- Failure-rollout data (`04`) expands support needed for candidate scaling (`05`).
- Candidate scaling is unsafe without a separately validated value function (`06`) and uncertainty/support diagnostics.
- Generated-prefix training (`07`) changes the state distribution and should be evaluated with action-sensitive physical metrics (`08`).
- Condition masking (`10`) can undermine every action-alignment intervention if not controlled.

A factorial or staged ablation may be statistically efficient, but the KB does not decide task order or experiment scheduling.

## 14. Invalid generalizations

- Do not infer that every action-conditioned DiT needs IRASim's exact AdaLN design; cross-attention or action tokens may already preserve frame identity.
- Do not treat higher PSNR or latent L2 as evidence of safer planning.
- Do not treat `r=0.99` from four policies on one LIBERO task as a universal evaluator guarantee.
- Do not increase `K` merely because the best Push-T row improves; `P=0` demonstrates explicit search-induced degradation.
- Do not infer that failure-rollout count alone matters; coverage, task stage, policy provenance, and label quality are confounders.
- Do not treat the qualitative implausible-action example as a safety filter; a model that ignores a dangerous action can appear physically reasonable.
- Do not transfer private v2 capabilities from the paper into the public v1 checkpoint.
- Do not claim an end-to-end planning gain when only the world model changes and the value model or proposal budget also changes.

## 15. Transfer record template

```text
Transfer ID:
Source mechanism and exact evidence:
Target failure signature:
Target-model attachment point:
Required data/action/evaluator changes:
Baseline and matched controls:
Trainable parameters and initialization:
Compute and inference-budget change:
Primary and regression metrics:
Expected movement and mechanism probe:
Confounders and interaction risks:
Minimum experiment:
Falsification result:
Observed artifact or run record:
```

## Sources

- [IRASRC-PAPER-V2] mechanism, experiments, and numerical evidence.
- [IRASRC-CODE-CURRENT] released attachment points and implementation-specific conditions.
- [IRASRC-GPC] identity of the planning comparison family.
