---
id: world-model-kb.papers.x-wam.optimization-transfer
title: X-WAM Mechanism Transfer and Falsification
kind: paper
status: maintained
last_updated: 2026-08-24
owners:
  - AIBuildAI world-model group
---

# X-WAM Mechanism Transfer and Falsification

## Retrieval metadata

**Relevant queries:** transfer X-WAM depth branch, transfer ANS, optimize another WAM, multi-view geometry supervision, early action decoding, asynchronous sampler, action-video loss, history conditioning, experiment design, or falsification.

**Knowledge provided:** target-independent mechanism hypotheses with attachment points, required data, expected signals, regression risks, controlled tests, and rejection conditions.

**Related pages:** [Paper](paper.md) owns source evidence; [X-WAM optimization playbook](../../models/x-wam/optimization-playbook.md) owns changes to the released model; [RoboCasa optimization reference](../../benchmarks/robocasa/optimization-reference.md) owns benchmark diagnostic slices.

## Transfer boundary

X-WAM provides two primary mechanisms: a late unilateral auxiliary depth branch and a coupled noise distribution aligned with early action decoding. Their paper evidence comes from a Wan2.2-based unified video/state/action flow model. Transfer to an autoregressive policy, latent-state model, or WAM with separate modality towers is an analogy until the target's information flow and inference trajectory are mapped explicitly.

## Hypothesis 1: late unilateral geometry branch

**Mechanism.** Duplicate the final blocks of a pretrained visual backbone. Let the geometry branch read main-branch features while preventing geometry tokens from perturbing the main branch's late computation. Supervise inverse depth or another geometric target; disable the branch when low-latency policy output is sufficient.

**Applicable target.** A visual generative WAM with a shared pretrained backbone, accessible late blocks, aligned RGB/geometry supervision, and a policy path that can benefit from shared early representations.

**Attachment.** Copy the last `M` blocks and prediction head; use main-branch keys/values as unilateral cross-attention context. Initialize copies from the corresponding main blocks. The target must define whether gradients from depth loss update shared blocks, copied blocks, or both.

**Required data.** Camera-calibrated depth or pseudo-depth aligned with training RGB; multi-view data if 3D consistency is evaluated. Pseudo-label source and uncertainty must be retained.

**Expected evidence.** Better depth and fused-geometry metrics; improved precision-heavy policy slices such as insertion and buttons; policy-only latency close to no-depth when the branch is disabled.

**Risks.** Pseudo-depth bias, branch capacity increasing memory, main shared gradients harming RGB/action, improvement caused by extra parameters rather than geometry, or no policy benefit because action-only inference never consumes branch output.

**Minimum controlled test.** Compare no depth, late branch, parameter-matched non-geometric auxiliary branch, and depth with frozen shared blocks. Hold data volume, backbone, optimizer, steps, sampler, and policy protocol fixed. Measure RGB, depth, point cloud, per-task policy success, latency, memory, and calibration slices.

**Falsification.** Reject the policy-benefit hypothesis if geometry metrics improve but paired precision-task success and action error do not, or if a parameter-matched non-geometric branch gives the same gain.

## Hypothesis 2: inference-support-matched timestep sampling

**Mechanism.** When one modality is decoded earlier than another, train only or preferentially on joint noise states that the inference process visits. X-WAM enforces `t_video >= t_action` and includes clean-action/video-noisy samples.

**Applicable target.** A multi-output diffusion or flow model with distinct inference schedules and a later phase where generated clean actions condition continuing world prediction.

**Attachment.** Replace independent timestep sampling with a joint distribution derived from the actual scheduler trajectories. Preserve a configurable clean-fast-modality mixture. If modalities use different timestep parameterizations, map them to comparable signal-to-noise or log-SNR coordinates before imposing order.

**Expected evidence.** At fixed action latency, better video/depth continuation after actions become clean; at fixed generation quality, fewer action model calls; possibly better policy success from reduced train/inference mismatch.

**Risks.** Reduced coverage of useful joint-noise states, dependence on one sampler, shifted loss balance, or improvements caused by a changed marginal timestep distribution rather than coupling.

**Minimum controlled test.** Cross independent versus coupled training with synchronous versus asynchronous inference in a 2×2 design. Match the marginal video and action timestep histograms where possible. Measure action error/success, visual and geometry metrics, and model-call latency.

**Falsification.** Reject the coupling explanation if a marginal-matched independent sampler performs identically across asynchronous evaluation or if benefits vanish under another scheduler while claimed as scheduler-independent.

## Hypothesis 3: geometry-aware state/camera consistency

X-WAM's fused point cloud depends on predicted end-effector pose for wrist-camera extrinsics. A transferable objective can enforce consistency among state prediction, wrist-camera pose, depth, and multi-view point clouds. Attachment points include a pose loss, reprojection loss, cross-view point-cloud loss, or calibrated wrist transform head.

The controlled test separates static-view depth quality from wrist-view fusion. Ground-truth pose at evaluation is an oracle counterfactual: if it repairs Chamfer Distance, pose/state prediction is the bottleneck; if not, depth or calibration dominates. Falsify a state-loss intervention if it lowers state error without improving wrist fusion or policy precision.

## Hypothesis 4: preserve longer temporal context

X-WAM conditions on a fixed observation window and predicts one finite chunk; its paper identifies missing history as a long-horizon limit. Candidate transfers include history tokens, KV-cached causal context, recurrent state summaries, or explicit task-progress targets. The target behavior is composite-task stage disambiguation, not merely higher training likelihood.

A minimum experiment holds action horizon and compute approximately fixed, compares no history with multiple context lengths, and reports atomic versus composite tasks, stage-transition success, latency, memory, and error accumulation. Oracle stage labels test whether context ambiguity causes the failure. If oracle progress does not help, history expansion is unlikely to address the bottleneck.

## Hypothesis 5: data-mixture and geometry-label interactions

The paper's final 79.2% combines depth/ANS with 5,873.9 hours of pretraining, while ablations omit that pretraining. Depth gains may depend on pseudo-depth quality and dataset mixture; ANS gains may depend on action frequency and embodiment distribution. A factorial study should vary data mixture, depth supervision, and ANS rather than importing Table 4 effect sizes into the pretrained regime.

Required measures include per-dataset validation losses, pseudo-depth uncertainty, single/dual-arm and real/sim slices, RoboCasa skill slices, action latency, and RGB/depth regression. The hypothesis that a mechanism is robust to pretraining scale is rejected when its gain changes sign or disappears after equal-compute large-scale pretraining.

## Transfer to Cosmos3-Nano

Cosmos3-Nano's Generator/action surfaces differ from X-WAM's Wan DiT: Nano uses its own multimodal architecture and action adapters. Directly copying X-WAM blocks is not justified. The transferable questions are narrower:

- can an auxiliary geometry branch read generator features without perturbing the principal generation/action path;
- does Nano use different action and visual denoising schedules, and if so, does its training noise distribution match inference support;
- can action output become available earlier without invalidating later video generation;
- do depth/geometry targets improve RoboCasa precision slices after controller/interface alignment?

Each requires source-level attachment mapping and a target-specific baseline. Similar “world action model” naming is not evidence of architectural compatibility.

## Evidence standard

A transfer becomes reusable knowledge only after the target mechanism, data, compute, protocol, regression metrics, and rejection result are recorded. Until then it is an optimization hypothesis. This page informs design judgment but does not schedule experiments or select repositories.

## Sources

Mechanisms and source evidence use `XWAM-PAPER-V2` and `XWAM-CODE-72CF`. Target benchmark constraints use `RC24-PAPER-V1` and `RC24-CODE-V02` through the [RoboCasa registry](../../benchmarks/robocasa/sources.yaml).
