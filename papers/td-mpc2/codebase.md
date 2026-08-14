---
id: world-model-kb.papers.td-mpc2.codebase
title: TD-MPC2 Released Implementation Graph
kind: reference
status: maintained
last_updated: 2026-08-14
owners:
  - AIBuildAI world-model group
---

# TD-MPC2 Released Implementation Graph

## Retrieval metadata

**Relevant queries:** tdmpc2 repository, commit e9f5932, WorldModel, TDMPC2._plan, SimNorm, two-hot, Q ensemble init, OnlineTrainer, OfflineTrainer, config.yaml, evaluate.py, or env wrappers.

**Knowledge provided:** the pinned implementation call graph, configuration and tensor contracts, exact mechanism attachment points, released artifacts, static defects, and the boundary between ICLR evidence and post-paper maintenance.

**Related pages:** [`paper.md`](paper.md) owns the method and results; [`reproduction.md`](reproduction.md) owns executed status; [model-based RL](../../foundations/decision-making/model-based-rl.md) owns the generic loop; [Cosmos3-Nano action modeling](../../models/cosmos3-nano/action-modeling.md) owns target-model FD/WAM surfaces; [Cosmos3-Nano reasoner](../../models/cosmos3-nano/reasoner.md) owns the latent-planning attachment for this paper.

## 1. Revision and release policy

All file and symbol mappings below use `nicklashansen/tdmpc2@e9f59321933cbc8e11a002b842adc7d4ffae8ff1`, the inspected `main` commit dated 2026-07-13. The repository is MIT-licensed. There is no separate model zoo with one checksum per inner checkpoint in this KB; released `.pt` files must be hashed on download. [TDMPC2-CODE]

This commit includes a **Q-ensemble weight-initialization fix** implemented through `tdmpc2/common/init.py` (`weight_init`, `zero_`) and applied to each ensemble member in `tdmpc2/common/world_model.py`. The fix is **maintenance**, not ICLR 2024 evidence. A strict table replication should either check out the parent of this change or record the delta. [TDMPC2-CODE; TDMPC2-PAPER]

Foundation paper identity: [MBRL-TDMPC2-2024] — not duplicated in [`sources.yaml`](sources.yaml).

## 2. Released surface versus paper surface

| Capability | Paper | Public implementation at pinned commit | Consequence |
|---|---|---|---|
| Single-task online RL | 104-task sweep, one yaml | `train.py` + `trainer/online_trainer.py` + `config.yaml` | released core training surface |
| Multitask offline 80-task | 545M transitions, 1M-317M models | `train.py` selects `OfflineTrainer` when `cfg.multitask` | requires the offline dataset; not a smoke path |
| MPPI planning | Table 8 | `tdmpc2.py` `TDMPC2._plan` / `_estimate_value` | matches H=3, 512/24/64, +2 iters if `|A|>=20` |
| SimNorm, 101-bin regression, 5 Q | Table 8 | `common/layers.py`, `common/world_model.py`, `config.yaml` | released-faithful |
| 317M widths / 8 Q | Table 9 | `model_size=317` overrides in parser | must set `model_size`, not the yaml defaults |
| Visual 64x64 + shift | 10 DMC visual tasks | `common/layers.py` `conv`, `ShiftAug`, `PixelPreprocess` | `obs=rgb` |
| Discrete actions | explicitly open | no discrete action encoder | paper-only limitation, not a missing script |
| Real robot | not claimed | no hardware loop | paper-only absence |
| Q-ensemble init | paper-era init | post-paper `init.weight_init` on each ensemble MLP | do not treat scores from this pin as ICLR numbers |

## 3. Configuration resolution

`python train.py` / `python evaluate.py` are Hydra entry points with `config_name='config'` and `config_path='.'`. They must be launched from the `tdmpc2/` package directory so `config.yaml` resolves. `common.parser.parse_cfg` fills convenience fields (`obs_shape`, `action_dim`, `multitask`, `tasks`, `bin_size`, `seed_steps`, `work_dir`). [TDMPC2-CODE, `train.py`, `evaluate.py`, `config.yaml`]

Defaults that match Table 8 unless `model_size` overrides them:

| Key | Default |
|---|---|
| `horizon` | 3 |
| `iterations` | 6, then code adds `2 * int(action_dim >= 20)` |
| `num_samples` | 512 |
| `num_pi_trajs` | 24 |
| `num_elites` | 64 |
| `num_q` | 5 |
| `num_bins` | 101 |
| `simnorm_dim` | 8 |
| `batch_size` | 256 (parser sets 1024 for multitask) |
| `consistency_coef` / `reward_coef` / `value_coef` | 20 / 0.1 / 0.1 |
| `lr` / `enc_lr_scale` / `grad_clip_norm` / `tau` | `3e-4` / 0.3 / 20 / 0.01 |
| `compile` | true |

`model_size` must be one of `{1, 5, 19, 48, 317}`. Yaml placeholders (`checkpoint: ???`, `model_size: ???`) are filled by Hydra overrides. CUDA is required: both scripts `assert torch.cuda.is_available()`. [TDMPC2-CODE, `train.py`, `evaluate.py`, `config.yaml`]

## 4. Model construction and tensor contract

`TDMPC2.__init__` builds `WorldModel(cfg)` on `cuda:0`. For the released 5M-class single-task setting:

- state observation: `[B, obs_dim]` or time-major `[T, B, obs_dim]` in the update window;
- RGB observation: `[B, C, 64, 64]` after `ShiftAug` + `PixelPreprocess` (`x/255 - 0.5`); the conv encoder **asserts** the last spatial size is 64;
- latent `z`: `[B, latent_dim]` with SimNorm; default `latent_dim=512`, Table 9 317M uses **1376**;
- action `a`: `[B, action_dim]` in `[-1, 1]` after squashing; planning tensors are `[H, num_samples, action_dim]`;
- reward / Q logits: `[B, 101]` per head; ensemble forward is vmapped to `[num_q, B, 101]`;
- policy prior: MLP outputs `[B, 2 * action_dim]` (mean and log std);
- multitask: task embedding dim 96 concatenated on the last axis; `_action_masks[task]` zeros unused action dims.

`WorldModel.Q(..., return_type)`:

- `'all'`: raw ensemble logits for the value loss;
- `'min'`: two-hot decode two random members, then min — used for TD targets;
- `'avg'`: mean of two random members — used for planning and the policy objective.

[TDMPC2-CODE, `tdmpc2.py`, `common/world_model.py`, `common/layers.py`]

## 5. Call graph

```text
tdmpc2/train.py
  -> parse_cfg / set_seed / make_env
  -> TDMPC2(cfg) -> WorldModel
  -> Buffer(cfg)
  -> OfflineTrainer if cfg.multitask else OnlineTrainer
  -> trainer.train()
       OnlineTrainer:
         seed_steps of random actions
         then agent.act -> env.step -> buffer.add
         agent.update(buffer)
       OfflineTrainer:
         sample 545M-scale offline batches (multitask)
         agent.update(buffer)

tdmpc2/evaluate.py
  -> TDMPC2.load(checkpoint)
  -> for each task / episode:
       agent.act(obs, t0=..., task=task_idx)
       env.step; optional imageio mp4 at 15 fps
  -> MT80 score: Meta-World success*100 else return/10

TDMPC2.act
  -> if cfg.mpc: TDMPC2.plan -> _plan (optionally torch.compile)
  -> else: encode + pi mean

TDMPC2._plan
  -> encode obs
  -> roll 24 policy-prior trajectories
  -> MPPI: sample, _estimate_value, elite softmax, update mean/std
  -> Gumbel-softmax elite (train) or mean (eval_mode)

TDMPC2._update
  -> encode obs[1:] as next_z; _td_target
  -> latent rollout zs[0:H], consistency MSE vs next_z
  -> Q all-members, reward logits, optional termination BCE
  -> soft_ce vs two-hot targets
  -> Adam on encoder/dynamics/reward/Qs/task_emb
  -> update_pi on detached zs
  -> soft_update_target_Q (Polyak tau)
```

Environment factories live in `envs/dmcontrol.py`, `envs/metaworld.py`, `envs/maniskill.py`, and `envs/myosuite.py`, selected by `envs.make_env`. There is no `planner.py` or `agent.py` in this tree; planning is a method on `TDMPC2`. [TDMPC2-CODE]

## 6. Paper versus code ledger

| ID | Evidence | Effect | Minimal repair boundary |
|---|---|---|---|
| `TDMPC-GAP-01` | Q ensemble members call `.apply(init.weight_init)` in `common/world_model.py`; helpers live in `common/init.py` | post-paper score drift versus ICLR checkpoints trained before the fix | pin parent commit for table replication; treat this SHA as maintenance |
| `TDMPC-GAP-02` | `self.cfg.iterations += 2*int(cfg.action_dim >= 20)` in `TDMPC2.__init__` | high-dim tasks silently use 8 planning iters | record resolved `iterations` in the run log; do not assume yaml `6` |
| `TDMPC-GAP-03` | `WorldModel.termination` contains `assert task is None` | episodic + multitask termination head is not a supported path | keep `episodic=false` unless a documented single-task episodic env is used |
| `TDMPC-GAP-04` | `compile: true` by default | `torch.compile` on `_update` and `_plan` | disable compile for a first smoke if inductor fails; this is not a paper ablation |
| `TDMPC-GAP-05` | CUDA assert in `train.py` and `evaluate.py` | CPU-only machines cannot run the documented commands | no author CPU path |
| `TDMPC-GAP-06` | `evaluate.py` warns that single-task eval of `mt80`/`mt30` checkpoints is unsupported | a `task=dog-run` eval of an MT80 weight is not a paper protocol | use `task=mt80` or `task=mt30` for multitask checkpoints |
| `TDMPC-GAP-07` | yaml `batch_size: 256`; paper Table 8 says 1024 multitask | parser, not yaml, must apply the multitask batch | log resolved batch size |
| `TDMPC-GAP-08` | no discrete-action encoder | cannot close the paper's open discrete-action problem from this repo | do not invent a discrete wrapper and call it TD-MPC2 |
| `TDMPC-GAP-09` | 317M widths are parser overrides, not `config.yaml` defaults | copying yaml without `model_size=317` trains the 5M-class net | bind `model_size` and print `WorldModel` param count |
| `TDMPC-GAP-10` | Hydra `work_dir` and checkpoint `???` placeholders | copied commands fail without overrides | always pass `checkpoint=` and a writable Hydra output dir |

## 7. Change surfaces for optimization

| Intervention | Primary code surface | Controlled variables to retain |
|---|---|---|
| Decoder-free vs reconstructive latent | `WorldModel` (no decoder exists) | Q heads, SimNorm, discrete regression, planning budget |
| SimNorm group size / temperature | `layers.SimNorm`, `simnorm_dim` | latent dim, encoder, losses |
| Discrete vs MSE reward/value | `num_bins`, `math.soft_ce`, `two_hot_inv` | vmin/vmax, ensemble, `rho` |
| Ensemble size and min-vs-avg | `num_q`, `WorldModel.Q` | target tau, dropout 0.01 |
| Planning horizon and population | `horizon`, `num_samples`, `num_elites`, `num_pi_trajs` | learned dynamics frozen vs joint |
| High-dim extra iterations | `TDMPC2.__init__` heuristic | action dim, temperature 0.5 |
| Policy-only vs MPC | `cfg.mpc` | same checkpoint |
| Visual vs state encoder | `obs=rgb` vs `state`; `layers.enc` | 64x64, random shift pad=3 |
| Multitask embedding / action mask | `_task_emb`, `_action_masks` | offline dataset identity |
| Q init (maintenance) | `common/init.py`, ensemble `.apply` | do not call this a paper mechanism |

Any experiment derived from this map should distinguish **paper-aligned** (ICLR recipe, pre-fix init) from **maintenance-aligned** (this pin). The second is what the public tree actually runs.

## 8. Cosmos3 attachment surface

TD-MPC2 transfers **value-aware latent planning without pixel reconstruction**. On Cosmos3-Nano the compatible surfaces are the **Reasoner** visual/state representation and a latent planner that scores action chunks — not the Generator video decode path and not FD/WAM pixel futures. A hybrid that uses Generator FD/WAM as a baseline is allowed only when labeled as a contrastive control, not as a TD-MPC2 attachment. [TDMPC2-PAPER; Cosmos3-Nano reasoner]

## Sources

- [TDMPC2-CODE] `nicklashansen/tdmpc2@e9f59321933cbc8e11a002b842adc7d4ffae8ff1`.
- [TDMPC2-PAPER] ICLR 2024 / arXiv:2310.16828 for claimed architecture and tables.
- [MBRL-TDMPC2-2024] Foundation identity.
