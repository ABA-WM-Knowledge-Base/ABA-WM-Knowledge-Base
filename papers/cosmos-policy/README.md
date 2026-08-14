---
id: world-model-kb.papers.cosmos-policy
title: Cosmos Policy Paper Knowledge Entry
kind: paper
status: maintained
last_updated: 2026-08-14
owners:
  - AIBuildAI world-model group
---

# Cosmos Policy Paper Knowledge Entry

## Retrieval metadata

**Relevant queries:** Cosmos Policy, latent frame injection, video model as robot policy, Predict2 post-training, LIBERO, RoboCasa, ALOHA, best-of-N planning, value latent, dual policy and planning checkpoints, or Cosmos3-Nano Policy-DROID.

**Knowledge provided:** paper identity and Predict2 versus Predict2.5 code-tree boundary, latent-frame injection mechanism, joint policy/world-model/value training, reported simulation and real-robot evidence, released implementation and checkpoints, reproduction state, and falsifiable transfer hypotheses.

**Related pages:** [P25-COSMOS-POLICY] owns the bibliographic paper identity already registered by the Cosmos-Predict2.5 entry; [Cosmos-Predict2.5](../cosmos-predict2-5/README.md) owns the source video model family and must not inherit Policy success rates; [planning and control](../../foundations/decision-making/planning-and-control.md) owns search/evaluator interactions; [embodied systems](../../foundations/embodied-systems/robotics-and-embodied-ai.md) owns robot interfaces; [Cosmos3-Nano policy](../../models/cosmos3-nano/policy.md) owns the later Policy-DROID surface.

## Identity and revision boundary

| Field | Canonical value | Consequence |
|---|---|---|
| Work | *Cosmos Policy: Fine-Tuning Video Models for Visuomotor Control and Planning* | This entry reconstructs the Predict2-initialized policy paper, not Predict2.5 video generation results. |
| Paper identity | [P25-COSMOS-POLICY] `arXiv:2601.16163` | Do not re-register the paper in this entry's `sources.yaml`. |
| Official Predict2 code | `NVlabs/cosmos-policy@18a2accadf4e7a3531e56754102af5a24d2316da` | Primary mechanism-to-code mapping snapshot dated 2026-01-23. [CPOL-CODE] |
| Project page | NVIDIA DIR Cosmos Policy | Mutable presentation surface; numerical claims remain paper-owned. [CPOL-PROJECT] |
| Predict2.5 cookbook path | Cosmos Cookbook plus `nvidia-cosmos/cosmos-predict2.5` in-tree `cosmos_policy` | A later adaptation surface; not paper-era evidence for Tables 1-3. [CPOL-COOKBOOK] |
| LIBERO checkpoint | `nvidia/Cosmos-Policy-LIBERO-Predict2-2B` | Policy weights for the LIBERO suites; not RoboCasa or ALOHA. [CPOL-HF-LIBERO] |
| RoboCasa checkpoint | `nvidia/Cosmos-Policy-RoboCasa-Predict2-2B` | Policy weights for RoboCasa kitchen tasks. [CPOL-HF-ROBOCASA] |
| ALOHA policy checkpoint | `nvidia/Cosmos-Policy-ALOHA-Predict2-2B` | Direct policy for real bimanual tasks. [CPOL-HF-ALOHA] |
| ALOHA planning checkpoint | `nvidia/Cosmos-Policy-ALOHA-Planning-Model-Predict2-2B` | Dual-deployment ranking model; not a standalone policy. [CPOL-HF-ALOHA-PLAN] |

The paper initializes from **Cosmos-Predict2-2B-Video2World**, not Cosmos-Predict2.5 and not Cosmos3-Nano. Cookbook instructions that mention Predict2.5 are a separate implementation family. [P25-COSMOS-POLICY; CPOL-COOKBOOK]

## Operational model boundary

Cosmos Policy is a **single-stage post-trained visuomotor policy** that reuses a pretrained latent video diffusion transformer without new action heads. Additional modalities are encoded as latent frames and inserted into the diffusion sequence. The model can emit an action chunk, a future observation (images plus proprioception), and a scalar value. Direct policy execution uses only the action chunk. Model-based planning uses future-state and value latents to rank proposals. [P25-COSMOS-POLICY, Sec. 4]

| Surface | Inputs | Outputs | Invalid projection |
|---|---|---|---|
| Direct policy | current images, proprioception, language | action chunk | Cosmos-Predict2.5 video scores or Cosmos3-Nano Policy-DROID |
| Joint generation | same, optional action condition | future images, future proprioception, value | calibrated physics simulator |
| Best-of-N planning | policy proposals plus planning checkpoint | selected action chunk | receding-horizon guarantee or safety certificate |
| Predict2.5 cookbook recipe | Predict2.5-2B Video2World | a later post-training path | paper Table 1 LIBERO 98.5% |

## Knowledge map

| Question | Canonical page |
|---|---|
| Method, architecture, data, experiments, and evidence limits | [`paper.md`](paper.md) |
| Released modules, configs, and Predict2 versus Predict2.5 code split | [`codebase.md`](codebase.md) |
| What has been executed locally | [`reproduction.md`](reproduction.md) |
| Transferable interventions and falsification tests | [`optimization-transfer.md`](optimization-transfer.md) |
| Code, checkpoint, and dataset identities | [`sources.yaml`](sources.yaml) |

These associations support retrieval and synthesis. They do not define Agent selection, task sequence, experiment priority, repository choice, permissions, or AIBuildAI workflow orchestration.

## High-value evidence anchors

- Latent frame injection encodes proprioception, action chunks, extra camera views, and values as duplicated normalized volumes in the Wan2.1 VAE latent grid, avoiding a new action network. Scratch initialization drops LIBERO average from 98.5 to 94.6 and Long from 97.6 to 88.6. [P25-COSMOS-POLICY, Sec. 4.1, Table 4]
- Joint training mixes 50% demonstration policy samples with 25% world-model and 25% value rollout samples. Removing future-state supervision on the RoboCasa policy collapses average success from 62.5 to 44.4. [P25-COSMOS-POLICY, Tables 4-5]
- Direct-policy LIBERO average success is 98.5% over four suites, 500 trials per suite, three seeds (6000 trials). RoboCasa average success is 67.1% trained on 50 human demos per task, 3600 trials. [P25-COSMOS-POLICY, Tables 1-2]
- Real ALOHA average completion 93.6 across four bimanual tasks and 101 matched initial states (30/20/25/26). In-distribution 96.3; OOD 89.3, where π0.5 is 92.5. Preserve the OOD reversal. [P25-COSMOS-POLICY, Table 3]
- Dual deployment keeps the original policy checkpoint for action proposals and a rollout-finetuned checkpoint for world-model and value ranking. `N=8` planning costs 4.9 s on 8 H100s and is reported to add 12.5 points on two hard ALOHA tasks under a harder initial-state slice. [P25-COSMOS-POLICY, Sec. 4.3, Fig. 7, Appendix A.4.2]
- Inference uses `sigma_min=4` rather than the base EDM floor 0.002. LIBERO `flip_images` and JPEG augmentation are part of the published contract. [P25-COSMOS-POLICY, Appendix A.2.1; CPOL-CODE]
- No local inference, metric, or training run is registered. [`reproduction.md`](reproduction.md) owns the executed-state boundary.

## Sources

Paper identity resolves through [P25-COSMOS-POLICY]. Implementation and checkpoint identities resolve through [`sources.yaml`](sources.yaml).
