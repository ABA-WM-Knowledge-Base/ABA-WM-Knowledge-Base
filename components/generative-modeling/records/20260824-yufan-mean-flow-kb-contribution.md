---
id: world-model-kb.components.generative-modeling.records.yufan-mean-flow-kb-contribution
title: YUFAN Mean Flow Knowledge Contribution Record
kind: record
status: maintained
last_updated: 2026-08-24
owners:
  - downeyflyfan
---

# YUFAN Mean Flow Knowledge Contribution Record

## Scope

| Field | Value |
|---|---|
| Branch | `YUFAN` |
| Base branch | `main` |
| Repository | `ABA-WM-Knowledge-Base` |
| Contributor identity | `downeyflyfan` |
| Knowledge area | Flow Matching, MeanFlow, Improved MeanFlow, Pixel MeanFlow |
| Source access date | 2026-08-24 |

## Sources reviewed

- Mean Flows for One-step Generative Modeling, arXiv:2505.13447.
- Improved Mean Flows: On the Challenges of Fastforward Generative Models, arXiv:2512.02012 version 2.
- One-step Latent-free Image Generation with Pixel Mean Flows, arXiv:2601.22158 version 3.
- Official Improved MeanFlow implementation: `Lyy-iiis/imeanflow`.
- Official Pixel MeanFlow implementation: `Lyy-iiis/pMF`.

## Repository changes

- Added the canonical component page `mean-flow-and-pixel-mean-flow.md`.
- Added source identities and implementation identities to the Generative Modeling source registry.
- Added the method page to the Generative Modeling map.
- Linked the new page from Flow Matching and Rectified Flow.
- Added MeanFlow and Pixel MeanFlow to the global topic index.

## Validation

Command:

```text
/tmp/aba-wm-kb-venv/bin/python tools/validate_kb.py
```

Result: validation passed. Existing warnings concern unavailable Windows-local paths already present on the workstation-independent main branch; no new validation errors or warnings were introduced by this contribution.

## Evidence boundary

The paper metrics remain image-generation evidence. The knowledge page records transfer hypotheses for video and action-conditioned flow models, with temporal, physical, action, latency, memory, and closed-loop metrics required before treating a transfer as supported.
