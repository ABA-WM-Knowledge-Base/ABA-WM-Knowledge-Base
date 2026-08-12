---
id: world-model-kb.models.cosmos3-nano.reproduction
title: Cosmos3-Nano Execution-State Ledger
kind: record
status: maintained
last_updated: 2026-08-11
owners:
  - AIBuildAI world-model group
---

# Cosmos3-Nano Execution-State Ledger

## Retrieval metadata

**Relevant queries:** executed surface, local reproduction, hosted attempt, HTTP failure, retained artifact, environment snapshot, or claim status.

**Knowledge provided:** immutable execution observations, surface-specific claim states, artifact locations, raw-status interpretation, and the evidence available for each reproduction claim.

**Related pages:** [Inference](inference.md) contains reference commands; [Optimization reference](optimization-playbook.md) contains experiment-design patterns; [evaluation methodology](../../foundations/data-and-evaluation/evaluation-methodology.md) defines model-independent evidence standards. This ledger records evidence and does not schedule retries or choose a backend.

## Claim registry

| Surface | State | Decisive record | Valid claim |
|---|---|---|---|
| Hosted Reasoner | `blocked` | Two real two-case runs returned HTTP 404 for the exact served model ID | The client and audit path executed; hosted model output was not reproduced |
| Local Transformers Reasoner | `not_attempted` | No checkpoint-load or output artifact | No local Reasoner claim |
| Framework Generator | `not_attempted` | No checkpoint-load or generated-media artifact | No Generator claim |
| Policy-DROID | `not_attempted` | No policy-server or action-output artifact | No policy claim |
| Training or post-training | `not_attempted` | No training state, checkpoint, or evaluation artifact | No training claim |
| Published evaluation reproduction | `not_attempted` | No benchmark run | Published values remain source-reported results |
| RoboCasa adaptation | `not_attempted` | No fixed simulator protocol or rollout | No RoboCasa transfer claim |

[`manifest.yaml`](manifest.yaml) contains only a pointer to this registry; it does not mirror mutable states. A state may change only when the acceptance contract below is satisfied and the corresponding immutable artifacts are registered. [LOCAL-REPRO-20260809-FIRST; LOCAL-REPRO-20260809; LOCAL-ENV-20260809]

## State semantics

- `not_attempted`: no qualifying execution artifact exists.
- `blocked`: an in-scope attempt reached a prerequisite, service, resource, or interface boundary before the target output contract.
- `failed`: the target model executed far enough to evaluate its output contract, but at least one acceptance condition failed.
- `reproduced`: every declared acceptance condition passed and the complete provenance bundle is retained.
- `partial`: permitted only when a named sub-contract passes; it must not be promoted to the parent surface.

A successful mock, import, download, process exit, API authentication, or non-empty file is not sufficient evidence of model inference. Hosted success does not establish local checkpoint loading. Reasoner success does not establish Generator or policy execution.

### Raw-status mapping

The hosted harness writes raw run status `failed` whenever the requested case set does not complete successfully. That field summarizes the process outcome; it is not the KB surface state. Apply this deterministic mapping:

| Raw observation | KB state | Reason |
|---|---|---|
| No qualifying attempt artifact | `not_attempted` | No execution claim can be evaluated |
| Authentication, route, entitlement, resource, dependency, or interface boundary occurs before target-model output | `blocked` | A prerequisite prevented evaluation of the model output contract |
| Target model returns output, but content, shape, decode, metric, or acceptance checks fail | `failed` | The target output contract was reached and evaluated |
| A named sub-contract passes but the parent acceptance contract remains incomplete | `partial` | Only the named sub-contract is supported |
| Every declared acceptance condition passes | `reproduced` | The full surface claim is artifact-backed |

Both hosted summaries contain raw status `failed`, but their HTTP 404 responses occurred before any target-model output. Their KB state is therefore `blocked`, not model-execution `failed`.

## Fixed execution objects

| Object | Fixed value |
|---|---|
| Cosmos source revision | `f76cd8705dc04e5d6fba0ce0c057930b4393ad5d` |
| Hugging Face reference revision | `411f42a8fdfb8c5b2583cb8786e0938f49796eaa` |
| Hosted endpoint | `https://integrate.api.nvidia.com/v1/chat/completions` |
| Hosted model ID | `nvidia/cosmos3-nano-reasoner` |
| Hosted checkpoint revision | Not exposed by the NVIDIA service |
| Runner | Windows 11 x86-64; Python 3.12; `requests==2.32.3` |
| Local GPU | GeForce RTX 4060 Laptop GPU; 8,188 MiB |

The hosted revision must remain `unknown` unless the service exposes an immutable deployment identifier. It must not be replaced with the Hugging Face reference revision by inference. [C3-HF; C3-BUILD; LOCAL-ENV-20260809]

## Hosted Reasoner acceptance contract

The hosted surface is `reproduced` only if all conditions hold in one run:

1. The request model is exactly `nvidia/cosmos3-nano-reasoner`; no fallback model is used.
2. Both fixed image-conditioned cases pass their size and SHA256 checks.
3. Both requests return HTTP 200.
4. Both responses contain non-empty `choices[0].message.content` text.
5. The sanitized request, unmodified response JSON, extracted text, timestamps, model field, and request identifier are retained for each case.
6. The run summary points to all artifacts and contains no credential material.

The two cases are:

| Case | Input contract | Prompt | Required output |
|---|---|---|---|
| `caption` | `robot_153.jpg`; 279,410 bytes; SHA256 `886e6cfa8a0d6c4d96459cfe79b51c56aff4d63e1c523f8366f1771ea9c2788d` | `Caption the image in detail.` | Non-empty detailed image description |
| `robot_planning` | `robot_planning.png`; 230,656 bytes; SHA256 `6686b937bdb28e2c9804c435bd63a7ab56ac1531ffc9b482f2b8a75aed8770f5` | `The task is to put flower into the red bottle. Generate a plan consisting of subtasks for accomplish the task.` | Non-empty embodied task plan |

Both inputs originate from the fixed Cosmos repository revision and are indexed by [`cosmos3_reproduction/inputs/manifest.json`](../../../cosmos3_reproduction/inputs/manifest.json). These cases test visual description and text planning only; neither validates executable actions or closed-loop control. [C3-REASONER-COOKBOOK]

## Recorded hosted runs

| Run ID | Time interval, UTC | Caption | Robot planning | Raw status | KB state |
|---|---|---|---|---|---|
| `20260809T044050.760336Z` | `04:40:50.761556` to `04:40:51.125584` | HTTP 404 | HTTP 404 | `failed` | `blocked` |
| `20260809T051230.022876Z` | `05:12:30.024367` to `05:12:30.350162` | HTTP 404 | HTTP 404 | `failed` | `blocked` |

Both summaries are retained: [`20260809T044050.760336Z/run_summary.json`](../../../cosmos3_reproduction/outputs/20260809T044050.760336Z/run_summary.json) and [`20260809T051230.022876Z/run_summary.json`](../../../cosmos3_reproduction/outputs/20260809T051230.022876Z/run_summary.json). Each records two `404 page not found` responses from the configured chat-completions endpoint. The latest run also retains per-case input-integrity and request/error artifacts. No `response.json` or `output.txt` exists because neither run returned a successful completion. [LOCAL-REPRO-20260809-FIRST; LOCAL-REPRO-20260809]

### Diagnostic boundary

The retained request and error artifacts directly support these statements:

- the exact endpoint and model ID were requested;
- both official inputs passed their recorded hashes;
- two independent full runs returned HTTP 404 for both cases;
- the failure was not an HTTP 401 or 403 response;
- no target-model output was obtained.

The separate diagnostic note reports that an authenticated model catalog omitted the exact model ID, direct lookup failed, and a second credential produced the same behavior. Raw catalog and lookup responses were not retained. Treat those observations as a lower-strength operator note, not as replayable proof of service-wide availability or root cause. [LOCAL-HOSTED-DIAGNOSIS-20260809]

A related forum report indicates that another account requested Cosmos serverless entitlement. It is a community case, not an NVIDIA service-status statement and not proof of this run's root cause. [NVIDIA-FORUM-ENTITLEMENT]

## Artifact map

| Artifact | Use |
|---|---|
| [`first run summary`](../../../cosmos3_reproduction/outputs/20260809T044050.760336Z/run_summary.json) | Immutable outcome for the first two-case attempt |
| [`run_summary.json`](../../../cosmos3_reproduction/outputs/20260809T051230.022876Z/run_summary.json) | Canonical latest run outcome |
| [`event log`](../../../cosmos3_reproduction/logs/20260809T051230.022876Z.jsonl) | Ordered, sanitized execution events |
| [`caption request`](../../../cosmos3_reproduction/outputs/20260809T051230.022876Z/caption/request.json) | Exact non-secret request contract |
| [`caption error metadata`](../../../cosmos3_reproduction/outputs/20260809T051230.022876Z/caption/response_error_metadata.json) | Status and error metadata |
| [`planning request`](../../../cosmos3_reproduction/outputs/20260809T051230.022876Z/robot_planning/request.json) | Exact non-secret request contract |
| [`planning error metadata`](../../../cosmos3_reproduction/outputs/20260809T051230.022876Z/robot_planning/response_error_metadata.json) | Status and error metadata |
| [`environment snapshot`](artifacts/environment-20260809.yaml) | Host resource boundary; not checkpoint-load evidence |

## Promotion rules by surface

### Hosted Reasoner

A comparable retest retains the same model ID and two fixed cases. New timestamped artifacts preserve the blocked runs. The evidence state becomes `reproduced` only when the full hosted acceptance contract passes; AIBuildAI independently decides whether and when to run a retest.

### Local Reasoner

Require Linux, an explicitly resolved `nvidia/Cosmos3-Nano` revision, package and driver versions, exact processor inputs, raw text outputs for both fixed cases, duration, and peak allocated/reserved VRAM. An 8 GiB local GPU is below the official approximately 16-17 GB Reasoner-only observations and is not a suitable BF16 baseline target. [C3-REASONER-COOKBOOK; LOCAL-ENV-20260809]

### Framework Generator

Require fixed Cosmos Framework and checkpoint revisions, resolved inference arguments, an official T2I input, decodable non-empty `vision.jpg`, `sample_args.json`, `sample_outputs.json`, logs, duration, and memory measurements. Generator success must not change the Reasoner state. [C3-FW-INFERENCE; C3-FW-FAQ]

### Policy-DROID and RoboCasa

First validate the DROID observation/action contract and an open-loop output shape against the fixed policy checkpoint. Closed-loop promotion additionally requires a fixed simulator revision, task split, cameras, controller, action mapping, seeds, rollout count, success evaluator, safety filters, and failure taxonomy. Policy-DROID execution alone does not establish RoboCasa compatibility. [C3-POLICY-DROID-HF; C3-FW-POLICY-DROID-DOC]

## Next unmet gates

1. Hosted: observe the exact model ID in an authenticated service catalog or obtain an official route/entitlement resolution; then rerun both cases without fallback.
2. Local Reasoner: allocate a supported Linux runner with sufficient GPU memory and run the fixed Transformers contract.
3. Generator: allocate a Linux runner with at least the official capacity class and execute the fixed T2I smoke test.
4. Policy: define and test the source observation/action schema before any target-environment rollout.

[Research registry](research-queue.md) contains discriminating experiment knowledge, while [Inference](inference.md) contains executable reference commands. An unmet execution dependency is evidence about the runtime surface, not evidence for a model-quality optimization hypothesis.

## Sources

Source records are resolved through [`sources.yaml`](sources.yaml): `C3-HF`, `C3-BUILD`, `C3-REASONER-COOKBOOK`, `C3-FW-INFERENCE`, `C3-FW-FAQ`, `C3-FW-POLICY-DROID-DOC`, `C3-POLICY-DROID-HF`, `LOCAL-REPRO-20260809-FIRST`, `LOCAL-REPRO-20260809`, `LOCAL-HOSTED-DIAGNOSIS-20260809`, `LOCAL-ENV-20260809`, and `NVIDIA-FORUM-ENTITLEMENT`.
