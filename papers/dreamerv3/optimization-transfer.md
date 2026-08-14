---
id: world-model-kb.papers.dreamerv3.optimization-transfer
title: DreamerV3 Transferable Optimization Knowledge
kind: guide
status: maintained
last_updated: 2026-08-14
owners:
  - AIBuildAI world-model group
---

# DreamerV3 Transferable Optimization Knowledge

## Retrieval metadata

**Relevant queries:** transfer DreamerV3, symlog, free bits, unimix, imagination actor-critic, categorical RSSM, Cosmos3 Generator FD/WAM, not pixel U-Net replacement.

**Knowledge provided:** ten falsifiable hypotheses. Nature is canonical; public `danijar/dreamerv3` is the attachment analog, not Google internal code.

**Related pages:** [`paper.md`](paper.md); [model-based RL](../../foundations/decision-making/model-based-rl.md); [Cosmos3-Nano action modeling](../../models/cosmos3-nano/action-modeling.md).

Foundation: [MBRL-DREAMERV3-2025].

## 1. Transfer discipline

DreamerV3 optimizes **control return** in a **compact latent RSSM**. Cosmos3-Nano Generator optimizes **continuous video latents**. Transfer only for matching failures (reward-scale blow-up, collapsed KL, no imagination credit). Do not treat Nature leadership as proof that symlog fixes Cosmos3 video FID.

Attach on Generator FD/WAM scalar heads and optional compact planner, not Reasoner text, unless a JEPA-style latent is the explicit target.

## 2. Intervention matrix

| ID | Target failure | Mechanism | Attachment | Evidence | Risk |
|---|---|---|---|---|---|
| `DREAMERV3-XFER-01` | reward scale outliers | symlog + two-hot | FD/WAM scalar heads | Nature robustness list | wrong on bounded [0,1] rewards |
| `DREAMERV3-XFER-02` | multi-loss collapse | free bits + `beta_rep=0.1` | joint WM losses | Nature KL clip 1 nat | under-regularized latents |
| `DREAMERV3-XFER-03` | one-step real data only | imag_length 15 | WAM imagination | Nature actor-critic | model exploitation |
| `DREAMERV3-XFER-04` | continuous latent blur | categorical latents | optional discrete bottleneck | RSSM categoricals | contact loss |
| `DREAMERV3-XFER-05` | actor ignores WM | critic on imagined returns | WAM critic | imagination training | critic-only gains |
| `DREAMERV3-XFER-06` | pixel WM too slow | compact RSSM + Generator renderer | two-timescale | Minecraft 1 GPU | extra latency |
| `DREAMERV3-XFER-07` | per-task norm drift | fixed global perc/symlog | shared stats | BSuite scale robustness | domain interference |
| `DREAMERV3-XFER-08` | missing terminals | continue head | FD continue | continue predictor | unused auxiliary |
| `DREAMERV3-XFER-09` | overconfident categoricals | 1% unimix | discrete heads | Nature unimix | entropy too high |
| `DREAMERV3-XFER-10` | replay off-policy collapse | large online replay | buffer | Nature replay list; `replay.size 5e6` | memory |

## 3. `DREAMERV3-XFER-01`: symlog and two-hot scalars

**Source mechanism.** Vector observations use symlog; reward and critic use symexp two-hot (`sign(x)(exp(|x|)-1)` inverse) with 255 bins in the public config to handle signed, heavy-tailed scales without running-stat nonstationarity. Nature lists this among "changes introduced for DreamerV3". [DV3SRC-PAPER-NATURE; DV3SRC-CODE-CURRENT, `rewhead.output: symexp_twohot`]

**Target behavior.** Cosmos3 WAM value/reward heads that diverge on mixed robotics/game scales.

**Attachment.** Apply to **scalar** FD/WAM targets in [action modeling](../../models/cosmos3-nano/action-modeling.md), not to entire diffusion latents and not to Reasoner text.

**Minimum controlled experiment.** Linear versus standardization versus symlog+two-hot on three reward scales. Report FD error, return, and calibration. Hold RSSM size and `imag_length` fixed.

**Expected movement.** Stable critic across scales; BSuite-like scale robustness.

**Falsification.** Reject if linear matches on all three domains, or if loss improves while closed-loop return drops.

## 4. `DREAMERV3-XFER-02`: free bits and KL balance

**Source mechanism.** `L_dyn` and `L_rep` clip below 1 nat (~1.44 bits); `beta_pred=1`, `beta_dyn=1`, `beta_rep=0.1` plus KL balancing via stop-gradient avoids dead or trivial latents across visual complexity. Public key: `free_nats: 1.0`. [DV3SRC-PAPER-NATURE; DV3SRC-CODE-CURRENT, `dreamerv3/rssm.py`]

**Target behavior.** Joint Generator + auxiliary losses where one term vanishes.

**Attachment.** Clip KL-like regularizers on compact state tokens; keep prediction loss dominant. Not Reasoner.

**Minimum controlled experiment.** No clip versus 1 nat versus 0.1 nat; sweep `beta_rep`. Report latent entropy, reconstruction, and imagination return.

**Expected movement.** Informative yet predictable latents without per-domain retuning.

**Falsification.** Reject if clipping equals no KL, or if reconstruction wins while imagination return falls.

## 5. `DREAMERV3-XFER-03`: short imagination rollouts

**Source mechanism.** Actor-critic trains on imagined latent trajectories. Public default `imag_length: 15`. Nature trains concurrently from replay while acting. [DV3SRC-PAPER-NATURE; DV3SRC-CODE-CURRENT]

**Target behavior.** WAM that never trains through Generator rollouts.

**Attachment.** WAM self-consistency / imagined return on Generator latents (compact planner), not pixel-FID.

**Minimum controlled experiment.** Real-only versus imag-15 versus imag-1. Real-env return at matched env steps. Include a real-env validation gate (same lesson as DIAMOND `DIAMOND-XFER-08`).

**Expected movement.** Better sample efficiency if the latent WM is calibrated.

**Falsification.** Reject if imagination helps imagined return only (exploitation).

## 6. `DREAMERV3-XFER-04`: categorical state bottleneck

**Source mechanism.** RSSM uses softmax categoricals (`stoch=32`, `classes=64` default). [DV3SRC-CODE-CURRENT]

**Target behavior.** Continuous FD tokens that smear over long Minecraft-like horizons.

**Attachment.** Optional discrete bottleneck **before** a compact planner, not replacing Wan VAE for pixels.

**Minimum controlled experiment.** Continuous vs categorical compact state, matched params.

**Expected movement.** Better long-horizon item collection; possible pixel quality drop if used as a codec.

**Falsification.** Reject if discreteness hurts contact without horizon benefit.

## 7. `DREAMERV3-XFER-05`: critic on imagined returns

**Source mechanism.** Critic learns values of imagined states; actor maximizes them with entropy (`actent` 3e-4 public). [DV3SRC-PAPER-NATURE]

**Target behavior.** Policy that uses FD only as a renderer, not for credit assignment.

**Attachment.** WAM critic on predicted latent returns.

**Minimum controlled experiment.** Actor from real TD vs imagined lambda-returns.

**Expected movement.** Sparse-reward tasks move first (Minecraft-style).

**Falsification.** Reject if gains track a better critic on real data only, independent of rollouts.

## 8. `DREAMERV3-XFER-06`: two-timescale compact planner + video renderer

**Source mechanism.** Dreamer is fast enough for 1 A100 Minecraft diamonds; pixel diffusion WMs (DIAMOND Table 4) are slower. [DV3SRC-PAPER-NATURE; contrast DIASRC-PAPER Table 4]

**Target behavior.** Cosmos3 inner loop too slow for RL.

**Attachment.** RSSM-like planner in latent, Generator as occasional renderer.

**Minimum controlled experiment.** Generator-only imagination vs compact planner + freeze Generator.

**Expected movement.** Higher env-step throughput; return competitive if latents suffice.

**Falsification.** Reject if two-timescale adds latency without return, or if the planner ignores pixels that the Generator needed.

## 9. `DREAMERV3-XFER-07`: global normalization across tasks

**Source mechanism.** Fixed hyperparameters including percentile returns; BSuite scale-robustness is highlighted. [DV3SRC-PAPER-NATURE]

**Target behavior.** Per-task running stats that break when Cosmos3 mixes domains.

**Attachment.** Shared perc/symlog stats across FD domains, with a domain-id ablation.

**Minimum controlled experiment.** Global vs per-domain norm on mixed rewards.

**Expected movement.** Global wins on scale-shift slices.

**Falsification.** Reject if per-domain norm strictly dominates without instability.

## 10. `DREAMERV3-XFER-08`: continue / discount head

**Source mechanism.** Continue predictor with logistic loss; public `contdisc: True`. [DV3SRC-PAPER-NATURE]

**Target behavior.** Infinite-horizon imagination past episode ends.

**Attachment.** FD terminal/continue auxiliary.

**Minimum controlled experiment.** With vs without continue head on episodic tasks.

**Expected movement.** Better episode-boundary values.

**Falsification.** Reject if the head is unused at inference or harms calibration.

## 11. `DREAMERV3-XFER-09`: unimix on discrete heads

**Source mechanism.** 1% uniform mix on RSSM and actor categoricals. [DV3SRC-PAPER-NATURE; `unimix: 0.01`]

**Target behavior.** Collapsed discrete action or latent codes.

**Attachment.** Unimix on any categorical WAM/ID head (including LAPA-style codes if discrete).

**Minimum controlled experiment.** 0 vs 0.01 vs 0.05 unimix.

**Expected movement.** Higher entropy early, no collapse; small final-return cost.

**Falsification.** Reject if 0% unimix matches 1% on collapse diagnostics.

## 12. `DREAMERV3-XFER-10`: large online replay of latents

**Source mechanism.** Nature lists larger capacity, online queue, storing latent states. Public `replay.size: 5e6`, `online: True`. [DV3SRC-PAPER-NATURE; `embodied/core/replay.py`]

**Target behavior.** Tiny buffers that overfit recent Generator failures.

**Attachment.** WAM replay of latent transitions, not only raw video.

**Minimum controlled experiment.** 1e5 vs 5e6, online on/off.

**Expected movement.** More stable imagination targets.

**Falsification.** Reject if larger replay only delays learning without final return gain.

## 13. Invalid generalizations

- Do not retitle the work *Mastering Diverse Domains...* as canonical.
- Do not cite `danijar/dreamerv3` as Google-internal.
- Do not paste DIAMOND Atari100k 1.459 into DreamerV3 Nature Atari 200M.
- Do not attach all robustness tricks to Reasoner JEPA without a latent-state hypothesis.
- Do not treat public `imag_length: 15` as a Nature table cell.
- Do not claim Extended Data Table 1 numbers that were not extracted.
- Pixel-diffusion WMs (DIAMOND, Vista) are a different class; transfer RSSM robustness to compact latent WAM, not as a drop-in UNet loss.

## 14. Transfer record template

```text
Hypothesis ID (DREAMERV3-XFER-NN):
Nature vs public reimplementation:
Attachment (latent WAM/ID, not Reasoner text, not pixel FID):
Config keys held fixed:
Metrics (return, collapse diagnostics, scale robustness):
Decision:
```

No transfer experiment is registered.

## 15. Attachment checklist for Cosmos3

| Do | Do not |
|---|---|
| Transfer RSSM robustness to compact latent WAM | Drop-in UNet / pixel FID losses |
| Keep Nature as the result surface | Treat `danijar/dreamerv3` as Google-internal |
| Separate Atari 200M, Atari100k, and DIAMOND HNS | Paste 1.459 into Nature tables |
| Record `free_nats` / `unimix` / `imag_length` from `configs.yaml` | Invent Extended Data Table 1 cells |
| Label public-code curves as reimplementation | Claim Nature binary replica |

## Sources

- [DV3SRC-PAPER-NATURE], [DV3SRC-CODE-CURRENT].
