# Day 1 Explainer — Prompt Caching Prefix Mechanics
**Author:** Nebiyou Abebe (answering Natnael Alemseged's question)
**Date:** 2026-05-04
**System:** OpenRouter → qwen/qwen3-235b-a22b

---

## The question

Natnael's Week 10 sales agent routes an intent-classification call through OpenRouter to
`qwen/qwen3-235b-a22b`. His CFO memo stated that inference costs were "optimized by provider
caching." He wanted to know: (1) whether that model/provider combination actually exposes
prompt caching, and (2) if it does, what exact token-prefix condition must hold for a cache hit
— specifically whether interpolating `{company_name}` into the system prompt or appending a
new message would break the reusable prefix.

---

## Why this matters

Every FDE who deploys an LLM in a repeated-call pattern faces the same question: can I
reduce prefill cost by reusing a shared prefix? The intuition says yes — static content should
be cacheable. But the answer depends entirely on whether the provider exposes caching for the
specific model in use. Getting this wrong means either paying for an optimization that was
never available, or missing one that is. For Natnael, it meant a claim in a CFO memo that was
unverified and incorrect.

---

## Short answer

Provider-side prompt caching is not available on this stack. OpenRouter passes Anthropic's
`cache_control` and OpenAI's automatic prefix caching through to those providers natively —
but for third-party models routed through OpenRouter (including all Qwen3 variants), no
provider-side KV cache is exposed via the API. The system pays full prefill on every call
regardless of prefix structure or prompt length. There is no redesign path through caching
on this stack.

The rest of this explainer covers the mechanics so the CFO memo can be corrected accurately
and so the pattern is recognizable when it does apply.

---

## What provider-side caching is

When a model processes a prompt, it computes Key (K) and Value (V) attention matrices for
every token in the context. These are expensive. Provider-side caching stores those K/V
matrices server-side and reuses them if the same token prefix appears in a future API call —
reducing the prefill cost on subsequent calls.

Two providers expose this today:
- **Anthropic** — explicit `cache_control` breakpoints, ~5-minute TTL, minimum 2,048 tokens (Sonnet)
- **OpenAI** — automatic at 1,024-token boundaries, no annotation needed

OpenRouter acts as a proxy. For Anthropic and OpenAI models it forwards these caching
semantics. For everything else — including Qwen3 — it does not. The underlying inference
cluster may use internal KV caching for efficiency, but that is not exposed as a cost
reduction mechanism through the API.

---

## The exact prefix condition (for caching-capable stacks)

**The token sequence from position 0 to the cache breakpoint must be byte-for-byte identical
across calls.**

Interpolating any dynamic field — including `{company_name}` — before the breakpoint produces
a unique token sequence for every call. Cache miss every time.

The correct prompt structure pushes all dynamic fields after the breakpoint:

```python
# WRONG — {company_name} is in the system prompt, breaking the prefix per prospect
messages = [
    {
        "role": "system",
        "content": f"Classify the intent of this message from {company_name}. Rules: ..."
    },
    {"role": "user", "content": inbound_message}
]

# RIGHT — static content is cacheable; dynamic fields come after the breakpoint
messages = [
    {
        "role": "system",
        "content": "Classify intent. Rules: ...",
        "cache_control": {"type": "ephemeral"}   # Anthropic breakpoint
    },
    {
        "role": "user",
        "content": f"Company: {company_name}\nMessage: {inbound_message}"
    }
]
```

Appending a new message at the end of a conversation does not break the prefix — the system
prompt before the breakpoint is unchanged. The growing conversation history adds tokens after
the breakpoint, not before it.

---

## What else invalidates reuse

1. **TTL expiry** — Anthropic's cache has a ~5-minute TTL. A sales agent handling one prospect
   per session at human conversational pace almost always exceeds this.
2. **Prompt below minimum size** — OpenAI: 1,024 tokens; Anthropic Sonnet: 2,048 tokens.
   A small classification call is often below both. Caching never activates.
3. **Model version change** — cached K/V matrices are model-specific.

Diagnostic order before any redesign: (1) does the provider expose caching for this model?
(2) is the prompt above the minimum cacheable size? (3) are dynamic fields before the
breakpoint? Most systems fail at step 1 or 2.

---

## CFO memo correction

Delete: *"inference costs are optimized by provider caching."*

Replace with: *"Prompt caching is not available on the current inference stack
(OpenRouter + Qwen3-235b-a22b). OpenRouter exposes provider-side caching only for Anthropic
and OpenAI models. The system pays full prefill cost on every classification call in
`reply_intent.py`. The available cost reduction levers are: (1) replacing the LLM
classification call with a deterministic classifier for high-confidence intent categories,
(2) routing to a smaller model tier, or (3) switching to an Anthropic or OpenAI model with a
static system prompt above the minimum cacheable threshold."*

---

## Adjacent concepts

**1. Inference-time KV cache vs provider-side caching**
These are frequently confused. The inference-time KV cache (always active within a single
generation call) prevents recomputing already-seen tokens during the decode phase of one call.
Provider-side caching reuses K/V matrices *across separate API calls*. The first is automatic
and invisible; the second requires provider support and correct prompt structure.

**2. Prefill vs decode phase costs**
Prompt caching reduces prefill cost — processing input tokens. But for autoregressive
generation, decode dominates: each output token requires a full model forward pass. For a
0.6B model generating ~300 tokens from a ~200-token input on a T4 GPU, approximately 13–14 s
of the total latency is decode; prefill accounts for a few hundred milliseconds. Even if
caching were available on this stack, the savings on a 200-token prefix would be marginal —
the bottleneck is in the phase caching cannot touch.

**3. Quantization as the real decode cost lever**
If the goal is reducing inference cost on a decode-dominated workload, quantization is the
highest-leverage tool. 4-bit quantization halves the weight size loaded from HBM per decode
step, directly attacking the memory-bandwidth bottleneck. On Unsloth + T4, this is available
with one flag change (`load_in_4bit=True`). Prompt caching addresses the wrong phase for this
workload; quantization addresses the right one.

---

## Papers, tools, and follow-on directions

**Papers**
- Hu et al. (2021) *LoRA: Low-Rank Adaptation of Large Language Models* — arxiv.org/abs/2106.09685.
  Section 4 explains merge_and_unload and why merged weights share the base model's shape.
- Kwon et al. (2023) *Efficient Memory Management for Large Language Model Serving with
  PagedAttention* — arxiv.org/abs/2309.06180. Section 2 is the clearest published description
  of the inference-time KV cache and how it differs from provider-side caching.

**Primary documentation**
- Anthropic Prompt Caching — docs.anthropic.com/en/docs/build-with-claude/prompt-caching
- OpenAI Prefix Caching — platform.openai.com/docs/guides/prompt-caching

**Tool used**
OpenRouter API documentation and model routing table — verified that Qwen3-235b-a22b does not
appear in OpenRouter's list of models with exposed cache_control or automatic prefix caching.

**Follow-on directions**
- If switching to Anthropic: measure static prefix length in `reply_intent.py` against the
  2,048-token minimum before annotating any breakpoints.
- If staying on OpenRouter + Qwen3: profile whether the classification call can be replaced
  with a deterministic rule or a smaller locally-hosted classifier to eliminate the prefill
  cost entirely.
