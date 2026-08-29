---
id: world-model-kb.papers.vlabench.optimization-transfer
title: VLABench Transferable Optimization Knowledge
kind: guide
status: maintained
last_updated: 2026-08-21
owners:
  - AIBuildAI world-model group
---

# VLABench Transferable Optimization Knowledge

## Retrieval metadata

**Relevant queries:** improve VLABench score, action representation matters, delta chunk, cross-category generalization, texture robustness, semantic instruction, progress score shaping, data generation augmentation, camera augmentation, track-specific intervention, protocol hygiene.

**Knowledge provided:** falsifiable intervention patterns that the benchmark's own design and released baselines support, their attachment surfaces on a VLA policy such as Xiaomi-Robotics-1, required controls, expected movement, and invalid generalizations.

**Related pages:** [`paper.md`](paper.md) owns the protocol; [`codebase.md`](codebase.md) owns surfaces; [Xiaomi-Robotics-1 optimization playbook](../../models/xiaomi-robotics-1/optimization-playbook.md) owns experiment discipline; [ERVLA transfer](../ervla/optimization-transfer.md) owns language-side interventions.

## 1. Transfer discipline

VLABench is the measurement, not the method; its evidence about interventions is indirect (baseline deltas the maintainers published, the benchmark's own generalization axes, and defects that bias metrics). Every item below is a hypothesis for a specific policy and must be tested on the paired official configs.

## 2. Intervention matrix

| ID | Target failure | Mechanism | Attachment surface | Primary evidence | Principal risk |
|---|---|---|---|---|---|
| `VLABENCH-XFER-01` | low Track-1 SR from action encoding | action representation (delta chunk vs relative chunk) | data path + client integration | pi0-FAST 29.1 -> 51.2 by changing the transform | must match the served client's integration |
| `VLABENCH-XFER-02` | Track 2 drop (unseen categories/instances) | instance/category diversity: object-swap augmentation at generation time or in-data relabelling | VLABench generator (`trajectory_generation.py`) or episode duplication | benchmark axis definition | generator failures on many tasks (issues 73, 87); contamination with track configs |
| `VLABENCH-XFER-03` | Track 6 drop (textures) | texture/background randomization | generator camera/texture augmentation (2025-08 release) or image augmentation in the trainer | benchmark axis; camera-augmentation feature | train/eval resolution asymmetry in XR-1 |
| `VLABENCH-XFER-04` | Track 3/4 drop (commonsense, semantics) | instruction paraphrase and attribute grounding | instruction field of the training JSON; CoT content | benchmark axis; ERVLA evidence | paraphrases must not copy test instructions |
| `VLABENCH-XFER-05` | noisy selection | use the official config prefix for every candidate (paired) | evaluation harness | Evaluator takes the list prefix deterministically | a random resample is a different protocol |
| `VLABENCH-XFER-06` | misread metrics | SR as the decision metric; PS/IS as diagnostics | reporting | issues 55/82 | none |
| `VLABENCH-XFER-07` | partial credit ignored | PS-aware data weighting (upweight episodes of tasks with low PS) | sampler | PS formula (stage completion) | overfits stages |
| `VLABENCH-XFER-08` | episode cap losses | speed: replan horizon and chunk usage | client `replan_steps` | caps 100/200/300 | off-protocol if changed for the reported number |

## 3. `VLABENCH-XFER-01`: action representation

**Source evidence.** The maintainers' pi0-FAST fine-tunes: relative-chunk transform 29.1 % Track-1 SR versus the aligned delta-chunk transform 51.2 %. [VLAB-CODE README; VLAB-HF-ORG]

**Attachment.** For XR-1, the served client integrates per-step world-frame deltas; the representation is fixed by the checkpoint's training data path and processor stats.

**Minimum experiment.** Two data paths (released per-step convention vs an alternative) each exported with matching stats and scored by the same client; a convention change that requires a client change is off-protocol.

**Falsification.** No SR difference beyond ~6 pp.

## 4. `VLABENCH-XFER-02`/`03`: generalization-axis augmentation

**Attachment.** Either regenerate episodes with the benchmark's own generator (object and texture sampling) - keeping Track-1 provenance requires declaring the new data - or augment within the official set (colour/texture jitter, instance relabelling is not possible without regeneration).

**Minimum experiment.** Baseline vs augmented at equal steps; per-track paired SR; report Track-1 change as the regression guard.

**Falsification.** Track 2/6 unchanged or Track 1 down.

## 5. `VLABENCH-XFER-05`: paired prefix selection

**Mechanism.** `Evaluator` consumes `episode_config[task][:n]`; the first k configs are identical for every candidate, making per-episode paired comparisons valid and the prefix an unbiased estimate of the full protocol. **Falsification test for a harness.** Two runs of the same checkpoint and seed must produce identical per-episode outcomes.

## 6. Invalid generalizations

- Legacy-protocol numbers (paper Table 2) are not comparable to track numbers.
- A Track 1-4 PS average (Awesome-WAM) is not a 5-track SR average.
- Track 5 is open and user-defined; it never enters the standard average.
- Results from `lerobot/vlabench_unified` training are a different provenance.

## Sources

[VLAB-PAPER]; [VLAB-CODE] README, `evaluation/evaluator/base.py`; [VLAB-HF-ORG]; [VLAB-WAM-LEADERBOARD]; [VLAB-DATA-UNIFIED]; [VLAB-ISSUE-55]; [VLAB-ISSUE-82]; [ERV-PAPER].
