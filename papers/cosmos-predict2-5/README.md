---
id: world-model-kb.papers.cosmos-predict2-5
title: Cosmos-Predict2.5 Paper Knowledge Entry
kind: paper
status: maintained
last_updated: 2026-08-13
owners:
  - AIBuildAI world-model group
---

# Cosmos-Predict2.5 Paper Knowledge Entry

## Retrieval metadata

**Relevant queries:** Cosmos-Predict2.5, video world model, Text2World, Image2World, Video2World, Physical AI video generation, flow matching, action-conditioned video prediction, domain SFT, model merging, diffusion RL, timestep distillation, or multiview generation.

**Knowledge provided:** paper identity and scope, a map to its mechanisms and experiments, the released implementation and checkpoint boundary, reproduction state, and falsifiable transfer hypotheses.

**Related pages:** [Video world models](../../foundations/representations/video-world-model.md) owns the general observation-prediction category; [diffusion and flow matching](../../foundations/learning-objectives/diffusion-and-flow-matching.md) owns the objective family; [actions and interventions](../../foundations/problem-formulation/actions-and-interventions.md) distinguishes passive from action-conditioned prediction; [Cosmos3-Nano training](../../models/cosmos3-nano/training.md) owns the later model's lineage-specific use of Predict2.5 concepts.

## Identity and revision boundary

| Field | Canonical value | Consequence |
|---|---|---|
| Work | *World Simulation with Video Foundation Models for Physical AI* | This entry reconstructs the Cosmos-Predict2.5 claims inside the combined Predict2.5/Transfer2.5 report. |
| Paper snapshot | `arXiv:2511.00062v2`, report date 2026-02-24 | Result and method locators refer to this 44-page revision. [P25-TR] |
| Local paper identity | `cosmos-predict2.5.pdf`, SHA256 `2597170ef9e8128c1ec3c87aa1eaf321cd599268451da1f61aead325eca576fe` | Prevents silent substitution of a later paper version. [P25-TR] |
| Feature-release code | `f2146f47a07abf72459c92a9958484ff447ed37d` | Introduces the v1.5.0 functionality and is the primary mechanism-to-code mapping snapshot. [P25-CODE-PAPER] |
| Report-date code tree | `a24ac3df55d55f87deff7067907afcaf961045f1` | Includes the same-day hotfix and the README capability update; use this full tree for a paper-era execution attempt. [P25-CODE-REPORT-UPDATE] |
| Current inspected code | `a2c298b0a3df3778b973fe65e9e58877b292d8a7` | Supplies maintenance and environment updates, not retroactive paper evidence. [P25-CODE-CURRENT] |
| Current 2B checkpoint repository | `nvidia/Cosmos-Predict2.5-2B@85f8ae7bfe8f5525c8d103429524dcf12f98bf7b` | Contains base and specialized 2B assets; current revision is not asserted to be the exact evaluated snapshot. [P25-HF-2B] |
| Current 14B checkpoint repository | `nvidia/Cosmos-Predict2.5-14B@18839bf38537b31f191f2ec834a4d9181ee09ca2` | Contains pre-trained and post-trained 14B assets. [P25-HF-14B] |
| Code/model licenses | Apache-2.0 code; NVIDIA Open Model License checkpoints | License scope differs between source and weights. [P25-CODE-PAPER; P25-HF-2B; P25-HF-14B] |

Git tags are not used as immutable paper identities. The inspected `v1.5.0` tag currently resolves to an April maintenance commit rather than either February snapshot. This observation does not establish the tag's historical mutation sequence; it establishes only that the current tag is unsuitable as a paper-era identity. Reproduction and comparison records should bind full commits and checkpoint revisions rather than a release label.

## Operational model boundary

Cosmos-Predict2.5 is best classified as a **video-based latent world foundation model**: it models future decoded observations in video form using a latent rectified-flow transformer. The base model unifies text-only, image-prefix, and video-prefix conditioning. This supplies a high-capacity observational simulator but does not, by itself, define calibrated action interventions, rewards, a controller, or a closed-loop policy. [P25-TR, pp.8-11]

| Surface | Conditional query | Valid interpretation | Invalid projection |
|---|---|---|---|
| Base Text2World | `p(video | text)` | plausible video sampled from a prompt-conditioned distribution | causal consequences of a robot command |
| Base Image2World | `p(video_future | image_prefix, text)` | continuation grounded in an observed first frame | hidden-state recovery or policy action |
| Base Video2World | `p(video_future | video_prefix, text)` | observation continuation or transformation | counterfactual dynamics without action labels |
| `2B/robot/action-cond` | `p(video_future | image, action_chunk)` | action-indexed forward observation model for the Bridge action contract | universal embodiment transfer or executable policy |
| Auto/robot multiview specialists | `p(target_views | source, cameras, text)` | camera-conditioned synchronized rendering | persistent explicit 3D state or physical intervention |
| Transfer2.5 family | spatial-control-conditioned translation | a related control branch built on the Predict backbone | a base Predict2.5 checkpoint capability |
| Cosmos Policy | image/proprioception/task to actions and predicted futures | later separately published visuomotor policy extension | evidence reported in the Predict2.5 paper [P25-COSMOS-POLICY] |

## Knowledge map

| Question | Canonical page |
|---|---|
| What is the predictive distribution, architecture, data curriculum, training signal, and reported evidence? | [`paper.md`](paper.md) |
| Which released modules implement each mechanism, and where does code diverge from the report? | [`codebase.md`](codebase.md) |
| What has actually run, what remains unexecuted, and what would constitute a valid reproduction? | [`reproduction.md`](reproduction.md) |
| Which mechanisms may transfer, where would they attach, and what would falsify each hypothesis? | [`optimization-transfer.md`](optimization-transfer.md) |
| Which immutable papers, commits, model revisions, and local artifacts support the entry? | [`sources.yaml`](sources.yaml) |

These associations support knowledge retrieval. They neither impose reading order nor define AIBuildAI Agent selection, repository selection, experiment scheduling, permissions, or workflow orchestration.

## Capability ownership and exclusions

This entry owns paper-specific explanations of Predict2.5 data curation, latent flow training, conditional-frame curriculum, domain specialization, weight merging, reward post-training, rCM distillation, reported benchmarks, action-conditioning ablations, and the corresponding public code boundary. Model-independent definitions remain in Foundations. The later Cosmos3-Nano entry owns Cosmos 3 implementation facts rather than inheriting Predict2.5 results.

Because the source is a combined Predict2.5/Transfer2.5 report, [`paper.md`](paper.md) follows the report through both the base model and its Transfer2.5, robot, driving, multiview, synthetic-data, and action-conditioned extensions. Every result remains attached to its named checkpoint family; an extension is not projected onto the base Predict2.5 checkpoint. [`optimization-transfer.md`](optimization-transfer.md) extracts only falsifiable mechanisms rather than reproducing the report's application narrative. Cosmos Policy is named only to prevent version conflation; its algorithms and results belong in a separate paper entry. Local execution claims are restricted to [`reproduction.md`](reproduction.md).

## High-value evidence anchors

- The data pipeline retains approximately 200 million clips from more than 6 billion candidates derived from 35 million hours of raw video. The report separately calls this approximately 4% retention, although the rounded counts imply at most 3.33%; [`paper.md`](paper.md) preserves this unresolved denominator mismatch rather than silently normalizing it. [P25-TR, pp.4-7]
- The 2B and 14B base models share the same conditional surface but differ in capacity; the report lists 32 and 36 layers, while the released 2B configuration exposes 28 transformer blocks. The unresolved count mismatch is preserved in [`codebase.md`](codebase.md). [P25-TR, p.9, Table 3; P25-CODE-PAPER]
- The final pre-training stage samples zero, one, or two conditioning frames with probabilities `0.5/0.25/0.25`; a targeted 5% draw from the highest 2% of noise is reported to reduce abrupt transitions, without an isolated numeric ablation. [P25-TR, pp.10-11]
- Domain-specific SFT, checkpoint merging, reward optimization, and four-step distillation form distinct adaptation mechanisms. Gains from their final composition cannot be assigned to one component unless the relevant ablation exists. [P25-TR, pp.11-15]
- The action-injection comparison is the strongest direct architecture ablation: time-embedding injection improves all four reported Bridge prediction metrics over channel concatenation and improves PSNR, SSIM, and FVD over cross-attention. [P25-TR, pp.33-35, Tables 19-20]

## Sources

Source identities and revision pins are maintained in [`sources.yaml`](sources.yaml). Claim-level locators remain in the owning pages.
