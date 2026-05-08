# Signoff — Day 4
**Partners:** Nebiyou Abebe, Yakob Dereje, Rafia Kedir
**Date:** 2026-05-08

---

## Nebiyou signs off on Yakob's question

**Question:** In my Week 11 Tenacious-Bench, my LLM judge achieved ≥80% inter-rater
agreement but was never tested for position bias, length bias, or self-preference bias.
My Delta A result of +0.263 (p<0.0001) was measured using this judge. Does this result
hold, or could systematic judge bias explain part of the lift?

**Status: Resolved.**

The explainer covers: (1) position bias as a token-level effect — slot identity becomes
a feature during judge inference before the model has fully read the content; (2) length
bias as verbosity tokens acting as proxy quality signals — longer outputs contain more
rubric-adjacent tokens that inflate judge scores independent of actual quality; (3)
self-preference bias as style familiarity rather than authorship — the mechanism persists
across different model families because frontier models share overlapping post-training
data; (4) two live experiments — a deterministic length-bias screen (no positive pattern
at n=50) and a live position-swap audit via gpt-4o-mini (flip_rate=0.20, slot_A asymmetry
detected at n=5); (5) the correct defensible framing for Yakob's result.

**Gap-closure judgment: Closed.**

Before this explainer I understood inter-rater agreement as sufficient evidence that a
judge is reliable. I now understand that agreement answers one question (does the judge
agree with humans overall?) while bias tests answer a different question (does the judge's
verdict change when irrelevant features of the evaluation setup change?). Those are
separate validity checks. An 80% agreement rate combined with an unaudited position order
does not rule out a partially inflated Delta A. Yakob's result is not wrong — it is
under-audited. The minimum fix is a position-swap on 20+ pairs using his actual judge.

**Signed:** Nebiyou Abebe — 2026-05-08

---

## Rafia signs off on Nebiyou's question

**Question:** Does auto-deriving evaluation topics and relevance labels from the same
PageIndex structure used by the retrieval method create circular bias that inflates
`precision@3` for PageIndex-assisted retrieval over baseline vector search, and is a
held-out human-labeled query set the minimum fair fix?

**Status: Resolved.**

The explainer confirms: both the retrieval system and the evaluation labels share the
same PageIndex structure — evaluation coupling. PageIndex has a structural advantage
because the benchmark is aligned with how it organizes information. Vector search
retrieves by semantic similarity and may retrieve genuinely useful content that still
scores lower because it does not align with PageIndex section boundaries. The benchmark
measures two things simultaneously: real retrieval improvement plus structural advantage
from label alignment. A held-out human-labeled query set with independent relevance
judgments is the minimum fair fix — humans write queries from real information needs,
not from section names, and judge relevance without knowing which system produced each
result.

**Gap-closure judgment: Closed.**

Before this explainer I understood my precision@3 result as a straightforward comparison
between two retrieval approaches. I now understand it as partially confounded — the labels
were derived from the same structure that PageIndex was built from, which means the
benchmark cannot distinguish genuine retrieval improvement from structural alignment
advantage. This is the same class of problem as test-collection bias in the Cranfield/TREC
tradition: relevance judgments must be independent of the retrieval system being evaluated.
My Week 3 result is not invalid — it tells me PageIndex performs well under structure-aware
evaluation. It cannot tell me PageIndex is universally better without an independent
evaluation set.

**Signed:** Rafia Kedir — 2026-05-08

---

## Joint confirmation

All three partners confirm that questions were sharpened before the morning call, explainers
were exchanged, experiments were run (live position-swap audit and length-bias screen for
Yakob's question), and results were discussed in the evening session.

**Connecting insight:** Both Day 4 questions are the same underlying problem — evaluation
coupling. The measurement system shares structure with the thing being measured. In both
cases the metric is real but partially confounded, and in both cases the fix is the same:
separate the evaluation labels from the system being evaluated.
