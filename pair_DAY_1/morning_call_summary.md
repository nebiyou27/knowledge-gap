# Morning Call Summary — Day 1
**Partners:** Nebiyou Abebe & Natnael
**Format:** Async exchange (question delivered at 4:00 PM, sharpening via DM)

---

## What Was Ambiguous in the Original Draft

Nebiyou's original draft asked how inference decomposes into prefill and decode phases for a
0.6B model. The question was technically valid but generic — it could apply to any model without
reference to any specific observation or artifact. It did not name what was surprising or why
the gap mattered to existing work.

## How the Question Was Sharpened

The key interrogation was: "You have actual latency numbers from your own ablation — why are you
asking a textbook question instead of asking about the surprising thing in your data?"

That reframe shifted the question from "explain prefill/decode" to "explain why 183 ms separates
two systems that should differ more." The artifact pointer was made explicit (the cost-Pareto
section of the eval memo) and the deployment consequence was named (the 18,000 ms gate).

## What the Final Question Is

Why does merging a LoRA adapter into a base model add virtually no per-task latency (~183 ms on
a T4 GPU), and where does the dominant 14,000 ms actually go during autoregressive generation?
The answer must be specific enough to rewrite the cost-Pareto section of the Week 11 eval memo
with a real mechanistic explanation.

## Partner Confirmation

Natnael confirmed the sharpened question is unambiguous and resolvable in one explainer.
