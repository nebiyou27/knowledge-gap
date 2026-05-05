# Day 1 Question — Inference-time Mechanics
**Asker:** Nebiyou Abebe
**Partner:** Natnael
**Topic:** Inference-time mechanics

---

## Final Question

When I ran live inference on my Week 11 ablation, two very different systems produced nearly
identical per-task latency:

- **Trained model** (Qwen3-0.6B base + LoRA adapter merged via `merge_and_unload()`): **14,228 ms**
- **Prompt-only model** (Qwen3-0.6B base, no adapter): **14,045 ms**

The difference is only **183 ms — essentially nothing**, despite the trained model having extra
weights merged into every linear layer.

I expected the adapter to slow things down. It didn't. My question is: **why not?**

Specifically — when a language model generates a response one token at a time, where does the
time actually go on a GPU? And why would merging a LoRA adapter's weights into the base model
have virtually no effect on per-task latency?

---

## Connection to Portfolio Artifact

This question connects directly to the **cost-Pareto section of my Week 11 evaluation memo**
(`reports/tenacious_bench_eval_memo.md`). That section currently reports:

> "Trained: 14,228 ms/task. Prompt-only: 14,045 ms/task. Difference: +183 ms (+1.3%)."

It reports the numbers but cannot explain them. I cannot currently answer:
- Why are they so close?
- Which phase of inference (prefill or decode) dominates the 14,000 ms?
- What would actually need to change to bring latency below the 18,000 ms deployment gate I set?

Understanding the mechanism would let me rewrite that section with a real explanation rather
than a bare number — and would change how I design any future inference pipeline in an FDE
engagement.

---

## Why This Gap Matters Beyond My Work

Every FDE who deploys a fine-tuned or adapted model faces the same question: does the adapter
add cost? The intuition says yes — more weights means more compute. The data says no in this
case. Understanding why resolves a misconception that affects every LoRA deployment decision:
whether to merge-and-unload vs. keep the adapter separate, whether adapter rank affects
inference cost, and what the real latency levers are for autoregressive generation.

---

## Original Draft (before sharpening)

> "How does inference decompose into prefill and decode phases on a GPU, and which phase
> dominates for a 0.6B model generating ~300 tokens from a ~200-token prompt?"

The original draft was generic — it could apply to any model and didn't use the surprising
observation from my own data. The sharpened version anchors the question in the 183 ms result,
which is the thing that actually needs explaining.
