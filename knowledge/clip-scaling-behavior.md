---
title: "CLIP Scaling Behavior (Zero-Shot Error vs Compute)"
type: insight
summary: "Across CLIP model and compute scales, average zero-shot error follows a smooth log-log linear trend, suggesting scaling-law-like behavior and large compute requirements to reach top overall zero-shot performance."
tags: [ml, vision, multimodal, scaling]
created: "2026-02-09"
edges:
  - path: /knowledge/clip.md
    label: source
    description: "This scaling observation is described in the CLIP paper’s experiments across model/compute sizes."
sources:
  - url: "https://arxiv.org/abs/2103.00020"
    title: "Learning Transferable Visual Models From Natural Language Supervision"
---

## Observation

When CLIP is trained at different scales (model size / training compute), its average zero-shot error across a suite of tasks improves in a smooth, approximately log-log linear way.

## Evidence

Radford et al. report that average zero-shot error trends smoothly with compute across multiple training runs and architectures, and extrapolate that substantially more compute would be needed for zero-shot performance to reach the best overall results across their evaluation suite.

## Implications

- CLIP-style pretraining behaves predictably under scaling, making it easier to plan compute/performance trade-offs.
- Competitive “across-the-board” zero-shot performance may require very large training compute, beyond incremental scaling.
