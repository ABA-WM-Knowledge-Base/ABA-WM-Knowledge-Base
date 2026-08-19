---
id: world-model-kb.models.cosmos3-nano.reasoner
title: Cosmos3-Nano Reasoner Optimization Reference
kind: reference
status: maintained
last_updated: 2026-08-19
owners:
  - AIBuildAI world-model group
---

# Cosmos3-Nano Reasoner Optimization Reference

## Retrieval metadata

**Relevant queries:** multimodal understanding, physical or temporal reasoning, task decomposition, text grounding, failure explanation, or AR semantic context.

**Knowledge provided:** Reasoner identity, mechanisms, deployment contracts, output schemas, capability-specific levers, failure interpretations, and published evaluation evidence.

**Related pages:** [Generator](generator.md) covers continuous media; [Action modeling](action-modeling.md) covers action decoding; [Policy](policy.md) covers DROID control; [Reproduction](reproduction.md) records runtime outcomes. Foundation context is owned by [world foundation models](../../foundations/definitions-and-taxonomy/world-foundation-model.md), [representation learning and JEPA](../../foundations/representations/representation-learning-and-jepa.md), and [evaluation methodology](../../foundations/data-and-evaluation/evaluation-methodology.md). [Explicit physical reasoning](../../components/reasoning/explicit-physical-reasoning.md) and [reasoning–generation–action integration](../../components/reasoning/reasoning-generation-action.md) own the applicable cross-paper method syntheses.

## Identity and capability boundary

Cosmos3-Nano Reasoner is the approximately 8B autoregressive tower inside unified Nano. It consumes text plus optional image/video visual tokens and predicts text with a causal next-token objective.[C3-TR, pp.11-15, Figure 5 and Table 3]

The name "Reasoner" can refer to three different surfaces. Always record which one is used:

| Surface | Identity | Revision visibility | Typical use |
|---|---|---|---|
| Reasoner component | AR tower within `nvidia/Cosmos3-Nano` | tied to the unified checkpoint revision | joint Nano experiments |
| Reasoner-only local load | Transformers, vLLM, or TensorRT-LLM loading only relevant weights | local revision is recordable | memory-efficient local inference or tuning |
| Hosted Reasoner | `nvidia/cosmos3-nano-reasoner` on NVIDIA API/NIM | actual server checkpoint SHA is not public | managed image-conditioned inference |

[C3-REASONER-COOKBOOK; C3-NIM-API; C3-BUILD]

Native Reasoner contract:

```text
text + optional image/video -> autoregressive text
```

Supported task families include detailed scene description, object and relation recognition, physical and causal explanation, robot-task planning and subtask decomposition, visual grounding expressed in text, and temporal reasoning over video.[C3-TR, pp.49-54; C3-REASONER-COOKBOOK]

The following are outside the native contract:

- image, video, or audio latent generation;
- audio input on the current official Reasoner surface;
- domain-adapted continuous action tensors;
- guaranteed feasible closed-loop plans;
- Policy-DROID action chunks;
- within-call access to a rollout currently being denoised by Generator.

[C3-TR, pp.9-12, Figures 4-5; C3-REASONER-COOKBOOK]

Natural-language planning is a semantic intermediate. It becomes executable only after grounding, action-space conversion, controller and safety checks, and closed-loop observation updates.

## Canonical mechanisms and invariants

### Input encoding

Text uses the tokenizer and language embeddings. Image and video inputs use a Qwen3-VL-style ViT with 16x16 patches and 2x2 token merging. The ViT and multimodal connector are trained with Reasoner; this path is distinct from the frozen Wan2.2 VAE used for Generator visual latents.[C3-TR, pp.7-10, Figures 3-4]

Video reasoning depends on frame selection and temporal positions. The fixed Framework uniformly samples frames and documents 2 FPS as a decoder-sampling default. This is a local preprocessing default, not a statement about all training-video frame rates.[C3-FW-INFERENCE]

### Autoregressive objective

Reasoner applies causal next-token prediction to AR tokens. AR queries attend only to AR key/value states, even when the unified sequence contains DM tokens. Diffusion state therefore does not rewrite the current Reasoner hidden state.[C3-TR, pp.9-12, Figures 4-5]

Optimization constraints:

- Preserve causal masking unless the experiment explicitly tests an architecture change.
- Treat visual-token sampling, ordering, and timestamps as part of the input distribution.
- Do not use a Generator loss as a proxy for improved Reasoner output unless AR behavior is evaluated directly.
- For rollout critique, use an external decode, re-encode, and re-invoke loop.

### Relation to Generator

DM queries can attend to AR states, so Generator can use Reasoner semantic context. AR queries cannot attend to DM states. Improving Reasoner may therefore improve Generator condition quality, but this transfer must be measured; a Reasoner benchmark gain does not prove better media or action generation.[C3-TR, pp.11-14, Figure 5 and Table 2]

### Training initialization and scale

Reasoner is initialized from Qwen3-VL-8B. The language model, vision encoder, and multimodal connector are trained together rather than restricting updates to a lightweight adapter. Published pre-training uses next-token prediction with a maximum 16K context, approximately 2,048 visual tokens for images, and 8,192 for videos.[C3-TR, pp.25-27]

| Stage | Reported sample count | Primary role |
|---|---:|---|
| Multimodal pre-training | 22,002,013 | general and physical-world visual-language learning |
| Supervised fine-tuning | 2,171,673 | instruction following, physical reasoning, and Physical AI tasks |

[C3-TR, p.15, Table 3 and Figure 7]

Pre-training runs for 2 epochs. SFT runs for 8,200 iterations at global batch size 512 and mixes pre-training:SFT examples at 1:4, retaining part of the pre-training distribution during instruction tuning.[C3-TR, pp.25-27]

Use [data.md](data.md) for dataset composition and [training.md](training.md) for optimizer, compute, and parameter-update details.

## Deployment contracts

| Surface | Loaded scope | Approximate cookbook memory footprint | Media input | Output |
|---|---|---:|---|---|
| Cosmos Framework | unified Nano path | approximately 34 GB observed for single-GPU Framework Reasoner | depends on packaged/configured vision tower | `reasoner_text.txt` |
| Transformers | Reasoner-only | approximately 16-17 GB starting scale | cookbook demonstrates image input; verify vision config | text |
| vLLM | Reasoner-only serving | approximately 16-17 GB starting scale | image/video examples | OpenAI-compatible text |
| TensorRT-LLM | compiled Reasoner-only engine | engine dependent | engine dependent | text |
| NIM / hosted API | server managed | no client model load | service supports image-conditioned requests | chat-completion text |

The cookbook values are observed memory footprints for its documented workloads and configurations, not weight-file sizes or hardware guarantees. KV cache, visual tokens, precision, concurrency, and implementation change peak use.[C3-REASONER-COOKBOOK; C3-FW-INFERENCE; C3-NIM-API]

Framework `reasoner` mode accepts a prompt and optional image/video and writes text. A checkpoint load path without an available vision tower may reject media while text-only Reasoner still works. Do not switch to a different model and label that as success.[C3-FW-INFERENCE]

Hosted/NIM requests use chat-completions semantics with model ID `nvidia/cosmos3-nano-reasoner`; media can be a supported URL or asset reference. Entitlement, media limits, and catalog availability are service state, not model capability.[C3-NIM-API; C3-BUILD]

## Output schemas for optimization

Free-form answer quality is too ambiguous for automated model improvement. Convert tasks into typed outputs whenever possible:

| Reasoner output class | Suggested schema | Direct metric | Must not be treated as |
|---|---|---|---|
| Scene state | objects, attributes, relations, confidence | entity/relation precision and recall | metric 3D state truth |
| Physical explanation | initial state, event, mechanism, predicted consequence | causal-choice or counterfactual consistency | numerical dynamics simulation |
| Subtask plan | ordered subgoals, preconditions, completion tests | ordering, prerequisite, and terminal-condition accuracy | executable joint command |
| Grounding | object ID, region/point, reference frame | localization and referring-expression accuracy | calibrated robot coordinates |
| Failure diagnosis | observed discrepancy, candidate cause, discriminating test | diagnosis accuracy and test usefulness | proof that the named cause occurred |
| Action reasoning in text | intended motion, constraints, expected outcome | semantic consistency | action decoder output |

Require the model to separate observations, inferences, and proposed actions. This makes hallucination, missing-state, and planning failures independently measurable.

## Optimization levers

### Diagnose before choosing the trainable surface

| Failure class | First lever | Escalation path | Retention set |
|---|---|---|---|
| Objects or relations are missed | resolution, crop, frame selection, visual-token budget | visual connector, then ViT adaptation | general VQA and OCR-like probes |
| Correct perception, wrong physical inference | physical counterfactual data and causal SFT | selective Reasoner unfreezing | general reasoning and instruction following |
| Correct states, wrong subgoal order | structured planning examples with explicit preconditions | plan-specific adapter or tower tuning | perception and short-plan probes |
| Video events are reordered | temporal sampling, timestamps, key-state coverage | temporal curriculum and longer-context tuning | image reasoning and short video |
| Grounding is verbose but inaccurate | coordinate schema, region supervision, resolution | connector and localization-focused tuning | caption and relation accuracy |
| Output is generic or unparseable | explicit schema, decoding constraints, targeted SFT | output-head or tower adaptation | answer correctness under original prompts |
| Domain accuracy improves but general ability drops | replay mixture and lower update scope | regularization or parameter-efficient tuning | published general benchmark subset |

Start with preprocessing and output-schema controls. If the model has the relevant information but fails to use it, adapt the connector or Reasoner. If information is destroyed before encoding, tower tuning will not repair the input.

### Data construction

High-value Reasoner optimization data separates intermediate capabilities:

- paired images that differ in one relation, contact, containment, or object state;
- short videos with annotated state transitions and temporally reversed controls;
- counterfactual physical questions that vary one causal factor;
- task plans annotated with preconditions, failure recovery, and termination tests;
- hard negatives containing visually plausible but nonexistent objects or relations;
- failed-policy rollouts with verified failure labels and discriminating observations;
- multiple instruction granularities for the same task while holding observations fixed.

Avoid training only on long free-form rationales. Include schema-constrained targets and direct-answer metrics so style gains cannot masquerade as reasoning gains.

### Parameter scope

Use a staged intervention:

1. fixed-model prompt/schema baseline;
2. data and preprocessing ablation;
3. connector or parameter-efficient adaptation;
4. selective ViT or upper-Reasoner unfreezing;
5. broader tower tuning only after retention and compute estimates are available.

When changing ViT or shared AR representations, also test Generator condition adherence because DM queries consume AR context.

### External imagination loop

To test whether imagined futures improve reasoning:

```text
Reasoner creates candidate plan or action semantics
  -> Generator/WAM predicts candidate outcomes
  -> outcomes are decoded and re-encoded
  -> Reasoner ranks, critiques, or revises
```

Use controls with no rollout, shuffled rollout, and real environment transition. Separate errors from proposal quality, rollout accuracy, re-encoding, critique, and final selection. Move a successful system pattern to [optimization-playbook.md](optimization-playbook.md); keep untested variants in [research-queue.md](research-queue.md).

## Diagnostics and failure signatures

| Signature | Likely cause | Minimum diagnostic |
|---|---|---|
| Hallucinates absent objects or contact | insufficient visual resolution, occlusion, language prior | structured object inventory plus crop and no-image controls |
| Plan is semantically correct but infeasible | missing geometry, IK, collision, or gripper constraints | score semantic plan separately from grounding and controller feasibility |
| Video event order is wrong | sparse sampling or lost temporal coordinates | persist sampled frame indices and timestamps; add key-state frames |
| Answer is generic | underspecified task or output schema | compare free-form and typed prompts with identical input |
| Local media input is rejected | vision tower unavailable on selected load path | audit backend, checkpoint config, and loaded tensors |
| Hosted 401/403 | key or entitlement | classify as credential/access failure; do not alter model ID |
| Hosted 404 for model | catalog does not expose target ID | preserve response and stop model substitution |
| Hosted 429/5xx | quota or transient service error | bounded retry with per-attempt timestamps |
| Nonempty response is unrelated to image | media URL inaccessible, expired asset, or malformed message | use a diagnostic image with an unambiguous control question and inspect redacted request |
| Domain tuning improves prose but not task accuracy | style shift or answer leakage | blind structured metrics and held-out counterfactuals |
| Short clips work, long clips fail | frame budget, temporal aliasing, or state-memory limits | length sweep with constant event density and token accounting |

Prior Cosmos work reported risks including object permanence, contact dynamics, instruction following, gravity, lighting, and fluids. Treat these as lineage-derived test priorities, not observed Cosmos3-Nano Reasoner failures.[C1-TR, p.58]

## Evaluation guidance

The report aggregates 48 Reasoner benchmarks into four groups. Nano reports the following group averages:[C3-TR, p.51, Table 10]

| Group | Cosmos3-Nano | Qwen3-VL-8B baseline |
|---|---:|---:|
| General | 69.6 | 68.9 |
| Robotics | 55.1 | 48.5 |
| Smart infrastructure | 61.0 | 52.7 |
| Driving | 76.0 | 46.4 |

These are aggregates over heterogeneous tasks, metrics, and sample counts. They support a narrow hypothesis that Physical AI data and training improve domain-group performance. They do not establish universal superiority, executable planning, RoboCasa success, or equivalence between a hosted endpoint and the paper checkpoint. Nano remains behind Gemini 3.1 Pro in the report's general reasoning aggregation, with a smaller gap in robotics.[C3-TR, pp.52-53]

For model optimization, use a ladder rather than one aggregate:

1. perception: entities, attributes, relations, and state;
2. temporal tracking: state transitions, occlusion, and persistence;
3. physical inference: contact, support, containment, causality, and counterfactuals;
4. affordance and constraint inference;
5. subgoal ordering and recovery;
6. grounding into a benchmark-compatible schema;
7. correlation with downstream action selection or control success.

Report exact tasks and sample counts. Use [evaluation.md](evaluation.md) for published protocols. A valid optimization claim requires improvement on the target rung, no unacceptable regression on the retention set, and a downstream test when the claimed benefit concerns action or generation.

## Experiment template

For each Reasoner experiment, record:

- surface: unified component, local Reasoner-only, or hosted model ID;
- checkpoint revision when visible, backend, code commit, and preprocessing;
- text prompt/system prompt, media hashes, frames, timestamps, resolution, and visual-token count;
- output schema and decoding parameters;
- trainable and frozen modules, data mixture, loss, and learning-rate groups;
- target, retention, calibration, and downstream metrics;
- matched baseline, seed set, confidence interval, and failure slices;
- raw outputs and parse failures.

Recommended ablations include no image, shuffled frames, reversed video, image-only versus image-plus-history, free-form versus typed output, generic versus domain data, connector-only versus tower tuning, and with/without replay data.

Execution results belong in [reproduction.md](reproduction.md). Optimization decisions belong in [optimization-playbook.md](optimization-playbook.md). Questions such as hosted checkpoint identity, visual-preprocessing details, and rollout-critique value belong in [research-queue.md](research-queue.md) until resolved.

## Related knowledge

- Architecture and attention invariants: [architecture.md](architecture.md)
- Input and backend contracts: [modalities-and-io.md](modalities-and-io.md)
- Data and training: [data.md](data.md), [training.md](training.md), [post-training.md](post-training.md)
- Published evaluation and limitations: [evaluation.md](evaluation.md), [limitations.md](limitations.md)
- Inference setup: [inference.md](inference.md)
- Source registry: [sources.yaml](sources.yaml)
