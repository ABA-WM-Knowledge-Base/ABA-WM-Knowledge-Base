---
id: world-model-kb.models.cosmos3-nano.research-queue
title: Cosmos3-Nano Open Research Registry
kind: record
status: maintained
last_updated: 2026-08-24
owners:
  - AIBuildAI world-model group
---

# Cosmos3-Nano Open Research Registry

## Retrieval metadata

**Relevant queries:** unresolved question, missing evidence, dependency, discriminating experiment, source conflict, or open optimization hypothesis.

**Knowledge provided:** a descriptive registry of unresolved questions, known facts, missing evidence, possible discriminating experiments, and closure evidence. Its section order and dependency-impact labels do not schedule AIBuildAI work.

**Related pages:** canonical topic pages contain established model knowledge; [Reproduction](reproduction.md) contains completed execution observations; [Optimization reference](optimization-playbook.md) contains experiment-design patterns. [Open problems](../../foundations/research-frontiers/open-problems.md) owns cross-model unknowns; [Original RoboCasa](../../benchmarks/robocasa/README.md) owns benchmark uncertainties; [X-WAM research](../x-wam/research-queue.md) owns comparator-specific unknowns. This page retains only Cosmos3-Nano-specific questions.

## Registry semantics

Dependency-impact labels describe what remains scientifically uninterpretable while evidence is missing; they do not express scientific interest or AIBuildAI scheduling priority:

- `critical`: blocks trustworthy execution, control, or attribution.
- `decision`: blocks selection among plausible optimization paths.
- `traceability`: improves completeness or historical reproducibility but does not block a minimum baseline.

States are evidence-record states, not Agent or workflow states. `ready` means the listed dependencies appear available; `blocked` means at least one named evidence dependency is absent; `in_progress` records that an immutable experiment contract exists; `resolved` means the closure rule is met; and `superseded` points to a narrower or corrected question. These labels inform reasoning but do not instruct AIBuildAI to start, stop, schedule, or abandon work.

Each item follows this schema:

```yaml
id: RQ-<SURFACE>-<NNN>
dependency_impact: critical_or_decision_or_traceability
state: ready_or_blocked_or_in_progress_or_resolved_or_superseded
decision: decision unlocked by resolution
known: facts already owned by canonical pages
unknown: one discriminating uncertainty
depends_on: queue IDs or execution gates
minimum_experiment: smallest causal test
metrics: pass/fail observations or quantitative measures
artifacts: immutable closure bundle
closure_rule: exact condition for state transition
```

## Dependency graph

```text
RQ-HOSTED-001 ----> hosted Reasoner baseline
RQ-LOCAL-001 -----> local Reasoner baseline ----> RQ-REASONER-001
RQ-GEN-001 --------> Generator baseline --------> RQ-GEN-002
RQ-ACTION-001 -----> action contract -----------> RQ-POLICY-001
RQ-POLICY-001 -----> target interface ----------> RQ-POLICY-002
RQ-POLICY-002 -----> safe zero-shot baseline ---> RQ-TRANSFER-001
RQ-EVAL-001 -------------------------------------> all optimization decisions
```

## Critical dependency impact

### RQ-HOSTED-001 - Hosted Reasoner route availability

- **Dependency impact:** `critical`
- **State:** `blocked`
- **Decision:** whether the hosted surface can provide the first real image-conditioned Reasoner baseline.
- **Known:** the exact `nvidia/cosmos3-nano-reasoner` requests reached the configured chat-completions endpoint in two timestamped runs; both fixed cases returned HTTP 404. No fallback model was used. [LOCAL-REPRO-20260809]
- **Unknown:** whether the public route is unpublished, entitlement-restricted, region/organization-scoped, or affected by a service-routing defect.
- **Depends on:** external service state or an NVIDIA entitlement/route response.
- **Minimum experiment:** retain an authenticated `GET /v1/models` response with timestamp and request ID; if and only if the exact ID is present, run both fixed image cases once with the existing harness.
- **Metrics:** exact ID presence; HTTP status; returned model field; non-empty content for both cases.
- **Artifacts:** sanitized catalog response, headers/request IDs, both request objects, both raw response JSON files, extracted outputs, and run summary.
- **Closure rule:** resolve as `available` only when both cases meet the hosted acceptance contract; resolve as `unavailable_under_scope` when NVIDIA provides a retained statement defining the unavailable account/region/service scope. A repeated 404 without new service evidence leaves the item blocked.

The hosted service does not expose a checkpoint SHA. Even a successful route would not close local-revision reproducibility. [C3-BUILD; C3-HF]

### RQ-LOCAL-001 - Local Reasoner reference baseline

- **Dependency impact:** `critical`
- **State:** `blocked`
- **Decision:** whether subsequent Reasoner changes can be compared against the fixed open checkpoint without hosted-service ambiguity.
- **Known:** official backend observations place Reasoner-only BF16 inference at approximately 16-17 GB, while the recorded local GPU has 8,188 MiB. [C3-REASONER-COOKBOOK; LOCAL-ENV-20260809]
- **Unknown:** exact output, latency, and peak memory for the fixed revision and two cases on an adequately provisioned runner.
- **Depends on:** supported Linux runner with sufficient GPU memory.
- **Minimum experiment:** load `nvidia/Cosmos3-Nano@411f42a8fdfb8c5b2583cb8786e0938f49796eaa` through the fixed Transformers path and execute the `caption` and `robot_planning` cases with fixed generation settings.
- **Metrics:** load success, non-empty output, duration, peak allocated/reserved VRAM, and input hash match.
- **Artifacts:** environment lock, resolved snapshot revision, processor/generation inputs, raw outputs, logs, memory trace, and run summary.
- **Closure rule:** resolve when both outputs and the complete local acceptance bundle are retained; an OOM on a runner below the planned capacity does not resolve model executability.

### RQ-GEN-001 - Fixed Generator T2I baseline and capacity

- **Dependency impact:** `critical`
- **State:** `blocked`
- **Decision:** which hardware and runtime configuration may be used for Generator optimization.
- **Known:** Framework documentation lists a 32 GB Nano inference requirement. Separately, a backend comparison observed approximately 34 GB for a single-GPU Framework **Reasoner** workload; it is not a measured Generator peak. [C3-FW-FAQ; C3-REASONER-COOKBOOK]
- **Unknown:** peak allocated, reserved, and device-reported memory for the fixed T2I smoke contract, with and without guardrails, on the selected Framework revision.
- **Depends on:** Linux GPU runner in at least the 48 GB class and fixed checkpoint snapshot.
- **Minimum experiment:** run official `inputs/omni/t2i.json` at seed 0 with fixed revisions; record three memory measures and resolved arguments; repeat only the guardrail factor if access permits.
- **Metrics:** decodable output, wall time, peak memory by measure, and safety-stage state.
- **Artifacts:** input, command, `sample_args.json`, `sample_outputs.json`, image, environment, logs, memory trace, and checkpoint file manifest.
- **Closure rule:** resolve when a reproducible workload-specific capacity row exists. Do not collapse the result into a universal minimum-VRAM number.

### RQ-ACTION-001 - Base Nano action-mode contract

- **Dependency impact:** `critical`
- **State:** `blocked`
- **Decision:** whether base Nano can serve as the initial forward-dynamics, inverse-dynamics, or WAM model for the target robot domain.
- **Known:** Framework arguments expose `forward_dynamics`, `inverse_dynamics`, and `wam`; action generation depends on checkpoint configuration, `domain_name`, action metadata, and the action adapter. [C3-FW-ARGS; C3-FW-ACTION]
- **Unknown:** which public Nano configurations and domain adapters expose each action mode, and the exact raw/normalized action semantics for the official robot example.
- **Depends on:** Generator-capable runner and fixed action example.
- **Minimum experiment:** execute `inputs/omni/action_policy_robot.json` without target-domain changes; capture resolved model configuration, adapter, raw action, normalized action, optional predicted media, and mode-specific failures.
- **Metrics:** mode availability, output shape/dtype/range, normalization invertibility, media decode state, and latency.
- **Artifacts:** fixed input, resolved configuration, model/checkpoint identifiers, raw output arrays, semantic field map, logs, and summary.
- **Closure rule:** resolve per mode only when an executable example and semantic mapping exist. One mode must not imply availability of the other modes.

### RQ-POLICY-001 - Target observation and action interface

- **Dependency impact:** `critical`
- **State:** `blocked`
- **Decision:** whether Policy-DROID can be connected safely to a selected RoboCasa embodiment and task.
- **Known:** the DROID policy contract uses language, proprioception, a three-view image canvas, and a 32-step absolute joint-position action chunk at 15 Hz. A same-shaped target tensor does not imply matching semantics. [C3-TR, pp.31-32; C3-POLICY-DROID-HF]
- **Unknown:** target camera roles/calibration, state field ordering, controller type, action fields, coordinate frames, units, normalization, time base, reset, and termination semantics.
- **Depends on:** one fixed RoboCasa simulator revision, embodiment, controller, and task.
- **Minimum experiment:** export ten episodes' raw interface schemas; implement pure `ObservationAdapter` and `ActionAdapter` functions; test golden observation fixtures and action round trips without loading the model.
- **Metrics:** pixel/state equality, shape/dtype, coordinate/unit agreement, round-trip error, bounds, timing, and determinism.
- **Artifacts:** simulator/config revisions, machine-readable schemas, camera calibration, normalization statistics, fixtures, adapter code, and tests.
- **Closure rule:** resolve when every source and target field has an explicit mapping or an explicit incompatibility, and all deterministic contract tests pass.

### RQ-POLICY-002 - Action-chunk execution policy

- **Dependency impact:** `critical`
- **State:** `blocked`
- **Decision:** safe mapping from a 32-step, 15 Hz predicted chunk to simulator control and replanning.
- **Known:** executing an entire open-loop chunk and receding-horizon execution impose different drift, latency, and compute tradeoffs. [C3-TR, pp.31-32]
- **Unknown:** appropriate observation rate, control decimation, action repeat, network/model latency budget, and number of actions executed before replanning.
- **Depends on:** `RQ-POLICY-001` and a passing open-loop model contract.
- **Minimum experiment:** compare full-chunk execution with replanning after 1, 4, and 8 actions on paired deterministic initial states under safety limits.
- **Metrics:** task success, state/action age, P50/P95 end-to-end latency, drift, collision, saturation, timeout, and compute.
- **Artifacts:** timestamped observation/action traces, resampling rule, controller logs, paired rollout seeds, videos, and failure labels.
- **Closure rule:** resolve when one execution policy satisfies declared safety/latency limits and dominates or is selected by a predeclared tradeoff rule.

### RQ-EVAL-001 - Target metric and evaluator contract

- **Dependency impact:** `critical`
- **State:** `blocked`
- **Decision:** whether an optimization result is attributable and task-relevant.
- **Known:** visual similarity does not uniquely measure plausible physical futures; judge-based protocols depend on judge version and prompt; several published evaluations have non-public components. [C3-TR, pp.57 and pp.65-67]
- **Unknown:** which metric bundle best predicts the selected target capability and closed-loop objective.
- **Depends on:** fixed target task and baseline outputs.
- **Minimum experiment:** label a stratified baseline set with task state, physics/contact, visual quality, and success; compute metric correlations, calibration, and disagreement cases.
- **Metrics:** rank correlation, calibration error, inter-rater agreement, slice coverage, cost, and sensitivity to known corruptions.
- **Artifacts:** evaluator version/prompt, raw judgments, human rubric if used, per-example metric table, confidence intervals, and disagreement examples.
- **Closure rule:** resolve when the primary metric and critical regressions can detect seeded failures and have a declared relationship to the target outcome. A convenient but unvalidated proxy does not close the item.

## Decision dependency impact

### RQ-REASONER-001 - Does structured Reasoner planning improve policy success?

- **Dependency impact:** `decision`
- **State:** `blocked`
- **Decision:** whether Reasoner output should enter the control stack or remain an analysis/evaluation surface.
- **Known:** Cosmos 3 reports planning and trajectory reasoning, but free-form Reasoner text is not an action tensor and does not establish a causal policy gain. [C3-TR, pp.17-20]
- **Unknown:** whether a frozen, non-oracle plan improves target policy success enough to justify latency and plan-error risk.
- **Depends on:** local or hosted Reasoner baseline, `RQ-POLICY-001`, and a fixed policy baseline.
- **Minimum experiment:** paired `policy_only` versus `frozen_plan_conditioned_policy`; generate each plan before execution, freeze it for the declared horizon, and keep policy weights, initial states, and action budget fixed.
- **Metrics:** task success, subgoal completion, recovery, plan factuality, latency, and failure attribution between planner and executor.
- **Artifacts:** image/prompt, plan, policy input, actions, rollout, seed, evaluator output, and per-failure causal label.
- **Closure rule:** accept plan conditioning only if it passes the preregistered success effect and latency/regression limits; reject if gains disappear after paired control or plan errors dominate.

### RQ-GEN-002 - Does future-video auxiliary supervision improve action quality?

- **Dependency impact:** `decision`
- **State:** `blocked`
- **Decision:** whether to retain visual future prediction during target policy post-training and/or inference.
- **Known:** Policy-DROID training uses future RGB as an auxiliary output, and inference may skip video-latent decoding. The report does not isolate a complete action-only versus action-plus-vision ablation for the target domain. [C3-TR, pp.31-32]
- **Unknown:** causal effect of the auxiliary visual objective on adaptation speed, final closed-loop success, latency, and memory.
- **Depends on:** action/policy baseline and target post-training pipeline.
- **Minimum experiment:** matched initialization, data, optimizer, updates, and action head; vary only auxiliary RGB loss. At inference, separately vary decoding to distinguish training benefit from runtime cost.
- **Metrics:** early and final action metrics, task success, sample efficiency, media quality, memory, and latency.
- **Artifacts:** paired configs, data exposure, learning curves, checkpoints, offline predictions, rollouts, and resource traces.
- **Closure rule:** resolve when the auxiliary objective's effect and decoding cost are separable under matched compute.

### RQ-TRANSFER-001 - Which initialization transfers best to RoboCasa?

- **Dependency impact:** `decision`
- **State:** `blocked`
- **Decision:** choose DROID-specific, multi-task, or base/pre-trained initialization for target post-training.
- **Known:** published transfer results show that initialization can change early adaptation behavior, but they do not establish zero-shot RoboCasa compatibility under the target protocol. [C3-TR, pp.67-70]
- **Unknown:** target-data efficiency and final performance under equal exposure and optimization budget.
- **Depends on:** `RQ-POLICY-001`, `RQ-POLICY-002`, fixed target splits, and a passing zero-shot baseline.
- **Minimum experiment:** compare eligible initializations with the same target examples, sampling order, optimizer, updates, action adapter, seeds, and evaluation cadence.
- **Metrics:** learning-curve area, steps/examples to threshold, final success, robustness slices, general-domain regression, and compute.
- **Artifacts:** initialization manifests, exact exposure logs, configs, checkpoints, paired rollouts, and uncertainty estimates.
- **Closure rule:** select using a predeclared efficiency/performance Pareto rule; report no winner if intervals and resource differences make attribution inconclusive.

### RQ-DATA-001 - Which data mixture improves target physics without catastrophic regression?

- **Dependency impact:** `decision`
- **State:** `blocked`
- **Decision:** select target, robotics, and general Physical-AI sampling weights for post-training.
- **Known:** Cosmos 3 uses staged mixtures across general, Physical-AI, robotics, and action/video data; reported recipes motivate a curriculum but do not define the optimal target-domain mixture. [C3-TR, pp.15-32 and pp.70-72]
- **Unknown:** marginal value and interference of each source at a fixed exposure budget.
- **Depends on:** target failure taxonomy, data manifests, and `RQ-EVAL-001`.
- **Minimum experiment:** mixture ablation with fixed total examples/tokens/frames and optimizer updates; compare target-only, target plus general replay, and target plus the most mechanistically relevant auxiliary source.
- **Metrics:** target slice, general regressions, learning speed, gradient conflict diagnostic if available, and data/compute cost.
- **Artifacts:** source-level manifests, sampling traces, deduplication groups, exposure counts, configs, curves, and per-slice outputs.
- **Closure rule:** resolve for the tested budget when one mixture meets the target gain and regression constraints; do not generalize to untested scale.

### RQ-SAMPLER-001 - Minimum-cost Generator inference configuration

- **Dependency impact:** `decision`
- **State:** `blocked`
- **Decision:** choose denoising steps, guidance, seed budget, and parallelism before weight adaptation.
- **Known:** inference arguments and parallelism presets change latency, throughput, memory, and possibly output quality. [C3-FW-INFERENCE; C3-FW-ARGS; C3-INFERENCE-BENCHMARKS]
- **Unknown:** Pareto frontier for the target mode and hardware.
- **Depends on:** `RQ-GEN-001` and fixed evaluation inputs.
- **Minimum experiment:** factorial or successive-halving sweep over steps and guidance, followed by only the relevant parallelism presets; keep weights and evaluation set fixed.
- **Metrics:** target quality bundle, adherence, wall time, throughput, allocated/reserved/device memory, and failure rate.
- **Artifacts:** resolved arguments, topology, inputs/seeds, raw outputs, benchmark JSON, and Pareto selection rule.
- **Closure rule:** resolve when a non-dominated configuration is selected for an explicit latency or throughput objective. Sampling gains must remain labeled inference-only.

### RQ-REASONER-002 - Visual context and frame-sampling frontier

- **Dependency impact:** `decision`
- **State:** `blocked`
- **Decision:** choose image count, frame rate, resolution, and token budget for long visual reasoning.
- **Known:** longer or denser visual context increases memory and may include more task evidence, but redundant frames can consume tokens without improving decisions. NIM guidance places a practical vision-token recommendation on its deployment path. [C3-NIM-API]
- **Unknown:** failure and memory frontier for target event durations and occlusion patterns.
- **Depends on:** a working Reasoner backend and stratified video set.
- **Minimum experiment:** sweep event-centered frame sampling and resolution while fixing prompt and generation settings; include a condition that deliberately omits the causal transition.
- **Metrics:** target accuracy by event type, vision tokens, TTFT, total latency, peak memory, and truncation/failure rate.
- **Artifacts:** input manifests, timestamps, processor outputs, token counts, raw responses, and resource traces.
- **Closure rule:** resolve when a sampling policy satisfies target accuracy and runtime limits across declared duration slices.

## Traceability dependency impact

### RQ-SOURCE-001 - Training-throughput hardware count conflict

- **Dependency impact:** `traceability`
- **State:** `ready`
- **Decision:** whether an exact published training-throughput row can be reproduced or used for capacity planning.
- **Known:** the Cosmos 3 report body and the Table 8 caption differ in their Nano/Super GB200 counts: 1,024/2,048 versus 2,048/4,096. [C3-TR, pp.45-46]
- **Unknown:** authoritative hardware count for each measurement.
- **Minimum experiment:** seek an official erratum, revised report, or code/config artifact that binds the throughput row to topology.
- **Metrics:** immutable official source and internally consistent row.
- **Artifacts:** dated source snapshot and exact page/table mapping.
- **Closure rule:** resolve only with an official clarification; until then retain both values and do not choose one silently.

### RQ-SOURCE-002 - Nano HUE I2V value conflict

- **Dependency impact:** `traceability`
- **State:** `ready`
- **Decision:** exact value to cite in a benchmark reproduction target.
- **Known:** Table 14 reports 88.6 while adjacent prose reports 88.5. [C3-TR, p.59]
- **Unknown:** whether either number is rounded, stale, or erroneous.
- **Minimum experiment:** locate an official corrected table, evaluation artifact, or revision note.
- **Metrics:** source consistency.
- **Artifacts:** dated source and exact location.
- **Closure rule:** until clarified, cite both locations; resolve only through an official correction.

### RQ-SOURCE-003 - PAIBench-G pair-count discrepancy

- **Dependency impact:** `traceability`
- **State:** `ready`
- **Decision:** exact evaluation set cardinality for protocol replication.
- **Known:** the report states 1,044 pairs, while the six listed category counts sum to 1,033, leaving 11 pairs unexplained. The authors also report substituting Qwen2.5-VL-72B when the public protocol's Qwen3-VL-235B judge could not be reproduced. [C3-TR, p.57]
- **Unknown:** membership of the 11-pair difference and the canonical judge version/prompt.
- **Minimum experiment:** obtain the official manifest and evaluator package or an author clarification.
- **Metrics:** manifest cardinality, category sum, duplicate count, and judge identity.
- **Artifacts:** immutable manifest, hashes, prompt, judge revision, and scoring code.
- **Closure rule:** resolve only when cardinality and evaluator are reproducible; otherwise label any rerun as a modified protocol.

### RQ-SOURCE-004 - Dynamic leaderboard comparability

- **Dependency impact:** `traceability`
- **State:** `ready`
- **Decision:** whether current RoboArena or MolmoSpaces ranks can be compared with report-era ranks.
- **Known:** leaderboard position is time-dependent and may change with models, votes, filters, or protocols. Reported ranks are valid only for their snapshot dates. [C3-TR, pp.67-70]
- **Unknown:** current protocol compatibility and current rank.
- **Minimum experiment:** capture a dated leaderboard snapshot plus protocol/model version changes.
- **Metrics:** unchanged task protocol and comparable sample/vote definition.
- **Artifacts:** dated snapshot, protocol revision, model identity, and comparison notes.
- **Closure rule:** compare ranks only within a compatible dated protocol; otherwise report separate snapshots.

## Registry maintenance notes

When an item changes state:

1. preserve its stable ID;
2. attach the closure artifact and date;
3. update the canonical topic page if the result establishes reusable knowledge;
4. update [Reproduction](reproduction.md) if an execution surface changes state;
5. update [Optimization playbook](optimization-playbook.md) only if the decision rule changes;
6. replace the open experiment with the result and remaining narrower question; do not erase negative outcomes;
7. add new official or local artifact records to [`sources.yaml`](sources.yaml).

The `blocked` label preserves the exact missing dependency instead of replacing it with a convenient assumption. If a minimum experiment reveals multiple independent uncertainties, new stable IDs and a parent relation keep the evidence graph interpretable. AIBuildAI decides how that information affects its workflow.

## Sources

Source records are resolved through [`sources.yaml`](sources.yaml): `C3-TR`, `C3-HF`, `C3-BUILD`, `C3-REASONER-COOKBOOK`, `C3-NIM-API`, `C3-FW-FAQ`, `C3-FW-INFERENCE`, `C3-FW-ARGS`, `C3-FW-ACTION`, `C3-FW-POLICY-DROID-DOC`, `C3-POLICY-DROID-HF`, `C3-INFERENCE-BENCHMARKS`, `LOCAL-REPRO-20260809`, and `LOCAL-ENV-20260809`.
