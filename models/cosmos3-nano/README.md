---
id: world-model-kb.models.cosmos3-nano
title: Cosmos3-Nano Agent Knowledge Entry
kind: model
status: maintained
last_updated: 2026-08-19
owners:
  - AIBuildAI world-model group
---

# Cosmos3-Nano Agent Knowledge Entry

## Retrieval metadata

**Relevant queries:** Cosmos 3, Cosmos3-Nano, Reasoner, Generator, action modeling, Policy-DROID, inference, evaluation, adaptation, or model optimization.

**Knowledge provided:** model identity boundaries, topic ownership, a document map, and high-level capability distinctions.

**Related pages:** [`agent-index.yaml`](agent-index.yaml) provides machine-readable profiles for dynamic knowledge retrieval; [`manifest.yaml`](manifest.yaml) provides model identity and fixed revisions. The Foundation pages for [world models](../../foundations/definitions-and-taxonomy/world-model.md), [world foundation models](../../foundations/definitions-and-taxonomy/world-foundation-model.md), and [world action models](../../foundations/definitions-and-taxonomy/world-action-model.md) own model-independent definitions. The Components for [Reasoning](../../components/reasoning/README.md) and [Generative Modeling](../../components/generative-modeling/README.md) own cross-paper capability evolution. None of these resources defines AIBuildAI workflow orchestration.

## Retrieval integration

[`agent-index.yaml`](agent-index.yaml) groups related queries with knowledge, strategies, best practices, and evidence that can ground design and implementation decisions. AIBuildAI may dynamically select and combine those profiles according to the current task and state. The catalog does not decide Agent selection, repository selection, task sequencing, or execution scheduling.

Source tokens resolve through [`sources.yaml`](sources.yaml). Executed-state claims are recorded in [`reproduction.md`](reproduction.md), while topic pages contain stable model knowledge. This is a knowledge-ownership distinction, not an instruction about how AIBuildAI must plan or execute a task.

## Identity constraints

| Object | Correct scope | Never infer |
|---|---|---|
| `nvidia/Cosmos3-Nano` | Unified approximately 16B base checkpoint with an approximately 8B autoregressive tower and an approximately 8B diffusion tower | That every backend loads both towers or exposes every modality |
| Reasoner component | Autoregressive text output conditioned on text and optional image/video inputs | Continuous robot action output or image/video generation |
| `nvidia/cosmos3-nano-reasoner` | Hosted or served Reasoner model ID | The hosted checkpoint SHA or equality with a local HF revision |
| Generator component | Rectified-flow generation of continuous visual, audio, and action representations | A safety-certified simulator or a general robot policy |
| Base action modes | Forward dynamics, inverse dynamics, and WAM surfaces using domain-specific action adapters | DROID policy results without policy-specific post-training |
| `nvidia/Cosmos3-Nano-Policy-DROID` | DROID-specific post-trained policy checkpoint | Zero-shot RoboCasa compatibility |
| Super T2I/I2V checkpoints | Cosmos3-Super specialization branches | Base Nano image/video scores |

[C3-TR, pp.9–14 and pp.25–32; C3-HF; C3-HF-BLOG; C3-POLICY-DROID-HF]

## Model graph

```text
Qwen3-VL-8B initialization
  -> Reasoner pre-training and Physical AI SFT
  -> frozen/initialized AR context for Generator training
  -> Generator image/video/audio pre-training
  -> action- and transfer-inclusive mid-training
  -> base nvidia/Cosmos3-Nano
       -> Reasoner-only deployment surfaces
       -> media and action generation surfaces
       -> DROID-specific policy post-training
            -> nvidia/Cosmos3-Nano-Policy-DROID
```

The autoregressive subsequence contains language and ViT visual tokens. The diffusion subsequence contains VAE visual tokens, audio latents, action representations, and control conditions. Diffusion queries may attend to autoregressive context; autoregressive queries do not consume diffusion state during the same denoising pass. [C3-TR, pp.9–14, Figures 4–6]

## Retrieval profile catalog

The profiles below are knowledge groupings for dynamic retrieval. Their content can influence diagnosis and strategy selection, but the profiles do not select or order AIBuildAI work.

| Query family | Profile ID | Knowledge scope |
|---|---|---|
| Identity, scale, revision, license, or lineage | `model_identity` | Model and checkpoint identity |
| Architecture, attention, modalities, preprocessing, or I/O | `architecture_and_interfaces` | Computation and interface facts |
| Visual/physical reasoning or planning text | `reasoner_knowledge` | Reasoner mechanisms and evidence |
| Image, video, audio-video, physics, or control generation | `generator_knowledge` | Generator mechanisms and evidence |
| Forward dynamics, inverse dynamics, WAM, or action representation | `action_and_wam_knowledge` | Action-modeling semantics |
| Policy-DROID, embodiment transfer, or RoboCasa | `policy_and_embodiment_knowledge` | Policy and control interfaces |
| Data, objective, curriculum, optimizer, or post-training | `data_and_training_knowledge` | Learning state and variables |
| Source code, configuration, or checkpoint conversion | `implementation_knowledge` | Fixed-revision code locations |
| Inference, serving, runtime symptom, or resources | `runtime_knowledge` | Runtime references and observations |
| Benchmark, metric, comparison, or ablation | `evaluation_knowledge` | Evaluation conditions and results |
| Experiment-design pattern or unresolved question | `optimization_and_open_questions` | Optional design references and evidence gaps |

## Experiment-design context

[Optimization reference](optimization-playbook.md) collects scientific design patterns such as checkpoint binding, causal hypotheses, matched baselines, metrics, and artifacts. These patterns help assess evidence quality; the AIBuildAI workflow remains responsible for deciding whether, when, and how to use them.

## Canonical ownership map

### Model semantics

- [Architecture and computation](architecture.md)
- [Modality and I/O contracts](modalities-and-io.md)
- [Reasoner](reasoner.md)
- [Generator](generator.md)
- [Action modeling](action-modeling.md)
- [Policy-DROID](policy.md)

### Learning and evaluation

- [Data system](data.md)
- [Training curriculum](training.md)
- [Post-training and adaptation](post-training.md)
- [Evaluation protocols](evaluation.md)
- [Limitations and risk boundaries](limitations.md)

### Execution and optimization

- [Codebase map](codebase.md)
- [Inference decision guide](inference.md)
- [Execution-state ledger](reproduction.md)
- [Optimization playbook](optimization-playbook.md)
- [Research queue](research-queue.md)

## Evidence interpretation boundaries

- A result is uniquely interpretable when checkpoint or served model ID, code revision, task mode, input contract, and evaluation protocol are known.
- Fluency, visual realism, PSNR, and leaderboard rank are not equivalent to physical correctness or task success.
- Reasoner plans are text outputs rather than controller commands.
- Direct and best-of-N results represent different inference budgets.
- Dynamic leaderboard claims require a snapshot date for reproducible interpretation.
- Documentation, a mocked request, a process exit code, or a non-empty file does not by itself establish model inference reproduction.
- Unresolved assumptions remain hypotheses rather than model facts until supporting evidence exists.
