---
id: world-model-kb.papers.dreamerv3.codebase
title: DreamerV3 Public Reimplementation Graph
kind: reference
status: maintained
last_updated: 2026-08-14
owners:
  - AIBuildAI world-model group
---

# DreamerV3 Public Reimplementation Graph

## Retrieval metadata

**Relevant queries:** danijar dreamerv3, rssm.py, configs.yaml, embodied/run/train.py, minecraft.py, reimplementation disclaimer.

**Knowledge provided:** pinned public tree, config keys, train entry, and paper-code scope. Not Google internal code.

**Related pages:** [`paper.md`](paper.md); [`reproduction.md`](reproduction.md).

## 1. Revision policy

`danijar/dreamerv3@e3f02248693a79dc8b0ebd62c93683888ddaccfe` (2026-05-25). README: reimplementation of the Nature algorithm from the open DreamerV2 codebase; **unrelated to Google or DeepMind**. [DV3SRC-CODE-CURRENT]

Nature remains canonical for claims. This tree is the public attachment surface.

## 2. Tree

```text
dreamerv3/main.py            # CLI entry
dreamerv3/agent.py
dreamerv3/rssm.py
dreamerv3/configs.yaml
embodied/run/train.py
embodied/run/train_eval.py
embodied/run/eval_only.py
embodied/run/parallel.py
embodied/jax/agent.py
embodied/jax/heads.py        # two-hot, binary, policy dists
embodied/jax/nets.py
embodied/jax/opt.py          # AGC, LaProp-style
embodied/core/replay.py
embodied/core/driver.py
embodied/envs/atari.py
embodied/envs/minecraft.py
embodied/envs/minecraft_flat.py
embodied/envs/dmc.py
embodied/envs/dmlab.py
embodied/envs/procgen.py
embodied/envs/bsuite.py
embodied/envs/crafter.py
baselines.yaml
Dockerfile / entrypoint.sh / requirements.txt
```

## 3. Launch graph

```text
python dreamerv3/main.py \
  --logdir ~/logdir/dreamer/{timestamp} \
  --configs crafter \
  --run.train_ratio 32
```

Reproduce-style: `--configs atari --task atari_pong`. Platform: `--jax.platform cpu` to leave GPU. Multiple config blocks stack (`--configs crafter size50m`). Continue by repeating the same `--logdir`. [DV3SRC-CODE-CURRENT README]

```text
main.py -> embodied.run.train
  -> env from embodied/envs/*
  -> JAX agent (rssm encoder/dynamics/heads)
  -> replay online queue
  -> imagine imag_length steps -> actor-critic
  -> JSONL + Scope logs
```

`debug` config sets `run.debug: True` and tiny widths — not a paper run.

Size and task blocks documented in `dreamerv3/configs.yaml` (6365 B): `size1m` through `size400m`; `atari`, `atari100k`, `minecraft`, `dmc_proprio`, `dmc_vision`, `procgen`, `dmlab`, `bsuite`, `crafter`. Atari wrapper flags: `env.atari.sticky: True`, `repeat: 4`, size `[96,96]`. Atari100k block: `sticky: False`, size `[64,64]`, `run.steps: 1.1e5`, `train_ratio: 256`, `envs: 1`. Minecraft: `break_speed: 100.0`, `length: 36000`. JAX stack: `embodied/jax/agent.py` (19820 B), `nets.py` (21805 B), `heads.py` (5237 B), `opt.py` (5617 B). [DV3SRC-CODE-CURRENT]

## 4. RSSM / heads mapping

| Nature mechanism | Public keys / files |
|---|---|
| Categorical latents | `rssm.stoch=32`, `classes=64` in `configs.yaml`; `dreamerv3/rssm.py` |
| Free bits | `free_nats: 1.0` |
| Unimix 1% | `unimix: 0.01` on rssm and `policy` |
| Representation loss scale | `loss_scales.rep: 0.1` |
| Symlog observations | `enc.simple.symlog: True` |
| Symexp two-hot | `rewhead.output`, `value.output` |
| Percentile return norm | `retnorm.impl: perc` 5-95 |
| Block GRU | `rssm.blocks: 8`, `deter: 8192` |
| Imagination | `imag_length: 15` |

Atari wrapper: `env.atari.sticky: True`, `repeat: 4`, size `[96,96]`. Atari100k block: `sticky: False`, size `[64,64]`, `run.steps: 1.1e5`, `train_ratio: 256`, `envs: 1`. Minecraft: `break_speed: 100.0`, `length: 36000`. [DV3SRC-CODE-CURRENT, `configs.yaml`, `embodied/envs/atari.py`, `minecraft.py`]

## 5. Gap ledger

| ID | Evidence | Effect | Repair |
|---|---|---|---|
| `DREAMERV3-CODE-GAP-01` | README reimplementation disclaimer | not internal Google code | never claim bit-exact Nature binaries |
| `DREAMERV3-CODE-GAP-02` | arXiv HTML failed | preprint tables not scraped | Nature + this tree |
| `DREAMERV3-CODE-GAP-03` | Extended Data Table 1 not in HTML | missing aggregate numbers | supplementary PDF not fetched |
| `DREAMERV3-CODE-GAP-04` | extra env packages | import errors | Dockerfile as hint |
| `DREAMERV3-CODE-GAP-05` | `Too many leaves` on mismatched ckpt | silent wrong logdir | new logdir per config |
| `DREAMERV3-CODE-GAP-06` | `debug` easy to leave on | toy run | require `run.debug false` |

## 6. Change surfaces

| Intervention | Files |
|---|---|
| Symlog / two-hot | `configs.yaml` enc/rewhead/value; `embodied/jax/heads.py` |
| Free bits / unimix | `rssm.py`, `free_nats`, `unimix` |
| Imagination length | `imag_length` |
| Return percentile | `retnorm` |
| Env wrappers | `embodied/envs/*.py` |

## 7. Additional public modules

| Path | Bytes | Role |
|---|---:|---|
| `dreamerv3/agent.py` | 18262 | JAX agent |
| `dreamerv3/rssm.py` | 13639 | RSSM |
| `dreamerv3/main.py` | 9451 | CLI |
| `dreamerv3/configs.yaml` | 6365 | all flags |
| `embodied/jax/nets.py` | 21805 | blocks |
| `embodied/jax/agent.py` | 19820 | scan/train |
| `embodied/run/parallel.py` | 16997 | multi-env |
| `embodied/core/replay.py` | 13895 | buffer |
| `embodied/envs/minecraft_flat.py` | 14011 | diamond chain |
| `embodied/envs/atari.py` | 5676 | sticky/repeat |
| `baselines.yaml` | 4269 | comparison dumps |
| `Dockerfile` / `entrypoint.sh` | install hint | not Nature binaries |

Disclaimer in README must be copied into every run record: reimplementation, unrelated to Google or DeepMind.

Also present: `embodied/core/driver.py`, `wrappers.py`, `selectors.py`, `embodied/run/train_eval.py`, `eval_only.py`, `embodied/jax/outs.py`, `transform.py`, `embodied/envs/loconav.py`, `pinpad.py`, `procgen.py`, `dmlab.py`, `bsuite.py`, `crafter.py`, `plot.py`, `setup.py`. Perf/tests under `embodied/perf/` and `embodied/tests/` are not Nature tables.

## 8. Paper versus public code

| Nature surface | Public tree | Consequence |
|---|---|---|
| Algorithm (RSSM, symlog, unimix, free bits) | `rssm.py`, `configs.yaml`, `heads.py` | mechanism mapping allowed |
| Minecraft diamonds within 100M | `minecraft_flat.py` | protocol analog; not Nature logs |
| Atari 57 sticky 200M | `atari` config | reimplementation |
| Atari100k SimPLe 26 games | `atari100k` config | different wrapper flags |
| Extended Data Table 1 | absent from inspected HTML | no aggregate claim |
| Internal Google trainer | explicitly disclaimed | never implied |

`DREAMERV3-CODE-GAP-00` in earlier notes: this tree is DreamerV2-lineage reimplementation. Do not treat checkpoint compatibility with unpublished Nature binaries as given.

## Sources

- [DV3SRC-CODE-CURRENT] pinned commit.
- [DV3SRC-PAPER-NATURE] algorithm claims.
