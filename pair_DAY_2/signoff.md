# Signoff — Day 2
**Partners:** Nebiyou Abebe & Addisu Taye
**Deadline:** 2026-05-07 02:00 UTC

---

## Nebiyou signs off on Addisu's question

**Question:** What is the model actually doing at the token level when it "decides" to call a
tool, and what parts of the prompt or schema most strongly influence that choice?

**Status: Resolved.**

The explainer covers: (1) tool schemas are serialized and injected into the system prompt —
the model processes them as tokens, not as a function registry; (2) a tool call emerges when
the most probable next token is the opening of a structured tool-call sequence, not prose — no
separate selection mechanism exists; (3) three concrete reasons agents skip tools: `tool_choice:
"auto"` allows zero calls, too many tools dilute probability mass, and unsupported stacks
produce no tool-call tokens at all; (4) five-trial experiment demonstrating both the
probability-over-instruction effect (Approach A always used a fence it was told not to) and the
enforcement-layer effect (Approach B failed entirely on an unsupported stack).

Addisu confirmed the root cause of the Conversion Engine misbehavior was vague tool descriptions
and overlapping tool names rather than agent logic, which is consistent with the probability-mass
explanation.

**Gap-closure judgment: Closed.**

Before this explainer, I understood tool calling as "telling the model which tools it has" —
I assumed a well-described tool would reliably be called when relevant. I now understand there
is no special tool-selection mechanism: a tool call is just next-token prediction landing on
a structured output sequence. The consequences are precise: tool name specificity, description
exactness, tool count, and enforcement layer are not stylistic choices — they are probability
shifts. For the P24 failure in my Week 10 system, this clarifies why the fix is architectural
(structured output channel or constrained decoding) rather than a better-phrased instruction.

**Signed:** Nebiyou Abebe — 2026-05-06

---

## Addisu signs off on Nebiyou's question

**Question:** In ai_maturity.py, 43.3% of calls to Qwen3 via OpenRouter returned invalid
JSON, yet the same rubric prompt succeeded on other models. What is the token-level mechanism
behind this failure, and what is the minimum architectural change required to prevent it?

**Gap-closure judgment: Closed.**

Before this explainer, I understood structured output failures as prompt problems — fix the
instruction, fix the output. I now understand that prompt instruction and constrained decoding
are mechanically different enforcement levels, not stronger and weaker versions of the same
thing. Prompting shifts probabilities; constrained decoding changes which tokens are physically
allowed at each step.

The P24 failure happened before parsing. The model never committed to a JSON output channel.
The contradictory rubric prompt (no-fence instruction with a fenced example) sent a mixed
signal that the model's training distribution resolved by predicting a fence — because fenced
JSON appears more often than unfenced JSON in similar contexts. The parser that follows cannot
rescue output that was never structured to begin with.

The minimum architectural fix is not a better prompt. It is moving enforcement upstream: native
structured outputs or constrained decoding (via `transformers-cfg` or equivalent) so the model
cannot produce non-compliant tokens. The parser becomes a fallback, not the primary line of
defense.

**Remaining uncertainty:** Constrained decoding guarantees schema-valid output but does not
guarantee semantically correct output. A follow-up would test whether GCD-enforced outputs
actually improve downstream scoring accuracy or just format compliance.

**Signed:** Addisu Taye — 2026-05-06

---

## Joint confirmation

Both partners confirm that their respective questions were sharpened from generic drafts to
artifact-grounded questions before the morning deadline, that explainers were exchanged before
the evening call, and that the grounding commit has been made to the Week 10 ai_maturity rubric.
