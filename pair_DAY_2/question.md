# Day 2 Question — Agent and Tool-Use Internals

**Asker:** Nebiyou Abebe  
**Partner:** Addisu Taye  
**Topic:** Agent and tool-use internals

---

## Final Question

In my Week 10 Conversion Engine, the AI maturity judgment module (`agent/judgment/ai_maturity.py`) asks the LLM to return a structured JSON object. In 43.3% of tau2 evaluation runs on thinking-model / Qwen3 inference, the model returned prose reasoning or empty JSON instead of a valid JSON object. This triggered the P24 failure and forced the system to abstain: no score was emitted and no S4 pitch was sent.

The current implementation handles this with a code-side parser and validator rather than native function-calling, structured outputs, or constrained decoding.

My question is:

**At the token level, what is mechanically different between asking a model to "return JSON" in the prompt and using native `tool_use`, structured outputs, or constrained decoding?**

More specifically, is the model doing the same next-token prediction task in all cases, or do native structured-output paths change the inference process by restricting or shaping which tokens are allowed? In my P24 case, would switching to native `tool_use` have prevented invalid JSON failures, or would it only move the failure to another layer, such as wrong tool selection, missing arguments, or schema mismatch?

---

## Connection to Portfolio Artifact

This question connects directly to the P24 failure in my Week 10 Conversion Engine.

The relevant files are:

- `agent/judgment/ai_maturity.py`
- `agent/prompts/ai_maturity_rubric.md`

The prompt asks:

> "Respond with ONLY a JSON object, no markdown fencing, no explanation."

But the example immediately below uses a markdown-fenced JSON block. That creates a mixed signal: the instruction says not to use a fence, while the example demonstrates a fenced response.

The parser in `ai_maturity.py` tries to handle both cases by stripping a markdown fence if present, then falling back to raw JSON parsing. But when the model returned prose reasoning instead of JSON, the parser raised `AiMaturityParseError`, and the system abstained.

Understanding this mechanism would let me revise the P24 explanation and decide whether the correct fix belongs in the prompt, the parser/validator, or the inference path itself.

---

## Why This Gap Matters Beyond My Work

Many agent systems rely on structured outputs: JSON judgments, function calls, tool arguments, routing decisions, and evaluator scores. A common shortcut is to ask the model in the prompt to "return JSON," then parse the text afterward.

This works until it does not.

The broader FDE question is when prompt-instructed JSON is enough, and when the system should use native `tool_use`, structured outputs, constrained decoding, or stricter schema validation. Understanding the token-level difference helps diagnose whether a failure is caused by prompt ambiguity, schema design, model behavior, decoding constraints, or downstream validation.

That matters for any production agent where malformed outputs can trigger abstentions, skipped actions, wrong tool calls, or broken business logic.

---

## Original Draft Before Sharpening

> At the token level, what is the mechanical difference between a model generating JSON via a "please return JSON" instruction versus generating structured output via native `tool_use` or constrained decoding? Does the model treat these as the same task, or are they fundamentally different inference paths?

The original draft identified the right mechanism, but it was still too generic. After Addisu asked for the concrete implementation details, I grounded the question in the actual P24 failure: the 43.3% invalid-output rate, the `ai_maturity.py` parser behavior, and the mixed-signal rubric prompt that said "no markdown fencing" while showing a fenced JSON example.
