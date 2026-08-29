---
id: world-model-kb.papers.diamond
title: DIAMOND Paper Knowledge Entry
kind: paper
status: maintained
last_updated: 2026-08-19
owners:
  - AIBuildAI world-model group
---

# DIAMOND Paper Knowledge Entry

## Retrieval metadata

**Relevant queries:** DIAMOND, diffusion world model Atari, EDM, visual details matter, IRIS comparison, Atari 100k, mean HNS 1.459, NeurIPS 2024 Spotlight, src/play.py --pretrained, csgo branch, or in-imagination actor-critic.

**Knowledge provided:** NeurIPS 2024 Spotlight identity, image-space EDM world model, Atari 100k evidence, CSGO branch separation, Hugging Face play surface, reproduction state, and Cosmos3-Nano FD/WAM transfer hypotheses.

**Related pages:** [Video world models](../../foundations/representations/video-world-model.md); [diffusion and flow matching](../../foundations/learning-objectives/diffusion-and-flow-matching.md); [model-based RL](../../foundations/decision-making/model-based-rl.md); [observation-space state](../../components/world-representation/observation-space-state.md); [observation-space dynamics](../../components/dynamics-modeling/observation-space-dynamics.md); [diffusion generative modeling](../../components/generative-modeling/diffusion.md); [action-conditioned video modeling](../../components/generative-modeling/action-conditioned-video.md); [Cosmos3-Nano Generator](../../models/cosmos3-nano/generator.md); [action modeling](../../models/cosmos3-nano/action-modeling.md).

Foundation registry [REP-DIAMOND-2024](../../foundations/representations/video-world-model.md) owns the bibliographic identity — this entry does not duplicate that ID in [`sources.yaml`](sources.yaml).

The official [project page](https://diamond-wm.github.io) is a mutable video surface; numerical claims remain bound to the pinned paper. [DIASRC-PAPER]

## Identity and revision boundary

| Field | Canonical value | Consequence |
|---|---|---|
| Work | *Diffusion for World Modeling: Visual Details Matter in Atari* | NeurIPS 2024 Spotlight is the scientific anchor. |
| Paper | arXiv:2405.12399 | Table 1 mean HNS **1.459** (prose 1.46), IQM **0.641**, 11 superhuman games, 5 seeds. [DIASRC-PAPER, Table 1] |
| Official Atari code | `eloialonso/diamond@5bcd1599755b4f2fae8e5e079e02f0728e174965` | `main`, 2024-12-06, Apache-2.0. Entry `src/main.py`, play `src/play.py`. There is no `train_wm.py`. [DIASRC-CODE-CURRENT] |
| CSGO surface | `git checkout csgo` | Qualitative neural game engine on static Dust II logs. **Must not** bind to Atari 100k HNS. [DIASRC-CODE-CSGO-BRANCH] |
| DDPM analysis | `ddpm` branch | Section 5.1 only. |
| Hugging Face | `eloialonso/diamond` | `python src/play.py --pretrained`; not executed here. Inner SHA256 unregistered. [DIASRC-HF-MODEL] |
| Agent class | actor-critic inside `WorldModelEnv` | Not DQN. `training.model_free` must stay `false` for Table 1. |

The paper introduction mentions **87 hours** of CSGO gameplay for the qualitative engine; Appendix M Table 8 instead uses the Clean **190k-frame** split for FID/FVD. Those two CSGO data statements must not be mixed, and neither is an Atari score. [DIASRC-PAPER, Sec. 1, Appendix M]

## Operational model boundary

DIAMOND trains an actor-critic **entirely inside** an EDM diffusion world model operating on pixels. Real Atari supplies world-model data under a 100k-step budget; policy gradients see imagined frames. Evaluation is on the real games.

```text
real Atari -> train EDM denoiser D_theta and reward/termination R_psi
imagine H=15 steps with 3 Euler denoising steps -> train pi_phi, V_phi
deploy pi_phi on real Atari for Table 1
```

| Surface | Inputs | Output or decision | Evidence boundary |
|---|---|---|---|
| Diffusion WM | `L=4` stacked frames plus discrete action | next RGB frame in image space | Atari EDM; AdaGN action; not VQ tokens |
| Reward / terminate | imagined transition | scalar reward and continue flag | Separate `RewEndModel`; not folded into the U-Net by default |
| In-WM actor-critic | imagined observations | policy and value | Entire RL inner loop inside `WorldModelEnv` for Table 1 |
| Atari 100k eval | real env, 5 seeds, 26 games | mean HNS 1.459, IQM 0.641 | World-model-trained class; not BBF SOTA (`2.247`) |
| Pretrained play | Hub weights, one game | interactive demo | Not Table 1; play horizon 50 vs train `H=15` |
| CSGO / driving Appendix M | static datasets, logged actions | FID/FVD/LPIPS Table 8 | **Not** Table 1; no RL; different branch |

A plausible imagined frame is evidence about the denoiser, not a reproduced HNS. A Hub play session is not a 100k training run.

## Knowledge map

| Question | Canonical page |
|---|---|
| Architecture, tables, ablations, limits | [`paper.md`](paper.md) |
| Pinned files, Hydra keys, paper-code gaps | [`codebase.md`](codebase.md) |
| Execution state and acceptance | [`reproduction.md`](reproduction.md) |
| Ten Cosmos3 FD/WAM hypotheses | [`optimization-transfer.md`](optimization-transfer.md) |
| Source identities | [`sources.yaml`](sources.yaml) |

These associations support retrieval. They do not define Agent selection, task order, permissions, or AIBuildAI workflow.

## High-value evidence anchors

- **Image-space EDM, 3 steps.** Adaptive `c_skip` mixing is why few denoising steps remain stable versus DDPM color drift. Table 7 top-10 subset mean HNS `3.052` at 3 steps versus `1.962` at 1 step (1-step is **one seed**). [DIASRC-PAPER, Sec. 5.1-5.2, Eqs. 5-7, Table 7]
- **Table 1 Atari 100k.** Mean HNS `1.459`, IQM `0.641`, 11 superhuman, 5 seeds. Strengths include Breakout `132.5`, Asterix `3698.5`, RoadRunner `20673.2`, Assault `1526.4`. Weak cells include BankHeist `19.7`, PrivateEye `114.3`, Frostbite `274.1`. Best among **world-model-trained** agents in the table, not versus BBF. [DIASRC-PAPER, Tables 1, 6]
- **Compute.** 13M parameters, 2.9 days/game on RTX 4090, versus IRIS 30M / 4.1 days / mean HNS 1.046 and DreamerV3 18M / <1 day / 1.097. [DIASRC-PAPER, Tables 4-5]
- **CSGO isolation.** Appendix M Table 8 and the `csgo` branch are visual-quality / interactive demos. Never cite them as support for 1.46 HNS. Frame-stack Atari versus CSGO cross-attention is `DIAMOND-XFER-10`, not a Table 1 claim. [DIASRC-CODE-CSGO-BRANCH]
- **Play versus train.** `python src/play.py --pretrained` from `main`; training is `python src/main.py env.train.id=BreakoutNoFrameskip-v4 common.devices=0`. Hydra keys: `num_steps_total=100000`, `horizon=15`, `num_steps_denoising=3`, `sigma` loc/scale `-0.4`/`1.2`. Not executed. [`reproduction.md`](reproduction.md)
- **Cosmos3 attachment.** Pixel FD and in-imagination WAM attach to **Generator FD/WAM**, not Reasoner. [`optimization-transfer.md`](optimization-transfer.md)

## Failure modes and non-goals

- Do not bind CSGO FID/FVD (Appendix M Table 8) or the `csgo` branch to Atari mean HNS 1.459.
- Do not describe the agent as DQN. It is actor-critic in `WorldModelEnv`.
- Do not treat Hub play (`src/play.py --pretrained`, horizon 50) as Table 1.
- Do not claim SOTA versus BBF 2.247; the paper's class is world-model-trained agents (IRIS 1.046, DreamerV3 1.097 in Table 4).
- PrivateEye `114.3` and BankHeist `19.7` remain weak; mean HNS is not a per-game win rate.
- `training.model_free=true` is a different agent.

## Evidence index

| Claim | Locator | Page |
|---|---|---|
| Mean HNS 1.459 / IQM 0.641 | Table 1 | [`paper.md`](paper.md) |
| 11 superhuman, 5 seeds | Table 1 | paper |
| Breakout 132.5, Asterix 3698.5, RoadRunner 20673.2 | Table 1 | paper |
| BankHeist 19.7, PrivateEye 114.3 | Table 1 | paper |
| 13M params, 2.9 days, vs IRIS 1.046 | Tables 4-5 | paper |
| 3-step vs 1-step 3.052 vs 1.962 | Table 7 | paper |
| CSGO Table 8 not Atari | Appendix M | paper |
| Entry `src/main.py`, play `src/play.py` | pinned tree | [`codebase.md`](codebase.md) |
| `num_steps_denoising=3`, `H=15` | `config/trainer.yaml` | codebase |
| Ten FD/WAM hypotheses | `DIAMOND-XFER-01..10` | [`optimization-transfer.md`](optimization-transfer.md) |
| Not executed | all train/play | [`reproduction.md`](reproduction.md) |

## Sources

Identities in [`sources.yaml`](sources.yaml). Cross-entry registration: [REP-DIAMOND-2024](../../foundations/representations/video-world-model.md).
