# Signoff — Day 1
**Partners:** Natnael Alemseged & Nebiyou Abebe
**Deadline:** 2026-05-05 02:00 UTC

---

## Nebiyou signs off on Natnael's question

**Question:** What exact token-prefix condition must hold for provider-side prompt caching to
hit across successive calls, what invalidates that reuse, and whether changing a company name
or appending a new message breaks the reusable prefix?

**Status: Resolved.**

The explainer covers: (1) the byte-for-byte prefix condition and how breakpoints work on
Anthropic vs. OpenAI, (2) four invalidation cases — dynamic field in prefix, TTL gap, prompt
below minimum size, model version change — (3) why appending a message does not break the
prefix if the static section is unchanged, and (4) a diagnostic sequence for the specific case
where a small classification call may be below the minimum cacheable threshold.

Natnael confirmed the classification prompt is approximately 600 tokens — below the OpenAI
1,024-token floor — which identifies the actual blocker as prompt size, not prefix structure.
The CFO memo answer is therefore "caching is not applicable at this call size" rather than
"we should restructure the prefix."

**Gap-closure judgment: Closed.**

Before this explainer, I assumed prompt caching was automatic — that any system reusing similar
prompts would benefit from it. I now understand that is not true. Prompt caching only applies
when the specific provider and model combination supports it, and when the repeated portion of
the prompt is byte-for-byte identical across calls. I also understand that caching only reduces
the cost of reading the input (prefill), not the cost of generating the answer (decode) — which
means even a perfectly structured cacheable prompt does not remove the dominant bottleneck for
generation-heavy workloads. For Natnael's system, because provider-side caching could not be
verified for the OpenRouter → Qwen3 route, the CFO memo claim of caching savings was
unsubstantiated and needed to be removed.

**Signed:** Nebiyou Abebe — 2026-05-05

---

## Natnael signs off on Nebiyou's question

**Question:** When I ran live inference on my Week 11 ablation, the trained model (Qwen3-0.6B
+ LoRA merged via merge_and_unload()) took 14,228 ms/task and the prompt-only baseline took
14,045 ms — a difference of only 183 ms (+1.3%). Why does merging a LoRA adapter add virtually
no per-task latency?

**Gap-closure judgment: Closed.**

Before this explainer, I expected the LoRA-trained model to take longer at inference time
because I thought adding a trained adapter meant adding extra computation during generation.
I now understand that this depends on whether the LoRA adapter is kept separate or merged into
the base model.

In my Week 11 ablation, the trained model used the same base model with the LoRA adapter
merged into it. Because `merge_and_unload()` bakes the LoRA changes into the base weights, the
model does not run a separate adapter path during inference. The model still generates tokens
through the same basic decode loop, so the per-token latency stays almost the same.

The 183 ms difference on a roughly 14-second task should not be treated as strong statistical
evidence from a single measurement. The better explanation is mechanistic: merged LoRA does not
predict a meaningful slowdown unless the adapter remains unmerged, the output length changes,
the model architecture changes, or the serving path changes.

This closes the gap because I can now revise the cost/latency section of my Week 11 evaluation
report. Instead of only reporting that the trained and bare models had similar latency, I can
explain why: the main inference bottleneck is token-by-token decoding, and merging LoRA changes
the weights without adding a separate inference-time module.

**Remaining uncertainty:** A useful follow-up would be to run repeated benchmarks comparing
base, unmerged LoRA, and merged LoRA under the same local GPU conditions.

**Signed:** Natnael Alemseged — 2026-05-05

---

## Joint confirmation

Both partners confirm that their respective questions were sharpened from generic drafts to
artifact-grounded questions before the morning deadline, that explainers were exchanged before
2am, and that the grounding commit has been made to the Week 11 eval memo.
