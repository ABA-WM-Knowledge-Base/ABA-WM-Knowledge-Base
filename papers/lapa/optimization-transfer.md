---
id: world-model-kb.papers.lapa.optimization-transfer
title: LAPA Transferable Optimization Knowledge
kind: guide
status: maintained
last_updated: 2026-08-14
owners:
  - AIBuildAI world-model group
---

# LAPA Transferable Optimization Knowledge

## Retrieval metadata

**Relevant queries:** transfer LAPA, LAQ, latent VLA, unlabeled video pretrain, Cosmos3 WAM/ID head, not Reasoner, LAPA7B-openx.

**Knowledge provided:** ten falsifiable hypotheses attached to Generator WAM and ID surfaces. Continuous Policy-DROID is out of scope unless a discrete-to-continuous adapter is tested.

**Related pages:** [`paper.md`](paper.md); [inverse dynamics](../../foundations/problem-formulation/inverse-dynamics.md); [Cosmos3-Nano action modeling](../../models/cosmos3-nano/action-modeling.md).

## 1. Transfer discipline

LAPA shows that **discrete pseudo-actions from video** plus **instruction-conditioned code prediction** transfer to robots after a small labeled adapter. Attach on Cosmos3 **Generator WAM/ID**, not Reasoner text. `LAPA7B-openx` ([LAPA-HF]) is a latent VLA, not a joint policy.

## 2. Intervention matrix

| ID | Target failure | Mechanism | Attachment | Evidence | Risk |
|---|---|---|---|---|---|
| `LA-XFER-01` | no action labels | LAQ from frame pairs | ID quantizer | Stage 1 | codebook collapse |
| `LA-XFER-02` | ID overfits embodiment | latent VLA pretrain | WAM token prediction | Table 1 vs Scratch | gap |
| `LA-XFER-03` | language ignored | instruction-conditioned codes | multimodal path | Table 2 unseen instr 48.5 | shortcut |
| `LA-XFER-04` | tiny labeled set | two-stage then adapter | domain decoder | 1k Language Table | negative transfer |
| `LA-XFER-05` | rollouts ignore actions | LAQ decoder WM | forward head | Fig. 7 qualitative | visuals only |
| `LA-XFER-06` | dense transition tokens | VQ bottleneck `8^4` | tokenizer | inference README | lost contact |
| `LA-XFER-07` | joint then forget | freeze LAQ then VLA | staged schedule | three-stage design | forgetting |
| `LA-XFER-08` | camera motion as action | pair `(o_t,o_{t+1})` | ID inputs | LAQ architecture | false codes |
| `LA-XFER-09` | codebook too small | vocab/sequence scale | LAQ size | Fig. 5, 16 | compute |
| `LA-XFER-10` | no robot labels at all | human SSv2 pretrain | unlabeled human video | Table 2 human 34.0; Fig. 4 | embodiment gap |

## 3. `LA-XFER-01`: discrete LAQ from video

**Source mechanism.** LAQ is a vector-quantized inverse-dynamics model on unlabeled frame pairs `(o_t, o_{t+H})`. It does not see robot joints in Stage 1. The released inference alphabet is size `8^4`. Implementation: `laq/laq_model/latent_action_quantization.py` and NSVQ in `nsvq.py`. [LAPA-PAPER, Sec. 3; LAPA-CODE]

**Target behavior.** Cosmos3 inverse-dynamics when joint labels are scarce or heterogeneous across embodiments.

**Attachment.** Auxiliary **ID quantizer** on Generator visual transitions. Not Reasoner text, not a Policy-DROID continuous head without a discrete-to-continuous adapter.

**Minimum controlled experiment.** Continuous ID regression versus scalar VQ versus multi-token LAQ, matched parameter count, same unlabeled shard, same Stage-3 adapter budget. Probes: reverse-time pairs, shuffled frames, and held-out ID accuracy at 1k labels.

**Expected movement.** Higher held-out ID accuracy at equal labels; reverse-time codes should not equal forward codes.

**Falsification.** Reject if codes fail reverse-time / shuffle-frame probes, if codebook perplexity collapses, or if continuous ID matches discrete on the 0.5% label Language Table analog.

## 4. `LA-XFER-02`: cross-video latent pretrain

**Source mechanism.** Language Table in-domain: LAPA **62.0±8.7** versus Scratch **15.6±9.2** after 181k unlabeled videos plus 1k labeled trajectories (0.5%). ActionVLA with ground-truth actions still leads at **77.0±3.5**; the transfer is the unlabeled-pretrain gap, not a claim that LAPA beats labeled VLAs. [LAPA-PAPER, Table 1]

**Target behavior.** WAM/ID that only sees one robot's joints and therefore fails on new verbs or tables.

**Attachment.** Predict discrete codes from (image, instruction) on mixed video, then a small domain adapter (`deploy.py` analog). Generator WAM token prediction, not Reasoner.

**Minimum controlled experiment.** Scratch versus latent-pretrain at 1k labels, matched adapter architecture and finetune steps. Report in-domain and unseen-instruction slices separately.

**Expected movement.** Large relative gain in the 0.5% label regime; smaller gap as labels approach 100%.

**Falsification.** Reject if Scratch matches at 1k labels, or if pretrain only helps in-domain seen combinations.

## 5. `LA-XFER-03`: instruction-conditioned codes

**Source mechanism.** Real-world unseen instruction: LAPA Open-X **48.5** versus OpenVLA 43.4 versus Scratch 25.4. Unseen combo **57.8**. Paired win rate versus OpenVLA Open-X is **65.4%** excluding ties. n=54 is small; many trials tie. [LAPA-PAPER, Table 2, Fig. 11]

**Target behavior.** ID head that ignores language or uses it only as a style tag.

**Attachment.** Language tokens into the WAM/ID path (Generator multimodal), not a Reasoner plan dump that never reaches the action head.

**Minimum controlled experiment.** With versus without instruction; shuffle language; report unseen-instruction partial success and a shuffle drop.

**Expected movement.** Unseen-instruction partial success rises; shuffle drops it toward Scratch.

**Falsification.** Reject if shuffled instructions match true ones, or if language only changes the text log without moving joints.

## 6. `LA-XFER-04`: low-label adapter finetune

**Source mechanism.** Stage 3 maps latents to joints with 1k-7k trajectories. Cross-env still 33.6 versus Scratch 15.6. ActionVLA with labels still leads (64.8). SIMPLER uses 100 finetune trajectories. [LAPA-PAPER, Table 1, Sec. 4.1]

**Target behavior.** Full VLA finetune that needs 100% action labels on every new robot.

**Attachment.** Small decoder on WAM codes to domain action (`latent_pretraining/deploy.py` plus csv scales). Keep LAQ frozen first.

**Minimum controlled experiment.** 100 versus 1k versus full labels, pretrained versus scratch, same embodiment YAML/csv.

**Expected movement.** Pretrain wins below a few thousand trajectories; the gap shrinks with more labels.

**Falsification.** Reject if adapter underperforms scratch at matched labels on the same embodiment, or if Stage 3 without Stages 1-2 matches the pretrained adapter.

## 7. `LA-XFER-05`: latent-action decoder as coarse WM

**Source mechanism.** Fig. 7 shows qualitative closed-loop decode of `(x_1, predicted latent)` without Stage 3 joints (broccoli-from-pot example). This is **not** a control success table. [LAPA-PAPER, Fig. 7, Sec. 5]

**Target behavior.** Need a cheap forward rollout of latent actions before a joint adapter exists.

**Attachment.** LAQ decoder on Generator: `(o, a~) -> o'`. This is a coarse FD head, not Reasoner JEPA.

**Minimum controlled experiment.** Quantify contact/object persistence and shuffled-code video distance. Do not accept anecdotes.

**Expected movement.** Coarse object-change videos aligned with codes; shuffle codes should change the imagined contact.

**Falsification.** Reject if decoder ignores `a~` (shuffle codes = same video) or if pixel metrics improve while objects never move.

## 8. `LA-XFER-06`: tight discrete bottleneck

**Source mechanism.** Inference README: latent space size `8^4`. Fig. 5/16 sweep codebook and sequence length. Language Table prefers vocab growth over sequence length. [LAPA-PAPER, Fig. 5, 16; LAPA-CODE]

**Target behavior.** Over-complete continuous ID that cannot pretrain as a language-model token stream.

**Attachment.** Finite alphabet for WAM tokens on the Generator ID head.

**Minimum controlled experiment.** Sweep codebook size and sequence length on one downstream bench (SIMPLER or Language Table analog). Report collapse diagnostics (perplexity, unused codes).

**Expected movement.** Mid-size codes beat tiny (under-express) and huge (overfit/collapse).

**Falsification.** Reject if continuous ID matches discrete on low-label transfer, or if unused-code fraction exceeds 50% at the chosen size.

## 9. `LA-XFER-07`: staged freeze then joint

**Source mechanism.** Three explicit stages; mixing them is not the released recipe. Scripts: `train_sthv2.py` then `scripts/latent_pretrain_openx.sh` then `scripts/finetune_real.sh`. [LAPA-PAPER; LAPA-CODE]

**Target behavior.** Joint train that destroys the codebook while fitting joints.

**Attachment.** Freeze LAQ while training VLA; then train decoder. Cosmos3 analog: freeze ID quantizer during WAM SFT.

**Minimum controlled experiment.** Staged versus fully joint from step 0, matched total steps and data.

**Expected movement.** Staged keeps codebook entropy and downstream success.

**Falsification.** Reject if joint matches staged at equal steps without collapse.

## 10. `LA-XFER-08`: pair-wise transitions, not single frames

**Source mechanism.** LAQ explains frame **pairs**; window `H` sets delta-time. Bridgev2 5 Hz default `H=3` (~0.6 s); human video ~2.4 s. Fig. 15: robust except very large windows. [LAPA-PAPER, Fig. 15]

**Target behavior.** Static-scene false actions from camera shake or lighting.

**Attachment.** ID inputs `(o_t, o_{t+H})` with H matched to control rate on Generator.

**Minimum controlled experiment.** H in {1, 3, large}; reverse-time negatives; camera-only motion clips if available.

**Expected movement.** H~0.6 s robot default; too large hurts contact timing.

**Falsification.** Reject if single-frame ID matches pair-wise on reverse-time tests.

## 11. `LA-XFER-09`: scale vocab and sequence

**Source mechanism.** Fig. 5/16: larger vocab/sequence helps SIMPLER; Language Table prefers vocab growth over sequence length. Exact Table 12 cells were not fully recovered from HTML. [LAPA-PAPER, Fig. 5, 16]

**Target behavior.** 1-token action that cannot express pick-then-place.

**Attachment.** Multi-token latent actions on WAM.

**Minimum controlled experiment.** Factor vocab x sequence on one downstream bench; freeze other stages.

**Expected movement.** Monotone until saturation; Language Table analog should prefer vocab.

**Falsification.** Reject if extra tokens never move success beyond a 1-token VQ.

## 12. `LA-XFER-10`: human unlabeled video

**Source mechanism.** SSv2 pretrain: real-world AVG **34.0** versus Scratch 21.2; beats OpenVLA-Bridge 30.8 on average despite a larger embodiment gap. Fig. 4: human-video pretrain still beats Scratch/UniPi/Vpt on SIMPLER. Table 12 (10% vs 100% SSv2) cells were not fully recovered. [LAPA-PAPER, Table 2, Fig. 4]

**Target behavior.** No robot teleop available for pretrain.

**Attachment.** Human manipulation video into LAQ+VLA, then robot adapter on Generator WAM/ID.

**Minimum controlled experiment.** 10% versus 100% human hours plus a robot-only control. Report unseen objects separately from in-domain Bridge correlation.

**Expected movement.** Positive transfer on unseen objects; not necessarily Table 2 Open-X 50.1.

**Falsification.** Reject if human video matches scratch after adapter, or if it only helps SIMPLER in-domain Bridge correlation.

## 13. Invalid generalizations

- Do not treat `LAPA7B-openx` as executable joints.
- Do not attach LAQ to Reasoner as a planner ID.
- Do not claim LAPA dominates ActionVLA on Language Table (Table 1 contradicts).
- Do not paste the Hugging Face repo slug into running text; cite [LAPA-HF] and write `LAPA7B-openx`.
- Do not treat Language Table ActionVLA cells as LAPA wins.
- Decoder Fig. 7 is not Table 2.
- SIMPLER WidowX is not Franka Table 2.

## 14. Transfer record template

```text
Hypothesis ID (LA-XFER-NN):
Attachment (Generator WAM/ID, not Reasoner):
Hub citation ([LAPA-HF] / LAPA7B-openx):
Controls (codebook, H, labels, human vs robot video):
Metrics (low-label success, shuffle-instruction, reverse-time ID):
Decision:
```

No transfer experiment is registered.

Cite Hub weights only as [LAPA-HF] / `LAPA7B-openx`. Stage 2 smoke is latents; Stage 3 is joints.

## 15. Attachment checklist for Cosmos3

| Do | Do not |
|---|---|
| Attach LAQ to Generator WAM/ID discrete bottleneck | Attach LAQ to Reasoner as a planner ID |
| Keep Stage 3 adapter per embodiment | Serve Hub latents as Policy-DROID 9D |
| Keep ActionVLA Language Table cells | Claim Table 1 LAPA dominance |
| Separate SIMPLER WidowX from Franka Table 2 | Merge embodiments in one metric row |
| Reverse-time or shuffle-instruction probes | Trust instruction-conditioned codes without a shuffle control |

## Sources

- [LAPA-PAPER], [LAPA-CODE], [LAPA-HF].
