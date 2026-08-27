---
id: world-model-kb.components.dynamics-modeling.joint-multimodal-dynamics
title: Joint Multimodal Dynamics
kind: component
status: maintained
last_updated: 2026-08-27
owners:
  - AIBuildAI world-model group
---

# Joint Multimodal Dynamics

## Retrieval metadata

**Relevant queries:** joint video-action dynamics, WAM transition, X-WAM asynchronous noise, Cosmos forward dynamics, coupled denoising, not Policy-DROID.

**Knowledge provided:** How models jointly evolve video, state, and action variables, which training-time coupling is a dynamics mechanism, and which policy-success tables are not dynamics evidence.

**Related pages:** [Multimodal state](../world-representation/multimodal-state.md) owns the streams; [world action models](../../foundations/definitions-and-taxonomy/world-action-model.md) owns WAM definitions; [action-conditioned video](../generative-modeling/action-conditioned-video.md) owns video-only action interfaces; [Cosmos3-Nano action modeling](../../models/cosmos3-nano/action-modeling.md) owns FD/ID/WAM contracts; [X-WAM Paper](../../papers/x-wam/README.md) owns ANS evidence.

## Method definition

Joint multimodal dynamics predict several future modalities together:

\[
p_\theta(o_{t+1:t+H}, x_{t+1:t+H}, a_{t:t+H-1}\mid h_t, c),
\]

where \(x\) may be proprioception or depth and \(a\) may be generated rather than only conditioned. The dynamics claim is that the coupled process is consistent: actions that are executed should match the visual/state future the model associates with them. Generating an action chunk is not, by itself, a World Model–Policy Interface evaluation; closed-loop success belongs to that future Component.

Inverse dynamics (infer \(a\) from an observed \(o\to o'\)) is a different prediction direction and is out of scope here even when the same backbone can run an ID mode.

## Cosmos3-Nano: FD versus WAM as dynamics modes

Base Nano documents three action-related Generator objectives. **Forward dynamics** predicts future observations from observation and action. **WAM** jointly generates action and a corresponding visual future. **Inverse dynamics** is excluded from this Component. Policy-DROID is a separately post-trained executable checkpoint and must not inherit base FD/WAM measurements. [C3-TR, pp. 7–10 and pp. 31–32]

FD is observation-space (or latent-observation) dynamics with an external action path. WAM is joint dynamics. Both remain Generator surfaces, not Reasoner text. Domain adapters, padding, and H-actions versus H+1 observations are implementation contracts on the model page, not generic WAM theorems.

## X-WAM: asynchronous coupling of video and action time

X-WAM jointly denoises multi-view RGB, depth-like latents, proprioceptive state, and actions. Asynchronous Noise Scheduling constrains the video timestep to be no earlier than the action timestep and samples a clean-action component with probability 0.5, training both joint denoising and visual continuation after actions are clean. Independent or synchronous timestep sampling are separate ablations. [XWAM-PAPER-V2, pp. 5–6 and 11]

This is a dynamics-training mechanism: it changes the joint process \(p(o,a)\) over noise time. Paper RoboCasa 79.2% mean success and RoboTwin 89.8%/90.7% are **policy-mode / SFT** outcomes. Depth/ANS ablations fine-tuned from Wan2.2 without the 5,873.9-hour pretraining stage reach 67.8% and support mechanism direction under that regime; they do not decompose the 79.2% checkpoint into a pure dynamics score. [XWAM-PAPER-V2, pp. 7–9, Tables 1–4]

## DreamZero: joint video–action denoising with real-frame refresh

DreamZero jointly denoises future video and motor actions on Wan2.1. Closed loop writes **real** observations into the AR KV cache after each executed chunk, which is a context-refresh dynamics choice (generated video is not the next world state). Flash samples video times from \(\mathrm{Beta}(7,1)\) while action times stay uniform. DROID and AgiBot checkpoints are embodiment-specific; they are not a universal transition. [DZ-PAPER; DZ-CODE]

Task-progress numbers (DROID 22.5, AgiBot 62.2 in the Paper retrieval field) are policy/eval surfaces. Do not cite them as proof that joint denoising is calibrated FD.

## Controllable surfaces

| Surface | Mechanism | Expected observable | Main confounder |
|---|---|---|---|
| Conditioned FD vs joint WAM | whether \(a\) is input or output | action sensitivity vs joint consistency | Policy-DROID leakage |
| Relative noise times | which modality is cleaner | continuation after clean action | independent-timestep ablation mix |
| Real versus generated visual refresh | what re-enters the transition | closed-loop drift | KV-cache implementation |
| Loss weights video/action/state | which residual dominates | per-modality errors | global success only |
| Embodiment adapter | action/state kinematics in \(d\) | cross-robot transfer failure | language-only prompts |

## Evaluation and failure diagnosis

| Symptom | Plausible cause | Discriminating evidence |
|---|---|---|
| Good video, inconsistent actions | visual loss dominates | component-wise action error |
| Success cited as FD | policy interface mixed in | bind FD, WAM, or SFT policy |
| ANS ablation over-claimed | missing pretraining stage | 67.8% regime versus 79.2% |
| ID numbers in this page | wrong prediction direction | move to Action Representation |
| Base Nano given DROID scores | checkpoint leakage | Policy-DROID identity |

## Cosmos3-Nano connection

This method is the native FD/WAM split. Optimization hypotheses should freeze one of FD, WAM, or Policy-DROID, hold the action adapter fixed, and report action counterfactuals plus per-modality errors. Inverse-dynamics experiments are out of scope. Playbook details remain in [optimization-playbook.md](../../models/cosmos3-nano/optimization-playbook.md).

## Sources

- [C3-TR] identifies Nano FD/WAM (not ID, not Policy-DROID) as dynamics modes.
- [XWAM-PAPER-V2] identifies asynchronous joint denoising and the ablation-regime limit.
- [DZ-PAPER] and [DZ-CODE] identify joint video–action denoising and real-frame cache refresh.
