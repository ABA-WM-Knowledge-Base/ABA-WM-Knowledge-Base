---
id: world-model-kb.papers.lapa.reproduction
title: LAPA Reproduction State and Experiment Contracts
kind: record
status: maintained
last_updated: 2026-08-14
owners:
  - AIBuildAI world-model group
---

# LAPA Reproduction State and Experiment Contracts

## Retrieval metadata

**Relevant queries:** LAPA reproduced, latent_pretraining.inference, LAPA7B-openx, finetune_real, SIMPLER lapa_bridge, not attempted.

**Knowledge provided:** inspection-only state, documented commands, Hub file list. No training or inference executed.

**Related pages:** [`codebase.md`](codebase.md); [`paper.md`](paper.md); [evaluation methodology](../../foundations/data-and-evaluation/evaluation-methodology.md).

## 1. Current execution state

| Surface | Evidence state | Recorded evidence | Permitted claim |
|---|---|---|---|
| ICLR paper | source inspected | ar5iv HTML of arXiv:2410.11758; Tables 1-2 extracted | Numbers inspected. |
| GitHub | source inspected | recursive tree at `46aca51d7faebcec02d7d323bbb3820c2df07bc6`; 41 LAPA-owned blobs | Scripts and byte sizes are real. |
| [LAPA-HF] | metadata inspected | tokenizer.model, vqgan, params, laq_openx.pt named in README | Inner hashes not registered. |
| LWM backbone | documented | [LAPA-LWM] required to retrain Stage 2 | Not fetched. |
| `python -m latent_pretraining.inference` | not attempted | documented | No latent codes generated. |
| Stage 3 deploy | not attempted | documented | No robot actions. |
| LAQ `train_sthv2.py` | not attempted | documented | No codebook. |
| Table 1 Language Table | not attempted | paper-only | Not reproduced. |
| Table 2 real-world | not attempted | paper-only | 50.1 AVG not reproduced. |
| SIMPLER | not attempted | vendored scripts present | Not reproduced. |

Static inspection is not inference. Latent inference is not joint control. No row may be promoted without an immutable run record.

## 2. Reproduction vocabulary

- **Documented:** a pinned paper or repository describes a behavior.
- **Source inspected:** relevant pages or files were reconciled.
- **Artifact reachable:** an immutable URL responds.
- **Artifact verified:** complete file SHA256 retained.
- **Executed:** a command completes with raw artifacts.
- **Metric reproduced:** pinned checkpoint and protocol yield the declared metric within a predeclared tolerance.
- **Paper result reproduced:** model, data, code, evaluator, and aggregation identities match the named table.

## 3. Artifact and environment boundary

Python 3.10. Real finetune: 4x80GB A100 (`--mesh_dim` second index = GPU count). Open-X latent pretrain: 8xH100 ~34 h; authors say ~70K steps at batch 256 can be enough for decent finetune. SIMPLER needs extra SimplerEnv dependencies from the vendored tree. `requirements.txt` is not a lockfile. [LAPA-CODE]

Do not record workstation filesystem locations in this KB. Hash Hub files after download. Cite the bundle as [LAPA-HF] / `LAPA7B-openx` in run records; do not paste the hyphenated Hub slug into KB prose.

## 4. Commands documented, not executed

```bash
git clone https://github.com/LatentActionPretraining/LAPA.git
cd LAPA
git checkout 46aca51d7faebcec02d7d323bbb3820c2df07bc6
conda create -n lapa python=3.10 -y
conda activate lapa
pip install -r requirements.txt
mkdir lapa_checkpoints && cd lapa_checkpoints
# download tokenizer.model, vqgan, params from [LAPA-HF]
cd ..
python -m latent_pretraining.inference
```

Stage 3:

```bash
python data/finetune_preprocess.py --input_path "..." \
  --output_filename data/real_finetune.jsonl --csv_filename data/real_finetune.csv
./scripts/finetune_real.sh
python -m latent_pretraining.deploy \
  --load_checkpoint "params::..." --action_scale_file data/real_finetune.csv
```

LAQ: `conda create -n laq python=3.10`; `cd laq && pip install -e .`; `accelerate launch train_sthv2.py`; `python inference_sthv2.py`. Stage 2 retrain: LWM under `lwm_checkpoints`, jsonl under `data/`, `./scripts/latent_pretrain_openx.sh`. SIMPLER: `./scripts/finetune_simpler.sh` then `SimplerEnv/scripts/lapa_bridge.sh`.

## 5. Minimum smoke contract

Pinned commit; hashed [LAPA-HF] files; `inference` emits a latent in alphabet `8^4`; instruction and image recorded. **Not** Table 2 (no joints).

## 6. Table contracts

**Table 1:** average success % ± SE; 50 rollouts per task category (250 per model per table in appendix); name the split (in-domain 1k, cross-task 7k, cross-env 1k). ActionVLA cells must remain in the comparison.

**Table 2:** 54 rollouts (3 tasks x 3 generalization types x 6), matched object poses, partial success, Open-X vs Bridge vs human pretrain named separately. Win-rate protocol: alternate models, identical inits (Fig. 11); 65.4% excluding ties.

**SIMPLER:** 4 WidowX tasks, 100 finetune trajectories, 24 eval rollouts/task. Do not mix with Franka Table 2.

## 7. Identity checklist

| Check | Required value | Status |
|---|---|---|
| Paper | arXiv:2410.11758 ICLR 2025 | source inspected |
| Commit | `46aca51d7faebcec02d7d323bbb3820c2df07bc6` | source inspected |
| Hub citation | [LAPA-HF] / `LAPA7B-openx` | documented |
| Files | tokenizer.model, vqgan, params hashed | not recorded |
| LAQ | `laq_openx.pt` if Stage 1 in scope | not recorded |
| LWM | [LAPA-LWM] if retraining Stage 2 | not fetched |
| Stage | inference vs deploy | not executed |
| Not Genie | different paper class | documented |

## 8. Run-record template

```text
Experiment ID:
Commit:
[LAPA-HF] file SHA256:
Stage (LAQ | latent VLA | deploy):
Embodiment / csv scale file:
Metrics:
Evidence conclusion:
```

No run record is registered.

## 9. Non-goals for this KB session

No training, no inference, no robot. Hub latents must not be scored as Table 2. Decoder Fig. 7 is qualitative. Do not attach LAQ to Reasoner.

## 10. Training and metric reproducibility boundary

| Regime | Publicly recoverable | Missing for exact reproduction |
|---|---|---|
| Stage 2 Hub smoke | commit, `inference.py`, named Hub files | inner SHA256, tokenizer/vqgan/params hashes |
| Stage 3 real deploy | `finetune_preprocess.py`, `finetune_real.sh`, `deploy.py` | robot identity, csv scale hashes, 54-rollout poses |
| Language Table Table 1 | split sizes (1k / 7k / 1k), 50 rollouts/category | env revision, ActionVLA checkpoints, SE aggregation code |
| Real-world Table 2 | n=54 protocol, Fig. 11 paired wins | hardware, object-pose logs, human rater instructions |
| SIMPLER WidowX | `lapa_bridge.sh`, 100 traj / 24 eval | SimplerEnv pin vs vendored tree, success judge |
| LAQ SSv2 | `train_sthv2.py` | folder layout, NSVQ seeds, `8^4` dump hashes |
| Stage 2 retrain | `latent_pretrain_openx.sh`, [LAPA-LWM] | Open-X jsonl identity, 8xH100 34 h logs |

A Table 2 claim remains blocked until Stage 3 joints, matched poses, and the paired protocol are bound. A Hub `inference` run that emits `8^4` codes is only Stage 2 smoke.

## 11. Acceptance checks that must not be skipped

1. Hub citation is [LAPA-HF] / `LAPA7B-openx` — never a hyphenated slug in KB prose.
2. Latent alphabet recorded as `8^4` before any joint metric.
3. ActionVLA Language Table cells remain in the comparison (Table 1 does not crown LAPA).
4. SIMPLER WidowX is not merged into Franka Table 2.
5. Decoder Fig. 7 is labeled qualitative.

## Sources

- [LAPA-PAPER], [LAPA-CODE], [LAPA-HF], [LAPA-LWM].
