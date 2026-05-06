# Day 2 Explainer — How Function-Calling Works at the Token Level
**Author:** Nebiyou Abebe (answering Addisu Taye's question)
**Date:** 2026-05-06

---

## The question

Addisu's Week 10 Conversion Engine sometimes called the wrong tool, skipped tools entirely, or
continued in natural language even when a tool was available. Small changes to the prompt or
tool description could completely change the agent's behavior. His question: what is the model
actually doing at the token level when it "decides" to call a tool, and what parts of the
prompt or schema most strongly influence that choice?

---

## Why this matters

Any FDE building a multi-agent system eventually hits this failure: the agent ignores a tool
you gave it, picks the wrong one, or produces prose when it should have fired a tool call.
Without understanding what the model is actually doing, every fix is a guess. Understanding
the token-level mechanism tells you exactly where to intervene: the tool name, the description,
the schema, the conversation history, or the enforcement layer.

---

## Short answer

The model does not have a tool-selection mechanism separate from language generation. It has
one mechanism: predict the next token. A tool call emerges when the most probable next token,
given everything in the context, is the opening of a structured tool-call sequence rather than
ordinary prose. Tool definitions are injected into the system prompt and become part of the
token context the model conditions on. Whether a tool call happens depends on whether the
model's training makes tool-call tokens more probable than prose tokens in that context.

---

## What actually happens at the token level

When you include tools in an API call, the provider serializes your tool definitions and
injects them into the system prompt before the model sees anything. A simplified version looks
like this:

```
[SYSTEM]
You are a helpful assistant.

Available tools:
- classify_intent(message: str, company: str) -> IntentLabel
  Use this to classify the intent of an inbound customer message.

[USER]
Classify this message: "We're interested in your enterprise plan..."
```

The model processes this as a single token sequence. When it generates a response, it predicts
the next token given all previous tokens. If the model's training has associated this context
pattern with tool-call outputs, it will predict the opening tokens of a tool call — something
like `{"tool": "classify_intent", "arguments":` — rather than `I think this message means...`.

There is no hidden branch in the inference graph. There is only next-token prediction.

---

## Why small prompt changes cause large behavioral differences

Tool names, descriptions, and parameter names shift the probability distribution over next
tokens. A tool named `process_input` is ambiguous — the model's training gives it no clear
signal about when to use it. A tool named `classify_inbound_intent` is specific — the model
has seen enough training signal associating "classify" + "intent" + "inbound message" contexts
with structured tool-call outputs to make that call probable.

The same applies to descriptions. According to Anthropic's tool-use documentation, tool
descriptions are "by far the most important factor" in tool selection. A description that says
"Use this when the user sends a message" is nearly useless — it matches almost any context.
A description that says "Use this to classify the intent of an inbound sales message into one
of: inquiry, objection, request, off-topic" gives the model a specific conditional signal.

This is why Addisu's agent behaved differently after small prompt edits: he was not changing
the agent's logic, he was shifting the probability distribution the model samples from.

---

## Why agents skip tools or continue in prose

Three concrete reasons:

**1. `tool_choice: "auto"` allows zero tool calls.**
In auto mode, the model chooses whether to call a tool at all. If prose feels more probable
than a tool call — because the description is vague, the tool name is ambiguous, or the
conversation history contains mostly prose responses — the model generates prose.

**2. Too many tools dilute the signal.**
Each additional tool in the context competes for probability mass. With ten tools and an
ambiguous query, no single tool may be sufficiently more probable than prose to win the sample.

**3. Unsupported enforcement layers.**
If the provider or model does not support native tool_use, there are no "tool call tokens" in
the model's output vocabulary for this context. The model falls back to text.

---

## Concrete demonstration — experiment results

To test the difference between prompt-instructed structure and native tool_use, I ran 5 trials
of each approach using `meta-llama/llama-3.1-8b-instruct` through OpenRouter, using the same
AI maturity scoring task from my Week 10 system:

| Approach | Failures | Observation |
|---|---|---|
| Prompt-instructed JSON | 0/5 | Model always used markdown fence despite "no fence" instruction — parser rescued it |
| Native tool_use | 5/5 | Complete failure — model produced no tool call at all |

The Approach A result illustrates the token-probability point directly: the model was told
"no markdown fencing" but its training data contained fenced JSON far more often than unfenced
JSON in similar contexts. The most probable next token was `` ```json ``, so that is what it
produced — ignoring the instruction. The downstream parser rescued the output.

The Approach B result illustrates the enforcement-layer point: `meta-llama/llama-3.1-8b-instruct`
routed through OpenRouter's gateway did not expose a working tool-call path. There were no
tool-call tokens to predict. The model produced nothing useful. Native tool_use is not
universally more reliable — it depends on whether the model and provider actually support it.

---

## Adjacent concepts

**1. Logit bias and temperature**
Before sampling the next token, the model produces a probability distribution over its entire
vocabulary. Temperature scales this distribution (lower = more peaked, higher = more uniform).
Logit bias allows manual adjustment of specific token probabilities before sampling — you can
force or suppress specific tokens. This is the low-level mechanism behind logit-based
structured output enforcement.

**2. Fine-tuning for tool use**
Models that reliably call tools have been fine-tuned on examples of tool-call outputs. This
training shifts the model's weights so that tool-call token sequences become more probable in
the right contexts. A model that has not been fine-tuned for tool use will produce tool-call
tokens only if prompted very explicitly — and even then unreliably.

**3. Constrained decoding**
Instead of shifting probabilities through prompting or fine-tuning, constrained decoding
restricts which tokens are legal at each generation step using a grammar or schema. A grammar
state machine runs alongside the model: after each token, only tokens that keep the output
valid according to the grammar are allowed. This makes valid JSON or valid tool calls
guaranteed at the decoder level — not just probable.

GCD (Geng et al., EMNLP 2023) demonstrates this for structured NLP tasks without any
fine-tuning. The key point for P24: you do not need to retrain the model to get reliable
structured output. Constraining the decoder at inference time — via `transformers-cfg` on a
HuggingFace model — gives the same guarantee as fine-tuning on structured outputs, without
touching the weights. This moves the enforcement from "prompt the model to comply" to "the
model physically cannot produce non-compliant output."

---

## Papers, tools, and follow-on directions

**Primary documentation**
- Anthropic Tool Use documentation — docs.anthropic.com/en/docs/build-with-claude/tool-use
- OpenAI Function Calling documentation — platform.openai.com/docs/guides/function-calling

**Papers**
- Vaswani et al. (2017) *Attention Is All You Need* — arxiv.org/abs/1706.03762
  Section 3 describes the decoder's next-token prediction mechanism that underlies all of this.
- Willard & Louf (2023) *Efficient Guided Generation for Large Language Models* — arxiv.org/abs/2307.09702
  The Outlines paper; describes grammar-constrained decoding as a finite-state machine over
  the model's token vocabulary.

**Tool used**
OpenRouter API with `meta-llama/llama-3.1-8b-instruct` — 5-trial comparison of
prompt-instructed JSON vs native tool_use on an AI maturity scoring task. Results showed
prompt JSON succeeded (parser-rescued) while native tool_use failed entirely on this stack.

**Follow-on directions**
- Enable `tool_choice: "required"` or force a specific tool when the agent must call a tool
- Use strict schema enforcement (Anthropic strict tool use, OpenAI strict mode) to get
  grammar-constrained guarantees rather than best-effort compliance
- Keep the tool set small and names non-overlapping to reduce probability dilution
- For P24-style failures specifically: the fix is structured outputs or strict tool_use on a
  supported model, not a more elaborate prompt
