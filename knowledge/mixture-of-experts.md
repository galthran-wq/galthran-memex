---
title: "Mixture of Experts"
type: concept
summary: "A neural network architecture that routes inputs to specialized sub-networks (experts), activating only a subset per forward pass for efficiency."
tags: [ml, architecture, efficiency]
created: "2026-02-09"
edges:
  - path: /knowledge/expert-pruning.md
    label: about
    description: "Expert pruning is a compression technique applied to MoE models"
---

## Definition

Mixture of Experts (MoE) is a neural network architecture where the model consists of multiple parallel sub-networks called "experts", combined with a gating mechanism that routes each input to a subset of experts. Unlike dense models that activate all parameters for every input, MoE models achieve conditional computation by only activating relevant experts per token.

## How It Works

1. **Experts**: Parallel feed-forward networks (typically in transformer blocks replacing the standard FFN)
2. **Router/Gate**: A learned network that produces routing weights determining which experts process each token
3. **Top-K Selection**: Only the top K experts (typically K=2 or K=8) are activated per token
4. **Sparse Activation**: Despite having many more total parameters, computational cost scales with active experts only

Key examples:
- DeepSeek-R1 (671B total, ~37B active): 256 fine-grained experts per layer
- Qwen3-30B-A3B: 30B total parameters, 3B active
- Mixtral 8x7B: 8 experts, 2 active per token

## Connections

The MoE architecture enables scaling model capacity without proportional compute increase, but introduces a memory bottleneck: all experts must reside in memory even though only a fraction are used per forward pass. This motivates techniques like [expert pruning](/knowledge/expert-pruning.md) to reduce memory requirements for deployment.
