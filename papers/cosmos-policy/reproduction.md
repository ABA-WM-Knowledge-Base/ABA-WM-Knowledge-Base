---
id: world-model-kb.papers.cosmos-policy.reproduction
title: Cosmos Policy Reproduction State and Experiment Contracts
kind: record
status: maintained
last_updated: 2026-08-14
owners:
  - AIBuildAI world-model group
---

# Cosmos Policy Reproduction State and Experiment Contracts

## Retrieval metadata

**Relevant queries:** Cosmos Policy reproduced, LIBERO eval command, Docker uv run, checkpoint download, VRAM, ALOHA hardware, PolicyEvalConfig, or not attempted.

**Knowledge provided:** documented commands, current non-execution, known blockers, and minimum contracts that would promote a row from documented to executed.

**Related pages:** [`codebase.md`](codebase.md) owns the call graph; [`paper.md`](paper.md) owns reported values; [evaluation methodology](../../foundations/data-and-evaluation/evaluation-methodology.md) owns comparison validity.

## 1. Current execution state

| Surface | Evidence state | Recorded evidence | Permitted claim |
|---|---|---|---|
| Paper identity | source inspected | arXiv:2601.16163 via [P25-COSMOS-POLICY] | Method and tables cited in this entry were read from the paper snapshot. |
| Official repository | source inspected | pinned commit `18a2accadf4e7a3531e56754102af5a24d2316da` | README, configs, and scripts were inspected; no command was run. |
| Hugging Face checkpoints | metadata inspected | model cards for LIBERO, RoboCasa, ALOHA, planning model | Artifacts are advertised; inner SHA not verified locally. |
| T5 embedding caches | documented | `libero_t5_embeddings.pkl` shipped with LIBERO weights | Cache presence is required by `get_action`; not hashed here. |
| Docker inference | not attempted | none | No LIBERO action chunk has been generated here. |
| Benchmark metrics | not attempted | none | 98.5% / 67.1% / 93.6% remain paper-reported. |
| Training | not attempted | none | No optimizer step is local evidence. |
| Predict2.5 cookbook path | documentation inspected | Cookbook HTML | Not treated as paper-table reproduction. |
| ALOHA hardware eval | not reconstructable from public artifacts | 101 private initial states | Table 3 remains paper-only without hardware identity. |

Static inspection is not inference reproduction. Source availability is not checkpoint integrity. No row may be promoted to executed inference or metric reproduction without an immutable run record.

## 2. Reproduction vocabulary

- **Documented:** a pinned paper or repository describes a behavior.
- **Source inspected:** the relevant paper pages or code paths were reconciled.
- **Artifact reachable:** an immutable URL responds and its advertised outer identity is recorded.
- **Artifact verified:** the complete downloaded file has a retained SHA256 and expected archive structure.
- **Executed:** a command completes in a recorded environment with raw artifacts.
- **Metric reproduced:** a pinned checkpoint and protocol yield the declared metric within a predeclared tolerance.
- **Paper result reproduced:** model, data, code, evaluator, sampling, and aggregation identities are sufficiently matched to support the named table or figure.

These terms describe evidence only. They do not prescribe AIBuildAI workflow, task order, permissions, or experiment priority. None of the last three states is claimed here.

## 3. Artifact and environment boundary

Documented training hardware: 64x H100 for LIBERO (40K steps, batch 1920, 48 h), 32x H100 for RoboCasa (45K, batch 800, 48 h), 8x H100 for ALOHA (50K, batch 200, 48 h). Documented inference VRAM: 6.8 / 8.9 / 6.0 GB for direct policy; 10.0 GB serial planning. [P25-COSMOS-POLICY, Appendix A.2, A.4.2; CPOL-CODE]

The Cookbook path clones a different tree (`nvidia-cosmos/cosmos-predict2.5` in-tree `cosmos_policy`). Following it silently changes initialization and is not Table 1-5 reproduction. [CPOL-COOKBOOK]

ALOHA real-robot rows additionally require hardware identity, 25 Hz control, 50-step / 2 s chunks, and the 101-state protocol (30+20+25+26). Public code cannot reconstruct Table 3 without those identities.

## 4. Documented commands, not executed

From the pinned README, after Docker setup in `SETUP.md`:

```text
uv run --extra cu128 --group libero --python 3.10 python
```

Then the `PolicyEvalConfig` + `get_action` snippet with `ckpt_path="nvidia/Cosmos-Policy-LIBERO-Predict2-2B"` and config name `cosmos_predict2_2b_480p_libero__inference_only`. Domain-specific procedures are in `LIBERO.md`, `ROBOCASA.md`, and `ALOHA.md`. Training entry is `cosmos_policy/scripts/train.py`. [CPOL-CODE]

Do not mix the README 5/1/1 denoising split with Appendix A.3.1 table protocol (5 or 10 parallel steps for direct policy; 10/5/5 autoregressive for planning).

## 5. Known blockers

| ID | Blocker | Effect |
|---|---|---|
| `POLICY-CODE-GAP-01` | Predict2.5 Cookbook clone | wrong initialization family for Tables 1-5 |
| `POLICY-CODE-GAP-02` | README 5/1/1 versus paper 5 or 10 steps | copied snippet is not Table 1 protocol |
| `POLICY-CODE-GAP-04` | Hugging Face `ckpt_path` has no inner SHA | hosted ID != evaluated snapshot |
| `POLICY-CODE-GAP-05` | ALOHA hardware and 101-state protocol | Table 3 not reconstructable |
| `POLICY-CODE-GAP-06` | missing T5 pickle | `get_action` blocked |

## 6. Minimum contracts for a future executed record

### 6.1 LIBERO smoke inference

A LIBERO smoke inference becomes `executed` only with: pinned commit, resolved config name, checkpoint revision or file hash, T5 pickle hash, environment lock, one recorded observation, raw `action_return_dict`, `sigma_min`, denoising-step counts, `flip_images` flag, and logs.

### 6.2 Table 1 metric contract

A metric row becomes `metric reproduced` only with 500 trials per suite, three seeds, 6000 trials total, the paper evaluator, and the LIBERO-Predict2-2B identity. Do not average Long-only comparator rows into the full-suite table.

### 6.3 Table 2 / Table 5

Bind 50 human demos per task (not MimicGen 1000), 24 tasks, 50 trials x 3 seeds = 3600, chunk 32 with execute-16, and the named peel-down variant. One-step 66.4% is a separate identity from 5-step 67.1%.

### 6.4 Table 3 and planning

Bind hardware identity, 101 matched initial states, ID/OOD split, dual checkpoints for planning, `N`, majority-mean rule, and full-chunk execution. Report OOD separately from the 93.6 full average.

## 7. Run-record template

```text
Experiment ID:
Timestamp:
Question and predeclared acceptance criterion:
Paper, code, data, checkpoint, T5 cache, and evaluator identities:
Patch identity and rationale:
Environment and hardware:
Input, annotation, preprocessing, and action-contract hashes:
Exact command and resolved configuration:
Seeds, episodes, clips, or rollout IDs:
Baseline and intervention:
Controlled variables:
Raw output/log paths and SHA256:
Metrics, aggregation, and uncertainty:
Failure, root cause, and minimal fix:
Remaining deviation:
Evidence conclusion:
```

No inference run record is registered.

## 8. Training and metric reproducibility boundary

| Regime | Publicly recoverable | Missing for exact reproduction |
|---|---|---|
| LIBERO smoke | Docker `uv` snippet, `get_action`, LIBERO Hub card | T5 pickle hash, inner ckpt SHA, `sigma_min`, step split |
| Table 1 | 500 trials/suite x 3 seeds = 6000 | evaluator, `flip_images`, 5-step parallel decode |
| Table 2 | 50 demos/task, 3600 trials | MimicGen-not-used confirmation, execute-16 |
| Table 3 | 101 matched states, ID/OOD split | **private ALOHA hardware**; not reconstructable |
| Table 4-5 ablations | auxiliary / scratch / peel-down | matching train logs; 1-step 66.4% ≠ 5-step 67.1% |
| Planning N=8 | dual checkpoints, majority mean | 8 H100, 4.9 s, 648 rollouts |
| Cookbook Predict2.5 | documented later path | **out of scope** for Tables 1-5 |

## 9. Acceptance checks that must not be skipped

1. Initialization family is Predict2-2B via `NVlabs/cosmos-policy`, not Predict2.5 Cookbook.
2. README 5/1/1 denoising split is not Table 1 protocol.
3. Table 3 OOD reversal (π0.5 92.5 vs Cosmos Policy 89.3) is preserved.
4. Policy-DROID is a different product and does not inherit 98.5% / 67.1% / 93.6%.
5. No local action chunk has been generated in this KB.

## Sources

[CPOL-CODE; P25-COSMOS-POLICY; CPOL-COOKBOOK]
