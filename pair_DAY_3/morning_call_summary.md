# Morning Call Summary — Day 3
**Partners:** Nebiyou Abebe & Gashaw Bekele
**Topic:** Training and post-training mechanics

---

Nebiyou's original draft asked how to diagnose a directional but non-significant post-training
result. The question was grounded in a specific artifact: the Week 11 ORPO LoRA run on
Qwen3-0.6B, where the trained adapter lifted pass rate from 12% to 26% (+14pp, n=50, p=0.23).
The first version listed several competing hypotheses without prioritizing them: evaluation
sample size, preference-pair quality, epochs, ORPO objective fit, and training setup.

During sharpening, the question became a decision tree: first rule out evaluation sample size,
because statistical power can be computed without running new training; only then investigate
training-side causes. The final question asks for the minimum diagnostic experiment and the eval
size needed to detect a +14pp lift with 80% power.

Gashaw's question is grounded in a precise asymmetry from his Week 11 LoRA run
(`gashawbekele/tenacious-bench-lora-path-a`, r=16, α=16, Qwen2.5-0.5B-Instruct, 221 SFT
pairs). The adapter learned output length reduction (−18%, from 256 to 210 words) but did not
learn banned-phrase suppression (Delta A = 0.00 across all three conditions), even though both
behaviors appeared in the training pairs.

His question asks whether length reduction and token suppression are expressible by the same
kind of low-rank update, or whether suppressing a specific token requires a fundamentally
different mechanism than a rank-r LoRA adapter can reliably learn from SFT alone.

Both questions are now committed. Nebiyou's question targets statistical power and the decision
threshold for when a non-significant result should be attributed to evaluation design versus
training quality. Gashaw's question targets the representational capacity of low-rank updates
and whether LoRA can encode context-conditional token suppression through SFT alone.
