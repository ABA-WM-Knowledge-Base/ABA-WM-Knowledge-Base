---
id: world-model-kb.papers.diamond.optimization-transfer
title: DIAMOND Transferable Optimization Knowledge
kind: guide
status: maintained
last_updated: 2026-08-14
owners:
  - AIBuildAI world-model group
---

# DIAMOND Transferable Optimization Knowledge

## Retrieval metadata

**Relevant queries:** transfer DIAMOND, pixel EDM world model, visual detail for control, in-model actor-critic, 3-step denoising, frame-stack conditioning, AdaGN action, Cosmos3 Generator FD/WAM, or IRIS versus diffusion.

**Knowledge provided:** ten falsifiable hypotheses with Cosmos3-Nano attachment, minimum experiments, expected movement, and falsification. Atari Table 1 numbers are never used as evidence for CSGO branch behavior.

**Related pages:** [`paper.md`](paper.md); [diffusion and flow matching](../../foundations/learning-objectives/diffusion-and-flow-matching.md); [video world models](../../foundations/representations/video-world-model.md); [Cosmos3-Nano Generator](../../models/cosmos3-nano/generator.md); [action modeling](../../models/cosmos3-nano/action-modeling.md); [optimization playbook](../../models/cosmos3-nano/optimization-playbook.md).

Foundation evidence anchor: [REP-DIAMOND-2024]. Each item is a **hypothesis** until a controlled Cosmos3 experiment isolates it.

## 1. Transfer discipline

DIAMOND shows that an **image-space EDM** world model can train an actor-critic entirely in imagination on Atari 100k (mean HNS `1.459`, IQM `0.641`). Cosmos3-Nano Generator already performs flow-based video modeling with action conditioning. Transfers test whether DIAMOND-style **detail retention**, **few-step EDM**, and **in-model RL** improve Generator FD/WAM — not whether to replace Wan VAE + rectified flow with a 13M Atari U-Net.

Evidence strengths:

1. **direct architecture comparison:** Table 1 versus IRIS/STORM/DreamerV3; Table 7 denoising-step ablation; Table 4 compute;
2. **coupled system evidence:** joint WM + reward model + actor-critic under one 100k budget;
3. **qualitative / other-domain probes:** Appendix M CSGO/driving Table 8, which is **not** an Atari HNS result.

Do not assign Table 1 causal credit to CSGO demos.

## 2. Intervention matrix

| ID | Target failure | Mechanism transferred | Attachment surface | Primary evidence | Principal risk |
|---|---|---|---|---|---|
| `DIAMOND-XFER-01` | small visual cues lost in FD | image-space / high-res DM detail | Generator FD native resolution | Table 1 Asterix/Breakout/RoadRunner | codec already discards the cue |
| `DIAMOND-XFER-02` | WAM overfits real frames | train actor on WM rollouts only | WAM updates on Generator samples | Sec. 1, 3; in-WM agent | artifact exploitation |
| `DIAMOND-XFER-03` | global action blurs local sprites | AdaGN / per-frame action | FD spatial blocks | Table 2 AdaGN | parameter confound |
| `DIAMOND-XFER-04` | too few sampler steps blur control | imagination-time step count | Generator `num_steps` | Table 7 `3.052 -> 1.962` | latency without gain |
| `DIAMOND-XFER-05` | long imagination drifts | horizon `H` matched to backup | WAM rollout length | Table 3 `H=15` | short-step regression |
| `DIAMOND-XFER-06` | no reward on imagined frames | separate reward/termination head | auxiliary head on FD tokens | `rew_end_model.py`; Table 5 timing | misspecified reward |
| `DIAMOND-XFER-07` | VQ tokenizer erases contact | compare discrete vs full DM | optional tokenizer before temporal FD | Table 1 IRIS 1.046 vs 1.459 | compute confound |
| `DIAMOND-XFER-08` | imagined ranking fails on real | real-env promotion gate | eval on real vs imagined | deploy-on-real protocol | extra env budget |
| `DIAMOND-XFER-09` | DDPM-style long drift | EDM few-step score | flow/EDM sampler family | Sec. 5.1-5.2, Fig. 8 | domain-specific drift |
| `DIAMOND-XFER-10` | 3-D history via heavy cross-attn | frame-stack / channel concat | Generator history channels | Table 8 frame-stack vs cross-attn | Table 8 is not Atari HNS |

## 3. `DIAMOND-XFER-01`: preserve visual detail in FD

**Source mechanism.** DIAMOND argues that discrete-latent world models discard sprites that change the optimal action. On Atari 100k it records Breakout `132.5` versus IRIS `83.7` and DreamerV3 `31.0`, Asterix `3698.5` versus IRIS `853.6`, RoadRunner `20673.2` versus IRIS `9614.6`, with aggregate mean HNS `1.459` versus IRIS `1.046`. [DIASRC-PAPER, Table 1, Sec. 4.2, 5.3]

**Target behavior.** Improve Generator FD on tasks where millimetre contact, gripper edges, or small object identity drive success.

**Attachment.** Cosmos3-Nano **Generator FD/WAM** path at native Wan latent resolution. Do not attach to the Reasoner text tower. Avoid extra spatial downsampling unless ablated.

**Minimum controlled experiment.** Match data, optimizer, and sampler. Compare (a) default FD resolution, (b) extra 2x spatial downsample, (c) matched-parameter wider but more compressed FD. Report action-shuffle separation, contact timing, and FD loss.

**Expected movement.** Higher true-versus-shuffled action sensitivity and better contact event timing, with limited regression in passive FID.

**Falsification.** Reject if extra compression matches or beats native resolution on contact metrics, or if FD loss improves while WAM return is flat.

## 4. `DIAMOND-XFER-02`: train WAM entirely on generated rollouts

**Source mechanism.** The Atari agent updates `pi_phi` and `V_phi` inside `WorldModelEnv`; real env steps train the world model and reward head, not the inner RL loop. [DIASRC-PAPER, Sec. 3; DIASRC-CODE-CURRENT, `src/envs/world_model_env.py`]

**Target behavior.** Reduce WAM memorization of logged real frames when imagination is available.

**Attachment.** A WAM phase whose policy/value updates consume only Generator-rollout frames conditioned on proposed actions.

**Minimum controlled experiment.** Real-mixed versus WM-only WAM updates at matched env-query budget at evaluation. Log imagined versus real return gap.

**Expected movement.** Similar or better real-env return at equal queries if the Generator is calibrated; larger imagined-real gap flags exploitation.

**Falsification.** Reject if WM-only training wins on imagined return and loses on real env, or if real-mixed training matches WM-only at equal queries.

## 5. `DIAMOND-XFER-03`: local action conditioning (AdaGN)

**Source mechanism.** Atari DIAMOND injects actions with Adaptive Group Normalization rather than a single pooled trajectory vector. [DIASRC-PAPER, Table 2]

**Target behavior.** Restore per-frame action identity when Cosmos3 FD currently uses one chunk embedding.

**Attachment.** Per-frame or per-token AdaLN/AdaGN on Generator spatial/video blocks, analogous in spirit to IRASim Frame-Ada. Generator FD/WAM only.

**Minimum controlled experiment.** Global chunk condition versus per-frame AdaGN at matched parameter count, plus shuffled frame-action alignment.

**Expected movement.** Lower frame-indexed state error and larger shuffle gap.

**Falsification.** Reject if shuffled alignment matches true alignment, or if gains vanish under parameter matching.

## 6. `DIAMOND-XFER-04`: imagination-time denoising budget

**Source mechanism.** Table 1 uses 3 EDM steps. Reducing to 1 step on the top-10 games drops subset mean HNS from `3.052` to `1.962` (single seed for `n=1`), with Boxing `86.9 -> 41.9` and RoadRunner `20673.2 -> 5084.0`. [DIASRC-PAPER, Table 7]

**Target behavior.** Avoid media-default step counts that are either too cheap (blurred control) or too expensive (no extra return).

**Attachment.** Generator sampler `num_steps` used **inside** WAM imagination, not only for showcase videos. [`codebase.md`](codebase.md) analog is `config/trainer.yaml` `num_steps_denoising`.

**Minimum controlled experiment.** Sweep `{1, 3, 8, 16}` steps with fixed horizon and WAM LR. Report return, contact metrics, and milliseconds per imagined step.

**Expected movement.** A knee where extra steps stop helping control.

**Falsification.** Reject if 1-step already matches 3-step on control metrics, or if more steps help FID but not WAM return.

## 7. `DIAMOND-XFER-05`: imagination horizon curriculum

**Source mechanism.** Training uses `H=15` with `lambda=0.95` and `backup_every=15`. Play demos use horizon 50, which is visualization, not the training contract. [DIASRC-PAPER, Table 3; DIASRC-CODE-CURRENT]

**Target behavior.** Reduce exposure bias when WAM currently trains on one-step FD only.

**Attachment.** Curriculum on imagined horizon in the WAM loss, keeping a clean one-step regression suite.

**Minimum controlled experiment.** Fixed `H=1` versus `H=15` versus a 1-to-15 schedule. Horizon-stratified error and realized return.

**Expected movement.** Better long-chunk ranking without collapsing one-step FD.

**Falsification.** Reject if longer horizons always reduce realized return, or if play-horizon 50 is treated as a training hyperparameter without an ablation.

## 8. `DIAMOND-XFER-06`: auxiliary reward and termination heads

**Source mechanism.** A separate `R_psi` predicts reward and continuation; Table 5 shows 115 ms of a 543 ms update on 4090, so the head is cheap relative to actor-critic. [DIASRC-PAPER, Tables 2, 5; DIASRC-CODE-CURRENT, `src/models/rew_end_model.py`]

**Target behavior.** Enable imagination when Cosmos3 WAM currently requires a real env for scalar feedback.

**Attachment.** Auxiliary reward/continue MLP on Generator tokens for domains with scalar rewards. Not Reasoner.

**Minimum controlled experiment.** With versus without the head on WM-only WAM training; evaluate ranking of action proposals on real env.

**Expected movement.** Usable imagined returns and better proposal ranking.

**Falsification.** Reject if the head fits training reward but does not rank held-out real trajectories, or if it is unused at inference.

## 9. `DIAMOND-XFER-07`: discrete tokenizer versus full diffusion state

**Source mechanism.** Table 1 places IRIS (discrete tokens) at mean HNS `1.046` and DIAMOND at `1.459` under the world-model-trained class, with DIAMOND using 13M versus IRIS 30M parameters. [DIASRC-PAPER, Tables 1, 4]

**Target behavior.** Decide whether a VQ bottleneck before Cosmos3 temporal FD is worth the speed.

**Attachment.** Optional discrete bottleneck versus native DM tokens on Generator FD.

**Minimum controlled experiment.** Match parameters and data. Report contact metrics and WAM return, not FID alone.

**Expected movement.** Diffusion path wins on contact-heavy slices; VQ may win on latency.

**Falsification.** Reject if VQ matches diffusion on behavior metrics at lower cost — then do not pay for pixel EDM.

## 10. `DIAMOND-XFER-08`: real-environment validation gate

**Source mechanism.** After in-WM training, Table 1 is measured on **real** Atari. The paper does not promote agents from imagined score alone. [DIASRC-PAPER, Sec. 4.2]

**Target behavior.** Prevent Cosmos3 WAM from selecting actions that only look good under Generator artifacts.

**Attachment.** Require a real-env (or held-out real video) checkpoint eval before policy promotion; log imagined versus real gap.

**Minimum controlled experiment.** Select top-k by imagined value versus verify on real rollouts.

**Expected movement.** Smaller promotion error; detection of anti-correlated rankings.

**Falsification.** Reject if imagined ranking anti-correlates with real return and the gate is skipped, or if the gate consumes the entire evaluation budget without changing selection.

## 11. `DIAMOND-XFER-09`: EDM few-step score instead of many-step DDPM

**Source mechanism.** Section 5.1-5.2 and Figure 8 show DDPM world models drift in color over 1000 Breakout steps even at 10 denoising steps, while 1-step EDM remains more stable. Adaptive signal-noise mixing is the stated reason 3 steps suffice. [DIASRC-PAPER, Sec. 5.1-5.2, Appendix K]

**Target behavior.** Reduce long-rollout drift in Cosmos3 imagination without inflating step count.

**Attachment.** Prefer EDM/flow samplers with high-noise training mass for FD imagination; do not copy DDPM 50-step media recipes into the WAM inner loop.

**Minimum controlled experiment.** Matched U-Net/DiT: DDPM-50 versus EDM-3 versus EDM-1 on the same imagination horizon. Measure pixel drift, action sensitivity, and return.

**Expected movement.** Few-step EDM matches or beats many-step DDPM on control.

**Falsification.** Reject if DDPM-50 wins on both drift and return at acceptable latency.

## 12. `DIAMOND-XFER-10`: frame-stack history versus cross-attention encoder

**Source mechanism.** Appendix M Table 8, on **static CS:GO and driving datasets** (not Atari 100k), finds frame-stack FID/FVD better than a cross-attention history encoder (CS:GO FVD `34.8` versus `81.4`). This is a visual-quality architecture result under logged actions. It is **not** evidence for Table 1 HNS `1.459`. [DIASRC-PAPER, Table 8, Appendix M; DIASRC-CODE-CSGO-BRANCH]

**Target behavior.** Cheap autoregressive history for Generator FD when a full 3-D attention stack is too slow.

**Attachment.** Channel-concatenated recent latents into Generator spatial blocks as an alternative to a separate history cross-attention tower.

**Minimum controlled experiment.** Frame-stack versus cross-attention at matched parameters on Cosmos3 robot or AV clips. Report FD error and latency. Do **not** import CSGO checkpoints or cite Table 8 as Atari HNS.

**Expected movement.** Frame-stack wins on short AR fidelity per flop.

**Falsification.** Reject if cross-attention wins on long-horizon consistency at similar latency, or if the experiment silently uses CSGO weights to justify Atari or Cosmos3 robot claims.

## 13. Invalid generalizations

- Do not bind CSGO branch demos or Table 8 to Atari mean HNS 1.46 or to Cosmos3 robot numbers.
- Do not treat 1.46 as SOTA over BBF (`2.247`) or EfficientZero (`1.943`).
- Do not replace Wan VAE with an Atari pixel U-Net without a codec ablation.
- Do not call the agent DQN; it is actor-critic inside `WorldModelEnv`.
- Do not skip real-env validation when copying in-WM training.

## Sources

- [DIASRC-PAPER] Tables 1, 4, 5, 7, 8 and EDM analysis.
- [DIASRC-CODE-CURRENT] `config/trainer.yaml`, `world_model_env.py`, `rew_end_model.py`.
