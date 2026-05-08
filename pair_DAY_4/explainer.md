# LLM-as-a-Judge Biases: Does Yakob's Lift Hold?
**Author:** Nebiyou Abebe (answering Yakob's question)
**Date:** 2026-05-08

---

## Yakob's question in plain English

Yakob has a Week 11 LLM-as-a-judge evaluation system. The judge reached at least 80%
inter-rater agreement, and the measured result was large: Delta A = +0.263 with p < 0.0001.
But the judge was not tested for three known biases: position bias, length bias, and
self-preference bias.

The question is not "is the system bad?" The question is narrower:

**Can we trust the measured lift as a model-quality gain, or could part of it be a judge artifact?**

---

## Short answer

The result is **promising but not fully defensible as-is**. High inter-rater agreement says
the judge is consistent with the reference labeling protocol. It does not prove the judge is
invariant to presentation order, output length, or model-family/style familiarity.

With Delta A = +0.263 and p < 0.0001, systematic judge bias probably does not need to explain
the entire lift to matter. If the better-scoring system was usually shown first, produced longer
answers, or used a style closer to the judge's preferred distribution, then part of the lift could
be inflated.

The minimum additional check is cheap:

1. Re-judge 5-10 paired examples with A/B order swapped and report score or winner flip rate.
2. On 10-50 existing judged samples, correlate output length with judge score.
3. If model lineage is available, stratify score deltas by generator family vs judge family.

If the order-swap flip rate is low and length-score correlation is small, Yakob can defend the
result much more confidently.

---

## Why 80% agreement is not enough

Zheng et al. (2023) found that strong LLM judges can reach over 80% agreement with human
preferences, roughly comparable to human-human agreement in their setting, but the same paper
explicitly flags position, verbosity, and self-enhancement biases as limitations. Wang et al.
(2023) go harder: they show that simply changing response order can change the apparent winner
and propose balanced position calibration as a mitigation.

So inter-rater agreement answers one question:

**Does the judge generally agree with humans or another labeler?**

It does not answer:

**Is the judge's measured Delta A robust to irrelevant changes in the evaluation setup?**

Those are different validity checks.

---

## 1. Position bias

**Precise definition**

Position bias is a systematic preference for the response shown in a particular slot, such as
"Assistant A" or "the first answer", independent of content quality.

**Token-level mechanism**

During judge inference, the model reads a prompt containing two candidates. The candidate labels,
ordering, separators, and nearby instruction tokens become part of the context. If the judge has
learned an evaluation prior like "the first answer is usually the reference" or if earlier text
receives more salient attention during comparison, the decoder's logits for tokens such as `A`,
`Assistant A`, `first`, or a higher score for candidate A become slightly more likely before the
model has fully grounded the decision in rubric evidence.

In practical terms, the judge is not consciously "cheating." It is completing an evaluation
pattern where slot identity becomes a feature.

**Cheapest observable diagnostic**

Take 5 already-scored pairs. Re-run the exact same judge prompt, but swap candidate order:

```text
Original: Candidate A = trained, Candidate B = baseline
Swapped:  Candidate A = baseline, Candidate B = trained
```

Then measure:

```text
flip_rate = pairs where the preferred underlying output changes / total swapped pairs
slot_bias_rate = pairs where the judge keeps choosing slot A or slot B after the swap
```

If the judge picks "A" before and after the swap, that is a position-bias red flag.

---

## 2. Length bias

**Precise definition**

Length bias is a systematic tendency to assign higher scores to longer outputs, even when the
extra length does not improve correctness, grounding, or usefulness. Zheng et al. call this
verbosity bias: LLM judges may favor longer, more detailed answers.

**Token-level mechanism**

Longer outputs contain more tokens that look like evidence of quality: connective phrases,
polite framing, caveats, explanations, examples, and rubric keywords. During judge inference,
those tokens increase lexical overlap with the rubric and give the model more surface cues to
attend to. The decoder then becomes more likely to emit tokens like `better`, `more detailed`,
`comprehensive`, `A`, or a higher numeric score.

This can happen even when the extra words are fluff. The judge may treat "more text" as "more
complete reasoning."

**Cheapest observable diagnostic**

No new API calls are required if judged outputs already exist. For 10 samples:

```text
words(candidate_output) vs judge_score
```

Report Pearson or Spearman correlation. Also compare mean length for pass vs fail:

```text
mean_words_passed - mean_words_failed
```

If longer outputs strongly correlate with higher scores, rerun a small controlled test by trimming
or length-normalizing a few outputs and re-judging.

The included `experiment.py` implements this cheap length screen against the Week 11 artifacts.

---

## 3. Self-preference bias

**Precise definition**

Self-preference bias is a judge's tendency to favor outputs produced by itself, its own model
family, or outputs with familiar style/policy patterns, beyond what human or gold judgments would
justify.

**Token-level mechanism**

The judge has a learned distribution over what "good assistant text" looks like. When a candidate
uses phrasing, structure, safety style, hedging, formatting, or reasoning patterns close to that
distribution, the candidate has lower surprise for the judge. Wataoka et al. (2024) connect
self-preference to familiarity measured by perplexity; Panickssery et al. (2024) show LLMs can
recognize and favor their own generations.

At inference time, this means familiar text activates quality-associated continuations. The judge
is more likely to produce tokens such as `clear`, `well-structured`, `aligned`, or a higher score
because the candidate resembles the judge's own preferred response manifold.

**Cheapest observable diagnostic**

Use metadata already logged in the benchmark:

```text
generator_family, judge_family, judge_score
```

Then compare:

```text
same_family_score_mean vs different_family_score_mean
```

If model lineage is not logged, use a cheaper proxy: manually tag 10 outputs by visible style
markers such as template shape, hedging style, chain-of-thought-like rationale, apology pattern,
or safety language, then check whether judge scores cluster by style rather than task success.

---

## Does cross-model judging eliminate self-preference?

No. It **partially mitigates** direct self-preference, but it does not eliminate style-familiarity
bias.

Using different model families prevents the most obvious failure mode: one model grading its exact
own outputs. That is why Week 11's judge-rotation memo is directionally right. But two mechanisms
remain:

1. **Shared post-training style:** Different frontier models are often trained on overlapping
   instruction-following, safety, and preference data. They can prefer similar answer shapes.
2. **Familiarity rather than authorship:** Wataoka et al. argue that judges may favor lower
   perplexity or more familiar text regardless of whether the judge literally generated it.

So cross-model judging is a useful control, not a proof of neutrality.

---

## Yakob's specific Delta A

Given:

```text
Delta A = +0.263
p < 0.0001
position order = unknown
output length delta = unknown
self-preference audit = not run
```

The result is **not invalid**, but it is **under-audited**. The low p-value says the measured
difference is unlikely under the statistical null for the recorded judge scores. It does not say
the judge scores are unbiased measurements of true quality.

The defensible wording is:

**"Delta A shows a large, statistically robust improvement under the current judge protocol, but
we have not ruled out position, length, or model-family/style bias as partial explanations."**

Do not say:

**"The trained model is definitely +0.263 better in true quality."**

That overclaims.

---

## Minimum check to make it defensible

The smallest defensible package is:

1. **Position audit:** Swap order on 5-10 pairs. Require no large slot preference and report
   flip rate.
2. **Length audit:** Correlate output word count with judge score on at least 10 samples.
3. **Lineage audit:** Confirm generator and judge family separation; if already separated, say
   this mitigates but does not eliminate self-preference.

If only one check can be run, run the **position swap** first. Wang et al. show order alone can
materially change LLM-judge outcomes, and the test is cheap.

---

## Position-swap audit Yakob should run next

I did not run a live position-swap here because the diagnostic requires extra judge API
calls against Yakob's actual LLM comparative judge — not a deterministic scorer. A
deterministic scorer evaluates each candidate independently against a rubric, so slot
order is irrelevant by design. Yakob's judge sees both candidates in one prompt and picks
a winner — that is exactly where position bias lives.

**Minimum audit — 5 pairs, ~10 API calls:**

```python
for task_id in five_sampled_task_ids:
    # Order 1: trained = slot A, baseline = slot B
    score_order1 = judge(prompt(slot_A=trained[task_id], slot_B=baseline[task_id]))

    # Order 2: baseline = slot A, trained = slot B
    score_order2 = judge(prompt(slot_A=baseline[task_id], slot_B=trained[task_id]))

    flipped = preferred_output(score_order1) != preferred_output(score_order2)
```

**What to report:**

```
flip_rate = flipped_pairs / total_pairs
slot_A_win_rate_order1 = times slot_A won when trained was in slot_A
slot_A_win_rate_order2 = times slot_A won when baseline was in slot_A
```

**Red flag:** If `slot_A_win_rate` is high in both orderings regardless of which output
is in slot A, the judge is preferring position over content. Wang et al. (2023) found
this pattern in GPT-4 — it preferred the first response in 60%+ of cases in some
settings even when the content was equivalent.

**Green flag:** flip_rate < 0.2 and slot_A_win_rates roughly equal across both orderings.

---

## Concrete demonstration: length-bias screen

I implemented the low-cost length diagnostic in `experiment.py`. It uses the existing Week 11
prediction files and deterministic scorer, so it requires no API calls.

The script reports:

```text
Pearson(words, score)
Spearman(words, score)
mean words for passed vs failed outputs
paired length deltas between trained and baselines
```

Actual local run on the Week 11 artifacts:

| Prediction file | n | Mean words | Mean score | Pass rate | Pearson words-vs-score | Spearman words-vs-score |
|---|---:|---:|---:|---:|---:|---:|
| trained | 50 | 81.74 | 0.9578 | 0.66 | -0.5098 | -0.2431 |
| prompt_only | 50 | 118.40 | 0.9283 | 0.48 | -0.5413 | -0.6066 |
| week10_baseline | 50 | 78.80 | 0.9710 | 0.72 | -0.0178 | 0.0075 |

Paired length deltas:

| Comparison | Paired n | Mean word delta |
|---|---:|---:|
| trained - prompt_only | 50 | -36.66 words |
| trained - week10_baseline | 50 | +2.94 words |

Interpretation rule:

If longer outputs are consistently higher scoring, length bias is a plausible confound. If the
correlation is weak or negative, this cheap screen does not find length bias, but a live LLM judge
audit is still needed for the actual judge.

Result from this screen: **no obvious positive length-bias pattern appears in the saved deterministic
artifacts.** The trained outputs are much shorter than prompt-only outputs, and longer outputs do
not receive higher local deterministic scores. This does not clear the live LLM judge, but it makes
length bias a less likely explanation from the saved artifacts alone.

---

## Practical answer to Yakob

Yakob can keep the result, but should downgrade the claim until the bias checks are run.

Best phrasing:

**"Delta A = +0.263, p < 0.0001 is a strong result under the current judge. However, because the
judge was not audited for position, length, or self-preference bias, systematic judge bias could
explain part of the lift. A small order-swap audit plus a length-score correlation check is the
minimum needed before treating the lift as a defensible model-quality gain."**

---

## Sources

See `sources.md` for Harvard-style references.
