---
title: "EASY-EP: Domain-Specific Pruning of Large MoE Models"
type: reference
summary: "A method for pruning 50-75% of experts from large MoE models like DeepSeek-R1 using few-shot calibration, achieving 2.99-4.33x throughput with minimal domain-specific performance loss."
tags: [ml, paper, moe, compression, efficiency]
created: "2026-02-09"
edges:
  - path: /knowledge/mixture-of-experts.md
    label: about
    description: "Proposes a pruning method for MoE models"
  - path: /knowledge/expert-pruning.md
    label: about
    description: "Introduces a specific expert pruning approach"
  - path: /knowledge/few-shot-expert-localization.md
    label: about
    description: "Key observation enabling the method"
  - path: /knowledge/output-aware-expert-importance.md
    label: about
    description: "Introduces this scoring method"
sources:
  - url: "https://arxiv.org/abs/2504.06792"
    title: "EASY-EP: Domain-Specific Pruning of Large Mixture-of-Experts Models with Few-shot Demonstrations"
  - url: "https://github.com/RUCAIBox/EASYEP"
    title: "EASY-EP GitHub Repository"
---

## Summary

EASY-EP (NeurIPS 2025) addresses the memory problem of large MoE models: DeepSeek-R1 (671B) requires ~1500GB in BF16 or ~750GB in FP8, even though only ~37B parameters activate per token. The paper shows that for domain-specific deployments, 50-75% of experts can be permanently removed with minimal performance loss.

The method requires only a single forward pass over 5-25 domain examples (no backpropagation). It uses [output-aware expert importance](/knowledge/output-aware-expert-importance.md) scoring to rank experts and leverages the [few-shot expert localization](/knowledge/few-shot-expert-localization.md) finding that domain-critical experts can be reliably identified from minimal calibration data.

## Key Takeaways

**Performance Results (DeepSeek-R1)**:
- 50% retention (128/256 experts): near-full-model performance on target domain; 90%+ on mixed-domain
- 75% pruning (64/256 experts): still functional where baseline methods collapse
- Throughput gains: 128 experts = 2.99x, 64 experts = 4.33x
- Also validated on Qwen3-30B-A3B

**Practical Limitations**:
- Requires full model loaded for calibration forward pass
- Pruned model needs patched sglang fork (not standard vLLM/SGLang compatible)
- No pre-pruned checkpoints released
- Best suited for high-volume narrow-domain deployments, not general chat

## Relevance

EASY-EP demonstrates that aggressive [expert pruning](/knowledge/expert-pruning.md) is viable for production deployments when the use case is well-defined. The few-shot calibration requirement makes it practical: no need for large datasets or expensive fine-tuning. The throughput gains (3-4x) can significantly reduce serving costs for specialized applications like math tutoring or code generation assistants.
