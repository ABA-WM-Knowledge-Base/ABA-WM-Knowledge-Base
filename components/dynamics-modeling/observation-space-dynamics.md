---
id: world-model-kb.components.dynamics-modeling.observation-space-dynamics
title: Observation-Space Dynamics
kind: component
status: maintained
last_updated: 2026-08-27
owners:
  - AIBuildAI world-model group
---

# Observation-Space Dynamics

## Retrieval metadata

**Relevant queries:** visual forward dynamics, next-frame transition, action-conditioned video dynamics, IRASim rollout, DIAMOND imagination transition, Vista control, iVideoGPT act-cond, train-rollout mismatch.

**Knowledge provided:** How next-observation models implement transitions, which tests distinguish continuation from action-conditioned dynamics, and how chained clips accumulate generated-state error.

**Related pages:** [Action-conditioned video modeling](../generative-modeling/action-conditioned-video.md) owns action-timing interfaces; [observation-space state](../world-representation/observation-space-state.md) owns pixels as state; [diffusion](../generative-modeling/diffusion.md) and [autoregressive generation](../generative-modeling/autoregressive.md) own sampler families; [forward dynamics](../../foundations/problem-formulation/forward-dynamics.md) owns the FD contract.

## Method definition

Observation-space dynamics predict future sensory variables:

\[
p_\theta(o_{t+1:t+H}\mid o_{\leq t}, a_{t:t+H-1}, c).
\]

The backbone may be diffusion, flow, or autoregressive tokens. This page owns the **transition role**: action sensitivity, multi-step drift, and train–rollout mismatch. The Generative Modeling Component owns how samples are drawn.

Teacher-forced training on real prefixes does not prepare the model for feeding its own outputs back as context. Logged-action reconstruction does not isolate counterfactual dynamics.

## IRASim: action-chunk visual FD

IRASim implements \(p_\theta(I_{t+1:t+n+1}\mid I_{t-h:t}, a_{t:t+n})\) with frame-level action modulation in a latent diffusion transformer. Short-trajectory prediction measures reconstruction under logged actions. Long-trajectory prediction chains clips and accumulates generated-state error. [IRASRC-PAPER-V2, Eq. 1, pp. 4–6]

LIBERO policy evaluation and Push-T planning use generated rollouts with **external** judges or value heads. They are not pure dynamics metrics. The Push-T \(P=0\) row, where larger search helps only after failure-rollout adaptation, is evidence that search amplifies transition/evaluator error. Public code lacks the v2 planning pipeline; paper mechanism and release must stay separate. [IRASRC-PAPER-V2, pp. 9–14, Table 5; IRASRC-CODE-CURRENT]

## DIAMOND: pixel transitions inside MBRL

DIAMOND’s denoiser is the transition: next RGB from a 4-frame stack and a discrete action, with a separate reward/termination head. The actor trains on \(H=15\) imagined steps at 3 Euler denoising steps. Changing the denoising budget changes the imagined transition the policy sees (top-10 subset 3.052 versus 1.962 HNS). Atari 100k Table 1 is an agent score, not a per-game dynamics win rate. CSGO is not this transition. [DIASRC-PAPER, Secs. 3 and 5, Tables 1 and 7]

## Vista and iVideoGPT: controlled versus action-free video

Vista’s action-free Table 2 FID/FVD is continuation quality. Controlled Table 3 IDM L2 tests whether trajectory/command/steer/goal conditions move the predicted driving future; Waymo is unseen. Reward Table 4’s 0.014 gap is a weak ranking signal, not a planner. [VISTA-PAPER, Tables 2–4]

iVideoGPT first learns action-free tokens, then named action-conditioned checkpoints (BAIR FVD 75.0 to 60.8). OXE pretrain is action-free because action spaces are heterogeneous. Do not treat `ivideogpt-oxe-64-act-cond` as Table 1 OXE pretrain. RLVR-World is a later paper. [IVG-PAPER, Tables 1–2]

## Controllable surfaces

| Surface | Mechanism | Expected observable | Main confounder |
|---|---|---|---|
| Action alignment in time | which frames an action affects | swapped-action pairs | prompt-only control |
| Context refresh / chaining | generated \(o\) re-enters the model | horizon-conditioned drift | teacher-forced eval |
| Sampler steps / CFG | imagined transition distribution | policy or IDM vs NFE | best-of-N |
| Logged versus counterfactual actions | reconstruction versus FD | held-out interventions | dataset action coverage |
| External judge / value | planning loop | \(P=0\) versus adapted WM | judge bias |

## Evaluation and failure diagnosis

| Symptom | Plausible cause | Discriminating evidence |
|---|---|---|
| Sharp clip, action ignored | condition bypass | matched swapped actions, fixed noise |
| Short clip good, long chain fails | train–rollout mismatch | prefix versus generated context |
| FVD gain, worse ranking | perceptual transition | policy eval or IDM |
| Paper planning, missing code | release gap | bind v2 paper vs SHA |
| Driving FID used as robot FD | domain leakage | embodiment and action schema |

## Cosmos3-Nano connection

Generator FD is this family when the output is future observation given action. Test action counterfactual sensitivity and chained generated context on the FD surface, not Reasoner text and not Policy-DROID. Exact padding and H-actions/H+1-observations structure remain on [action modeling](../../models/cosmos3-nano/action-modeling.md).

## Sources

- [IRASRC-PAPER-V2] and [IRASRC-CODE-CURRENT] identify IRASim visual FD and release limits.
- [DIASRC-PAPER] identifies pixel transitions and denoising-step effects.
- [VISTA-PAPER] and [IVG-PAPER] identify continuation versus action-conditioned video dynamics.
