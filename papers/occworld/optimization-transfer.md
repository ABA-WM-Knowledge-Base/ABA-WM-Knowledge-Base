---
id: world-model-kb.papers.occworld.optimization-transfer
title: OccWorld Transferable Optimization Knowledge
kind: guide
status: maintained
last_updated: 2026-08-14
owners:
  - AIBuildAI world-model group
---

# OccWorld Transferable Optimization Knowledge

## Retrieval metadata

**Relevant queries:** transfer OccWorld to Cosmos3, auxiliary occupancy head, tokenizer recon vs forecast, spatial temporal attention, ego-temporal pose, OccWorld-O vs S, collision occupancy, or parallel geometric stream.

**Knowledge provided:** falsifiable intervention patterns derived from OccWorld, their attachment as a geometric head **parallel to** Cosmos3-Nano Generator FD/WAM (not pixel replacement), required controls, expected evidence, and invalid generalizations.

**Related pages:** [`paper.md`](paper.md) owns OccWorld evidence; [`codebase.md`](codebase.md) owns implementation; [3D and 4D world models](../../foundations/representations/3d-and-4d-world-model.md); [video world models](../../foundations/representations/video-world-model.md); [Cosmos3-Nano generator](../../models/cosmos3-nano/generator.md); [action modeling](../../models/cosmos3-nano/action-modeling.md); [optimization playbook](../../models/cosmos3-nano/optimization-playbook.md).

## 1. Transfer discipline

OccWorld forecasts **metric occupancy tokens** and **ego waypoints**. Cosmos3-Nano Generator forecasts **continuous video latents** with an appearance prior. Transfers test a **parallel geometric head** or a dual stream — not deletion of Wan VAE pixels.

OccWorld-O uses **occupancy GT**. It is not an unsupervised or label-free method. OccWorld-S (camera, none) scores mIoU **0.26** and is a negative control, not a drop-in WM. [OCCSRC-PAPER, Tables 1-2]

Every item below is a **hypothesis** until a controlled target-model experiment separates it from data, compute, tokenizer size, and evaluator protocol (STP3 vs VAD/dagger).

## 2. Intervention matrix

| ID | Target failure | Mechanism transferred | Attachment surface | Primary evidence | Principal risk |
|---|---|---|---|---|---|
| `OCCW-XFER-01` | video FD lacks metric free space | auxiliary occupancy head | Generator tokens → BEV/occ, **parallel** | OccWorld-O mIoU 17.14 vs Copy&Paste 11.33 | head unused |
| `OCCW-XFER-02` | appearance OK, layout wrong | dual occupancy + video streams | geometry tokenizer + FD/WAM | O vs S: 17.14 vs 0.26 mIoU | compute without planning gain |
| `OCCW-XFER-03` | ego motion decoupled from scene | joint tokens + waypoints | FD/WAM + pose head | Table 4 w/o ego temporal L2 5.89 | ego prior overfit |
| `OCCW-XFER-04` | 3 s occupancy collapse | AR geometric tokens beside flow video | short AR on VQ-BEV | 1 s 25.78 vs 3 s 10.51 | AR no better than flow |
| `OCCW-XFER-05` | instance/HD-map addiction | occupancy-only planning features | ablate map raster; keep occ GT if present | OccWorld-O L2 1.17 vs UniAD 1.03 | calling O “unlabeled” |
| `OCCW-XFER-06` | pixel loss misses collisions | collision from decoded occupancy | occ head → collision loss | O col 0.60 vs UniAD 0.31; 3 s 1.35 | loss ignored |
| `OCCW-XFER-07` | recon-tuned VQ hurts forecast | (50²,128,512) not max recon | VQ on BEV before temporal model | Table 3: recon 78.12 → forecast 12.38 | codebook 1024 overfit |
| `OCCW-XFER-08` | missing spatial occupancy structure | spatial attention on token map | occ head spatial blocks | Table 4 w/o spatial 10.07 | video attn already enough |
| `OCCW-XFER-09` | missing temporal occupancy structure | temporal occupancy attention | occ head time blocks | Table 4 w/o temporal 8.98 | hurts short-horizon RGB |
| `OCCW-XFER-10` | camera-only treated as occupancy WM | keep named variants; S as floor | data contract, not architecture | S mIoU 0.26 IoU 5.00; L2 1.83 col 2.02 | silent O/S mix |

## 3. `OCCW-XFER-01`: auxiliary occupancy head parallel to Generator

**Source mechanism.** OccWorld’s primary representation is 3D semantic occupancy. OccWorld-O reaches average mIoU **17.14** / IoU **26.63** at **18 FPS**, versus Copy&Paste **11.33 / 20.52**. [OCCSRC-PAPER, Table 1]

**Target behavior.** Cosmos3 video FD/WAM looks plausible but misplaces free space and occupied volume.

**Attachment.** A lightweight BEV/occupancy head on Generator intermediate tokens. RGB latents stay on the frozen video codec. **Do not** replace FD/WAM pixel decode with voxels.

**Minimum controlled experiment.** FD/WAM with vs without the occupancy auxiliary on a driving adapter. Measure BEV mIoU, collision, and action sensitivity. Hold video FID/FVD as a regression suite.

**Expected movement.** Higher occupancy IoU and lower collision at matched video quality.

**Falsification.** Reject if the aux loss drops with no occupancy or collision movement, or if video metrics collapse enough to erase FD/WAM utility.

## 4. `OCCW-XFER-02`: dual geometric and appearance streams

**Source mechanism.** OccWorld-O (occupancy GT) vs OccWorld-S (camera, none): mIoU **17.14** vs **0.26**. Camera appearance without occupancy tokens does not yield a geometric WM. [OCCSRC-PAPER, Table 1]

**Hypothesis.** Video latents and occupancy tokens are complementary. Fusing them should beat either stream on layout-sensitive planning.

**Attachment.** Two encoders into the Generator temporal stack: Wan VAE appearance plus an occupancy/depth preprocessor. Fusion is concat or gated add, not voxel-for-pixel substitution.

**Experiment.** Video-only vs occupancy-only vs dual-stream on joint FD/WAM + occupancy metrics.

**Expected movement.** Dual-stream wins occupancy and collision; video-only wins FID; occupancy-only looks unlike RGB.

**Falsification.** Reject if dual-stream adds compute without occupancy or WAM improvement, or if the occupancy stream is ignored (gradient ~0).

## 5. `OCCW-XFER-03`: joint occupancy and ego trajectory

**Source mechanism.** Pose tokens run through the same transformer as occupancy. Without ego-temporal modeling, planning L2 is **5.89** and collision **6.23** versus OccWorld-O **1.17 / 0.60**. [OCCSRC-PAPER, Table 4 vs Table 2]

**Hypothesis.** Predicting waypoints from the same latent that forecasts occupancy couples “where the scene goes” and “where the ego goes.”

**Attachment.** FD/WAM (or a parallel occ head) emits an action/ego chunk **and** future geometric tokens. Weight the plan regression analogously to `PlanRegLossLidar` 0.1.

**Experiment.** Joint vs sequential (forecast then plan) vs occupancy-only. Use STP3 L2/collision, not a mixed VAD/dagger table.

**Expected movement.** Joint training reduces L2 and collision versus occupancy-only; sequential may match L2 but miss collisions.

**Falsification.** Reject if joint training destabilizes FD/WAM, or if trajectory gains are only an ego-speed prior (ablate scene tokens).

## 6. `OCCW-XFER-04`: autoregressive geometry for the 3 s tail

**Source mechanism.** OccWorld-O mIoU **25.78** at 1 s vs **10.51** at 3 s (average 17.14). Copy&Paste average is 11.33 — the 3 s tail is near the floor. [OCCSRC-PAPER, Table 1]

**Hypothesis.** A cheap AR occupancy token model can carry layout beyond the horizon where video flow blurs, if trained on generated prefixes.

**Attachment.** Short AR on VQ-BEV tokens **beside** flow/video FD, used for horizons >2 s. Video remains the appearance path.

**Experiment.** Match 1/2/3 s; compare occupancy mIoU and planning L2 vs video-only FD/WAM.

**Expected movement.** 3 s occupancy and collision improve; 1 s video quality stays flat.

**Falsification.** Reject if AR geometry never beats flow on 3 s at matched compute, or if AR improves 3 s mIoU while collision worsens (layout not used).

## 7. `OCCW-XFER-05`: occupancy-only planning features (not “no labels”)

**Source mechanism.** OccWorld-O plans without instance/HD-map aux, L2 avg **1.17** vs UniAD **1.03**, collision **0.60** vs **0.31**, FPS **18**. OccWorld-O still uses **3D-Occ GT**. [OCCSRC-PAPER, Table 2]

**Hypothesis.** For map-free deployment, occupancy self-supervision can replace HD-map rasters **if occupancy GT or a strong teacher exists**. Removing maps without occupancy is OccWorld-S, which fails.

**Attachment.** Ablate map condition channels in a driving FD adapter; add occupancy GT or a frozen OccWorld-O teacher. Log the supervision honestly.

**Experiment.** Map vs map-free+occ vs map-free camera-only (S analog).

**Expected movement.** Map-free+occ approaches map L2 with a collision gap similar to 0.60 vs 0.31.

**Falsification.** Reject if map-free+occ matches S (occupancy unused), or if the write-up calls OccWorld-O unlabeled.

## 8. `OCCW-XFER-06`: collision-aware losses from occupancy

**Source mechanism.** Occupancy supports explicit collision checks. OccWorld-O collision is **0.07 / 0.38 / 1.35** at 1/2/3 s (avg 0.60), worse than UniAD 0.31. [OCCSRC-PAPER, Table 2]

**Hypothesis.** A differentiable or sampled collision term on predicted occupancy can close part of the UniAD gap without instance tracks.

**Attachment.** Decode the parallel occ head to BEV occupancy; penalize ego-footprint overlap. Keep pixel/FD losses unchanged.

**Experiment.** With vs without collision loss; report STP3 collision and L2, plus video regression.

**Expected movement.** Lower 2–3 s collision; possible conservative (higher L2) trajectories.

**Falsification.** Reject if collision rate is unchanged or the loss is ignored, or if the ego simply stops (L2 explodes).

## 9. `OCCW-XFER-07`: do not maximize tokenizer reconstruction

**Source mechanism.** Tokenizer **(100², 128, 512)** reaches recon mIoU **78.12** but forecast average **12.38**, worse than default **(50², 128, 512)** forecast **17.14**. Codebook **1024** overfits. [OCCSRC-PAPER, Table 3]

**Hypothesis.** Fine spatial tokens memorize low-level occupancy noise and become unpredictable. Forecast CE, not recon mIoU, should select codebook size and downsample.

**Attachment.** VQ on lifted BEV patches before the temporal model. Sweep spatial size `{25², 50², 100²}` and `n_e in {256,512,1024}`.

**Experiment.** Plot recon mIoU vs forecast mIoU vs planning L2. Predeclare forecast as the selection criterion.

**Expected movement.** Mid-size 50² / 512 wins forecast; 100² and 1024 win recon only.

**Falsification.** Reject if larger recon always helps forecast on the Cosmos adapter (domain shift), but still do not select VQ on recon alone without reporting forecast.

## 10. `OCCW-XFER-08`: spatial occupancy attention

**Source mechanism.** Without spatial attention, forecast mIoU is **10.07** versus **17.14**. [OCCSRC-PAPER, Table 4]

**Hypothesis.** Occupancy tokens need within-frame spatial mixing to keep object blobs coherent. Video spatial attn on RGB latents does not automatically provide metric blob coherence.

**Attachment.** Spatial self-attention (or conv U-blocks as in PlanU) on the occ-head token map.

**Experiment.** Occ head with vs without spatial attn at matched parameters.

**Expected movement.** Forecast mIoU moves toward the 17 vs 10 gap; small objects improve more than road class.

**Falsification.** Reject if spatial attn is a no-op once the Generator already attends spatially to the same BEV, or if it helps recon but not forecast (Table 3 trap).

## 11. `OCCW-XFER-09`: temporal occupancy attention

**Source mechanism.** Without temporal attention, forecast mIoU is **8.98** — worse than the spatial-off 10.07. [OCCSRC-PAPER, Table 4]

**Hypothesis.** Layout dynamics (vehicles entering/leaving) live in temporal occupancy mixing. Copy&Paste (11.33 mIoU) already encodes “nothing moves”; beating it requires time.

**Attachment.** Temporal attention or a small AR block on occ tokens across 2 s history.

**Experiment.** Temporal on/off; report 1 s vs 3 s mIoU separately.

**Expected movement.** 3 s mIoU improves more than 1 s; Copy&Paste gap widens.

**Falsification.** Reject if temporal attn only helps 1 s (memorizing input) or if it degrades video FD/WAM short-horizon quality without occupancy gain.

## 12. `OCCW-XFER-10`: named-variant data contracts

**Source mechanism.** OccWorld-S camera-only: mIoU **0.26**, IoU **5.00**, planning L2 **1.83**, collision **2.02**. OccWorld-D/T sit between S and O and must stay named. [OCCSRC-PAPER, Tables 1-2]

**Hypothesis.** Most “OccWorld failed on Cosmos” reports will be S-like (RGB only) scored against O tables. The transfer is a **data contract**: occupancy GT or a teacher, not a transformer trick.

**Attachment.** Registry fields: observation type `{occ-GT, camera+occ, camera+sem-lidar, camera}`. Refuse to compare an S-like run to Table 1’s OccWorld-O row.

**Experiment.** Four observation arms on the same backbone. Predeclare O-row vs S-row acceptance.

**Expected movement.** O-like data recovers geometric metrics; S-like stays near Copy&Paste or below.

**Falsification.** Reject any paper that quotes 17.14 mIoU for a camera-only Cosmos run. If camera-only somehow matches O, the occupancy labels were leaked.

## 13. Interaction map

- Parallel occ head (`01`) is the attachment for dual stream (`02`), collision (`06`), and spatial/temporal (`08`,`09`).
- Joint ego (`03`) needs temporal occupancy (`09`) and fails without pose tokens (Table 4).
- Long-horizon AR (`04`) should be selected with Table 3 discipline (`07`), not recon IoU.
- Map-free (`05`) is invalid without an occupancy contract (`10`).
- Generator FD/WAM video quality is a **regression suite** on every geometric transfer.

This KB does not schedule experiments.

## 14. Invalid generalizations

- Do not replace Generator pixels with occupancy voxels and call it OccWorld transfer.
- Do not merge OccWorld-O with D/T/S or with UniAD aux-label scores.
- Do not call OccWorld-O unlabeled or unsupervised.
- Do not mix STP3 Table 2 with dagger/VAD 0.64 / 0.24.
- Do not tune VQ on reconstruction after Table 3.
- Do not skip nuScenes license when copying the data pipeline.
- Do not treat occupancy WM as a Reasoner language planner.

## 15. Transfer record template

```text
Transfer ID:
Source mechanism and exact evidence (named variant required):
Target failure signature:
Target-model attachment point (parallel occ head / FD/WAM, not pixel replacement):
Observation contract {occ-GT, camera+occ, camera+sem-lidar, camera}:
Required data/evaluator changes:
Baseline and matched controls:
Trainable parameters and initialization:
Compute and inference-budget change:
Primary and regression metrics:
Expected movement and mechanism probe:
Confounders and interaction risks:
Minimum experiment:
Falsification result:
Observed artifact or run record:
```

## Sources

- [OCCSRC-PAPER] OccWorld mechanisms, named variants, and tables.
- [OCCSRC-CODE-CURRENT] implementation surfaces.
- [REP-OCCWORLD-2024] Foundation identity.
