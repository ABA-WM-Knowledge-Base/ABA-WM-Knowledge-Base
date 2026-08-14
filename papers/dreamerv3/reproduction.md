---
id: world-model-kb.papers.dreamerv3.reproduction
title: DreamerV3 Reproduction State and Experiment Contracts
kind: record
status: maintained
last_updated: 2026-08-14
owners:
  - AIBuildAI world-model group
---

# DreamerV3 Reproduction State and Experiment Contracts

## Retrieval metadata

**Relevant queries:** DreamerV3 reproduced, Nature 2025, danijar reimplementation, minecraft diamond, configs.yaml, not attempted.

**Knowledge provided:** inspection-only state. Nature tables vs public code. No training or inference executed.

**Related pages:** [`codebase.md`](codebase.md); [`paper.md`](paper.md); [evaluation methodology](../../foundations/data-and-evaluation/evaluation-methodology.md).

## 1. Current execution state

| Surface | Evidence state | Recorded evidence | Permitted claim |
|---|---|---|---|
| Nature article | source inspected | PMC/Nature HTML; protocols and Minecraft prose | Algorithm and protocol inspected. |
| Extended Data Table 1 numbers | not recovered | HTML placeholder "Open in a new tab" | Do not cite invented aggregates. |
| Supplementary task tables | not extracted | not in the inspected HTML | Do not invent per-task scores. |
| arXiv 2301.04104 HTML | conversion failed | ar5iv fatal error | Preprint not used for tables. |
| Public repo | source inspected | tree at `e3f02248693a79dc8b0ebd62c93683888ddaccfe`; `configs.yaml` fetched | Reimplementation map only. |
| `python dreamerv3/main.py` | not attempted | documented | No return curve. |
| Minecraft diamonds | not attempted | Nature: all seeds within 100M | Paper-only. |
| Atari 200M / Atari100k | not attempted | Nature prose only | Not mixed with DIAMOND HNS. |

Static inspection is not execution. Public-code execution would still be a **reimplementation**, not a Nature binary replica.

## 2. Reproduction vocabulary

- **Documented:** a pinned paper or repository describes a behavior.
- **Source inspected:** relevant pages or files were reconciled.
- **Executed:** a command completes with raw artifacts.
- **Metric reproduced:** public-code return within a predeclared tolerance of a **named** Nature number.
- **Paper result reproduced:** requires recovered Nature table cells plus matched protocol. Currently blocked for aggregates.

## 3. Artifact and environment boundary

README: Linux/Mac, Python 3.11+, JAX GPU. Nature: one A100 per agent; Minecraft 100M steps ~9 days on 1 GPU. `debug` shrinks widths and log intervals. Extra env packages are listed in `Dockerfile`, not in a lockfile. `--jax.platform cpu` is for debugging only. Reloading a mismatched checkpoint raises `Too many leaves for PyTreeDef`. [DV3SRC-CODE-CURRENT README]

A few-thousand-step `crafter` or `dummy` run may be **executed smoke** only.

## 4. Commands documented, not executed

```bash
git clone https://github.com/danijar/dreamerv3.git
cd dreamerv3
git checkout e3f02248693a79dc8b0ebd62c93683888ddaccfe
pip install -U -r requirements.txt
python dreamerv3/main.py --logdir ~/logdir/dreamer/{timestamp} \
  --configs crafter --run.train_ratio 32
```

Paper-facing examples: `--configs atari --task atari_pong`; `--configs atari100k --task atari100k_pong`; `--configs minecraft --task minecraft_diamond`; `--configs dmc_proprio`; `--configs dmc_vision`; `--configs procgen`; `--configs dmlab`; `--configs bsuite`. Stack blocks: `--configs crafter size50m`. Continue by repeating the same `--logdir`. View: `python -m scope.viewer --basedir ~/logdir --port 8000`. JSONL scalars are written beside Scope summaries.

## 5. Minimum smoke contract

Pinned commit; non-debug config; `dummy` or `crafter` for a few thousand steps; finite losses; JSONL written; disclaimer recorded (reimplementation, unrelated to Google/DeepMind). Not Minecraft diamonds, not Nature Extended Data Table 1.

## 6. Nature result contract

Bind when claiming a domain: sticky Atari 57 @ 200M; Atari100k original SimPLe settings; ProcGen hard 50M; DMLab 100M vs baselines at 1B; Control Suite 1M; BSuite required seeds (10); Minecraft 100M, item list, `break_speed` analog, episode length 36000. Report seed count. Label public-code runs as **reimplementation**.

Until Extended Data Table 1 numeric cells are recovered from PDF/supplement, **no aggregate-score reproduction claim is allowed**.

## 7. Identity checklist

| Check | Required value | Status |
|---|---|---|
| Title | *Mastering diverse control tasks through world models* | canonical |
| DOI | 10.1038/s41586-025-08744-2 | documented |
| Preprint | arXiv:2301.04104 old title only | not used for tables |
| Public commit | `e3f02248693a79dc8b0ebd62c93683888ddaccfe` | source inspected |
| Disclaimer | reimplementation, unrelated to Google/DeepMind | documented |
| Config | no `debug` for paper-facing runs | not executed |
| Extended Data Table 1 | numeric cells | **not recovered** |
| Not DIAMOND | Atari100k HNS 1.459 out of scope | documented |

## 8. Run-record template

```text
Experiment ID:
Nature vs public reimplementation:
Commit:
Config blocks (must not include debug):
Task:
Steps / train_ratio:
Metrics:
Deviation from Nature protocol:
Evidence conclusion:
```

No run record is registered.

## 9. Non-goals for this KB session

No training, no JAX run, no Minecraft. Do not scrape broken ar5iv HTML. Do not invent Extended Data Table 1. Do not call the public tree Google-internal.

## 10. Training and metric reproducibility boundary

| Regime | Publicly recoverable | Missing for exact Nature reproduction |
|---|---|---|
| Crafter / dummy smoke | `main.py`, `configs.yaml`, `requirements.txt` | lockfile, GPU SKU, Scope log hashes |
| Atari 57 @ 200M | sticky/repeat/96x96 flags | Nature binaries, seeds, Extended Data Table 1 cells |
| Atari100k | `atari100k` block, 26-game SimPLe settings | sticky False / 64x64 / 1 env confirmation vs Nature PDF |
| Minecraft diamonds | `break_speed: 100`, length 36000, 100M steps | MineRL stack, all-seed logs, VPT unmatched compute |
| DMC proprio/vision | `dmc.py`, 1M-step budget | Nature table cells |
| ProcGen / DMLab / BSuite | wrappers + config blocks | 16 hard / 30 tasks / 10-seed lists |
| Public reimplementation | README disclaimer | internal Google/DeepMind trainer |

Any numeric aggregate claim is blocked until Extended Data Table 1 cells are recovered from PDF/supplement. A public-code return curve is a **reimplementation metric**, not a Nature replica.

## 11. Acceptance checks that must not be skipped

1. Title is *Mastering diverse control tasks through world models*; arXiv old title is preprint-only.
2. `run.debug` is false for any paper-facing logdir.
3. Atari 200M sticky protocol is not mixed with Atari100k or DIAMOND HNS 1.459.
4. Minecraft diamond claim records seed count and 100M budget.
5. Run records copy the README disclaimer: unrelated to Google or DeepMind.

## Sources

- [DV3SRC-PAPER-NATURE], [DV3SRC-PAPER-ARXIV], [DV3SRC-CODE-CURRENT].
