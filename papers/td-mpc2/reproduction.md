---
id: world-model-kb.papers.td-mpc2.reproduction
title: TD-MPC2 Reproduction State and Experiment Contracts
kind: record
status: maintained
last_updated: 2026-08-14
owners:
  - AIBuildAI world-model group
---

# TD-MPC2 Reproduction State and Experiment Contracts

## Retrieval metadata

**Relevant queries:** TD-MPC2 reproduced, evaluate.py, train.py dog-run, mt80-48M checkpoint, 104-task sweep, 317M multitask, Q init fix, Hydra config, or acceptance criteria.

**Knowledge provided:** immutable source-inspection evidence, current local execution boundaries, released reference commands, known blockers, and minimum contracts for evaluation and training. No training or inference was run for this entry.

**Related pages:** [`codebase.md`](codebase.md) owns the released call graph and gaps; [`paper.md`](paper.md) owns reported values; [evaluation methodology](../../foundations/data-and-evaluation/evaluation-methodology.md) owns comparison validity; [Cosmos3-Nano reproduction](../../models/cosmos3-nano/reproduction.md) is a separate model's execution registry.

## 1. Current execution state

| Surface | Evidence state | Recorded evidence | Permitted claim |
|---|---|---|---|
| ICLR 2024 / arXiv:2310.16828 identity | source inspected | [TDMPC2-PAPER]; [MBRL-TDMPC2-2024] | Equations, tables, and compute numbers in this entry were inspected from the paper. |
| Official repository identity | source inspected | clean pin at `e9f59321933cbc8e11a002b842adc7d4ffae8ff1` (2026-07-13) | The released implementation graph and static gaps were inspected. |
| Q-ensemble init fix | source inspected | `common/init.py` helpers applied per ensemble MLP in `common/world_model.py` | Maintenance, not paper evidence; no A/B score is local. |
| Checkpoint catalog | metadata inspected | README / release notes describe single-task and mt30/mt80 weights | No `.pt` file has been downloaded or hashed. |
| `evaluate.py` smoke | **not attempted** | none | No episode return is local evidence. |
| MT80 / 317M eval | **not attempted** | none | Table 1 scores remain paper evidence. |
| 104-task aggregate | **not attempted** | none | Single-hparam claim unverified locally. |
| `train.py` online or offline | **not attempted** | none | No optimizer step, loss curve, or checkpoint is local evidence. |
| Visual 64x64 eval | **not attempted** | none | DrQ-v2 / DreamerV3 comparison remains paper evidence. |
| Few-shot 19M protocol | **not attempted** | none | 2x-at-20k-steps remains paper evidence. |

Static inspection is not inference reproduction. Source availability is not checkpoint integrity. No row may be promoted to executed inference or metric reproduction without an immutable run record.

## 2. Reproduction vocabulary

- **Documented:** a pinned paper or repository describes a behavior.
- **Source inspected:** the relevant paper pages or code paths were reconciled.
- **Artifact reachable:** an immutable URL responds and its advertised outer identity is recorded.
- **Artifact verified:** the complete downloaded file has a retained SHA256.
- **Executed:** a command completes in a recorded environment with raw artifacts.
- **Metric reproduced:** a pinned checkpoint and protocol yield the declared metric within a predeclared tolerance.
- **Paper result reproduced:** model, data, code, evaluator, planning budget, and aggregation identities are sufficiently matched to support the named table.

These terms describe evidence only. They do not prescribe workflow, task order, or experiment priority.

## 3. Artifact and environment boundary

Commands assume a CUDA GPU: `train.py` and `evaluate.py` both `assert torch.cuda.is_available()`. Default `compile: true` enables `torch.compile` on `_update` and `_plan`. Single-task replay is documented at **12 GB** RAM; the 80-task offline dataset at **128 GB**; 317M training at **24 GB** GPU memory. These are paper-reported envelopes, not measurements from this KB. [TDMPC2-PAPER; TDMPC2-CODE]

Domain extras (DMControl, Meta-World, ManiSkill, MyoSuite) are separate installs. Exact simulator versions are not locked in a single author-provided lockfile covering all four suites. A replication must record the resolved environment.

Hydra launches must run from the `tdmpc2/` directory so `config.yaml` resolves. Placeholders such as `checkpoint: ???` and `model_size: ???` require CLI overrides.

## 4. Released commands: documented, not executed

### 4.1 Clone and pin

```bash
git clone https://github.com/nicklashansen/tdmpc2.git
cd tdmpc2
git checkout e9f59321933cbc8e11a002b842adc7d4ffae8ff1
# install per README; record a resolved lock externally
cd tdmpc2
```

For **strict ICLR table replication**, also record the parent commit before the Q-ensemble init fix and compare scores. The pin used here is **maintenance-aligned**. [TDMPC2-CODE, `TDMPC-GAP-01`]

### 4.2 Multitask evaluation (documented)

```bash
python evaluate.py task=mt80 model_size=48 checkpoint=/path/to/mt80-48M.pt
```

Related documented variants at the same pin include `task=mt30 model_size=317 checkpoint=/path/to/mt30-317M.pt`. Single-task evaluation of an `mt80`/`mt30` checkpoint is **unsupported** by `evaluate.py` and prints a warning. [TDMPC2-CODE, `evaluate.py`]

**Executed** smoke (not yet run): CUDA visible; checkpoint path exists; model loads; one episode returns a finite scalar.

**Metric reproduced:** mean normalized MT80 score within a predeclared epsilon of Table 1 for that size (48M → 68.0; 317M → 70.6) with the paper’s episode count and scoring (Meta-World success×100, DMControl return/10). [TDMPC2-PAPER, Table 1]

### 4.3 Single-task evaluation (documented)

```bash
python evaluate.py task=dog-run checkpoint=/path/to/dog-1.pt save_video=true
```

Videos are written under Hydra `work_dir/videos` at 15 fps when `save_video=true`. Default `eval_episodes` is 10. [TDMPC2-CODE, `evaluate.py`, `config.yaml`]

### 4.4 Single-task training (documented, resource intensive)

```bash
python train.py task=dog-run steps=7000000
```

Default yaml `steps` is 10M; the README example uses 7M for `dog-run`. `OnlineTrainer` collects seed random steps, then interleaves `agent.act` / `agent.update`. Do not claim a 104-task result from one task. [TDMPC2-CODE, `train.py`, `trainer/online_trainer.py`]

### 4.5 Multitask training (documented, out of local scope unless clustered)

```bash
python train.py task=mt80 model_size=48
python train.py task=mt30 model_size=317
```

`train.py` selects `OfflineTrainer` when `cfg.multitask` is set. This path expects the 80-task / 545M-transition dataset. Full 317M training is outside a laptop envelope even before license and data issues. [TDMPC2-PAPER, Table 1; TDMPC2-CODE, `train.py`]

## 5. Minimum evaluation contract

### 5.1 Identity

Record:

- git commit (paper-aligned vs `e9f5932…` maintenance);
- checkpoint filename, SHA256, and whether it is single-task, mt30, or mt80;
- resolved Hydra config (horizon, iterations after the `|A|>=20` bump, `num_q`, `model_size`, `obs`, `mpc`, `compile`);
- env suite versions and wrappers (`envs/dmcontrol.py`, `metaworld.py`, `maniskill.py`, `myosuite.py`);
- `eval_episodes`, seed, CUDA device, PyTorch/CUDA versions;
- planning vs policy-only (`mpc` flag).

### 5.2 Outputs

Retain stdout/stderr, per-task return and success, normalized aggregate if multitask, optional mp4 hashes, wall time, and peak GPU memory.

### 5.3 Acceptance

An evaluation is **executed** only when a pinned checkpoint loads, the documented Hydra command completes, and raw logs are retained. It is **not** a Table 1 reproduction until scoring, episode count, and checkpoint identity match. It is **not** a 104-task result.

## 6. Table 1 and 104-task contracts

For a protocol-aligned MT80 reconstruction:

1. use `task=mt80` with the matching `model_size` in `{1,5,19,48,317}`;
2. bind checkpoint hash to the size row (1M 16.0 / 5M 49.5 / 19M 57.1 / 48M 68.0 / 317M 70.6);
3. preserve the released aggregator (MW success×100, DMC return/10);
4. record GPU-days only if retraining; eval-only runs must not quote Table 1 GPU-days as local compute;
5. if using this pin, annotate `TDMPC-GAP-01` (Q init).

For the 104-task single-hparam claim, every task must use Table 8 defaults (H=3, 6 planning iters plus the high-dim bump, population 512, 24 prior, 64 elites, 5 Q, SimNorm V=8, batch 256, 101 bins). Per-task yaml edits falsify the “one hparam set” claim even if scores look good. [TDMPC2-PAPER, Table 8]

## 7. Mechanism reproduction

The minimum causal experiment is not “TD-MPC2 gets a high return.” Compare under matched backbone, data, and optimizer:

| Variant | Dynamics | Critic | Planner |
|---|---|---|---|
| Policy-only | trained | trained | `mpc=false` |
| MPC released | decoder-free + SimNorm | 101-bin ensemble | Table 8 |
| No SimNorm | same MLPs, identity output | same | Table 8 |
| MSE critic | same | scalar MSE | Table 8 |
| Paper-aligned init | same | pre-fix Q init | Table 8 |

Measure return, success, grad_norm, Q range, and planning-vs-realized return. A transfer claim is falsified if MPC improves predicted value without realized return, or if removing SimNorm does not change stability.

## 8. Training reproducibility boundary

| Regime | Publicly recoverable | Missing for exact reproduction |
|---|---|---|
| Single-task online (e.g. dog-run) | architecture, yaml, trainers, env wrappers | full dependency lock, seeds across 104 tasks, paper-era Q init |
| Visual 10 DMC | conv encoder + ShiftAug | exact visual wrapper versions, paper seeds |
| MT80 offline | OfflineTrainer path, model_size grid | 545M-transition archive hash, 128 GB RAM host, 240 specialist provenance |
| 317M | Table 9 widths, 8 Q | 24 GB GPU run, inner checkpoint hashes until downloaded |
| Few-shot 19M / 70+10 | protocol in paper | held-out task list binding, 20k-step checkpoints |
| Discrete actions | stated as open | no code path |

## 9. Run-record template

```text
Experiment ID:
Timestamp:
Question and predeclared acceptance criterion:
Paper, code, data, and checkpoint identities:
Paper-aligned vs maintenance (Q init) pin:
Resolved Hydra config (including iterations after |A| bump):
Environment and hardware:
Exact command:
Seeds, tasks, episode returns / successes:
Normalized aggregate vs Table 1:
Failure, root cause, and minimal fix:
Remaining deviation:
Evidence conclusion:
```

No inference or training run record is registered. When one exists, store immutable artifacts outside this KB or in a declared artifact store and register the summary through [`sources.yaml`](sources.yaml).

## Sources

- [TDMPC2-PAPER] protocols, metrics, compute, and limitations.
- [TDMPC2-CODE] commands, configs, trainers, and maintenance init.
- [MBRL-TDMPC2-2024] Foundation identity.
