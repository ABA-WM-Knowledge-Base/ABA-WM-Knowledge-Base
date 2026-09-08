---
id: world-model-kb.models.cosmos3-nano.inference
title: Cosmos3-Nano Inference Knowledge Guide
kind: guide
status: maintained
last_updated: 2026-09-08
owners:
  - AIBuildAI world-model group
---

# Cosmos3-Nano Inference Knowledge Guide

## Retrieval metadata

**Relevant queries:** backend characteristics, environment dependencies, reference commands, runtime memory, output artifacts, serving paths, few-step Generator inference, NFE, latency, or inference failure symptoms.

**Knowledge provided:** documented backend options, reference configurations, resource observations, command examples, artifact fields, and failure interpretations. These references do not select tools or authorize execution.

**Related pages:** [Reproduction](reproduction.md) records whether a path actually ran; [Evaluation](evaluation.md) interprets model quality; [Optimization reference](optimization-playbook.md) collects experiment-design patterns; [Few-Step and One-Step Video Distillation](../../components/fast-video-inference/few-step-distillation.md) owns the cross-paper distinction among step count, NFE, denoising time, and end-to-end latency.

## Backend capability map

Backend compatibility depends on the required output, component, input contract, hardware, platform, resource class, revision visibility, and available artifacts. Hosted, Transformers/vLLM, full-Framework, and Policy-DROID results are distinct execution surfaces and are not interchangeable evidence. The table below provides strategy-relevant backend knowledge; AIBuildAI retains tool and execution choices.

## Task-to-backend matrix

| Required output | Preferred first backend | Loaded scope | Typical memory class | Output contract |
|---|---|---|---:|---|
| Image/video understanding to text | Transformers Reasoner | Approximately 8B AR component | Approximately 16–17 GB | Non-empty decoded text |
| Reasoner service or concurrency tests | vLLM | Reasoner-only serving | Approximately 16–17 GB plus cache | OpenAI-compatible response |
| Packaged self-hosted Reasoner API | NVIDIA NIM | Reasoner engine | Backend-dependent | Local chat completion |
| No-local-GPU Reasoner probe | NVIDIA Build hosted API | Remote Reasoner | Client only | Hosted chat completion |
| T2I/T2V/I2V/V2V/audio/transfer/action | Cosmos Framework | Unified checkpoint and modality stack | Documented 32 GB Nano class; mode-specific peak unresolved | Media/action artifacts plus resolved args |
| Omni-model serving | vLLM-Omni or supported integrated runtime | Unified model | Large accelerator, mode-dependent | OpenAI-compatible omni endpoint |
| DROID closed-loop policy | Framework policy server | Policy-DROID checkpoint and adapter | Multi-GPU reference deployment | Action dictionary; optional predicted video |

[C3-REASONER-COOKBOOK; C3-FW-INFERENCE; C3-INFERENCE-BENCHMARKS; C3-FW-POLICY-DROID-DOC]

Memory values are reference observations, not guaranteed minima. The cookbook's approximately 34 GB observation is specifically a single-GPU Framework **Reasoner** workload; it is not a Generator/action measurement. Visual-token count, KV cache, VAE, classifier-free guidance, guardrails, compilation, precision, concurrency, and allocator behavior change peak memory.

## Platform and resource considerations

| Check | Compatibility information |
|---|---|
| Operating system | Use Linux for supported local paths; do not treat native Windows as a validated Cosmos 3 platform |
| GPU architecture | Use a supported NVIDIA Ampere, Hopper, or Blackwell target for documented paths |
| Precision | BF16 is the tested checkpoint precision; quantized or other precision is a separate experiment |
| CUDA/toolchain | Match the fixed cookbook/framework dependency group; do not reuse a Predict2.5 environment |
| GPU memory | Reserve approximately 16–17 GB for Reasoner-only; use at least the documented 32 GB Nano class for unified Framework planning, then measure the selected Generator/action mode rather than importing the 34 GB Framework Reasoner observation |
| Disk | Include checkpoint, environment, caches, compile artifacts, and output media |
| Authentication | Separate HF, NGC, and hosted API credentials; never log secret values |

[C3-HF; C3-REASONER-CARD; C3-FW-SETUP; C3-FW-FAQ]

A resource mismatch predicts OOM or uncontrolled offload and does not measure model quality. A compatible runner or a separately identified compression/offload experiment yields more interpretable evidence; the consuming workflow decides which path to take.

## Environment isolation

Use one environment per backend family. Never merge these into the local `cosmos-predict2.5` environment.

| Environment | Intended surface | Dependency-scope note |
|---|---|---|
| Reasoner Transformers | Direct single-process Reasoner | Full Framework training groups |
| vLLM Reasoner | OpenAI-compatible Reasoner serving | Legacy Cosmos3 plugin when native support is used |
| Reasoner NIM | Packaged container service | Host Python model dependencies |
| Cosmos Framework | Unified Generator/action/training | Unpinned ad hoc wheels |
| Policy server | Policy-DROID service and client | General Generator assumptions about observation/action I/O |

Record Python, PyTorch, CUDA runtime, Transformers/vLLM/Framework version, GPU, driver, and exact lockfile or container digest.

## Route A: hosted Reasoner

Endpoint contract:

```text
POST https://integrate.api.nvidia.com/v1/chat/completions
model = nvidia/cosmos3-nano-reasoner
```

The request must use an OpenAI-compatible multimodal message, a fixed input URL or uploaded asset, `stream=false`, and an explicit output token limit. The hosted service does not expose its checkpoint SHA. [C3-NIM-API; C3-BUILD]

Minimal request shape:

```json
{
  "model": "nvidia/cosmos3-nano-reasoner",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "image_url",
          "image_url": {"url": "https://example.invalid/fixed-image.jpg"}
        },
        {"type": "text", "text": "Caption the image in detail."}
      ]
    }
  ],
  "stream": false,
  "seed": 0,
  "max_tokens": 4096
}
```

Hosted success requires HTTP 200 and non-empty `choices[0].message.content` for the declared case. Never switch to another model on 404. The current service state is owned by [reproduction.md](reproduction.md).

Retry policy:

- missing key: exit before network access;
- 401/403: credential or entitlement failure, no retry loop;
- 404: model/catalog/route mismatch, no model substitution;
- 429 or 5xx: at most three bounded exponential-backoff retries;
- 400/422 caused by remote media transport: use the documented asset-upload path, then delete the temporary asset;
- always redact authorization material from requests, errors, and logs.

## Route B: Transformers-only Reasoner

Environment:

```bash
uv venv --python 3.13 --seed --managed-python
source .venv/bin/activate
uv pip install --torch-backend=auto \
  accelerate av pillow "safetensors>=0.8.0" torch \
  "torchvision==0.25.0" "transformers>=5.11.0"
```

Fixed image example:

```python
from pathlib import Path

import torch
from transformers import AutoProcessor, Cosmos3OmniForConditionalGeneration

MODEL_ID = "nvidia/Cosmos3-Nano"
REVISION = "411f42a8fdfb8c5b2583cb8786e0938f49796eaa"
IMAGE = Path("assets/robot_153.jpg").resolve()

processor = AutoProcessor.from_pretrained(MODEL_ID, revision=REVISION)
model = Cosmos3OmniForConditionalGeneration.from_pretrained(
    MODEL_ID,
    revision=REVISION,
    dtype=torch.bfloat16,
    device_map="auto",
)

messages = [{
    "role": "user",
    "content": [
        {"type": "image", "path": str(IMAGE)},
        {"type": "text", "text": "Caption the image in detail."},
    ],
}]
inputs = processor.apply_chat_template(
    messages,
    tokenize=True,
    add_generation_prompt=True,
    return_dict=True,
    return_tensors="pt",
).to(model.device, torch.bfloat16)

generated = model.generate(**inputs, do_sample=False, max_new_tokens=512)
trimmed = [out[len(inp):] for inp, out in zip(inputs.input_ids, generated)]
text = processor.batch_decode(
    trimmed,
    skip_special_tokens=True,
    clean_up_tokenization_spaces=False,
)[0]
assert text.strip()
print(text)
```

[C3-COOKBOOK; C3-REASONER-COOKBOOK]

Record the resolved HF snapshot, package lock, peak allocated/reserved VRAM, prompt/input hash, raw text, and latency. `device_map="auto"` must not hide uncontrolled CPU offload in a baseline; record the final device map.

## Route C: vLLM Reasoner service

The fixed cookbook uses native Cosmos 3 support in vLLM 0.23. Do not combine it with an older plugin recipe unless the experiment explicitly compares the two paths. [C3-COOKBOOK]

```bash
uv venv --python 3.13 --seed --managed-python
source .venv/bin/activate
uv pip install --torch-backend=cu130 "vllm==0.23.0"

CUDA_VISIBLE_DEVICES=0 vllm serve nvidia/Cosmos3-Nano \
  --tensor-parallel-size 1 \
  --mm-encoder-tp-mode data \
  --async-scheduling \
  --allowed-local-media-path "$(pwd)" \
  --media-io-kwargs '{"video":{"num_frames":-1}}' \
  --port 8000
```

If DeepGEMM is unavailable, test with `VLLM_USE_DEEP_GEMM=0`. Preserve server arguments, served model list, health output, client concurrency, TTFT, request latency, token throughput, and peak memory.

Client contract:

```python
from pathlib import Path
import openai

client = openai.OpenAI(api_key="EMPTY", base_url="http://127.0.0.1:8000/v1")
served_model = client.models.list().data[0].id
response = client.chat.completions.create(
    model=served_model,
    messages=[{"role": "user", "content": [
        {"type": "image_url", "image_url": {
            "url": Path("assets/robot_153.jpg").resolve().as_uri()
        }},
        {"type": "text", "text": "Caption the image in detail."},
    ]}],
    max_tokens=512,
    seed=0,
)
assert response.choices[0].message.content.strip()
```

## Route D: Reasoner NIM

The fixed cookbook uses `nvcr.io/nim/nvidia/cosmos3-reasoner:1.7.0`. This is a self-hosted container, not the free hosted Build endpoint. [C3-COOKBOOK; C3-NIM-API]

```bash
export NGC_API_KEY="<NGC key>"
echo "$NGC_API_KEY" | docker login nvcr.io \
  --username '$oauthtoken' --password-stdin

docker run --runtime=nvidia --gpus all \
  --shm-size=32GB \
  -e NGC_API_KEY="$NGC_API_KEY" \
  -e NIM_MODEL_SIZE=nano \
  -v ~/.cache/nim:/opt/nim/.cache \
  -u "$(id -u)" \
  -p 8000:8000 \
  nvcr.io/nim/nvidia/cosmos3-reasoner:1.7.0
```

Readiness endpoint: `GET http://127.0.0.1:8000/v1/health/ready`.

Chat endpoint: `POST http://127.0.0.1:8000/v1/chat/completions` with served model `nvidia/cosmos3-nano-reasoner`.

## Route E: unified Framework smoke test

Use T2I with one output frame as the smallest Generator execution gate.

```bash
git clone https://github.com/NVIDIA/cosmos-framework.git
cd cosmos-framework
git checkout 4155d61d14b14e05a8cafe2bd796d090fcb5f145

export GIT_LFS_SKIP_SMUDGE=1
uv sync --all-extras --group=cu130-train
source .venv/bin/activate

python -m cosmos_framework.scripts.inference \
  --parallelism-preset=latency \
  -i inputs/omni/t2i.json \
  -o outputs/omni_nano_t2i_<run-id> \
  --checkpoint-path Cosmos3-Nano \
  --seed=0 \
  --no-guardrails
```

[C3-FW-SETUP; C3-FW-INFERENCE]

`--no-guardrails` is acceptable only for an isolated technical smoke test that separates model loading from gated guardrail dependencies. Production or quality evaluation must record the actual guardrail state and version.

Success requires all of the following:

- process completion without a recorded sample error;
- fresh output directory;
- resolved `sample_args.json`;
- `sample_outputs.json` indicating success;
- decodable, non-empty `vision.jpg` with expected dimensions;
- fixed checkpoint/code identity;
- wall-clock and peak memory record.

For OOM, diagnose in order:

1. confirm component scope and resolved mode;
2. distinguish allocation fragmentation from true capacity;
3. verify visible GPUs and actual parallel mesh;
4. apply documented sharding or guardrail offload;
5. separate compile failure from capacity failure;
6. move to a suitable runner rather than weakening the model identity or success contract.

## Route F: Policy-DROID service

The policy server uses a separate dependency group and defaults to the Policy-DROID checkpoint. [C3-FW-POLICY-DROID-DOC; C3-FW-POLICY-SERVER]

```bash
python -m cosmos_framework.scripts.action_policy_server_robolab \
  --checkpoint-path nvidia/Cosmos3-Nano-Policy-DROID \
  --port 8000
```

Server startup is not a policy-success claim. Before a new embodiment can connect, define camera layout, proprioceptive keys, action coordinates, normalization, gripper convention, action horizon, control frequency, safety constraints, and termination semantics. Use [Policy](policy.md) and [Optimization playbook](optimization-playbook.md).

## Failure classifier

| Symptom | Classification | Next action |
|---|---|---|
| 401/403 | Credential or entitlement | Verify the correct credential domain; do not retry as model failure |
| 404 exact model ID | Catalog or route state | Preserve response and model list; do not switch models |
| 400/422 media request | Input/transport contract | Validate media URL, type, size, and asset API path |
| Model load rejects visual input | Missing/incompatible vision tower or config | Inspect checkpoint layout and backend capability gate |
| CUDA OOM before sampling | Capacity/configuration | Inspect loaded components, mesh, cache, guards, and resolved dimensions |
| CUDA OOM during sampling | Workload peak | Inspect frames, resolution, CFG, VAE, cache, and allocator trace |
| Empty text with HTTP 200 | Output-contract failure | Preserve raw response and prompt; fail the case |
| Valid file but wrong dimensions/frames | Resolved-config or decode failure | Compare output metadata with `sample_args.json` |
| Zero or unchanged ID/WAM action | Action path or decode failure | Check mode, action generation flag, placeholder replacement, and adapter |
| Policy action out of range | Interface/normalization failure | Stop execution; verify coordinate, statistics, units, and postprocessing |

## Reproducibility artifact fields

A run record is more reproducible when it includes:

- run ID and UTC timestamps;
- model/checkpoint/service ID and exposed revision;
- code commit or container digest;
- input manifest and content hashes;
- raw prompt and structured conditions;
- resolved configuration;
- seed, precision, backend, device map, and parallelism;
- package lock or image digest;
- stdout/stderr or server logs;
- raw response or model output;
- expected task artifact and validation result;
- latency and peak memory when local;
- explicit pass/fail reason with no automatic model substitution.

The existence of an artifact is not sufficient; validate content, shape, decode, freshness, and task semantics.
