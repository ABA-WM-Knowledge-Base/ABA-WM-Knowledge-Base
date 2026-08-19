---
id: world-model-kb.components.reasoning.comparison-and-optimization
title: Reasoning Method Comparison and Optimization
kind: component
status: maintained
last_updated: 2026-08-19
owners:
  - AIBuildAI world-model group
---

# Reasoning Method Comparison and Optimization

## Retrieval metadata

**Relevant queries:** choose reasoning method, compare latent imagination JEPA explicit reasoning, reasoning failure diagnosis, Cosmos3-Nano reasoning optimization, reasoning evaluation, open reasoning questions.

**Knowledge provided:** Stable comparison axes across reasoning methods, recurring evidence-supported patterns, failure-to-measurement mappings, Cosmos3-Nano attachment hypotheses, and unresolved questions.

**Related pages:** [Latent simulation](latent-simulation-and-imagination.md), [predictive representation](predictive-representation-and-planning.md), [explicit physical reasoning](explicit-physical-reasoning.md), and [reasoning integration](reasoning-generation-action.md) own method details; [evaluation methodology](../../foundations/data-and-evaluation/evaluation-methodology.md) owns general evidence rules.

## Comparison by method, not chronology

| Method | World representation | Reasoning operation | Strongest evidence surface | Principal unresolved boundary |
|---|---|---|---|---|
| Latent simulation | stochastic recurrent state | roll forward candidate actions | realized return under learned-model use | model exploitation and prior drift |
| Latent imagination actor–critic | state, reward, continuation, and value | improve behavior through imagined trajectories | sample efficiency and environment return | shared transition/value bias |
| Predictive representation | target embedding predicted from context | latent comparison and goal search | transfer probes plus planning success | action grounding and lost control detail |
| Explicit physical reasoning | language-addressable multimodal state | answer, explain, or form a text plan | balanced task accuracy and grounding tests | shortcuts and plan-to-action gap |
| Reasoning–generation integration | AR semantic context plus continuous media/action latents | condition generation or verify a plan | interface ablation and downstream outcome | directional coupling and latency |
| Executable policy | embodiment-specific observation/action state | issue feedback-conditioned action chunks | closed-loop task and safety metrics | cross-embodiment validity |

The methods are not replacements on one scale. Selection depends on the required output, available supervision, uncertainty model, latency, and downstream decision.

## Recurring supported patterns

### Preserve decision-relevant information

World Models and Dreamer show that a compact latent can support control; V-JEPA 2 shows that reconstruction-free features can support goal search; explicit Physical AI supervision improves language-addressable reasoning. [FND-WORLD-MODELS-2018; MBRL-DREAMER-2020; VJ2-PAPER; R1-TR]

The transferable principle is conditional: retain information required by the target decision rather than maximizing reconstruction or abstraction alone. Test state probes, action sensitivity, and downstream utility together.

### Couple prediction to consequence-sensitive evidence

The World Models virtual–real gap, Dreamer's environment-return loop, and V-JEPA 2-AC planning experiments all show that passive prediction metrics are insufficient for decision claims. [FND-WORLD-MODELS-2018, Table 2; MBRL-DREAMER-2020; VJ2-PAPER, Sec. 5]

Action counterfactuals should alter predicted outcomes correctly, and those predictions should improve realized decisions under a matched budget.

### Separate broad pretraining from action grounding

V-JEPA 2-AC freezes its large video representation while learning action-conditioned prediction from a smaller interaction set. This yields a clean representation-versus-action attribution test. [VJ2-PAPER, Secs. 3–5]

The same separation can be tested in Cosmos3-Nano, but reduced data need is a hypothesis until compared with scratch and jointly adapted baselines.

### Treat post-training signals as an interacting system

DreamerV3's robustness stack and Cosmos-Reason1's SFT/RL stages affect different failure surfaces. Aggregate gains can hide task regressions. [MBRL-DREAMERV3-2025, Fig. 6; R1-TR, Tables 8–10]

Report component ablations, interactions, per-slice deltas, and general-capability regressions rather than copying one coefficient or reward into another architecture.

### Preserve interface boundaries

Cosmos 3 makes Reasoner-to-Generator conditioning architecturally possible, but does not prove transfer or convert a language plan into a policy. [C3-TR, Fig. 3 and pp. 55–69]

Freeze one side of the interface where possible, hold inference budget fixed, and measure the downstream surface directly.

## Failure-to-measurement map

| Observable failure | Competing causes | Discriminating measurement |
|---|---|---|
| High imagined value, low return | model exploitation or reward bias | identical action-sequence replay in model and environment |
| Good one-step prediction, poor long rollout | compounding error or memory loss | horizon-conditioned prior rollout error |
| Strong reconstruction, weak planning | nuisance-detail capacity or missing control state | task-state probes and matched planning return |
| Strong representation probe, weak control | separability without action structure | action-conditioned latent error and ranking regret |
| Correct text answer, wrong counterfactual | language shortcut or missing grounding | matched visual counterfactuals |
| Coherent plan, failed execution | missing action schema or infeasibility | typed action validation and closed-loop stage success |
| Reasoner gain, no Generator gain | unused semantics or interface bottleneck | frozen-Generator condition ablation |
| Aggregate gain with slice regression | mixture or reward imbalance | per-category deltas and worst-slice confidence intervals |

## Cosmos3-Nano attachment map

| Target surface | Method knowledge | Testable hypothesis | Evidence required |
|---|---|---|---|
| Reasoner representation | predictive embedding | auxiliary future-feature prediction improves physical state | probes, counterfactual accuracy, VLM regressions |
| Reasoner SFT | explicit physical reasoning | balanced counterfactual and failure data reduce shortcuts | category-held-out and evidence-removal tests |
| Reasoner post-training | explicit reward design | verification or consistency rewards improve robustness | reward ablation with per-dataset deltas |
| AR-to-DM context | integration | structured relations or subgoals improve generation | frozen-Generator context comparison |
| Generator FD | latent simulation | action-sensitive and multi-step losses improve consequences | horizon calibration and action counterfactuals |
| Joint WAM | simulation plus integration | action/video consistency helps only when replay-grounded | feasibility, replay, ranking, closed-loop success |
| Policy-DROID | predictive representation or shared initialization | pretrained features reduce target data need | matched sample-efficiency and latency |

Exact experiment configurations remain in the [Cosmos3-Nano optimization playbook](../../models/cosmos3-nano/optimization-playbook.md); this table provides mechanism and evidence logic.

## Open questions

1. Which representation retains the minimum state needed for physical decisions across tasks and embodiments?
2. How should epistemic uncertainty and multimodal valid futures propagate into plans or actions?
3. Which explicit-reasoning gains arise from visual dynamics rather than language priors?
4. Can passive-video prediction reduce action data without weakening intervention sensitivity?
5. When does longer imagination improve decisions rather than amplify exploitation?
6. Can generated futures revise semantic plans at a viable control rate?
7. Which offline combination best predicts failure recovery, not only nominal success?

These questions define missing evidence, not work priority or workflow.

## Sources

Method-specific source identities and exact locators are listed on the owning method pages. [C3-TR] anchors the Cosmos3-Nano attachment hypotheses; none is a reproduced optimization result.
