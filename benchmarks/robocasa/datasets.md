---
id: world-model-kb.benchmarks.robocasa.datasets
title: Original RoboCasa Demonstration Data
kind: benchmark
status: maintained
last_updated: 2026-08-24
owners:
  - AIBuildAI world-model group
---

# Original RoboCasa Demonstration Data

## Retrieval metadata

**Relevant queries:** RoboCasa dataset, human demonstrations, MimicGen trajectories, 100K trajectories, task coverage, image rendering, texture randomization, dataset download, supervision, or data license.

**Knowledge provided:** dataset provenance, volumes, task coverage, released variants, training/evaluation appearance shift, and data-quality limitations relevant to model optimization.

**Related pages:** [MimicGen](../../papers/mimicgen/README.md) owns the general generation mechanism; [tasks and environments](tasks-and-environments.md) owns task semantics; [baselines and results](baselines-and-results.md) owns the paper's scaling evidence. Foundation data principles are in [datasets and supervision](../../foundations/data-and-evaluation/datasets-and-supervision.md) and [data curation](../../foundations/data-and-evaluation/data-curation-and-filtering.md).

## Human demonstration surface

Four operators collected 50 SpaceMouse demonstrations for each of the 25 atomic tasks, yielding 1,250 atomic human trajectories. Each episode sampled a kitchen floor plan, style, and AI-generated textures. The experimental composite-task subset uses 50 human demonstrations for each of five named tasks. The paper states that demonstrations accompany all 100 tasks, while the fixed `v0.2` download documentation promises human data for all atomic tasks and only a subset of composite tasks. A reproduction must use the released dataset registry rather than infer complete 100-task coverage from the paper's broad wording. [RC24-PAPER-V1, pp.2, 5-6, 8; RC24-CODE-V02, `docs/use_cases/downloading_datasets.md`]

Human collection supplies action and state trajectories under the simulator's robot and controller. It is not a language-only task dataset: episodes also depend on camera rendering, scene configuration, object instances, fixture states, and task metadata. Dataset conversion must preserve those semantics or document every change.

## MimicGen expansion

For 24 atomic manipulation tasks, the paper uses the 50 human demonstrations per task as seeds for 3,000 accepted MimicGen trajectories per task, producing 72,000 trajectories. Navigation is excluded because the generation method did not support the mobile base motion. The main experiment uses Objaverse objects; an additional 28,000 trajectories with AI-generated objects brings the publicized total to more than 100,000 trajectories. [RC24-PAPER-V1, pp.6-7, Figure 7]

MimicGen decomposes a demonstration into known object-centric subtask segments, transforms those segments to new object poses, stitches them, executes the trajectory, and retains only successful attempts. Success acceptance guarantees the terminal predicate, not smoothness or collision-free behavior. The RoboCasa paper explicitly reports jerky motions and collisions among technically successful generated trajectories. [RC24-PAPER-V1, pp.5-6, 9]

## Experimental dataset variants

| Variant | Tasks | Demonstrations per task | Total | Role |
|---|---:|---:|---:|---|
| `Human-50` | 25 atomic | 50 | 1,250 | Multi-task BC baseline |
| `Generated-100` | 24 manipulation | 100 | 2,400 | Scaling subset |
| `Generated-300` | 24 manipulation | 300 | 7,200 | Scaling subset |
| `Generated-3000` | 24 manipulation | 3,000 | 72,000 | Full Objaverse generated set used in the atomic experiment |
| Additional AI-object generation | subset described by release | not stated as one uniform per-task count | 28,000 | Extends the public total beyond 100K |

The `Generated-100` and `Generated-300` sets are random subsets of the 3,000-per-task generated data, not independently generated distributions. Scaling comparisons therefore change sample count while largely holding the parent generation pipeline fixed. [RC24-PAPER-V1, pp.6-7]

## Rendering and distribution shift

Atomic training images use randomly sampled AI-generated textures and the lightweight MuJoCo renderer. Evaluation uses human-curated textures; two of five fixed evaluation scenes use styles absent from training, and object instances are unseen. This design probes appearance and instance generalization but couples several changes unless results are sliced by scene, style, and object. [RC24-PAPER-V1, pp.6, 11]

The `v0.2` downloader exposes at least `human_raw`, `human_im`, and `mg_im` dataset types. Raw variants omit rendered images; image variants embed observations and are much larger. Default storage is `datasets/` under the repository and can be redirected through `DATASET_BASE_PATH` in the generated private macros. [RC24-EVAL-DOC-V02]

## Licensing and conversion constraints

Official code is MIT licensed; assets and datasets are CC BY 4.0. A derived dataset must retain attribution and should record the source code revision, original dataset identity, conversion script revision, camera keys, image/depth transforms, action coordinates, normalization statistics, episode count, task distribution, and output hashes. [RC24-CODE-V02, `README.md` and `LICENSE`]

The public X-WAM RoboCasa dataset is a separate converted and depth-augmented artifact. Its `raw_actions` field overrides reconstructed action fields, its RGB/depth streams are organized in a new episode JSON layout, and its HF revision must be treated as model-specific data rather than the canonical Original RoboCasa download. [XWAM-HF-ROBOCASA; XWAM-CODE-72CF, `data/robot_dataset.py`]

## Data diagnostics for optimization

Binary task success is an insufficient filter. Reusable data-quality axes include collision count, jerk and acceleration, controller saturation, grasp retry count, path length, stage transition delay, scene/style/object frequency, success-conditioned state coverage, and rare failure recovery. Improvement claims should hold task count and rollout protocol fixed while changing one data operator, and should report per-skill and per-object slices in addition to the overall average.

## Sources

Original data claims resolve through `RC24-PAPER-V1`, `RC24-CODE-V02`, and `RC24-EVAL-DOC-V02` in [`sources.yaml`](sources.yaml). X-WAM artifact identities resolve through the [X-WAM model source registry](../../models/x-wam/sources.yaml).
