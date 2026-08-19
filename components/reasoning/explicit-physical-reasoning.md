---
id: world-model-kb.components.reasoning.explicit-physical-reasoning
title: Explicit Physical and Embodied Reasoning
kind: component
status: maintained
last_updated: 2026-08-19
owners:
  - AIBuildAI world-model group
---

# Explicit Physical and Embodied Reasoning

## Retrieval metadata

**Relevant queries:** explicit physical reasoning, physical common sense, embodied reasoning, Cosmos-Reason1, Physical AI SFT, GRPO, visual chain of thought, text plan grounding.

**Knowledge provided:** The shift from implicit predictive state to language-addressable physical judgments, the Cosmos-Reason1 data and post-training mechanism, its measured gains, and the boundary between semantic reasoning and executable action.

**Related pages:** [World foundation models](../../foundations/definitions-and-taxonomy/world-foundation-model.md) owns the general family; [robotics and embodied AI](../../foundations/embodied-systems/robotics-and-embodied-ai.md) owns embodiment contracts; [Cosmos3-Nano Reasoner](../../models/cosmos3-nano/reasoner.md) owns the later model implementation.

## Method definition

Explicit physical reasoning models a conditional distribution over an externally inspectable answer, rationale, explanation, or plan:

\[
p_\phi(y\mid o_{\leq t},q,c).
\]

Unlike latent simulation, the output can name objects, relations, temporal order, physical constraints, and intended actions. Inspectability is useful for supervision and evaluation, but language also introduces shortcut risks. A model can produce a coherent explanation from dataset priors without correctly grounding the relevant visual evidence or simulating the intervention.

The method must distinguish:

- **physical common sense:** spatial, temporal, material, and fundamental-physics judgments;
- **embodied reasoning:** sensory interpretation, action effects, constraints, interaction history, and embodiment;
- **planning language:** an ordered description of subgoals;
- **executable control:** actions with units, frames, rates, constraints, and feedback.

Only the last surface directly controls a robot.

## Cosmos-Reason1 data and architecture

The current Cosmos-Reason1 report revision describes 7B and 56B vision-language models and two principal post-training stages: Physical AI supervised fine-tuning followed by Physical AI reinforcement learning. The 7B model uses a Qwen2.5-VL base; the 56B model uses a larger hybrid Mamba–MLP–Transformer language backbone. [R1-TR, pp. 6–15]

Its knowledge ontology separates physical common sense into space, time, and fundamental physics, with finer subcategories, and embodied reasoning into sensory processing, action effects, physical constraints, interaction learning, and embodiment. The report describes roughly four million video–text annotations created through model distillation and human annotation. [R1-TR, pp. 8–15]

The ontology is a data and evaluation mechanism: it exposes which physical relations receive supervision and prevents one broad aggregate from hiding entire missing categories. It is not a proof that the learned representation is causal or complete.

## Supervised and reinforcement post-training

Supervised fine-tuning teaches the model to express answers and rationales that reflect the Physical AI annotations. The RL stage applies group relative policy optimization with an exact-answer reward and a format reward on multiple-choice reasoning tasks. The reported configuration samples nine outputs per question, uses a maximum response length of 6,144 tokens, learning rate \(4\times10^{-6}\), KL coefficient 0.005, and 500 iterations. [R1-TR, pp. 15, 20]

The mechanism differs across stages:

- SFT expands the target distribution toward physical and embodied demonstrations.
- Exact-answer reward shifts probability toward task-correct options.
- Format reward stabilizes parseable outputs.
- KL regularization limits departure from the reference policy.

Exact-answer reward verifies a benchmark response, not the faithfulness of every intermediate rationale. A rationale can be post-hoc even when the final answer is correct.

## Reported evidence

For the 7B model, SFT raised the reported physical-common-sense average from 47.4 to 54.3 and the embodied-reasoning average from 50.8 to 61.8 relative to the named Qwen2.5-VL-7B baseline. Across the combined evaluation, RL raised the average from 60.7 to 65.7. The change was not uniform: HoloAssist decreased from 63 to 60 while other rows improved. [R1-TR, Tables 4 and 8–10]

On the report's intuitive-physics aggregate, the base model scored 42.1, SFT 74.5, and RL 81.5. The large SFT delta supports targeted physical supervision for that evaluation. It does not establish a corresponding gain in continuous state prediction or robot control. [R1-TR, Tables 8–10]

The correct inference is scoped:

- targeted data substantially changes explicit Physical AI benchmark behavior;
- RL provides additional aggregate improvement under the reported reward;
- per-dataset regressions require slice-level analysis;
- no table converts the language output into an action tensor.

## Design and data surfaces

| Surface | Mechanism | Measurement | Risk |
|---|---|---|---|
| Ontology coverage | balances physical relation types | per-category held-out accuracy | synthetic taxonomy artifacts |
| Counterfactual pairs | forces sensitivity to changed physical conditions | answer-change consistency | lexical leakage |
| Failure and recovery examples | exposes violated assumptions and replanning | failure diagnosis and recovery plan quality | overfitting common failure templates |
| Rationale supervision | makes intermediate concepts inspectable | faithfulness interventions | post-hoc explanation |
| Reward composition | changes correctness, format, consistency, or verification pressure | per-dataset reward ablation | reward hacking and regression |
| Visual grounding | binds claims to regions, frames, or events | occlusion and evidence-removal tests | language-prior shortcuts |
| Action schema grounding | maps plans to typed control variables | feasibility and replay consistency | unsupported embodiment transfer |

Any reward change should report both aggregate and worst-slice deltas. A gain from simultaneously changing data, prompts, and reward cannot attribute the mechanism.

## Evaluation and falsification

Explicit reasoning requires more than benchmark accuracy:

1. Matched visual counterfactuals should change the answer in the expected direction.
2. Removing the decisive frame or region should reduce confidence or alter the rationale.
3. Paraphrased questions should preserve the physical judgment.
4. Explanations should predict measurable state changes, not only restate the answer.
5. Text plans should be checked for action-schema completeness and kinematic feasibility.
6. Closed-loop execution should remain a separate evaluation.

If a model preserves accuracy when decisive visual evidence is contradicted, the result supports language prior use rather than grounded physical reasoning.

## Cosmos3-Nano connection

Cosmos3-Nano Reasoner is initialized from Qwen3-VL-8B and receives its own multimodal pre-training and supervised fine-tuning. The Cosmos 3 report does not document simply carrying the Cosmos-Reason1 GRPO recipe into Nano. Cosmos-Reason1 therefore supplies a lineage and intervention hypothesis, not an undocumented Nano training fact. [R1-TR, pp. 15, 20; C3-TR, pp. 25–27]

Candidate adaptations include counterfactual physical data, category-balanced evaluation, failure-recovery supervision, and verifier or consistency rewards. Their value must be tested against general VLM regression, rationale faithfulness, Generator conditioning utility, and downstream action grounding.

## Sources

- [R1-TR] identifies Cosmos-Reason1 arXiv v3 and its exact 7B/56B, SFT, RL, and evaluation surface.
- [C3-TR] identifies the later Cosmos 3 model family; Cosmos3-Nano-specific facts remain in its Model entry.
