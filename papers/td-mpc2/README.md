---
id: world-model-kb.papers.td-mpc2
title: TD-MPC2 Paper Knowledge Entry
kind: paper
status: maintained
last_updated: 2026-08-14
owners:
  - AIBuildAI world-model group
---

# TD-MPC2 Paper Knowledge Entry

## Retrieval metadata

**Relevant queries:** TD-MPC2, temporal difference MPC, decoder-free latent world model, SimNorm, MPPI, 104 tasks one hparam, 317M MT80, 545M transitions, Q ensemble, discrete log-space regression, or few-shot 19M.

**Knowledge provided:** the paper's latent-planning interface, shared hyperparameter contract, scale and domain evidence, released implementation boundary including post-paper Q init, reproduction state, and falsifiable transfers toward Cosmos3-Nano Reasoner latent planning — not Generator pixels.

**Related pages:** [Model-based RL](../../foundations/decision-making/model-based-rl.md) owns the generic loop; [planning and control](../../foundations/decision-making/planning-and-control.md) owns search versus policy; [latent world models](../../foundations/representations/latent-world-model.md) owns decoder-free representation; [forward dynamics](../../foundations/problem-formulation/forward-dynamics.md) owns action-conditioned prediction; [Cosmos3-Nano reasoner](../../models/cosmos3-nano/reasoner.md) owns the target attachment; [Cosmos3-Nano action modeling](../../models/cosmos3-nano/action-modeling.md) owns FD/WAM contrast.

Foundation bibliographic identity: [MBRL-TDMPC2-2024] for *TD-MPC2: Scalable, Robust World Models for Continuous Control* (ICLR 2024, `arXiv:2310.16828`). This entry extends with code pins and transfer hypotheses without duplicating that Foundation ID. [TDMPC2-PAPER; TDMPC2-CODE]

## Identity and revision boundary

| Field | Canonical value | Consequence |
|---|---|---|
| Work | *TD-MPC2: Scalable, Robust World Models for Continuous Control* | ICLR 2024 is the scientific anchor. |
| Paper snapshot | `arXiv:2310.16828` / ICLR 2024 | Tables 1, 8, 9 and the 104-task claim refer to this artifact. [TDMPC2-PAPER] |
| Foundation ID | [MBRL-TDMPC2-2024] | Cross-cite; not in [`sources.yaml`](sources.yaml). |
| Official code | `nicklashansen/tdmpc2@e9f59321933cbc8e11a002b842adc7d4ffae8ff1` | Pin dated **2026-07-13**. [TDMPC2-CODE] |
| Maintenance delta | Q-ensemble init via `tdmpc2/common/init.py` applied in `world_model.py` | **Not** paper evidence. Strict table replication needs the parent commit or a recorded delta. |
| Checkpoints | public single-task and mt30/mt80 `.pt` files | Must be hashed on download; not verified here. |

The paper and the pin have the same architecture, but the pin is newer than ICLR training. Paper numbers and public-eval numbers from this SHA must be retrieved separately. [TDMPC2-PAPER; TDMPC2-CODE]

## Operational model boundary

TD-MPC2 is a **decoder-free implicit latent world model** coupled to **MPPI** at decision time. It predicts latent transitions, discrete rewards, and an ensemble of discrete Q-values without reconstructing observations:

```text
z_t = h(o_t)           # SimNorm V=8
plan a_{t:t+H-1} in z  # H=3, 512 samples, 24 policy prior, 64 elites
execute a_t
```

It is not a pixel Generator, not an FD/WAM video model, and not a discrete-action agent. Transfers target **Reasoner / latent planning** on Cosmos3-Nano. Generator FD/WAM appears only as a latency baseline. [TDMPC2-PAPER, Sec. 3, Table 8]

| Surface | Inputs | Output or decision | Evidence boundary |
|---|---|---|---|
| Single-task online RL | state or 64x64 RGB, continuous action | first action of an H=3 plan | 104 tasks, one yaml; not per-task optimality |
| Visual RL | 64x64 + random shift | same planner | comparable to DrQ-v2/DreamerV3 on 10 DMC tasks |
| Multitask offline | 545M transitions from 240 specialists | one agent, 80 tasks | Table 1 scores; 128 GB dataset RAM |
| Few-shot | 19M pretrained on 70 tasks | finetune 10 held-out | 2x scratch at 20k steps |
| Policy-only (`mpc=false`) | same model | `pi(z)` mean | ablation, not the main claim |
| Discrete actions | — | — | left open |

## Documented commands (not executed)

```bash
python evaluate.py task=mt80 model_size=48 checkpoint=/path/to/mt80-48M.pt
python evaluate.py task=dog-run checkpoint=/path/to/dog-1.pt save_video=true
python train.py task=dog-run steps=7000000
```

Launch from the `tdmpc2/` Hydra directory. CUDA is required. Multitask checkpoints must be evaluated with `task=mt80` or `task=mt30`, not a single-task name. [`reproduction.md`](reproduction.md)

## Knowledge map

| Question | Canonical page |
|---|---|
| Prediction equation, architecture, data, tables, ablations, limits? | [`paper.md`](paper.md) |
| Which released files implement each mechanism, and where does the pin diverge from ICLR? | [`codebase.md`](codebase.md) |
| What has been inspected or executed, and what would establish reproduction? | [`reproduction.md`](reproduction.md) |
| Which mechanisms may improve another model, where do they attach, and what falsifies each transfer? | [`optimization-transfer.md`](optimization-transfer.md) |
| Which paper and code identities support the entry? | [`sources.yaml`](sources.yaml) |

These associations support retrieval and synthesis. They do not define Agent selection, task sequence, or experiment priority.

## High-value evidence anchors

- **One hyperparameter set on 104 tasks** spanning DMControl, Meta-World, ManiSkill2, and MyoSuite. Shared Table 8: `H=3`, 6 planning iters (+2 if `|A|>=20`), population 512, 24 policy prior, 64 elites, 5 Q-functions, SimNorm `V=8` `tau=1`, batch 256/1024, 101-bin log-space regression. Discrete actions remain open. [TDMPC2-PAPER, Abstract, Table 8]
- **MT80 scale table:** 1M 3.7 GPU-days score 16.0; 5M 4.2d 49.5; 19M 5.3d 57.1; 48M 12d 68.0; 317M 33d 70.6. The 48M→317M gain is small relative to compute. [TDMPC2-PAPER, Table 1]
- **317M widths:** encoder dim 4096, MLP 4096, latent 1376, 5 encoder layers, 8 Q-functions. [TDMPC2-PAPER, Table 9]
- **5M capacity split:** encoder 167,936; dynamics 843,264; Q 3,156,985; total ~5.39M — the critic dominates. [TDMPC2-PAPER, architecture tables]
- **Offline multitask data:** 545M transitions from 240 single-task agents; 12 GB RAM single-task vs 128 GB for the 80-task dataset; 317M train needs 24 GB GPU. [TDMPC2-PAPER, Sec. 4]
- **Few-shot:** 19M on 70 tasks, finetune 10 held-out, **2x** scratch at 20k steps. [TDMPC2-PAPER, Sec. 4]
- **Visual RL:** conv encoder 64x64 + random shift, comparable to DrQ-v2/DreamerV3 on 10 DMC tasks; still decoder-free. [TDMPC2-PAPER, Sec. 4]
- **Stability:** SimNorm is essential; original TD-MPC had exploding gradients; adding a decoder is not part of the main recipe. [TDMPC2-PAPER, Sec. 3]
- **Code pin:** `e9f5932…` (2026-07-13) fixes Q-ensemble initialization. Record as maintenance. [`codebase.md`](codebase.md)
- **Execution:** all training and inference **not attempted**. [`reproduction.md`](reproduction.md)

## Limits that change retrieval

- The 104-task claim is **online specialists with one yaml**; the 80-task claim is **one offline agent**. Do not merge them. [TDMPC2-PAPER, Sec. 4]
- Table 1 GPU-days are training cost, not eval cost. An `evaluate.py` run must not quote 33 GPU-days.
- `evaluate.py` refuses single-task eval of `mt80`/`mt30` checkpoints. [`codebase.md`](codebase.md) `TDMPC-GAP-06`
- CUDA is required; `compile: true` is a default, not a paper ablation.
- Memory envelopes (12 GB / 128 GB / 24 GB GPU) are paper-reported, not local measurements. [TDMPC2-PAPER]
- Transfers attach to **Reasoner / latent planning**, never to Generator pixels. [`optimization-transfer.md`](optimization-transfer.md)

## Sources

Source identities and revision pins are maintained in [`sources.yaml`](sources.yaml). Claim-level locators remain in the owning pages. Foundation: [MBRL-TDMPC2-2024].
