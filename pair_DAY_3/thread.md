# LinkedIn Thread — Day 3
**Author:** Nebiyou Abebe
**Topic:** Training mechanics — why fine-tuning learned one behavior and completely missed another

---

**Post 1**

My partner fine-tuned a LoRA adapter on 221 examples.

Two behaviors were in the training data:
→ Write shorter answers
→ Never use a specific banned phrase

After training:
✓ Output length dropped 18%
✗ Banned phrase still there. Delta A = 0.00.

Same model. Same data. Same training run. One behavior transferred perfectly. The other didn't move at all.

I spent a day figuring out exactly why.

---

**Post 2**

First instinct: "LoRA's low-rank structure can't represent token suppression."

That's wrong.

LoRA adds a low-rank update (rank r) to frozen weight matrices. It's capacity-limited — but nothing in the formulation says "length changes are learnable, token suppression is not."

Both behaviors are expressible by changing logits. The real question is: which one gets a useful gradient signal from your loss function?

The answer is what changes everything.

---

**Post 3**

Length reduction is a dense, positive signal.

If your 221 training examples all have short answers, SFT rewards early stopping and lower elaboration across hundreds of token positions, across every example.

The model doesn't need a precise rule. It just needs to become more willing to stop sooner.
That's exactly what positive-only imitation does well.

---

**Post 4**

Banned-token suppression is a completely different problem.

It's not "sound a bit different overall."
It's "when this exact token becomes likely in context, don't pick it."

Sparse. Local. Context-sensitive.

SFT's cross-entropy loss has no mechanism for this.

ORPO's own pilot study showed something striking: fine-tuning on chosen responses alone raised the log-probability of BOTH chosen AND rejected responses at the same time.

SFT learned what the answer should look like.
It never learned what it must not contain.

---

**Post 5**

I tested this mechanically.

5 trials. Both conditions given an explicit instruction: "You MUST use the word 'absolutely'."

→ No constraint: 5/5 produced it. "Absolutely, our consulting process..."
→ logit_bias = −100: 0/5 produced it. "Certainly!" and "Of course!" every time.

Condition B was *told* to use the word. It physically could not.

That's the gap my partner's training hit.

His SFT training sent a preference signal: "here are 221 examples without the banned phrase." That shifts probabilities — it doesn't block the token.

logit_bias blocks at the decode step, after all probabilities are computed.
Preference signal and hard constraint are not the same mechanism. They don't even operate at the same layer.

---

**Post 6**

The practical rule:

If a behavior is a broad style preference (shorter, more formal, less verbose) → SFT handles it. The signal is dense and consistent.

If a behavior is a hard requirement (never say X, always include Y, always return valid JSON) → SFT alone is the wrong tool. You need either:
- ORPO/DPO with rejected pairs that contain the violation (explicit negative signal during training)
- Decode-time enforcement: logit_bias, bad_words_ids, constrained decoding (guaranteed at generation time)

My partner's immediate fix: add bad_words_ids to the generation pipeline. Token blocked at decode step. No retraining needed.

Full explainer + experiment code: https://medium.com/p/821b9c233dd8

Sources:
- Hong et al. (2024) ORPO — arxiv.org/abs/2403.07691
- Welleck et al. (2019) Unlikelihood Training — arxiv.org/abs/1908.04319
- Hu et al. (2021) LoRA — arxiv.org/abs/2106.09685

Week 12 · 10 Academy TRP1 · Knowledge Gap Formulation
