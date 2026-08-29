---
id: world-model-kb.components.wm-policy-interface.deployment-boundaries
title: Deployment Boundaries
kind: component
status: draft
last_updated: 2026-08-20
owners:
  - AIBuildAI world-model group
---

# Deployment Boundaries

## Retrieval metadata

**Relevant queries:** WAM as policy, zero-shot world model policy, world model latency, WAM versus VLA robustness, control frequency, pixel generation cost.

**Knowledge provided:** The measured limits of using a world/action model directly as the policy: the latency evidence across systems, and the robustness boundary against VLA baselines.

**Related pages:** [Joint denoising and schedules](../action-conditioning/joint-denoising-and-schedules.md) owns schedule-level latency mitigation; [predictive representation and planning](../reasoning/predictive-representation-and-planning.md) owns the latent-planning alternative; the [DreamZero Paper entry](../../papers/dreamzero/README.md) owns full zero-shot claims.

## The latency boundary

The pixel-generative interface pays a measured tax at every consumption point:

- Same lab, same task, opposite interfaces: V-JEPA 2-AC plans with 800 samples in 16 seconds per action and reaches 80% cup pick-and-place; the pixel-generative Cosmos baseline uses 80 samples, takes 4 minutes per action, and scores 0% [VJ2-PAPER, Secs. 4-5].
- Cosmos Policy planning costs about five seconds per action chunk with a one-layer search tree [P25-COSMOS-POLICY, p. 11].
- DreamZero needs two GB200 GPUs to reach 7 Hz control, versus VLAs above 20 Hz on consumer GPUs [DZ-PAPER, p. 18].
- In the controlled robustness study, evaluated WAMs ran at least 4.8 times slower than pi0.5, with Fast-WAM at 3.0 times [COMP-WPI-WAMROBUST-2026, pp. 11-12].
- The counterexample defines the escape route: LaWAM's latent-subgoal interface reaches 98.6% LIBERO at 187 ms per action chunk, providing dynamics foresight without iterative pixel synthesis [COMP-WPI-LAWAM-2026, pp. 2, 6].

Across systems the recurring price of pixel-space consumption is latency and decode noise, and the recurring escape is staying latent.

## The robustness boundary

DreamZero's zero-shot claim is real but scoped: 62.2% average task progress on unseen environments versus 27.4% for the best pretrained VLA, while its authors call it a short-horizon System 1 and propose a separate System 2 planner for long horizons [DZ-PAPER, pp. 13, 18-19].

The controlled comparison answers the general question negatively: WAMs do not universally beat VLAs. WAMs lead under noise, lighting, and layout perturbations; VLAs lead under geometric ones (camera viewpoint, robot state). pi0.5 wins LIBERO-Plus overall at 85.7%, and Fast-WAM falls from 97.6% clean to 51.5% perturbed. The study itself notes results confound architecture with training-data diversity [COMP-WPI-WAMROBUST-2026, pp. 8-12].

Interface consequence: "the world model is the policy" removes the interface boundary entirely, which means there is no seam at which to substitute a faster planner, a robustness wrapper, or an independent evaluator. The direct-policy position should be adopted for its measured benefits under the perturbations that matter for the deployment, not as a default.

## Sources

- [VJ2-PAPER] identifies V-JEPA 2; it resolves through the V-JEPA 2 entry's registry.
- [P25-COSMOS-POLICY] identifies Cosmos Policy; it resolves through the Cosmos Policy entry's registry.
- [DZ-PAPER] identifies DreamZero; it resolves through the DreamZero entry's registry.
- [COMP-WPI-WAMROBUST-2026] identifies the WAM-versus-VLA robustness study; it resolves through the local [source registry](sources.yaml).
- [COMP-WPI-LAWAM-2026] identifies LaWAM; it resolves through the local [source registry](sources.yaml).
