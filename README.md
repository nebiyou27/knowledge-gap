# Week 12 — Knowledge Gap Formulation

**Author:** Nebiyou Abebe (nebiyoua@10academy.org)
**Program:** 10 Academy TRP1
**Week:** 12 — Peer knowledge-gap pairing exercise

---

## What this is

Two days of structured peer pairing where each partner surfaces a real knowledge gap from their
Week 10/11 work, sharpens it into a precise technical question, exchanges explainers, and makes
a grounding commit to an existing artifact.

Each day produces 9 deliverables: a question, morning call summary, explainer, sources,
experiment or demonstration, LinkedIn thread, evening call summary, signoff, and grounding
commit record.

---

## Partners

| Day | Partner | Topic |
|-----|---------|-------|
| Day 1 | Natnael Alemseged | Inference-time mechanics — prompt caching and LoRA latency |
| Day 2 | Addisu Taye | Agent and tool-use internals — function-calling at the token level |

---

## Structure

```
pair_DAY_1/          # Day 1 — Natnael Alemseged
pair_DAY_2/          # Day 2 — Addisu Taye
```

Each folder contains:

| File | Description |
|------|-------------|
| `question.md` | Sharpened question grounded in a specific artifact and failure |
| `morning_call_summary.md` | Pre-exchange context — both questions and how they were sharpened |
| `explainer.md` | Technical explainer answering the partner's question |
| `sources.md` | Papers, docs, and tools cited in Harvard style |
| `experiment.py` or equivalent | Live demonstration or code supporting the explainer |
| `thread.md` | 6-post LinkedIn thread summarizing the explainer publicly |
| `evening_call_summary.md` | Post-exchange synthesis — what the partner's explainer resolved |
| `signoff.md` | Both partners' gap-closure judgments |
| `grounding_commit.md` | Documents the change made to an existing artifact as a result |

---

## Day 1 — Inference-Time Mechanics

**Nebiyou's question:** Why did merging a LoRA adapter via `merge_and_unload()` add only 183 ms
(+1.3%) to per-task inference latency in the Week 11 ablation, even though the trained model
has different weights?

**Natnael's question:** What exact token-prefix condition must hold for provider-side prompt
caching to hit across successive calls, and does changing a company name or appending a message
break the reusable prefix?

**Grounding commit:** `D:\TRP-1\week-11\Sales Eval Bench\reports\tenacious_bench_eval_memo.md`
— rewrote the cost-Pareto section with a mechanistic explanation of memory-bandwidth bound
decode and the merge_and_unload shape argument. Added single-measurement caveat.

**Published:** [Medium blog](https://medium.com/p/aef6253cc4e4)

---

## Day 2 — Agent and Tool-Use Internals

**Nebiyou's question:** In `ai_maturity.py`, 43.3% of calls to Qwen3 via OpenRouter returned
invalid JSON. What is the token-level mechanism behind this failure, and what is the minimum
architectural change required to prevent it?

**Addisu's question:** What is the model actually doing at the token level when it "decides"
to call a tool, and what parts of the prompt or schema most strongly influence that choice?

**Key finding:** A tool call is next-token prediction — there is no separate tool-selection
mechanism. Three enforcement layers exist: prompt instruction (probabilistic), native tool_use
(structured channel, requires model/provider support), constrained decoding (grammar state
machine, guaranteed valid output). Most agent failures happen because teams assume layer 2 or
3 when they are at layer 1.

**Experiment:** 5-trial comparison of prompt-instructed JSON vs native tool_use on
`meta-llama/llama-3.1-8b-instruct` via OpenRouter. Approach A: 0/5 failures (parser rescued
fenced output). Approach B: 5/5 failures (no tool-call support on this stack).

**Grounding commit:** `D:\TRP-1\week-10\Conversion Engine\agent\prompts\ai_maturity_rubric.md`
— removed markdown fence from the Output Format example that contradicted the "no markdown
fencing" instruction. This mixed signal was the root cause of the P24 failure (43.3% invalid
JSON rate).

**Published:** [Medium blog](https://medium.com/p/5552d690723d)

---

## Papers

- Vaswani et al. (2017) *Attention Is All You Need* — [arxiv.org/abs/1706.03762](https://arxiv.org/abs/1706.03762)
- Willard & Louf (2023) *Efficient Guided Generation for Large Language Models* — [arxiv.org/abs/2307.09702](https://arxiv.org/abs/2307.09702)
- Geng et al. (2023) *Grammar-Constrained Decoding for Structured NLP Tasks without Finetuning* — [EMNLP 2023](https://github.com/epfl-dlab/GCD)
- Hu et al. (2022) *LoRA: Low-Rank Adaptation of Large Language Models* — [arxiv.org/abs/2106.09685](https://arxiv.org/abs/2106.09685)
