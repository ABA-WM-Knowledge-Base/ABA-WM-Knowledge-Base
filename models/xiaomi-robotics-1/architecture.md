---
id: world-model-kb.models.xiaomi-robotics-1.architecture
title: Xiaomi-Robotics-1 Architecture and Computation Semantics
kind: model
status: maintained
last_updated: 2026-08-21
owners:
  - AIBuildAI world-model group
---

# Xiaomi-Robotics-1 Architecture and Computation Semantics

## Retrieval metadata

**Relevant queries:** Mixture-of-Transformers, Qwen3-VL-4B backbone, DiT action head, KV-cache coupling, sink token, state projector, action projector, adaLN, mRoPE position ids, 2B/5B/10B sizes, parameter counts.

**Knowledge provided:** the component boundaries, tensor flow, attention visibility, parameter lineage, and the invariants a post-training intervention must respect.

**Related pages:** [Modality contracts](modalities-and-io.md) owns input/output shapes; [VLM backbone](vlm-backbone.md) and [Action head](action-head.md) own component behaviour; [Codebase](codebase.md) owns file locations; [diffusion and flow matching](../../foundations/learning-objectives/diffusion-and-flow-matching.md) owns the objective family.

## Canonical model boundaries

The technical report describes a Mixture-of-Transformers (MoT) policy: a pre-trained vision-language model (VLM, Qwen3-VL) and a diffusion transformer (DiT) with the same number of layers but a smaller hidden size. Three sizes are reported; one is released. [XR1-TR, Table 1]

| Variant | Layers | VLM hidden | VLM params | DiT hidden | DiT params | Total | Released |
|---|---:|---:|---:|---:|---:|---:|---|
| 2B | 28 | 2048 | 2.1B | 1024 | 470M | 2.6B | no |
| **5B** | 36 | 2560 | 4.4B | 1024 | 604M | 5.1B | yes (`Xiaomi-Robotics-1-5B` + fine-tunes) |
| 10B | 36 | 4096 | 8.8B | 2048 | 1.5B | 10.5B | no |

The pinned implementation builds the 5B VLM from `Qwen/Qwen3-VL-4B-Instruct`'s config and the DiT with `layer_num=36`, `hidden_size=1024`, `head_dim=128`, 8 KV heads. [XR1-CODE, `xr1/mibot/models/VLA/XR1.py`]

## Transformer specification

```text
images (3 views) + instruction + <state> + [<a_0>..<a_{K-1}> <score>]   (VLM sequence)
        | Qwen3-VL-4B: vision tower (deepstack) + 36-layer text decoder
        | per-layer KV cache  ------------------------------------------+
                                                                        |
[sink] + state_projector(state_60d) + action_projector(noisy_chunk)     |   (DiT sequence, 1 + 1 + K tokens)
        | 36 DiT layers; each layer attends to [VLM KV of layer i ; own causal tokens]
        | adaLN modulation from t_projector(t_embedder(1000 * t))
        v
action_output_layer -> velocity field over the K x 60 chunk
```

- DiT position ids continue the VLM's mRoPE sequence (`max(position_ids) + 1 + arange(query_length)`), with +10 added to the non-prefix action positions; a rotary embedding built from the VLM text config supplies cos/sin. [XR1-CODE, `XR1.py:forward`]
- Attention mask = [cache mask over VLM tokens | causal mask over DiT tokens]; in training with an action prefix longer than 2, prefix columns are randomly masked with probability 0.5 (keeping the last 2). [XR1-CODE, `_random_mask_prefix`]
- The DiT block is pre-norm attention + SwiGLU MLP (4x) with a learned `adaln_table` (6 x hidden) added to the timestep modulation; qkv projection has bias, output projection does not; q/k RMSNorm per head. [XR1-CODE, `DecoderLayer`, `Attention`]
- Training additionally reads VLM hidden states at the `<a_i>` tokens into `action_projector_choice` (5 candidate chunks x 60) and at `<score>` into `score_projector_choice` (5 scores). These modules exist only in the trainer model. [XR1-CODE, `XR1.py:_build_model`]

## Core mechanisms and invariants

1. **One VLM pass per chunk.** The VLM runs once with `use_cache=True`; all 5 denoising Euler steps reuse its KV cache. Changing the image count or prompt changes the cache length but not the DiT. [XR1-CODE]
2. **Fixed 60-D slot layout.** Action and state tensors are always 60-wide; robot types differ only by which slots carry non-zero std (mask). The VLABench fine-tune uses slots 0..6. [XR1-HF-VLABENCH, `preprocessor_config.json`]
3. **Frozen input embeddings.** `get_input_embeddings().requires_grad_(False)`; everything else, including the vision tower (with gradient checkpointing) and the language MLPs (checkpointed), trains. [XR1-CODE]
4. **No text generation at serving.** `MiBoTForActionGeneration.forward` computes the VLM cache and the DiT rollout; it never samples tokens. A `/cot` prompt only changes the prompt text. [XR1-HF-VLABENCH, `modeling_mibot.py`]
5. **bf16 throughout.** Weights, DiT inputs, and state are cast to bf16 in both trainer and server; losses are computed in fp32. [XR1-CODE]

## Parameter lineage and update scope

Pre-training and post-training update the whole network except the token embeddings (report: "the model is trained end to end"); benchmark fine-tunes start from the post-trained 5B. The HF benchmark checkpoints contain 1,120 tensors: `vlm.*`, `dit.*`, `state_projector`, `action_projector`, `action_output_layer`, `t_embedder`, `t_projector`, `sink`; `vlm.lm_head.weight` is tied to the embeddings and not stored; the `*_choice` heads (12 tensors) and the `<a_i>` / `<score>` token embeddings (`vlm.model.action_embed.weight`, `vlm.model.score_embed.weight`) are absent - 15 trainer tensors in all, measured 2026-08-21 against the 1,135-tensor base `model_states.pt`. [XR1-HF-VLABENCH, `model.safetensors.index.json`; XR1-HF-5B]

## Optimization levers

| Lever | Implementation surface | Expected signal | Constraint or regression risk | Validation |
|---|---|---|---|---|
| Denoising steps (`num_steps`) | HF `forward(num_steps=...)`; trainer `self.num_steps=5` | Latency vs chunk quality | Released stats were produced with 5 | Paired L2 episodes at 3/5/10 steps |
| Freeze the vision tower | `self.vlm.model.visual.requires_grad_(False)` | Memory and speed; texture-track generalization up or down | Released recipe trains it | Track-6 SR with and without |
| DiT-only fine-tune | freeze `self.vlm` | Cheapest adaptation; language tracks may stagnate | VLM carries instruction grounding | Track-3/4 SR vs full |
| Action prefix length (`async_train`) | `XR1.forward` prefix sampling 1..6 | Robustness under latency; no effect on the synchronous eval client | Eval replans without a prefix | Only measurable with a prefix-aware client |

Hypotheses, not observed results; none is reported in the technical report.

## Diagnostics and failure signatures

- A loss that starts at a fresh-init magnitude after `pretrained=` points at a key mismatch; the trainer raises on any missing/unexpected key, so a silent partial load cannot occur. [XR1-CODE, `BaseRunner.configure_model`]
- A served chunk shorter than 5 rows or narrower than 7 columns raises in the client; a chunk whose length differs from 10 means the processor action_config was replaced. [XR1-CODE-EVAL-VLABENCH]

## Sources

[XR1-TR] Table 1 and Sec. 3; [XR1-CODE] `xr1/mibot/models/VLA/XR1.py`; [XR1-HF-VLABENCH] `config.json`, `modeling_mibot.py`, `model.safetensors.index.json`.
