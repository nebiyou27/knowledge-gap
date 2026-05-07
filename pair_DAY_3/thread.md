# LinkedIn Thread — Day 3
**Author:** Nebiyou Abebe
**Topic:** Training and post-training mechanics — why LoRA learned one behavior and not another

---

**Post 1**

My partner fine-tuned a LoRA adapter on 221 training examples.

Two behaviors were in the data: write shorter answers, and never use a banned phrase.

After training — shorter answers: yes. Banned phrase: still there, Delta A = 0.00.

Same data. Same adapter. One behavior transferred. One didn't. Here's why.

---

**Post 2**

First, the rank question. LoRA adds a low-rank update (B×A, rank r) to a frozen weight
matrix. That limits which directions the adapter can move the weights — but it doesn't
categorically block certain behaviors.

Both length reduction and token suppression are, in principle, expressible by changing logits.

The difference is not what LoRA can represent. It's what the training signal can teach.

---

**Post 3**

Length reduction is a broad distributional shift.

If many target answers are short, SFT repeatedly rewards early stopping and fewer elaborative
tokens. Dense signal, consistent direction, many positions across many examples.

The model doesn't need a precise rule. It just needs to become more willing to stop sooner.
That's exactly what positive-only imitation is good at.

---

**Post 4**

Banned-token suppression is a different class of problem.

It's not "sound different overall." It's "when this exact token becomes attractive, don't
choose it." Sparse, local, context-sensitive.

SFT's cross-entropy loss has no direct mechanism for this. ORPO's own pilot study showed
that fine-tuning on chosen responses alone raised the log-probability of both chosen AND
rejected responses together.

SFT learned what the answer should look like. It never learned what it shouldn't contain.

---

**Post 5**

I tested this mechanically — 5 trials of each approach using gpt-4o-mini via OpenRouter.

Both approaches included an explicit instruction: "you MUST use the word 'absolutely'."

| Approach | Produced banned word | What happened |
|---|---|---|
| No constraint | 5/5 | Model obeyed — "Absolutely, our consulting process..." |
| logit_bias = −100 | 0/5 | Blocked — "Certainly!" and "Of course!" every run |

Approach B was *told* to use the word. It still couldn't produce it.

That's the difference between a preference signal and a hard constraint at the decode step.
Gashaw's SFT training sent a preference signal. His evaluation needed a hard constraint.

---

**Post 6**

Full explainer with sources: https://medium.com/p/821b9c233dd8

Sources:
- Hu et al. (2021) LoRA — arxiv.org/abs/2106.09685
- Hong et al. (2024) ORPO — arxiv.org/abs/2403.07691
- Welleck et al. (2019) Unlikelihood Training — arxiv.org/abs/1908.04319

Week 12 · 10 Academy TRP1 · Knowledge Gap Formulation
