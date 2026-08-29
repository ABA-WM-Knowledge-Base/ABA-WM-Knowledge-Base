---
id: world-model-kb.components.world-representation.comparison-and-optimization
title: World Representation Comparison and Optimization
kind: component
status: maintained
last_updated: 2026-08-27
owners:
  - AIBuildAI world-model group
---

# World Representation Comparison and Optimization

## Retrieval metadata

**Relevant queries:** choose world-model state, pixel versus latent versus embedding, reconstructive versus predictive state, occupancy versus video state, Cosmos3-Nano representation optimization.

**Knowledge provided:** Stable comparison axes across representation methods, evidence-supported selection patterns, failure-to-measurement mappings, Cosmos3-Nano attachment hypotheses, and unresolved questions.

**Related pages:** [Observation-space state](observation-space-state.md), [reconstructive latents](reconstructive-latents.md), [predictive embeddings](predictive-embeddings.md), [discrete and structured state](discrete-and-structured-state.md), and [multimodal state](multimodal-state.md) own method details; [evaluation methodology](../../foundations/data-and-evaluation/evaluation-methodology.md) owns general evidence rules.

## Comparison by method, not chronology

| Method | State variable | What it tends to keep | Principal loss risk | Strongest current evidence |
|---|---|---|---|---|
| Observation-space | RGB / frame stack | appearance, overlays, small objects | nuisance and compute | DIAMOND Atari; Vista video quality |
| Reconstructive latent | VAE / RSSM / codec \(z\) | compressible appearance plus some dynamics | contact and task-state erasure | DreamerV3; Predict2.5/IRASim codecs |
| Predictive embedding | target feature \(z\) | predictable semantics and motion | control-detail invariance | V-JEPA 2 probes, not 2-AC robots |
| Discrete / occupancy token | codebook grid | quantized entities or free space | recon–forecast mismatch | iVideoGPT; OccWorld Table 3 |
| Multimodal streams | typed tuple | specialist information per stream | unused or dominating stream | Cosmos3-Nano; X-WAM modes |

The rows are independent axes. Cosmos3-Nano already combines reconstructive visual latents with an AR semantic stream. Selecting “a latent world model” without naming which row is under-specified.

## Recurring supported patterns

### Optimize for the downstream reader of the state

World Models and DreamerV3 use \(z\) as a control state; DIAMOND uses pixels as the imagination observation; OccWorld uses occupancy tokens for planning metrics. Changing the reader (actor, denoiser, planner, language head) changes which information must survive. [FND-WORLD-MODELS-2018; MBRL-DREAMERV3-2025; DIASRC-PAPER; OCCSRC-PAPER]

Measure the reader’s metric, not only reconstruction or FID.

### Reconstruction is not sufficiency

OccWorld’s finer tokenizer improved reconstruction and hurt forecasting. DreamerV3’s ablation split reconstruction and reward/value gradients across tasks. DIAMOND argues some visual detail is decision-relevant in Atari. The valid synthesis is a rate–distortion–utility frontier, not “more recon is better” or “always compress.” [OCCSRC-PAPER, Table 3; MBRL-DREAMERV3-2025, Fig. 6; DIASRC-PAPER, Sec. 4]

### Do not leak variant or surface identities

V-JEPA 2 versus 2-AC, OccWorld-O versus OccWorld-S, Predict2 versus Predict2.5, DROID versus AgiBot, Policy-DROID versus base Nano, Atari versus CSGO: each binds a different state or supervision. Mixing tables fabricates a state that no checkpoint implements. [VJ2-PAPER; OCCSRC-PAPER; P25-TR; DZ-PAPER; C3-TR; DIASRC-PAPER]

### Language and latent actions are not world state

Reasoner text describes; it does not occupy space. LAPA-style quantized latent actions are action codes. Record them as invalid equivalences here; do not expand them into this Component’s methods.

### Separate codec state from decision state

A DiT denoising latent and an RSSM categorical can both be called “latent.” They answer different interfaces. Hypotheses that copy Dreamer KL coefficients onto Cosmos codec training need an explicit reader and a matched ablation. [P25-TR; MBRL-DREAMERV3-2025; C3-TR]

## Failure-to-measurement map

| Observable failure | Competing causes | Discriminating measurement |
|---|---|---|
| Sharp image, wrong contact | perceptual latent or codec stride | contact/object probes at matched decode |
| Strong probe, failed control | embedding lacks action structure | frozen versus action-conditioned error |
| High recon, low forecast | tokenizer selected on appearance | Table-3-style recon/forecast split |
| Two towers, no transfer | unused AR context | freeze Generator, swap Reasoner context |
| Cross-robot collapse | embodiment not in the state | adapter and camera/joint schema |
| Pixel WM assumed for Nano | observation-space versus codec | name the actual Nano stream |

## Cosmos3-Nano attachment map

| Target surface | Method knowledge | Testable hypothesis | Evidence required |
|---|---|---|---|
| Visual VAE tokens | reconstructive / codec | codec scale changes task-state retention | probes plus Generator metrics at matched NFE |
| Reasoner visual tokens | predictive embedding | future-feature auxiliary helps physical probes | frozen-Generator, category-held-out tests |
| Occupancy-like head | discrete structured | parallel geometric codes help driving consistency | occupancy metrics, not only FID |
| RGB-D-like depth | multimodal | depth stream improves contact without hurting RGB | AbsRel/delta versus video quality |
| Action latents | multimodal, not this Component’s action ontology | visual residual dominating action | per-modality errors |
| Policy-DROID | do not inherit base state | post-trained observation/action state is separate | bind the policy checkpoint |

Exact experiment configurations remain in the [Cosmos3-Nano optimization playbook](../../models/cosmos3-nano/optimization-playbook.md).

## Open questions

1. Which minimum state retains physical decision variables across robot, driving, and game domains?
2. When should pixels, reconstructive latents, and predictive embeddings be stacked rather than substituted?
3. Can occupancy or depth codes be added to Nano without treating them as a persistent 3D simulator?
4. How should AR semantic state be tested so that unused context is not counted as world state?
5. Which tokenizer or codec choices maximize forecast and control rather than reconstruction?

These questions define missing evidence, not work priority or workflow.

## Sources

Method-specific identities and locators are listed on the owning method pages. [C3-TR] anchors Nano attachment hypotheses; none is a reproduced optimization result.
