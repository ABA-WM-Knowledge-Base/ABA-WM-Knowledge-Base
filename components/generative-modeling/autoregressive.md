---
id: world-model-kb.components.generative-modeling.autoregressive
title: Autoregressive and Recurrent Generative Modeling
kind: component
status: maintained
last_updated: 2026-09-09
owners:
  - AIBuildAI world-model group
---

# Autoregressive and Recurrent Generative Modeling

## Retrieval metadata

**Relevant queries:** autoregressive world model, recurrent video prediction, MDN-RNN, causal token generation, video tokenizer, teacher forcing, exposure bias, iVideoGPT.

**Knowledge provided:** Causal and recurrent factorizations for future prediction, continuous-latent versus discrete-token implementations, their optimization and inference properties, and their world-model evidence.

**Related pages:** [Autoregressive modeling](../../foundations/learning-objectives/autoregressive-modeling.md) owns the general likelihood factorization; [latent world models](../../foundations/representations/latent-world-model.md) owns codec choices; [iVideoGPT](../../papers/ivideogpt/README.md) owns system-specific evidence. [Causal and Streaming Generation](../fast-video-inference/causal-streaming.md) owns temporal factorization, history-state validity, incremental delivery, and interaction latency.

## Method definition

Autoregressive modeling factorizes a conditional sequence distribution:

\[
p_\theta(x_{1:N}\mid c)=\prod_{i=1}^{N}p_\theta(x_i\mid x_{<i},c).
\]

For a world model, tokens may represent frames, compressed video codes, actions, rewards, or states. A recurrent continuous-latent model implements a related temporal factorization through a hidden state and a next-latent distribution:

\[
p_\theta(z_{t+1}\mid z_t,a_t,h_t).
\]

The causal factorization gives a normalized local objective and a clear history interface. It does not guarantee that the token order reflects physical causality or that generated states remain valid under long rollout.

## Recurrent latent prediction

World Models compressed images with a VAE and used an MDN-RNN to predict the distribution of the next latent from current latent, action, and hidden state. The mixture density represented multiple next-latent modes, while the recurrent state carried predictive history. [FND-WORLD-MODELS-2018, Secs. 2–4]

This design reduced the spatial generation burden and let the controller train inside a virtual environment. Its main generative lesson is that stochastic recurrent prediction can express uncertainty with far less output dimension than pixel generation. Its main failure lesson is exposure: an optimized controller visited model weaknesses, creating a large virtual–real gap at low sampling temperature. [FND-WORLD-MODELS-2018, Tables 1–2]

## Discrete autoregressive video tokens

iVideoGPT combines a compressive conditional VQ tokenizer with a causal Transformer. The tokenizer maps context and future video into discrete codes; the Transformer predicts future codes and can incorporate optional actions, goals, or rewards. It pretrains on heterogeneous action-free video and then adapts named checkpoints for downstream conditional tasks. [IVG-PAPER, Secs. 3–4]

On BAIR, the paper reports action-free FVD 75.0 and action-conditioned FVD 60.8 for its named variants and protocols. This supports the value of the action signal in that dataset, not a universal superiority of the autoregressive family. The work also reports visual-planning and model-based RL applications, with exact task and checkpoint boundaries preserved in its [Paper page](../../papers/ivideogpt/paper.md). [IVG-PAPER, Tables 1–2 and Sec. 4]

Action-free Open-X pretraining does not create a unified Open-X action-conditioned model because constituent datasets use heterogeneous action spaces. Downstream action-conditioned checkpoints remain task-specific.

## Training and inference mechanics

### Teacher forcing

Maximum likelihood trains each conditional on the ground-truth prefix. This makes optimization stable and parallel across positions during training, but inference consumes sampled prefixes. The resulting exposure gap grows with rollout length.

### Tokenization

Discrete codes reduce spatial and temporal sequence length, but introduce quantization and reconstruction error. Tokenizer rate, codebook size, temporal compression, and conditioning architecture determine whether small motion or contact survives.

### Ordering

Frame-major, spatial, modality, and action-token order determine which variables can condition which others. A causal order that places action after its predicted effect cannot support the intended intervention without a special attention mask.

### Sampling

Temperature, top-k, top-p, and deterministic decoding change diversity and error propagation. Comparison requires fixed sample count and decoding budget.

### Cache and serial cost

Key–value caching reduces repeated Transformer computation, but generation remains sequential over sampled tokens. Higher compression reduces token latency at the risk of lost dynamics detail.

## Design surfaces

| Surface | Expected effect | World-model risk | Required measurement |
|---|---|---|---|
| Spatial/temporal compression | shorter sequence and lower compute | contact or identity loss | codec state probes and rollout error |
| Codebook capacity | more representational detail | sparse or unstable usage | rate–distortion and code utilization |
| Context length | longer memory | compute and irrelevant history | horizon-conditioned consistency |
| Token order/attention | changes condition availability | temporal leakage or delayed action | counterfactual action test |
| Scheduled or corrupted prefixes | reduces clean-prefix dependence | training instability | open-loop versus teacher-forced gap |
| Sampling temperature | controls diversity | implausible or collapsed futures | coverage–fidelity calibration |
| Action/reward token weighting | increases intervention/task sensitivity | broad-video regression | action effect and downstream utility |

## Evaluation

Report teacher-forced likelihood and open-loop rollout separately. For video, include perceptual metrics, state/event metrics, identity consistency, and horizon. For action-conditioned use, swap candidate actions under identical context and measure whether predicted effects change correctly. For planning, measure candidate-ranking regret and realized success at a fixed generation budget.

An autoregressive model can achieve good likelihood by predicting common continuations while ignoring rare but decision-critical events. Event-stratified evaluation is therefore necessary.

## Cosmos3-Nano connection

Cosmos3-Nano Reasoner uses autoregressive language modeling, while Generator models continuous media/action outputs with rectified flow rather than categorical video-code prediction. Temporal factorization and within-block sampling are different axes: rectified flow can model each conditional of a block-autoregressive generator. The pinned Framework exposes temporal-causal configuration and per-frame Diffusion Forcing training; those hooks do not prove that a particular Nano checkpoint supports a ready-to-use streaming path. See [causal and streaming generation](../fast-video-inference/causal-streaming.md) for the source-level evidence and transfer boundaries. [C3-TR, pp. 8–13; C3-FW, cosmos_framework/model/generator/omni_mot_model.py]

The cross-method interface is developed in [omnimodal generation](omnimodal-generation.md) and [comparison and optimization](comparison-and-optimization.md).

## Sources

- [FND-WORLD-MODELS-2018] identifies the recurrent latent system.
- [IVG-PAPER] identifies iVideoGPT and its exact autoregressive tokenizer, checkpoint, and experiment surface.
