---
id: world-model-kb.papers.v-jepa-2.paper
title: V-JEPA 2 Method, Architecture, and Experimental Evidence
kind: paper
status: maintained
last_updated: 2026-08-14
owners:
  - AIBuildAI world-model group
---

# V-JEPA 2 Method, Architecture, and Experimental Evidence

## Retrieval metadata

**Relevant queries:** V-JEPA 2 architecture, VideoMix22M, ViT-g 1B, SSv2 77.3, EK100 39.7, PerceptionTest 84.0, progressive 256/16 to 384/64, V-JEPA 2-AC DROID, Franka Table 2 Lab 1 vs Lab 2, Cosmos video WM Table 3, three image sub-goals, or V-JEPA 2.1.

**Knowledge provided:** the paper's problem formulation per variant, complete input-to-output architecture, data and training protocol, understanding and robot experiments with locators, ablations with numbers, and the limits of each claim.

**Related pages:** [Representation learning and JEPA](../../foundations/representations/representation-learning-and-jepa.md) owns the generic objective; [latent world models](../../foundations/representations/latent-world-model.md) owns decoder-free prediction; [planning and control](../../foundations/decision-making/planning-and-control.md) owns latent MPC; [actions and interventions](../../foundations/problem-formulation/actions-and-interventions.md) owns action semantics; [evaluation methodology](../../foundations/data-and-evaluation/evaluation-methodology.md) owns evidence-layer distinctions.

Foundation bibliographic identity: [OBJ-VJEPA2-2025].

## 1. Problem statement

### 1.1 Three named stacks (mandatory split)

This paper family contains three public names that must not share metrics:

| Variant | What it is | Action input | Robot pick-place evidence |
|---|---|---|---|
| **V-JEPA 2** | action-free video JEPA encoder + predictor | none | **none** — do not assign Franka numbers here |
| **V-JEPA 2-AC** | frozen encoder + action-conditioned predictor + latent CEM | yes | Table 2 / Table 3 only |
| **V-JEPA 2.1** | later repository training recipe / encoder (`app/vjepa_2_1`) | per release notes | **not** paper Table 2/3 unless a 2.1 card repeats them |

[OBJ-VJEPA2-2025; VJ2-PAPER; VJ2-CODE]

### 1.2 Action-free prediction task (V-JEPA 2)

Given a video clip, a context mask, and target blocks, predict **target encoder embeddings**, not pixels:

```text
z_ctx = Enc_theta(unmasked patches)
z_tgt = sg(Enc_bar(target patches))
z_hat = Pred_phi(z_ctx, mask tokens)
L_JEPA = distance(z_hat, z_tgt)
```

The encoder is a Vision Transformer from ViT-L (~300M) to ViT-g (~1B). The predictor is approximately ViT-small. No pixel decoder is trained. The scientific claim is that large-scale **action-free** video (1M+ hours; VideoMix22M) yields representations for understanding, anticipation, and as a frozen backbone for a *separate* action-conditioned planner. [VJ2-PAPER, Sec. 1-3]

### 1.3 Action-conditioned planning task (V-JEPA 2-AC only)

After freezing the ViT-g encoder, a smaller predictor is trained on **<62 hours** of DROID robot video with actions. Planning is CEM in latent space against **image sub-goals**. Pick-place uses **three** goal images (grasp 4 steps, near-place 10, place 4). Franka + RobotiQ evaluations in two labs, 10 trials per cell, are **2-AC evidence**. [VJ2-PAPER, Sec. 4, Tables 2-3]

## 2. Method and architecture

### 2.1 V-JEPA 2 data flow (action-free)

```text
raw clip (up to 64 frames at cooldown)
        |
tubelet embed (patch 16, tubelet 2)
        |
multi-block 3-D mask  -->  context tokens | target tokens
        |                         |
   context encoder Enc_theta    target encoder Enc_bar (EMA / stop-grad)
        |
   predictor (narrow ViT) on context + mask tokens
        |
   predicted target embeddings
        |
   L1/L2 in representation space  (no RGB reconstruction)
```

Masking is spatiotemporal multi-block 3-D (`src/masks/multiseq_multiblock3d.py` in the release). Collapse is prevented by a stop-gradient / EMA target encoder and by predicting embeddings rather than pixels. [VJ2-PAPER, Sec. 3; VJ2-CODE]

### 2.2 Progressive resolution schedule

Pretraining is not full-resolution from step one. The paper uses a long **16-frame / 256 px** phase (including warmup and a large main-iteration block on the order of **252K** total pretrain steps in the scaling narrative), then a **cooldown** at **64 frames / 384 px** for the ViT-g384 model. End-to-end 64×384×384 from scratch is estimated at about **60 GPU-years**; the progressive schedule is reported as up to **8x** cheaper than full-resolution training. Native 64-frame 384 training of ViT-g is the expensive counterfactual, not the released recipe. [VJ2-PAPER, Sec. 3, Fig. 5]

### 2.3 V-JEPA 2-AC data flow

```text
DROID RGB  (Franka + RobotiQ)
        |
frozen ViT-g encoder
        |
feature maps z_k  of shape 16 x 16 x 1408   (256 px, patch 16)
        |
interleave per time index:  (a_k, s_k, z_k)
        |     a_k = action embed (7-D)
        |     s_k = proprio / state embed
        |
action-conditioned predictor  (causal action-block attention)
        |
teacher-forcing loss on next-z  (not pixel decode)
        |
planning: CEM over action sequences scoring predicted z vs goal encoding
          pick-place: three image sub-goals (4 / 10 / 4 steps)
```

The AC predictor maps encoder tokens into a predictor width, concatenates action and state tokens **in front of** each frame's spatial tokens, applies RoPE blocks with a causal action-block mask, then projects back to encoder width. Optional extrinsics add a third conditioning token. [VJ2-PAPER, Sec. 4; VJ2-CODE, `src/models/ac_predictor.py`]

Teacher-forcing next-z is the training loss. Closed-loop CEM rollouts are inference-only and accumulate error; the paper lists long-horizon accumulation as a limit. [VJ2-PAPER, Sec. 4-5]

### 2.4 Planning versus video world models

V-JEPA 2-AC does **not** generate RGB. A concurrent baseline in Table 3 is a **Cosmos video world model** that does. That baseline is slower and, in Lab 2, weaker on grasp and pick-place. This is evidence about **latent vs video** planners on this robot setup, not a claim that Cosmos Generator FD/WAM is generally inferior, and not an invitation to put JEPA losses on a Generator. [VJ2-PAPER, Table 3]

## 3. Experimental setup

### 3.1 Action-free pretraining data

| Aspect | Value |
|---|---|
| Duration | **1M+ hours** of video |
| Mix name | **VideoMix22M** (SSv2, K400/600/700, HowTo100M, retrieval-curated YT1B, ImageNet-as-video) |
| Actions / labels | none at pretrain |
| Encoder scale | ViT-L ~300M → ViT-g ~1B |
| Predictor | ~ViT-small |
| Schedule | long 16f/256 phase then cooldown 64f/384 |

[VJ2-PAPER, Sec. 3, Table 1]

### 3.2 Understanding evaluation

Frozen or lightly probed encoders are evaluated on video classification and anticipation. LLM alignment (Qwen2-7B / 8B-class) is a **separate** head for PerceptionTest and video QA; it is not the robot planner. [VJ2-PAPER, Sec. 4, Tables 4-6]

### 3.3 Robot evaluation (2-AC only)

| Aspect | Value |
|---|---|
| Post-train data | DROID **<62 h** |
| Encoder | **frozen** ViT-g |
| Embodiment | Franka + RobotiQ |
| Sites | two labs |
| Trials | **10** per cell |
| Goal spec | image sub-goals; pick-place uses **three** images (4 / 10 / 4 steps) |

[VJ2-PAPER, Sec. 4, Tables 2-3]

## 4. Results

### 4.1 Understanding (V-JEPA 2, action-free)

ViT-g384 (1B, 384 px) frozen-probe table: [VJ2-PAPER, Table 4]

| Benchmark | Metric | ViT-g384 |
|---|---|---:|
| Kinetics-400 | top-1 | 87.3 |
| Something-Something v2 | top-1 | **77.3** |
| Diving48 | top-1 | 90.2 |
| Jester | top-1 | 97.8 |
| COIN | top-1 | 87.3 |
| ImageNet | top-1 | 91.1 |
| Six-task average | — | **85.1** (an **88.2** column appears under a different aggregation; cite the named task) |

ViT-g at 256 px is lower on SSv2 (**75.3** in the paper's 256 protocol). These numbers are **not** robot success rates. [VJ2-PAPER, Table 4]

EK100 action anticipation, mean-class recall-at-5 on val: ViT-L **32.7** → ViT-g **38.0** → ViT-g384 **39.7** (verb 63.6, noun 57.1). [VJ2-PAPER, Table 5]

PerceptionTest **84.0** is reported after **8B-class LLM alignment**. It must not be quoted as a frozen ViT-g number. [VJ2-PAPER, Table 6; VJ2-CODE README]

### 4.2 Scaling (action-free)

Cumulative gains versus a ViT-L/16 baseline, ending at **88.2%** (**+4.0** total) on the paper's scaling probe: [VJ2-PAPER, Fig. 5 / scaling table]

| Lever | Change | Approximate gain |
|---|---|---:|
| Data | 2M → 22M videos | +1.0 |
| Model | ViT-L → ViT-g | +1.5 |
| Steps | 90K → 252K iterations | +0.8 |
| Resolution / frames | 256→384 and 16→64 | remainder of the +4.0 |

The four levers are complementary. Quoting 88.2% without naming the probe task and the ViT-L/16 baseline is incomplete. A 64-frame cooldown helps in this study; 128/256-frame probes did not add a matching gain on the reported set. [VJ2-PAPER, Fig. 5, Table 4]

### 4.3 Robot success (V-JEPA 2-AC only, Table 2)

Two objects (cup, box), 10 trials per lab, Franka + RobotiQ: [VJ2-PAPER, Table 2]

| Skill | Lab 1 | Lab 2 | Average |
|---|---:|---:|---:|
| Reach | 100% | 100% | **100%** |
| Grasp cup / box | 70 / 30 | 60 / 20 | **65 / 25** |
| Reach with object cup / box | 90 / 80 | 60 / 70 | **75 / 75** |
| Pick-and-place cup / box | 80 / 80 | 80 / 50 | **80 / 65** |

Reach is saturated. Grasp is object-sensitive (cup 65% vs box 25%). Lab 2 box pick-place (50%) versus Lab 1 (80%) is the paper's camera-pose caution. Octo, under the same protocol, averages grasp cup/box 15%/0% and pick-place 15%/10%. Pick-place is not a property of the action-free encoder. [VJ2-PAPER, Table 2, Sec. 4.2; OBJ-VJEPA2-2025]

### 4.4 Lab 2 CEM comparison on RTX 4090 (Table 3)

Same robot protocol, different world-model inner loop, CEM, goal-embedding energy: [VJ2-PAPER, Table 3]

| Planner | Samples / iters / horizon | Time / action | Reach | Grasp cup / box | Pick-place cup / box |
|---|---|---|---:|---:|---:|
| Cosmos video WM | 80 samples, 10 iter, **H=1** | **4 min** | 80% | 0% / 20% | 0% / 0% |
| V-JEPA 2-AC | **800** samples, 10 iter, H=1 | **16 s** | 100% | 60% / 20% | 80% / 50% |

The video world model is constrained to H=1 by latency; a full pick-place episode with Cosmos is reported as more than one hour wall-clock. V-JEPA 2-AC can afford 10x samples and still be two orders of magnitude faster per action. Grasp-box remains weak in both (20%). [VJ2-PAPER, Table 3]

## 5. Ablations and protocol facts

| Observation | Effect | Locator |
|---|---|---|
| Progressive 16f/256 then 64f/384 | up to 8x vs full-res; 64×384×384 ≈ 60 GPU-years | [VJ2-PAPER, Sec. 3, Fig. 5] |
| Data / model / steps / resolution | +1.0 / +1.5 / +0.8 / rest of +4.0 | [VJ2-PAPER, Fig. 5] |
| ViT-g 256 vs g384 on SSv2 | 75.3 vs 77.3 | [VJ2-PAPER, Table 4] |
| Frozen ViT-g + AC predictor | robot numbers exist at all | [VJ2-PAPER, Sec. 4] |
| Three image sub-goals | required for pick-place (4 / 10 / 4) | [VJ2-PAPER, Sec. 4.2] |
| Teacher-forcing next-z | training; CEM rollout is inference | [VJ2-PAPER, Sec. 4] |
| LLM 8B-class alignment | PerceptionTest 84.0 and QA tables only | [VJ2-PAPER, Tables 4-6] |
| Octo under the same robot protocol | much lower grasp and pick-place | [VJ2-PAPER, Table 2] |

No paper table assigns Franka success to V-JEPA 2.1 or to the action-free encoder alone.

## 6. Limits and evidence boundaries

- **Variant leakage is a documentation failure.** Action-free SSv2/EK100/PerceptionTest numbers must not be cited as manipulation competence. [OBJ-VJEPA2-2025]
- **Camera pose sensitivity.** Monocular RGB induces an implicit action axis; Lab 1 vs Lab 2 box pick-place is 80% vs 50%. Changing camera extrinsics without retraining can break CEM. [VJ2-PAPER, Table 2, Sec. 5]
- **Long-horizon error accumulation.** Teacher-forcing does not train closed-loop predicted prefixes. [VJ2-PAPER, Sec. 5]
- **Image sub-goals** are required for pick-place; language-only goals are not the Table 2 protocol. [VJ2-PAPER, Sec. 4.2, Sec. 5]
- **DROID <62 h** and **10 trials** per cell: binomial uncertainty is large (especially grasp-box 25% and Table 3 grasp-box 20%).
- **Two labs** are not a random embodiment sample; both use Franka + RobotiQ.
- **1M+ hour pretrain** is not a local reproduction target; transfers should start from released checkpoints.
- **V-JEPA 2.1** is a repository recipe (`app/vjepa_2_1/`). It is not a license to relabel Table 2. [VJ2-CODE]
- **Table 3 Cosmos video WM** is a published baseline on this robot, not a Cosmos3-Nano FD/WAM transfer study.

These limits narrow the evidence; they do not negate SSv2 77.3 or Table 2 pick-place. [`reproduction.md`](reproduction.md) owns executed-state claims.

## Sources

- [VJ2-PAPER] *V-JEPA 2: Self-Supervised Video Models Enable Understanding, Prediction and Planning*, arXiv:2506.09985.
- [VJ2-CODE] `facebookresearch/vjepa2` at the pinned commit.
- [VJ2-PROJECT] presentation surface; numbers bind to the paper.
- [OBJ-VJEPA2-2025] Foundation identity and variant discipline.
