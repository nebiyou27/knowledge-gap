# Signoff — Day 3
**Partners:** Nebiyou Abebe & Gashaw Bekele
**Date:** 2026-05-07

---

## Nebiyou signs off on Gashaw's question

**Question:** In my Week 11 ORPO LoRA run, the trained adapter reduced output length by 18%
but showed Delta A = 0.00 on banned-phrase suppression. Both behaviors were present in the
training data. Why did one transfer and the other not?

**Status: Resolved.**

The explainer covers: (1) LoRA's low-rank subspace is a capacity constraint, not a categorical
ban on certain behaviors — both length reduction and token suppression are representable in
principle; (2) the stronger explanation is objective mismatch — SFT's cross-entropy loss adds
probability mass to chosen outputs but never subtracts from rejected tokens; (3) ORPO's own
pilot study shows that fine-tuning on chosen responses alone raised log-probabilities of both
chosen AND rejected responses together; (4) length reduction transfers easily because it is a
dense, consistent, many-token signal — the model just needs to stop sooner; (5) banned-token
suppression is sparse, local, and context-sensitive — exactly what positive-only imitation
cannot enforce; (6) five-trial experiment confirming the mechanical difference: Approach A
(prompt instruction) produced the banned word 5/5 times when told to, Approach B
(logit_bias=−100) produced it 0/5 times even when explicitly instructed to.

**Gap-closure judgment: Closed.**

Before this explainer I assumed that if a behavior was demonstrated consistently in training
data, SFT would suppress it. I now understand that SFT can learn what an output should look
like while leaving an unwanted token too likely — because the loss has no direct mechanism for
penalizing rejected tokens. The fix for hard suppression is either an objective with an
explicit negative signal (ORPO with rejected pairs containing the banned phrase) or
inference-time enforcement (logit_bias, bad_words_ids). Preference signal and hard constraint
are not stronger and weaker versions of the same thing — they operate at different layers.

**Signed:** Nebiyou Abebe — 2026-05-07

---

## Gashaw signs off on Nebiyou's question

**Question:** In my Week 11 ORPO LoRA run on Qwen3-0.6B, the trained adapter lifted pass rate
from 12% to 26% (+14 pp, n=50), but the result was not statistically significant (p=0.23).
What is the minimum diagnostic experiment needed to determine whether this is mainly an
evaluation sample-size problem before blaming the training setup? Specifically, what eval size
would be needed to detect a +14 pp lift with 80% power?

**Status: Resolved.**

The explainer covers: (1) Cohen's h for the observed 12%→26% lift is h=0.3627; (2) required n
for 80% power is 48 one-tailed / 60 two-tailed — the original n=50 was right at the boundary;
(3) sensitivity analysis showing that if the true effect is smaller than observed (likely given
CI of −2% to +30%), required n could reach 163–276; (4) the minimum diagnostic experiment is
to run 100 tasks, which gives 95.2% power assuming the true effect is ~14 pp.

The 100-task run was executed. Result: Delta B (trained vs prompt-only same backbone) gave
**+18 pp, CI [+2%, +36%]** — the CI excludes zero. Verdict: sample-size was the problem, not
the training setup. The adapter learned. The remaining gap (Delta A: −6 pp vs Claude baseline,
not significant) is a capacity ceiling on a 0.6B model, not a training failure.

**Gap-closure judgment: Closed.**

Before this explainer I understood statistical non-significance as evidence that training
failed. I now understand it can equally mean the evaluation was underpowered — and that the
correct diagnostic order is: rule out sample size first, then investigate training. The 100-task
run ruled out sample size and confirmed the training signal is real.

**Signed:** Gashaw Bekele — 2026-05-07

---

## Joint confirmation

Both partners confirm that questions were sharpened before the morning deadline, explainers
were exchanged, experiments were run (logit_bias override test and 100-task power eval), and
results were discussed in the evening session. The grounding commit for Day 3 updates the
Week 11 eval memo to reflect 100 tasks and the confirmed power analysis result.
