---
title: "Expert Pruning"
type: concept
summary: "A model compression technique that permanently removes experts from MoE models to reduce memory footprint while preserving task performance."
tags: [ml, compression, efficiency, moe]
created: "2026-02-09"
edges:
  - path: /knowledge/mixture-of-experts.md
    label: requires
    description: "Expert pruning is specifically applied to MoE architectures"
  - path: /knowledge/few-shot-expert-localization.md
    label: uses
    description: "Few-shot methods can identify which experts to retain"
  - path: /knowledge/output-aware-expert-importance.md
    label: uses
    description: "Importance scoring determines which experts to prune"
---

## Definition

Expert pruning is a structured compression technique for Mixture of Experts models that permanently removes entire expert sub-networks from the model. Unlike weight pruning (removing individual parameters) or quantization (reducing precision), expert pruning eliminates whole computational units while attempting to preserve performance on target tasks.

## How It Works

1. **Importance Estimation**: Score each expert's contribution to model outputs on calibration data
2. **Selection**: Retain top-K experts per layer based on importance scores
3. **Removal**: Permanently delete unselected experts from the model
4. **Deployment**: Run the pruned model with reduced memory and potentially higher throughput

The key challenge is determining expert importance. Methods include:
- Activation frequency (how often an expert is selected by the router)
- Output magnitude (L2 norm of expert outputs)
- Task-aware scoring like [output-aware expert importance](/knowledge/output-aware-expert-importance.md)

## Connections

Expert pruning exploits the observation that MoE models exhibit [domain specialization](/knowledge/few-shot-expert-localization.md) — different experts handle different types of inputs. For domain-specific deployments, experts irrelevant to the target domain can be removed with minimal performance loss.

Trade-offs:
- 50% expert retention: near-full performance on target domain
- 75% pruning: still functional but degraded
- General-purpose deployment requires retaining more experts
