# LinkedIn Thread — Day 4
**Author:** Nebiyou Abebe
**Topic:** LLM-as-a-judge biases — can you trust your evaluation result?

---

**Post 1**

A peer got p<0.0001 on his AI evaluation benchmark. Delta A = +0.263.

Statistically rock solid. But he never tested his judge for three known biases.

Here's why that matters — and what each bias actually does at the token level.

---

**Post 2**

First: 80% inter-rater agreement is not enough.

Zheng et al. (2023) showed strong LLM judges reach 80%+ agreement with humans.
But the same paper explicitly flags position bias, verbosity bias, and self-enhancement
bias as limitations.

Agreement answers: does the judge agree with humans overall?
Bias tests answer: does the verdict change when irrelevant setup features change?

Those are different validity checks.

---

**Post 3**

Position bias — the judge cares which slot the answer is in.

When a judge reads "Candidate A" and "Candidate B", slot identity enters the context.
The model has learned evaluation priors from training — "the first answer is usually
the reference." Its logits get nudged toward slot A before it has fully read the content.

Wang et al. (2023) showed GPT-4 preferred the first response in 60%+ of cases in some
settings — even when content was equivalent.

I ran a live 5-pair swap using gpt-4o-mini. slot_A_win_rate jumped from 0.20 to 0.60
when the outputs changed slots. That asymmetry is the signal.

---

**Post 4**

Length bias — the judge mistakes word count for quality.

Longer outputs contain more tokens that look like quality signals: polite framing,
rubric keywords, caveats, explanations. The judge attends to those tokens and becomes
more likely to emit "better", "more complete", or a higher score.

The cheap diagnostic: correlate output word count with judge score on existing data.
No API calls required.

I ran this on 50 judged outputs. No positive pattern — trained outputs were shorter
and still scored higher. Length bias is less visible here, but the live judge may
still behave differently.

---

**Post 5**

Self-preference bias — the judge favors outputs that sound like itself.

Every LLM has a learned distribution of what "good text" looks like. When a candidate
matches that distribution — same hedging style, safety language, formatting — it has
lower perplexity for the judge. Higher scores follow.

Using different model families for generation and judging reduces the worst case.
It does not eliminate it. Frontier models share overlapping post-training data and
prefer similar answer shapes. Familiarity is about style, not authorship.

---

**Post 6**

The honest framing for a strong but under-audited result:

"Delta A = +0.263 is a strong result under the current judge protocol. We have not
ruled out position, length, or self-preference bias as partial explanations. A
position-swap audit on 20+ pairs is the minimum before treating this as a fully
defensible model-quality gain."

Don't say the result is wrong. Say it needs one more audit step.

Full explainer + experiment code:
https://github.com/nebiyou27/knowledge-gap/blob/main/pair_DAY_4/explainer.md

Blog post: https://medium.com/p/d8f349ab17b2

Sources:
- Zheng et al. (2023) MT-Bench — arxiv.org/abs/2306.05685
- Wang et al. (2023) Large LLMs are not Fair Evaluators — arxiv.org/abs/2305.17926

Week 12 · 10 Academy TRP1 · Knowledge Gap Formulation
