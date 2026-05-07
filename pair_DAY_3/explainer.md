# Why LoRA Learned "Be Shorter" but Not "Never Say This Word"
**Author:** Nebiyou Abebe (answering Gashaw Bekele's question)
**Date:** 2026-05-07

---

## Gashaw's question in plain English

Gashaw fine-tuned a small LoRA adapter on 221 supervised examples. Two desired behaviors
were present in those examples: make answers shorter, and avoid a banned phrase. After
training, the model clearly became shorter (−18%, from 256 to 210 words), but it did not
reduce use of the banned phrase at all — Delta A = 0.00 across all three conditions. The
question is whether that failure came from LoRA's low-rank structure itself, or from the
kind of training signal SFT provides.

---

## Short answer

The stronger explanation is **objective mismatch, not a hard rank limit.** A LoRA adapter
adds a low-rank update to a frozen weight matrix, so it is capacity-limited. But nothing in
the LoRA formulation says "length changes are representable while token suppression is
impossible." The more important issue is that plain SFT increases the probability of chosen
outputs but does not directly penalize rejected tokens. ORPO and unlikelihood-style objectives
add an explicit negative signal. Decoding-time controls can hard-ban tokens altogether.

---

## What a low-rank update can and cannot change

In LoRA (Hu et al., 2021), a frozen weight matrix W₀ is adapted by adding a trainable
low-rank update BA, where the rank of BA is at most r. The adapter can only move W₀ in
r directions — not arbitrarily across the full parameter space. That is a **capacity
constraint, not a categorical ban on certain kinds of behavior.**

The LoRA paper is explicit: as rank increases, LoRA approaches the expressiveness of full
fine-tuning. The paper also reports that many downstream updates have low intrinsic rank,
which is why small-rank adapters often work well. So the right framing is not "can LoRA only
learn style but not suppression?" It is: given this rank, data, and loss, **which behaviors
get the clearest gradient signal?**

Length reduction and token suppression can both, in principle, be expressed by changing
logits. The difference is how easy they are to learn from the available supervision.

---

## Why length reduction transfers easily

"Be shorter" is a broad distributional preference. If many target answers are concise, SFT
repeatedly rewards continuations that stop earlier and place more probability mass on short
completions. That signal is **dense and consistent** across many training examples: lots of
tokens, lots of positions, same general direction.

As ORPO (Hong et al., 2024) notes, SFT's standard causal language-modeling objective pushes
probability toward the reference continuation at every token position. A global brevity habit
fits that mechanism well — the model does not need a precise context-conditional rule for one
lexical item. It mainly needs to become more willing to end sooner or elaborate less.

---

## Why token suppression is a different class of problem

Banned-token suppression is much more specific. It is not "sound a bit different overall."
It is "when this exact token becomes attractive in context, do not choose it." That is a
**sparse, local, context-sensitive constraint.**

This is exactly where plain SFT is weak. ORPO's analysis states that cross-entropy gives no
direct penalty for non-answer tokens and no direct mechanism for penalizing rejected
responses. In their pilot study, fine-tuning on chosen responses alone **increased the
log-probabilities of both chosen and rejected responses together.** That is the key fact for
Gashaw's case: SFT can learn what the preferred answer looks like while still leaving an
unwanted token too likely — especially when that token is already salient from the prompt or
base model.

Welleck et al. (2019) make the same point from a different direction: likelihood training
alone can assign too much probability to undesirable outputs because the model never receives
a gradient signal that explicitly lowers the probability of unwanted tokens.

So the asymmetry makes sense. "Be shorter" is a many-example, many-token trend. "Never say
this word" is a hard negative constraint. Those are not equally well served by positive-only
imitation.

---

## Why SFT is the wrong objective for hard suppression

If the requirement is truly hard — not "prefer alternatives" but "do not emit this token" —
then SFT alone is usually the wrong tool. ORPO was proposed precisely because SFT lacks an
explicit negative signal; its odds-ratio term adds pressure against rejected responses during
the same training phase. Unlikelihood training (Welleck et al., 2019) takes a similar
approach: add an objective that explicitly lowers probability on unwanted tokens or sequences
alongside the standard likelihood term.

**The primary suspect is the training objective, not LoRA's subspace capacity.** Rank may
still matter at the margin — especially at very low rank or for a genuinely complex
suppression rule — but Gashaw's result does not require a "LoRA cannot represent suppression"
explanation. The experiment below confirms this mechanically.

---

## Concrete demonstration — experiment results

To prove the difference between a preference signal and a hard constraint at the decode layer,
I ran 5 trials of each approach using `openai/gpt-4o-mini` via OpenRouter. Both approaches
used an identical user message that explicitly instructed the model to use the word
"absolutely."

| Approach | Produced banned word | What happened |
|---|---|---|
| No constraint (baseline) | 5/5 | Model obeyed the instruction — "Absolutely, our consulting process..." every run |
| logit_bias = −100 | 0/5 | Token blocked at decode step — model substituted "Certainly!" and "Of course!" |

The override test is the key: Approach B was *instructed* to use the word and still could not
produce it. This is not a probability shift — it is a physical block at the token sampling
step, applied after all logits are computed.

```python
import tiktoken
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=API_KEY)
enc = tiktoken.encoding_for_model("gpt-4o-mini")

banned_word = "absolutely"
blocked = {}
for form in [banned_word, banned_word.capitalize(),
             f" {banned_word}", f" {banned_word.capitalize()}"]:
    for tok_id in enc.encode(form):
        blocked[str(tok_id)] = -100  # -100 effectively sets log-prob to -inf

resp = client.chat.completions.create(
    model="openai/gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a sales consultant."},
        {"role": "user", "content": f'You MUST use the word "{banned_word}". Reply in 2 sentences.'},
    ],
    logit_bias=blocked,   # instruction says USE it; logit_bias says CANNOT
    temperature=0.7,
    max_tokens=150,
)
# Output: "Certainly! Our consulting process begins with..."
# "absolutely" never appears despite the explicit instruction.
```

Gashaw's SFT training sent the same class of signal as a prompt instruction: "here are 221
examples of outputs without the banned phrase." That shifts probabilities. It does not block
the token. Logit_bias does the blocking directly — the same way `bad_words_ids` and
`NoBadWordsLogitsProcessor` do in HuggingFace generation.

---

## What works better

**For soft behavioral preference** (like length reduction): SFT is appropriate. The signal
is dense, consistent, and positive-only imitation is sufficient.

**For hard token suppression:**

1. **ORPO or DPO** — preference pairs where rejected responses contain the banned phrase.
   The odds-ratio term explicitly penalizes the rejected output, not just rewarding the
   chosen one.
2. **Unlikelihood training** — add a loss term that directly lowers probability on the
   banned token during training.
3. **Decoding-layer enforcement** — `logit_bias=-100` (OpenAI-compatible API),
   `bad_words_ids` or `NoBadWordsLogitsProcessor` (HuggingFace). The token is
   physically blocked at every generation step. No training required.

The production rule is: if the constraint must hold at runtime, enforce it where tokens are
chosen — not only where probabilities are nudged during training.

---

## Diagnostic experiments Gashaw should run next

**Minimum experiment to isolate objective vs rank:**

Hold rank fixed at r=16. Change only the objective:

1. SFT on chosen outputs only (current setup)
2. Same rank, same data, but ORPO with rejected responses that contain the banned phrase

If suppression appears in condition 2 without increasing rank, the bottleneck was objective,
not subspace capacity. As an immediate product-side control: add a decode-time ban
(`bad_words_ids`) and re-evaluate. If the banned phrase disappears there, you have confirmed
that inference-time enforcement solves the hard requirement regardless of what SFT learned.

**To isolate rank as a factor:**

Train at r=4, r=16, r=64 on identical data with the same SFT objective. If suppression
improves with rank, rank capacity is a contributing factor. If it does not, the objective is
the bottleneck regardless of rank.

---

## Adjacent concepts

**1. Intrinsic dimensionality of fine-tuning**
The LoRA paper shows that many downstream task updates have low intrinsic rank — meaning
a rank-r adapter can approximate full fine-tuning for many tasks. This is why r=16 is often
sufficient for style/length changes. Token suppression may sit in a higher-rank subspace
depending on how context-specific the suppression rule is.

**2. Logits processors in HuggingFace**
HuggingFace exposes `NoBadWordsLogitsProcessor`, `SuppressTokensLogitsProcessor`, and
`sequence_bias` — production-grade decoding controls that set specified token log-probabilities
to −inf at each generation step. These are the inference-time equivalent of what ORPO/
unlikelihood training tries to approximate through weight updates.

**3. The training/inference enforcement gap**
A recurring pattern across Days 2 and 3 of this pairing week: systems fail because they
assume a training-time signal (SFT, prompt instruction) will enforce a constraint that
actually requires an inference-time mechanism (constrained decoding, logit_bias, tool_choice).
The fix in both cases is to move enforcement to where tokens are chosen.

---

## Sources

Hu, E.J., Shen, Y., Wallis, P., Allen-Zhu, Z., Li, Y., Wang, S., Wang, L. and Chen, W.
(2021) 'LoRA: Low-rank adaptation of large language models', *arXiv preprint arXiv:2106.09685*.
Available at: https://arxiv.org/abs/2106.09685 (Accessed: 7 May 2026).

Hong, J., Lee, N. and Thorne, J. (2024) 'ORPO: Monolithic preference optimization without
reference model', *arXiv preprint arXiv:2403.07691*. Available at:
https://arxiv.org/abs/2403.07691 (Accessed: 7 May 2026).

Welleck, S., Kulikov, I., Roller, S., Dinan, E., Cho, K. and Weston, J. (2019) 'Neural text
generation with unlikelihood training', *arXiv preprint arXiv:1908.04319*. Available at:
https://arxiv.org/abs/1908.04319 (Accessed: 7 May 2026).

Hugging Face (2026) *Generation utilities — logits processors*. Hugging Face Documentation.
Available at: https://huggingface.co/docs/transformers/internal/generation_utils
(Accessed: 7 May 2026).

OpenAI (2026) *Create chat completion — logit_bias*. OpenAI Platform Documentation.
Available at: https://platform.openai.com/docs/api-reference/chat/create
(Accessed: 7 May 2026).
