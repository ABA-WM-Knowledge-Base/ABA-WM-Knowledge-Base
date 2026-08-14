---
id: world-model-kb.papers.diamond.codebase
title: DIAMOND Released Implementation Graph
kind: reference
status: maintained
last_updated: 2026-08-14
owners:
  - AIBuildAI world-model group
---

# DIAMOND Released Implementation Graph

## Retrieval metadata

**Relevant queries:** eloialonso diamond, src/main.py, src/play.py --pretrained, WorldModelEnv, denoiser.py, actor_critic.py, config/trainer.yaml, csgo branch, or DIAMOND-CODE-GAP.

**Knowledge provided:** pinned Atari `main` call graph with real paths, Hydra configs, tensor/sampler contracts, CSGO branch isolation, and paper-code gaps.

**Related pages:** [`paper.md`](paper.md); [`reproduction.md`](reproduction.md); [Cosmos3-Nano Generator](../../models/cosmos3-nano/generator.md); [action modeling](../../models/cosmos3-nano/action-modeling.md).

## 1. Revision and branch policy

All file mappings below use `eloialonso/diamond@5bcd1599755b4f2fae8e5e079e02f0728e174965` on `main`, dated 2024-12-06, Apache-2.0. The repository has no release tag. [DIASRC-CODE-CURRENT]

| Identity | Pin | Scope |
|---|---|---|
| Atari quantitative surface | `main` at the commit above | Table 1 HNS, `src/main.py` training, `results/data/DIAMOND.json` |
| CSGO qualitative demo | `git checkout csgo` (separate branch) | `src/play.py` interactive engine; **never** bind to Table 1 |
| DDPM analysis code | `ddpm` branch (README) | Section 5.1 comparison; not the Table 1 agent |
| Hugging Face weights | `eloialonso/diamond` | downloaded by `src/play.py --pretrained` |

Rule: any CSGO-branch capability is out of scope for Atari table reproduction unless a run record checks out that branch under a different acceptance contract. [DIASRC-CODE-CSGO-BRANCH]

## 2. Tree at the pinned commit

```text
config/trainer.yaml              # Hydra root: collection 100k, H=15, 3 denoising steps
config/agent/default.yaml        # U-Net / actor-critic widths
config/env/atari.yaml            # Atari wrappers
src/main.py                      # training entry
src/trainer.py                   # epoch loop, WM + AC updates
src/play.py                      # play / --pretrained / dataset replay
src/agent.py                     # wraps denoiser, rew_end, actor_critic
src/models/diffusion/denoiser.py
src/models/diffusion/inner_model.py
src/models/diffusion/diffusion_sampler.py
src/models/actor_critic.py
src/models/rew_end_model.py
src/models/blocks.py             # AdaGN residual blocks
src/envs/world_model_env.py      # imagination environment
src/envs/atari_preprocessing.py
src/envs/env.py
src/coroutines/collector.py
src/coroutines/env_loop.py
src/data/dataset.py              # episode store
src/game/play_env.py             # interactive play
scripts/resume.sh
results/data/DIAMOND.json        # paper seed scores
requirements.txt
```

There is no `train_wm.py` or `train_agent.py`. Those names in older notes are incorrect for this commit.

## 3. Configuration resolution

Hydra loads `config/trainer.yaml`, which composes `env: atari` and `agent: default`. Relevant released defaults: [DIASRC-CODE-CURRENT, `config/trainer.yaml`]

| Key | Value | Role |
|---|---|---|
| `collection.train.num_steps_total` | 100000 | Atari 100k budget |
| `collection.train.steps_per_epoch` | 100 | real env steps / epoch |
| `collection.train.epsilon` | 0.01 | collection epsilon-greedy |
| `world_model_env.horizon` | 15 | imagination `H` |
| `diffusion_sampler.num_steps_denoising` | 3 | Table 1 default |
| `diffusion_sampler.sigma_min / sigma_max` | `2e-3` / `5.0` | EDM sampler |
| `diffusion_sampler.order` | 1 | Euler |
| `denoiser.training.steps_per_epoch` | 400 | WM updates / epoch |
| `denoiser.training.batch_size` | 32 | |
| `sigma_distribution.loc / scale` | `-0.4` / `1.2` | matches paper `P_mean`, `P_std` |
| `actor_critic_loss.gamma / lambda_` | `0.985` / `0.95` | Table 3 |
| `weight_entropy_loss` | 0.001 | Table 3 `eta` |
| `training.model_free` | `false` | must stay false for in-WM RL |
| `training.compile_wm` | `true` | `torch.compile` on the denoiser |

`scripts/resume.sh` is the documented crash-recovery path. `common.devices` defaults to `0`.

## 4. Training call graph

```text
src/main.py
  -> Hydra config
  -> Trainer (src/trainer.py)
       -> env factory (src/envs/env.py, atari_preprocessing.py)
       -> Agent: Denoiser + RewEndModel + ActorCritic
       -> Dataset episode store (src/data/dataset.py)
       -> collector (src/coroutines/collector.py)
       for epoch:
            collect 100 real steps (epsilon 0.01)
            Denoiser.training_step   # EDM loss on next frame
            RewEndModel.training_step
            ActorCritic.training_step inside WorldModelEnv
            periodic eval on real env
            checkpoint checkpoints/state.pt and agent_versions/agent_epoch_*.pt
```

`WorldModelEnv` (`src/envs/world_model_env.py`) is the imagination MDP: it calls `DiffusionSampler` for the next frame, then `RewEndModel` for reward and continuation. Actor-critic losses live in `src/models/actor_critic.py` (`ActorCriticLossConfig`: `backup_every=15`). [DIASRC-CODE-CURRENT]

## 5. Denoiser tensor contract

`src/models/diffusion/inner_model.py` implements the frame-stack U-Net. Expected Atari layout:

- stacked conditioning frames plus noised next frame on the channel axis;
- discrete action embedded and injected by AdaGN together with `sigma`;
- output: denoised next-frame prediction in image space (not VQ tokens).

`src/models/diffusion/diffusion_sampler.py` runs the EDM Euler/Heun loop. Play-mode horizon defaults to 50 steps in the README visualization path; training imagination stays at `horizon: 15`. Editing `world_model_env.diffusion_sampler` in `config/trainer.yaml` is the documented way to trade steps for speed. [DIASRC-CODE-CURRENT; DIASRC-PAPER, Table 2]

## 6. Play and Hugging Face

```bash
python src/play.py --pretrained
```

This downloads a game-specific world-model plus policy from `eloialonso/diamond` on the Hub and caches locally. Controls: `m` switches policy/human; arrows change imagination horizon. Add `-d` for dataset replay of `dataset/rec_*` recordings. No inner checkpoint SHA256 is registered in this KB. [DIASRC-HF-MODEL; DIASRC-CODE-CURRENT, `src/play.py`]

CSGO:

```bash
git checkout csgo
python src/play.py
```

Apple Silicon requires `PYTORCH_ENABLE_MPS_FALLBACK=1`. This path is a different tree and weight set. [DIASRC-CODE-CSGO-BRANCH]

## 7. Paper-code gap ledger

| ID | Evidence | Effect | Repair boundary |
|---|---|---|---|
| `DIAMOND-CODE-GAP-00` | CSGO and DDPM live on other branches | Table 1 cannot be reproduced from `csgo` HEAD | pin `main` SHA on every Atari run |
| `DIAMOND-CODE-GAP-01` | no release tag | identity is commit-only | record `5bcd1599755b4f2fae8e5e079e02f0728e174965` |
| `DIAMOND-CODE-GAP-02` | `requirements.txt` is short; Python 3.10 in README | env drift | external lock; do not call it author-complete |
| `DIAMOND-CODE-GAP-03` | Atari ROM download acknowledges license | legal/install friction | record ROM hash and license accept |
| `DIAMOND-CODE-GAP-04` | HF inner file hashes not in KB | integrity unverified | SHA256 on fetch |
| `DIAMOND-CODE-GAP-05` | `training.compile_wm: True` | compile graphs can hide numerical diffs | record compile on/off |
| `DIAMOND-CODE-GAP-06` | play horizon 50 vs train `H=15` | demo quality ≠ training imagination | do not treat play videos as Table 1 evidence |
| `DIAMOND-CODE-GAP-07` | `results/data/DIAMOND.json` is reported scores, not a rerun | convenience copy of Table 1 seeds | rerun still required for reproduction |

## 8. Optimization change surfaces

| Intervention | Primary files | Controls to retain |
|---|---|---|
| Denoising steps at imagination | `config/trainer.yaml` `num_steps_denoising`; `diffusion_sampler.py` | horizon, actor LR, 100k budget |
| Frame-stack vs cross-attention | `inner_model.py` (Atari is frame-stack) | parameter count; do not import CSGO weights |
| Action AdaGN strength | `src/models/blocks.py`, `inner_model.py` | sigma embedding, channel width |
| Imagination horizon | `world_model_env.horizon`, `backup_every` | gamma, lambda |
| Unplug WM | `training.model_free` | this is no longer the paper agent |
| Reward head | `src/models/rew_end_model.py` | do not fold into denoiser without ablation |

A **released-compatible** run keeps `num_steps_denoising=3`, `H=15`, `model_free=false`, and `main`. A paper-faithful reconstruction may change sampler order or compile flags but must record the diff.

## 9. Additional pinned blobs

| Path | Bytes | Role |
|---|---:|---|
| `src/trainer.py` | 17698 | epoch loop |
| `src/utils.py` | 10910 | helpers |
| `src/models/blocks.py` | 8351 | AdaGN |
| `src/play.py` | 5886 | Hub play |
| `src/game/play_env.py` | 6470 | interactive |
| `src/envs/world_model_env.py` | 5152 | imagination MDP |
| `src/data/dataset.py` | 4950 | episode store |
| `src/models/rew_end_model.py` | 4741 | reward/term |
| `src/models/actor_critic.py` | 4619 | AC |
| `src/models/diffusion/denoiser.py` | 4296 | EDM wrapper |
| `config/trainer.yaml` | 3061 | Hydra root |
| `results/data/DIAMOND.json` | 2585 | reported seeds |
| `requirements.txt` | 210 | not a lockfile |

## Sources

- [DIASRC-CODE-CURRENT] `eloialonso/diamond@5bcd1599755b4f2fae8e5e079e02f0728e174965`.
- [DIASRC-PAPER] architecture tables and Atari protocol.
- [DIASRC-HF-MODEL] pretrained play surface.
- [DIASRC-CODE-CSGO-BRANCH] CSGO branch policy.
