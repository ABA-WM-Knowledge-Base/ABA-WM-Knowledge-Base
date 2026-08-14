---
id: world-model-kb.foundations.representations.latent-world-model
title: Latent World Models
kind: concept
status: maintained
last_updated: 2026-08-14
owners:
  - AIBuildAI world-model group
---

# Latent World Models

## Retrieval metadata

**Relevant queries:** latent dynamics, RSSM, latent state-space model, VAE world model, discrete latent, tokenizer, posterior collapse, imagination, or rate-distortion.

**Knowledge provided:** latent-state formulations, major continuous and discrete families, objective trade-offs, and tests for whether compression preserves dynamics and task-relevant information.

**Related pages:** [State, observation, and belief](../problem-formulation/state-observation-and-belief.md) distinguishes latent state from belief; [video world models](video-world-model.md) covers decoded observation rollouts; [problem formulation](../problem-formulation/problem-formulation.md) owns transition and task heads.

## Definition and formalism

A latent world model maps history or observations to a learned variable `z_t` and predicts evolution in that space. A recurrent state-space form is

```text
h_t = f_theta(h_{t-1}, z_{t-1}, a_{t-1}),
prior:     p_theta(z_t | h_t),
posterior: q_theta(z_t | h_t, o_t),
p_theta(o_t, r_t, d_t | h_t, z_t).
```

Training often resembles a sequential variational objective,

```text
E_q sum_t [
  log p_theta(o_t | h_t,z_t)
  + lambda_r log p_theta(r_t | h_t,z_t)
  + lambda_d log p_theta(d_t | h_t,z_t)
  - beta KL(q_theta(z_t|h_t,o_t) || p_theta(z_t|h_t))
].
```

The exact factorization, KL direction, balancing, and auxiliary losses differ by model. This expression is a generic map, not a reconstruction of any one implementation.

`Latent` means learned compression, not true state. A useful latent may be predictive, reconstructive, controllable, task-sufficient, or some mixture. MuZero demonstrates an intentionally abstract state optimized for reward, value, and policy prediction rather than observation reconstruction. [PLAN-MUZERO-2020]

## Assumptions and scope

Compression assumes that much of the observation is unnecessary for the intended query. The sufficiency criterion must therefore be named. A latent sufficient for one reward or policy can discard variables needed for a new task, causal diagnosis, or high-fidelity generation.

Posterior states have access to the current observation; imagined prior states do not. Good reconstruction under the posterior does not imply stable autonomous rollout. Likewise, a discrete tokenizer with low perceptual distortion need not preserve velocities, contact transitions, or action-relevant small objects.

## Representation families

| Family | State type | Strength | Main risk |
|---|---|---|---|
| Continuous deterministic | vector or feature map | simple and fast | hides multimodal uncertainty |
| Continuous stochastic | distributional latent | alternative hypotheses and regularization | posterior collapse or prior mismatch |
| Deterministic memory plus stochastic state | recurrent `h_t` and random `z_t` | separates long memory from local uncertainty | bypass paths can weaken stochastic state |
| Discrete latent/tokenizer | codebook indices | scalable sequence interfaces | codebook collapse and quantization loss |
| Locally structured latent | linear or constrained local transition | planning-friendly inductive bias | invalid outside local regions |
| Task-oriented abstract state | reward/value/policy sufficient | efficient search and control | narrow transfer surface |

E2C imposed locally linear latent dynamics for control from images. VQ-VAE established learned discrete codes. World Models and PlaNet combined learned compact dynamics with policy or planning, while Dreamer systems trained behavior through imagined latent trajectories. [FND-E2C-2015; REP-VQVAE-2017; FND-WORLD-MODELS-2018; FD-PLANET-2019; MBRL-DREAMERV3-2025]

## Design implications and trade-offs

Important levers include latent dimensionality and topology, continuous versus discrete state, codebook size, temporal stride, reconstruction target, KL or rate weight, free-bits or balancing rules, overshooting horizon, and relative weights of reward, termination, value, and observation heads.

More rate can preserve detail but increases transition complexity and imagination cost. Strong compression can improve abstraction while erasing control-critical evidence. A powerful decoder may reconstruct plausible observations without requiring the latent to encode exact dynamics. Task heads encourage relevant information but can overfit the current reward definition. Prior-posterior alignment improves rollout robustness but may reduce information from new observations if forced too strongly.

## Evaluation and falsification

- Report posterior reconstruction and prior-only rollout separately.
- Measure prediction and task performance across latent rate, capacity, and tokenizer resolution.
- Probe action, velocity, contact, identity, reward, and termination information, including held-out tasks.
- Track KL usage, active dimensions, codebook occupancy, perplexity, and posterior-prior divergence.
- Compare equal-compute latent and observation-space models rather than treating compression as a free gain.
- Search for model exploitation by planning in latent space and replaying actions independently.

A claim that the latent is Markov is weakened when longer raw history improves future prediction after conditioning on it. A claim that it is task-sufficient is falsified by downstream errors caused by distinctions absent from the latent. A calibrated-state claim requires proper uncertainty tests, not merely stochastic sampling.

## Failure modes

- **Posterior collapse:** the stochastic state is ignored by a strong decoder or recurrent path.
- **Codebook collapse:** only a small portion of discrete codes is used.
- **Prior-posterior gap:** training states differ from imagination states.
- **Control-detail erasure:** small objects, contact, or proprioceptive variables disappear under compression.
- **Good reconstruction, poor dynamics:** decoder quality masks transition error.
- **Task overcompression:** current reward prediction improves while transfer-relevant state is lost.
- **Latent exploitation:** a planner discovers unrealizable high-value latent trajectories.
- **Semantic instability:** latent codes change meaning across time, domains, or model versions.

## Cross-part instantiations

- [Cosmos3-Nano architecture](../../models/cosmos3-nano/architecture.md) owns its actual tokenizers and latent pathways; generic RSSM assumptions should not be projected onto it.
- [Generator](../../models/cosmos3-nano/generator.md) and [training](../../models/cosmos3-nano/training.md) specify model-specific latent targets and losses.
- [Action modeling](../../models/cosmos3-nano/action-modeling.md) identifies which latent or decoded outputs are conditioned on actions.
- [DreamerV3](../../papers/dreamerv3/paper.md) instantiates an RSSM with categorical latents and imagination actor-critic; the public repository is a DreamerV2-based reimplementation, not Google internal code.
- [TD-MPC2](../../papers/td-mpc2/paper.md) instantiates decoder-free latent dynamics with MPPI planning; latest public commits include post-paper Q-ensemble initialization fixes.
- [Optimization playbook](../../models/cosmos3-nano/optimization-playbook.md) can use rate, objective balance, and rollout diagnostics as testable hypotheses rather than universal prescriptions.

## Sources

- [FND-E2C-2015] Watter et al., *Embed to Control: A Locally Linear Latent Dynamics Model for Control from Raw Images*, NeurIPS 2015, arXiv:1506.07365.
- [REP-VQVAE-2017] van den Oord, Vinyals, and Kavukcuoglu, *Neural Discrete Representation Learning*, NeurIPS 2017, arXiv:1711.00937.
- [FND-WORLD-MODELS-2018] Ha and Schmidhuber, *Recurrent World Models Facilitate Policy Evolution*, NeurIPS 2018, arXiv:1809.01999.
- [FD-PLANET-2019] Hafner et al., *Learning Latent Dynamics for Planning from Pixels*, ICML 2019, PMLR 97.
- [PLAN-MUZERO-2020] Schrittwieser et al., *Mastering Atari, Go, Chess and Shogi by Planning with a Learned Model*, Nature, 2020, DOI:10.1038/s41586-020-03051-4.
- [MBRL-DREAMERV3-2025] Hafner et al., *Mastering Diverse Control Tasks through World Models*, Nature, 2025, DOI:10.1038/s41586-025-08744-2.
