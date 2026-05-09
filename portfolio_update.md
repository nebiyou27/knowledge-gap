# Portfolio Update — Week 12 Grounding Commits
**Author:** Nebiyou Abebe
**Audience:** FDE hiring manager reviewing TRP1 portfolio
**Date:** 2026-05-09

---

## Summary

Four grounding commits made during Week 12 pair sessions improved existing artifacts from
Weeks 3, 10, and 11. Each commit resolves a specific technical gap found during peer exchange
— not a cleanup, not a refactor, but a targeted correction to something that was wrong or
missing. The changes are small by design: the point was to trace a knowledge gap back to a
real artifact and fix the exact thing that was broken.

---

## Commit 1 — Week 11 eval memo: mechanistic latency explanation

**File:** `reports/tenacious_bench_eval_memo.md`
**Commit:** `d1b8f24`

**Before:** The cost-Pareto section described the 183 ms trained/prompt-only latency
difference as a measurement result without explaining why it was small.

**After:** Rewrote the section with a mechanistic explanation: after `merge_and_unload()`,
the forward pass is identical to a standard dense forward pass — no adapter overhead. The
183 ms difference is attributable to weight-loading and memory allocation, not additional
compute. Decode is the dominant cost phase on a T4 GPU; prefill (where caching would help)
is a small fraction of total latency. Added a single-measurement caveat.

**Why it matters for an FDE portfolio:** The original memo reported a number. The revision
explains the number. Unexplained results in an evaluation memo invite the question "did you
get lucky?" A mechanistic explanation shows you understand the system, not just the output.

---

## Commit 2 — Week 11 eval memo: confirmed 100-task power analysis result

**File:** `reports/tenacious_bench_eval_memo.md`
**Commit:** `243e1cd`

**Before:** The statistical significance gate stated "requires 150–200 tasks for a reliable
significance test" — an estimate based on a preliminary power analysis.

**After:** Updated to reflect the confirmed 100-task result: Delta B +18 pp, CI [+2%, +36%],
CI excludes zero. The significance gate now cites the actual experiment rather than a
projection. The 100-task run was the diagnostic experiment from Day 3 pairing: Cohen's h for
a 12%→26% lift is 0.3627, requiring ~60 tasks at 80% power two-tailed. 100 tasks gave 95.2%
power assuming the observed effect size.

**Why it matters:** An eval memo that replaces a projection with a confirmed result is a more
honest document. Any practitioner reading the original would have been misled about the
minimum viable eval size. The correction matters for anyone replicating or extending the work.

---

## Commit 3 — Week 10 AI maturity rubric: removed mixed signal in Output Format

**File:** `D:\TRP-1\week-10\Conversion Engine\agent\prompts\ai_maturity_rubric.md`
**Commit:** `grounding_commit.md` in `pair_DAY_2/`

**Before:** The Output Format example used a markdown code fence to display the required JSON
structure, while the instruction text below it said "do not include markdown fencing in your
response." The model received two conflicting learned behaviors simultaneously.

**After:** Removed the markdown fence from the Output Format example. The example now shows
raw JSON without fencing, which is consistent with the instruction.

**Why it matters:** This was the root cause of the 43.3% invalid JSON failure rate in Week
10's Qwen3 calls. The bug was not in the model, not in the API, not in the parsing logic — it
was a one-line inconsistency in a prompt template. Identifying prompt-level root causes and
fixing them at the source is a core FDE skill. The fix cost one line; the diagnosis required
understanding how a model learns format compliance probabilistically from training data and
how mixed signals resolve at inference time.

---

## Commit 4 — Week 3 Document Refinery: evaluation coupling disclosure

**File:** `D:\TRP-1\Week-3\document-refinery\README.md`
**Commit:** `e9b080c`

**Before:** The Batch Phase 3 evaluation section described the `precision@3` comparison
between PageIndex-assisted retrieval and baseline vector search without noting any limitation.

**After:** Added an evaluation limitation note explaining that the benchmark uses topics and
relevance labels auto-derived from PageIndex sections — the same structure used by the
PageIndex retrieval method. This creates evaluation coupling: the benchmark cannot distinguish
genuine retrieval improvement from structural alignment advantage. The note describes what a
trustworthy comparison requires (independent queries, independent relevance judgments,
Cranfield/TREC standard) and explicitly names this as future work.

**Why it matters:** A benchmark that documents its own limitations is a more honest instrument
than one that reports a metric without noting what it can and cannot prove. An FDE reviewing
a Week 3 result with no limitations note would have no way to know the comparison was
partially confounded. The addition makes the artifact usable — readers can now correctly scope
what the result means.

---

## What these four commits show together

Each commit targets a different class of correctness problem:

| Commit | Problem class | Artifact type |
|--------|--------------|---------------|
| 1 | Missing mechanistic explanation | Eval memo |
| 2 | Projection replaced by confirmed result | Eval memo |
| 3 | Root cause of failure in production pipeline | Prompt template |
| 4 | Undisclosed benchmark limitation | README |

None of these changes required building something new. They required finding the exact place in
an existing artifact where the gap lived and fixing it precisely. The skill being demonstrated
is not code output — it is the ability to trace a technical finding back to the artifact it
should change and make that change correctly.
