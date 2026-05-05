# LinkedIn Thread — Day 1
**Author:** Nebiyou Abebe
**Topic:** Inference-time mechanics — prompt caching

---

**Post 1**

I built a sales agent that makes a repeated LLM call for intent classification.
My CFO memo said inference costs were "optimized by provider caching."

Then I checked whether that was actually true for my stack.

It wasn't. Here's why — and what the first question you should always ask actually is.

---

**Post 2**

Provider-side prompt caching stores the computed KV matrices for a shared prefix
server-side and reuses them across API calls — saving prefill cost on repeated calls
with the same static content.

But it only works for specific provider/model combinations.

OpenRouter exposes caching only for Anthropic and OpenAI models. For Qwen3 routed
through OpenRouter, there is no provider-side KV cache available via the API.

Before reasoning about prefix structure or token counts: ask if your provider even
exposes caching for your model. Most stacks fail here.

---

**Post 3**

If you are on a caching-capable stack (Anthropic or OpenAI), the rule is strict:

The token sequence from position 0 to your cache breakpoint must be byte-for-byte
identical across calls.

Interpolating {company_name} anywhere in your system prompt means every prospect call
has a unique prefix — cache miss every time, regardless of how much static KB content
follows.

The fix is structural — static content before the breakpoint, dynamic fields after:

```
# WRONG — dynamic field breaks the prefix
messages = [
    {"role": "system", "content": f"Classify intent for {company_name}. Rules: ..."},
    {"role": "user",   "content": inbound_message}
]

# RIGHT — static prefix is cacheable
messages = [
    {"role": "system", "content": "Classify intent. Rules: ...",
     "cache_control": {"type": "ephemeral"}},          # breakpoint here
    {"role": "user",   "content": f"{company_name}: {inbound_message}"}
]
```

---

**Post 4**

Two more traps that have nothing to do with prefix structure:

**TTL expiry.** Anthropic's cache has a 5-minute window. A sales agent handling one
prospect per session at human conversational pace almost always misses it.

**Minimum size.** OpenAI: 1,024 tokens. Anthropic Sonnet: 2,048 tokens. A small
classification call is often below both thresholds — caching never activates regardless
of annotation or structure.

Diagnostic order before any redesign:
1. Does your provider expose caching for this model?
2. Is your prompt above the minimum cacheable size?
3. Are dynamic fields appearing before the breakpoint?

Most systems fail at step 1 or 2.

---

**Post 5**

This connects to a deeper question: which phase of inference actually dominates cost?

Prompt caching reduces **prefill cost** — processing the input tokens.
But for autoregressive generation, **decode dominates** — generating output tokens one
at a time, each requiring a full model forward pass.

For a 0.6B model generating ~300 tokens from a ~200-token input on a T4 GPU, ~13–14 s
of the total latency is decode. Prefill on 200 tokens is a few hundred milliseconds.

Caching would have saved prefill cost — but the bottleneck was never there.
This is why my Week 11 trained vs prompt-only models differed by only 183 ms on a
14,000 ms baseline: the expensive part is the decode loop, not the input processing.

Know your bottleneck before optimizing.

---

**Post 6**

Full explainer with sources: https://medium.com/p/aef6253cc4e4

Sources:
- Anthropic Prompt Caching docs — docs.anthropic.com/en/docs/build-with-claude/prompt-caching
- OpenAI Prefix Caching docs — platform.openai.com/docs/guides/prompt-caching
- Hu et al. (2021) LoRA — arxiv.org/abs/2106.09685
- Kwon et al. (2023) vLLM/PagedAttention — arxiv.org/abs/2309.06180

Week 12 · 10 Academy TRP1 · Knowledge Gap Formulation
