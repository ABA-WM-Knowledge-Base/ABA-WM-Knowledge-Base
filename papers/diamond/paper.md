---
id: world-model-kb.papers.diamond.paper
title: DIAMOND Method, Architecture, and Experimental Evidence
kind: paper
status: maintained
last_updated: 2026-08-14
owners:
  - AIBuildAI world-model group
---

# DIAMOND Method, Architecture, and Experimental Evidence

## Retrieval metadata

**Relevant queries:** DIAMOND architecture, EDM world model, frame stacking, Adaptive Group Normalization, Atari 100k Table 1, mean HNS 1.459, IQM 0.641, 3 denoising steps, actor-critic imagination, IRIS comparison, or NeurIPS 2024 Spotlight.

**Knowledge provided:** the paper's problem, image-space EDM world model, actor-critic trained in imagination, Atari 100k tables bound to the `main` agent, ablations, and the CSGO/driving visual-quality appendix as a separate evidence surface.

**Related pages:** [`README.md`](README.md) owns identity boundaries; [`codebase.md`](codebase.md) owns the Atari `main` tree; [video world models](../../foundations/representations/video-world-model.md) owns pixel-space rollouts; [diffusion and flow matching](../../foundations/learning-objectives/diffusion-and-flow-matching.md) owns EDM; [model-based RL](../../foundations/decision-making/model-based-rl.md) owns imagination training; [evaluation methodology](../../foundations/data-and-evaluation/evaluation-methodology.md) owns HNS aggregation.

Foundation registry [REP-DIAMOND-2024](../../foundations/representations/video-world-model.md) owns the bibliographic identity. Do not duplicate that ID in [`sources.yaml`](sources.yaml).

## 1. Problem statement

### 1.1 Prediction and control task

DIAMOND (DIffusion As a Model Of eNvironment Dreams) is an RL agent whose policy is trained **entirely inside a diffusion world model**. The world model is an action-conditioned next-frame generator in image space. Real Atari interaction supplies world-model and reward/termination data; actor-critic updates consume imagined observations. Evaluation remains on the real environment. [DIASRC-PAPER, Abstract, Sec. 1]

The prediction interface is next-frame denoising given a short clean history and the executed action:

```text
x_{t+1}^0 ~ D_theta(x_{t+1}^tau | x_{t-L+1:t}^0, a_t)
```

`L=4` conditioning frames is the Atari architecture default. The model does not output a safety certificate, a tree-search plan, or a discrete latent codebook. [DIASRC-PAPER, Sec. 3, Table 2]

### 1.2 Design problem versus discrete-latent world models

IRIS, STORM, TWM, and DreamerV3 compress observations into discrete or compact latents. The paper's hypothesis is that **visual details matter**: small sprites (ball, enemy, score digits) that a tokenizer discards can change the optimal action. Diffusion in image space is proposed as a drop-in environment substitute that retains those details while remaining conditionable and multimodal. [DIASRC-PAPER, Sec. 1-2]

## 2. Method and architecture

### 2.1 End-to-end data flow

```text
real Atari env (100k interaction budget)
        |
  collector: (o_t, a_t, r_t, d_t, o_{t+1})
        |
  three concurrent learners
        |
  +-- Denoiser D_theta (EDM U-Net, frame-stack, AdaGN on action+sigma)
  |      imagines next RGB frame with 3 Euler steps
  +-- Reward/termination model R_psi (CNN + LSTM)
  +-- Actor-critic pi_phi, V_phi trained on imagined trajectories of horizon H=15
        |
  evaluate pi_phi on real Atari (sticky-action 100k protocol)
```

The reported Atari 100k agent is **not** a model-free DQN. Policy learning is actor-critic with lambda-returns inside `WorldModelEnv`. Setting `training.model_free: true` unplugs the world model and is a different recipe. [DIASRC-PAPER, Sec. 3, Appendix D-E; DIASRC-CODE-CURRENT, `config/trainer.yaml`]

### 2.2 EDM denoiser in image space

The world model follows EDM (Karras et al., 2022). Training samples log-noise from a Gaussian:

```text
log(sigma(tau)) ~ N(P_mean, P_std^2),   P_mean = -0.4, P_std = 1.2
```

The network `F_theta` predicts a mixture of clean image and noise. Adaptive mixing lets the model emit a usable clean-image estimate even when noise dominates, which is why 3 denoising steps suffice for Atari imagination. DDPM is analyzed as an alternative and rejected for long-horizon color drift. [DIASRC-PAPER, Sec. 3.1, 5.1-5.2, Eq. 13; Appendix K]

Conditioning:

- **observations:** concatenate the previous `L` clean frames with the noised next frame (frame stacking into a 2-D U-Net);
- **action and diffusion time:** Adaptive Group Normalization (AdaGN), not cross-attention, in the Atari agent. [DIASRC-PAPER, Table 2]

U-Net residual blocks use layers `[2,2,2,2]` and channels `[64,64,64,64]` with conditioning width 256. The full Atari agent is about 13M parameters. [DIASRC-PAPER, Tables 2, 4]

### 2.3 Reward, termination, and actor-critic

`R_psi` is a separate CNN+LSTM (channels `[32,32,32,32]`, LSTM 512) that predicts reward and episode termination from imagined frames. The actor-critic uses residual blocks `[1,1,1,1]` / channels `[32,32,64,64]` and LSTM 512. Imagination horizon `H=15`, discount `gamma=0.985`, lambda `0.95`, entropy weight `0.001`. [DIASRC-PAPER, Tables 2-3]

At each imagined step the denoiser produces the next frame (3 Euler steps, `sigma_min=2e-3`, `sigma_max=5.0` in the released config), the reward model scores it, and the actor samples an action. Gradients do not flow through the frozen denoiser into the policy in the standard loop; the policy treats the world model as an environment. [DIASRC-PAPER, Appendix E; DIASRC-CODE-CURRENT, `config/trainer.yaml`]

### 2.4 Training loop

Table 3 and Algorithm 1 specify 1000 epochs, 400 optimizer steps per learner per epoch, 100 real environment steps per epoch, batch 32, AdamW, learning rate `1e-4`. Collection uses epsilon-greedy `0.01`. Total real interaction is the Atari 100k budget (`collection.train.num_steps_total: 100000` in the released config). [DIASRC-PAPER, Table 3; DIASRC-CODE-CURRENT]

On an RTX 4090 the paper profiles 543 ms per combined update (88 denoiser + 115 reward/termination + 340 actor-critic), 217 s per epoch, and 2.9 days per game including collection. Imagination uses 15 steps times 3 denoising steps (4.2 ms each). [DIASRC-PAPER, Table 5]

## 3. Experimental setup

### 3.1 Atari 100k protocol

The quantitative agent is evaluated on the 26-game Atari 100k suite after about two hours of real-time experience. Scores in Table 1 are means over **5 seeds**. Human-normalized score (HNS) uses the standard random/human references printed in the table. Aggregation reports mean HNS and interquartile mean (IQM), with stratified bootstrap intervals in Figure 2. [DIASRC-PAPER, Table 1, Fig. 2, Sec. 4.2]

Sticky-action and preprocessing details bind to the released `config/env/atari.yaml` plus the paper protocol. Do not substitute Atari 200M DreamerV3 Nature numbers into this table.

### 3.2 World-model-only comparison class

Table 1 compares agents **trained entirely within a world model**: SimPLe, TWM, IRIS, DreamerV3 (Hafner et al. 2023 Atari 100k numbers as cited), STORM, and DIAMOND. Appendix J adds search-based and model-free methods (MuZero, EfficientZero, CURL, SPR, SR-SPR, BBF). BBF mean HNS `2.247` and EfficientZero `1.943` exceed DIAMOND; the paper treats MCTS and reset/hyperparameter schedules as orthogonal and not a matched world-model ablation. [DIASRC-PAPER, Table 1, Table 6]

### 3.3 CSGO and driving appendix (not Table 1)

Appendix M trains the **diffusion world model only** on static datasets: CS:GO Clean Dust II (190k frames at 16 Hz, 150k/40k split, 64x64) and comma.ai motorway driving (4.4 hours daylight, 10 Hz, 64x64). No RL is performed. Visual metrics in Table 8 therefore **must not** be cited as support for Atari mean HNS 1.46. The CSGO interactive demo lives on a **separate git branch**. [DIASRC-PAPER, Appendix M, Table 8; DIASRC-CODE-CSGO-BRANCH]

## 4. Trajectory and control results

### 4.1 Atari 100k Table 1 (canonical quantitative surface)

| Game | Human | IRIS | DreamerV3 | STORM | DIAMOND |
|---|---:|---:|---:|---:|---:|
| Asterix | 8503.3 | 853.6 | 932.0 | 1028.0 | **3698.5** |
| Boxing | 12.1 | 70.1 | 78.0 | 79.7 | **86.9** |
| Breakout | 30.5 | 83.7 | 31.0 | 15.9 | **132.5** |
| CrazyClimber | 35829.4 | 59324.2 | 97190.0 | 66776.0 | **99167.8** |
| Kangaroo | 3035.0 | 838.2 | 4098.0 | 4208.0 | **5382.2** |
| Krull | 2665.5 | 6616.4 | 7782.0 | 8412.6 | **8610.1** |
| Pong | 14.6 | 14.6 | 18.0 | 11.3 | **20.4** |
| RoadRunner | 7845.0 | 9614.6 | 15565.0 | 17564.0 | **20673.2** |
| BankHeist | 753.1 | 53.1 | 649.0 | 641.2 | 19.7 |
| BattleZone | 37187.5 | 13074.0 | 12250.0 | 13540.0 | 4702.0 |
| Superhuman count | N/A | 10 | 9 | 10 | **11** |
| Mean HNS | 1.000 | 1.046 | 1.097 | 1.266 | **1.459** |
| IQM | 1.000 | 0.501 | 0.497 | 0.636 | **0.641** |

Prose rounds mean HNS to **1.46** and IQM to **0.64**. Use `1.459` / `0.641` when reproducing Table 1. DIAMOND is superhuman on 11 games. Weak games include BankHeist (`19.7` versus STORM `641.2`) and BattleZone (`4702.0` versus STORM `13540.0`); the mean is not a uniform per-game win. [DIASRC-PAPER, Table 1, Sec. 4.2]

The paper attributes large gains on Asterix, Breakout, and Road Runner to retained sprite-level detail. That causal story is supported by qualitative rollouts plus the Table 1 deltas, not by a matched tokenizer-capacity ablation on those three games alone. [DIASRC-PAPER, Sec. 4.2, 5.3]

### 4.2 Compute comparison

| | IRIS | DreamerV3 | DIAMOND |
|---|---:|---:|---:|
| Parameters | 30M | 18M | **13M** |
| Training days | 4.1 | <1 | 2.9 |
| Mean HNS | 1.046 | 1.097 | **1.459** |

DIAMOND has the highest mean HNS in this world-model trio at the lowest parameter count, but it is slower than DreamerV3. [DIASRC-PAPER, Table 4]

### 4.3 Denoising-step ablation (Atari, not CSGO)

Table 7 reduces denoising steps from 3 to 1 on the 10 highest-performing games. The 1-step column is **one seed**. Mean HNS on that subset falls from `3.052` to `1.962`. Boxing drops `86.9 -> 41.9`, Breakout `132.5 -> 50.8`, RoadRunner `20673.2 -> 5084.0`. Asterix rises `3698.5 -> 6687.0` under the single seed, so the ablation is not uniformly monotonic. Default Table 1 uses `n=3`. [DIASRC-PAPER, Table 7, Sec. 5.2]

### 4.4 Appendix M visual quality (separate claim)

On static CS:GO / driving datasets with `L=6` real context frames and real actions, frame-stack DIAMOND reports CS:GO FID/FVD/LPIPS `9.6 / 34.8 / 0.107` versus IRIS-64 `22.8 / 85.7 / 0.116` and DreamerV3 `106.8 / 509.1 / 0.173`. Driving FID/FVD/LPIPS are `16.7 / 80.3 / 0.058`. Sample rate is 7.4 Hz (20 denoising steps) versus DreamerV3 266.7 Hz. Frame-stack outperforms the paper's cross-attention U-Net variant. These numbers measure reconstruction under logged actions, not Atari HNS and not closed-loop CSGO RL. [DIASRC-PAPER, Table 8]

## 5. Limits

- Mean HNS 1.46 is **best among world-model-trained agents in Table 1**, not Atari 100k SOTA (BBF 2.247, EfficientZero 1.943).
- Five seeds; BankHeist and BattleZone remain weak.
- Table 7 one-step results are single-seed.
- No shuffled-action or counterfactual Atari table isolates causal action sensitivity.
- CSGO/driving Table 8 is a different architecture scale (~122M), static data, and no RL.
- Public `eloialonso/diamond` `main` is the Atari implementation; CSGO requires `git checkout csgo`.
- Hugging Face `play.py --pretrained` is documented, not executed here.

### 4.5 Remaining Table 1 games (same 5-seed protocol)

Games omitted from the highlight table still bind to Table 1 and must be reproduced with the same seeds:

| Game | IRIS | DreamerV3 | STORM | DIAMOND |
|---|---:|---:|---:|---:|
| Alien | 420.0 | 959.0 | 983.6 | 744.1 |
| Amidar | 143.0 | 139.0 | 204.8 | 225.8 |
| Assault | 1524.4 | 706.0 | 801.0 | 1526.4 |
| ChopperCommand | 1565.0 | 420.0 | 1888.0 | 1369.8 |
| DemonAttack | 2034.4 | 303.0 | 164.6 | 288.1 |
| Freeway | 31.1 | 0.0 | 33.5 | 33.3 |
| Frostbite | 259.1 | 909.0 | 1316.0 | 274.1 |
| Gopher | 2236.1 | 3730.0 | 8239.6 | 5897.9 |
| Hero | 7037.4 | 11161.0 | 11044.3 | 5621.8 |
| Jamesbond | 462.7 | 445.0 | 509.0 | 427.4 |
| KungFuMaster | 21759.8 | 21420.0 | 26182.0 | 18713.6 |
| MsPacman | 999.1 | 1327.0 | 2673.5 | 1958.2 |
| PrivateEye | 100.0 | 882.0 | 7781.0 | 114.3 |
| Qbert | 745.7 | 3405.0 | 4522.5 | 4499.3 |
| Seaquest | 661.3 | 618.0 | 525.2 | 551.2 |
| UpNDown | 3546.2 | 9234.0 | 7985.0 | 3856.3 |

Mean HNS `1.459` is not a per-game win rate. PrivateEye and Frostbite remain far from STORM; Assault and Amidar are strengths. [DIASRC-PAPER, Table 1]

### 4.6 EDM objective used at training

Conditioned denoising score matching (paper Eqs. 5-7) is:

```text
L(theta) = E || D_theta(x_{t+1}^tau, tau, x_{<=t}^0, a_{<=t}) - x_{t+1}^0 ||^2
D_theta = c_skip^tau * x^tau + c_out^tau * F_theta(c_in^tau * x^tau, y)
```

`c_skip -> 0` at high noise (predict clean image) and `c_skip -> 1` at low noise (predict residual noise). Euler order-1 is the released sampler; Heun (`order: 2`) is supported but not the Table 1 default. [DIASRC-PAPER, Sec. 2.2-3.1, Eqs. 5-7; DIASRC-CODE-CURRENT, `config/trainer.yaml`]

The CSGO qualitative engine used **87 hours** of static Dust II gameplay in the introduction narrative; Appendix M's quantitative Table 8 instead uses the Clean 190k-frame split. Do not mix those two CSGO data statements. Neither is an Atari 100k HNS result. [DIASRC-PAPER, Sec. 1, Appendix M]

[`reproduction.md`](reproduction.md) owns executed-state claims. [`codebase.md`](codebase.md) owns paper-code mapping.

## Sources

- [DIASRC-PAPER] Alonso et al., *Diffusion for World Modeling: Visual Details Matter in Atari*, NeurIPS 2024 Spotlight / arXiv:2405.12399.
- [DIASRC-CODE-CURRENT] `eloialonso/diamond@5bcd1599755b4f2fae8e5e079e02f0728e174965`.
- [DIASRC-CODE-CSGO-BRANCH] separate `csgo` branch; qualitative only.
