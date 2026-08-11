---
id: world-model-kb.models.cosmos3-nano.codebase
title: Cosmos3-Nano Codebase Map
kind: reference
status: maintained
last_updated: 2026-08-11
owners:
  - AIBuildAI world-model group
---

# Cosmos3-Nano Codebase Map

## Retrieval metadata

**Relevant queries:** repository responsibility, class or function location, call path, configuration ownership, task-mode extension, checkpoint conversion, or regression fixture location.

**Knowledge provided:** pinned source locations, runtime and training call graphs, configuration precedence, checkpoint lifecycle, and implementation-level invariants.

**Related pages:** [Inference](inference.md) contains commands and resource characteristics; [Evaluation](evaluation.md) owns benchmark interpretation; [Reproduction](reproduction.md) owns observed execution outcomes.

## Fixed source graph

| Object | Fixed reference | Code responsibility |
|---|---|---|
| Release and cookbook repository | `NVIDIA/cosmos@f76cd8705dc04e5d6fba0ce0c057930b4393ad5d` | Backend recipes, examples, deployment notes, and inference benchmark tables |
| Runtime and training framework | `NVIDIA/cosmos-framework@4155d61d14b14e05a8cafe2bd796d090fcb5f145` | Native model implementation, inference, SFT/post-training, checkpoint conversion, and policy server |
| Base checkpoint | `nvidia/Cosmos3-Nano@411f42a8fdfb8c5b2583cb8786e0938f49796eaa` | Root configuration, processor/tokenizer, safetensors, Diffusers components, and assets |
| Policy checkpoint | `nvidia/Cosmos3-Nano-Policy-DROID@6706d7680581c255ff61e0f3bb49d90eac55c79e` | DROID-specific post-trained policy parameters |

[C3-REPO; C3-FW; C3-HF; C3-POLICY-DROID-HF]

Never resolve a code fact from the local `cosmos-predict2.5` repository. It implements an earlier model family with different packages, registries, dependencies, checkpoints, and conditioning architecture.

## Repository responsibility boundaries

### `NVIDIA/cosmos`

Use this repository to select a supported backend, copy a pinned example, inspect reference assets, and read published performance tables. It is not the native PyTorch implementation of the full Cosmos 3 model. [C3-COOKBOOK; C3-REASONER-COOKBOOK; C3-INFERENCE-BENCHMARKS]

### `NVIDIA/cosmos-framework`

Use this repository for model classes, task modes, input adaptation, generation, training, checkpoint conversion, guardrails, and policy serving. Its `AGENTS.md` is the canonical high-level code map for the fixed revision. [C3-FW-AGENTS]

### Hugging Face model repositories

Use the HF repositories for weights, model configuration, processors, assets, and revision-bound deployment. A served model ID does not reveal the deployed revision; never substitute the reference HF SHA for an unexposed hosted SHA.

## Inference call path

```text
python -m cosmos_framework.scripts.inference
  -> parse CLI and parallelism arguments
  -> load mode defaults
  -> load input JSON or directory
  -> merge sample fields and CLI overrides
  -> validate SampleMeta and capability gates
  -> resolve/download checkpoint
  -> construct Cosmos3OmniModel / OmniInference
  -> route by ModelMode
       reasoner           -> AR processor -> generate_reasoner_text
       media generation   -> build conditions -> generate_samples_from_batch
       FD / ID / WAM      -> action adapter -> diffusion/action decode
  -> decode media/action/text
  -> write resolved arguments and outputs
```

The public offline entry point is `python -m cosmos_framework.scripts.inference`. [C3-FW-INFERENCE]

## Configuration precedence

The effective sample is assembled in this order:

1. mode-specific built-in defaults;
2. fields from the input JSON or sample directory;
3. CLI overrides applied to the selected run.

`OmniSampleOverrides.build_sample()` performs the final merge and validation. The output-side `sample_args.json` is the canonical resolved configuration; the original command alone is insufficient for debugging or comparison. [C3-FW-ARGS; C3-FW-FAQ]

When adding a sampling field, update all owners of that field:

- the relevant `SamplingArgs` and override model;
- each applicable mode default file;
- merge/forwarding logic in `OmniSampleOverrides.build_sample()`;
- serialization into resolved artifacts;
- validation and at least one mode-specific regression fixture.

## Core implementation map

| Fixed code location | Key object | Agent use |
|---|---|---|
| [`inference/args.py`](https://github.com/NVIDIA/cosmos-framework/blob/4155d61d14b14e05a8cafe2bd796d090fcb5f145/cosmos_framework/inference/args.py#L157-L202) | `ModelMode` | Verify exact public mode names and avoid inventing aliases |
| [`inference/args.py`](https://github.com/NVIDIA/cosmos-framework/blob/4155d61d14b14e05a8cafe2bd796d090fcb5f145/cosmos_framework/inference/args.py#L298-L720) | `SampleMeta` and modality argument models | Locate required fields and capability gates |
| [`inference/args.py`](https://github.com/NVIDIA/cosmos-framework/blob/4155d61d14b14e05a8cafe2bd796d090fcb5f145/cosmos_framework/inference/args.py#L1026-L1131) | `OmniSampleArgs`, `OmniSampleOverrides` | Trace defaults, precedence, and resolved sampling parameters |
| [`inference/model.py`](https://github.com/NVIDIA/cosmos-framework/blob/4155d61d14b14e05a8cafe2bd796d090fcb5f145/cosmos_framework/inference/model.py#L432-L578) | `Cosmos3OmniConfig`, `Cosmos3OmniModel` | Trace root/Diffusers weight mapping and load hooks |
| [`inference/inference.py`](https://github.com/NVIDIA/cosmos-framework/blob/4155d61d14b14e05a8cafe2bd796d090fcb5f145/cosmos_framework/inference/inference.py#L600-L675) | `_get_reasoner_sample_data()`, `get_sample_data()` | Trace raw input to model batch |
| [`inference/inference.py`](https://github.com/NVIDIA/cosmos-framework/blob/4155d61d14b14e05a8cafe2bd796d090fcb5f145/cosmos_framework/inference/inference.py#L1872-L1954) | `_generate_reasoner_batch()` | Trace Reasoner generation and text artifact output |
| [`model/generator/omni_mot_model.py`](https://github.com/NVIDIA/cosmos-framework/blob/4155d61d14b14e05a8cafe2bd796d090fcb5f145/cosmos_framework/model/generator/omni_mot_model.py#L2686) | `generate_samples_from_batch()` | Primary diffusion/flow generation entry |
| [`model/generator/omni_mot_model.py`](https://github.com/NVIDIA/cosmos-framework/blob/4155d61d14b14e05a8cafe2bd796d090fcb5f145/cosmos_framework/model/generator/omni_mot_model.py#L4796) | `generate_reasoner_text()` | Framework AR text generation entry |
| [`inference/action.py`](https://github.com/NVIDIA/cosmos-framework/blob/4155d61d14b14e05a8cafe2bd796d090fcb5f145/cosmos_framework/inference/action.py#L40-L212) | action loading and batch builders | Trace domain, width, observation length, padding, FD, ID, and WAM semantics |
| [`scripts/action_policy_server_robolab.py`](https://github.com/NVIDIA/cosmos-framework/blob/4155d61d14b14e05a8cafe2bd796d090fcb5f145/cosmos_framework/scripts/action_policy_server_robolab.py#L279-L633) | `RobolabServerArgs`, `RobolabPolicyService` | Trace Policy-DROID preprocessing, inference, and server output |
| [`scripts/train.py`](https://github.com/NVIDIA/cosmos-framework/blob/4155d61d14b14e05a8cafe2bd796d090fcb5f145/cosmos_framework/scripts/train.py) | `--sft-toml` training entry | Trace public SFT/post-training launch |
| [`configs/toml_config/sft_config.py`](https://github.com/NVIDIA/cosmos-framework/blob/4155d61d14b14e05a8cafe2bd796d090fcb5f145/cosmos_framework/configs/toml_config/sft_config.py) | `SFTExperimentConfig` | Validate structured recipe fields before launch |

[C3-FW-ARGS; C3-FW-MODEL; C3-FW-OMNI-MOT; C3-FW-ACTION; C3-FW-POLICY-SERVER; C3-FW-TRAINING]

## Mode invariants

| Mode family | Required semantic invariant | Common implementation error |
|---|---|---|
| Reasoner | Output remains autoregressive text; image/video inputs use the Reasoner visual path | Routing an image through the Generator VAE and calling the result reasoning |
| T2I/T2V/I2V/V2V | Visual targets use the diffusion path and compatible VAE/config | Reusing a Reasoner-only load or mismatched checkpoint layout |
| Forward dynamics | Actions are conditions; output is a future visual observation | Omitting `action_path` or using the wrong domain/action width |
| Inverse dynamics | Observed transition conditions action prediction | Treating the initialized zero-action placeholder as final output |
| WAM | Model predicts action and optional future visual state jointly | Calling the mode `policy` or attributing Policy-DROID behavior to base WAM |
| Policy-DROID | DROID observation/action transform and policy checkpoint are both required | Changing only the checkpoint string while leaving embodiment semantics undefined |

## Training and checkpoint lifecycle

```text
public dataset / structured JSONL
  -> recipe TOML + experiment SKU
  -> checkpoint conversion
       generator/action: HF -> DCP
       Nano Reasoner: LM + public vision tower -> VLM safetensors
  -> cosmos_framework.scripts.train --sft-toml=<recipe>
  -> resolved config + DCP iteration state + per-rank RNG state
  -> export_model
  -> inference safetensors
  -> optional Diffusers conversion
```

The public framework exposes SFT/post-training recipes, not a data-equivalent reproduction of the internal foundation-scale pre-training and mid-training curricula. [C3-FW-TRAINING]

Do not interchange checkpoint layouts:

- a base HF snapshot is an initialization source;
- DCP stores distributed training and resume state;
- exported safetensors are inference-oriented;
- Diffusers conversion is a separate layout;
- hosted service revisions may remain undisclosed.

## Code-change routing

| Intended change | Primary owner | Required adjacent checks |
|---|---|---|
| Add or rename a task mode | `ModelMode`, sample schema, mode defaults, routing | CLI parsing, capability gate, serialization, output artifact |
| Add a sampling parameter | argument model and override merge | defaults, resolved config, backend forwarding, determinism |
| Change attention or tower logic | `omni_mot_model.py` and model config | AR/DM visibility mask, checkpoint compatibility, both Reasoner and Generator regression |
| Change visual preprocessing | processor or sample-data construction | Reasoner/Generator path separation, resolution/FPS/token budgets |
| Add an action domain | action registry, encoder/decoder, metadata | raw width, coordinate frame, normalization, padding, decode round trip |
| Change policy observation/action mapping | policy server transform | camera layout, history, gripper convention, inverse normalization, safety layer |
| Change training recipe fields | TOML schema, experiment SKU, launcher | resolved config, resume compatibility, output/export path |
| Change checkpoint loading | model wrapper and conversion scripts | root/Diffusers/DCP formats, missing vision tower, strict revision tests |

## Minimum regression contract

Evidence that improves interpretability of a code modification includes:

1. fixed code commit or diff;
2. resolved configuration before and after the change;
3. one smallest valid fixture for every affected mode;
4. shape, dtype, device, and finite-value assertions at the modified boundary;
5. deterministic comparison when the change is not intended to alter output;
6. target metric plus a regression slice when output is intended to change;
7. fresh output directory containing `sample_args.json`, `sample_outputs.json`, and the expected media/text/action artifact;
8. failure classification when the run does not reach model execution.

## Change-risk signals

- An unfixed repository or checkpoint revision prevents exact attribution.
- A change that crosses Reasoner, Generator, action, and policy boundaries without separate regression fixtures confounds component effects.
- A missing resolved configuration makes the effective experiment unknown.
- An action-domain change without an explicit coordinate and normalization contract can be numerically valid but semantically unsafe.
- Checkpoint deletion or conversion without verified source and destination layouts risks irreversible corruption.
- A runtime result alone does not establish model quality; [Evaluation](evaluation.md) and [Execution state](reproduction.md) provide the relevant distinctions.
