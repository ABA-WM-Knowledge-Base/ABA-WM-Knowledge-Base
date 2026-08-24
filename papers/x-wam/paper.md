---
id: world-model-kb.papers.x-wam.paper
title: X-WAM Method, Architecture, and Experimental Evidence
kind: paper
status: maintained
last_updated: 2026-08-24
owners:
  - AIBuildAI world-model group
---

# X-WAM Method, Architecture, and Experimental Evidence

## Retrieval metadata

**Relevant queries:** X-WAM architecture, unified sequence, multi-view RGB-D, action token, proprioception, depth adaptation, unilateral attention, ANS distribution, asynchronous denoising, flow matching loss, pretraining mixture, RoboCasa result, reconstruction metric, ablation, or real-robot latency.

**Knowledge provided:** a complete end-to-end reconstruction of the paper's model and learning system, protocol-bound quantitative results, ablations, compute, and evidence limits.

**Related pages:** [Codebase](codebase.md) maps each mechanism to the release; [X-WAM Model architecture](../../models/x-wam/architecture.md) owns concrete checkpoint behavior; [Original RoboCasa protocols](../../benchmarks/robocasa/protocol-and-metrics.md) owns benchmark semantics.

## 1. Problem and output contract

X-WAM addresses the mismatch between policy models, which output actions but do not explicitly simulate future geometry, and visual world models, which synthesize observations but do not directly control a robot. Given language instruction `c`, current multi-view RGB observation `O_0`, and current proprioceptive state `s_0`, it jointly predicts future RGB video `O_1:H`, future depth `D_1:H`, future states `s_1:H`, and a denser action sequence `a_1:K`. The paper fixes `H=8` future frames/states and `K=32` actions; one conditioning frame gives nine total video frames. [XWAM-PAPER-V2, pp.4-5, Figure 2]

The four objectives are coupled but distinct:

1. high-fidelity RGB future generation;
2. depth prediction and multi-view 3D reconstruction;
3. closed-loop action success;
4. action availability before full video denoising completes.

An improvement in one output is not evidence for all four. Task success, RGB metrics, depth metrics, point-cloud consistency, and latency remain separate evaluation axes.

## 2. End-to-end system

```text
conditions
  language c --------------------------> UMT5 text context
  multi-view RGB O_0 -> Wan causal VAE -> fixed clean RGB latent
  current state s_0 -> state MLP ------> fixed clean state token

prediction variables initialized/noised
  future RGB O_1:H -> VAE latents z_O
  future states s_1:H -> state MLP latents z_s
  actions a_1:K -> action MLP latents z_a

unified sequence [z_O0, z_O1:H, z_s0, z_s1:H, z_a1:K]
  + temporal/spatial RoPE
  + learned camera-view embeddings
  + separate video and state/action noise timesteps
                  |
       Wan2.2-TI2V-5B DiT shared blocks
                  |
        final M blocks split into
          main RGB/state/action branch
          depth branch reading main-branch KV
                  |
  RGB velocity -> VAE decode -> multi-view RGB future
  state velocity -> state MLP decode -> future end-effector state
  action velocity -> action MLP decode -> action chunk
  inverse depth -> VAE decode -> depth future
                  |
  static camera poses + predicted end-effector pose and hand-eye transform
                  -> fused time-varying point clouds
```

The backbone is initialized from Wan2.2-TI2V-5B. RGB is encoded by the original causal VAE; state and action vectors use learnable MLP encoders and decoders. All three main modalities share bidirectional full attention after concatenation. The initial RGB and state remain clean (`t=0`) during denoising, while future variables are generated. [XWAM-PAPER-V2, pp.4-6, Equations 1-6]

## 3. Temporal and geometric representation

Actions run at four times the video/state sampling rate: `K/H=4`. The model uses the base video's temporal RoPE for video, state, and action tokens so positional proximity can express alignment across modalities. Learnable view embeddings distinguish cameras while preserving the pretrained single-view spatial and temporal RoPE. [XWAM-PAPER-V2, p.5]

For a dual-arm interface, each state is 16-dimensional: `(position_3 + quaternion_4 + gripper_1) × 2`. Each action is 14-dimensional: `(delta-position_3 + delta-axis-angle_3 + gripper-action_1) × 2`. Single-arm data supervises only the first arm and masks the second. Per-dataset 1st/99th quantiles normalize heterogeneous embodiments; action ranges are chosen symmetrically so zero remains the no-motion value. [XWAM-PAPER-V2, pp.16-17]

X-WAM does not directly predict arbitrary camera extrinsics. Static camera poses are calibration constants. For a wrist camera, it predicts end-effector transform `T_ee` and derives camera pose using fixed hand-eye calibration `T_h2e`:

```text
T_wrist = T_ee · T_h2e
```

Depth and pose then lift all views into a common frame. Chamfer Distance therefore entangles depth quality, multi-view consistency, static extrinsic calibration, and predicted wrist pose. It is not a pure per-pixel depth metric. [XWAM-PAPER-V2, p.5, Equation 2]

## 4. Lightweight depth adaptation

Depth is represented in the RGB VAE space: one inverse-depth channel is replicated into pseudo-RGB, encoded and decoded through the same VAE. Instead of appending depth tokens—which doubles sequence length and raises attention cost—or concatenating depth channels—which shifts the base model input distribution—the architecture copies the final `M` of `N` DiT blocks into a depth branch. The released configuration uses `N=32`, `M=10`. [XWAM-PAPER-V2, pp.5-6; XWAM-CODE-72CF, `modules/wan_model.py`]

After `N-M` shared blocks produce hidden state `H`, main and depth streams start from the same state. At each copied layer, the depth block can read the main branch's same-layer input through cross-attention, while the main branch cannot read depth. This unilateral connection preserves the main pretrained computation path and permits the depth branch to be disabled during action-only policy inference. The depth head regresses inverse depth with mean-squared error. [XWAM-PAPER-V2, p.6, Equation 3; p.16, Algorithm 1]

The design assumes useful depth is inferable from RGB features. It does not guarantee metric depth under unseen camera or geometry distributions, and the main branch can benefit from depth supervision only through shared blocks and joint parameter updates, not direct depth-to-main attention in the copied layers.

## 5. Asynchronous Noise Sampling

Video needs more denoising than low-dimensional actions. Independent video/action timestep sampling wastes training probability on states that asynchronous inference never visits—for example, a cleaner video paired with noisier action (`t_O < t_a`). ANS couples training timesteps to the intended inference region. [XWAM-PAPER-V2, pp.6, 16-17, Algorithm 2]

With probability `p`, actions are clean and video timestep is uniform:

```text
t_a = 0, t_O ~ Uniform(0,1)
```

Otherwise:

```text
t_a ~ Uniform(0,1)
b ~ Beta(1.5,1)
t_O = t_a + (1 - t_a) b
```

Thus `t_O >= t_a`. The released/paper configuration sets `p=0.5`. This mixture trains both action-conditioned video continuation and joint asynchronous denoising.

At inference, separate UniPC schedulers use `T_a < T_O`. Action and state become clean after `T_a` model calls and can be dispatched. Video can continue for `T_O-T_a` calls conditioned on the now-clean action/state. The final experiments use 10 action steps and 50 video steps. Policy serving sets `early_stop=True`, exits after action denoising, disables the depth branch, and never decodes a video. Full world generation uses all 50 steps and can return RGB-D. [XWAM-PAPER-V2, pp.6, 17; XWAM-CODE-72CF, `runners/xwam_runner.py`]

## 6. Learning objective and pretraining

For modality `m` in video, state, and action, X-WAM uses flow matching with interpolation `z_t=(1-t)z_0+t epsilon` and predicts velocity `epsilon-z_0`. Its loss is:

```text
L_total = L_video + lambda_s L_state + lambda_a L_action + lambda_D L_depth
```

The paper uses all weights equal to `1.0`. State timestep equals action timestep. In the action-clean branch of ANS, action/state loss is masked because those variables are conditions rather than noisy prediction targets. [XWAM-PAPER-V2, p.6, Equations 5-6; XWAM-CODE-72CF, `runners/xwam_runner.py::training_step`]

Pretraining contains 1,492,026 episodes and 5,873.9 hours: [XWAM-PAPER-V2, p.16, Table 5]

| Dataset | Domain | Episodes | Hours |
|---|---|---:|---:|
| AgibotWorld-Beta | real | 866,562 | 2,221.5 |
| DROID | real | 74,734 | 280.3 |
| InternA1-Aloha | simulation | 184,803 | 1,337.3 |
| InternA1-Genie1 | simulation | 50,638 | 174.0 |
| InternA1-Lift2 | simulation | 231,018 | 1,464.7 |
| RoboCasa MimicGen | simulation | 56,771 | 282.4 |
| RoboTwin 2.0 | simulation | 27,500 | 113.7 |

Episodes with base locomotion, dexterous manipulation, or failed execution are removed; stationary DROID frames are also filtered. Video is downsampled to 3.75 fps and resized to 320×256. Because most sources lack depth, Video Depth Anything supplies pseudo-depth. This pretraining distribution excludes behavior the paper's universal interface cannot represent, so “cross-embodiment” is bounded by end-effector pose/action compatibility.

The paper reports 256 H20 GPUs, 40,000 steps, peak learning rate `1e-4`, 1,000-step warmup, cosine decay, and global batch 2,048. Benchmark fine-tuning is reported as 32 H20 GPUs, 20,000 steps, learning rate `3e-5`, and batch 128. Released configs differ in several values; [Codebase](codebase.md) preserves that conflict. [XWAM-PAPER-V2, pp.16-17]

## 7. Policy evaluation

### 7.1 RoboCasa

X-WAM reports mean success over 24 Original RoboCasa manipulation tasks, 100 episodes per task. [XWAM-PAPER-V2, pp.7-8, 17, Tables 1 and 6]

| Method | Family | Average success |
|---|---|---:|
| pi-zero | VLA | 62.5% |
| GR00T-N1.5 | VLA | 64.1% |
| UWM | WAM | 60.8% |
| DreamZero with Wan2.2-5B replacement | WAM | 62.4% |
| Cosmos Policy | WAM | 67.1% |
| X-WAM | WAM | 79.2% |

Per-task X-WAM success ranges from 35% on `TurnOffStove` and 45% on `CoffeeSetupMug` to 100% on `CloseDrawer`. The spread preserves diagnostic information hidden by 79.2%. [XWAM-PAPER-V2, pp.18-19, Table 6]

### 7.2 RoboTwin 2.0

On 50 dual-arm tasks, X-WAM reports 89.8% Clean and 90.7% Randomized, versus 88.7%/87.0% for the strongest listed prior method, Motus. Training uses all AgileX trajectories described as 50 clean and 500 randomized trajectories on each task. Randomized success exceeding Clean is possible because the training composition includes substantially more randomized trajectories; it should not be interpreted as randomized environments being intrinsically easier. [XWAM-PAPER-V2, pp.7-8, Table 2]

## 8. 4D reconstruction and generation

RoboCasa predicted observations are compared with simulator ground truth. PSNR, SSIM, and LPIPS measure RGB; AbsRel and delta-1 measure per-view depth; Chamfer Distance measures fused point clouds. Pixel metrics use only two static cameras because small predicted wrist-pose errors misalign pixels in the dynamic camera. [XWAM-PAPER-V2, p.8]

| Method | PSNR up | SSIM up | LPIPS down | AbsRel down | delta-1 up | CD down |
|---|---:|---:|---:|---:|---:|---:|
| DreamZero + Depth Anything 3 | 21.12 | 0.7788 | 0.1580 | 0.1362 | 0.8594 | 0.0680 |
| Robot4DGen | 22.67 | 0.8207 | 0.1026 | 0.0736 | 0.9443 | 0.0134 |
| X-WAM without depth + DA3 | 23.09 | 0.8916 | 0.0548 | 0.1045 | 0.9089 | 0.0401 |
| X-WAM | 23.46 | 0.8942 | 0.0513 | 0.0349 | 0.9738 | 0.0049 |

[XWAM-PAPER-V2, p.8, Table 3]

This table favors joint depth modeling, but comparisons include different generation pipelines and do not match policy success or compute. It establishes metric performance under the paper's reconstruction protocol, not general 3D physical correctness.

## 9. Controlled ablations

All Table 4 variants are fine-tuned directly from Wan2.2-TI2V-5B on benchmark data without large-scale X-WAM pretraining. They share data, hyperparameters, and schedule within the ablation. [XWAM-PAPER-V2, p.9]

Depth architecture findings:

- No depth: 63.0% success, 1,033 ms.
- Sequence concatenation: 68.7%, 1,888 ms; best reported reconstruction metrics but expanded sequence.
- Channel concatenation: 64.2%, 1,266 ms.
- Interleaved branch: 67.8%, 1,033 ms, with strong depth/point-cloud metrics.

ANS findings:

- Synchronous training/inference: 66.4%, 4,665 ms, strongest RGB metrics in that block.
- Decoupled training/synchronous inference: 66.3%, 4,665 ms.
- Independently decoupled training/asynchronous inference: 67.2%, 1,033 ms, degraded reconstruction.
- ANS training/asynchronous inference: 67.8%, 1,033 ms, repairing depth quality and slightly raising success.

The ablation uses 25 synchronous steps versus five asynchronous action steps on RTX 3090; final released configs use 10 action/50 video steps. The `67.8 → 79.2` gap includes large-scale pretraining and possibly released-config differences, so Table 4 does not allocate the final model gain among depth, ANS, and data scale.

## 10. Real-robot experiment

X-WAM is fine-tuned on about 20 hours of demonstrations for a four-stage dual-arm earphone-packing task. Three cameras run at 320×256. Training uses 64 H20 GPUs for 40,000 steps. On RTX 5090 D, eight denoising steps take about 300 ms per action chunk; Real-Time Chunking overlaps inference and execution at 15 Hz with 15 actions per chunk and a six-action delay. [XWAM-PAPER-V2, pp.18-21]

Across six trials per condition, X-WAM improves average progress over Xiaomi-Robotics-0 on packing two earphones (`93.8 vs 79.1`), novel placements (`70.8 vs 58.3`), and distractors (`75.0 vs 66.7`), while matching unseen tablecloth (`66.7`). Six trials make estimates coarse, and progress credits completed stages rather than only full episode success. The experiment supports deployment feasibility under one task and platform, not general real-time or long-horizon reliability.

## 11. Limits and decision consequences

The paper names two limits: fixed-length context without history or autoregressive rollout, and higher latency than dedicated policies. The former can confuse task stage; the latter makes actions stale despite Real-Time Chunking. [XWAM-PAPER-V2, p.21]

Additional evidence boundaries follow from the design:

- 4D output is reconstructed from RGB-D and pose, not a persistent native 3D state.
- Pseudo-depth pretraining can inherit Video Depth Anything biases.
- Filtering removes locomotion and dexterity, narrowing the universal action interface.
- Final policy performance is not decomposed against an equal-compute pretrained no-depth/no-ANS baseline.
- Baseline data and implementations are only broadly, not exactly, matched.
- Action-only early stop bypasses the depth branch at inference; any policy benefit from depth must be encoded during training in shared parameters.
- The released artifacts and paper training values conflict; a reproduction must select and label one identity.

These constraints turn the paper into testable design knowledge: depth supervision, timestep-distribution alignment, and asynchronous action decoding are mechanisms with measurable benefits and trade-offs, not unconditional recipes.

## Sources

All paper claims use `XWAM-PAPER-V2`; implementation-qualified statements use `XWAM-CODE-72CF`. Both resolve through [`sources.yaml`](sources.yaml).
