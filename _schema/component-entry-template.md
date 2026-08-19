---
id: world-model-kb.component-entry-template
title: World Model Component Entry Template
kind: guide
status: maintained
last_updated: 2026-08-19
owners:
  - AIBuildAI world-model group
---

# World Model Component Entry Template

A Component entry is a cross-paper account of how one reusable world-model capability evolved. It is not a taxonomy page, a bibliography, a compressed set of paper summaries, or a model-specific optimization queue.

## Required directory

```text
components/<component-id>/
|-- README.md
`-- sources.yaml
```

## Canonical page contract

The entry `README.md` uses ID `world-model-kb.components.<component-id>`, kind `component`, and the standard `Retrieval metadata` fields. Organize the body around the following information flow:

1. **Capability boundary:** define the modeled input, output, uncertainty, decision use, and neighboring capabilities that are not equivalent.
2. **Historical evolution:** follow the field's causal sequence. For every milestone, state the inherited bottleneck, exact intervention, mechanism, scoped evidence, and remaining limitation.
3. **Evolution summary:** compare stages on stable axes instead of ranking papers by recency.
4. **Supported patterns:** extract recurring design patterns only when more than one source or a controlled ablation supports them.
5. **Failure boundaries:** connect observable failures to competing explanations and discriminating measurements.
6. **Current directions and open questions:** express scientific uncertainties, not priorities or work assignments.
7. **Model attachment map:** connect the synthesis to concrete model surfaces without copying model facts or claiming transfer before measurement.

The historical section should remain the main body. Preserve the source paper's model variant, data, metric, protocol, seed or rollout count, and compute condition whenever a result supports an evolutionary claim.

## Evidence grammar

- **Source-reported:** a named source reports the mechanism or result under a specified protocol.
- **Cross-source synthesis:** several results support a shared pattern, but not a universal law.
- **Hypothesis:** a proposed mechanism-to-outcome relation that still requires a controlled test.

Do not treat chronological succession as proof of superiority. Do not transfer an image-generation result to video dynamics, a text-reasoning result to action control, a simulator score to real-environment return, or an offline metric to closed-loop success without the missing evidence.

## Provenance

The local `sources.yaml` contains only source identities whose canonical owner is this Component. Reuse globally unique IDs from Foundation, Paper, or Model registries for already registered works, and link to their canonical pages for detailed interpretation. Every local source must be cited by the entry.

## Authority boundary

Component knowledge may influence Agent understanding, diagnosis, strategy choice, and experiment design. It must not encode Agent selection, repository selection, task sequencing, permissions, execution scheduling, retries, stopping, or other AIBuildAI workflow orchestration.
