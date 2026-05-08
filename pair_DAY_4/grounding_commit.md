# Grounding Commit — Day 4
**Author:** Nebiyou Abebe
**Date:** 2026-05-08

---

## What was changed

**File:** `D:\TRP-1\Week-3\document-refinery\README.md`
**Commit:** `e9b080c` — "docs: add evaluation limitation note — test-collection bias in precision@3 benchmark"

A limitation note was added to the Batch Phase 3 evaluation section explaining that the
`precision@3` comparison between PageIndex-assisted retrieval and baseline vector search
uses evaluation topics and relevance labels auto-derived from PageIndex sections. This
creates evaluation coupling — the retrieval system and the labels share the same source
structure, giving PageIndex a structural advantage independent of retrieval quality.

---

## Why this change

The Day 4 explainer from Rafia confirmed that the Week 3 benchmark cannot distinguish
genuine retrieval improvement from structural alignment advantage. A benchmark that
documents its own limitations is more honest and more useful than one that reports
a metric without noting what it can and cannot prove.

The README now states:
- What the benchmark actually measures (PageIndex alignment with its own sections)
- Why vector search is disadvantaged (semantic retrieval penalized for not matching
  section boundaries)
- What a trustworthy comparison requires (independent queries, independent relevance
  judgments, Cranfield/TREC standard)

---

## Causal chain

Rafia's explainer named the problem: evaluation coupling. The retrieval system and the
labels share the same PageIndex structure. Vector search retrieves semantically correct
content but scores lower because it does not align with section boundaries. The benchmark
measures two things simultaneously — real retrieval improvement plus structural advantage.

This is the same class of problem as test-collection bias in the Cranfield/TREC tradition:
relevance judgments must be independent of the retrieval system being evaluated. The README
now documents this so any future user of the benchmark understands its scope.

---

## What was NOT changed

The benchmark code itself was not changed. The `precision@3` metric and the evaluation
pipeline remain intact. The commit adds a documentation caveat, not a code fix. The full
fix — a held-out human-labeled query set with independent relevance judgments — would
require collecting 30-50 queries from real user information needs and re-running the
evaluation, which is future work beyond Day 4 scope.
