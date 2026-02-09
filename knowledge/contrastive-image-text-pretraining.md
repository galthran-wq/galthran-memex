---
title: "Contrastive Image-Text Pretraining"
type: concept
summary: "A pretraining approach that aligns image and text representations by contrasting matched image-text pairs against mismatched pairs, producing shared embeddings useful for retrieval and zero-shot classification."
tags: [ml, vision, multimodal]
created: "2026-02-09"
edges:
  - path: /knowledge/clip.md
    label: example_of
    description: "CLIP is a canonical system trained with contrastive image-text pretraining."
  - path: /knowledge/infonce-contrastive-objective.md
    label: uses
    description: "A common training recipe is an InfoNCE-style in-batch contrastive objective."
  - path: /knowledge/zero-shot-image-classification-with-text-prompts.md
    label: uses
    description: "A shared embedding space enables prompt-based zero-shot classification."
sources:
  - url: "https://arxiv.org/abs/2103.00020"
    title: "Learning Transferable Visual Models From Natural Language Supervision"
---

## Definition

Contrastive image-text pretraining learns an embedding space where images and their corresponding text descriptions are close, and non-matching image-text pairs are far apart. The resulting representations are typically used for cross-modal retrieval and open-vocabulary (prompt-based) classification.

## How It Works

- **Two encoders**: an image encoder produces an image embedding $v$, and a text encoder produces a text embedding $t$.
- **Shared space**: both embeddings are projected into the same dimension and L2-normalized.
- **Batch-wise contrasting**: for a batch of aligned pairs, the model assigns high similarity to the correct match and low similarity to all other in-batch negatives (often with a learned temperature).

## Connections

- [CLIP](/knowledge/clip.md) is a widely used instance of this approach.
- Training is often expressed via an [InfoNCE-style contrastive objective](/knowledge/infonce-contrastive-objective.md).
- The shared space supports [zero-shot classification via text prompts](/knowledge/zero-shot-image-classification-with-text-prompts.md).
