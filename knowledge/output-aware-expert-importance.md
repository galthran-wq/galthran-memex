---
title: "Output-Aware Expert Importance"
type: concept
summary: "A scoring method that combines gating weights with expert output magnitude and token contribution to rank expert importance for pruning."
tags: [ml, moe, compression]
created: "2026-02-09"
edges:
  - path: /knowledge/expert-pruning.md
    label: about
    description: "A method for scoring experts during pruning"
  - path: /knowledge/mixture-of-experts.md
    label: requires
    description: "Applies to MoE architectures"
  - path: /knowledge/easy-ep.md
    label: source
    description: "Introduced in the EASY-EP paper"
---

## Definition

Output-Aware Expert Importance is a scoring method for ranking experts in MoE models during pruning. Unlike simple activation frequency counting, it considers both the magnitude of expert outputs and how much each token's representation changes due to the MoE layer.

## How It Works

The method computes expert importance in a single forward pass (no backpropagation):

**Step 1: Expert Contribution Score**

$$c_{i,t} = g_{i,t} \cdot \|e_{i,t}\|$$

Where $g_{i,t}$ is the gating value (router weight) for expert $i$ on token $t$, and $\|e_{i,t}\|$ is the L2 norm of expert $i$'s output for token $t$.

**Step 2: Token Contribution Estimation**

$$s_t = 1 - \cos(h_t, \tilde{h}_t)$$

Where $h_t$ is the hidden state after the MoE layer and $\tilde{h}_t$ is the hidden state before. This measures how much the MoE layer changes the representation.

**Step 3: Final Expert Score**

$$I(E_i) = \sum_t c_{i,t} \cdot s_t$$

Aggregates across all tokens, weighting by how influential each token's MoE transformation is.

## Connections

This scoring method addresses limitations of simpler approaches:
- **Activation frequency** ignores output magnitude — an expert selected often but contributing little scores high
- **Raw output norm** ignores routing weights and token importance
- **Output-aware scoring** captures both what the expert produces and whether it matters for the final representation
