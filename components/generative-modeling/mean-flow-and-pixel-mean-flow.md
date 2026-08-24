---
id: world-model-kb.components.generative-modeling.mean-flow-and-pixel-mean-flow
title: Mean Flow and Pixel Mean Flow
kind: component
status: maintained
last_updated: 2026-08-24
owners:
  - AIBuildAI world-model group
---

# Mean Flow and Pixel Mean Flow

## Retrieval metadata

**Relevant queries:** MeanFlow, improved MeanFlow, iMF, pixel MeanFlow, pMF, average velocity, one-step flow, fastforward generation, x-prediction, latent-free flow, Jacobian-vector product, classifier-free guidance.

**Knowledge provided:** The transition from instantaneous-velocity Flow Matching to average-velocity prediction, the stability and guidance changes in Improved MeanFlow, the pixel-space output design of Pixel MeanFlow, and falsifiable transfer hypotheses for video and action-conditioned flow models.

**Related pages:** [Flow matching and rectified flow](flow-matching-and-rectified-flow.md) owns the broader transport family; [Diffusion and flow matching](../../foundations/learning-objectives/diffusion-and-flow-matching.md) owns model-independent objectives; [latent diffusion and DiT](latent-diffusion-and-dit.md) owns latent-space representation trade-offs.

## Why MeanFlow changes the one-step problem

Standard Flow Matching trains an instantaneous velocity: the tangent of a trajectory at one time. Generation then approximates an integral with an ordinary differential equation solver. MeanFlow instead learns the average velocity over a time interval. The prediction is a displacement divided by interval length, so one network evaluation can represent a long segment of the trajectory.

The distinction matters because a straight conditional path does not guarantee a straight marginal path. Different data and noise pairs can cross at the same intermediate state; the marginal velocity can therefore curve even when each conditional path is linear. A coarse solver step then incurs integration error. MeanFlow moves the long-interval integration burden into training rather than pretending that a single instantaneous tangent is a complete endpoint map. [COMP-MF-2025, Secs. 3–4]

The paper derives an identity linking average velocity, instantaneous velocity, and the total derivative of average velocity. This identity supplies a training target without numerically integrating the trajectory. The total derivative includes the state derivative and the explicit time derivative, which can be evaluated with a Jacobian-vector product. The training loss stops gradients through the derived target, avoiding higher-order backpropagation through that Jacobian-vector product. [COMP-MF-2025, Sec. 4]

```latex
\[
z_t=a_t x+b_t\epsilon,\qquad
v_t=\frac{d z_t}{d t},\qquad
u(z_t,r,t)=\frac{1}{t-r}\int_r^t v(z_\tau,\tau)\,d\tau,
\]
\[
u(z_t,r,t)=v(z_t,t)-(t-r)\frac{d}{d t}u(z_t,r,t),
\qquad
\frac{d}{d t}u=v\,\partial_z u+\partial_t u,
\]
\[
u_{\mathrm{tgt}}=v_t-(t-r)\left(v_t\partial_z u_\theta+\partial_t u_\theta\right),
\qquad
\mathcal{L}=\mathbb{E}\left\|u_\theta-\operatorname{stopgrad}(u_{\mathrm{tgt}})\right\|_2^2.
\]
```

MeanFlow is trained from scratch and does not require distillation, pre-training, or a curriculum. On ImageNet at 256 by 256 resolution, the paper reports a Fréchet Inception Distance of 3.43 with one function evaluation. This is an image-generation result under the paper's model, data, and evaluation protocol; it is not evidence of one-step physical video prediction or action validity. [COMP-MF-2025, Abstract; Sec. 5]

## Improved MeanFlow

Improved MeanFlow addresses two concrete weaknesses in the original formulation.

First, the original effective target contains derivatives of the current network. That target is mathematically grounded but network-dependent in finite optimization, which can make training less stable. Improved MeanFlow re-parameterizes the problem as a more standard regression loss on the instantaneous velocity while retaining a network that predicts average velocity. The change targets optimization stability, not a new sampler family. [COMP-IMF-2025, Abstract; Secs. 3–4]

Second, original MeanFlow fixes the classifier-free guidance scale during training. Improved MeanFlow exposes guidance information as an explicit condition, allowing the scale to vary at inference. In-context conditioning represents the condition variants without requiring a separate large parameter stream for every guidance setting. This improves deployment flexibility, but guidance scale remains an inference control that must be evaluated for adherence, diversity, and trajectory distortion. [COMP-IMF-2025, Abstract; Sec. 4]

The revised method reports a Fréchet Inception Distance of 1.72 with one function evaluation on ImageNet at 256 by 256 resolution, trained from scratch without distillation. The official implementation reports small reproduction differences between its own evaluation and the paper, so the exact metric must stay bound to the named checkpoint, implementation, and evaluation stack. [COMP-IMF-2025, Abstract; IMF-CODE]

## Pixel MeanFlow

Pixel MeanFlow separates network output space from loss space. The network predicts a clean image in pixel space, which is treated as lying near a lower-dimensional image manifold. The loss still uses the MeanFlow relation in velocity space. This design avoids forcing a pixel-space network to regress a high-variance velocity target directly and removes the external autoencoder bottleneck used by latent models.

The method is therefore not “ordinary MeanFlow at higher resolution.” It changes the representation surface, output parameterization, and reconstruction path simultaneously. Pixel-space detail can improve fidelity, while the absence of a latent codec increases memory and compute pressure. The paper reports ImageNet results of 2.22 Fréchet Inception Distance at 256 by 256 and 2.48 at 512 by 512, both with one-step latent-free generation. [COMP-PMF-2026, Abstract; Sec. 5]

The official implementation exposes pMF model families at 256 by 256 and 512 by 512, with the reported results depending on the released configuration and TPU evaluation setup. The repository also provides PyTorch and high-sharding branches, but those branches are implementation artifacts, not interchangeable evidence surfaces. [PMF-CODE]

## Decision guidance for a flow world model

MeanFlow-family ideas are candidates for changing inference budget, not automatic replacements for a video model's objective. A world model must preserve temporal consistency, action response, and uncertainty across a rollout. An image Fréchet Inception Distance improvement can coexist with worse event timing or action-conditioned state error.

| Candidate intervention | Mechanism | Attach point | Required evidence | Stop condition |
|---|---|---|---|---|
| Average-velocity head | Predicts an interval transport quantity suited to long steps | Flow generator output and time-condition interface | Same checkpoint evaluated at matched function evaluations; temporal error by interval length | One-step quality rises while multi-frame event timing or action response falls |
| Improved target parameterization | Removes network-dependent target sensitivity from the main regression surface | Training loss and Jacobian-vector product path | Loss variance, gradient norm, stability, and held-out rollout metrics | Stability improves without any rollout or endpoint gain, or derivative cost dominates |
| Explicit guidance condition | Allows guidance scale to vary at test time | Condition embedding and sampler configuration | Adherence, diversity, physical consistency, and latency across guidance scales | Higher guidance increases condition score but damages dynamics or diversity |
| Pixel-space prediction | Preserves detail without latent codec reconstruction loss | Decoder/output head and memory budget | Pixel detail, temporal consistency, memory, throughput, and action sensitivity | Detail gain is smaller than memory or temporal-regression cost |

Optimization hypothesis: if a target video flow model's main failure is solver error over curved marginal paths, average-velocity prediction may reduce the number of function evaluations needed for a fixed endpoint error. Test this with the same backbone, data, condition tokens, resolution, duration, and compute budget. Do not infer success from visual sharpness alone.

For action-conditioned video, add action-conditioned state error, action sensitivity, contact or event timing, and closed-loop task metrics. For multimodal outputs, report per-modality degradation; a shared average-velocity objective can privilege the modality with larger token count or loss scale. Pixel MeanFlow's latent-free result does not establish that raw-pixel video is preferable to a latent representation when temporal length and control conditioning dominate memory.

## Limits and non-transfer claims

- One function evaluation means one network evaluation under the paper's sampling protocol; it does not mean zero integration error for an arbitrary target model.
- MeanFlow, Improved MeanFlow, and Pixel MeanFlow are primarily image-generation evidence. Their reported Fréchet Inception Distance values do not measure physical validity, action causality, or long-horizon rollout calibration.
- Pixel-space output changes the codec and memory surface. It should not be transferred to a video model without a resolution, duration, memory, and bandwidth analysis.
- Improved guidance flexibility does not prove that arbitrary guidance scales preserve world-model dynamics.
- A successful image-generation implementation is not a reproduction of a world-action model. Transfer remains a hypothesis until controlled rollout and decision metrics improve.

## Sources

- [COMP-MF-2025] identifies Mean Flows for One-step Generative Modeling.
- [COMP-IMF-2025] identifies Improved Mean Flows, version 2.
- [COMP-PMF-2026] identifies One-step Latent-free Image Generation with Pixel Mean Flows, version 3.
- [IMF-CODE] and [PMF-CODE] identify the official implementations and their reported evaluation surfaces.
