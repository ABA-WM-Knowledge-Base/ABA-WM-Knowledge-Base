---
id: world-model-kb.papers.ervla.codebase
title: ERVLA Implementation Surface and Closest Public Code
kind: reference
status: maintained
last_updated: 2026-08-21
owners:
  - AIBuildAI world-model group
---

# ERVLA Implementation Surface and Closest Public Code

## Retrieval metadata

**Relevant queries:** ERVLA code, ERVLA checkpoint, CoT corpus release, where to implement reasoning dropout, CoT next-token loss implementation, choice branch implementation, knowledge truncation implementation, ACoT-VLA code, Xiaomi xr1 as a proxy implementation.

**Knowledge provided:** the release state of ERVLA's own artifacts, the public code trees that implement the same mechanisms (the `xr1` trainer for the choice branch and flow head; the aibuildai `xr1_cot` extension for the CoT loss; ACoT-VLA for a different action-CoT design), and the mapping from paper mechanism to code surface.

**Related pages:** [`paper.md`](paper.md) owns claims; [Xiaomi-Robotics-1 codebase](../../models/xiaomi-robotics-1/codebase.md) owns the xr1 tree; [`reproduction.md`](reproduction.md) owns execution state.

## 1. Release state

At the access date the project page announces code, data, and checkpoints as forthcoming; no repository, corpus, or weights are public. Every implementation statement below therefore maps the paper's mechanism to OTHER public code that realizes the same idea, labelled as proxies. [ERV-PROJECT]

## 2. Mechanism-to-surface map

| Paper mechanism | Closest public surface | Notes |
|---|---|---|
| Flow-matching DiT head with Beta timestep sampling | `xr1/mibot/models/VLA/XR1.py` (`xr1.forward`, `_generate`) | Same backbone family (Qwen3-VL-4B) and head design; shared authors |
| Choice policy branch + score loss | `XR1.py:compute_choice_loss`, `action_projector_choice`, `score_projector_choice` | 5 candidates, L1 best-of-K, score MSE |
| Knowledge truncation (DiT reads only the semantic prefix cache) | `custom_collate.py` `action_vlm_condition_segments` + `XR1._unpad` | The DiT cache is cut at the last `<|im_start|>` before `<state>`, i.e. the prefix before action tokens |
| `/cot` vs `/no_cot` rendering | `json_dataset.py:_prompt` appends `/no_cot` and `<cot></cot>`; the eval client offers `--cot` | The public trainer renders only `/no_cot` |
| CoT next-token loss | absent in `xr1` (`skip_logits=True`); aibuildai `mibot/ext/xr1_cot.py` adds CE over the labelled `<cot>` span | Our implementation of the described mechanism, not ERVLA's code |
| CoT annotation pipeline (detectors + simulator replay) | absent; aibuildai `gen_cot_labels.py` uses a VLM over keyframes | Different content source; grounded positions from replay are not reproduced |
| Action-oriented CoT alternative | `AgibotTech/ACoT-VLA` | Different design (action chain-of-thought); public |

[XR1-CODE; ERV-ACOT-CODE]

## 3. Tensor contract for a CoT loss on the xr1 stack

Packed sequence per batch: `[user turn with 3 images + instruction + suffix] [assistant <cot>TEXT</cot>] [user "Robot state: <state>"] [assistant <a_0>..<score>]`. Labels: -100 everywhere except the CoT assistant content through its `<|im_end|>`; the logit for position p is computed from hidden state p-1 through `vlm.lm_head` at labelled positions only (avoids a full-vocabulary logits tensor over the packed batch). Loss added as `cot_coefficient x CE` to the released loss dict. [aibuildai `mibot/ext/vlabench_data.py`, `mibot/ext/xr1_cot.py`]

## 4. Documentation/code mismatches to watch

- The xr1 eval client's `--cot` flag only drops the pre-filled `<cot></cot>` turn; the HF model generates no text, so it does not implement ERVLA-style reasoning at inference either. [XR1-CODE-EVAL-VLABENCH; XR1-HF-VLABENCH]
- ERVLA's `p_cot` is unstated; Xiaomi-Robotics-1 uses 50 %.

## Sources

[ERV-PAPER]; [ERV-PROJECT]; [ERV-ACOT-CODE]; [XR1-CODE]; [XR1-CODE-EVAL-VLABENCH]; [XR1-HF-VLABENCH].
