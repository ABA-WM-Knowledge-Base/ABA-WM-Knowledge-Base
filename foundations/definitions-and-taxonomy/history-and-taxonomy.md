---
id: world-model-kb.foundations.definitions-and-taxonomy.history-and-taxonomy
title: History and Taxonomy of World Models
kind: concept
status: maintained
last_updated: 2026-08-11
owners:
  - AIBuildAI world-model group
---

# History and Taxonomy of World Models

## Retrieval metadata

**Relevant queries:** world model history, taxonomy, environment model lineage, model-based reinforcement learning, video world model, foundation world model, or contested world-model terminology.

**Knowledge provided:** a non-exclusive historical map, an orthogonal classification tuple, and terminology boundaries that prevent architecture, objective, representation, and use from being collapsed into one label.

**Related pages:** [World models](world-model.md) owns the operational definition; [problem formulation](../problem-formulation/problem-formulation.md) owns process notation; the [representations](../representations/README.md) and [learning objectives](../learning-objectives/README.md) indexes own their respective axes.

## Definition and formalism

World-model research is a convergence of several lineages rather than a single sequence of replacements. A useful classification describes a model by an orthogonal tuple:

```text
tau(M) = (
  domain,
  representation,
  conditioning/intervention,
  stochasticity,
  predicted heads,
  horizon,
  learning objective,
  downstream use
).
```

For example, `latent`, `diffusion`, and `planner` are not competing answers to the same question: they specify a representation, an objective or sampler, and a use. A model may be latent, action-conditioned, stochastic, flow-trained, and used as a policy auxiliary at the same time.

## Assumptions and scope

The timeline below identifies durable ideas, not exclusive origins:

| Period | Lineage and contribution |
|---|---|
| 1960s | Kalman filtering formalized recursive estimation for linear-Gaussian systems; partially observed control separated hidden state from observations and introduced sufficient information states. [FND-KALMAN-1960; FND-ASTROM-1965] |
| 1990s | Dyna integrated learning a model, planning with it, and direct acting; POMDP work consolidated belief-state planning under partial observability. [MBRL-DYNA-1990; CTRL-POMDP-1998] |
| 2010s | Deep action-conditioned video prediction learned transitions directly from pixels; variational and recurrent latent dynamics enabled compact imagined rollouts. [FND-OH-VIDEO-2015; FND-E2C-2015; FND-WORLD-MODELS-2018; FD-PLANET-2019] |
| 2020s | Task-oriented models such as MuZero showed that useful learned dynamics need not reconstruct observations; large token, diffusion, and flow models expanded scale, modality, horizon, and generative coverage. [PLAN-MUZERO-2020; WFM-GENIE-2024; C3-TR] |

This history should not be read as a claim that modern generative video models subsume control theory, or that a high-capacity simulator is always preferable to a compact task model. Each lineage preserves different assumptions and evaluation standards.

## Taxonomy families

| Axis | Representative values | Question answered |
|---|---|---|
| Domain | physical process, game, robot, driving, open-world video | What environment is modeled? |
| Representation | explicit state, pixels, latent tokens, objects/graphs, 3D fields | What variables carry predictive information? |
| Conditioning | passive context, action, language, goal, camera, proprioception | What can change or constrain the prediction? |
| Stochasticity | deterministic, categorical, latent-variable, diffusion/flow | How are alternative futures represented? |
| Predicted heads | state, observation, reward, termination, value, action | What interface does the model expose? |
| Horizon | one-step, fixed rollout, variable horizon, persistent simulation | Over what temporal range is it intended to be valid? |
| Objective | likelihood, reconstruction, contrastive/feature prediction, control loss | What statistical behavior is optimized? |
| Use | forecasting, generation, representation learning, planning, policy | How is the learned surface consumed? |

The labels `video world model`, `latent world model`, `object-centric world model`, `world foundation model`, and `world action model` name different combinations of these axes. They are not a partition.

## Design implications and trade-offs

Taxonomy improves experiment interpretation by locating the changed axis. Replacing a pixel decoder with a latent predictor tests representation and target choice; replacing autoregressive likelihood with flow matching tests the conditional distribution and sampler; adding action conditioning changes the causal query surface; adding a policy head changes the product interface and often the data distribution.

Historical comparisons require matched claims. Classical filters can be calibrated under narrow assumptions but do not provide open-world perceptual generation. Large video models cover broader appearances but may lack explicit uncertainty, reward, or action semantics. Task-oriented abstractions can outperform reconstructive models for a fixed objective while becoming brittle when the task changes.

## Evaluation and falsification

A taxonomy is useful if two systems placed in the same cell expose comparable conditionals, outputs, and use. It fails when labels conceal critical differences such as action-free versus action-conditioned prediction, open-loop generation versus closed-loop policy execution, or reconstructed pixels versus reward/value heads.

For historical performance claims, verify that environment, data scale, horizon, observation/action contract, compute, and evaluation use are comparable. A newer model's superior visual metric does not falsify a classical estimator's state-calibration result; a better control score does not establish a more complete visual simulator.

## Failure modes

- **Single-lineage narrative:** presenting control, reinforcement learning, and video generation as one linear progression.
- **Axis collapse:** treating `latent`, `diffusion`, `world action model`, and `planner` as mutually exclusive architectures.
- **Brand-defined ontology:** allowing one paper's product term to become the category definition.
- **Scale substitution:** inferring causal or control competence from parameter count or dataset size.
- **Temporal ambiguity:** using `4D`, `long horizon`, or `persistent` without an operational duration and metric.
- **Version leakage:** assigning capabilities of a post-trained policy checkpoint to a base generative model.

## Contested terminology

- **World model:** ranges from any learned environment transition to broad generative knowledge of the physical world.
- **Environment model / dynamics model:** sometimes includes rewards and observations; sometimes means only state transition.
- **Video world model:** may mean passive video prediction or an action-conditioned simulator.
- **World foundation model:** implies broad reuse and scale, but no universal capability or transfer threshold exists.
- **World action model:** an emerging label for models that jointly model action and future; factorization and deployment semantics differ across papers.
- **4D world model:** usually means 3D structure over time, not four spatial dimensions; representation persistence varies.

## Cross-part instantiations

- [Cosmos3-Nano architecture](../../models/cosmos3-nano/architecture.md) should be classified by its documented surfaces rather than a single umbrella label.
- [Generator](../../models/cosmos3-nano/generator.md), [Reasoner](../../models/cosmos3-nano/reasoner.md), [action modeling](../../models/cosmos3-nano/action-modeling.md), and [Policy-DROID](../../models/cosmos3-nano/policy.md) occupy distinct cells in the taxonomy.
- [Cosmos3-Nano limitations](../../models/cosmos3-nano/limitations.md) records boundaries that scale-oriented labels do not convey.
- [Paper entries](../../papers/README.md) preserve source-specific terminology and evaluation protocols.

## Sources

- [FND-KALMAN-1960] Kalman, *A New Approach to Linear Filtering and Prediction Problems*, Journal of Basic Engineering, 1960, DOI:10.1115/1.3662552.
- [FND-ASTROM-1965] Astrom, *Optimal Control of Markov Processes with Incomplete State Information*, Journal of Mathematical Analysis and Applications, 1965, DOI:10.1016/0022-247X(65)90154-X.
- [MBRL-DYNA-1990] Sutton, *Integrated Modeling and Control Based on Reinforcement Learning and Dynamic Programming*, NeurIPS 1990.
- [CTRL-POMDP-1998] Kaelbling, Littman, and Cassandra, *Planning and Acting in Partially Observable Stochastic Domains*, Artificial Intelligence, 1998, DOI:10.1016/S0004-3702(98)00023-X.
- [FND-OH-VIDEO-2015] Oh et al., *Action-Conditional Video Prediction using Deep Networks in Atari Games*, NeurIPS 2015.
- [FND-E2C-2015] Watter et al., *Embed to Control: A Locally Linear Latent Dynamics Model for Control from Raw Images*, NeurIPS 2015, arXiv:1506.07365.
- [FND-WORLD-MODELS-2018] Ha and Schmidhuber, *Recurrent World Models Facilitate Policy Evolution*, NeurIPS 2018, arXiv:1809.01999.
- [FD-PLANET-2019] Hafner et al., *Learning Latent Dynamics for Planning from Pixels*, ICML 2019, PMLR 97.
- [PLAN-MUZERO-2020] Schrittwieser et al., *Mastering Atari, Go, Chess and Shogi by Planning with a Learned Model*, Nature, 2020, DOI:10.1038/s41586-020-03051-4.
- [WFM-GENIE-2024] Bruce et al., *Genie: Generative Interactive Environments*, ICML 2024, arXiv:2402.15391.
- [C3-TR] NVIDIA, *Cosmos 3: Omnimodal World Models for Physical AI*, arXiv:2606.02800.
