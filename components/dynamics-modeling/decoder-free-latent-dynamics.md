---
id: world-model-kb.components.dynamics-modeling.decoder-free-latent-dynamics
title: Decoder-Free Latent Dynamics
kind: component
status: maintained
last_updated: 2026-08-27
owners:
  - AIBuildAI world-model group
---

# Decoder-Free Latent Dynamics

## Retrieval metadata

**Relevant queries:** TD-MPC2 dynamics, decoder-free transition, SimNorm, implicit latent world model, no reconstruction, exploding gradients TD-MPC.

**Knowledge provided:** How a latent transition can be learned without reconstructing observations, which TD-MPC2 results isolate the dynamics MLP, and why MPPI use is not the dynamics claim.

**Related pages:** [Latent world models](../../foundations/representations/latent-world-model.md) owns decoder-free representation; [planning and control](../../foundations/decision-making/planning-and-control.md) owns MPPI; [TD-MPC2 Paper](../../papers/td-mpc2/README.md) owns tables and the post-paper Q-init fix; [reconstructive latents](../world-representation/reconstructive-latents.md) for the contrasting decoder-backed state.

## Method definition

Decoder-free latent dynamics encode an observation once and predict the next latent without an observation likelihood:

\[
z_t = h(o_t),\qquad
z_{t+1} = d(z_t, a_t).
\]

There is no \(\log p(o_t\mid z_t)\) term. The transition is supervised by latent consistency, reward, and value targets in \(z\)-space. The representation claim (what \(z\) contains) and the dynamics claim (whether \(d\) is a usable \(p(z'\mid z,a)\)) remain separable. Adding a decoder is not part of the main TD-MPC2 recipe and was treated as a distractor relative to value learning. [TDMPC2-PAPER, Sec. 3; MBRL-TDMPC2-2024]

Planning with MPPI in this latent is a decision method. This page owns \(d\). Policy-only (`mpc=false`) is an ablation of search, not a different transition.

## TD-MPC2: SimNorm MLP transitions

TD-MPC2 applies SimNorm (\(V=8\), \(\tau=1\)) to encoder and dynamics outputs. Original TD-MPC had exploding gradients; SimNorm is described as essential for stability. The 5M-parameter split attributes about 843k parameters to dynamics versus about 3.16M to Q, so capacity is critic-heavy even though the transition is central to planning. [TDMPC2-PAPER, Sec. 3, architecture tables]

Shared planning/dynamics hyperparameters on 104 tasks include horizon \(H=3\), 6 planning iterations (+2 if \(|A|\ge 20\)), population 512, and 101-bin log-space reward/value regression. Discrete actions remain open. Visual RL uses a 64x64 conv encoder with random shift and remains decoder-free; it is comparable to DrQ-v2/DreamerV3 on 10 DMC tasks, not a pixel Generator. [TDMPC2-PAPER, Table 8, Sec. 4]

MT80 scale (1M score 16.0 through 317M score 70.6) mixes encoder, dynamics, and Q width. The 48M to 317M gain is small relative to compute. Do not attribute Table 1 solely to \(d\). Few-shot 19M pretrain then 10 held-out tasks at 2x scratch after 20k steps is an agent transfer result. [TDMPC2-PAPER, Table 1, Sec. 4]

The public pin `e9f59321933cbc8e11a002b842adc7d4ffae8ff1` changes Q-ensemble initialization. That is maintenance, not ICLR dynamics evidence. [TDMPC2-CODE]

## What this method is not

It is not Cosmos Generator FD, not Dreamer RSSM (which has a decoder head), not V-JEPA 2-AC (frozen encoder plus AC predictor), and not inverse dynamics. Transfers toward Cosmos3-Nano target Reasoner / latent planning, with Generator FD/WAM only as a latency or interface contrast. [TDMPC2-PAPER, Sec. 3]

## Controllable surfaces

| Surface | Mechanism | Expected observable | Main confounder |
|---|---|---|---|
| SimNorm \(V,\tau\) | simplex constraint on \(z\) | gradient stability | changed latent dimension |
| Latent consistency loss | trains \(d\) | multi-step \(z\) error | Q-loss dominating |
| Horizon \(H\) | how far \(d\) is queried | planning return | extra MPPI compute |
| Decoder on/off | reconstruction distractor | control versus recon | extra parameters |
| Task embedding | multitask \(d\) | held-out task score | dataset RAM and width |

## Evaluation and failure diagnosis

| Symptom | Plausible cause | Discriminating evidence |
|---|---|---|
| Exploding gradients | unconstrained \(z\) | SimNorm on/off |
| Strong Q, weak \(d\) | critic capacity | freeze Q, measure latent rollout |
| Visual DMC ≠ video WM | 64x64 encoder only | no FVD comparison |
| Paper vs pin mismatch | Q init delta | record SHA when quoting eval |
| Called pixel FD | naming | no decoder, no video |

## Cosmos3-Nano connection

A decoder-free latent \(d\) is a Reasoner-side hypothesis (compact state for short-horizon search), not a replacement for Generator rectified-flow FD. Test SimNorm-like constraints or latent consistency only with a named Nano state stream and without assuming MPPI is already present. [C3-TR, pp. 55–69]

## Sources

- [TDMPC2-PAPER], [TDMPC2-CODE], and [MBRL-TDMPC2-2024] identify decoder-free transitions, SimNorm, and the 104-task recipe.
