---
id: world-model-kb.models.xiaomi-robotics-1.codebase
title: Xiaomi-Robotics-1 Codebase Map
kind: reference
status: maintained
last_updated: 2026-08-21
owners:
  - AIBuildAI world-model group
---

# Xiaomi-Robotics-1 Codebase Map

## Retrieval metadata

**Relevant queries:** Xiaomi-Robotics-1 repository, xr1 package, mibot, XR1.py, json_dataset.py, custom_collate.py, base_runner.py, cfg_utils.py, weight_convert.py, deploy/server.py, deploy/client.py, eval_vlabench/main.py, dispatch.py, merge_results.py, modeling_mibot.py, processing_mibot.py, call path, configuration precedence.

**Knowledge provided:** the fixed source graph at the pinned revision, the responsibility boundary of each directory, the two serving paths, the inference call path, configuration precedence, and the code-change impact map for post-training on VLABench.

**Related pages:** [Architecture](architecture.md) owns computation; [Inference](inference.md) owns runtime; [Training](training.md) owns defaults; [VLABench codebase](../../papers/vlabench/codebase.md) owns the simulator side.

## Fixed source graph

| Object | Revision | Role |
|---|---|---|
| `XiaomiRobotics/Xiaomi-Robotics-1` | `556cca33963a2b36d835a40374c3b4c8eef68401` | trainer, servers, eval clients |
| `XiaomiRobotics/Xiaomi-Robotics-1-VLABench` (HF) | `f4986843002d86502e2e53079ca06d00a33abffc` | remote code + weights + processor |
| `XiaomiRobotics/Xiaomi-Robotics-1-5B` (HF) | `ee21d524b5c52ac961d941e1bc7d6d92836c3d5e` | `model_states.pt` |
| `OpenMOSS/VLABench` | `cf588fe60c0c7282174fe979f5913170cfe69017` | simulator, tracks, evaluator |

[XR1-CODE; XR1-HF-VLABENCH; XR1-HF-5B; VLAB-CODE]

## Repository responsibility boundaries

```text
Xiaomi-Robotics-1/
|-- xr1/                      post-training + real-robot runtime (package `mibot`)
|   |-- configs/{config,data/load_washer,model/posttrain,trainer/deepspeed}.yaml
|   |-- tools/train.py        Hydra entry: DATASETS.build(cfg.data), MIMODEL.build(cfg.model), Lightning Trainer
|   |-- tools/weight_convert.py   HF AutoModel -> {"module": {"model."+k: v}} model_states.pt
|   |-- scripts/train.sh      torchrun launcher (RESOURCE_GPU, WORLD_SIZE/RANK/MASTER_*), MAX_LENGTH=20000
|   |-- scripts/deploy.sh     tmux servers of mibot/server/deploy.py (npz protocol)
|   |-- mibot/data/{datamodule/base_datamodule,datasets/json_dataset,collate/custom_collate}.py
|   |-- mibot/models/{__init__ (MIMODEL registry), runner/base_runner, VLA/XR1, VLM/qwen3vl}.py
|   |-- mibot/server/{deploy.py, runtime/{server,client}.py}
|   `-- mibot/utils/{io,cfg_utils,cosine_warmup,model_utils}.py
|-- deploy/{server,client}.py HF-format server (pickle protocol) + AutoProcessor client
|-- scripts/{deploy,launch_vlabench,launch_robocasa,launch_robocasa365}.sh
|-- eval_vlabench/{main,dispatch,merge_results}.py + README.md
|-- eval_robocasa/, eval_robocasa365/
`-- docs/DEPLOYMENT.md
```

[XR1-CODE]

## Two serving paths (not interoperable)

| Path | Loads | Protocol | Processor | Client |
|---|---|---|---|---|
| HF (`deploy/server.py`) | `AutoModel.from_pretrained(trust_remote_code)` safetensors dir | pickle, length-prefixed; request = processor batch + `task_id` + `seed`; reply = normalized `actions` | `MiBotProcessor` from the model dir (`action_config` per robot type) | `deploy/client.py` (decodes with `decode_action`), used by all benchmark evals |
| Trainer runtime (`mibot/server/deploy.py`) | `config.py` + `last.ckpt/checkpoint/mp_rank_00_model_states.pt` | npz, length-prefixed; server normalizes state/action with the data config's stats | `Qwen/Qwen3-VL-4B-Instruct` processor | `mibot/server/runtime/client.py` (real-robot state dict, `action_prefix`, crops) |

A trainer checkpoint reaches the benchmark evals only through an export to the HF layout (inverse of `weight_convert.py`, keeping the reference's 1,120 keys). [XR1-CODE]

## Inference call path (HF)

```text
client.processor.apply_chat_template(messages, state=(1,1,60), robot_type) -> batch
  -> socket -> Server: model(**batch) -> MiBoTForActionGeneration.forward
       -> self.vlm(**kwargs, use_cache=True)            (Qwen3VLForConditionalGeneration)
       -> position ids / masks for 1 + state + K tokens
       -> torch.manual_seed(seed); x = randn_like(action_mask)
       -> 5 x dit_forward(x, t) Euler                    (DiT + projectors + sink)
       -> ActionGenerationOutput(actions=x)              (normalized)
  <- client: processor.decode_action(actions, robot_type) = x * std + mean
```

[XR1-HF-VLABENCH, `modeling_mibot.py`, `processing_mibot.py`; XR1-CODE, `deploy/*.py`]

## Configuration precedence (trainer)

Hydra defaults `data: load_washer`, `model: posttrain`, `trainer: deepspeed` in `configs/config.yaml`; command-line overrides win; `cfg_utils.helper` moves optimizer/scheduler under `model.params`, sets `default_root_dir = <root>/project_<project>/<exp_name>`, seeds `42 + RANK`, dumps `config.py`/`config.yaml` into the run dir and `./assets/config.py`. `MAX_LENGTH` is read from the environment by the collate. [XR1-CODE, `cfg_utils.py`, `custom_collate.py`]

## Core implementation map

| Mechanism | Location |
|---|---|
| MoT model, losses, prefix, sampler | `xr1/mibot/models/VLA/XR1.py` (`xr1`, `DiT`, `DecoderLayer`, `compute_flow_loss`, `compute_choice_loss`, `_generate`) |
| VLM with state token injection and `skip_logits` | `xr1/mibot/models/VLM/qwen3vl.py` (`Qwen3VLForConditionalGeneration.forward`) |
| Strict pretrained load, optimizer groups | `xr1/mibot/models/runner/base_runner.py` |
| Slot layout, normalizers, masks, rotation math | `xr1/mibot/utils/io.py` (`ACTION_PARTS`, `compose_state`, `normalize_quantile`, `rotm2aa_batch`, `recover_action`) |
| Real-robot JSON dataset | `xr1/mibot/data/datasets/json_dataset.py` |
| Packed collate, special-token ids, mRoPE positions | `xr1/mibot/data/collate/custom_collate.py` |
| Checkpoint writer | `tools/train.py` (`ModelCheckpoint(save_top_k=-1, save_last=True, every_n_train_steps=save_interval)`) |
| VLABench policy/client | `eval_vlabench/main.py` (`VLABenchPolicy`, `_build_messages`, `_model_state`, `predict`) |
| Track dispatch and folding | `eval_vlabench/dispatch.py`, `eval_vlabench/merge_results.py` |

## Code-change impact map (VLABench post-training)

| Change | Touches | Invalidates |
|---|---|---|
| New data conventions | a new dataset/collate (ext module), not `JsonDataset` | nothing served, if stats exported |
| CoT next-token loss | subclass of `xr1` with a VLM forward hook, labels from the collate | nothing served |
| Stats change | data config + processor `action_config` on export | any HF dir exported with old stats |
| Chunk length change | stats shape `(K, 60)` + processor | client `--action-chunk-size` |
| Client settings | `eval_vlabench` args | comparability with the released numbers |

## Minimum regression contract

Export an untrained warm start and score it: its L2 must match the released checkpoint's within noise. That single run validates importer, exporter, processor, data conventions, and serving together.

## Sources

[XR1-CODE]; [XR1-CODE-XR1-README]; [XR1-CODE-EVAL-VLABENCH]; [XR1-HF-VLABENCH]; [XR1-HF-5B]; [VLAB-CODE].
