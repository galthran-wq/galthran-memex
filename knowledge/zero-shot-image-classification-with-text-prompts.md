---
title: "Zero-Shot Image Classification with Text Prompts"
type: concept
summary: "An open-vocabulary classification method that scores an image against natural-language descriptions of candidate labels using a shared image-text embedding space."
tags: [ml, vision, multimodal]
created: "2026-02-09"
edges:
  - path: /knowledge/clip.md
    label: source
    description: "CLIP popularized prompt-based zero-shot image classification as a standard interface."
  - path: /knowledge/contrastive-image-text-pretraining.md
    label: requires
    description: "The method relies on a model trained to align image and text embeddings."
  - path: /knowledge/prompt-ensembling.md
    label: uses
    description: "Ensembling multiple prompts per class can substantially improve accuracy."
sources:
  - url: "https://arxiv.org/abs/2103.00020"
    title: "Learning Transferable Visual Models From Natural Language Supervision"
---

## Definition

Zero-shot image classification with text prompts predicts labels without training a task-specific classifier by converting each candidate label into a natural-language prompt, embedding prompts and images into a shared space, and choosing the label whose prompt embedding is most similar to the image embedding.

## How It Works

Given candidate labels $\{c_k\}_{k=1}^K$:

1. **Prompt labels**: define a prompt template (for example, “a photo of a {label}”) and render a text string for each label.
2. **Embed text**: compute normalized text embeddings $\hat t_k$ for each prompted label.
3. **Embed image**: compute a normalized image embedding $\hat v$ for the input image.
4. **Score and select**: compute similarities (often scaled by a learned temperature) and pick the best label:

$$
s_k = \tau \cdot \hat v^\top \hat t_k,\quad \hat y = \arg\max_k s_k.
$$

Intuitively, the text embeddings $\hat t_k$ behave like the weight vectors of a linear classifier in the shared embedding space.

## Connections

- Models trained with [contrastive image-text pretraining](/knowledge/contrastive-image-text-pretraining.md) make this interface possible.
- [Prompt ensembling](/knowledge/prompt-ensembling.md) reduces sensitivity to prompt wording.
