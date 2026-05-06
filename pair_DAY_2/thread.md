# LinkedIn Thread — Day 2
**Author:** Nebiyou Abebe
**Topic:** Agent and tool-use internals — function-calling at the token level

---

**Post 1**

My partner's sales agent sometimes called the wrong tool, skipped tools entirely, or kept
generating prose when a tool was right there.

He thought something was wrong with his agent logic.

It wasn't. The model doesn't have a separate tool-selection mechanism. Here's what's actually
happening — one token at a time.

---

**Post 2**

When you give an LLM a set of tools, the provider serializes those tool definitions and injects
them into the system prompt. The model sees them as tokens — not as a menu or a function
registry.

A tool call emerges when the most probable next token, given everything in the context, is the
opening of a structured tool-call sequence rather than prose.

There is no hidden branch. There is only next-token prediction.

```
[SYSTEM]
Available tools:
- classify_intent(message: str) -> IntentLabel
  Use this to classify the intent of an inbound sales message.

[USER]
Classify this: "We're interested in your enterprise plan..."

[MODEL predicts]: {"tool": "classify_intent", "arguments": ...
```

---

**Post 3**

This explains why small prompt changes cause large behavioral shifts.

Tool names and descriptions shift the probability distribution over next tokens. A tool named
`process_input` gives the model no clear signal. A tool named `classify_inbound_intent` with a
specific description gives it a precise conditional.

Three reasons agents skip tools or produce prose instead:

1. `tool_choice: "auto"` — the model can choose zero tools if prose feels more probable
2. Too many tools — probability mass gets diluted across competing options
3. Unsupported stack — if the provider doesn't expose tool-call tokens for this model,
   there is nothing to predict

---

**Post 4**

I tested this directly — 5 trials each of prompt-instructed JSON vs native tool_use on the
same task, using meta-llama/llama-3.1-8b-instruct through OpenRouter:

| Approach | Failures | What happened |
|---|---|---|
| Prompt JSON | 0/5 | Model ignored "no fence" instruction — always used markdown fence. Parser rescued it. |
| Native tool_use | 5/5 | Complete failure — no tool-call tokens on this stack |

The Approach A result shows token probability winning over prompt instruction. The model's
training data had fenced JSON far more often than unfenced JSON in similar contexts — so it
predicted a fence regardless of the instruction.

The Approach B result shows that native tool_use is not universally more reliable. It requires
actual model and provider support. Without it, the failure moves — not disappears.

---

**Post 5**

The deeper concept: there are three layers of enforcement, each stronger than the last.

1. **Prompt instruction** — nudges probabilities ("please return JSON"). Weakest. Can be
   overridden by training distribution.
2. **Native tool_use / function calling** — dedicated tool channel. Stronger. But requires
   the model and provider to actually support it.
3. **Constrained decoding** — grammar state machine runs alongside the model and filters
   illegal tokens at every step. Mathematically guaranteed valid output. Strongest.

Most agent failures happen because teams assume they are at layer 2 or 3 when they are
actually at layer 1.

---

**Post 6**

Full explainer with sources: https://medium.com/p/5552d690723d

Sources:
- Vaswani et al. (2017) Attention Is All You Need — arxiv.org/abs/1706.03762
- Willard & Louf (2023) Efficient Guided Generation — arxiv.org/abs/2307.09702
- Anthropic Tool Use docs — docs.anthropic.com/en/docs/build-with-claude/tool-use
- OpenAI Function Calling docs — platform.openai.com/docs/guides/function-calling

Week 12 · 10 Academy TRP1 · Knowledge Gap Formulation
