---
id: world-model-kb.components.dynamics-modeling.recurrent-latent-dynamics
title: Recurrent Latent Dynamics
kind: component
status: maintained
last_updated: 2026-08-27
owners:
  - AIBuildAI world-model group
---

# Recurrent Latent Dynamics

## Retrieval metadata

**Relevant queries:** RSSM transition, MDN-RNN dynamics, Dreamer latent dynamics, prior versus posterior rollout, overshooting, model exploitation temperature.

**Knowledge provided:** How recurrent latent models implement \(p(z_{t+1}\mid z_t,a_t,h_t)\), which World Models and DreamerV3 results speak to the transition rather than the actor, and how imagination use is separated from the dynamics claim.

**Related pages:** [Forward dynamics](../../foundations/problem-formulation/forward-dynamics.md) owns the FD contract; [reconstructive latents](../world-representation/reconstructive-latents.md) owns \(z\) as state; [latent simulation and imagination](../reasoning/latent-simulation-and-imagination.md) owns actor–critic through imagination; [DreamerV3 Paper](../../papers/dreamerv3/README.md) owns Nature evidence.

## Method definition

Recurrent latent dynamics maintain a deterministic memory \(h_t\) and a stochastic state \(z_t\), then predict the next state without requiring the next observation:

\[
h_t = f_\theta(h_{t-1}, z_{t-1}, a_{t-1}),\qquad
p_\theta(z_t\mid h_t),\qquad
q_\phi(z_t\mid h_t,o_t).
\]

The **posterior** \(q\) is used when the next observation is available (training, filtering). The **prior** \(p\) is the open-loop transition used in imagination. A dynamics claim must say which of those two is evaluated. One-step posterior accuracy does not establish prior-rollout calibration.

Using the prior to train an actor is a reasoning method. This page owns the transition; the [imagination page](../reasoning/latent-simulation-and-imagination.md) owns decision use.

## World Models: mixture-density recurrent transition

After the VAE produced \(z_t\), World Models trained an MDN-RNN \(p(z_{t+1}\mid z_t,a_t,h_t)\). Mixture outputs matter because the next latent is not generally unimodal. Sampling temperature changed how sharply the virtual environment followed learned modes. On VizDoom, low temperature kept virtual scores above 2,000 while real scores stayed below 200; raising temperature reduced the gap, with reported real score peaking near temperature 1.15. That is transition-model exploitation, not only controller failure. [FND-WORLD-MODELS-2018, Table 2; COMP-REASONING-WORLD-MODELS-PROJECT]

CarRacing Table 1 compares controllers with and without \(M\). It supports a useful recurrent transition under that protocol; it does not isolate every architectural difference from \(V\) and \(C\). [FND-WORLD-MODELS-2018, Table 1]

## Dreamer and DreamerV3: RSSM transitions for imagination

Dreamer predicted observations, rewards, and continuation from RSSM states and rolled the learned transition while the actor produced actions. The transition is on the gradient path from actions to imagined return. [MBRL-DREAMER-2020, Secs. 2–3]

DreamerV3 kept that transition and added robustness that directly affects latent dynamics learning: KL balancing and free bits for prior–posterior use of \(z\), plus categorical mixtures. Figure 6 reports that KL balancing and free bits had the largest aggregate effect on the 14-task ablation set. Those knobs are dynamics-training levers, not policy tricks. [MBRL-DREAMERV3-2025, pp. 648–650, Fig. 6; DV3SRC-PAPER-NATURE, Fig. 6]

Minecraft diamond results and eight-domain coverage are agent-level outcomes. They mix dynamics, actor, critic, and exploration. Use them as existence proofs of a working stack, not as isolated transition metrics. Extended Data Table 1 numeric cells were not recovered; do not invent them. [DV3SRC-PAPER-NATURE]

## Controllable surfaces

| Surface | Mechanism | Expected observable | Main confounder |
|---|---|---|---|
| Prior versus posterior evaluation | open-loop versus filtered | horizon-conditioned prior error | teacher-forced one-step loss |
| Overshooting / multi-step latent loss | train on imagined \(z\) | lower long-horizon drift | loss-scale change |
| Stochasticity / mixtures | multimodal \(z'\) | calibration and mode coverage | temperature as a free eval knob |
| KL balance / free bits | information in the prior | stable prior rollouts | replay ratio |
| Imagination horizon | how long the prior is trusted | return versus virtual–real gap | extra actor compute |

## Evaluation and failure diagnosis

| Symptom | Plausible cause | Discriminating evidence |
|---|---|---|
| Accurate decode, drifting prior | posterior uses future pixels | posterior-versus-prior curves |
| High imagined value, low return | biased \(p(z'\mid z,a)\) or reward head | replay the same actions in env |
| Temperature fixes virtual scores | overconfident mixture | report real and virtual together |
| RSSM called a video generator | decoder treated as the model | who consumes \(z'\) |

## Cosmos3-Nano connection

Nano Generator is not an RSSM. Recurrent latent evidence informs FD hypotheses about action-sensitive multi-step losses and prior-rollout calibration on action-conditioned latents, each to be measured on the Generator checkpoint. Contracts remain on [action modeling](../../models/cosmos3-nano/action-modeling.md).

## Sources

- [FND-WORLD-MODELS-2018] and [COMP-REASONING-WORLD-MODELS-PROJECT] identify MDN-RNN transitions and temperature exploitation.
- [MBRL-DREAMER-2020], [MBRL-DREAMERV3-2025], and [DV3SRC-PAPER-NATURE] identify RSSM transition evidence.
