# Evening Call Summary — Day 3
**Partners:** Nebiyou Abebe & Gashaw Bekele
**Date:** 2026-05-07

---

## What was resolved

**Nebiyou's question — sample size vs training problem:**
The 100-task power eval ran during the session. Delta B (trained vs prompt-only same backbone)
came back +18 pp, CI [+2%, +36%] — CI excludes zero. The question is answered: sample size
was the blocker. The training signal is real. The remaining gap (Delta A: −6 pp vs Claude
baseline) is a capacity ceiling on 0.6B, not a training failure.

**Gashaw's question — LoRA behavioral asymmetry:**
The explainer confirmed that objective mismatch (not rank limit) explains why length reduction
transferred and banned-phrase suppression did not. SFT raises log-probability of both chosen
and rejected responses. Length is a dense signal; suppression is sparse and local. The
logit_bias override experiment proved the mechanical difference: a preference signal shifts
probability, a decode-layer constraint blocks the token regardless of instruction.

---

## What Gashaw applied back to Week 11

After the session Gashaw made three changes to his Week 11 project based on the Day 3
explainers:

**1. Scoring bug fixed**
The banned-phrase scorer was reading from input context, not the model's response. Delta A
corrected from 0.000 to +0.070. The training signal was always there — the measurement was
wrong. This validates the explainer's argument: objective mismatch is primary, not rank limit.
SFT did partially suppress the phrase; the metric just couldn't see it.

**2. Decode-time enforcement added**
`build_bad_words_ids()` added to `scoring_evaluator.py`. This is the direct application of
the training/inference enforcement gap: SFT sends a preference signal, logit_bias / bad_words_ids
enforces a hard constraint at the token level. Expected impact: banned_phrase_check 0.33 → 1.00,
overall score 0.60 → ~0.79.

**3. Held-out set expanded (n=3 → n=17)**
Gashaw applied Nebiyou's power analysis to his own project. n=3 gives approximately 10% power —
effectively unmeasurable. Moving to n=17 enables a real measurement. This is the same diagnostic
order from the explainer: rule out sample size before interpreting results.

---

## What this confirms

Both gaps are closed. The clearest evidence: Gashaw didn't just say he understood — he shipped
three fixes. Each fix maps directly to one concept from the Day 3 explainers:

| Fix | Concept |
|-----|---------|
| Scoring bug | Measurement integrity before training conclusions |
| bad_words_ids | Training/inference enforcement gap |
| n=3 → n=17 | Power analysis — sample size before training blame |
