---
title: "CLIP Robustness Under Natural Distribution Shift"
type: insight
summary: "In Radford et al. (2021), zero-shot CLIP reduces the typical gap between ImageNet accuracy and accuracy on natural distribution shifts (sketches, renditions, adversarially filtered natural images), relative to standard supervised baselines."
tags: [ml, vision, robustness, multimodal]
created: "2026-02-09"
edges:
  - path: /knowledge/clip.md
    label: source
    description: "This robustness observation is reported and analyzed in the CLIP paper."
sources:
  - url: "https://arxiv.org/abs/2103.00020"
    title: "Learning Transferable Visual Models From Natural Language Supervision"
---

## Observation

Zero-shot CLIP shows comparatively stronger performance under several natural distribution shifts than typical supervised ImageNet models, shrinking the robustness gap between in-distribution ImageNet and shifted variants.

![Robustness under natural distribution shift](/knowledge/assets/figure_13.png)

## Evidence

Radford et al. evaluate CLIP zero-shot on ImageNet and multiple shifted variants (for example, sketches, renditions, and adversarially curated natural images) and report that:

- Zero-shot CLIP tends to retain more accuracy under these shifts than supervised baselines with similar ImageNet performance.
- Adapting or fine-tuning to ImageNet can increase ImageNet accuracy without necessarily improving (and sometimes slightly reducing) average robustness across the shift suite.

## Implications

- Prompt-based, web-scale image-text pretraining can act as a robustness prior compared to standard closed-label supervised training.
- Improving in-distribution accuracy via fine-tuning may not translate to improvements under natural distribution shift, so robustness should be tracked separately.
