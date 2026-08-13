---
id: world-model-kb.foundations.data-and-evaluation.data-curation-and-filtering
title: Data Curation and Filtering
kind: concept
status: draft
last_updated: 2026-08-13
owners:
  - AIBuildAI world-model group
---

# Data Curation and Filtering

## Retrieval metadata

**Relevant queries:** quality filtering, top-k selection, data pruning, demonstration curation, subset selection, retention budget, coverage collapse, rare-mode preservation, stratified filtering, influence-based selection, success-only filtering, or filtering a synthetic candidate pool.

**Knowledge provided:** a formal account of the selection step that maps a candidate pool to a retained training subset, the mechanism families that implement it, the conditions under which scalar-quality selection silently deletes rare modes, and the controls a filtering comparison needs before its result is interpretable.

**Related pages:** [Datasets and supervision](datasets-and-supervision.md) owns data domains, sequence construction, mixture design, and provenance; this page owns the selection operator applied to a candidate pool and its distributional consequences. [Evaluation methodology](evaluation-methodology.md) owns metric validity and statistical comparison; this page states which of those instruments a curation claim must use. [Cosmos3-Nano data](../../models/cosmos3-nano/data.md) records a model-specific filtering pipeline; [Cosmos-Predict2.5](../../papers/cosmos-predict2-5/paper.md) documents staged filtering at foundation scale.

## Definition and scope

Data curation is the selection of a retained subset from a candidate pool under a retention budget, using scores, predicates, influence estimates, or diversity objectives computed per candidate. The candidate pool may be scraped video, teleoperated demonstrations, or synthetically generated trajectories; the operator is the same. This page owns the selection operator and what it does to the retained distribution. It does not own the composition of the pool (datasets and supervision), the metric definitions used to audit the result (evaluation methodology), or any specific model's dataset mixture.

The central phenomenon this page tracks: a selection score is a proxy, and any latent factor correlated with the score is redistributed by selection. When a low-density mode of the pool correlates with low score, budgeted global selection deletes it, even though no step of the pipeline names that mode. The deletion is invisible to aggregate metrics and to the mean of the score itself.

## Formalization

Let the pool be `D = {x_1, ..., x_N}` with a latent mode assignment `m(x) in {1..M}` that no curation input observes. A scalar score `s: X -> R`, a retention budget `k < N`, and a selection operator `S(D, s, k) subset D`, `|S| = k`, define the curation step. Global top-k is `S = argsort_s(D)[:k]`. Stratified selection first partitions `D` by a grouping function `c(x)` (true labels when available, unsupervised clusters otherwise), allocates per-stratum quotas (typically proportional to stratum occupancy), and applies the score within each stratum. Predicate filtering (for example task success) is the special case of a binary score with the budget set by the predicate's pass rate.

The audit quantities are the pre- and post-selection mode occupancy `n_m(D)` versus `n_m(S)`, and the downstream risk conditional on mode or region, alongside the aggregate. Comparisons between operators are defined only at equal `k`: retention volume is itself a treatment, and unequal budgets masquerade as method effects.

## Assumptions and invariants

- **Score-mode correlation is the driver.** Collapse requires only that `s` and `m` are dependent; it does not require the rare mode to be low quality. When the rare mode is easy for the scorer, global top-k oversamples it and collapses a different mode instead, so the failure direction follows the correlation sign, not rarity itself.
- **Budget matching is a comparison invariant.** Any claim "operator A beats operator B" presupposes `k_A = k_B` and identical downstream training.
- **Label availability separates repair families.** Supervised per-class quotas assume mode labels exist; label-free stratification substitutes an unsupervised partition and inherits the additional assumption that the clustering features are informative about the latent mode while insensitive to the defect being filtered. When that insensitivity fails, the repair fails with it.
- **Selection effects survive downstream.** A model trained on `S` cannot recover support the selection removed; a rare mode absent from `S` fails as an out-of-distribution input at deployment, regardless of training quality.

## Mechanism or method families

| Family | Core mechanism | Assumptions | Strengths | Failure boundary | Representative evidence |
|---|---|---|---|---|---|
| Global score top-k | rank all candidates by one scalar, keep best k | score correlates with usefulness | simple, scalable, removes junk | deletes any mode negatively correlated with the score; measured imbalance amplification in both easy- and hard-removal directions | [DATA-SORSCHER-2022, pp.9, 45-47] |
| Outcome predicate | keep candidates passing a binary test (task success) | outcome observable per candidate | guarantees usable candidates | initial-state support coverage of generated datasets falls as low as 43.5 percent on measured task variants while the best-covered exceed 89 percent, so the bias is variant-dependent and silent; generation success rate does not predict trained-policy success | [DATA-MIMICGEN-2023, pp.40-42] |
| Influence-based selection | estimate each candidate's effect on a validation objective | validation set represents deployment | targets downstream utility directly | global influence ranking retains 104-115 demos for three tasks and 13 for a fourth, near-deleting it; documented coverage-blind | [DATA-ATHENA-2026, pp.5, 19-21], [DATA-DATAMIL-2025, p.10] |
| Diversity-maximizing subset | select subset maximizing a diversity functional (trajectory-kernel entropy) | diversity measurable in a feature space | label-free coverage pressure | no quality axis; audits coverage after diversity selection, not after quality filtering | [DATA-FAKTUAL-2026, pp.4-5, 8] |
| Redundancy and suboptimality removal | self-supervised masks for near-duplicate and suboptimal transitions | defect detectable without labels | removes junk with cluster structure | within-cluster step is deduplication, not quality ranking under coverage quotas; no per-region coverage reported | [DATA-SCIZOR-2025, pp.13-17] |
| Supervised per-class quotas | fix per-class retention floors, filter within class | true class labels available | provably prevents class deletion | inapplicable when modes are latent; classification-only evidence | [DATA-SORSCHER-2022, pp.45-47], [DATA-PERCLASS-2025, pp.4-8] |
| Label-free cluster-stratified filtering | cluster the pool on defect-insensitive features, allocate proportional quotas, rank within cluster | clustering recovers latent modes; features insensitive to the filtered defect | keeps junk removal while preserving mode occupancy at matched budget | fails when clustering features are sensitive to the defect (the repair inherits the collapse) | internal preregistered measurement, hypothesis at KB level pending artifact bundling; nearest published structure is SCIZOR's cluster-then-dedup |

The families vary on independent axes (what is scored, whether structure is imposed, what labels are assumed); a pipeline may compose several, and composition order changes the retained distribution.

## Design implications and trade-offs

- **Filtering benefit is defect-density dependent.** When the pool has little to remove, selection buys no quality and still spends diversity; the measured benefit of coverage-preserving filtering grows with corruption severity and approaches zero on clean pools (internal preregistered measurement, trend p = 0.002; hypothesis at KB level pending artifact bundling). Design consequence: the decision to filter at all should reference an estimate of pool defect density, not a fixed pipeline habit.
- **Junk removal and mode preservation are separable effects.** Global top-k can beat random selection on aggregate error at high defect density while still deleting the rare mode; the aggregate win is junk removal, the conditional loss is mode deletion, and a design that wants both must measure both.
- **Score choice is a coverage decision.** Whatever latent factor the score loads on is what selection redistributes; a smoothness or consistency score computed from the same signal that distinguishes modes will trade coverage for quality silently. The newest scalar demo filters do not measure retained diversity or rare-behavior survival [DATA-PSD-2026, pp.4-7], and quality itself is not an intrinsic scalar of a datum: it depends on demonstrator, dataset size, and learner [DATA-DATAQUALITY-2023, p.4].
- **The largest generation pipelines currently skip selection entirely.** A 240k-trajectory synthetic pipeline reports no rejection step and names generated-trajectory quality as its bottleneck [DATA-DREAMGEN-2025, pp.2-4, 9, 15]; curation pressure on synthetic pools is therefore rising, and the operator chosen will determine which modes of the generator's output survive.
- **Proxy optimization is the ancestor failure.** Selecting data by an imperfect score is structurally the same operation as optimizing a policy inside an imperfect model, where the optimizer migrates into the proxy's largest errors [FND-WORLD-MODELS-2018, pp.8-10 of the arXiv version]; curation inherits that lesson at the dataset level.

## Evaluation and falsification

A curation comparison supports a claim only under these controls, all owned in detail by [evaluation methodology](evaluation-methodology.md):

- all arms at exactly matched retention budgets, with a budget-matched random arm as floor;
- aggregate and conditional (per-mode or per-region) downstream metrics reported together, since the aggregate can improve while a conditional collapses;
- pre- and post-selection occupancy of the strata or regions, fixed from system variables before any outcome is inspected;
- an oracle-stratified arm (true labels) when testing label-free stratification, to separate clustering failure from stratification failure;
- no per-run win counts as evidence for near-zero effects, and no model selection on the reporting split.

Falsifiers: a label-free stratified arm that fails to preserve occupancy under a defect-insensitive feature set falsifies the repair claim for that pool; a global top-k arm that preserves occupancy on a pool where score and mode are measured to be dependent falsifies the collapse mechanism as stated.

## Failure modes and invalid equivalences

- **Silent rare-mode deletion.** Symptom: aggregate metric flat or improved, conditional metric on a rare region collapsed, post-selection occupancy of that region near zero. Cause: score-mode correlation under a global budget. Diagnostic: pre/post occupancy table.
- **"Higher mean retained quality implies better downstream" is invalid.** Outcome-predicate evidence shows generation success rate and trained-policy success are uncoupled [DATA-MIMICGEN-2023, pp.40-42].
- **"The curator is label-free, therefore coverage-safe" is invalid.** Label-free objectives (influence, deduplication, diversity) each redistribute occupancy by their own proxy; the strongest published curators are coverage-blind by design [DATA-DEMOSCORE-2025, p.9], [DATA-DATAMIL-2025, p.10].
- **Stratification inherits its feature space.** When clustering features are sensitive to the defect being filtered, strata align with the defect rather than the mode and the repair reproduces the collapse (internal measurement, hypothesis at KB level; the boundary condition, not the headline, is the claim here).
- **"More diversity is always better" is invalid.** Trajectory diversity shows a mastery-dependent optimum; mode preservation and within-stratum diversity tuning are separate decisions [DATA-DIVERSITY-2026, pp.3-7].

## Cross-part connections

- **Paper evidence:** [Cosmos-Predict2.5](../../papers/cosmos-predict2-5/paper.md) instantiates staged filtering, semantic deduplication, and domain sharding at foundation scale; [MimicGen](../../papers/mimicgen/paper.md) owns the outcome-predicate evidence in full.
- **Model instantiations:** [Cosmos3-Nano data](../../models/cosmos3-nano/data.md) records single-model quality filtering plus semantic deduplication in pretraining; whether physical-mode coverage was affected is unresolved and belongs to the model's research registry, not to this page.
- **Open questions:** which score families are mode-insensitive for robot trajectories is unresolved field-wide; [open problems](../research-frontiers/open-problems.md) owns cross-model unknowns.

## Sources

- [DATA-SORSCHER-2022] Sorscher et al., *Beyond neural scaling laws: beating power law scaling via data pruning*, NeurIPS 2022, arXiv:2206.14486.
- [DATA-MIMICGEN-2023] Mandlekar et al., *MimicGen: A Data Generation System for Scalable Robot Learning using Human Demonstrations*, CoRL 2023, arXiv:2310.17596.
- [DATA-ATHENA-2026] Xu et al., *ATHENA: Accelerated Multi-Task Heterogeneous Influence Functions for Robot Data Curation*, arXiv:2606.16208.
- [DATA-DATAMIL-2025] Dass et al., *DataMIL: Selecting Data for Robot Imitation Learning with Datamodels*, arXiv:2505.09603.
- [DATA-FAKTUAL-2026] Sirigiri et al., *Diversity You Can Actually Measure: A Fast, Model-Free Diversity Metric for Robotics Datasets*, arXiv:2603.11634.
- [DATA-SCIZOR-2025] Zhang et al., *SCIZOR: A Self-Supervised Approach to Data Curation for Large-Scale Imitation Learning*, arXiv:2505.22626.
- [DATA-PERCLASS-2025] Tsai et al., *Class-Proportional Coreset Selection for Difficulty-Separable Data*, arXiv:2507.10904.
- [DATA-PSD-2026] Sojib and Begum, *An Efficient Metric for Data Quality Measurement in Imitation Learning*, arXiv:2605.01544.
- [DATA-DEMOSCORE-2025] Chen et al., *Curating Demonstrations using Online Experience*, arXiv:2503.03707.
- [DATA-DREAMGEN-2025] Jang et al., *DreamGen: Unlocking Generalization in Robot Learning through Video World Models*, arXiv:2505.12705.
- [DATA-DATAQUALITY-2023] Belkhale et al., *Data Quality in Imitation Learning*, NeurIPS 2023, arXiv:2306.02437.
- [DATA-DIVERSITY-2026] Luo et al., *Geometric Entropy: When Trajectory Diversity Helps and Hurts in Imitation Learning*, arXiv:2606.20871.
- [FND-WORLD-MODELS-2018] Ha and Schmidhuber, *Recurrent World Models Facilitate Policy Evolution*, NeurIPS 2018, arXiv:1803.10122.

Internally measured claims are labeled inline as internal preregistered measurements, carry hypothesis status at KB level until their artifacts are bundled under the KB artifact policy, and will be owned by the planned paper entry rather than this page.
