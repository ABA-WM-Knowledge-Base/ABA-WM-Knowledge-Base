---
id: world-model-kb.models.xiaomi-robotics-1.optimization-playbook
title: Xiaomi-Robotics-1 Optimization Design Reference for VLABench
kind: guide
status: maintained
last_updated: 2026-08-21
owners:
  - AIBuildAI world-model group
---

# Xiaomi-Robotics-1 Optimization Design Reference for VLABench

## Retrieval metadata

**Relevant queries:** optimization hypothesis, failure diagnosis, which track, generalization intervention, CoT, data augmentation, inference-time lever, controlled comparison, paired episodes, experiment artifact, what to try first.

**Knowledge provided:** optional experiment-design patterns connecting VLABench failure signatures to mechanisms, controllable variables on this model, measurements, confounders, and evidence quality. This page does not prescribe AIBuildAI task planning or execution.

**Related pages:** [Reproduction](reproduction.md) contains execution state; [Evaluation](evaluation.md) contains protocol and numbers; [Limitations](limitations.md) contains guardrails; [ERVLA transfer](../../papers/ervla/optimization-transfer.md), [VLABench transfer](../../papers/vlabench/optimization-transfer.md), and [Xiaomi-Robotics-1 transfer](../../papers/xiaomi-robotics-1/optimization-transfer.md) hold the paper-derived interventions; [evaluation methodology](../../foundations/data-and-evaluation/evaluation-methodology.md) owns comparison validity.

## Experiment description model

```text
target track(s) -> observed failure signature (from per-episode records)
  -> candidate mechanism -> controllable surface on XR-1
  -> minimum discriminating intervention -> paired-episode metric and regressions
  -> artifact bundle -> interpretation against the noise band
```

The anchor is the released checkpoint's own L2 on the same configs; every node is a paired comparison against it, not against the paper's 59.1.

## Evidence prerequisites

Checkpoint provenance (import/export records), data-path conventions asserted equal to the client, VLABench commit, client args, `train/token` versus declared batch, s/step, the per-track profile of the anchor.

## Surface selection

| Observed failure (per-episode records) | Diagnose first | Preferred first intervention | Avoid as first response |
|---|---|---|---|
| Track 3/4 low SR, IS low (wrong object approached) | instruction grounding; compare IS across paraphrases | CoT with grounded content (`cot_prob` > 0), instruction paraphrase augmentation | DiT-only fine-tune; more steps on Track-1 data |
| Track 2 low SR, IS high, PS mid (right object, failed grasp on unseen instance) | grasp geometry vs instance shape | visual augmentation, longer training on grasp-heavy tasks, wrist-view emphasis | CoT |
| Track 6 low SR (texture) | texture sensitivity; check train/eval resolution asymmetry | colour/texture augmentation, resolution matching | language-side changes |
| Track 1 regresses while others rise | over-regularization or catastrophic drift from the warm start | lower lr, fewer steps, midpoint checkpoint | more augmentation |
| All tracks drop sharply after fine-tune | convention mismatch (deltas, gripper, state) or stats mismatch | export-and-score an untrained warm start | hyperparameter search |
| Episodes end at step cap with near-zero motion | degenerate chunk scale; stats or mask wrong | inspect decoded chunks against dataset deltas | retraining |
| Majority errors / step 0 | serving chain | fix environment | anything model-side |

## Diagnosis protocol

1. **Localize** each failed episode with one primary label: `grounding` (wrong target, IS 0 with motion), `grasp` (approached, not lifted: PS < 0.5 with IS 1), `placement` (grasped, not placed), `timeout` (slow but on-path), `interface` (error, step 0, drift). Use `detail_info.json` + videos.
2. **Separate interface from capability**: an interface label in > 10 % of episodes invalidates the run for model comparisons.
3. **Stratified baseline**: the anchor's per-(track, task) SR table; compare cells, not only the average.
4. **Rank mechanisms** by the tracks they can move and by cost: inference-time levers (steps, seed ensembling, replan horizon) cost one eval each; data-path levers cost one training; architecture/freezing levers cost a training plus risk to the warm start.
5. **Measured decomposition of the anchor (run `xr1-l2-released-lambda-20260821-01`, 250 episodes).** Per-task SR ranges 0.28 (`add_condiment`) to 0.80 (`select_poker`); no task is systematically zero; weighting task names equally, the three weakest carry 39 % of the shortfall and the other nine carry 61 % - the failure mass is SPREAD, so per-task specialization has no concentrated target to attack. PS exceeds SR on every task and 34 % of episodes engaged the right target and still failed: the dominant signature is failing to complete a correctly-started manipulation, i.e. shared execution competence. Per-cell figures are 5 episodes (sd ~0.22 at p 0.5), so the 0.0-vs-1.0 swings of `select_fruit` and `select_chemistry_tube` across tracks are noise, not track-specific defects. Per-task IS is unusable (`select_chemistry_tube` IS 0.00 at SR 0.72 - VLABench issue 82), so diagnose with SR and PS and treat IS as corroboration.

## Lever hierarchy (cheapest first)

1. Inference-time: `num_steps`, seed ensembling, `replan_steps` (1..10), image crop — no training. Protocol note: any of these changes the comparability with the released numbers; report as a separate protocol.
2. Data-path: CoT mixing and content, paraphrases, visual augmentation, per-task weighting, wrapped-Euler stats.
3. Optimization (continued-post-training regime, see the survey section below): schedule without re-warm, split backbone/head lr, EMA, L2-SP toward the warm start, short step budgets with intermediate checkpoints selected on a non-test signal, post-hoc weight interpolation toward the warm start.
4. Parameter scope: DiT-only, LoRA on the backbone, VLM-frozen (vision-frozen-only is the scope the literature warns against). PREFERRED FIRST TRAINING INTERVENTION: a low-LR LoRA continuation (backbone adapters, full action head) under the level-3 optimization regime, because it bounds backbone drift, matches full fine-tuning on published VLA fine-tunes, and merges back into the released tensor names so the export and serving path are unchanged. Specialize-then-MERGE (per-cluster adapters combined by task arithmetic) before considering specialize-then-ROUTE (mixture of experts by upcycling a component); the latter also forfeits the byte-identical official evaluator.
5. Objective: `freq_coefficient`, choice-loss weights, `cot_coefficient`.

## Metric bundles

Primary: 5-track SR macro average on paired episodes. Always retained: per-track SR/PS/IS, per-task SR, error count, mean `consumed_step` on successes (speed), wall clock, `train/loss_mse`, `train/loss_cot`. Regression guard: Track 1 SR must not drop beyond the noise band.

## Comparison design

- Same 250 configs for every candidate; report the paired difference and the count of episodes that flipped each way.
- Two-candidate decisions inside ~6 pp of average SR are not decisions; extend episodes (the next 5 configs per task) before eliminating.
- Never mix an SR number with a PS leaderboard number.

## Result interpretation patterns

- A gain concentrated in one task of one track is a task fix, not a generalization gain; check whether that task's PS moved.
- Lower IS with higher SR indicates the evaluator's IS defect, not worse grounding.
- A higher Track-1 SR with lower Track-2/6 SR is memorization of the 500-episode set.

## Continued post-training from a converged checkpoint (survey, 2026-08-21)

The campaign warm-starts from a checkpoint already fine-tuned on the same 5,000 episodes it will train on. What the literature measures about that situation (external sources; "measured" = a reported number, "practice" = a default without an ablation):

- Re-warming the learning rate back to the original peak is the most damaging default: with zero distribution shift, every model that re-increased its LR from the decayed minimum saw a loss increase, and forgetting scaled with the peak (measured; Ibrahim et al. 2024, https://arxiv.org/abs/2403.08763). Xiaomi's default (2e-5 peak, 500 warmup, cosine) is exactly a re-warm.
- The LR on the VLM backbone is the dominant forgetting knob: full fine-tuning at 1e-5 cost 17-34 pp out-of-distribution, 1e-6 cost ~0 (measured; https://arxiv.org/abs/2603.14493). The language-heavy tracks (3, 4) live in the backbone.
- Freezing the vision encoder outright hurts (measured; OpenVLA 47.0 vs 69.7, https://arxiv.org/abs/2406.09246; Octo full > partial, https://arxiv.org/abs/2405.12213), but GR00T N1.5 freezes the whole VLM by design (practice). Per-module LR (VLM ~1e-6, action head ~1e-5 to 2e-5) is the middle path.
- Warm-starting from a fitted network on the SAME data loses plasticity and ~3-4 pp of generalization that LR/batch/L2 sweeps do not recover; shrink-perturb (lambda 0.6, sigma 0.01) did, on small CNNs only (measured at small scale; Ash & Adams 2020, https://arxiv.org/abs/1910.08475; DASH, NeurIPS 2024).
- Longer is not monotonically better on scripted simulation data: OpenVLA-OFT's LIBERO-Goal peaked at 50k of 150k steps (measured; https://github.com/moojink/openvla-oft/blob/main/LIBERO.md). Score every 1-2k steps and keep the best checkpoint, not the last.
- Replay of 1-5 % of the original mixture "significantly reduces forgetting" (measured; Ibrahim); Xiaomi's own post-training mixes VL data (practice). Only applicable if a VL or robot mixture is staged.
- EMA of weights is on by default in openpi (0.999) and Cosmos post-training (practice, not ablated).
- Interpolating the fine-tuned weights back toward the starting checkpoint (WiSE-FT, https://arxiv.org/abs/2109.01903; RETAIN for VLAs, alpha in {0.25, 0.5, 0.75}, language-model-only merge often suffices, https://arxiv.org/abs/2512.08333) gained 4-6 pp OOD at no ID cost - a free post-hoc sweep per trained node.
- Supervised continuation on demonstrations saturates (RL4VLA: SFT flat beyond 16k demos, https://rlvla.github.io/); the large measured gains from an SFT checkpoint come from on-policy methods in the simulator: piRL (flow-matching policies, LIBERO 77 -> 98, https://arxiv.org/abs/2510.25889), SimpleVLA-RL (GRPO, https://github.com/PRIME-RL/SimpleVLA-RL), RL4VLA (PPO), PLD (residual-RL failure probing + distillation, https://arxiv.org/abs/2511.00091). VLABench is a MuJoCo simulator, so these are available here.
- Xiaomi's VLABench fine-tune recipe (LR, steps, frozen modules) is not stated anywhere; 2e-5 / 500 warmup / cosine are generic defaults, not a validated continuation recipe.

Implication for the lever hierarchy above: under "Optimization", the first experiment is not "more steps" but the LR regime (no re-warm, VLM LR an order of magnitude below the head's, EMA on) against the default; under "Objective", on-policy data (RL or DAgger-style aggregation in the simulator) is the lever with measured headroom once supervised continuation plateaus.

## Sources

[XR1-TR] Table 4; [XR1-CODE]; [VLAB-CODE]; [VLAB-ISSUE-82]; [ERV-PAPER] Table 1; external survey links inline above.
