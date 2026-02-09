---
title: "CLIP"
type: reference
summary: "A contrastive image-text pretraining method (Radford et al., 2021) that learns a shared embedding space for images and natural-language descriptions, enabling strong zero-shot transfer via prompting."
tags: [ml, vision, multimodal, paper]
created: "2026-02-09"
edges:
  - path: /knowledge/contrastive-image-text-pretraining.md
    label: about
    description: "CLIP is a prominent instance of contrastive pretraining on paired image-text data."
  - path: /knowledge/infonce-contrastive-objective.md
    label: uses
    description: "CLIP trains with a symmetric in-batch contrastive objective (InfoNCE-style)."
  - path: /knowledge/zero-shot-image-classification-with-text-prompts.md
    label: about
    description: "CLIP’s shared embeddings make prompt-based zero-shot classification a standard inference interface."
  - path: /knowledge/prompt-ensembling.md
    label: uses
    description: "CLIP accuracy is sensitive to prompt choice; ensembling prompts boosts performance."
  - path: /knowledge/clip-robustness-under-natural-distribution-shift.md
    label: about
    description: "The paper reports reduced robustness gaps on natural distribution shifts for zero-shot CLIP."
  - path: /knowledge/clip-scaling-behavior.md
    label: about
    description: "CLIP exhibits smooth scaling behavior of average zero-shot error vs compute."
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

## Relevance

CLIP popularized large-scale contrastive image-text pretraining and made prompt-based, open-vocabulary classification a standard interface for vision models. Its encoders (or CLIP-like variants) are commonly used as backbones for retrieval, ranking, and as visual components in multimodal systems.
