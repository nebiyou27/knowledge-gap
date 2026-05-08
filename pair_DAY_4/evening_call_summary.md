# Evening Call Summary — Day 4
**Partners:** Nebiyou Abebe, Yakob Dereje, Rafia Kedir
**Date:** 2026-05-08

---

## What was resolved

**Nebiyou's question — circular evaluation bias in Document Refinery:**
Rafia's explainer confirmed the gap. Both the retrieval system and the relevance labels
share the same PageIndex structure — this is evaluation coupling. PageIndex has a structural
advantage in the benchmark not because it retrieves better in general, but because the
benchmark is aligned with how PageIndex organizes information. Vector search may retrieve
semantically correct content and still score lower because it does not align with PageIndex
section boundaries. The benchmark measures two things at once: real retrieval improvement
plus structural advantage from label alignment. A held-out human-labeled query set with
independent relevance judgments is the minimum fair fix.

**Yakob's question — LLM-as-a-judge biases:**
Nebiyou's explainer covered all three biases mechanically. Position bias: slot identity
becomes a feature during judge inference — logits for "A" or "slot A" get nudged before
the judge has fully read the content. Length bias: longer outputs contain more tokens that
look like quality signals — rubric keywords, polite framing, caveats — inflating scores
independent of actual quality. Self-preference bias: familiar style activates
quality-associated continuations even across different model families.

Two experiments were run:
- **Length-bias screen** on Week 11 artifacts (n=50): no positive length-bias pattern —
  trained outputs were shorter than prompt-only and still scored higher.
- **Live position-swap audit** via gpt-4o-mini (n=5): flip_rate=0.20, slot_A_win_rate
  jumped from 0.20 to 0.60 when outputs swapped slots — consistent with the position
  sensitivity Wang et al. (2023) describe. Ambiguous at n=5; Yakob needs to run at n=20+
  on his actual judge.

Bottom line: Delta A = +0.263 is not invalid but is under-audited. It is defensible as
a strong result under the current judge protocol, not as a fully bias-cleared model quality
gain.

---

## Key concepts from each explainer

**From Rafia (on Nebiyou's question):**
- Evaluation coupling — retrieval system and labels share the same source structure
- PageIndex benchmark measures structural alignment, not universal retrieval quality
- Vector search penalized for not matching section boundaries, not for being worse
- Fix: independent queries + independent relevance judgments

**From Nebiyou (on Yakob's question):**
- Position bias — slot identity as a token-level feature during judge inference
- Length bias — verbosity tokens as proxy quality signals in the judge's context
- Self-preference bias — style familiarity, not authorship, is the mechanism
- Cross-model judging mitigates but does not eliminate self-preference
- Wang et al. (2023): swap order on every pair and average — doubles cost, removes confound

---

## What connects the two questions

Both questions are the same underlying problem in different domains:

**Evaluation coupling** — the measurement system shares structure with the thing being
measured. In Nebiyou's case: PageIndex labels favor PageIndex retrieval. In Yakob's case:
an unaudited judge may favor outputs that match its preferred style or slot position.

In both cases the metric is real but partially confounded. In both cases the fix is
the same: separate the evaluation labels from the system being evaluated.
