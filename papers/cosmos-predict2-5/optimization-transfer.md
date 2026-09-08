---
id: world-model-kb.papers.cosmos-predict2-5.optimization-transfer
title: Cosmos-Predict2.5 Transferable Optimization Knowledge
kind: reference
status: maintained
last_updated: 2026-09-08
owners:
  - AIBuildAI world-model group
---

# Cosmos-Predict2.5 Transferable Optimization Knowledge

## Retrieval metadata

**Relevant queries:** transfer Predict2.5 mechanism, optimize video world model, improve temporal consistency, action conditioning, specialist merging, reward post-training, video distillation, multiview adaptation, or synthetic robot data.

**Knowledge provided:** source-grounded optimization patterns and hypotheses with target behavior, attachment point, data/objective change, expected evidence, compute and regression risks, minimum controlled experiment, and falsification criteria.

**Related pages:** [`paper.md`](paper.md) owns source evidence; [`codebase.md`](codebase.md) owns implementation surfaces; [evaluation methodology](../../foundations/data-and-evaluation/evaluation-methodology.md) owns controlled comparison; [Few-Step and One-Step Video Distillation](../../components/fast-video-inference/few-step-distillation.md) owns the broader method lineage, cost semantics, and failure taxonomy; [Cosmos3-Nano optimization](../../models/cosmos3-nano/optimization-playbook.md) owns target-model experiment design rather than inheriting these proposals automatically.

## 1. Transfer discipline

The interventions below are reusable knowledge patterns, not universal prescriptions. Each must be re-instantiated against a target model's representation, data, objective, and interface. Predict2.5 is a latent video DiT with clean-prefix flow training; architectural similarity by name does not establish weight, module, or optimizer compatibility with Cosmos3-Nano or another world model.

Evidence labels used locally are descriptive rather than a ranking system:

- **Source-supported mechanism:** directly reported or ablated by Predict2.5.
- **Transfer hypothesis:** a target-model intervention inferred from the source mechanism.
- **Invalid transfer condition:** a mismatch that breaks the causal analogy.

No pattern here selects an Agent, repository, experiment priority, schedule, permission, or workflow action.

## 2. Intervention matrix

| ID | Source-supported mechanism | Target behavior | Likely attachment | Strongest source evidence |
|---|---|---|---|---|
| `CP25-XFER-01` | targeted high-noise tail sampling | abrupt temporal transitions and poor recovery from weak context | noise/time sampler | reported qualitative reduction; no numeric ablation |
| `CP25-XFER-02` | zero/one/two clean-prefix curriculum | unified unconditional and conditional generation | condition mask and task sampler | final `0.5/0.25/0.25` mixture |
| `CP25-XFER-03` | staged filter, caption, dedup, and domain sharding | data quality and controllable mixture construction | data curation and loader | 6B candidates to 200M retained clips |
| `CP25-XFER-04` | independent specialist SFT plus merge | specialization without catastrophic cross-domain loss | checkpoint deltas and merge layer | domain human votes; model soup selected |
| `CP25-XFER-05` | reward optimization plus diffusion-data regularization | alignment/quality without reward hacking | diffusion trajectory objective | reward and human preference increase |
| `CP25-XFER-06` | multilevel Reason1 features projected to cross-attention | local/global prompt grounding | text encoder feature extraction and projection | final system only; no isolated encoder ablation |
| `CP25-XFER-07` | action embedding added to time and AdaLN modulation | action-sensitive future observation | global denoiser modulation | direct Bridge injection ablation |
| `CP25-XFER-08` | view-axis reuse plus camera embeddings/raymaps | synchronized multiview prediction | tokenizer sequence layout, RoPE, camera projection | Sampson improvement with rotation regression |
| `CP25-XFER-09` | few-step teacher distillation | lower sampling latency | student objective and solver | four-step aggregate quality near teacher |
| `CP25-XFER-10` | video augmentation with preserved or recovered actions | broaden policy-training visual coverage | generator plus label-transfer/IDM pipeline | related downstream studies; action correctness remains a gate |

## 3. `CP25-XFER-01`: high-noise tail coverage

**Source mechanism.** Predict2.5 reserves 5% of training draws for the highest 2% of its noise distribution after observing abrupt transitions under the shifted logit-normal schedule. The report states improvement but does not publish an isolated value. [P25-TR, pp.10-11]

**Transfer hypothesis.** If a target video flow model fails when condition evidence is weak or early samples are highly corrupted, modest tail oversampling can improve global temporal reconstruction and reduce discontinuities without increasing model capacity.

**Attachment and controls.** Change only the time/noise sampler. Hold data, latent codec, conditional-frame mixture, optimizer, update count, effective examples, resolution, batch, guidance, and inference solver fixed. Log the actual empirical time histogram after distributed sampling.

**Expected evidence.** Lower transition-discontinuity and horizon-conditioned state/identity errors, stable or improved perceptual quality, and no collapse in sample diversity. Inspect object permanence and camera cuts separately from generic motion.

**Compute and risks.** Training cost is nearly unchanged, but high-noise emphasis can reduce fine-detail learning or change loss scale. The intervention interacts strongly with resolution shift and conditional-prefix count.

**Minimum test.** Short matched continuation SFT runs at three tail masses, including zero and 5%, with at least three seeds or independent data orders. Falsify if gains disappear after equalizing loss/time weighting, if only an evaluator proxy improves, or if high-frequency detail and conditional adherence regress beyond uncertainty.

## 4. `CP25-XFER-02`: conditional-prefix curriculum

**Source mechanism.** One model trains across text-only, image-prefix, and video-prefix queries by replacing clean leading latents and sampling their count. The final mixture assigns half of examples to zero clean frames and a quarter each to one and two. [P25-TR, pp.9-11]

**Transfer hypothesis.** Shared parameters can transfer scene and dynamics knowledge across conditioning modes when the input/target mask is explicit and each mode receives sufficient gradient mass. Varying prefix length may improve robustness to partial observations.

**Attachment and controls.** Modify task probabilities and clean-prefix lengths, not the model architecture. Normalize comparison by target tokens or total compute because a longer clean prefix removes loss-bearing positions. Verify latent versus pixel frame counts and exclude clean positions from loss identically.

**Expected evidence.** A Pareto improvement or smaller regression frontier across T2W, I2W, short-prefix continuation, and longer-prefix continuation. Measure conditional identity preservation and generated-horizon quality separately.

**Risks and falsification.** Text-only quality may fall if conditional tasks dominate; conditional branches may exploit copied frames without learning continuation. Falsify shared-training benefit when matched single-mode specialists outperform the joint model at equal total tokens and a merge or adapter recovers all transfer more cheaply.

## 5. `CP25-XFER-03`: curated, queryable data mixtures

**Source mechanism.** Predict2.5 applies staged technical/semantic filters, three caption lengths, semantic deduplication, 26 content types, and domain-specific shards. The report calls final retention about 4%; its rounded `>6B` candidate and `~200M` retained counts imply at most 3.33%, so the exact denominator is unresolved. [P25-TR, pp.4-8]

**Transfer hypothesis.** For a fixed update budget, explicit event/domain/quality strata can allocate gradient mass toward rare Physical AI transitions more effectively than undifferentiated video scale. Multiple caption granularities may align coarse scene identity with fine action/state descriptions.

**Attachment and controls.** Instrument dataset units and filter decisions; bind clip/trajectory/scene identities; preserve a replayable transform manifest. Compare raw-scale, technical-only, semantic-filtered, and deduplicated mixtures at equal decoded frames and optimizer updates. Keep model and objective fixed.

**Expected evidence.** Better rare-event, contact, object-permanence, and instruction-following slices without leakage or diversity collapse. Report retention by source, domain, motion, duration, and text density, not one global retention rate.

**Risks and falsification.** Aesthetic/VLM filters can erase unusual but valid dynamics, bias environments, or create reward-model leakage. Falsify the proposed benefit when quality gains vanish on source-disjoint tests, when rare-event recall falls, or when an equal-compute random sample performs equivalently.

## 6. `CP25-XFER-04`: specialist deltas and merging

**Source mechanism.** Five independent SFT models improve their target-domain pairwise preference. The paper sweeps model soup, TIES, DARE-Linear, and DARE-TIES, selects model soup, and observes a negative DARE-Linear interaction. [P25-TR, pp.11-13, Figures 3-4]

**Transfer hypothesis.** When domain objectives interfere, independently learned parameter deltas can preserve specialist improvements and be recombined more controllably than one opaque mixed-data run.

**Attachment and controls.** Begin all specialists from one exact checkpoint. Record data tokens, trainable parameters, optimizer, and per-domain deltas. Reserve a selection set disjoint from final validation. Compare joint mixture, specialist-only, simple average, weighted soup, and at least one conflict-aware merge at equal aggregate SFT compute.

**Expected evidence.** A merged checkpoint closes most specialist gains while keeping a predeclared general and safety regression matrix within uncertainty. Report every candidate or preregister the selection rule to avoid best-of-many inflation.

**Risks and falsification.** Merge coefficients can overfit a small hand-picked set; neuron permutation and optimizer-induced geometry can make averaging invalid; common failures may reinforce. Falsify merge advantage if joint training dominates under equal compute, if validation gains disappear on a locked test, or if one specialist's improvement always requires unacceptable regression elsewhere.

## 7. `CP25-XFER-05`: reward optimization anchored to data

**Source mechanism.** VideoAlign evaluates text, motion, and visual quality; group-normalized diffusion-trajectory updates increase reward and human preference. Diffusion loss on fine-tuning data regularizes the policy to reduce reward hacking. [P25-TR, pp.13-14; P25-VIDEOALIGN; P25-DDRL]

**Transfer hypothesis.** Preference optimization can target failures underrepresented by likelihood training, while a data-distribution anchor limits overspecialization to reward-model artifacts.

**Attachment and controls.** Fix the starting checkpoint, prompt/data distribution, rollout count, sampler steps, reward revision, optimizer, and total generated samples. Sweep reward weights and data-loss coefficient. Maintain holdout evaluators that were not used for training.

**Expected evidence.** Training reward, independent human preference, and external physical/conditional metrics improve together; diversity, rare-event coverage, and base likelihood remain acceptable.

**Compute and risks.** This is expensive because each update needs multiple decoded video rollouts and reward inference. Multi-dimensional rewards can still share blind spots; group normalization can be unstable on homogeneous prompts; a strong anchor can nullify learning.

**Minimum test and falsification.** Compare reward-only, data-loss-only, combined, and unchanged checkpoints on a locked prompt set. Falsify if only the training reward improves, if human gains vanish with blinded random ordering, or if diversity/physics/action sensitivity regresses beyond the predeclared boundary.

## 8. `CP25-XFER-06`: multilevel language features

**Source mechanism.** Predict2.5 concatenates multiple Reason1 block activations and projects them to 1,024 dimensions for cross-attention. The paper has no matched single-layer or T5 ablation. [P25-TR, pp.9-10]

**Transfer hypothesis.** Intermediate and late language/VLM features may jointly preserve local object/action tokens and global scene semantics, helping a video generator ground complex prompts.

**Attachment and controls.** Treat encoder revision, chosen blocks, normalization, projection width, token length, and encoder freezing as independent variables. Match parameter count with a learned projection baseline and cache embeddings to separate feature quality from compute.

**Expected evidence.** Better compositional and action/state prompt adherence, especially for prompts requiring both fine entities and global temporal relations, without lowering visual quality.

**Invalid transfer condition.** A target already jointly trains text and video towers or uses native cross-modal attention may not benefit from fixed concatenated features. Falsify if a last-layer baseline matches performance at equal projection capacity or if gains arise only from a different encoder checkpoint.

## 9. `CP25-XFER-07`: action modulation through denoising state

**Source mechanism.** A chunk-level action MLP is added to time and AdaLN modulation. On the fixed Bridge setup, this beats cross-attention and channel concatenation on the reported video metrics. [P25-TR, pp.33-35, Table 20; P25-CODE-PAPER]

**Transfer hypothesis.** When one action chunk globally governs a short prediction horizon, modulating every block through denoising-state conditioning can expose the control signal more uniformly than a separate attention memory.

**Attachment and controls.** Define physical action units, frame, rate, chunk horizon, padding, gripper semantics, and normalization before comparing interfaces. Match added parameters and training compute across time/AdaLN, cross-attention, token, and channel variants. Include a shuffled-action and zero-action probe.

**Expected evidence.** Improved held-out rollout metrics plus increased sensitivity to feasible counterfactual action changes, lower replayed state/contact error, and no degradation under identical-action repeatability.

**Risks and falsification.** Flattening a chunk loses within-chunk temporal structure; global modulation may underperform for long or variable action sequences; observational correlations can hide action neglect. Falsify if shuffled actions leave outputs unchanged, if video metrics improve without environment transition accuracy, or if a temporally structured action-token interface wins at matched capacity.

## 10. `CP25-XFER-08`: repurposed sequence axes for multiview generation

**Source mechanism.** Predict2.5 concatenates views along the latent temporal dimension, adds per-view embeddings, constructs RoPE per view, and optionally adds projected Plucker raymaps. Multiview improves Sampson consistency but slightly worsens rotation error in the reported robot comparison. [P25-TR, pp.24-31, Table 17]

**Transfer hypothesis.** A pretrained spatiotemporal attention stack can cheaply acquire cross-view correspondence when view identity and camera geometry disambiguate the reused axis.

**Attachment and controls.** Compare temporal-axis reuse with explicit view-axis or factorized attention under equal tokens and parameters. Preserve calibration, temporal alignment, camera sampling at codec stride, source/target distinction, and caption-per-view behavior.

**Expected evidence.** Lower cross-view feature/reprojection inconsistency without degrading per-view temporal coherence or pose accuracy. Evaluate occlusion and disocclusion separately.

**Risks and falsification.** View/time aliasing can damage temporal generalization; a shared latent may hallucinate mutually consistent but wrong geometry. Falsify if independent geometric reconstruction disagrees, if pose error grows materially, or if the gain disappears when view count changes.

## 11. `CP25-XFER-09`: few-step distillation

**Source mechanism.** The paper's rCM student uses four steps with near-teacher PAI-Bench overall scores. The public repo instead exposes DMD2/TrigFlow. [P25-TR, pp.14-15, Tables 7-8; P25-RCM; P25-DMD2]

**Transfer hypothesis.** Combining a trajectory-consistency signal with distribution/score regularization can reduce solver steps while retaining broad video quality better than naive step truncation.

**Attachment and controls.** Choose one method identity; bind teacher, student initialization, solver, step budget, guidance, data, critic/adversarial terms, and training samples. Compare teacher at its native steps, teacher truncated to four, distilled student at four, and student at multiple steps.

**Expected evidence.** Lower end-to-end latency and peak resource use at matched or bounded loss in quality, temporal consistency, condition adherence, diversity, and action sensitivity.

**Risks and falsification.** Aggregate quality can hide mode loss and long-horizon drift; decoder and guardrail time can dominate denoising savings. Falsify if wall-clock gain is small, if best-of-N is needed to recover quality, or if rare/physical events regress despite a stable composite score.

## 12. `CP25-XFER-10`: synthetic video for robot learning

**Source mechanism.** The report describes two label pathways: preserve actions while visually translating a demonstration, or generate a task video and recover pseudo-actions with an inverse/latent-action model. Related Transfer2.5 augmentation improves a small real-robot study, while Predict2.5 DreamGen results evaluate instruction-following video rather than policy success. [P25-TR, pp.20-24, 31-34]

**Transfer hypothesis.** A controllable video model can expand appearance, object, and environment coverage while retaining or reconstructing task-relevant trajectories, improving a downstream policy when real demonstrations are scarce.

**Attachment and controls.** Separate visual augmentation from action relabeling. Validate preserved actions through replay feasibility; validate recovered actions through inverse-dynamics error, IK/constraint checks, and resulting transitions. Compare real-only, standard augmentation, synthetic-video with preserved labels, synthetic-video with recovered labels, and matched additional real data.

**Expected evidence.** Closed-loop success on held-out objects/environments with no increase in safety violations, interventions, or latency. Report stage progress and failure categories, not only aggregate success.

**Risks and falsification.** Video and recovered action can be jointly plausible but mutually wrong; synthetic diversity may be cosmetic; policy may exploit generator artifacts. Falsify if gains disappear under real held-out scenes, if replayed action/state consistency is poor, or if equivalent image augmentation matches the result.

## 13. Interaction map

| Interaction | Why it matters | Required discriminator |
|---|---|---|
| Noise-tail sampling x resolution shift | both change effective signal-to-noise difficulty | factorial sampler/resolution ablation |
| Prefix mixture x loss-token count | longer prefixes reduce supervised target positions | normalize by generated target tokens and compute |
| Data filters x reward model | both may prefer the same aesthetics and hide coverage loss | source-disjoint human/physics evaluator |
| Specialist SFT x merge selection | merge success depends on delta geometry and candidate selection | locked final test and complete candidate ledger |
| Reward RL x distillation | student may erase or amplify reward-induced biases | evaluate reward, diversity, and external metrics before/after distillation |
| Action injection x chunk length | flattened global action loses more temporal structure at long horizon | length sweep and per-step counterfactuals |
| View-axis reuse x temporal context | one token budget is shared across views and time | fixed-token view/time factorial comparison |
| Codec x action/object metrics | compression may remove small control-relevant evidence | decoded and latent/state/contact probes |

## 14. Invalid generalizations

- Predict2.5's PAI-Bench gain does not imply better robot control, action causality, or safety.
- The Bridge time-embedding ablation does not establish an optimal interface for native action-token models such as Cosmos3-Nano.
- The success of model soup under one set of specialists does not establish that averaging any post-trained checkpoints is safe.
- Reward improvement on VideoAlign does not establish physics improvement because the reward dimensions are text, motion, and visual quality.
- Four-step composite-score parity does not establish equal diversity, latency, memory, or long-horizon behavior.
- Synchronized rendered views do not establish an explicit or metrically correct 3D world state.
- A generated robot demonstration does not carry valid actions unless label preservation or independent action recovery is verified.
- Public code for a related mechanism does not establish reproduction of an unreleased paper stage.

## 15. Transfer record template

```text
Transfer ID and target model revision:
Source-supported mechanism and locator:
Target failure and observable:
Target attachment point:
Representation/interface compatibility:
Data and objective change:
Baseline and controlled variables:
Expected metric direction:
Compute and memory estimate:
Regression matrix:
Minimum discriminating experiment:
Falsification result:
Remaining confounders:
```

Use this schema to turn a pattern into a target-specific experimental proposal. Until instantiated and tested, the records remain hypotheses rather than model facts.

## Sources

Paper and implementation identities resolve through [`sources.yaml`](sources.yaml); model-independent mechanisms and evaluation principles remain canonical in Foundations.
