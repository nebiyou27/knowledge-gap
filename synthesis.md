# Week 12 Synthesis — Knowledge Gap Formulation
**Author:** Nebiyou Abebe
**Date:** 2026-05-09

---

## What this week was actually about

Four days of structured pairing with three partners — Natnael Alemseged, Addisu Taye, Gashaw
Bekele, and Yakob/Rafia — produced eight closed knowledge gaps, four published blog posts, and
four grounding commits to existing artifacts. The discipline was to name a gap precisely before
exchanging explainers: not "I don't understand caching" but "what exact token-prefix condition
must hold for provider-side prompt caching to hit across successive calls, and does changing a
company name break the reusable prefix?"

That sharpening step turned out to be the most transferable skill of the week.

---

## The eight gaps, closed

### Gap 1 — Prompt caching prefix conditions (Natnael's question, Day 1)

The condition is exact: the token sequence from position 0 to the cache breakpoint must be
byte-for-byte identical across API calls. Interpolating `{company_name}` into a system prompt
means every prospect call has a unique prefix — cache miss every time, regardless of how much
static knowledge base content follows. The structural fix is to push all dynamic content after
the breakpoint. But there are two prerequisites before structure matters at all: the provider
must expose caching for the model in use (OpenRouter does not expose KV caching for Qwen3),
and the prompt must exceed the minimum cacheable size (1,024 tokens for OpenAI, 2,048 for
Anthropic Sonnet). Most stacks fail at the first check.

### Gap 2 — LoRA merge latency (my question, Day 1)

Merging a LoRA adapter via `merge_and_unload()` added only 183 ms (+1.3%) to per-task
inference latency in the Week 11 ablation. The mechanism: after merge, the forward pass is
identical to a standard dense forward pass. There is no adapter overhead because the adapter
weights are absorbed into the base model. The 183 ms difference is attributable to
weight-loading order and memory allocation, not to any additional compute in the forward path.
More importantly, the dominant cost is decode, not prefill: on a T4 GPU, generating ~300 tokens
at ~21.4 tokens/second takes roughly 14 seconds. Prefill on 200 tokens is a few hundred
milliseconds. Caching would have saved prefill cost, but the bottleneck was never there.

### Gap 3 — JSON failure mechanism and minimum fix (my question, Day 2)

43.3% of calls to Qwen3 via OpenRouter returned invalid JSON in the Week 10 Conversion Engine.
The root cause was a mixed signal in `ai_maturity_rubric.md`: the Output Format section
described the required JSON structure using a markdown code fence, and a line below that fence
said "do not include markdown fencing." The model had two conflicting learned behaviors — format
the response in a fence (from pretraining on documentation), and don't (from the instruction).
Format compliance at the token level is probabilistic, so the model inconsistently obeyed one
or the other. The minimum fix was a one-line change: remove the fence from the example. The
grounding commit confirmed this — removing the mixed signal was sufficient; no constrained
decoding or retry logic was required for this specific failure mode.

### Gap 4 — Token-level tool-call mechanism (Addisu's question, Day 2)

A tool call is next-token prediction. There is no separate tool-selection module or decision
tree. When a model "decides" to call a tool, it is predicting that the next token should be
the tool-call syntax rather than prose. Three enforcement layers exist: prompt instruction
(probabilistic — shifts token probabilities, not a guarantee), native tool_use channel
(structured output via a dedicated API parameter, requires model and provider support),
and constrained decoding (grammar state machine, guaranteed valid output, requires inference
framework support). Most agent failures happen when teams assume they are at layer 2 or 3
when they are at layer 1. Identifying which layer you are actually on is the first diagnostic
step before debugging any tool-use failure.

### Gap 5 — Statistical power for a +14 pp lift (my question, Day 3)

The Week 11 ORPO run lifted pass rate from 12% to 26% (+14 pp, n=50), with p=0.23. The
question was whether this was a sample-size problem or a training failure. Cohen's h for a
12%→26% lift is h=0.3627. 80% power for detecting this effect size requires approximately 60
tasks two-tailed. n=50 was right at the boundary for the observed effect, and underpowered if
the true effect is smaller than what was observed (as it often is in a first run). The minimum
diagnostic experiment was to run 100 tasks. The 100-task run confirmed: Delta B +18 pp, CI
[+2%, +36%], significant. Sample size was the blocker, not training. The correct diagnostic
order is to rule out sample size first before investigating the training setup.

### Gap 6 — LoRA behavioral asymmetry: length vs banned-phrase (Gashaw's question, Day 3)

The trained adapter reduced output length by 18% but showed Delta A = 0.00 on banned-phrase
suppression, even though both behaviors were in the training data. The explanation is objective
mismatch, not rank limit. SFT's cross-entropy loss raises the log-probability of chosen outputs
but has no mechanism to lower the log-probability of rejected tokens. ORPO's own pilot study
shows that fine-tuning on chosen responses alone raised log-probabilities of both chosen and
rejected responses simultaneously. Length reduction is a dense, consistent, positive signal
across many tokens — imitation handles it. Banned-phrase suppression is sparse, local, and
context-sensitive — it requires a direct negative signal or inference-time enforcement. The
mechanical distinction: logit_bias=−100 blocked a token at decode time even when the model was
explicitly instructed to produce it (0/5 trials vs 5/5 without the constraint). Preference
signal and hard constraint are not stronger and weaker versions of the same mechanism. They
operate at different layers.

### Gap 7 — Circular bias in precision@3 evaluation (my question, Day 4)

The Week 3 Document Refinery benchmark derived evaluation topics and relevance labels from the
same PageIndex structure used by the PageIndex-assisted retrieval method. This is evaluation
coupling: the retrieval system and the labels share the same source structure, giving PageIndex
a structural advantage independent of actual retrieval quality. Vector search may retrieve
semantically correct content and still score lower because it does not align with predefined
section boundaries. The benchmark simultaneously measures two things — real retrieval
improvement and structural alignment advantage — and cannot separate them. A held-out
human-labeled query set with independent relevance judgments is the minimum fair fix, following
the Cranfield/TREC test-collection standard (Voorhees, 2002).

### Gap 8 — Can an unaudited judge's result be defended? (Yakob's question, Day 4)

Yakob's LLM judge achieved ≥80% inter-rater agreement but was never tested for position bias,
length bias, or self-preference bias. His Delta A = +0.263 (p<0.0001). The finding: 80%
agreement answers one question (does the judge agree with humans overall?) while bias tests
answer a different question (does the verdict change when irrelevant setup features change?).
These are separate validity checks. A live position-swap audit with gpt-4o-mini (n=5) produced
flip_rate=0.20 and slot_A_win_rate jumped from 0.20 to 0.60 when outputs changed slots — a
clear asymmetry. The correct framing for an under-audited result with strong statistics is not
"the result is wrong" but "the result is real and needs one more audit step: a position-swap on
20+ pairs." That framing is defensible; claiming the result is fully established is not.

---

## The most surprising thing learned

Going in, I assumed that statistical non-significance was evidence of training failure.
Gap 5 corrected this directly: the p=0.23 result from n=50 tasks was a measurement problem,
not a model problem. The same weight of evidence could support two completely different
conclusions depending on evaluation size. Running 100 tasks resolved the ambiguity — the
adapter learned, the signal was real, and the gap was never in the training setup.

The connected insight, which I did not expect to find, is that this exact pattern appears
across all four days. In every case, the first instinct was to blame the model or the training:
"the model ignores my instructions," "the adapter didn't learn banned phrases," "the trained
model is slower than prompt-only," "the baseline vector search underperforms." In every case
the actual cause was a measurement or enforcement layer problem sitting between the model and
the outcome: mixed signals in the prompt, the wrong enforcement layer, an underpowered eval,
evaluation coupling in the benchmark design. A model that appears to misbehave is often being
measured incorrectly.

---

## What changed in how I approach evaluation

Before this week, I treated evaluation as a one-number output: run the benchmark, read the
score. After four explainer exchanges, the scaffold I now reach for is:

1. **Is the measurement layer clean?** Does the benchmark measure what it claims to measure,
   or does it share structure with what it's evaluating?
2. **Is the eval powered?** What effect size am I expecting, and do I have enough samples to
   detect it at 80% power?
3. **Which enforcement layer am I on?** Prompt instruction (probabilistic), structured output
   (model-supported), or constrained decoding (guaranteed)? Most failures are at layer 1 while
   assuming layer 2.
4. **Has the judge been audited?** Inter-rater agreement is necessary but not sufficient. A
   position-swap audit is the minimum additional check before treating any judge-scored result
   as defensible.

These four questions did not exist as a checklist before Week 12. They emerged from having
to write precise technical answers to questions I did not choose.

---

## Reading list

See `canonical_list.md` for annotated papers, tools, and patterns with context on when each
is relevant.

---

## Public artifacts

- **Day 1:** https://medium.com/p/aef6253cc4e4
- **Day 2:** https://medium.com/p/5552d690723d
- **Day 3:** https://medium.com/p/821b9c233dd8
- **Day 4:** https://medium.com/p/d8f349ab17b2
