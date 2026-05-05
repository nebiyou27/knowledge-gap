# Sources — Day 1
**Compiled by:** Nebiyou Abebe

---

1. **Anthropic — Prompt Caching Documentation**
   https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching
   *Defines cache_control syntax, minimum cacheable sizes (1,024 tokens for Haiku; 2,048 for
   Sonnet/Opus), the 5-minute TTL, and cache-hit pricing discounts. Primary reference for the
   Anthropic-specific mechanics in the explainer.*

2. **OpenAI — Prompt Caching Documentation**
   https://platform.openai.com/docs/guides/prompt-caching
   *Describes automatic prefix caching at 1,024-token boundaries for GPT-4o and o-series models.
   No explicit annotation required; caching activates only above the 1,024-token floor.*

3. **Hu et al. (2021) — LoRA: Low-Rank Adaptation of Large Language Models**
   https://arxiv.org/abs/2106.09685
   *Original LoRA paper. Section 4 (practical implementation) explains merge_and_unload: the A
   and B adapter matrices are folded into the base weight W_merged = W_base + α/r × B·A,
   producing a weight with the same matrix shape as the base. Key to explaining why the merged
   model has no additional memory footprint at decode time.*

4. **Williams, Waterman, Patterson (2009) — Roofline: An Insightful Visual Performance Model**
   https://dl.acm.org/doi/10.1145/1498765.1498785
   *Foundational framework for arithmetic intensity and memory-bandwidth ceilings. Explains why
   autoregressive decode — one token per forward pass — is memory-bandwidth bound rather than
   compute bound at small batch sizes. Grounds the claim that per-token latency is determined
   by weight-load time, not FLOP count.*

5. **Kwon et al. (2023) — Efficient Memory Management for Large Language Model Serving
   with PagedAttention (vLLM)**
   https://arxiv.org/abs/2309.06180
   *Section 2 contains the clearest published description of the inference-time KV cache and how
   it differs from provider-side prompt caching. Essential for distinguishing the two mechanisms,
   which are frequently confused in production discussions.*
