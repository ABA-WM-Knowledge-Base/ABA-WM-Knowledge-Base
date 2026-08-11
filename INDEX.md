---
id: world-model-kb.index
title: Knowledge Base Topic Index
kind: index
status: maintained
last_updated: 2026-08-11
owners:
  - AIBuildAI world-model group
---

# Knowledge Base Topic Index

This index is a topic map. It helps readers and retrieval systems discover relevant knowledge without prescribing task order, context size, tool choice, or execution behavior.

## Content areas

| Knowledge area | Entry point | Current scope |
|---|---|---|
| Model-independent concepts | [Foundations](foundations/README.md) | Reserved; no concept pages yet |
| Representative methods and papers | [Papers](papers/README.md) | Reserved; no paper entries yet |
| Cosmos3-Nano model knowledge | [Cosmos3-Nano](models/cosmos3-nano/README.md) | Active model entry |
| KB representation and provenance | [Schema reference](_schema/README.md) | Metadata, naming, sources, and authoring conventions |
| Structural history | [Changelog](CHANGELOG.md) | Schema, path, and ownership changes |

## Cosmos3-Nano retrieval metadata

[`models/cosmos3-nano/agent-index.yaml`](models/cosmos3-nano/agent-index.yaml) associates query themes with knowledge that can ground design and implementation decisions. It supports AIBuildAI's dynamic loading, but is not a task router or orchestration control plane. AIBuildAI and its Agent architecture remain authoritative over Agent selection, repository selection, task sequencing, execution scheduling, and external actions.

## Metadata and maintenance references

| Knowledge change | Reference |
|---|---|
| Add or revise a canonical page | [Page template](_schema/page-template.md) and [style guide](_schema/style-guide.md) |
| Add a representative paper entry | [Paper entry template](_schema/paper-entry-template.md) |
| Add or rename a page ID or path | [Naming conventions](_schema/naming-conventions.md) |
| Change model identity, revisions, interfaces, or the execution-state pointer | [Manifest schema](_schema/manifest.schema.yaml); mutable states remain in [Reproduction](models/cosmos3-nano/reproduction.md) |
| Add or update a source | [Source schema](_schema/sources.schema.yaml) |
| Change required files or page metadata | [Metadata schema](_schema/metadata.schema.yaml) |
