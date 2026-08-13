---
id: world-model-kb.papers.irasim
title: IRASim Paper Knowledge Entry
kind: paper
status: maintained
last_updated: 2026-08-13
owners:
  - AIBuildAI world-model group
---

# IRASim Paper Knowledge Entry

## Retrieval metadata

**Relevant queries:** IRASim, trajectory-to-video, robot world model, action-conditioned video prediction, frame-level action conditioning, robot policy evaluation, model-based planning, Push-T, LIBERO, real-robot rollout simulation, test-time scaling, or failure-rollout data.

**Knowledge provided:** the paper's predictive and decision interfaces, action-frame conditioning mechanism, training and evaluation evidence, released implementation boundary, reproduction state, and falsifiable optimization transfers.

**Related pages:** [Forward dynamics](../../foundations/problem-formulation/forward-dynamics.md) owns the generic action-conditioned prediction problem; [video world models](../../foundations/representations/video-world-model.md) owns observation-space rollout modeling; [diffusion and flow matching](../../foundations/learning-objectives/diffusion-and-flow-matching.md) owns the objective family; [planning and control](../../foundations/decision-making/planning-and-control.md) owns candidate selection and model exploitation; [Cosmos3-Nano action modeling](../../models/cosmos3-nano/action-modeling.md) owns the target model's FD/WAM interfaces.

The official [project page](https://gen-irasim.github.io/) provides the current video presentation surface; numerical and protocol claims remain bound to the pinned paper revision. [IRASRC-PROJECT; IRASRC-PAPER-V2]

## Identity and revision boundary

| Field | Canonical value | Consequence |
|---|---|---|
| Work | *IRASim: A Fine-Grained World Model for Robot Manipulation* | This entry uses the peer-reviewed ICCV 2025 formulation and experiments. |
| Paper snapshot | `arXiv:2406.14540v2`, dated 2025-07-30; ICCV 2025, pp.9834-9844 | Equations, tables, appendices, and result claims refer to the 28-page v2 artifact. [IRASRC-PAPER-V2] |
| Inspected paper identity | SHA256 `aa781982d5635cbe5afdbb11d074b12151e453f7b8d7c0e41988c3c7aa9b1751` | Prevents silent substitution of another arXiv revision. [IRASRC-PAPER-V2] |
| Predecessor | v1, *Learning Interactive Real-Robot Action Simulators*, submitted 2024-06-20 | The old title and three-dataset benchmark explain the narrower public code and README surface. [IRASRC-PAPER-V1] |
| Official code | `bytedance/IRASim@c72b6dade6fcd65971e0aa8ab49ea39b15108c90` | This is the immutable released implementation inspected for mechanism-to-code mapping. [IRASRC-CODE-CURRENT] |
| Public artifact bundle | `fangqi/IRASim@dfcbf85c27b2c5d041dbf5df3df272111e758b48` | Pins the outer RT-1, Bridge, and Language-Table archives, including v1 checkpoints; it is not an ICCV-v2 checkpoint release. [IRASRC-HF-BUNDLE] |
| Code license | Apache-2.0 | The repository license does not establish a license for every dataset or checkpoint in the separate Hugging Face bundle. [IRASRC-CODE-CURRENT; IRASRC-HF-BUNDLE] |

The paper and code have different canonical scopes. The paper v2 adds RoboNet, LIBERO policy evaluation, Push-T planning, private real-robot planning, and OpenSora-initialized adaptation. The current public repository still identifies itself with the v1 title, publishes RT-1/Bridge/Language-Table configurations, and contains no released RoboNet, LIBERO, Push-T, reward-model, or real-robot planning pipeline. Paper evidence and released implementation must therefore be retrieved separately rather than merged into an assumed end-to-end package. [IRASRC-PAPER-V2, pp.6-14; IRASRC-CODE-CURRENT]

## Operational model boundary

IRASim is an **action-conditioned visual forward model**. Given historical observations and a future action chunk, it samples the future observation video. Its canonical surface can be written as

`p_theta(I_{t+1:t+n+1} | I_{t-h:t}, a_{t:t+n})`.

The model does not directly output actions, rewards, values, task success, or safety constraints. Policy evaluation requires an external success judge. Model-based planning requires an external proposal policy and value or cost function. A plausible rollout is therefore evidence about predicted observations, not an executable policy or an independently verified physical transition. [IRASRC-PAPER-V2, pp.4-6, Eq.1; pp.9-14]

| Surface | Inputs | Output or decision | Evidence boundary |
|---|---|---|---|
| Short trajectory prediction | one or two historical frames plus 10 or 15 actions | 10 or 15 future frames in one denoising pass | Measures reconstruction under logged actions; it does not isolate all counterfactual dynamics. |
| Long trajectory prediction | historical frame plus an episode action sequence | autoregressively chained video clips | Accumulates generated-state error; reported averages are shorter than the longest qualitative rollouts. |
| LIBERO policy evaluation | a policy rollout action sequence and scene observation | generated rollout judged success/failure by humans | One task, four policy checkpoints, and 50 trials per checkpoint; the `r=0.99` correlation has only four paired points. |
| Push-T planning | `K` policy proposals, IRASim rollouts, ResNet50 IoU predictor | execute the highest predicted-value proposal | Value quality and world-model quality are coupled; `P=0` shows larger search can exploit an unadapted model. |
| Real-robot planning | 50 sampled trajectories, goal image, MSE or ResNet50 cost | top-five candidates executed for evaluation | Three tasks are drawn from the training dataset and the dataset/model are not public in the official code. |
| Keyboard/VR control | out-of-distribution action chunks | qualitative virtual rollout | Demonstrates condition response but provides no numerical OOD-action fidelity or safety guarantee. |

## Knowledge map

| Question | Canonical page |
|---|---|
| What are the prediction equation, architecture, action-conditioning mechanism, data regimes, experiments, ablations, and limitations? | [`paper.md`](paper.md) |
| Which released files implement each mechanism, and where does the code diverge from ICCV v2? | [`codebase.md`](codebase.md) |
| What has actually been inspected or executed, what remains unattempted, and what evidence would establish reproduction? | [`reproduction.md`](reproduction.md) |
| Which IRASim mechanisms may improve another model, where do they attach, and what would falsify each transfer? | [`optimization-transfer.md`](optimization-transfer.md) |
| Which paper, code, dependency, and artifact identities support the entry? | [`sources.yaml`](sources.yaml) |

These associations support retrieval and synthesis. They do not define Agent selection, task sequence, experiment priority, repository choice, permissions, or AIBuildAI workflow orchestration.

## High-value evidence anchors

- Frame-Ada replaces one video-level trajectory embedding with per-frame action modulation in spatial blocks. Across RT-1, Bridge, and Language-Table it improves the two declared primary short-video metrics, PSNR and latent L2, over Video-Ada; it does not win every SSIM, FID, or FVD cell. [IRASRC-PAPER-V2, pp.5-9, Tables 1-3]
- Human preference only weakly separates Frame-Ada from Video-Ada on RT-1 (`38/32/30` win/tie/loss) and Bridge (`36/30/34`), but separates them on Language-Table (`66/20/14`). The mechanism should be judged with action-sensitive and task-state measures, not a universal visual-quality claim. [IRASRC-PAPER-V2, p.9, Fig.4; pp.23-24]
- Adding failure-containing policy rollouts is the clearest data intervention for decision use. On Push-T, increasing candidates with no post-trained rollouts reduces IoU from `0.637` at `K=1` to `0.418` at `K=50`; with `P=1000`, the same search reaches `0.961`. [IRASRC-PAPER-V2, pp.10-13, Table 5]
- The paper's statement that performance consistently increases with `K` for every `P>0` is stronger than its table: the `P=200` row drops from `0.916` at `K=10` to `0.912` at `K=50`, and the `P=500` row drops from `0.907` at `K=5` to `0.906` at `K=10`. Preserve the table rather than converting the narrative into a monotonic scaling rule. [IRASRC-PAPER-V2, pp.11-13, Table 5]
- Training duration is internally inconsistent: Appendix E says 300,000 steps, public configs and checkpoint names use 300,000, but Table 10 prints 3,000,000. Exact reproduction should treat 300,000 as implementation-aligned and retain the table conflict. [IRASRC-PAPER-V2, pp.21-24, Tables 10-12; IRASRC-CODE-CURRENT]
- The released repository contains two syntax-invalid scripts and several documentation/config mismatches. A public checkpoint is available inside a large split archive, but a successful local inference has not been established by this KB. [`reproduction.md`](reproduction.md) owns the executed-state boundary.

## Sources

Source identities and revision pins are maintained in [`sources.yaml`](sources.yaml). Claim-level locators remain in the owning pages.
