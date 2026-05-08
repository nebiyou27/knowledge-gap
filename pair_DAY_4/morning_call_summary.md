# Morning Call Summary — Day 4 (Evaluation and Statistics)

**Date:** 2026-05-08
**Triad:** Nebiyou Abebe, Yakob Dereje, Rafia Kedir
**Format:** Three-way morning call
**Prepared by:** Yakob Dereje | **Confirmed by:** Nebiyou & Rafia

---

Nebiyou presented his question on benchmark design bias —
specifically whether his precision@3 benchmark derived from
PageIndex sections inflates the measured PageIndex gain over
baseline vector search, and whether a held-out human-labeled
query set is the minimum fair validation standard.

Rafia presented her question on paired bootstrap testing —
specifically why paired bootstrap is the correct statistical
test for her ablation comparison rather than a paired t-test
or Wilcoxon signed-rank test, what p=0.189 means about the
null distribution of score differences across 59 held-out
tasks, and whether her 60/40 blended scoring formula
introduces systematic variance reduction that artificially
deflates test sensitivity.

Yakob presented his question on LLM-as-a-judge biases —
specifically whether his Delta A result of +0.263 (p<0.0001)
can be defended given that he never tested his judge for
position bias, length bias, or self-preference bias, and
whether cross-model judging between different Qwen families
eliminates or only partially mitigates self-preference bias.

All three questions were explained clearly and confirmed
unambiguous by all partners — each question is grounded in
a specific artifact from the asker's Week 10 or 11 repository.

Questions committed final by end of call.
