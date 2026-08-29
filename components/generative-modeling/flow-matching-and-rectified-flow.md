---
id: world-model-kb.components.generative-modeling.flow-matching-and-rectified-flow
title: Flow Matching and Rectified Flow
kind: component
status: maintained
last_updated: 2026-08-19
owners:
  - AIBuildAI world-model group
---

# Flow Matching and Rectified Flow

## Retrieval metadata

**Relevant queries:** flow matching, conditional flow matching, rectified flow, optimal transport path, vector field regression, reflow, ODE solver, few-step generation, Cosmos rectified flow.

**Knowledge provided:** Continuous transport objectives, the distinction between flow matching and rectified flow, path and solver trade-offs, and their implementation in Cosmos-Predict2.5 and Cosmos 3.

**Related pages:** [Diffusion and flow matching](../../foundations/learning-objectives/diffusion-and-flow-matching.md) owns generic mathematics; [diffusion](diffusion.md) owns DDPM lineage; [Mean Flow and Pixel Mean Flow](mean-flow-and-pixel-mean-flow.md) owns average-velocity and latent-free one-step extensions; [Cosmos-Predict2.5](../../papers/cosmos-predict2-5/README.md) owns its exact implementation.

## Method definition

Flow matching learns a velocity field for a continuous normalizing flow:

\[
\frac{dx_t}{dt}=v_\theta(x_t,t,c).
\]

Given a conditional probability path with a tractable target velocity \(u_t\), training regresses:

\[
\mathcal{L}_{\mathrm{FM}}
=\mathbb{E}_{t,x_t,c}\left\|v_\theta(x_t,t,c)-u_t(x_t\mid c)\right\|_2^2.
\]

For a straight interpolation between data \(x_0\) and noise \(\epsilon\),

\[
x_\sigma=(1-\sigma)x_0+\sigma\epsilon,\qquad
u_\sigma=\epsilon-x_0.
\]

Training does not require integrating the learned ODE. Sampling does.

## Flow matching versus rectified flow

Flow matching is the broader framework: it can use diffusion-like paths, optimal-transport conditional paths, or other probability paths. Rectified flow emphasizes straight transport between endpoint pairs. Reflow uses samples from a learned flow to construct new pairs and train a straighter trajectory.

The terms should not be collapsed:

- a flow-matching objective is not necessarily rectified flow;
- rectified flow is not automatically one-step;
- an ODE flow is not the same claim as an invertible discrete normalizing-flow layer;
- few-step quality depends on path curvature, model error, and solver.

[OBJ-FLOW-MATCHING-2023, Secs. 2–4; OBJ-RECTIFIED-FLOW-2023, Secs. 2–3]

## Reported evidence

In matched CIFAR-10 and ImageNet experiments, the Flow Matching paper reports favorable FID, likelihood, and function-evaluation trade-offs for its optimal-transport path relative to the compared diffusion paths. It also reports lower numerical error at a given evaluation budget in selected settings. [OBJ-FLOW-MATCHING-2023, Tables 1–3 and Figs. 4–6]

The Rectified Flow paper reports that reflow straightens trajectories and improves few-step generation in its experiments. [OBJ-RECTIFIED-FLOW-2023, Secs. 4–5]

These results support path geometry as an optimization surface. They do not prove that every flow-matched video model is faster or better than every diffusion model. Architecture, data, codec, solver, guidance, and hardware remain material.

## Path, time, and solver surfaces

| Surface | Mechanism | Measurement | Failure risk |
|---|---|---|---|
| Endpoint coupling | changes transport geometry | curvature and integration error | semantically poor pairings |
| Time sampling | allocates regression updates | error by time region | neglected global or local structure |
| Loss weighting | changes gradient emphasis | target-region quality | instability or regression elsewhere |
| Velocity parameterization | changes target scale | convergence and solver behavior | train–inference mismatch |
| Solver family/order | approximates ODE trajectory | error versus function evaluations | unstable large steps |
| Step schedule | allocates evaluations along path | latency–quality frontier | rare-event loss |
| Guidance | modifies conditional vector field | adherence and diversity | curved or off-manifold path |
| Distillation/reflow | reduces required steps | few-step quality | teacher bias and lost modes |

Comparisons should report function evaluations and wall-clock latency. “Four steps” is not a compute-equivalent statement if solver order, network size, or resolution differs.

## Cosmos-Predict2.5

Cosmos-Predict2.5 uses a latent flow-matching DiT and a causal video autoencoder. Its clean-prefix formulation leaves conditioning-frame latents exact while applying noise to generated regions. Training progresses across tasks and resolution, then named variants use domain SFT, merging, reward post-training, or distillation. [P25-TR, pp. 6–14]

The report states that drawing 5% of samples from the highest 2% of noise levels reduced abrupt transitions at the conditioning boundary. This is a direct time-sampling intervention tied to an observed artifact. It is not evidence that the same 5%/2% ratio transfers to another dataset or objective. [P25-TR, pp. 8–10]

## Cosmos 3

Cosmos 3 Generator uses straight interpolation and a velocity target for continuous video, audio, and action latents, with modality masks and per-modality time sampling. Diffusion queries may attend to autoregressive semantic context and other diffusion tokens. [C3-TR, pp. 8–13, 27–30]

The objective family is shared with rectified-flow lineage, but exact training distribution, masks, conditioning, solver, and post-training checkpoint determine behavior. The Model [Generator page](../../models/cosmos3-nano/generator.md) owns these concrete facts.

## Optimization and falsification

### Error-stratified time sampling

Measure loss, boundary artifacts, state error, and action sensitivity by time/noise bucket. Reweight only the identified region and control total updates. A global improvement with no change in the targeted bucket contradicts the proposed mechanism.

### Solver Pareto analysis

Compare steps and solvers at fixed checkpoint, condition, seed set, resolution, and duration. Report media, physical-event, diversity, action, latency, and memory metrics.

### Path straightness

Measure curvature or local truncation error and test whether reduced curvature predicts fewer evaluations at constant quality. Straightness without sample or decision improvement is insufficient.

### Distillation

Compare teacher and student on rare transitions and failure slices, not only average perceptual score. A distilled sampler fails the world-model objective if it loses action response or candidate ranking.

## Sources

- [OBJ-FLOW-MATCHING-2023] identifies the general flow-matching framework.
- [OBJ-RECTIFIED-FLOW-2023] identifies rectified flow and reflow.
- [P25-TR] and [C3-TR] identify the Cosmos implementations.
