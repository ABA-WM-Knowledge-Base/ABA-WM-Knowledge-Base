---
id: world-model-kb.papers.td-mpc2.paper
title: TD-MPC2 Method, Architecture, and Experimental Evidence
kind: paper
status: maintained
last_updated: 2026-08-14
owners:
  - AIBuildAI world-model group
---

# TD-MPC2 Method, Architecture, and Experimental Evidence

## Retrieval metadata

**Relevant queries:** TD-MPC2 architecture, decoder-free latent dynamics, SimNorm, discrete log-space regression, Q ensemble, MPPI horizon H=3, 104 tasks one hparam, MT80 317M, 545M transitions, few-shot 19M, visual RL 64x64, or exploding gradients.

**Knowledge provided:** the paper's control problem, complete encode-plan-update architecture, shared hyperparameter contract, scale and domain experiments, ablations with numbers, and the limits of each claim.

**Related pages:** [Model-based RL](../../foundations/decision-making/model-based-rl.md) owns the generic loop; [planning and control](../../foundations/decision-making/planning-and-control.md) owns search versus policy; [latent world models](../../foundations/representations/latent-world-model.md) owns decoder-free representation; [actions and interventions](../../foundations/problem-formulation/actions-and-interventions.md) owns action contracts; [evaluation methodology](../../foundations/data-and-evaluation/evaluation-methodology.md) owns evidence-layer distinctions.

Foundation bibliographic identity: [MBRL-TDMPC2-2024].

## 1. Problem statement

### 1.1 Prediction and control task

TD-MPC2 is a model-based reinforcement learning agent, not a pixel generator. Given an observation, it encodes a latent state, plans a short action sequence by simulating latent dynamics, and executes the first action:

```text
z_t = h(o_t)
z_{t+k+1} = d(z_{t+k}, a_{t+k})
r_{t+k} = R(z_{t+k}, a_{t+k})
a_t = argmax_{a_{t:t+H-1}}  sum_{k=0}^{H-1} gamma^k r_{t+k} + gamma^H Q(z_{t+H}, a_{t+H})
```

The world model outputs latent transitions, scalar rewards, and state-action values. It does not reconstruct observations, generate video, or emit a safety certificate. Planning is local trajectory optimization (MPPI) in latent space; a learned policy prior only proposes samples. [TDMPC2-PAPER, Sec. 3; MBRL-TDMPC2-2024]

### 1.2 Design problem

Continuous-control benchmarks mix locomotion, manipulation, and muscle actuation with incompatible observation widths, action dimensions, reward scales, and episode lengths. Prior MBRL methods often require **per-task hyperparameter grids** and become unstable when a decoder is trained jointly with value learning. Original TD-MPC exhibited **exploding gradients**. TD-MPC2 asks whether one decoder-free recipe, with simplicial latent normalization and discrete reward/value regression, can cover **104 tasks** and a **317M-parameter** agent on **80 tasks**. [TDMPC2-PAPER, Sec. 1-3, Table 8]

The principal hypothesis is that a compact implicit latent is sufficient for control if (i) the latent is constrained (SimNorm), (ii) reward and value are treated as discrete log-space regression rather than unbounded MSE, and (iii) an ensemble of Q-functions scores short-horizon plans. Pixel reconstruction is treated as a distractor, not a prerequisite. [TDMPC2-PAPER, Sec. 3; MBRL-TDMPC2-2024]

## 2. Method and architecture

### 2.1 End-to-end data flow

```text
environment observation o_t  (state vector or 64x64 RGB)
              |
        encoder h  (+ task embedding if multitask)
              |
         latent z_t   SimNorm V=8, tau=1
              |
   +---------- MPPI / CEM-style planning (H=3) -----------+
   |  24 policy-prior trajectories                         |
   |  512-24 Gaussian samples around shifted mean          |
   |  latent rollout: z' = d(z, a), r = R(z, a)            |
   |  terminal Q from 5-Q ensemble (8-Q at 317M)           |
   |  64 elites; 6 iterations (+2 if |A| >= 20)            |
   |  execute first action a_t in [-1, 1]                  |
   +-------------------------------------------------------+
              |
        environment o_{t+1}, r_t
              |
   replay buffer -> latent consistency + discrete reward/value TD
              |
        policy prior pi(z) updated to maximize scaled Q
```

At inference the agent plans in latent space every step. At training it interleaves environment interaction (single-task online) or offline replay (multitask) with gradient updates. This data flow is the paper-described architecture; [`codebase.md`](codebase.md) owns the released call graph and the post-paper Q-ensemble init fix. [TDMPC2-PAPER, Sec. 3, Fig. 2, Table 8; TDMPC2-CODE]

### 2.2 Decoder-free latent world model

Each observation is encoded independently. There is no observation decoder and no reconstruction loss:

```text
z = h(o)                         # SimNorm on the encoder output
z' = d(z, a)                     # MLP, SimNorm on the dynamics output
R_logits = R(z, a)               # 101 bins
Q_logits_i = Q_i(z, a)           # ensemble, 101 bins each
```

The implicit latent is trained to be **value-aware**: it must support reward prediction, TD backups, and short-horizon search. Details that do not affect those heads can be discarded. That is a control feature and a monitoring limitation. [TDMPC2-PAPER, Sec. 3; MBRL-TDMPC2-2024]

For the **5M** default architecture the paper reports parameter counts that make the critic dominate capacity: [TDMPC2-PAPER, Appendix / architecture tables]

| Module | Parameters |
|---|---:|
| Encoder | 167,936 |
| Dynamics | 843,264 |
| Q ensemble | 3,156,985 |
| Total (approx.) | ~5.39M |

The **317M** multitask agent widens the encoder and MLPs and increases the critic count: encoder dim **4096**, MLP dim **4096**, latent dim **1376**, **5** encoder layers, **8** Q-functions. [TDMPC2-PAPER, Table 9]

### 2.3 SimNorm

Latent vectors are partitioned into groups of `V=8` dimensions and passed through a softmax with temperature `tau=1`:

```text
z ~ R^{D}
z' = softmax( reshape(z, [..., D/V, V]) / tau )
```

Simplicial normalization bounds each group to the probability simplex. The paper presents this as essential for training stability at scale; original TD-MPC without it suffered exploding gradients when the latent was unconstrained. [TDMPC2-PAPER, Sec. 3, Table 8]

### 2.4 Discrete log-space regression

Rewards and Q-values are not trained with scalar MSE. Each head predicts a categorical distribution over **101** bins spanning `[vmin, vmax] = [-10, +10]` in a two-hot / soft cross-entropy scheme. Decoding uses a log-space expectation (`two_hot_inv` in the released code). The paper treats this as a second stabilizer: unbounded regression on heterogeneous reward scales is a source of gradient explosions. [TDMPC2-PAPER, Sec. 3, Table 8; TDMPC2-CODE, `common/world_model.py`, `tdmpc2.py`]

Conceptually:

```text
L_reward = soft_ce(R_logits(z, a), two_hot(r))
L_value  = soft_ce(Q_logits(z, a), two_hot(td_target))
td_target = r + gamma * (1 - terminated) * Q_target(z', pi(z'))
```

Q targets use the **minimum of two randomly subsampled** ensemble members (`return_type='min'`). Planning scores use the **average** of two subsampled members (`return_type='avg'`). [TDMPC2-CODE, `WorldModel.Q`; TDMPC2-PAPER, Sec. 3]

### 2.5 Planning (MPPI)

Default planning hyperparameters are shared across the 104-task sweep: [TDMPC2-PAPER, Table 8]

| Quantity | Value |
|---|---|
| Horizon `H` | 3 |
| Planning iterations | 6; **+2 if action dim >= 20** |
| Population | 512 |
| Policy-prior trajectories | 24 |
| Elites | 64 |
| Q-functions (default / 317M) | 5 / 8 |
| Action box | `[-1, 1]` after squashing |

The first 24 of 512 trajectories are rolled out from the policy prior. Remaining samples are Gaussian around a temporally shifted mean from the previous step. Each candidate is scored by predicted discounted return plus a terminal Q. Softmax weights with temperature 0.5 update the sampling mean and standard deviation. The executed action is a Gumbel-softmax draw among elites at training time and the mean at eval. [TDMPC2-PAPER, Sec. 3, Table 8; TDMPC2-CODE, `TDMPC2._plan`]

### 2.6 Training objective

The world-model loss is a weighted sum of latent consistency, discrete reward, discrete value, and optional termination:

```text
L = 20 * L_cons + 0.1 * L_rew + 0.1 * L_val  (+ termination if episodic)
```

Consistency compares a latent rollout `d(z, a)` to the encoder of the next observation, with temporal discount `rho=0.5` along the horizon. The policy prior is updated separately to maximize a running-scaled Q plus a small entropy bonus. Encoder learning rate is `0.3 x` the main `3e-4` Adam rate. Gradient clip is 20. Soft target update uses `tau=0.01`. [TDMPC2-PAPER, Table 8; TDMPC2-CODE, `tdmpc2.py`, `config.yaml`]

Batch size is **256** for single-task online training and **1024** for multitask offline training. [TDMPC2-PAPER, Table 8]

### 2.7 Multitask conditioning

Task identity is a learned embedding concatenated into encoder, dynamics, reward, and Q inputs. Per-task action masks zero unused dimensions so one network can host mixed action widths. The largest reported agent is **317M parameters on 80 tasks**. [TDMPC2-PAPER, Sec. 3, Table 9; TDMPC2-CODE, `WorldModel.task_emb`]

## 3. Experimental setup

### 3.1 Task suites

| Suite | Role | Notes |
|---|---|---|
| DMControl | locomotion / manipulation, state and visual | 30 of the 80-task mix, including **11 custom** tasks |
| Meta-World | 50 manipulation tasks in the 80-task mix | success-rate scoring in MT80 aggregates |
| ManiSkill2 | visual / contact-rich manipulation | included in the 104-task single-hparam sweep |
| MyoSuite | musculoskeletal control | included in the 104-task single-hparam sweep |

The **104-task** claim is a **single hyperparameter set** across all four domains. The **80-task** multitask agent is **50 Meta-World + 30 DMControl (including 11 custom)**. These two experiments must not be merged: 104 is online specialists with one yaml; 80 is one agent trained offline on specialist replay. [TDMPC2-PAPER, Sec. 4, Tables 1 and 8; MBRL-TDMPC2-2024]

### 3.2 Multitask data

The 80-task models are trained on **545M transitions** collected from **240 single-task agents**. This is an offline multitask regime, not online interaction of the 317M agent with 80 simulators simultaneously. RAM for that dataset is reported as **128 GB**; a single-task buffer fits in **12 GB**. Training the 317M model is reported to need a **24 GB** GPU. [TDMPC2-PAPER, Sec. 4, Table 1, compute appendix]

### 3.3 Metrics and baselines

DMControl uses episode return (often normalized by 10 in the released MT80 aggregator). Meta-World uses success rate. The paper compares against model-free and model-based families including SAC-style methods, DreamerV3, and DrQ-v2 on the visual subset. Visual RL uses a **conv encoder on 64x64** frames with **random shift** augmentation and is reported as comparable to DrQ-v2 and DreamerV3 on **10 DMC visual tasks**. [TDMPC2-PAPER, Sec. 4]

## 4. Results

### 4.1 One hyperparameter set on 104 tasks

A single configuration (Table 8) is used for online training across 104 tasks spanning the four domains. The supported claim is **competitive performance without per-task tuning**, not optimality versus a tuned specialist on every task. Discrete action spaces are explicitly left **open**. [TDMPC2-PAPER, Abstract, Sec. 4, Table 8]

### 4.2 Model scaling on the 80-task agent

Normalized score versus parameter count and GPU-days for the 80-task multitask setting: [TDMPC2-PAPER, Table 1]

| Model size | GPU-days | MT80 score |
|---|---:|---:|
| 1M | 3.7 | 16.0 |
| 5M | 4.2 | 49.5 |
| 19M | 5.3 | 57.1 |
| 48M | 12 | 68.0 |
| 317M | 33 | 70.6 |

Score rises steeply from 1M to 48M and only marginally from 48M (68.0) to 317M (70.6) despite nearly 3x GPU-days (12 to 33). Capacity helps, but 48M already captures most of the reported multitask return. [TDMPC2-PAPER, Table 1]

### 4.3 Few-shot transfer

A **19M** agent trained on **70** tasks is finetuned on **10 held-out** tasks. At **20k** environment steps the finetuned agent is reported at **2x** the performance of training from scratch on those tasks. This is few-shot adaptation of a latent world model, not a claim that 20k steps suffice from a random encoder. [TDMPC2-PAPER, Sec. 4]

### 4.4 Visual RL

Replacing the state encoder with a four-layer conv stack on **64x64** RGB plus **random shift** yields results comparable to DrQ-v2 and DreamerV3 on **10 DMControl visual tasks**. The visual path remains decoder-free: pixels are encoded, never reconstructed. [TDMPC2-PAPER, Sec. 4; TDMPC2-CODE, `common/layers.py` `conv`, `ShiftAug`]

## 5. Ablations

The paper's stability narrative is empirical, not only architectural:

| Ablation / observation | Reported effect | Locator |
|---|---|---|
| SimNorm removed | training instability; original TD-MPC exploding gradients | [TDMPC2-PAPER, Sec. 3, Table 8] |
| Continuous (MSE) reward/value instead of 101-bin log-space | less robust across reward scales | [TDMPC2-PAPER, Sec. 3, Table 8] |
| Decoder added | not used in the main recipe; reconstruction is treated as unnecessary for control | [TDMPC2-PAPER, Sec. 3] |
| Planning disabled (`mpc: false`) | policy prior only; planning is the inference-time search | [TDMPC2-PAPER, Sec. 3; TDMPC2-CODE, `TDMPC2.act`] |
| Extra planning iterations when `\|A\| >= 20` | heuristic for high-dimensional action | [TDMPC2-PAPER, Table 8] |
| Model size 1M vs 48M vs 317M on MT80 | 16.0 vs 68.0 vs 70.6 | [TDMPC2-PAPER, Table 1] |

SimNorm is described as **essential for stability**. Decoder-free training is a deliberate capacity allocation toward Q and dynamics rather than pixels. [TDMPC2-PAPER, Sec. 3-4]

## 6. Limits and evidence boundaries

- **Simulators only.** The 104-task and 80-task numbers are simulated continuous control. Real-robot transfer is not established. [TDMPC2-PAPER, Sec. 4-5]
- **Decoder-free latents** can drop visually salient but reward-irrelevant detail. They are the wrong interface for a pixel Generator or for human video inspection. [TDMPC2-PAPER, Sec. 3]
- **104-task one-hparam** does not imply that a specialist yaml cannot beat the shared recipe on a single task. [TDMPC2-PAPER, Abstract, Sec. 4]
- **317M vs 48M** is a small score gap (70.6 vs 68.0) at large extra compute (33 vs 12 GPU-days). Do not treat 317M as a required scale for transfer. [TDMPC2-PAPER, Table 1]
- **545M transitions from 240 specialists** are a data privilege. Multitask scores are not evidence that a randomly initialized 317M agent can learn 80 tasks online from scratch. [TDMPC2-PAPER, Sec. 4]
- **Discrete actions remain open.** The recipe assumes continuous, squashed actions in `[-1, 1]`. [TDMPC2-PAPER, Sec. 5]
- **Memory:** 12 GB RAM single-task, 128 GB for the 80-task dataset, 24 GB GPU for 317M training. These are paper-reported envelopes, not a local execution record. [TDMPC2-PAPER, compute notes]
- **Post-paper Q-ensemble init** in the pinned repository is maintenance, not ICLR evidence. [`codebase.md`](codebase.md); [TDMPC2-CODE]
- **Planning wall-clock** grows with population, horizon, and Q count. Comparisons that ignore search cost are incomplete.

These limits narrow the evidence; they do not negate the 104-task or MT80 tables. [`reproduction.md`](reproduction.md) owns executed-state claims.

## Sources

- [TDMPC2-PAPER] *TD-MPC2: Scalable, Robust World Models for Continuous Control*, arXiv:2310.16828 / ICLR 2024.
- [TDMPC2-CODE] `nicklashansen/tdmpc2` at the pinned commit.
- [MBRL-TDMPC2-2024] Foundation bibliographic identity (not re-registered in this entry's `sources.yaml`).
