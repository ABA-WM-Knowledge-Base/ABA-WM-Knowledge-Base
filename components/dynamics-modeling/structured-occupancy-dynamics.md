---
id: world-model-kb.components.dynamics-modeling.structured-occupancy-dynamics
title: Structured Occupancy Dynamics
kind: component
status: maintained
last_updated: 2026-08-27
owners:
  - AIBuildAI world-model group
---

# Structured Occupancy Dynamics

## Retrieval metadata

**Relevant queries:** occupancy forecasting, OccWorld PlanU, ego trajectory prediction, 3D occupancy dynamics, nuScenes world model, spatial versus temporal occupancy.

**Knowledge provided:** How occupancy-token models implement scene and ego transitions, which OccWorld ablations isolate spatial versus temporal dynamics, and which variants are not occupancy world models.

**Related pages:** [Discrete and structured state](../world-representation/discrete-and-structured-state.md) owns occupancy tokens; [3D and 4D world models](../../foundations/representations/3d-and-4d-world-model.md) owns geometric formalism; [OccWorld Paper](../../papers/occworld/README.md) owns O/D/T/S tables and licenses; [planning and control](../../foundations/decision-making/planning-and-control.md) owns using forecasts for planning metrics.

## Method definition

Structured occupancy dynamics forecast a geometric scene code and, in OccWorld, ego motion:

\[
p_\theta(\operatorname{occ}_{t+1:t+H}, \tau_{t+1:t+H}\mid \operatorname{occ}_{\leq t}, \tau_{\leq t}).
\]

Default OccWorld uses 2 s of history to predict 3 s of future on a \(50\times 50\) token grid. Ego waypoints are part of the transition output, not an after-the-fact controller. Planning L2/collision on STP3 is a downstream use of that forecast; it still depends on occupancy GT for OccWorld-O. [OCCSRC-PAPER, Secs. 3–4]

This is not pixel FD, not a persistent neural field, and not unlabeled camera dynamics.

## OccWorld transitions and variants

Table 1 forecasting (mIoU/IoU averaged over 1–3 s): Copy&Paste 11.33/20.52; OccWorld-O 17.14/26.63 at 18.0 FPS, with 1 s mIoU 25.78 falling to 10.51 at 3 s. Horizon drop is a dynamics fact: occupancy transitions degrade with time even under GT occupancy input. OccWorld-D 8.62/16.53, OccWorld-T 3.56/8.34, OccWorld-S 0.26/5.00. [OCCSRC-PAPER, Table 1]

Table 2 planning: OccWorld-O L2 1.17 and collision 0.60 (per-horizon 0.43/1.08/1.99 L2 and 0.07/0.38/1.35 collision) versus UniAD 1.03/0.31 with heavier instance/map auxiliaries. Dagger/VAD 0.64/0.24 is another protocol. OccWorld-S planning 1.83/2.02 is not occupancy-WM evidence. [OCCSRC-PAPER, Table 2]

Table 4 isolates dynamics operators: without spatial modeling, forecast mIoU 10.07; without temporal modeling, 8.98; without ego temporal modeling, plan L2 5.89 and collision 6.23. Spatial, temporal, and ego-time structure are separable transition pieces. [OCCSRC-PAPER, Table 4]

OccWorld-O uses occupancy GT. Camera-only OccWorld-S is a negative control. License: nuScenes, Occ3D, and Tsinghua pickles. `forward_autoreg` is `pass` at the inspected pin; autoregressive occupancy rollout in code is not a delivered operator. [OCCSRC-PAPER; OCCSRC-CODE-CURRENT; OCCSRC-NUSCENES]

## Controllable surfaces

| Surface | Mechanism | Expected observable | Main confounder |
|---|---|---|---|
| Spatial transformer | neighboring occupancy | Table 4 w/o spatial | tokenizer grid change |
| Temporal transformer | history to future tokens | 1 s versus 3 s mIoU | Copy&Paste baseline |
| Ego temporal path | pose-token dynamics | plan L2/collision | HD-map aux in UniAD |
| Input supervision O/D/T/S | what the transition sees | Table 1 columns | leaking O scores to S |
| Autoregressive decode | generated occ as next input | code-supported rollout | `pass` stub |

## Evaluation and failure diagnosis

| Symptom | Plausible cause | Discriminating evidence |
|---|---|---|
| Good 1 s, poor 3 s | compounding occupancy error | per-horizon mIoU |
| Plan collapse without ego time | missing \(\tau\) dynamics | Table 4 ego ablation |
| Camera model cited as OccWorld | variant leakage | bind O/D/T/S |
| Pixel FD replaced by occupancy | parallel-head hypothesis | both metrics, not substitution |
| Local eval claimed | license gate | nuScenes/Occ3D records |

## Cosmos3-Nano connection

Occupancy dynamics are a candidate **parallel** geometric transition beside Generator FD/WAM, not a pixel replacement. Nano does not document OccWorld-O GT occupancy inputs. Any attachment must name a new head and a licensed dataset; it must not inherit Table 1 as a video score. [OCCSRC-PAPER; C3-TR]

## Sources

- [OCCSRC-PAPER], [OCCSRC-CODE-CURRENT], and [OCCSRC-NUSCENES] identify occupancy/ego transitions, Table 4, code stubs, and the license gate.
