---
id: world-model-kb.papers.cosmos-policy.optimization-transfer
title: Cosmos Policy Transferable Optimization Knowledge
kind: guide
status: maintained
last_updated: 2026-08-14
owners:
  - AIBuildAI world-model group
---

# Cosmos Policy Transferable Optimization Knowledge

## Retrieval metadata

**Relevant queries:** transfer Cosmos Policy, latent frame injection, auxiliary future value, dual policy planning checkpoints, best-of-N video policy, sigma_min, hybrid EDM noise, Predict2 post-training, or Cosmos3-Nano Policy-DROID.

**Knowledge provided:** ten falsifiable intervention patterns, Cosmos3-Nano attachment points, required controls, expected metric movement, and invalid generalizations.

**Related pages:** [`paper.md`](paper.md) owns evidence; [`codebase.md`](codebase.md) owns code surfaces; [Cosmos3-Nano policy](../../models/cosmos3-nano/policy.md) and [action modeling](../../models/cosmos3-nano/action-modeling.md) own target surfaces; [optimization playbook](../../models/cosmos3-nano/optimization-playbook.md) owns experiment discipline.

## 1. Transfer discipline

Every item below is a **hypothesis**. Cosmos Policy post-trains Predict2-2B, not Cosmos3-Nano. Policy-DROID is a different checkpoint and protocol. Do not copy LIBERO 98.5% onto Nano.

Evidence strengths in the paper:

1. **direct architecture/objective ablations:** Tables 4-5 (auxiliary losses, scratch init, peel-down to `p(a|s)`, one-step sampling);
2. **coupled planning evidence:** dual checkpoints, 648 rollouts, Figure 7 `V(s')` versus `Q(s,a)`;
3. **protocol-bound leaderboard cells:** Tables 1-3.

Do not assign Table 1 causal credit to planning, or Table 5 credit to latent tiling alone.

## 2. Intervention matrix

| ID | Target failure | Mechanism transferred | Attachment surface | Primary evidence | Principal risk |
|---|---|---|---|---|---|
| `POLICY-XFER-01` | separate action head discards video priors | latent frame injection of actions | Generator latent sequence, not Reasoner | Sec. 4.1; Table 4 scratch drop | Cosmos3 VAE layout incompatibility |
| `POLICY-XFER-02` | policy ignores extra cameras | extra-view latent frames | Nano multi-view image tokens | Sec. 4.1, 11-frame example | viewpoint identity leakage |
| `POLICY-XFER-03` | proprioception dropped | tiled proprio latent | action adapter / WAM prefix | Sec. 4.1 tiling to `[-1,+1]` | scale mismatch across embodiments |
| `POLICY-XFER-04` | future prediction unused at test | auxiliary `s', V` targets | joint FD/WAM objective | Table 4 -1.5; Table 5 62.5->44.4 | extra capacity without causal gain |
| `POLICY-XFER-05` | planner overfits successes | mix failed rollouts into WM/value | data sampler | Sec. 4.2 10-20% LIBERO failures; 648 ALOHA rollouts | unsafe or off-policy coverage |
| `POLICY-XFER-06` | search uses stale value | dual policy vs planning checkpoints | Policy-DROID + ranking head | Sec. 4.3 dual deployment | two-checkpoint ops cost |
| `POLICY-XFER-07` | larger N does not help | best-of-N with majority-mean values | inference search | Fig. 7; 4.9 s N=8 | compute magnifies misspecification |
| `POLICY-XFER-08` | Predict2.5 recipe used as paper evidence | pin initialization family | training config | Cookbook vs `NVlabs/cosmos-policy` | version conflation |
| `POLICY-XFER-09` | value is Q vs V without ablation | mask prefix for `V(s')` vs `Q(s,a)` | value latent condition | Fig. 7, Fig. 12 | wrong backup for search |
| `POLICY-XFER-10` | JPEG/flip or `sigma_min` hidden | match LIBERO image and EDM contract | dataloader + `cosmos_sampler` | Appendix A.2.1, A.3; `flip_images` | eval-only tricks |

## 3. `POLICY-XFER-01`: latent frame injection

**Source mechanism.** Actions are encoded as latent frames and denoised with the pretrained DiT, with no new action network. Scratch initialization drops LIBERO average from 98.5 to 94.6 and Long from 97.6 to 88.6. [P25-COSMOS-POLICY, Sec. 4.1, Table 4]

**Target behavior.** Keep video-model spatiotemporal priors while emitting robot action chunks.

**Attachment.** On Cosmos3-Nano, the Generator diffusion subsequence is the candidate surface. Reasoner text tokens are the wrong surface. [`codebase.md`](codebase.md) analog is `policy_video2world_model.py` plus tiled non-image latents.

**Minimum controlled experiment.** Compare (a) frozen video backbone plus new action head, (b) latent-frame injection at matched parameter count, (c) shuffled action-latent alignment. Hold data, sampler, and eval protocol fixed.

**Expected movement.** Higher task success and larger true-versus-shuffled action sensitivity without collapsing video quality.

**Falsification.** Reject if matched-parameter action heads match or beat injection on task success, or if shuffled alignment is equal.

## 4. `POLICY-XFER-02`: extra-view latent frames

**Source mechanism.** Additional cameras are inserted as image latent frames rather than a fused backbone crop. [P25-COSMOS-POLICY, Sec. 4.1, Fig. 2]

**Attachment.** Nano multi-view image tokens on the Generator, with explicit camera-index embeddings.

**Minimum experiment.** One-view versus multi-view at matched resolution and parameter count; permute camera identity.

**Falsification.** Reject if extra views do not improve contact or occlusion-heavy tasks, or if shuffled camera IDs match the aligned layout.

## 5. `POLICY-XFER-03`: tiled proprioception

**Source mechanism.** Proprioception is duplicated into a full `H' x W' x 16` volume after `[-1,+1]` rescaling, not encoded by the Wan VAE. [P25-COSMOS-POLICY, Sec. 4.1]

**Attachment.** WAM/action-adapter prefix on Cosmos3, with per-embodiment scale tables.

**Minimum experiment.** No-proprio, raw-units proprio, and tiled normalized proprio at matched steps.

**Falsification.** Reject if proprio tiling matches a tiny MLP fused into AdaLN, or if transferring scale stats across robots preserves success.

## 6. `POLICY-XFER-04`: auxiliary futures and values

**Source mechanism.** Training `p(a,s',V|s)` rather than `p(a|s)` improves control. LIBERO -1.5 average without auxiliaries; RoboCasa collapses from 62.5 to 44.4 when future-state targets are removed from the policy. [P25-COSMOS-POLICY, Tables 4-5]

**Attachment.** Joint FD/WAM objective on Generator tokens, not a separate video loss on Reasoner.

**Minimum experiment.** Action-only, joint-train/action-only-infer, and joint-train/joint-infer at matched steps.

**Expected movement.** Direct-policy success rises even when futures are discarded at test time.

**Falsification.** Reject if action-only matches joint training on success and contact metrics.

## 7. `POLICY-XFER-05`: failed rollouts in the world-model set

**Source mechanism.** Policy training filters unsuccessful demos; world-model/value training keeps them. Planning further needs on-policy failures (648 ALOHA rollouts). [P25-COSMOS-POLICY, Sec. 4.2-4.3, 5.3]

**Attachment.** Data sampler that can mark success/failure without changing the visual codec.

**Minimum experiment.** Success-only WM versus mixed WM at matched volume; freeze the proposal policy.

**Falsification.** Reject if mixed failures do not improve hard-task ranking or if they degrade the proposal policy when mixed into the 10% policy slice.

## 8. `POLICY-XFER-06`: dual policy and planning checkpoints

**Source mechanism.** Rollout fine-tuning uses 90% WM/value and 10% policy; dual deployment keeps the original policy for proposals. [P25-COSMOS-POLICY, Sec. 4.3]

**Attachment.** A frozen Policy-DROID or WAM proposal checkpoint plus a separately updated ranking head or planning checkpoint.

**Minimum experiment.** Single-checkpoint search versus dual deployment at matched N and data.

**Falsification.** Reject if the refined checkpoint is a better proposer and a better ranker, or if dual deployment matches using the base checkpoint for both roles.

## 9. `POLICY-XFER-07`: best-of-N with majority mean

**Source mechanism.** N proposals, 3 futures, 5 values, majority-mean aggregation, full-chunk execution. `N=8` costs 4.9 s on 8 H100s and is reported to help two hard ALOHA tasks by 12.5 points under a harder initial-state slice. [P25-COSMOS-POLICY, Fig. 7, Appendix A.4.2]

**Attachment.** Inference search around Generator FD rollouts, not Reasoner text plans.

**Minimum experiment.** N in {1,2,4,8} crossed with naive mean versus majority mean; hold dual checkpoints fixed.

**Falsification.** Reject if N>1 with the unrefined value model matches dual deployment, if majority-mean equals naive mean, or if extra N only increases latency.

## 10. `POLICY-XFER-08`: pin the initialization family

**Source mechanism.** Paper identity is Predict2-2B via `NVlabs/cosmos-policy`. Cookbook Predict2.5 is a later path. [CPOL-COOKBOOK; P25-COSMOS-POLICY]

**Attachment.** Training config and checkpoint loader.

**Minimum experiment.** Train the same recipe from Predict2-2B versus Predict2.5-2B versus Nano Generator; report as three identities.

**Falsification.** Reject any claim that Cookbook success is Table 1 evidence.

## 11. `POLICY-XFER-09`: `V(s')` versus `Q(s,a)`

**Source mechanism.** Input masks on the value latent choose state value versus state-action value. Figure 7 reports model-based `V(s')` over `Q(s,a)` on limited rollouts. [P25-COSMOS-POLICY, Fig. 7, 12]

**Attachment.** Value-frame conditioning mask in the diffusion sequence.

**Minimum experiment.** Same rollout pool, same N; swap only the value mask.

**Falsification.** Reject if Q-search matches or beats V-search at equal data, or if V-search gains vanish without the world-model ensemble.

## 12. `POLICY-XFER-10`: image and EDM contracts

**Source mechanism.** LIBERO `flip_images`, JPEG augmentation, hybrid noise, and `sigma_min=4` are part of the published inference contract. [P25-COSMOS-POLICY, Appendix A.2.1; CPOL-CODE]

**Attachment.** Dataloader flags and `cosmos_sampler.py`.

**Minimum experiment.** Ablate flip/JPEG/`sigma_min` one at a time on a frozen checkpoint.

**Falsification.** Reject if default EDM `sigma_min=0.002` matches Table 1, or if flip/JPEG changes only FID-like metrics while success is flat.

## 13. Invalid transfers

- Treating Cookbook Predict2.5 success as paper evidence.
- Treating Policy-DROID as Cosmos Policy without a new entry.
- Treating value latents as physically calibrated rewards.
- Treating 93.6 ALOHA average as OOD superiority (Table 3 OOD: pi0.5 92.5 vs Cosmos Policy 89.3).
- Treating one-step 66.4% RoboCasa as a substitute for the 5-step 67.1% table identity.

## Sources

[P25-COSMOS-POLICY; CPOL-CODE; CPOL-COOKBOOK]
