---
id: world-model-kb.components.generative-modeling.action-conditioned-video
title: Action-Conditioned Video Modeling
kind: component
status: maintained
last_updated: 2026-08-19
owners:
  - AIBuildAI world-model group
---

# Action-Conditioned Video Modeling

## Retrieval metadata

**Relevant queries:** action-conditioned video world model, interactive simulator, action timing, control conditioning, UniSim, iVideoGPT action model, IRASim, DIAMOND planning, counterfactual actions.

**Knowledge provided:** The interface that turns generic video generation into an intervention-conditioned transition model, cross-architecture evidence, alignment and planning mechanisms, and failure diagnostics.

**Related pages:** [Actions and interventions](../../foundations/problem-formulation/actions-and-interventions.md) owns causal action semantics; [forward dynamics](../../foundations/problem-formulation/forward-dynamics.md) owns prediction direction; [planning and control](../../foundations/decision-making/planning-and-control.md) owns candidate selection.

## Method definition

An action-conditioned video model predicts:

\[
p_\theta(o_{t+1:t+H}\mid o_{\leq t},a_{t:t+H-1},c).
\]

The action sequence must define units, coordinate frame, temporal support, control frequency, embodiment, normalization, and missing-value behavior. A numeric tensor without that contract is not a transferable intervention.

Action conditioning differs from a text prompt. A prompt may correlate with likely outcomes; a physical action must change the predicted transition in a direction consistent with the process.

## Cross-architecture implementations

### UniSim

UniSim trains conditional real-world simulation across heterogeneous data and control types, including robot actions, camera motion, and text-like controls. The work reports interactive simulation and selected policy/planning transfer. Its main contribution to this method is interface breadth, not a single universal action ontology. [WFM-UNISIM-2024]

### iVideoGPT

iVideoGPT first learns action-free video tokens, then adapts task-specific action-conditioned checkpoints. The BAIR FVD change from 75.0 to 60.8 under the paper's named variants supports action information in that setting. Heterogeneous Open-X actions prevent treating its broad action-free pretraining as one universal action-conditioned model. [IVG-PAPER, Tables 1–2]

### IRASim

IRASim uses a latent diffusion Transformer with frame-level action modulation inside its blocks. Aligning each action segment with the corresponding future-frame latent directly addresses temporal conditioning. The paper reports robot-rollout results and a Push-T planning improvement from IoU 0.637 to 0.961 under its specified candidate and value-model protocol. [IRASRC-PAPER-V2, Secs. 3–4 and Table 5]

The released implementation, paper training steps, final-layer conditioning, and planning code have documented gaps in the [IRASim Paper entry](../../papers/irasim/README.md). The result therefore supports the paper mechanism, not complete public reproducibility.

### DIAMOND

DIAMOND conditions pixel-space diffusion on actions and trains an RL agent in the model. It demonstrates that detailed generated observations can support decision learning in Atari and exposes denoising-step sensitivity. [DIASRC-PAPER, Secs. 3–4]

Its action space, resolution, dynamics, and interaction budget differ materially from robot video. The transferable insight is to measure decision utility and sampler effects, not to copy its pixel representation.

## Temporal and semantic alignment

For action \(a_t\), define whether it affects:

- transition \(o_t\rightarrow o_{t+1}\);
- a fixed frame block;
- a continuous time interval;
- a delayed actuation interval;
- an action chunk with open-loop execution.

Camera exposure, sensor latency, interpolation, and action logging can shift this alignment. A one-frame offset may dominate model error while leaving generated video visually smooth.

Coordinate frame and normalization errors create similar symptoms. A model may appear action-insensitive because actions were rotated, scaled, clipped, or associated with the wrong embodiment.

## Data requirements

Action-conditioned learning benefits from:

- paired transitions with synchronized actions;
- coverage of contact, release, failure, recovery, and idle states;
- matched contexts with different actions;
- same endpoint reached by different trajectories;
- embodiment and controller metadata;
- calibration and camera information;
- action units and normalization transforms that are invertible.

Passive video can broaden perception and event coverage, but it cannot identify physical action effects without labels, latent-action assumptions, or controlled interventions.

## Planning use

Model-predictive planning samples candidate actions, generates futures, scores them, executes the first action or short prefix, and replans. The generator and evaluator are separate error sources. More candidates can increase success or increase exploitation of a biased model.

Report:

- candidate count, horizon, optimizer iterations, and sampling temperature;
- independent value or goal evaluator;
- predicted versus realized candidate ranking;
- generation latency and control frequency;
- stage and task success;
- constraint and safety violations.

Video realism is not a planning metric.

## Failure diagnosis

| Symptom | Plausible cause | Test |
|---|---|---|
| Action swap changes nothing | conditioning bypass or weak counterfactual data | paired-action intervention score |
| Motion direction is inverted | frame or coordinate transform error | unit-tested synthetic transition |
| Short rollout correct, long rollout drifts | exposure and model error | horizon-conditioned replay |
| Planner score high, outcome poor | model or evaluator exploitation | predicted-versus-realized ranking regret |
| Joint action/video looks coherent but fails | shared hallucination | ground-truth transition replay |
| Cross-robot transfer collapses | embodiment/action-schema mismatch | held-out embodiment with explicit adapter |

## Cosmos3-Nano connection

Cosmos3-Nano exposes forward-dynamics and joint world-action modes in its Generator family. The relevant method knowledge is temporal action alignment, typed adapters, counterfactual data, independent evaluation, and planning-budget reporting. [C3-TR, pp. 55–69]

Exact input/output modes belong to [action modeling](../../models/cosmos3-nano/action-modeling.md). Policy-DROID is a separately post-trained policy and cannot inherit base WAM evidence.

## Sources

- [WFM-UNISIM-2024] identifies UniSim.
- [IVG-PAPER] identifies iVideoGPT.
- [IRASRC-PAPER-V2] identifies IRASim v2.
- [DIASRC-PAPER] identifies DIAMOND.
- [C3-TR] identifies Cosmos 3 action surfaces.
