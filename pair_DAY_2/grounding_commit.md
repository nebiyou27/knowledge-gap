# Grounding Commit — Day 2
**File edited:** `agent/prompts/ai_maturity_rubric.md` (Week 10 Conversion Engine)
**Section:** Output Format
**Commit message:** `fix: remove markdown fence from ai_maturity rubric example (P24 fix)`

---

## What was changed

The Output Format section of the rubric previously read:

> Respond with ONLY a JSON object, no markdown fencing, no explanation:
>
> ```json
> {
>   "score": <integer 0-3>,
>   ...
> }
> ```

The instruction says "no markdown fencing" but the example immediately below uses a ` ```json `
fence. This is the prompt contradiction identified as the dominant cause of the P24 failure
(43.3% invalid JSON rate on Qwen3 via OpenRouter).

The fenced example was replaced with a bare JSON block — no opening ` ```json `, no closing
` ``` `. The instruction and the example now agree.

---

## Why this improves the artifact

A prompt that says one thing and demonstrates the opposite sends a mixed signal that token
prediction resolves by referencing the training distribution — not by following the instruction.
For thinking models especially, the probability mass is strongly concentrated on fenced JSON
(because fenced JSON appears far more often than unfenced JSON in instruction-following training
data). The model predicts a fence because the demonstration makes a fence the more probable
completion, regardless of the text instruction.

The fix removes the conflicting signal. The instruction and the example are now consistent:
both say "bare JSON." This does not guarantee structured output — for that, the architectural
fix is native structured outputs or constrained decoding upstream. But it removes the mixed
signal that made P24 failures predictable and removes the need for the downstream parser to
rescue fenced output that was explicitly prohibited.

This is the gap identified in the Week 12 Day 2 question: the rubric prompt was internally
contradictory at the demonstration level, not just the instruction level. Addisu's explainer
confirmed the causal chain (training distribution dominates over contradictory instruction;
thinking models are especially prone to prose deliberation before committing to a channel).
The grounding commit addresses the root cause at the prompt layer while the full architectural
fix remains a future improvement.
