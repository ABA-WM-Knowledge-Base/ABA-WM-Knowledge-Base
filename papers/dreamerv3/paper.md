---
id: world-model-kb.papers.dreamerv3.paper
title: DreamerV3 Method, Architecture, and Experimental Evidence
kind: paper
status: maintained
last_updated: 2026-08-14
owners:
  - AIBuildAI world-model group
---

# DreamerV3 Method, Architecture, and Experimental Evidence

## Retrieval metadata

**Relevant queries:** DreamerV3 Nature 2025, RSSM, symlog, free bits, unimix, Minecraft diamonds, Atari 200M, Atari100k, Proprio Control Suite, danijar/dreamerv3 reimplementation, arXiv 2301.04104 preprint.

**Knowledge provided:** Nature-canonical algorithm, robustness losses, eight-domain protocol, Minecraft milestone, and the preprint/public-code identity split.

**Related pages:** [`README.md`](README.md); [`codebase.md`](codebase.md); [model-based RL](../../foundations/decision-making/model-based-rl.md); [latent world models](../../foundations/representations/latent-world-model.md).

Foundation registry: [MBRL-DREAMERV3-2025]. Do not duplicate that ID in [`sources.yaml`](sources.yaml).

## 1. Canonical identity

**Canonical:** Hafner et al., *Mastering diverse control tasks through world models*, Nature 640:647-653 (2025), DOI 10.1038/s41586-025-08744-2. [DV3SRC-PAPER-NATURE]

**Preprint only:** arXiv:2301.04104, former title *Mastering Diverse Domains through World Models*. ar5iv HTML conversion **failed** for this id; do not scrape broken HTML. Use the preprint for revision history, not as the result surface. [DV3SRC-PAPER-ARXIV]

**Public code:** `danijar/dreamerv3` is a **reimplementation** based on open DreamerV2 code, "unrelated to Google or DeepMind," tested to reproduce a range of official results. It is not internal Google training infrastructure. [DV3SRC-CODE-CURRENT README]

## 2. Algorithm

Three networks trained concurrently from replay while acting: world model, critic, actor. World model is an RSSM:

```text
h_t = f(h_{t-1}, z_{t-1}, a_{t-1})          # block GRU sequence model
z_t ~ q(z_t | h_t, x_t)                    # encoder (categorical)
zhat_t ~ p(zhat_t | h_t)                   # dynamics
rhat, chat, xhat from (h_t, z_t)           # reward, continue, decode
```

Loss: `L = E sum_t (beta_pred L_pred + beta_dyn L_dyn + beta_rep L_rep)` with `beta_pred=1`, `beta_dyn=1`, `beta_rep=0.1`. KL terms use **free bits** clipped at 1 nat (~1.44 bits) and KL balancing via stop-gradient. Representations are vectors of softmax categoricals with straight-through gradients. [DV3SRC-PAPER-NATURE, World model learning]

Robustness stack (Nature "changes introduced for DreamerV3"):

- observation **symlog** on vector inputs and decoder targets;
- KL balance + free bits;
- **1% unimix** on RSSM and actor categoricals;
- percentile return normalization (5th-95th in the public config);
- **symexp two-hot** loss for reward head and critic;
- block GRU, RMSNorm, SiLU;
- adaptive gradient clipping, LaProp (RMSProp before momentum);
- larger replay, online queue, stored latent states.

Symlog / symexp:

```text
symlog(x) = sign(x) log(|x|+1)
symexp(x) = sign(x) (exp(|x|)-1)
```

Imagination trains actor-critic from predicted latents (public default `imag_length: 15`, `horizon: 333` with continue discount). [DV3SRC-PAPER-NATURE; DV3SRC-CODE-CURRENT, `dreamerv3/configs.yaml`]

## 3. Evaluation protocol (Nature)

Eight domains, **>150 tasks**, **one hyperparameter configuration** (replay ratio chosen to fit each budget). Five seeds except ten for BSuite and Minecraft. Single Nvidia A100 per agent. Default **200 million** parameter size. 16 env instances by default; 1 for BSuite and Atari100k; 64 remote workers for Minecraft. [DV3SRC-PAPER-NATURE, Benchmarks; Protocols]

| Domain | Budget / setting | Nature claim (prose) |
|---|---|---|
| Atari 57 sticky | 200M frames | outperforms MuZero at a fraction of compute; also Rainbow, IQN |
| Atari100k 26 games | 400k frames (100k after repeat) | outperforms IRIS, TWM, SimPLe, SPR; EfficientZero uses extra tricks/level resets |
| ProcGen 16 hard unlimited | 50M frames | outperforms PPG, Rainbow; PPO matches tuned official PPO |
| DMLab 30 tasks | 100M frames | exceeds IMPALA and R2D2+ **at 1B steps** (10x data advantage to baselines) |
| Proprio Control Suite 20 | 1M steps | matches DMPO, TD-MPC2 |
| Visual Control Suite 20 | 1M steps | SOTA vs DrQ-v2, TD-MPC2 |
| BSuite 23 envs / 468 configs | benchmark protocol | SOTA, especially scale robustness |
| Minecraft Diamond | 100M steps, ~30 min episodes, MineRL actions, faster block break | **all** Dreamer seeds collect diamonds; baselines do not |

**Extended Data Table 1** (aggregated scores) is present in Nature/PMC HTML only as a figure placeholder ("Open in a new tab"). Numeric cells were **not recovered** from HTML. Do not invent them. Individual-task scores are in Supplementary Information, also not extracted here. [DV3SRC-PAPER-NATURE]

Minecraft: 12-item chain from sparse rewards, no human data, no curriculum. Episodes up to 36,000 steps. VPT used contractor data and 720 GPUs for 9 days; Dreamer uses 1 GPU for 9 days in the Nature comparison paragraph. Voyager uses MineFlayer high-level commands — not a matched action space. [DV3SRC-PAPER-NATURE, Minecraft]

Public env wrappers at the pinned commit (not Nature internals): `embodied/envs/atari.py` (5676 B), `minecraft.py` (437 B) plus `minecraft_flat.py` (14011 B), `dmc.py`, `dmlab.py`, `procgen.py`, `bsuite.py`, `crafter.py`, `loconav.py`. Launch remains `python dreamerv3/main.py`. RSSM implementation: `dreamerv3/rssm.py` (13639 B). Agent: `dreamerv3/agent.py` (18262 B). Replay: `embodied/core/replay.py` (13895 B). Train loop: `embodied/run/train.py` (4039 B). [DV3SRC-CODE-CURRENT]

## 4. Public reimplementation hyperparameters (not a Nature table)

Pinned `dreamerv3/configs.yaml` defaults that match the Nature robustness list:

| Key | Value |
|---|---|
| `agent.dyn.rssm.deter / hidden / stoch / classes` | 8192 / 1024 / 32 / 64 |
| `blocks` / `free_nats` / `unimix` | 8 / 1.0 / 0.01 |
| `loss_scales.rep` | 0.1 |
| `rewhead.output` / `value.output` | `symexp_twohot`, 255 bins |
| `enc.simple.symlog` | true |
| `retnorm.impl` | `perc`, 5.0-95.0 |
| `imag_length` | 15 |
| `opt.agc` | 0.3 |
| `replay.size` | 5e6, `online: True` |

Size blocks: `size1m` ... `size400m`. Task blocks include `atari`, `atari100k`, `minecraft`, `dmc_proprio`, `dmc_vision`, `procgen`, `dmlab`, `bsuite`, `crafter`. `debug` shrinks the net and must not be used for paper claims. [DV3SRC-CODE-CURRENT]

## 5. Limits

- Nature Extended Data Table 1 numbers unverified from HTML.
- Public repo is a reimplementation; exact internal Google/DeepMind stack is undisclosed.
- Atari100k here is **not** DIAMOND's Table 1 (different paper, different agent).
- Minecraft uses abstract crafting and accelerated breaking; not keyboard-mouse VPT.
- No local training in this KB.

## 6. Cosmos3 attachment map

| DreamerV3 mechanism | Cosmos3 surface | Not this surface |
|---|---|---|
| Pixel/latent RSSM decode | compact latent WAM, optional renderer | Generator FID showcase |
| Symlog / two-hot / free bits / unimix | scalar FD/WAM heads | Reasoner text logits |
| Imagination actor-critic | WAM self-consistency | Policy-DROID without a WM |
| Continue head | terminal auxiliary | safety certificate |

Atari 100k in this paper is **not** DIAMOND Table 1 (different agent, different HNS). Minecraft diamonds are **not** VPT or Voyager.

## 7. Public config dump (implementation analog)

Additional `dreamerv3/configs.yaml` keys inspected at `e3f02248693a79dc8b0ebd62c93683888ddaccfe`:

| Key | Default (public) | Notes |
|---|---|---|
| `run.steps` | domain-specific | Atari100k block uses `1.1e5` |
| `run.train_ratio` | domain-specific | Atari100k `256`; Crafter example CLI uses `32` |
| `batch_size` / `batch_length` | see yaml | `debug` shrinks these |
| `opt.lr` / `opt.agc` | yaml; AGC `0.3` | LaProp-style in `embodied/jax/opt.py` |
| `policy.unimix` | 0.01 | matches RSSM unimix |
| `contdisc` | True | continue discount |
| `replay.online` | True | online queue |
| `agent.enc.simple.symlog` | True | vector obs |

Do not paste these keys into a Nature table. They are the public reimplementation contract. [DV3SRC-CODE-CURRENT]

### 7.1 Robustness list (Nature prose, not a numbered table)

The Nature text lists changes versus prior Dreamer versions: observation symlog; KL balancing and free bits (1 nat); 1% unimix on categoricals; percentile return normalization; symexp two-hot for reward and critic; block GRU with RMSNorm and SiLU; adaptive gradient clipping; LaProp; larger replay with an online queue and stored latent states. Public analogs: `free_nats: 1.0`, `unimix: 0.01`, `retnorm.impl: perc` 5-95, `opt.agc: 0.3`, `replay.size: 5e6`, `replay.online: True`. [DV3SRC-PAPER-NATURE; DV3SRC-CODE-CURRENT]

### 7.2 What was not recovered

- Extended Data Table 1 aggregate scores (HTML figure placeholder).
- Per-task supplementary tables.
- Internal Google/DeepMind trainer, exact JAX/TPU stack, and unreleased seeds.
- ar5iv HTML of arXiv:2301.04104 (fatal conversion).

Do not fill those cells from memory or from DIAMOND/iVideoGPT tables.

## 8. Domain wrappers (public tree)

| Domain | Wrapper files | Public flags to record |
|---|---|---|
| Atari 57 | `embodied/envs/atari.py` | sticky True, repeat 4, 96x96 |
| Atari100k | same + `atari100k` config | sticky False, 64x64, 1 env |
| Minecraft | `minecraft.py`, `minecraft_flat.py` | `break_speed: 100`, length 36000 |
| DMC proprio/vision | `dmc.py` | 1M-step Nature budget |
| DMLab | `dmlab.py` | 100M vs baselines at 1B |
| ProcGen | `procgen.py` | 16 hard, 50M |
| BSuite | `bsuite.py` | 10 seeds in Nature |
| Crafter | `crafter.py` | smoke-friendly |

Launch remains `python dreamerv3/main.py --configs <block> --task <id>`. Docker/`entrypoint.sh` is an install hint, not a Nature binary.

### 8.1 Minecraft protocol (Nature prose)

12-item crafting chain from sparse item rewards, no human data, no curriculum. Episodes up to 36,000 steps (~30 min). MineRL action space with accelerated block breaking. **All** Dreamer seeds collect diamonds within 100M steps; reported baselines do not. VPT comparison: contractor data and 720 GPUs for 9 days versus Dreamer 1 GPU for 9 days. Voyager uses MineFlayer high-level commands — unmatched action space. Public analog: `embodied/envs/minecraft_flat.py`, `break_speed: 100.0`, `length: 36000`. [DV3SRC-PAPER-NATURE; DV3SRC-CODE-CURRENT]

### 8.2 Atari protocols (do not mix)

Nature Atari 57 uses sticky actions and 200M frames. Nature Atari100k uses the original 26-game SimPLe protocol (400k frames including action repeat). Public `atari` vs `atari100k` config blocks differ (sticky, resolution, env count). Neither is DIAMOND Table 1 (mean HNS 1.459, EDM pixel WM). [DV3SRC-PAPER-NATURE; contrast DIASRC-PAPER]

Nature Control Suite: 20 proprio and 20 visual tasks at 1M steps; matches DMPO/TD-MPC2 on proprio and is reported SOTA versus DrQ-v2/TD-MPC2 on visual. ProcGen: 16 hard unlimited, 50M frames, versus PPG/Rainbow; PPO matches tuned official PPO. DMLab: 30 tasks, 100M frames, exceeds IMPALA and R2D2+ **at 1B steps** (10x data advantage to those baselines). BSuite: 23 envs / 468 configs; SOTA especially scale robustness. These are Nature **prose** claims; numeric Extended Data Table 1 cells remain unrecovered. [DV3SRC-PAPER-NATURE]

## Sources

- [DV3SRC-PAPER-NATURE] Nature 640:647-653 (2025).
- [DV3SRC-PAPER-ARXIV] preprint identity only.
- [DV3SRC-CODE-CURRENT] `danijar/dreamerv3@e3f02248693a79dc8b0ebd62c93683888ddaccfe`.
