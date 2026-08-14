---
id: world-model-kb.foundations.decision-making.model-based-rl
title: Model-Based Reinforcement Learning
kind: reference
status: maintained
last_updated: 2026-08-14
owners:
  - AIBuildAI world-model group
---

# Model-Based Reinforcement Learning

## Retrieval metadata

**Relevant queries:** model-based reinforcement learning, MBRL, Dyna, imagination, synthetic rollout, value-aware model, latent actor-critic, model bias, sample efficiency, or world-model policy learning.

**Knowledge provided:** the MBRL problem decomposition, model-use taxonomy, objective and rollout variables, and evidence boundaries connecting predictive fit to policy performance.

**Related pages:** [Planning and control](planning-and-control.md) covers online action selection; [forward dynamics](../problem-formulation/forward-dynamics.md) covers transition learning; [evaluation methodology](../data-and-evaluation/evaluation-methodology.md) covers comparison and statistical evidence.

## Definition and formalism

Model-based reinforcement learning estimates or uses a model of an environment to improve decisions. For an unknown MDP

```text
M = (S, A, P*, r*, gamma),
```

experience `D = {(s,a,r,s')}` supports estimates `P_hat` and `r_hat`. A planner or learning algorithm then derives a policy using real experience, simulated experience from the model, or both. Generic model learning can be written as

```text
P_hat, r_hat = LearnModel(D)
pi = ImprovePolicy(D, Rollouts(P_hat, r_hat), Planner).
```

The model can predict observations, latent states, rewards, continuation, values, policies, or another decision-relevant representation. Full observation reconstruction is therefore one design choice, not a definition of MBRL. MuZero learns reward, policy, and value predictions used in search; TD-MPC2 learns implicit decoder-free latent dynamics; Dreamer learns a recurrent state model and improves actor/critic networks from imagined trajectories. [PLAN-MUZERO-2020; MBRL-TDMPC2-2024; MBRL-DREAMER-2020; MBRL-DREAMERV3-2025]

## Assumptions and scope

MBRL separates two errors that can move independently:

1. **Model-estimation error:** the learned model differs from environment transitions or decision-relevant outcomes.
2. **Model-use error:** planning or policy optimization amplifies those differences by visiting unsupported states or exploiting optimistic predictions.

Maximum-likelihood prediction is not always aligned with decision quality. Value-Aware Model Learning formalizes a loss that weights model error through value-function structure, demonstrating one approach to task-relevant model estimation. This supports the narrower claim that decision-aware loss can be preferable under model approximation error in the analyzed setting, not that likelihood is generally unnecessary. [MBRL-VAML-2017]

MBRL is distinct from generic video pretraining and supervised policy learning. A pretrained video generator becomes part of an MBRL system only when a decision process supplies task objectives and uses the model to plan, improve a policy, estimate value, or generate learning experience. A behavior-cloning policy that never models or uses consequences is model-free with respect to this definition even when initialized from a large multimodal model.

## Mechanism families

| Family | Model use | Representative evidence | Central trade-off |
|---|---|---|---|
| Dyna | model-generated transitions supplement direct experience updates | Sutton integrates learning, planning, and reacting | more updates versus model bias |
| Online model-predictive control | optimize actions through a model at decision time | PETS and PlaNet | feedback and flexibility versus inference cost |
| Branched synthetic rollouts | start short model rollouts from real replay states | MBPO | sample augmentation versus rollout drift |
| Latent imagination actor-critic | train policy and value on compact imagined trajectories | Dreamer family | fast parallel imagination versus latent-model bias |
| Search with value-equivalent model | learned reward/value/policy dynamics guide tree search | MuZero | task relevance versus omitted world detail |
| Local latent trajectory optimization | optimize action sequences in implicit task-oriented model | TD-MPC2 | efficient control versus local search and task dependence |
| Uncertainty-aware MBRL | propagate model distributions or disagreement into decisions | PETS | risk awareness versus calibration and ensemble cost |

MBPO explicitly analyzes the trade-off between cheap model data and model bias and reports that short rollouts branched from real data work well in its evaluated continuous-control setting. Its rollout length is not a domain-independent constant. PETS reports probabilistic ensembles and trajectory sampling; DreamerV3 reports one fixed configuration across more than 150 tasks in its study. Each conclusion remains bound to its model, tasks, data, and protocol. [MBRL-MBPO-2019; MBRL-PETS-2018; MBRL-DREAMERV3-2025]

## Design implications and trade-offs

| Lever | Mechanistic effect | Expected signal | Main risk | Discriminating comparison |
|---|---|---|---|---|
| Model rollout horizon | changes synthetic-data volume and distance from real states | longer credit or more policy updates | compounding bias | real return and model error versus horizon |
| Real:model replay ratio | anchors policy learning to observed support | stability and sample efficiency | too little model use or excessive bias | fixed updates with mixture ablation |
| Model objective | selects likelihood, reconstruction, reward, value, or task-relevant information | better decision representation | over-specialization to current reward | predictive and transfer utility matrix |
| Uncertainty estimator | modifies exploration or pessimism | lower exploitation and safer coverage | miscalibration or conservatism | error-disagreement calibration and return |
| Policy/model update ratio | allocates compute between estimation and improvement | faster learning | stale model or overfit policy | equal environment data and total compute |
| Imagination start states | controls support of synthetic rollouts | realistic local coverage | replay bias and missed novel states | starts from real, model, and mixed states |
| Reward/continuation model | carries task objective and episode semantics | longer-horizon value accuracy | reward hacking or termination error | component ablation and realized return |
| Model capacity and scale | changes representation and fit | lower error or broader multitask transfer | compute confounding and optimization instability | scaling curves at fixed data and training budget |
| Offline support constraint | discourages unsupported actions without new interaction | safer offline improvement | overly conservative policy | OOD action slices and real evaluator |

These variables interact. For example, increasing rollout horizon while also improving uncertainty and changing the real:model ratio cannot attribute a gain to horizon alone. Reported robustness techniques from DreamerV3—normalization, balancing, and transformations—are established components of that algorithm; their benefit for a different model remains an experimental hypothesis. [MBRL-DREAMERV3-2025]

## Evaluation and falsification

An MBRL result carries at least six measurement surfaces:

- model error and calibration on on-policy and shifted data;
- environment interactions needed to reach declared performance;
- final real-environment return or task success;
- compute, wall-clock time, model updates, and planning evaluations;
- variance across seeds, tasks, and initial states;
- robustness to rollout horizon, model size, data support, and reward delay.

Sample efficiency means performance as a function of real environment interaction, not merely training updates. Compute efficiency is a separate claim. A model-based method can use fewer transitions while consuming more accelerator time through training and imagination.

A model-improvement hypothesis is falsified when predictive fit rises but realized return, candidate ranking, or policy learning does not improve under fixed downstream use. A policy-improvement hypothesis is narrowed when gains disappear under equal model-rollout count, optimizer updates, planning budget, or seeds. Results produced only in the learned model do not establish performance in the true environment.

## Failure modes

- **Model bias accumulation:** synthetic rollouts diverge from true dynamics as horizon increases.
- **Policy exploitation:** policy optimization finds actions that trigger optimistic model errors.
- **Distribution mismatch:** the optimized policy visits states not represented in model data.
- **Reward-model error:** imagined reward is easier to exploit than transition error is to detect.
- **Termination error:** incorrect continuation produces inflated or truncated returns.
- **Representation omission:** task-critical state is absent because reconstruction or prior tasks did not require it.
- **Uncertainty miscalibration:** the model is confident outside support or uncertain in familiar regimes.
- **Joint-training instability:** model, value, and policy targets move together and create feedback loops.
- **Compute masking:** extra model updates, samples, or search make an algorithm appear more data-efficient without being resource-efficient.
- **Benchmark overreach:** success on a finite task set is interpreted as a general world model or robot policy.

## Cross-part instantiations

- [Cosmos3-Nano action modeling](../../models/cosmos3-nano/action-modeling.md) provides action-conditioned prediction surfaces that could be studied as learned models, but the base checkpoint does not itself define an RL reward or policy-improvement loop.
- [Cosmos3-Nano Generator](../../models/cosmos3-nano/generator.md) can supply generated futures; their use as MBRL experience requires independent calibration and task semantics.
- [Cosmos3-Nano Policy-DROID](../../models/cosmos3-nano/policy.md) is supervised/post-trained policy evidence, not automatically evidence of MBRL.
- [Cosmos3-Nano data](../../models/cosmos3-nano/data.md), [training](../../models/cosmos3-nano/training.md), and [evaluation](../../models/cosmos3-nano/evaluation.md) expose model-specific variables and reported results.
- [DreamerV3](../../papers/dreamerv3/paper.md) instantiates imagination-based actor-critic with a compact RSSM under a fixed hyperparameter set; Nature and arXiv titles must not be collapsed.
- [TD-MPC2](../../papers/td-mpc2/paper.md) instantiates TD-trained latent models with MPPI; 104-task single-hyperparameter claims remain bound to the ICLR 2024 protocol.
- [DIAMOND](../../papers/diamond/paper.md) instantiates agent training inside an image-space diffusion world model on Atari 100k.
- [Paper entries](../../papers/README.md) can preserve Dyna, VAML, PETS, MBPO, PlaNet, Dreamer, MuZero, and TD-MPC2 algorithm details and experiments.

## Sources

- [MBRL-DYNA-1990] Sutton, *Integrated Modeling and Control Based on Reinforcement Learning and Dynamic Programming*, NeurIPS 1990.
- [MBRL-VAML-2017] Farahmand, Barreto, and Nikovski, *Value-Aware Loss Function for Model-Based Reinforcement Learning*, AISTATS 2017, PMLR 54:1486-1494.
- [MBRL-PETS-2018] Chua et al., *Deep Reinforcement Learning in a Handful of Trials using Probabilistic Dynamics Models*, NeurIPS 2018.
- [FD-PLANET-2019] Hafner et al., *Learning Latent Dynamics for Planning from Pixels*, ICML 2019.
- [MBRL-MBPO-2019] Janner et al., *When to Trust Your Model: Model-Based Policy Optimization*, NeurIPS 2019.
- [MBRL-DREAMER-2020] Hafner et al., *Dream to Control: Learning Behaviors by Latent Imagination*, ICLR 2020.
- [PLAN-MUZERO-2020] Schrittwieser et al., *Mastering Atari, Go, Chess and Shogi by Planning with a Learned Model*, Nature 588, DOI:10.1038/s41586-020-03051-4.
- [MBRL-TDMPC2-2024] Hansen, Su, and Wang, *TD-MPC2: Scalable, Robust World Models for Continuous Control*, ICLR 2024.
- [MBRL-DREAMERV3-2025] Hafner et al., *Mastering Diverse Control Tasks through World Models*, Nature 640:647-653, DOI:10.1038/s41586-025-08744-2.
