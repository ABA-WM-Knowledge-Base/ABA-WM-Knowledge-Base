---
id: world-model-kb.foundations.learning-objectives.autoregressive-modeling
title: Autoregressive Modeling
kind: concept
status: maintained
last_updated: 2026-08-14
owners:
  - AIBuildAI world-model group
---

# Autoregressive Modeling

## Retrieval metadata

**Relevant queries:** autoregressive world model, next-token prediction, visual token prediction, teacher forcing, exposure bias, scheduled sampling, video tokenizer, or multimodal sequence model.

**Knowledge provided:** the autoregressive factorization, serialization and tokenizer design choices, optimization trade-offs, and tests for likelihood, rollout, conditioning, and downstream utility.

**Related pages:** [Video world models](../representations/video-world-model.md) covers observation rollouts; [latent world models](../representations/latent-world-model.md) covers learned tokens and states; [diffusion and flow matching](diffusion-and-flow-matching.md) covers non-autoregressive generative objectives.

## Definition and formalism

An autoregressive model factorizes a joint conditional distribution according to an ordering:

```text
p_theta(x[1:N] | c) = product_i p_theta(x_i | x[<i], c),
L_AR = -sum_i log p_theta(x_i | x[<i], c).
```

For language, `x_i` is usually a subword token. For images, video, state, or action, it can be a raw value, discretized bin, learned codebook index, patch token, or modality-specific block. The ordering is part of the model: raster order, time-major order, interleaved action-observation order, and hierarchical coarse-to-fine order express different conditional independences and expose different serial bottlenecks.

Teacher forcing evaluates each conditional on ground-truth prefixes. Generation conditions on sampled prefixes, so early errors change all later input distributions. Scheduled sampling was proposed to address this discrepancy, but its objective and consistency differ from maximum likelihood; it is a design option rather than a universal correction. [OBJ-SCHEDULED-SAMPLING-2015]

## Assumptions and scope

Any finite joint distribution admits an autoregressive factorization, but a chosen architecture and context window may not model it efficiently. Exact likelihood under the serialization is a major advantage when tokens are discrete. Likelihood over learned codes is not likelihood over the original physical observations unless tokenizer probabilities and reconstruction are accounted for.

An autoregressive sequence can mix text, images, video, actions, rewards, or states. Shared token space does not guarantee shared semantics or causal coupling. Next-token competence also does not imply autonomous simulation: deployment must define how generated state becomes subsequent context and how actions enter the sequence.

## Representation and mechanism families

| Family | Unit and ordering | Strength | Main limitation |
|---|---|---|---|
| Raw-pixel autoregression | channel/subpixel in raster order | direct density model | extremely long sequences |
| Discrete visual-token model | VQ codes over space and time | scalable transformer interface | tokenizer distortion and codebook limits |
| Temporal block model | frames or latent blocks over time | parallelism within block | conditional independence inside block |
| Hierarchical model | coarse-to-fine space/time tokens | long-range structure plus detail | cross-level error and complex training |
| Interleaved multimodal model | text, action, and visual tokens | flexible joint conditionals | ordering and token-count imbalance |
| Recurrent latent dynamics | one latent state per step | compact rollouts | state bottleneck and drift |

PixelRNN demonstrated tractable autoregressive image density modeling. VQ-VAE supplied discrete learned codes that made high-dimensional media more sequence-like. TECO, VideoPoet, and Genie illustrate different uses of tokenized or autoregressive components for long video and interactive environments. [OBJ-PIXELRNN-2016; REP-VQVAE-2017; REP-TECO-2023; OBJ-VIDEOPOET-2024; WFM-GENIE-2024]

## Design implications and trade-offs

Tokenizer rate and distortion are coupled to model difficulty: more tokens preserve detail but increase sequence length and sampling latency. The codebook should be tested for task information, not only visual reconstruction. Temporal stride determines whether fast contacts and actions are observable. Serialization can place action before consequence to expose a forward conditional, or consequence before action to expose an inverse one; the two are not interchangeable.

Context length, causal attention pattern, positional encoding, modality loss weights, token masking, and sampling temperature affect rollout. Teacher-forced likelihood is statistically well-defined, while multi-step or scheduled objectives may better resemble deployment at the cost of altered optimization behavior. Parallel decoding, token blocks, caching, and distillation improve latency but can weaken dependencies the original factorization represented.

## Evaluation and falsification

- Report token negative log-likelihood or perplexity together with tokenizer reconstruction and semantic/task probes.
- Evaluate free-running rollouts separately from teacher-forced prediction and stratify by horizon.
- Hold conditioning fixed and perturb actions or goals to test whether output distributions respond appropriately.
- Compare quality, diversity, task utility, and wall-clock cost at matched sample budgets.
- Inspect error propagation by substituting a controlled wrong token at different positions.
- Evaluate rare events and small control-relevant details that contribute few tokens to the average loss.

A world-model claim is weakened when the serialization uses future or privileged tokens unavailable during rollout, when generated tokens cannot be decoded into the stated state/action interface, or when likelihood gains arise entirely from nuisance appearance. An action-coupling claim is falsified if counterfactual action tokens do not change the corresponding future distribution.

## Failure modes

- **Exposure bias:** sampled prefixes diverge from the teacher-forced training distribution.
- **Compounding error:** local token mistakes alter long-range state and identity.
- **Tokenizer erasure:** quantization drops contacts, small objects, text, or precise motion.
- **Serial latency:** token-by-token generation cannot meet control or simulation rate.
- **Ordering shortcut:** the sequence exposes labels or contemporaneous outcomes that trivialize prediction.
- **Modality imbalance:** high-count visual or text tokens dominate sparse action and reward tokens.
- **Likelihood-task mismatch:** frequent detail improves average NLL while decision-critical rare events regress.
- **Sampling sensitivity:** apparent capability depends on temperature, truncation, or best-of-N selection.

## Cross-part instantiations

- [Cosmos3-Nano Reasoner](../../models/cosmos3-nano/reasoner.md) uses an autoregressive language-output surface conditioned on multimodal context.
- [Cosmos3-Nano Generator](../../models/cosmos3-nano/generator.md) owns its media/action generation objective; it should not be classified as autoregressive output generation when the documented surface uses rectified flow.
- [Modalities and I/O](../../models/cosmos3-nano/modalities-and-io.md) defines token/modal ordering and conditioning contracts where exposed.
- [Training](../../models/cosmos3-nano/training.md) and [evaluation](../../models/cosmos3-nano/evaluation.md) own checkpoint-specific losses and metrics rather than inheriting generic autoregressive assumptions.
- [iVideoGPT](../../papers/ivideogpt/paper.md) instantiates compressive VQ plus GPT-style multimodal next-token prediction; RLVR-World is a later separate paper.
- [OccWorld](../../papers/occworld/paper.md) instantiates GPT-style occupancy-token forecasting plus ego-trajectory prediction.
- [DreamerV3](../../papers/dreamerv3/paper.md) uses recurrent latent dynamics rather than pixel-token autoregression; do not recast it as a VideoGPT.
- [Paper entries](../../papers/README.md) preserve implementation-specific tokenizers and sequence layouts.

## Sources

- [OBJ-BENGIO-LM-2003] Bengio et al., *A Neural Probabilistic Language Model*, Journal of Machine Learning Research 3, 2003.
- [OBJ-PIXELRNN-2016] van den Oord, Kalchbrenner, and Kavukcuoglu, *Pixel Recurrent Neural Networks*, ICML 2016, PMLR 48.
- [OBJ-SCHEDULED-SAMPLING-2015] Bengio et al., *Scheduled Sampling for Sequence Prediction with Recurrent Neural Networks*, NeurIPS 2015.
- [REP-VQVAE-2017] van den Oord, Vinyals, and Kavukcuoglu, *Neural Discrete Representation Learning*, NeurIPS 2017, arXiv:1711.00937.
- [REP-TECO-2023] Yan et al., *Temporally Consistent Transformers for Video Generation*, ICML 2023, PMLR 202.
- [WFM-GENIE-2024] Bruce et al., *Genie: Generative Interactive Environments*, ICML 2024, arXiv:2402.15391.
- [OBJ-VIDEOPOET-2024] Kondratyuk et al., *VideoPoet: A Large Language Model for Zero-Shot Video Generation*, ICML 2024, PMLR 235.
- [C3-TR] NVIDIA, *Cosmos 3: Omnimodal World Models for Physical AI*, arXiv:2606.02800.
