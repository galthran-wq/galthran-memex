---
title: "Prompt Ensembling (for CLIP-Style Zero-Shot)"
type: concept
summary: "A technique that improves zero-shot accuracy by averaging predictions across multiple prompt templates (or multiple phrasings) per class."
tags: [ml, vision, multimodal]
created: "2026-02-09"
edges:
  - path: /knowledge/zero-shot-image-classification-with-text-prompts.md
    label: about
    description: "Prompt ensembling is a practical enhancement to prompt-based zero-shot classification."
  - path: /knowledge/clip.md
    label: source
    description: "CLIP reports sizeable gains from prompting and ensembling multiple prompts."
sources:
  - url: "https://arxiv.org/abs/2103.00020"
    title: "Learning Transferable Visual Models From Natural Language Supervision"
---

## Definition

Prompt ensembling reduces sensitivity to the exact wording of a label prompt by combining scores from multiple prompt templates or multiple phrasings for the same class.

## How It Works

For each class $c_k$, create $M$ prompts $\{p_{k,m}\}_{m=1}^M$ and compute text embeddings $\hat t_{k,m}$. Given an image embedding $\hat v$, compute per-prompt scores

$$
s_{k,m} = \tau \cdot \hat v^\top \hat t_{k,m}.
$$

Common aggregation choices:

- **Average logits**: $s_k = \frac{1}{M}\sum_m s_{k,m}$
- **Average text embeddings then score**: $\bar t_k = \mathrm{normalize}\!\left(\frac{1}{M}\sum_m \hat t_{k,m}\right)$, then $s_k = \tau \cdot \hat v^\top \bar t_k$

## Connections

- Used as a simple, effective upgrade to [zero-shot image classification with text prompts](/knowledge/zero-shot-image-classification-with-text-prompts.md), especially for [CLIP](/knowledge/clip.md).
