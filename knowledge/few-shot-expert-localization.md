---
title: "Few-Shot Expert Localization"
type: insight
summary: "A small number of domain examples (5-25) suffices to reliably identify 90-99% of domain-critical experts in large MoE models."
tags: [ml, moe, efficiency]
created: "2026-02-09"
edges:
  - path: /knowledge/mixture-of-experts.md
    label: about
    description: "Observation about expert behavior in MoE models"
  - path: /knowledge/expert-pruning.md
    label: about
    description: "Enables efficient calibration for expert pruning"
  - path: /knowledge/easy-ep.md
    label: source
    description: "Key finding from the EASY-EP paper"
---

## Observation

In large-scale MoE models with many fine-grained experts (e.g., 256 per layer in DeepSeek-R1), experts exhibit strong domain specialization. The top-activated experts for math, coding, and science tasks are largely disjoint sets. Crucially, these domain-critical experts can be identified with just 5-25 examples from the target domain.

## Evidence

From EASY-EP experiments on DeepSeek-R1:
- Expert activation patterns are stable across different datasets within the same domain (84%+ overlap between MATH and GSM8K)
- Lower layers contain more shared/general experts; specialization increases with depth
- 5-shot calibration identifies most critical experts; 25-shot provides diminishing returns
- Cross-domain expert overlap is low — math experts differ from coding experts

## Implications

1. **Cheap Calibration**: No need for large calibration datasets; a handful of examples suffices
2. **Domain-Specific Deployment**: Organizations can prune models for their specific use case (e.g., math tutoring, code generation) without expensive retraining
3. **Memory-Performance Trade-off**: Domain specialization means aggressive pruning (75%) is viable for narrow deployments
4. **Architecture Insight**: Fine-grained experts (256 vs 8) amplify specialization, making pruning more effective
