---
id: world-model-kb.foundations.representations.3d-and-4d-world-model
title: 3D and 4D World Models
kind: concept
status: maintained
last_updated: 2026-08-27
owners:
  - AIBuildAI world-model group
---

# 3D and 4D World Models

## Retrieval metadata

**Relevant queries:** 3D world model, 4D world model, neural radiance field, dynamic NeRF, Gaussian splatting, occupancy prediction, scene flow, persistent geometry, or world-coordinate dynamics.

**Knowledge provided:** distinctions among spatial reconstruction and spatiotemporal dynamics, core field and occupancy formulations, representation trade-offs, and tests for geometric, temporal, and action-conditioned validity.

**Related pages:** [Video world models](video-world-model.md) covers observation-space sequences; [object-centric world models](object-centric-world-model.md) covers entity structure; [actions and interventions](../problem-formulation/actions-and-interventions.md) covers control-conditioned dynamics; [X-WAM architecture](../../models/x-wam/architecture.md) owns one RGB-D-to-point-cloud instantiation and its limits.

## Definition and formalism

A 3D representation organizes scene information in a spatial coordinate system rather than only in image coordinates. Common forms include occupancy grids, point clouds, meshes, signed-distance or radiance fields, and anisotropic Gaussians. A 4D representation usually means 3D structure evolving over time, not four spatial dimensions. The term remains broad: some systems reconstruct independent time slices, while others maintain persistent state and a transition model.

A neural radiance field maps position and viewing direction to density and color,

```text
F_theta(x, d) -> (sigma, c),
C(r) = integral T(t) sigma(r(t)) c(r(t), d) dt,
T(t) = exp(-integral_[near]^t sigma(r(u)) du).
```

Dynamic fields add time or a deformation from observation time to a canonical space. An occupancy world model instead predicts a spatial tensor such as

```text
y_t in {free, occupied-class-1, ..., unknown}^{H x W x D},
p(y_{t+1:t+H} | history, ego-motion, actions).
```

Static view synthesis becomes a world model only when the claimed interface includes change, uncertainty, or controllable transitions. [REP-NERF-2020; REP-DNERF-2021]

## Assumptions and scope

Multi-view reconstruction often assumes known or estimable camera intrinsics and poses, a sufficiently observed scene, and appearance consistency. Dynamic reconstruction adds correspondence, deformation, or scene-flow assumptions. Monocular input leaves scale, depth, occlusion, and motion ambiguities unless priors or other sensors resolve them.

Geometry can improve view consistency and collision reasoning, but reconstruction accuracy does not guarantee mass, contact, articulation, affordance, or action-response accuracy. Conversely, a compact task model may control successfully without reconstructing a metrically complete scene.

## Representation families

| Family | Parameterization | Strength | Main cost or ambiguity |
|---|---|---|---|
| Dense occupancy/voxel grid | regular 3D cells | explicit free space and semantics | cubic memory and resolution limits |
| Point cloud or sparse voxel | observed/sparse locations | sensor-aligned efficiency | holes and neighborhood definition |
| Mesh or surface | vertices and faces | compact explicit geometry | topology changes and extraction |
| Implicit neural field | coordinate network for density/SDF/radiance | continuous resolution and view synthesis | rendering cost and weak explicit dynamics |
| 3D Gaussian splats | explicit anisotropic primitives | fast differentiable rendering | editing, topology, and physical meaning remain indirect |
| Dynamic/canonical field | time-conditioned field or deformation | temporal view synthesis | canonical correspondence can fail |
| 4D occupancy/dynamics | spatial state plus temporal transition | planning-oriented scene evolution | uncertainty and long-horizon memory |

NeRF established differentiable implicit view synthesis; D-NeRF added time-varying deformation; 3D Gaussian Splatting provided a fast explicit radiance representation; OccWorld predicted future 3D occupancy as a world-model surface for driving. [REP-NERF-2020; REP-DNERF-2021; REP-3DGS-2023; REP-OCCWORLD-2024]

## Design implications and trade-offs

Camera calibration, pose estimation, coordinate frame, spatial resolution, temporal stride, depth/flow/occupancy supervision, and ego-motion compensation are first-order levers. Separating geometry from appearance can improve view transfer, while shared features can reduce compute. Canonical deformation encourages temporal correspondences but can be brittle for topology change, birth/death, or large non-rigid motion.

Action-conditioned 4D modeling requires more than appending action tokens: action frames and spatial frames must align, and the dataset must cover distinct consequences. Explicit occupancy helps collision and free-space queries but may omit texture and fine manipulation state. Radiance representations preserve appearance while leaving contact and occupancy implicit.

## Evaluation and falsification

- Measure novel-view rendering, depth, pose, occupancy, scene flow, and temporal persistence separately.
- Test unobserved regions and re-observation after occlusion rather than only interpolated views.
- Evaluate geometry under camera trajectories and scene motions outside training coverage.
- Perturb feasible actions and compare predicted 3D changes with independent rollout.
- Measure downstream collision, planning, or manipulation performance when those capabilities are claimed.
- Report spatial and temporal resolution, coordinate frames, sensor inputs, and inference cost.

A 4D dynamics claim is weakened when time-conditioned frames lack persistent identity or transition consistency. A physical-world claim is falsified by correct rendering paired with incorrect occupancy, contacts, or action consequences. A general 3D claim should be narrowed when scale or geometry depends on privileged poses unavailable at deployment.

## Failure modes

- **View-synthesis substitution:** rendering metrics are treated as evidence of dynamics or physics.
- **Pose leakage:** privileged camera trajectories solve alignment unavailable at deployment.
- **Monocular ambiguity:** scale, depth, and motion decompositions are underdetermined.
- **Occlusion hallucination:** unobserved geometry is plausible but wrong and overconfident.
- **Canonical-space failure:** topology change or non-rigid motion breaks deformation correspondences.
- **Ego/world confusion:** camera motion appears as scene dynamics.
- **Resolution bottleneck:** thin structures, contact gaps, or small objects disappear.
- **Static-model overclaim:** a NeRF or 3DGS scene is called a world model without temporal or intervention structure.

## Cross-part instantiations

- [Cosmos3-Nano Generator](../../models/cosmos3-nano/generator.md) should not be assumed to contain an explicit persistent 3D state unless the model documentation establishes it.
- [Modalities and I/O](../../models/cosmos3-nano/modalities-and-io.md) records camera, image, video, pose, or spatial conditioning that constrains geometric claims.
- [Evaluation](../../models/cosmos3-nano/evaluation.md) can separate perceptual video quality from 3D consistency; [limitations](../../models/cosmos3-nano/limitations.md) owns missing spatial evidence.
- [Discrete and structured state](../../components/world-representation/discrete-and-structured-state.md) and [structured occupancy dynamics](../../components/dynamics-modeling/structured-occupancy-dynamics.md) own occupancy-token state and occupancy/ego transitions.
- [OccWorld](../../papers/occworld/paper.md) instantiates 3D occupancy-token forecasting plus ego-trajectory prediction on nuScenes; license constraints and OccWorld-O versus supervised extensions remain entry-owned.
- [Action modeling](../../models/cosmos3-nano/action-modeling.md) provides the model-specific surface for intervention-conditioned scene change.
- [X-WAM](../../models/x-wam/README.md) predicts future multi-view RGB and inverse-depth-like latents, then lifts decoded depth with camera poses; it does not maintain a native persistent 3D scene state.
- [X-WAM evaluation](../../models/x-wam/evaluation.md) binds its AbsRel, delta1, and Chamfer Distance results to the paper protocol and separates them from policy success.

## Sources

- [REP-NERF-2020] Mildenhall et al., *NeRF: Representing Scenes as Neural Radiance Fields for View Synthesis*, ECCV 2020, DOI:10.1007/978-3-030-58452-8_24.
- [REP-DNERF-2021] Pumarola et al., *D-NeRF: Neural Radiance Fields for Dynamic Scenes*, CVPR 2021, DOI:10.1109/CVPR46437.2021.01018.
- [REP-3DGS-2023] Kerbl et al., *3D Gaussian Splatting for Real-Time Radiance Field Rendering*, ACM Transactions on Graphics, 2023, DOI:10.1145/3592433.
- [REP-OCCWORLD-2024] Zheng et al., *OccWorld: Learning a 3D Occupancy World Model for Autonomous Driving*, ECCV 2024, arXiv:2311.16038.
