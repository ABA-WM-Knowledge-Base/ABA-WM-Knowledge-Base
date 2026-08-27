---
id: world-model-kb.components.dynamics-modeling.comparison-and-optimization
title: Dynamics Method Comparison and Optimization
kind: component
status: maintained
last_updated: 2026-08-27
owners:
  - AIBuildAI world-model group
---

# Dynamics Method Comparison and Optimization

## Retrieval metadata

**Relevant queries:** choose world-model dynamics, latent versus observation transitions, occupancy versus video FD, joint WAM dynamics, action-invariant continuation, Cosmos3-Nano FD optimization.

**Knowledge provided:** Stable comparison axes across dynamics methods, tests that falsify continuation-as-dynamics, Cosmos3-Nano FD/WAM attachment hypotheses, and unresolved questions.

**Related pages:** [Recurrent latent dynamics](recurrent-latent-dynamics.md), [decoder-free latent dynamics](decoder-free-latent-dynamics.md), [observation-space dynamics](observation-space-dynamics.md), [structured occupancy dynamics](structured-occupancy-dynamics.md), and [joint multimodal dynamics](joint-multimodal-dynamics.md) own method details.

## Comparison by method, not chronology

| Method | Transition variable | Action role | Main drift mode | Strongest current evidence |
|---|---|---|---|---|
| Recurrent latent | \(z',h\) | input to RSSM/MDN | prior–posterior gap | World Models temperature; DreamerV3 KL |
| Decoder-free latent | \(z'=d(z,a)\) | input to MLP | unconstrained \(z\), critic-dominated capacity | TD-MPC2 SimNorm, 104-task recipe |
| Observation-space | future \(o\) | condition (sometimes weak) | generated-context chaining | IRASim; DIAMOND steps; Vista IDM |
| Occupancy / ego | future occ, \(\tau\) | mostly implicit in driving | 1 s to 3 s mIoU drop | OccWorld Tables 1 and 4 |
| Joint multimodal | \((o,x,a)\) | input and/or output | video residual dominates action | X-WAM ANS; Nano FD vs WAM |

Inverse dynamics, latent-action codes, and Policy-DROID closed-loop scores are not rows on this table.

## Recurring supported patterns

### Test action counterfactuals, not only reconstruction

IRASim logged-action clips, iVideoGPT action-free OXE pretrain, and Vista Table 2 FID can look like dynamics while remaining continuation. Hold observation, prompt, and seed; swap actions; require a change aligned with the process. [IRASRC-PAPER-V2; IVG-PAPER; VISTA-PAPER; C3-TR]

### Separate teacher-forced one-step from generated-context rollout

RSSM posterior versus prior, IRASim chained clips, DreamZero real-frame cache refresh, and OccWorld 1 s versus 3 s mIoU all show that the open-loop transition is a different object. [FND-WORLD-MODELS-2018; IRASRC-PAPER-V2; DZ-PAPER; OCCSRC-PAPER, Table 1]

### Search and imagination amplify transition error

World Models’ virtual–real temperature gap, IRASim \(P=0\) planning, and DIAMOND’s denoising-step ablation show that a planner or actor can exploit a biased \(p(s'\mid s,a)\). Dynamics evaluation should include identical-action replay in model and environment, not only imagined return. [FND-WORLD-MODELS-2018, Table 2; IRASRC-PAPER-V2, Table 5; DIASRC-PAPER, Table 7]

### Do not mix prediction directions or checkpoints

FD, ID, and WAM are different maps. Base Nano, Policy-DROID, DreamZero-DROID, and DreamZero-AgiBot are different transitions. OccWorld-O is not OccWorld-S. [C3-TR; DZ-HF-DROID; DZ-HF-AGIBOT; OCCSRC-PAPER]

### Backbone family is not the transition

Diffusion, flow, and AR can all implement observation-space dynamics. Choosing flow matching does not decide whether the model is FD, WAM, or a policy. Point to [generative modeling](../generative-modeling/README.md) for sampler families.

## Failure-to-measurement map

| Observable failure | Competing causes | Discriminating measurement |
|---|---|---|
| Action-invariant video | condition bypass or passive prior | swapped-action pairs, fixed noise |
| One-step good, long fail | exposure / chaining | prefix versus generated context |
| High imagined return | biased \(d\) or reward | replay in real env |
| Occupancy 3 s collapse | temporal dynamics | per-horizon mIoU, Table 4 |
| Joint model, dead actions | visual loss scale | per-modality action error |
| ID or policy numbers here | ownership leak | move to Components 3 or 6 |

## Cosmos3-Nano attachment map

| Target surface | Method knowledge | Testable hypothesis | Evidence required |
|---|---|---|---|
| Generator FD | observation-space / joint | action counterfactuals change futures | swapped actions, horizon curves |
| Generator WAM | joint multimodal | action/video consistency under replay | feasibility plus replay, not DROID scores |
| Latent consistency | decoder-free / RSSM | multi-step latent loss reduces prior drift | prior-versus-posterior on action latents |
| Occupancy-like head | structured dynamics | parallel geometric forecast | licensed occupancy metrics |
| Policy-DROID | out of scope for this Component | do not attach FD tables | bind the policy checkpoint elsewhere |

Exact experiment definitions remain in the [optimization playbook](../../models/cosmos3-nano/optimization-playbook.md).

## Open questions

1. When does a compact latent \(d(z,a)\) beat chained visual FD at matched action sensitivity and latency?
2. How should multimodal valid futures be represented so that dynamics calibration is not collapsed to one sample?
3. Which occupancy or depth transitions transfer without GT occupancy at deployment?
4. When does asynchronous joint denoising improve continuation-after-action versus ordinary FD conditioning?
5. Which virtual–real gaps are temperature or sampler artifacts rather than missing state?

These questions define missing evidence, not work priority or workflow.

## Sources

Method-specific identities are listed on the owning method pages. [C3-TR] anchors Nano FD/WAM attachment hypotheses; none is a reproduced optimization result.
