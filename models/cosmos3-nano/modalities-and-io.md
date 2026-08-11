---
id: world-model-kb.models.cosmos3-nano.modalities-and-io
title: Cosmos3-Nano Modality Representations and I/O Contracts
kind: reference
status: maintained
last_updated: 2026-08-11
owners:
  - AIBuildAI world-model group
---

# Cosmos3-Nano Modality Representations and I/O Contracts

## Retrieval metadata

**Relevant queries:** dataset adapter, inference request schema, observation or action mapping, modality role, AR versus DM subsequence, tensor shape, time, coordinates, or decoding.

**Knowledge provided:** typed interface facts covering raw fields, encoder paths, condition and target roles, shapes, time and coordinate conventions, checkpoint/backend scope, and output decoding. "Omnimodal" alone does not establish a specific backend contract.

**Related pages:** [Reproduction](reproduction.md) owns execution observations; mechanism-specific pages describe optimization variables; [Optimization reference](optimization-playbook.md) contains experiment-design patterns.

## Four interface layers

"Supports a modality" is incomplete. Resolve all four layers before building an adapter:

| Layer | Required question | Invalid shortcut |
|---|---|---|
| Representation | Which encoder or codec produces the model representation? | "Every modality uses one tokenizer." |
| Modeling | Is the representation AR or DM, and is it context or a prediction target? | "If the model can view an image, it can generate one." |
| Task | Which `model_mode` defines the required inputs and outputs? | "Omnimodal means arbitrary-to-arbitrary." |
| Deployment | Does the selected checkpoint and backend load the required tower and frontend? | "Unified checkpoint and Reasoner-only service are equivalent." |

The technical report primarily defines representation and modeling. Framework and serving documentation define task and deployment contracts.[C3-TR, pp.7-14; C3-FW-INFERENCE; C3-NIM-API]

## Canonical modality matrix

| Modality role | Raw form | Encoder or compression | Path | Typical role | Native decoded output |
|---|---|---|---|---|---|
| Language | text | tokenizer and embeddings | AR / Reasoner | instruction, question, semantic condition | autoregressive text tokens |
| Image understanding | RGB image | Qwen3-VL-style ViT; 16x16 patch, 2x2 merge | AR / Reasoner | caption, VQA, grounding, planning context | text |
| Video understanding | timestamped frames | ViT visual tokens plus temporal positions | AR / Reasoner | event, state-change, and temporal reasoning | text |
| Image/video generation | RGB frames | frozen Wan2.2-TI2V-5B VAE; approximately 32x32 spatial and 4x temporal compression | DM / Generator | clean visual condition or noisy generation target | image or video |
| Audio | 48 kHz stereo waveform | frozen audio VAE; hop 1,920, approximately 25 latent tokens/s | DM / Generator | audio condition or joint audiovisual target | waveform |
| Action | continuous pose, joint, or control sequence | domain-specific encoder, projection, and decoder | DM / Generator | dynamics condition or action target | continuous trajectory |
| Transfer control | edge, depth, segmentation, or related controls | control-specific condition encoder | DM / Generator | structured condition for video generation | image or video |

[C3-TR, pp.7-10, Figures 3-4; C3-FW-ARGS]

### Dual visual semantics

The same RGB file can enter two incompatible representation paths:

- **Understanding:** ViT encodes the image into AR visual tokens; Reasoner predicts text.
- **Generation:** the visual VAE encodes the image into DM latents used as a clean condition or noisy target.

I2V is not Reasoner describing an image and a separate decoder interpreting the description. Captioning is not Generator denoising an image into text. Log the selected visual frontend and sequence role in every experiment.[C3-TR, pp.7-10, Figures 3-4]

### Audio boundary

Audio belongs to the Generator/DM path. Cosmos 3 trains joint audiovisual generation, but the current official Reasoner surface does not accept audio input. Never convert base-model modality coverage into an API claim for `nvidia/cosmos3-nano-reasoner`.[C3-TR, pp.20-22 and pp.27-30; C3-REASONER-COOKBOOK]

### Action boundary

Base Nano uses domain-specific action projections for forward dynamics, inverse dynamics, and WAM. Policy-DROID adds a DROID-specific observation/action contract and post-training. These are separate inference surfaces even though Policy-DROID inherits the Nano representation.[C3-TR, pp.7-9, Figure 3 and pp.31-32; C3-FW-ACTION; C3-FW-POLICY-SERVER]

## Framework mode contracts

The fixed Cosmos Framework exposes task surfaces through `ModelMode`. Automation must read the enum and mode sample arguments from the pinned code revision instead of guessing strings from prose.[C3-FW-INFERENCE; C3-FW-ARGS; C3-FW-FAQ]

| Mode | Primary input | Model output | Typical artifact | Canonical page |
|---|---|---|---|---|
| `reasoner` | prompt; optional image/video when the vision path is available | text | `reasoner_text.txt` | [reasoner.md](reasoner.md) |
| `text2image` | prompt | image | `vision.jpg` | [generator.md](generator.md) |
| `text2video` | prompt | video | `vision.mp4` | [generator.md](generator.md) |
| `image2image` / I2I | prompt and visual condition | image | `vision.jpg` | [generator.md](generator.md) |
| `image2video` | prompt and `vision_path` | video | `vision.mp4` | [generator.md](generator.md) |
| `video2video` | prompt and `vision_path` | video | `vision.mp4` | [generator.md](generator.md) |
| `audio_image2video` | audio, image, and prompt/configuration | video and audio | media artifacts | [generator.md](generator.md) |
| `forward_dynamics` | observation, prompt, and `action_path` | future visual observation | image/video sequence | [action-modeling.md](action-modeling.md) |
| `inverse_dynamics` | observation transition, prompt, and domain configuration | action trajectory | `sample_outputs.json` | [action-modeling.md](action-modeling.md) |
| `wam` | observation, prompt, and domain configuration | action plus visual rollout | media and JSON | [action-modeling.md](action-modeling.md) |

CLI labels, enum values, and documentation labels may use abbreviations or expanded names. Bind an experiment to the exact enum value in the pinned commit.

## Reasoner I/O

### Local Framework

Reasoner mode accepts a text prompt and optional image or video. The framework samples video frames uniformly; the documented decoder sampling default is 2 FPS. It writes text to `reasoner_text.txt` and does not return media latents or continuous actions.[C3-FW-INFERENCE]

Some checkpoint configurations do not package a usable vision tower on this load path. In that case, text-only Reasoner may run while image/video input is rejected. This is a deployment constraint, not an architecture statement about all Reasoner surfaces.[C3-FW-INFERENCE]

### Reasoner-only backends and hosted service

Transformers, vLLM, and TensorRT-LLM can load only the Reasoner component. The official cookbook reports an approximate 16-17 GB Reasoner-only memory footprint, compared with an observed approximate 34 GB single-GPU memory footprint for Framework Reasoner. These figures are workload- and configuration-specific observations, not weight-file sizes or minimum-memory guarantees; visual tokens, KV cache, concurrency, precision, and backend affect peak use.[C3-REASONER-COOKBOOK]

NIM and the hosted API use an OpenAI-compatible chat-completions contract with model ID `nvidia/cosmos3-nano-reasoner`. Images are supplied as message media and text is returned in the assistant message. The service does not expose its actual checkpoint SHA, so do not label it with the local Hugging Face revision.[C3-NIM-API; C3-BUILD]

The fixed model card and service card state a Reasoner context window up to 256K tokens and recommend 4 FPS for video. The technical report records a 16K maximum training sequence, while the fixed Framework example defaults to 2 FPS preprocessing.[C3-HF, "Reasoner Input"; C3-REASONER-CARD, "Input"; C3-TR, pp.25-27; C3-FW-INFERENCE] These values respectively describe an external context claim, a service recommendation, the published training curriculum, and one local preprocessing default. Record backend, sampled frames, visual-token count, truncation, and actual request size for long-video experiments.

## Generator I/O

Generator consumes AR semantic context and one or more DM conditions, predicts continuous latents, and uses the relevant decoder to recover media or actions.

```text
text -> image
text -> video
text + image -> video
text + video/control -> video
text + image + audio -> audiovisual output
observation + action -> future observation
observation transition -> action
```

Coverage and quality vary by base, mid-trained, and post-trained checkpoint. A listed combination is not a guarantee that one checkpoint supports it with the same data or quality.[C3-TR, pp.9-10 and pp.27-32, Figures 4 and 10]

The fixed Hugging Face model card provides the following Generator **input** envelope: text up to 4,096 tokens; visual conditions at 256p, 480p, or 720p and five listed aspect ratios; input video up to 5 frames; audio up to 0.5 seconds; and action sequences spanning 16-400 video frames for listed embodiments.[C3-HF, "Generator Input"] These product-surface limits are not training-data limits and are not equivalent to output-frame caps in Framework.

The same card lists text alongside continuous Generator outputs, but the report places next-token text generation in the AR/Reasoner tower and continuous denoising in the DM/Generator tower.[C3-HF, "Generator Output"; C3-TR, pp.9-12, Figures 4-5] Use the following distinction:

- the unified checkpoint may output text through its Reasoner path;
- the Generator tower does not have a documented direct text-decoding objective.

Framework runtime caps are resolution dependent: 256p up to 400 output frames, 480p up to 300, 704/720/768p up to 200, and 1080p image-only in the fixed code. The report's 256/480/720p and 10-30 FPS training envelope describes a different layer of the system.[C3-TR, pp.27-30; C3-FW-ARGS; C3-FW-FAQ]

## Action I/O

### Canonical action families

Cosmos 3 maps domain-specific continuous actions into the shared hidden space through dedicated projections.[C3-TR, pp.7-9, Figure 3]

| Domain family | Reported canonical width | Representation note |
|---|---:|---|
| Autonomous vehicle | 9D | vehicle motion/control |
| Camera | 9D | camera pose motion |
| Egocentric human | 57D | body- and hand-related motion state |
| Single-arm robot | 10D | 3D translation, 6D rotation, grasp state |
| Dual-arm robot | 20D | two single-arm representations |
| Humanoid | 29D | humanoid-specific state |

Pose-related action families use relative SE(3) changes and a continuous 6D rotation representation.[C3-TR, pp.7-9, Figure 3] These are family-level representations, not universal raw JSON widths. The domain registry, raw action shape, normalization, adapter, and checkpoint must agree.[C3-FW-ACTION]

### Framework action fields

| Field | Contract | Validation requirement |
|---|---|---|
| `domain_name` | selects domain ID and action adapter | resolve against pinned registry and checkpoint |
| `vision_path` | provides observation or transition | validate views, frame order, crop, resolution, and timestamps |
| `action_path` | provides FD action JSON | validate shape, units, convention, and sampling rate |
| `action_chunk_size` | defines condition or prediction horizon | require H actions aligned with H+1 states |
| `view_point` | selects or interprets view | map benchmark names explicitly |
| `image_size` | defines visual size contract | record resize and crop geometry |

Forward dynamics loads an external action. Inverse dynamics and WAM create zero-action placeholders that the model replaces. The adapter adjusts visual length to `action_chunk_size + 1`, replicating boundary frames when short and truncating when long, and pads action dimensions in a domain-aware manner.[C3-FW-INFERENCE; C3-FW-ACTION]

Shape repair is not semantic repair. Replicated frames are not real observations; truncation can remove the terminal state; correct H+1 length does not establish that frame spacing matches the action-control period.

## Temporal, length, and spatial contracts

### Temporal scales

| Surface | Canonical scale | Agent constraint |
|---|---|---|
| Base visual latent | 24 FPS with 4x temporal compression, approximately 6 latent steps/s | preserve timestamps when resampling |
| Audio latent | 48 kHz stereo, hop 1,920, approximately 25 latent steps/s | align audio events to video time, not sequence index |
| Policy-DROID | 15 Hz observation and action scale | do not substitute a 24 FPS generation default |
| Framework Reasoner video | 2 FPS documented decoding default | treat as preprocessing, not Generator timing |

[C3-TR, pp.7-9 and pp.12-14; C3-FW-INFERENCE; C3-FW-POLICY-SERVER]

### Length budgets

The report gives a 16K maximum Reasoner training sequence, with approximately 2,048 visual tokens for images and 8,192 for videos. The model card separately claims a Reasoner context window up to 256K. Generator training uses approximately 74K-token packing. These budgets have different representations, densities, and objectives and must not be compared as if they were interchangeable text-token limits.[C3-TR, pp.25-30; C3-HF, "Reasoner Input"]

### Spatial layouts

Policy-DROID combines three camera views into a 540x640 canvas. General Generator uses 256p, 480p, and 720p training and runtime buckets. Resizing a policy canvas into a generic 16:9 video, or feeding a generated video back to policy without reconstructing its view layout, violates the input contract.[C3-TR, pp.27-32; C3-FW-POLICY-SERVER]

## Optimization levers

### Adapter-first decision table

| Deficit | First intervention | Do not change until isolated | Required probe |
|---|---|---|---|
| Small objects missing from Reasoner | crop/resize policy, ViT token budget, visual connector | Generator VAE | object inventory across resolutions |
| Generator loses initial-state geometry | visual VAE preprocessing, condition index, DM projection | Reasoner language model | same seed with valid, shuffled, and removed condition |
| Motion speed is wrong | timestamps, FPS, latent-time coordinates | backbone weights | identical trajectory under matched time bases |
| Action direction or magnitude is wrong | coordinate conversion, normalization, domain decoder | both towers | one-axis calibration sweep |
| New camera layout fails | view adapter or spatial encoding | action objective | canonical versus permuted-view comparison |
| Audio-video events drift | cross-modal timestamps or resampling | media quality loss | event-onset alignment metric |

### Representation changes

When changing a frontend or adapter, isolate whether the error comes from information loss or distribution shift:

1. measure a round-trip reconstruction or schema test before model inference;
2. compare the canonical encoder with the proposed encoder while holding downstream parameters fixed;
3. train only the connector or projection before unfreezing a tower;
4. evaluate both target performance and retention on the original modality path;
5. record token/latent count, time scale, and computational cost.

For action adaptation, define coordinates, units, absolute versus relative control, rotation representation, gripper convention, joint order, action rate, and inverse normalization as versioned data, not prose hidden in training code.

### System transforms

Prompt upsampling, external system prompts, guardrails, media upload, frame sampling, and output post-processing can change the observed I/O without changing model weights. Fix or ablate them before attributing a gain to the checkpoint.

## Diagnostics and failure signatures

| Symptom | First check | Interpretation |
|---|---|---|
| Local Reasoner accepts text but rejects image | loaded vision tower and backend contract | architecture support does not imply every load path exposes vision |
| Reasoner rejects audio | selected Reasoner-only surface | audio is a Generator/DM modality |
| I2V ignores input image | `vision_path`, condition index, VAE preprocessing, and sequence plan | file presence does not prove condition use |
| FD raises action shape/domain error | `domain_name`, registry, raw width, and adapter | action mapping is domain-specific |
| FD runs but motion time is wrong | frame timestamps, action rate, and chunk alignment | padding fixes shape only |
| ID/WAM returns zeros or invalid output | mode, action-generation flag, and decode path | placeholder was not replaced correctly |
| Output is shorter than requested | resolution-specific runtime cap | current implementation limits high-resolution length |
| Paper metric cannot be approached | prompt upsampling, sampler, seed count, preprocessing, judge | published protocols include system variables |
| Policy observation parses but action is wrong | three-view canvas, proprioception schema, action space | Policy-DROID has an independent contract |
| Hosted response is nonempty but unrelated | media URL/asset access and message schema | server may not have consumed the intended media |

## Experiment guidance

Before model optimization, run a contract suite:

1. **Serialization round trip:** raw sample to adapter tensors and decoded output, including shape and dtype checks.
2. **Temporal alignment:** verify timestamps for every frame, action, audio segment, and predicted horizon.
3. **Coordinate calibration:** single-axis actions with expected sign, scale, and gripper response.
4. **Condition sensitivity:** compare valid, shuffled, zeroed, and contradictory conditions with matched seeds.
5. **View sensitivity:** compare canonical, swapped, cropped, and missing camera inputs.
6. **Boundary lengths:** minimum, nominal, and maximum legal sequence, resolution, and chunk values.
7. **Backend parity:** compare identical inputs across selected backends only when checkpoint identity and preprocessing can be matched.

Persist the resolved request, not only the CLI. Framework precedence is CLI over input file over mode defaults.[C3-FW-INFERENCE; C3-FW-FAQ] A minimum run record contains:

- checkpoint or model ID and revision when available;
- backend and code commit;
- `model_mode` and fully resolved parameters;
- prompt, media hashes, sampled frame indices, timestamps, FPS, and resolution;
- action domain, width, coordinates, normalization, and rate;
- seed, sampling steps, guidance, and flow shift;
- guardrail and prompt-upsampler state;
- raw model outputs and decoded artifacts.

Store actual outcomes in [reproduction.md](reproduction.md), accepted adapter and optimization decisions in [optimization-playbook.md](optimization-playbook.md), and unresolved contract tests in [research-queue.md](research-queue.md).

## Output ownership and post-processing

Framework can enable a text blocklist, Qwen3Guard 0.6B, a video classifier, and face blurring. It can also disable or offload guardrail models.[C3-FW-INFERENCE] A refusal, blurred video, or filtered response is not a raw sample from the model distribution. Evaluation metadata must state which layers were active.

Likewise, a Generator prompt upsampler, external Reasoner system prompt, hosted-service preprocessing, action inverse normalization, and controller clipping belong to the system contract. Preserve both raw and transformed outputs when possible.

## Related knowledge

- Computation graph and invariants: [architecture.md](architecture.md)
- Reasoner behavior and optimization: [reasoner.md](reasoner.md)
- Generator behavior and optimization: [generator.md](generator.md)
- Action objectives and adapters: [action-modeling.md](action-modeling.md)
- Policy-DROID contract: [policy.md](policy.md)
- Backend setup: [inference.md](inference.md)
- Source registry: [sources.yaml](sources.yaml)
