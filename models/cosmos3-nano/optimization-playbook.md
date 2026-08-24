---
id: world-model-kb.models.cosmos3-nano.optimization-playbook
title: Cosmos3-Nano Optimization Design Reference
kind: guide
status: maintained
last_updated: 2026-08-24
owners:
  - AIBuildAI world-model group
---

# Cosmos3-Nano Optimization Design Reference

## Retrieval metadata

**Relevant queries:** optimization hypothesis, failure diagnosis, intervention variable, controlled comparison, metric selection, experiment artifact, or result interpretation.

**Knowledge provided:** optional experiment-design patterns connecting failure signatures, mechanisms, controllable variables, measurements, confounders, and evidence quality. This page does not prescribe AIBuildAI task planning or execution.

**Related pages:** [Reproduction](reproduction.md) contains observed execution state; [Inference](inference.md) contains runtime references; [Evaluation](evaluation.md) contains model-bound results. Foundation owners provide the [general problem formulation](../../foundations/problem-formulation/problem-formulation.md), [evaluation methodology](../../foundations/data-and-evaluation/evaluation-methodology.md), and [open problems](../../foundations/research-frontiers/open-problems.md). [Original RoboCasa optimization knowledge](../../benchmarks/robocasa/optimization-reference.md) owns benchmark-side slices; the [X-WAM playbook](../x-wam/optimization-playbook.md) provides a distinct RGB-D/action comparator.

## Experiment description model

A model-improvement claim is easier to interpret when every node in this chain is explicit:

```text
target capability
  -> observed failure signature
  -> candidate mechanism
  -> controllable implementation surface
  -> minimum discriminating intervention
  -> target metric and regressions
  -> artifact bundle
  -> result interpretation
```

Missing nodes reduce attribution strength. In particular, an output that "looks better" is not a failure definition, and a larger dataset or longer run is not a causal hypothesis.

## Evidence prerequisites

Variables that make an intervention interpretable include:

- exact base or post-trained checkpoint ID and immutable revision;
- Reasoner, Generator, action/WAM, or Policy-DROID surface;
- code revision and resolved configuration precedence;
- input, output, modality, coordinate, and time contracts;
- baseline artifact that executes the same task;
- primary metric with direction, aggregation, and uncertainty method;
- fixed evaluation slice and contamination boundary;
- compute, storage, wall-time, and safety budget.

Ambiguous checkpoint identity, an unobserved base execution path, an undefined action contract, or a non-discriminating evaluation prevents strong causal attribution. See [Manifest](manifest.yaml), [Modality contracts](modalities-and-io.md), and [Execution state](reproduction.md).

## Surface selection

| Observed failure | Diagnose first | Preferred first intervention | Avoid as first response |
|---|---|---|---|
| Wrong object, state, or relation in Reasoner text | Image/video sampling, crop, token budget, prompt/output parser | Targeted supervised examples plus hard negatives | Full-model training without a slice-level baseline |
| Correct perception but invalid physical inference | Temporal coverage, event boundary, causal labels | Physical reasoning SFT or verifier-filtered trajectories | More verbose chain-of-thought alone |
| Correct facts but unusable plan | Plan schema, preconditions, ordering, state transitions | Structured plan supervision and execution-grounded scoring | Treating free-form prose as controller actions |
| Generator ignores a condition | Condition serialization, control encoder, dropout, CFG | Adapter/control curriculum or condition-loss adjustment | Increasing denoising steps without measuring adherence |
| Realistic video with impossible contacts | State/action alignment, temporal rate, horizon, domain mixture | Physics-rich data, action conditioning, transition-aware objective | Optimizing only perceptual quality |
| Correct short-horizon action but long rollout drifts | Frame, normalization, action age, replanning interval | Interface correction or receding-horizon policy evaluation | Changing model capacity before contract tests |
| Policy works on DROID but fails target embodiment | Camera/state/action schema diff | Deterministic adapters, then target-domain post-training | Assuming equal tensor shape means equal semantics |
| OOM, startup, route, or dependency failure | Backend/component/resource classification | Runtime/configuration fix | Data or weight changes |

A low-cost change that can falsify the candidate mechanism while preserving checkpoint and evaluation identity often provides the most information per unit of compute.

## Diagnosis protocol

### 1. Localize the failure

Assign each example one primary failure label and optional secondary labels:

| Surface | Failure labels |
|---|---|
| Reasoner | `perception`, `grounding`, `temporal_order`, `state_tracking`, `physical_causality`, `spatial_reasoning`, `plan_precondition`, `plan_order`, `hallucination`, `format` |
| Generator | `condition_omission`, `identity_drift`, `geometry`, `contact`, `temporal_discontinuity`, `motion`, `audio_sync`, `artifact`, `diversity_collapse`, `safety` |
| Action/WAM | `schema`, `frame`, `normalization`, `timing`, `action_feasibility`, `state_prediction`, `rollout_drift`, `domain_mismatch` |
| Policy | `observation_adapter`, `language_grounding`, `reach`, `grasp`, `manipulation`, `recovery`, `collision`, `timeout`, `saturation` |

Keep raw outputs and label instructions. Do not let an LLM judge silently redefine the label set between experiments.

### 2. Separate interface failure from capability failure

Run deterministic checks before model changes:

- image order, resolution, crop, color space, frame timestamps, and blank-image behavior;
- prompt template and generation parser;
- action vector names, order, dtype, bounds, units, coordinate frame, absolute/delta semantics, frequency, and normalization round trip;
- seed, sampler, guidance, steps, and context length;
- checkpoint component and mode flags.

An interface error can produce finite, fluent, or visually plausible output. Passing shape checks is therefore necessary but insufficient.

### 3. Establish a stratified baseline

Report the aggregate metric and the failure slices most likely to move. Use fixed examples for debugging and a held-out evaluation set for decisions. Retain per-example outputs so an aggregate gain can be traced to solved cases, regressions, or judge drift.

### 4. Rank candidate mechanisms

For each mechanism, record:

```yaml
mechanism_id: M-001
failure_slice: temporal_order
observation: "event B is described before event A in 37% of long clips"
candidate_cause: insufficient event-boundary coverage in the adaptation mixture
alternative_causes:
  - frame sampler omits the transition
  - prompt requests an unordered summary
discriminating_test: compare dense boundary sampling with the current sampler before training
```

Prefer a diagnostic change to a training run when it can distinguish two causes at much lower cost.

## Reasoner optimization

The Reasoner is an autoregressive text generator conditioned on text and optional visual input. It is not the continuous action decoder. Its optimization targets should therefore be phrased as grounded text, structured reasoning, or planning quality. [C3-TR, pp.9-14 and pp.17-20; C3-HF]

| Target | Data lever | Objective or parameter lever | Required evaluation |
|---|---|---|---|
| Object/state grounding | Cropped positives, visually similar negatives, occlusion and viewpoint variation | Vision-language SFT; selective connector/tower updates | Detection-grounded factuality and general VLM regression |
| Temporal/causal reasoning | Event-boundary clips, before/after counterfactuals, state-transition labels | Video SFT; sequence or rationale supervision | Temporal-order and causality slices with prompt-matched judge |
| Physical plausibility | Contact, support, collision, permanence, tool-use examples; negative futures | Physical-AI SFT; preference/verifier filtering if available | Physical correctness, calibration, and hallucination rate |
| Embodied planning | State, goal, ordered subtask, precondition, termination tuples | Structured plan SFT and schema-constrained decoding | Plan validity, executability proxy, and downstream policy ablation |
| Robust concise output | Format-diverse prompts and counterexamples | Response-format SFT; decoding constraints | Task score, format validity, length, latency |

Interpretation patterns:

1. If the missing visual evidence is absent from the sampled input, change sampling before training.
2. If facts are present but prose is structurally unusable, constrain schema or post-train format before changing core reasoning capacity.
3. If plan conditioning is proposed for a policy, compare policy-only against frozen-plan-conditioned policy with paired rollout seeds; the plan must not access oracle future state.
4. Report extra inference cost and plan factuality alongside task success.

## Generator optimization

The Generator uses rectified-flow denoising over continuous visual, audio, and action representations while consuming autoregressive context. Improvements may come from data, condition interfaces, training objectives, adapters, or sampling. Do not attribute a sampling-only improvement to model learning. [C3-TR, pp.9-14, pp.25-32; C3-FW-OMNI-MOT]

### Lever hierarchy

1. **Contract:** validate modality serialization, control inputs, masks, duration, resolution, frame rate, and task mode.
2. **Sampler:** sweep denoising steps, guidance, seed count, and scheduling with fixed weights.
3. **Adapter/control path:** change condition encoder or adapter capacity when adherence fails but base quality remains strong.
4. **Post-training:** adapt to domain, control, or quality targets with a fixed base and mixture.
5. **Base-weight training:** reserve for failures that persist across contracts, sampling, and targeted adaptation.

### Metric bundles

| Optimization target | Minimum metric bundle |
|---|---|
| Visual quality | Perceptual quality, artifact rate, diversity, prompt/condition adherence |
| Temporal quality | Temporal consistency, motion quality, identity preservation, event completion |
| Physical prediction | Object state, contact/support, trajectory feasibility, action-conditioned transition, calibrated uncertainty |
| Audio-video | Semantic alignment, temporal synchronization, audio quality, visual regressions |
| Inverse dynamics | Action error by dimension, feasibility, multimodal ambiguity handling, downstream rollout impact |

Perceptual metrics and PSNR can disagree with task-relevant physics because multiple futures may be plausible. Never use one visual similarity number as the sole selection criterion for a world model. [C3-TR, pp.65-67]

## Action and WAM optimization

Action optimization begins with a domain contract, not a loss function. The Framework exposes forward-dynamics, inverse-dynamics, and WAM modes, while training recipes and specialized checkpoints may use different action-mode names or adapters. Bind every experiment to the resolved model configuration. [C3-FW-ARGS; C3-FW-ACTION]

### Action-contract fields

```yaml
observation:
  cameras: []
  image_size: null
  state_fields: []
  timestamp_rule: null
action:
  fields: []
  shape: null
  units: []
  coordinate_frame: null
  semantics: absolute_or_delta
  frequency_hz: null
  horizon: null
  normalization: null
controller:
  type: null
  limits: null
  control_decimation: null
```

One progressively higher-risk evidence sequence is:

1. golden observation fixture and pixel/state equality tests;
2. action normalize-denormalize round trip and boundary tests;
3. open-loop output shape, dtype, bounds, and latency;
4. offline prediction/action metrics on a frozen split;
5. shadow or simulator execution with safety filters;
6. paired closed-loop rollouts;
7. only then change model weights.

For forward dynamics, measure both media plausibility and task state. For inverse dynamics, acknowledge that several action sequences can explain the same transition. For WAM, evaluate generated actions and predicted consequences separately so one head cannot conceal failure in the other.

## Policy-DROID adaptation

`nvidia/Cosmos3-Nano-Policy-DROID` is a DROID-specific post-trained checkpoint, not a universal base-policy guarantee. Its reported interface includes task text, proprioception, a three-view 540 x 640 visual canvas, and 32-step absolute joint-position actions at 15 Hz. Bind exact semantics to the fixed implementation before reuse. [C3-TR, pp.31-32; C3-POLICY-DROID-HF; C3-FW-POLICY-DROID-DOC]

### Adaptation gates

| Gate | Required pass condition | Model updates allowed? |
|---|---|---|
| G0 identity | Checkpoint, code, and source interface fixed | No |
| G1 observation adapter | Golden fixtures match camera/state contract | No |
| G2 action adapter | Round-trip, units, frames, limits, and timing pass | No |
| G3 open-loop baseline | Finite actions, correct shape, bounded latency, offline metrics | No |
| G4 shadow/simulator safety | No uncontrolled execution; safety filter and trace complete | No |
| G5 zero-shot closed loop | Fixed safe tasks, seeds, evaluator, and failure taxonomy | No |
| G6 target post-training | Matched initialization and data-budget comparisons | Yes |
| G7 scaled evaluation | Held-out tasks, robustness slices, recovery and regressions | Yes |

If zero-shot performance is near zero, compare DROID initialization, relevant multi-task initialization, and base/pre-trained initialization under the same target-data and compute budget. Do not conclude that one initialization is superior from unmatched steps or exposures. The Cosmos 3 report's transfer results motivate such initialization comparisons but do not establish zero-shot RoboCasa compatibility. [C3-TR, pp.67-70]

## Data and training intervention evidence

[Data](data.md), [Training](training.md), and [Post-training](post-training.md) contain the state needed to interpret mixture or weight changes.

- Preserve a frozen data manifest with source, license, preprocessing, modality, domain, sampling weight, and deduplication group.
- Compare exposure, not only nominal dataset size. Log examples, tokens/frames, optimizer steps, global batch, and sampling probability.
- Separate new-domain gain from general-capability loss with a stable regression suite.
- Use the smallest parameter-update scope compatible with the hypothesis: adapter, head, selected tower, then full model.
- Match effective batch, learning-rate schedule, optimizer state, precision, sequence/horizon, and compute when attributing a gain.
- When synthetic or model-generated data is used, retain generator identity, prompt, filter, acceptance rate, and contamination checks.
- Never train on the decision test set or tune repeatedly against a hidden leaderboard without tracking exposure.

## Experiment specification

An immutable experiment record can use a structure equivalent to:

```yaml
experiment_id: c3n-<surface>-<date>-<sequence>
hypothesis: null
failure_slice: null
base:
  checkpoint_id: null
  checkpoint_revision: null
  code_revision: null
  parent_artifact: null
surface: reasoner_or_generator_or_action_or_policy
intervention:
  primary_factor: null
  unchanged_factors: []
data:
  train_manifest: null
  validation_manifest: null
  test_manifest: null
  exposure_budget: null
runtime:
  resolved_config: null
  compute_budget: null
evaluation:
  primary_metric: null
  minimum_effect: null
  regressions: []
  seeds: []
stop_conditions: []
accept_rule: null
reject_rule: null
artifacts: []
```

The `hypothesis` is most useful when it predicts which slice moves and why. A single causal change in `primary_factor` strengthens attribution. When multiple coupled changes are technically necessary, ablations or an explicit attribution limitation preserve interpretability.

## Comparison design

For action-conditioned rollout and planning hypotheses, [IRASim's transfer entry](../../papers/irasim/optimization-transfer.md) provides paper-specific controls for frame/action alignment, success/failure rollout coverage, candidate-count scaling, and independent value-model validation. These are optional knowledge inputs; this page remains the owner of Cosmos3-Nano experiment contracts.

Use these baselines when applicable:

- unchanged checkpoint and inference configuration;
- inference-only tuning with fixed weights;
- parameter-matched or compute-matched adapter;
- data-matched fine-tuning from alternative initialization;
- target intervention without the proposed auxiliary loss;
- oracle or interface upper bound when diagnosing adapters;
- trivial and strong non-Cosmos baselines for metric calibration.

For stochastic generation or closed-loop robotics, use paired seeds or initial states when possible. Report the distribution, not only the best sample. Best-of-N comparisons must use equal N and equal selection information.

## Result interpretation patterns

Evidence supporting an intervention is stronger when:

1. the primary metric exceeds the preregistered minimum effect;
2. uncertainty or repeated seeds support the direction;
3. critical regression and safety limits pass;
4. the artifact bundle is complete;
5. the mechanism remains plausible under ablations;
6. added compute, latency, memory, and data cost are recorded.

Evidence argues against the hypothesis when the target slice does not move, the gain disappears under matched compute, or regressions exceed declared limits. An inadequate evaluator, interface, or sample size leaves the result inconclusive. Repeated adjustment against the same evaluation set increases selection bias unless every exposure is recorded.

## Artifact contract

Retain at minimum:

- experiment contract and immutable parent identifiers;
- exact data manifests and preprocessing hashes;
- source diff or configuration diff;
- resolved runtime configuration, environment, and command;
- training curves, optimizer and scheduler state, and checkpoint manifest;
- raw per-example predictions or rollouts;
- evaluator versions, prompts, and raw judgments;
- aggregate and slice metrics with uncertainty;
- failure labels and representative regressions;
- resource use, wall time, and exit state;
- final accept/reject/escalate decision with rule evaluation.

Narrative summaries are not substitutes for the underlying artifacts. Completed execution observations belong in [Reproduction](reproduction.md), while unresolved evidence questions belong in the [Research registry](research-queue.md).

## Invalidity and deployment-risk signals

Unresolved credentials, licenses, model identity, evaluation contamination, or robot action semantics prevent a result from supporting the intended claim. Non-finite loss, output-contract failure, resource exhaustion, safety-filter rejection, or mutation of an immutable input are run-invalidity or deployment-risk signals.

Critical regressions and safety-limit failures are evidence against promoting a candidate checkpoint. Preserving failed checkpoints and their artifacts supports diagnosis and does not imply deployment. Any stop, rollback, promotion, or deployment decision remains outside the authority of this KB.

## Sources

Source records are resolved through [`sources.yaml`](sources.yaml): `C3-TR`, `C3-HF`, `C3-POLICY-DROID-HF`, `C3-FW-OMNI-MOT`, `C3-FW-ARGS`, `C3-FW-ACTION`, and `C3-FW-POLICY-DROID-DOC`.
