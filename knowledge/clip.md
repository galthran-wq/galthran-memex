---
title: "CLIP"
type: reference
summary: "A contrastive image-text pretraining method (Radford et al., 2021) that learns a shared embedding space for images and natural-language descriptions, enabling strong zero-shot transfer via prompting."
tags: [ml, vision, multimodal, paper]
created: "2026-02-09"
updated: "2026-02-09"
edges:
  - path: /knowledge/contrastive-image-text-pretraining.md
    label: about
    description: "CLIP is a prominent instance of contrastive pretraining on paired image-text data."
  - path: /knowledge/infonce-contrastive-objective.md
    label: uses
    description: "CLIP trains with a symmetric in-batch contrastive objective (InfoNCE-style)."
sources:
  - url: "https://arxiv.org/abs/2103.00020"
    title: "Learning Transferable Visual Models From Natural Language Supervision"
  - url: "https://github.com/openai/CLIP"
    title: "openai/CLIP"
---

## Summary

CLIP trains an image encoder and a text encoder jointly on a large set of (image, text) pairs, pushing matching pairs together and mismatched pairs apart in a shared embedding space. At inference time, it can classify an image into arbitrary user-provided categories by embedding natural-language label prompts (for example, “a photo of a {label}”) and choosing the label whose text embedding is most similar to the image embedding.

![CLIP overview diagram](/knowledge/assets/figure_1.png)

## Key Takeaways

- CLIP reframes classification as matching images to natural-language descriptions, avoiding a fixed label set during training.
- The training objective is an efficient in-batch contrastive loss over all image-text pairs in a batch (symmetric cross-entropy).
- Zero-shot accuracy depends meaningfully on prompt wording; prompt ensembling can improve results.
- Zero-shot CLIP can reduce the gap between ImageNet performance and performance under natural distribution shifts (relative to standard supervised baselines), while fine-tuning on ImageNet can trade off robustness for in-distribution accuracy.

## How Zero-Shot Classification Works

To classify an image into a set of classes, CLIP turns each label into one or more natural-language prompts (for example, “a photo of a {label}”). The text encoder embeds each prompt; these prompt embeddings behave like class weight vectors in the shared embedding space. The image encoder embeds the input image, and the predicted class is the prompt (or class) with highest cosine similarity to the image embedding.

### Prompting and prompt ensembling

Prompt choice matters. A simple way to reduce prompt sensitivity is to use multiple prompts per class and combine them:

- **Average logits**: compute a similarity score for each prompt and average the scores for prompts that correspond to the same class.
- **Average embeddings**: average the text embeddings for a class’s prompts, re-normalize, and score with the image embedding.

## Robustness Under Natural Distribution Shift

Radford et al. report that zero-shot CLIP tends to retain accuracy better under several natural distribution shifts (for example, sketches and renditions), reducing the usual gap between ImageNet and shifted ImageNet variants compared to standard supervised baselines. They also note that adapting/fine-tuning to ImageNet can increase ImageNet accuracy without necessarily improving average robustness across their shift suite.

![Robustness under natural distribution shift](/knowledge/assets/figure_13.png)

## Scaling Behavior

Across training runs at different compute/model scales, average zero-shot error follows a smooth log-log linear trend (scaling-law-like behavior). The paper extrapolates that very large additional compute would be required for zero-shot performance to reach the best overall results across their evaluation suite.

## Relevance

CLIP popularized large-scale contrastive image-text pretraining and made prompt-based, open-vocabulary classification a standard interface for vision models. Its encoders (or CLIP-like variants) are commonly used as backbones for retrieval, ranking, and as visual components in multimodal systems.
