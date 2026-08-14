---
id: world-model-kb.papers.diamond.reproduction
title: DIAMOND Reproduction State and Experiment Contracts
kind: record
status: maintained
last_updated: 2026-08-14
owners:
  - AIBuildAI world-model group
---

# DIAMOND Reproduction State and Experiment Contracts

## Retrieval metadata

**Relevant queries:** DIAMOND reproduced, src/play.py --pretrained, src/main.py Breakout, Atari 100k, WorldModelEnv, Hugging Face download, csgo branch, or acceptance criteria.

**Knowledge provided:** source-inspection evidence, all-not-attempted execution state, documented commands from the pinned tree, and contracts for smoke inference versus Table 1.

**Related pages:** [`codebase.md`](codebase.md); [`paper.md`](paper.md); [evaluation methodology](../../foundations/data-and-evaluation/evaluation-methodology.md).

## 1. Current execution state

| Surface | Evidence state | Recorded evidence | Permitted claim |
|---|---|---|---|
| NeurIPS paper identity | source inspected | ar5iv HTML of arXiv:2405.12399; Table 1/4/5/7/8 extracted | Equations and tables in this entry were inspected. |
| Atari `main` repository | source inspected | GitHub tree JSON at `5bcd1599755b4f2fae8e5e079e02f0728e174965`; README and `config/trainer.yaml` fetched | Module map and commands are from that commit. |
| CSGO branch | documented | README `git checkout csgo` | Not merged with Atari scores. |
| Hugging Face `eloialonso/diamond` | metadata inspected | Hub URL named by README | No inner SHA256 registered. |
| `python src/play.py --pretrained` | not attempted | command documented | No local demo video. |
| `python src/main.py` training | not attempted | none | No optimizer step or HNS. |
| Table 1 mean HNS 1.459 | not attempted | paper + `results/data/DIAMOND.json` as reported copy | Paper evidence only. |

Static inspection is not inference. No row may be promoted to executed without an immutable run record.

## 2. Reproduction vocabulary

- **Documented:** a pinned paper or repository describes a behavior.
- **Source inspected:** relevant pages or files were reconciled.
- **Artifact reachable:** an immutable URL responds.
- **Artifact verified:** complete file SHA256 retained.
- **Executed:** a command completes with raw artifacts.
- **Metric reproduced:** pinned checkpoint and protocol yield the declared metric within a predeclared tolerance.
- **Paper result reproduced:** model, data, code, evaluator, and aggregation identities match the named table.

These terms do not prescribe workflow or experiment priority.

## 3. Artifact and environment boundary

README specifies Python 3.10, `pip install -r requirements.txt`, and miniconda. Atari ROMs download with dependencies and constitute a license acknowledgment. `requirements.txt` is not a full lockfile. [DIASRC-CODE-CURRENT]

Paper training profile is 2.9 days per game on RTX 4090 (Table 5). Full 26-game 5-seed Table 1 is outside a laptop smoke envelope. The cheapest documented surface is `src/play.py --pretrained` for one game, which still downloads Hub weights and was **not attempted**.

CSGO weights and code are a different branch. Mixing them into an Atari run invalidates Table 1.

## 4. Released commands: documented, not executed

### 4.1 Clone Atari `main`

```bash
git clone https://github.com/eloialonso/diamond.git
cd diamond
git checkout 5bcd1599755b4f2fae8e5e079e02f0728e174965
conda create -n diamond python=3.10
conda activate diamond
pip install -r requirements.txt
```

### 4.2 Pretrained play (smoke candidate)

```bash
python src/play.py --pretrained
```

Record Hub revision, cached file SHA256, selected game, `num_steps_denoising`, and whether the controller is policy or human (`m`). This is **not** Table 1.

### 4.3 Training one game (paper-aligned entry)

```bash
python src/main.py env.train.id=BreakoutNoFrameskip-v4 common.devices=0
```

Hydra writes `outputs/YYYY-MM-DD/hh-mm-ss/` with `checkpoints/state.pt`, `config/trainer.yaml`, and `dataset/`. Resume:

```bash
./scripts/resume.sh
```

Keep `training.model_free=false`. Do not treat `compile_wm` differences as equivalent without a note.

### 4.4 CSGO qualitative only

```bash
git checkout csgo
python src/play.py
```

Separate run record, branch SHA, no Atari HNS acceptance.

## 5. Minimum smoke contract

**Executed smoke (play):** pinned `main` commit, Hub checkpoint hashed, one game loads, at least 16 imagined frames written, action/controller mode recorded.

**Executed smoke (train):** finite denoiser loss, finite actor-critic loss, `WorldModelEnv` used for AC updates, checkpoint saved. Neither smoke is Table 1.

## 6. Table 1 metric contract

Bind:

- commit `5bcd1599755b4f2fae8e5e079e02f0728e174965`;
- 26 games, 5 seeds, `num_steps_total=100000`;
- `num_steps_denoising=3`, `horizon=15`, `gamma=0.985`;
- sticky-action / ROM preprocessing as in `config/env/atari.yaml`;
- human/random references from paper Table 1;
- mean HNS target `1.459` and IQM `0.641` (prose 1.46 / 0.64);
- predeclared tolerance (for example within reported bootstrap interval, or mean HNS ±0.15 if no CI is reused).

Compare only to world-model-trained Table 1 peers unless Appendix J is explicitly in scope. Do not average CSGO FID into HNS.

## 7. Mechanism reproduction

| Variant | Denoising steps | Imagination | Valid Table 1 claim? |
|---|---|---|---|
| Released default | 3 | `WorldModelEnv` H=15 | candidate |
| 1-step ablation | 1 | same | Table 7 only; single-seed in paper |
| Model-free | n/a | off | not the paper agent |
| CSGO branch play | branch default | qualitative | never |

A transfer claim that "visual details cause HNS" is falsified if a matched-parameter discrete tokenizer matches DIAMOND on Breakout/Asterix/RoadRunner.

## 8. Run-record template

```text
Experiment ID:
Branch (main vs csgo vs ddpm):
Commit SHA:
Config hash (trainer.yaml merged):
Checkpoint / Hub SHA256:
Command:
WM-only vs model_free:
Denoising steps and horizon:
Game, seed, ROM identity:
Metrics (raw return, HNS):
Acceptance:
Evidence conclusion:
```

No run record is registered.

## 9. Identity checklist (must be filled before any promotion)

| Check | Required value | Status |
|---|---|---|
| Paper revision | arXiv:2405.12399 as inspected via ar5iv | source inspected |
| Code commit | `5bcd1599755b4f2fae8e5e079e02f0728e174965` | source inspected |
| Branch | `main` for Table 1; `csgo` only for Appendix M demos | documented |
| Hydra merge hash | dump of resolved `trainer.yaml` + `agent/default.yaml` + `env/atari.yaml` | not recorded |
| ROM identity | Atari ROM hash plus license-accept log | not recorded |
| Hub checkpoint | inner SHA256 of downloaded game weights | not recorded |
| Seeds | five independent seeds for Table 1 | not attempted |
| Sampler | Euler `order=1`, `num_steps_denoising=3` | documented default |
| `training.model_free` | `false` | documented default |
| Compile flag | `training.compile_wm` on or off, recorded | not recorded |

A missing row blocks any claim of paper-result reproduction. Filling the table from documentation alone does not change the **not attempted** execution state.

## 10. Environment and resource envelope

README: Python 3.10, `pip install -r requirements.txt` (210 bytes; not a lockfile). Atari ROM download is a license event. Paper Table 5: **2.9 days per game** on RTX 4090. Full 26-game 5-seed Table 1 is ~377 GPU-days if serialized, before evaluation. The cheapest documented surface is Hub play for one game; it still downloads weights and was **not attempted**. [DIASRC-PAPER, Table 5; DIASRC-CODE-CURRENT, `requirements.txt`]

Do not treat a laptop `debug` or shortened `num_steps_total` as Table 1. A one-game 100k run may be used only as **executed training smoke**, not as mean HNS.

## 11. Acceptance versus non-acceptance

**Accept as Table 1 reproduction** only if all of Section 6 bind, five seeds finish, and mean HNS / IQM land inside the predeclared tolerance versus `1.459` / `0.641`.

**Do not accept** if any of the following occur: `csgo` or `ddpm` branch mixed into Atari; `model_free=true`; 1-step denoising used as the main agent; play-horizon 50 videos cited as HNS; Hub play without training; averaging Appendix M FID into HNS; comparing only to BBF while claiming the world-model-trained SOTA sentence.

**Accept as smoke** under Section 5 without promoting metrics.

## Sources

- [DIASRC-PAPER] protocol and Table 1/7.
- [DIASRC-CODE-CURRENT] `src/main.py`, `src/play.py`, `config/trainer.yaml`.
- [DIASRC-HF-MODEL] pretrained demo.
