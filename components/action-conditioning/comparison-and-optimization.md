---
id: world-model-kb.components.action-conditioning.comparison-and-optimization
title: Action Conditioning Comparison and Optimization
kind: component
status: draft
last_updated: 2026-08-20
owners:
  - AIBuildAI world-model group
---

# Action Conditioning Comparison and Optimization

## Retrieval metadata

**Relevant queries:** choose action representation, compare action conditioning routes, action interface optimization, Cosmos3-Nano action attachment, action conditioning open questions.

**Knowledge provided:** Selection axes across the three action routes, recurring evidence-supported patterns, Cosmos3-Nano attachment hypotheses, and unresolved questions.

**Related pages:** [Latent-frame injection](latent-frame-injection.md), [joint denoising and schedules](joint-denoising-and-schedules.md), [latent and pseudo-actions](latent-and-pseudo-actions.md), and [future-prediction coupling](future-prediction-coupling.md) own method details; [action-conditioned video modeling](../generative-modeling/action-conditioned-video.md) owns timing semantics and failure diagnosis; [evaluation methodology](../../foundations/data-and-evaluation/evaluation-methodology.md) owns general evidence rules.

## Selection axes

| Axis | Options | Verified evidence anchor |
|---|---|---|
| Route | conditioning input / jointly denoised modality / inferred latent | route table in the [Component README](README.md) |
| Alignment granularity | video-level / frame-aligned | IRASim's Push-T planning gain over video-level conditioning [IRASRC-PAPER-V2] |
| Denoising schedule | synchronous / asynchronous (actions first) | X-WAM ANS: 66.4% to 67.8%, latency 4,665 ms to 1,033 ms [COMP-ACT-XWAM-2026, p. 9] |
| Auxiliary targets | actions only / actions plus future state and value | Cosmos Policy 44.4% vs 67.1% [P25-COSMOS-POLICY, p. 22] |
| History | none / temporal context | unpriced; both RoboCasa leaders are history-free |
| Supervision source | logged actions / latent mining / post-hoc pseudo-labels | Genie, LAPA, DreamGen (method pages) |

The axes compose: one system takes a position on every row, and the rows are not independent (the schedule axis only exists on the jointly denoised route; the supervision axis dominates when action logs are unavailable).

## Recurring supported patterns

### Make actions look like the pretrained modality

Latent-frame injection reuses an unchanged video diffusion objective by disguising robot modalities as latent frames [P25-COSMOS-POLICY, pp. 4-5]. The pattern generalizes: the cheapest action interface is the one the pretrained model already knows how to model. The cost is contract fragility: normalization and layout become part of the model identity.

### Never evaluate the action head alone

The 67.1-to-44.4 ablation and DreamZero's failure attribution both show action quality riding on future-prediction quality ([future-prediction coupling](future-prediction-coupling.md)). Any action-interface change should report the paired future-prediction metrics, not action accuracy alone.

### Treat the noise schedule as an interface decision

Asynchronous scheduling changed both success and latency in the only controlled measurement [COMP-ACT-XWAM-2026, p. 9]. Schedule choices belong in the model card next to the action contract, not in training internals.

### Audit recovered actions at the trajectory level

Latent and pseudo-actions have no per-action ground truth. The only corpus measurement of recovery cost is World2Act's 18%/19% decode-noise result; the audit burden moves to trajectory-level curation ([latent and pseudo-actions](latent-and-pseudo-actions.md)).

## Cosmos3-Nano attachment map

| Target surface | Method knowledge | Testable hypothesis | Evidence required |
|---|---|---|---|
| Action encoder/decoder | latent-frame injection contract | Cosmos 3's added action encoder, decoding MLP, and action tokens [C3-TR, pp. 31-32] inherit the same contract-fragility risks | contract round-trip tests, held-out normalization audit |
| Policy post-training | future-prediction coupling | keeping auxiliary RGB prediction (already present [C3-TR, pp. 31-32]) matters as much as the action loss | ablation with auxiliary targets removed, matched budget |
| Joint WAM mode | denoising schedules | an asynchronous action-first schedule reduces latency without success loss | matched ANS-style ablation on the target stack |
| Data pipeline | latent/pseudo-actions | pseudo-labeled trajectories are usable only with trajectory-level curation | per-mode coverage report before and after labeling |

Exact experiment configurations remain in the [Cosmos3-Nano optimization playbook](../../models/cosmos3-nano/optimization-playbook.md); this table provides mechanism and evidence logic.

## Open questions

1. Does frame-aligned conditioning beat video-level conditioning at RoboCasa scale? The only direct granularity comparison is Push-T [IRASRC-PAPER-V2].
2. Can latent actions represent precise, contact-rich manipulation?
3. What does the shared history-free design cost on partially observed tasks?
4. Does the future-state auxiliary effect (67.1 vs 44.4) replicate on any second system?

These questions define missing evidence, not work priority or workflow.

## Sources

Method-specific source identities and exact locators are listed on the owning method pages. [C3-TR] anchors the Cosmos3-Nano attachment hypotheses; none is a reproduced optimization result.
