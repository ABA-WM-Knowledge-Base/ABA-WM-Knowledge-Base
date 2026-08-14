---
id: world-model-kb.papers.ivideogpt.optimization-transfer
title: iVideoGPT Transferable Optimization Knowledge
kind: guide
status: maintained
last_updated: 2026-08-14
owners:
  - AIBuildAI world-model group
---

# iVideoGPT Transferable Optimization Knowledge

## Retrieval metadata

**Relevant queries:** transfer iVideoGPT, compressive VQ, AR world model, action tokens, OXE mixture, VP2, MBPO, Cosmos3 Generator FD/WAM, not RLVR-World.

**Knowledge provided:** ten falsifiable hypotheses attached to Cosmos3 Generator FD/WAM, not Reasoner.

**Related pages:** [`paper.md`](paper.md); [autoregressive modeling](../../foundations/learning-objectives/autoregressive-modeling.md); [Cosmos3-Nano action modeling](../../models/cosmos3-nano/action-modeling.md).

## 1. Transfer discipline

iVideoGPT supports **context-conditioned future tokens**, **unified AR of video/action/reward**, and **checkpoint-isolated conditioning**. Attach on Generator FD/WAM token or latent paths. Bind any baseline to the same Hub name (`act-free`, `goal-cond`, `256`, medium). Do not treat RLVR-World 2025 as iVideoGPT evidence.

## 2. Intervention matrix

| ID | Target failure | Mechanism | Attachment | Evidence | Risk |
|---|---|---|---|---|---|
| `IVIDEO-XFER-01` | AR context overflow | compressive conditional VQ | visual tokenizer | Tables 7-8 | contact loss |
| `IVIDEO-XFER-02` | separate reward net | reward in AR / symlog | WAM tokens | MBRL App. A.5 | sparse quantization |
| `IVIDEO-XFER-03` | weak action cond | act-cond finetune | FD action tokens | BAIR FVD 75.0->60.8 | embodiment semantics |
| `IVIDEO-XFER-04` | planning disjoint | goal-cond tokens | goal interface | oxe-64-goal-cond | goal shortcut |
| `IVIDEO-XFER-05` | short context | 256-res / longer context | sequence budget | oxe-256 | compute |
| `IVIDEO-XFER-06` | small AR underfits OXE | medium 436M | backbone width | Table 2 | cost |
| `IVIDEO-XFER-07` | open-loop drift | AR rollout training | horizon curriculum | VP2 open-slide fail | exposure bias |
| `IVIDEO-XFER-08` | passive pretrain unused | act-free then act-cond | two-stage schedule | 1000-traj FVD 82.3 | negative transfer |
| `IVIDEO-XFER-09` | naive 16x16 tokens OOM | keep compressive bottleneck | tokenizer | Table 7 OOM | over-compression |
| `IVIDEO-XFER-10` | checkpoint mix-up | isolate cond modes | eval configs | README names; RLVR split | false SOTA |

## 3. `IVIDEO-XFER-01`: compressive conditional tokenization

**Source mechanism.** Future VQ codes condition on context frames via multi-scale cross-attention. Generation **1.11 s** versus **22.5 s** for independent `16 x 16` tokens (4090, bs=1). Train: compressive 2.62 it/s and 22.3 GB versus `4 x 4` at 3.10 it/s and 10.6 GB; `16 x 16` OOM at batch 16 on 40 GB. Codebook 8192. [IVG-PAPER, Tables 7-8]

**Target behavior.** Cosmos3 FD AR or hybrid token stacks that blow the context window or OOM.

**Attachment.** Context-conditioned future codes on **Generator**, not Reasoner.

**Minimum controlled experiment.** Independent VQ versus compressive VQ versus native DM latents at matched AR params. Report contact metrics, shuffle-action gap, tokens/frame, and wall-clock.

**Expected movement.** Token savings with preserved action sensitivity.

**Falsification.** Reject if tokens drop but shuffle gap collapses, or if compressive matches `4 x 4` on contact (then the extra context attention is unused).

## 4. `IVIDEO-XFER-02`: reward tokens with symlog

**Source mechanism.** MBRL path predicts rewards in the same interactive model; symlog is used. [IVG-PAPER, Appendix A.5]

**Target behavior.** WAM that cannot score imagined clips.

**Attachment.** Scalar reward token/head on Generator FD/WAM.

**Minimum controlled experiment.** External reward MLP versus in-sequence reward on Meta-World-like tasks.

**Expected movement.** Better MBPO-style buffer quality.

**Falsification.** Reject if reward tokens fit train reward but do not rank held-out real trajectories.

## 5. `IVIDEO-XFER-03`: action-conditioned finetune

**Source mechanism.** BAIR FVD `75.0±0.20 -> 60.8±0.08` when actions are added (~20% relative). OXE itself has **no** public act-cond checkpoint because action spaces are heterogeneous. Downstream act-cond weights are BAIR/RoboNet/VP2-specific. [IVG-PAPER, Table 1; IVG-CODE README]

**Target behavior.** Action-free video prior that ignores robot commands.

**Attachment.** Action tokens into Generator FD after unlabeled pretrain (`train_gpt.py --action_conditioned --action_dim`).

**Minimum controlled experiment.** Act-free versus act-cond at matched steps on one embodiment; shuffle actions; do not swap in RLVR-World weights.

**Expected movement.** Lower FVD and higher shuffle gap.

**Falsification.** Reject if act-cond matches shuffled actions, or if OXE-act-cond Hub weights are invented.

## 6. `IVIDEO-XFER-04`: goal-conditioned tokens

**Source mechanism.** Released `thuml/ivideogpt-oxe-64-goal-cond` is a distinct Hub model (114M tokenizer + 138M transformer, action-free OXE, goal frame in the prefix). [IVG-HF-OXE-64-GOAL-COND; IVG-CODE README]

**Target behavior.** Planning that cannot condition on a goal image.

**Attachment.** Goal latent/frame in the Generator prefix. Not Reasoner text goals.

**Minimum controlled experiment.** No goal versus goal versus goal-shuffle on the same context clips. Report goal-frame distance and FVD.

**Expected movement.** Goal-conditioned rollouts approach the goal frame; shuffle should not.

**Falsification.** Reject if goal-cond equals act-free on goal distance, or if the eval silently loads act-free weights.

## 7. `IVIDEO-XFER-05`: higher-resolution / longer visual context

**Source mechanism.** RoboNet 256 PSNR `23.8` / SSIM `80.8` versus MaskViT `20.4` / `67.1`. README warns 256 OXE may be undertrained. [IVG-PAPER, Table 1]

**Target behavior.** 64px FD that misses grasp geometry.

**Attachment.** 256-class visual tokens or native higher-res latents on Generator.

**Minimum controlled experiment.** 64 vs 256 at matched token budget if possible.

**Expected movement.** Better contact at higher res.

**Falsification.** Reject if 256 wins PSNR but loses VP2-style control (paper itself warns perceptual ≠ control).

## 8. `IVIDEO-XFER-06`: medium transformer scale

**Source mechanism.** Medium transformer 436M / 24 layers versus 138M / 12. [IVG-PAPER, Table 2]

**Target behavior.** 138M AR that underfits OXE diversity.

**Attachment.** Width/depth sweep on Generator temporal stack.

**Minimum controlled experiment.** Small vs medium, matched data and tokens.

**Expected movement.** Better rare-embodiment FVD.

**Falsification.** Reject if medium matches small on downstream control after matched finetune.

## 9. `IVIDEO-XFER-07`: AR exposure / long-horizon control

**Source mechanism.** VP2 open-slide mean success `0.1611` versus SVG′ `0.5733`; paper cites discretization and reward design. [IVG-PAPER, Table 6]

**Target behavior.** AR FD that looks good at FVD but fails sliding contacts.

**Attachment.** Horizon curriculum and contact-centric eval on Generator.

**Minimum controlled experiment.** Teacher-forced vs scheduled sampling; report slide/drawer tasks separately.

**Expected movement.** Better open-slide analog without BAIR FVD collapse.

**Falsification.** Reject if FVD improves while slide success stays at floor.

## 10. `IVIDEO-XFER-08`: two-stage act-free then act-cond

**Source mechanism.** Pretrain helps at 100–1000 BAIR trajectories; 1000 act-cond BAIR FVD 82.3. Full downstream data reduces the gap. [IVG-PAPER, Sec. 4.1]

**Target behavior.** Training action-cond from scratch on small robot sets.

**Attachment.** Cosmos3 schedule: unlabeled video FD then action tokens.

**Minimum controlled experiment.** Scratch act-cond vs two-stage at 100/1000/full trajectories.

**Expected movement.** Two-stage wins in the low-data slice.

**Falsification.** Reject if scratch matches two-stage at 100 trajectories.

## 11. `IVIDEO-XFER-09`: do not train dense per-frame tokens at AR batch

**Source mechanism.** `16 x 16` tokenizer is OOM at batch 16 on 40 GB; compressive uses 22.3 GB. [IVG-PAPER, Table 7]

**Target behavior.** Naive full-frame VQ in a Cosmos3 AR auxiliary.

**Attachment.** Keep a tight future bottleneck; spend compute on the transformer.

**Minimum controlled experiment.** Force `16 x 16` at reduced batch versus compressive at full batch, matched wall clock.

**Expected movement.** Compressive wins per-hour FVD.

**Falsification.** Reject if reduced-batch dense tokens beat compressive on contact at equal wall time.

## 12. `IVIDEO-XFER-10`: isolate checkpoints and exclude RLVR-World

**Source mechanism.** README lists distinct Hub names and forbids assuming OXE act-cond. RLVR-World is a 2025 follow-up. [IVG-CODE README]

**Target behavior.** Leaderboards that mix act-free, goal-cond, and RLVR weights.

**Attachment.** Eval config must pin one Hub id.

**Minimum controlled experiment.** Run the same clips on act-free vs goal-cond; show they differ.

**Expected movement.** Conditioning mode is an identity, not a hyperparameter.

**Falsification.** Reject any claim that silently swaps RLVR-World or a missing OXE act-cond file.

## 13. Invalid generalizations

- Do not call MAGVIT-beating FVD a universal win (Table 1 is mixed).
- Do not attach AR reward tokens to Reasoner text.
- Do not use iVideoGPT as IRASim RoboNet numbers without noting imported baselines in IRASim.
- Do not treat `ivideogpt-oxe-64-act-cond` YAML titles as OXE pretrain weights.
- Do not mix 256 RoboNet paper numbers with OXE-256-act-free Hub files.
- Attach compressive VQ and action tokens to **Generator FD/WAM**, not Reasoner.

## 14. Transfer record template

```text
Hypothesis ID (IVIDEO-XFER-NN):
Hub id pinned (must not be RLVR-World):
Attachment (Generator FD/WAM):
Controls (tokenizer, AR width, data hours):
Metrics (FVD, shuffle gap, VP2-style success):
Decision:
```

No transfer experiment is registered.

## 15. Attachment checklist for Cosmos3

| Do | Do not |
|---|---|
| Attach compressive VQ and action tokens to Generator FD/WAM | Attach AR reward tokens to Reasoner text |
| Pin Hub name as an identity | Swap RLVR-World 2025 weights |
| Keep MAGVIT/FitVid mixed Table 1 | Call FVD a universal win |
| Use BAIR/RoboNet act-cond finetune scripts | Treat [IVG-HF-OXE-64-ACT-COND] as OXE pretrain |
| Drop RoboNet-256 if Hub file is gone | Substitute [IVG-HF-OXE-256] silently |

## Sources

- [IVG-PAPER], [IVG-CODE], named Hub cards.
