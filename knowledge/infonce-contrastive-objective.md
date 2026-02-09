---
title: "InfoNCE Contrastive Objective (In-Batch Softmax)"
type: concept
summary: "A contrastive learning loss that treats each example’s matched pair as the correct class among in-batch negatives via a softmax, commonly used to align image and text embeddings."
tags: [ml, contrastive-learning, multimodal]
created: "2026-02-09"
edges:
  - path: /knowledge/contrastive-image-text-pretraining.md
    label: about
    description: "InfoNCE is a common objective used in contrastive image-text pretraining."
  - path: /knowledge/clip.md
    label: source
    description: "CLIP popularized a symmetric image-to-text and text-to-image InfoNCE-style training objective at scale."
sources:
  - url: "https://arxiv.org/abs/2103.00020"
    title: "Learning Transferable Visual Models From Natural Language Supervision"
---

## Definition

InfoNCE is a contrastive objective that encourages a representation of an input to assign high probability to its matched paired representation among a set of candidates (often using in-batch examples as negatives). It can be viewed as a multiclass classification problem implemented with a softmax over similarity scores.

## How It Works

Given a batch of $N$ aligned image-text pairs $(v_i, t_i)$ with normalized embeddings $\hat v_i, \hat t_i$, define logits

$$
\ell_{i,j} = \tau \cdot \hat v_i^\top \hat t_j
$$

where $\tau$ is a learned temperature (equivalently, the inverse of a softmax temperature).

An image-to-text loss treats the correct match $t_i$ as the target class among $N$ text candidates:

$$
L_{v\rightarrow t} = \frac{1}{N}\sum_{i=1}^N -\log \frac{\exp(\ell_{i,i})}{\sum_{j=1}^N \exp(\ell_{i,j})}.
$$

CLIP uses a symmetric objective that also includes the text-to-image direction:

$$
L = \frac{1}{2}\left(L_{v\rightarrow t} + L_{t\rightarrow v}\right).
$$

## Connections

- This objective is a core component of [contrastive image-text pretraining](/knowledge/contrastive-image-text-pretraining.md).
- In [CLIP](/knowledge/clip.md), in-batch negatives make training compute-efficient compared to autoregressive captioning, focusing capacity on cross-modal alignment.
