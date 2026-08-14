---
id: world-model-kb.papers.td-mpc2.optimization-transfer
title: TD-MPC2 Transferable Optimization Knowledge
kind: guide
status: maintained
last_updated: 2026-08-14
owners:
  - AIBuildAI world-model group
---

# TD-MPC2 Transferable Optimization Knowledge

## Retrieval metadata

**Relevant queries:** transfer TD-MPC2, latent MPC Cosmos3, decoder-free world model, Q ensemble planning, SimNorm, MPPI, 104-task hparams, or Reasoner latent planning.

**Knowledge provided:** ten fully expanded hypotheses with source mechanism, target behavior, attachment, minimum experiment, expected movement, and falsification.

**Related pages:** [MBRL-TDMPC2-2024]; [`paper.md`](paper.md); [Cosmos3-Nano reasoner](../../models/cosmos3-nano/reasoner.md); [planning and control](../../foundations/decision-making/planning-and-control.md).

## 1. Transfer discipline

TD-MPC2 is **sim continuous-control** with **decoder-free** latents and MPPI. Attach to **Reasoner-encoded state or a compact z-planner**, not Cosmos3 **Generator FD/WAM pixels**, unless the Generator path is an explicit contrastive baseline. The pinned-repo Q-ensemble init fix is maintenance, not a transfer mechanism. [TDMPC2-PAPER; TDMPC2-CODE; MBRL-TDMPC2-2024]

## 2. Intervention matrix

| ID | Failure | Mechanism | Attachment | Evidence | Risk |
|---|---|---|---|---|---|
| `TDMPC-XFER-01` | reconstructive WM starves Q | decoder-free `d(z,a)` | Reasoner z | Sec. 3 | dropped visual cues |
| `TDMPC-XFER-02` | policy-only, no search | MPPI on z | latent planner | Eq. 6, Table 8 | dynamics too noisy |
| `TDMPC-XFER-03` | single Q overfits | 5 Q ensemble | Q heads | Sec. 3 | compute |
| `TDMPC-XFER-04` | per-task yaml explosion | one hparam set | shared yaml | 104 tasks | Cosmos diversity |
| `TDMPC-XFER-05` | specialist negative transfer | task embeddings + masks | multitask trunk | Table 1, Table 9 | tail collapse |
| `TDMPC-XFER-06` | exploding latents | SimNorm | z groups | Eq. 5, Table 8 | unused |
| `TDMPC-XFER-07` | pixel MPC too slow | z vs video MPC | Reasoner vs Generator | Table 1 GPU-days | contact needs pixels |
| `TDMPC-XFER-08` | model-only no TD | CE reward/value in log space | Q+reward heads | Eq. 3 | misspec bins |
| `TDMPC-XFER-09` | 317M overkill | 48M vs 317M | width | Table 1 68.0 vs 70.6 | memory |
| `TDMPC-XFER-10` | no few-shot adapt | 70->10 finetune | freeze encoder | Sec. 4 2x @ 20k | data privilege |

## 3. `TDMPC-XFER-01`: decoder-free latent transitions

**Source mechanism.** No observation decoder. Latent `z` is trained for reward, TD backups, and short-horizon search. Reconstruction is treated as a distractor. [TDMPC2-PAPER, Sec. 3; MBRL-TDMPC2-2024]

**Target behavior.** Allocate Cosmos3 Reasoner capacity to control-relevant state rather than pixels.

**Attachment.** Train `d(z,a)` + Q on Reasoner-encoded states **without** a decode loss. Generator FD/WAM is a contrastive baseline only.

**Minimum experiment.** Decoder-free Reasoner WM vs Dreamer-style reconstructive WM, matched parameters and sim tasks. Hold SimNorm, 101-bin critics, and the Table 8 planner fixed so the ablation isolates reconstruction. Report return/success, a pixel or VAE-latent probe that the decoder-free model is allowed to lose, and parameter split (in TD-MPC2 the 5M Q ensemble is 3.16M of ~5.39M). [TDMPC2-PAPER, architecture tables]

**Expected movement.** Equal or better return at lower decode FLOPs; possible loss on visual inspection metrics.

**Falsification.** Reconstructive WM dominates all control KPIs at equal parameters, or decoder-free gains vanish once the decoder's extra parameters are given to the Q heads of the reconstructive baseline.

Do not score this transfer on Generator FID/FVD. Those metrics belong to FD/WAM video, which is a labeled baseline (`TDMPC-XFER-07`), not the Reasoner attachment. A Cosmos3 experiment that changes both Reasoner latents and Generator denoisers cannot attribute a gain to TD-MPC2.

## 4. `TDMPC-XFER-02`: short-horizon MPPI on latents

**Source mechanism.** Default planning: horizon 3, 6 iterations, 512 samples, 64 elites, temperature 0.5; extra iterations when `|A| >= 20`. [TDMPC2-PAPER, Table 8, Eq. 6; TDMPC2-CODE, `TDMPC2._plan`]

**Target behavior.** Improve closed-loop return versus a Reasoner policy head alone.

**Attachment.** Wrap Cosmos policy with TD-MPC2-style MPPI on encoded state.

**Minimum experiment.** `H=0` (policy prior) vs `H=3` vs `H=15` at fixed checkpoint.

**Expected movement.** Planning beats policy-only on contact-rich sim; diminishing returns past a short H.

**Falsification.** Planning never beats policy-only beyond noise.

## 5. `TDMPC-XFER-03`: Q ensemble disagreement

**Source mechanism.** Five Q-functions; TD uses min of two subsampled members; planning uses average of two. [TDMPC2-PAPER, Sec. 3; TDMPC2-CODE, `WorldModel.Q`]

**Target behavior.** Penalize high-variance imagined trajectories.

**Attachment.** Ensemble `{Q_i}` on Reasoner z; optional variance penalty in MPPI scores.

**Minimum experiment.** 1 vs 5 Q at matched sample budget on contact-rich sim.

**Expected movement.** Better robustness / fewer catastrophic plans.

**Falsification.** Ensemble raises compute with no success gain or worse calibration.

## 6. `TDMPC-XFER-04`: single hyperparameter template

**Source mechanism.** One Table 8 yaml across 104 online specialist tasks (DMControl, Meta-World, ManiSkill2, MyoSuite). Discrete actions remain open. [TDMPC2-PAPER, Abstract, Sec. 4, Table 8]

**Target behavior.** Avoid per-task Cosmos sim yaml grids.

**Attachment.** One yaml for DMControl-class, Meta-World-class, and manipulation sims.

**Minimum experiment.** 20+ tasks, no per-task tuning; median normalized score.

**Expected movement.** Competitive median without specialist knobs.

**Falsification.** >30% of tasks need task-specific tuning to reach TD-MPC2 fractions.

## 7. `TDMPC-XFER-05`: multitask latent WM with task embeddings

**Source mechanism.** 80-task offline agent: learned task embeddings, action masks, up to 317M. Data are 545M transitions from 240 specialists—not online 80-env interaction. [TDMPC2-PAPER, Sec. 3-4, Tables 1, 9]

**Target behavior.** Share a Reasoner trunk across Cosmos sim families without collapsing tails.

**Attachment.** Task-conditioned dynamics + shared trunk; report histogram not mean only.

**Minimum experiment.** Multitask vs specialists on 20 manipulation tasks.

**Expected movement.** Higher median; watch catastrophic tail tasks.

**Falsification.** Multitask median wins while a large tail regresses with no mitigation.

## 8. `TDMPC-XFER-06`: SimNorm stabilizers

**Source mechanism.** Simplicial normalization on latent groups; original TD-MPC exploded without it. [TDMPC2-PAPER, Sec. 3, Eq. 5, Table 8]

**Target behavior.** Stable multitask Q learning in Reasoner latent space.

**Attachment.** Simplex normalization on z groups or Q inputs.

**Minimum experiment.** With/without SimNorm on an 80-task-scale subset.

**Expected movement.** Fewer gradient explosions; higher late-training score.

**Falsification.** Ablation shows no effect on stability or interference metrics.

## 9. `TDMPC-XFER-07`: latent planning vs Generator video MPC

**Source mechanism.** Control KPIs without pixel generation. 317M MT80 = 33 GPU-days, score 70.6. [TDMPC2-PAPER, Table 1]

**Target behavior.** Cut wall-clock versus short Cosmos3 Generator rollout MPC.

**Attachment.** Compare z-planning (Reasoner) vs 1-step Generator video MPC on identical tasks.

**Minimum experiment.** Timestamped control loop; matched success.

**Expected movement.** Latent MPC Pareto-dominates on latency at equal success for coarse control.

**Falsification.** Video MPC Pareto-dominates—visual rollouts required for contact alignment.

## 10. `TDMPC-XFER-08`: discrete log-space reward/value

**Source mechanism.** 101 bins on `[-10,+10]`; two-hot CE; log-space decode (`two_hot_inv`). Not scalar MSE. [TDMPC2-PAPER, Sec. 3, Eq. 3; TDMPC2-CODE]

**Target behavior.** Train Q across heterogeneous Cosmos reward scales.

**Attachment.** Categorical reward/value heads on Reasoner; compare to MSE.

**Minimum experiment.** Full TD-MPC2 loss vs latent consistency without Bellman Q; and CE vs MSE.

**Expected movement.** Better sample efficiency and fewer explosions.

**Falsification.** Model-only matches TD, or MSE matches CE on all reward scales.

## 11. `TDMPC-XFER-09`: 48M vs 317M capacity

**Source mechanism.** MT80 scores: 1M=16.0, 48M=68.0, 317M=70.6 at 4 / 12 / 33 GPU-days. [TDMPC2-PAPER, Table 1]

**Target behavior.** Avoid deploying 317M when 48M captures most return.

**Attachment.** Width sweep of Reasoner planner; hardware context required.

**Minimum experiment.** 19M / 48M / 317M analogs, matched data.

**Expected movement.** Knee near 48M-class width.

**Falsification.** 317M analog is required for the tail tasks that matter.

## 12. `TDMPC-XFER-10`: few-shot finetune of a multitask WM

**Source mechanism.** 19M agent on 70 tasks, finetuned on 10 held-out: **2x** scratch at 20k env steps. [TDMPC2-PAPER, Sec. 4]

**Target behavior.** Adapt a Cosmos Reasoner WM to a new sim task with few interactions.

**Attachment.** Freeze early encoder; finetune dynamics/Q on the new task.

**Minimum experiment.** Scratch vs frozen-encoder finetune at 20k steps.

**Expected movement.** Finetune ~2x scratch early; gap may close later.

**Falsification.** Scratch matches finetune at 20k (pretrain unused).

## 13. Interaction map

The ten hypotheses are not independent:

- Decoder-free allocation (`01`) is only interpretable if SimNorm (`06`) and discrete critics (`08`) are held fixed or crossed.
- Ensemble (`03`) and MPPI (`02`) jointly determine whether search is optimistic. Extra iterations for `|A|>=20` (Table 8) belong with `02`, not with width (`09`).
- Single-hparam discipline (`04`) should be measured before declaring a Cosmos task “too hard for TD-MPC2.”
- Offline mix (`05`) is the data support for few-shot (`10`); do not attribute 20k-step gains to architecture if the mix already contains near-duplicates.
- Width (`09`) interacts with Table 1 GPU-days: 48M already scores 68.0 versus 317M at 70.6.
- Video MPC (`07`) is the contrast that keeps Generator FD/WAM out of the other nine attachments.

A factorial or staged ablation may be statistically efficient. This KB does not schedule experiments.

## 14. Invalid generalizations

- Do not infer real-robot competence from 104 simulated tasks.
- Do not attach TD-MPC2 mechanisms to Generator pixels or claim an FD/WAM improvement from these hypotheses.
- Do not treat the Q-init fix at `e9f5932…` as an optimization idea.
- Do not treat 317M (70.6) as required when 48M already scores 68.0. [TDMPC2-PAPER, Table 1]
- Do not cite MT80 Table 1 as online-from-scratch multitask: the 80-task agent uses **545M transitions from 240 specialists** and **128 GB** RAM. [TDMPC2-PAPER, Sec. 4]
- Do not assume discrete actions work; the paper leaves them open.
- Do not claim a planning gain when horizon, population, Q ensemble, and data mix all changed.
- Do not transfer visual 64x64 conv+shift into a Reasoner that already has a different patch geometry without an adapter.

## 15. Transfer record template

```text
Transfer ID:
Source mechanism and exact evidence:
Target failure signature:
Target-model attachment point (Reasoner / latent planner, not Generator):
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

- [TDMPC2-PAPER] mechanism, experiments, and numerical evidence.
- [TDMPC2-CODE] released attachment points and Table 8 defaults.
- [MBRL-TDMPC2-2024] Foundation identity.
- [Cosmos3-Nano reasoner](../../models/cosmos3-nano/reasoner.md) target attachment.
