# Grounding Commit — Day 1
**File edited:** `reports/tenacious_bench_eval_memo.md` (Week 11 Sales Eval Bench)
**Section:** Cost Per Task — Production Implication paragraph
**Commit message:** `docs: rewrite cost-Pareto section with inference-phase mechanistic explanation`

---

## What was changed

The "Production implication" paragraph in the Cost Per Task section previously read:

> "The latency concern from the stub run (+79%) does not exist in live inference. The adapter
> merge-and-unload is a one-time cost at load time; per-task inference is essentially identical
> between trained and prompt-only modes. The latency deployment gate (18,000 ms) is already
> met by both systems."

This is factually correct but unsupported — it names the observation without explaining the
mechanism. Any reviewer can ask "why is inference essentially identical?" and the memo has no
answer.

The paragraph was rewritten to state:

1. Autoregressive decode on a T4 GPU is memory-bandwidth bound: each generated token requires
   loading the full set of model weights from HBM, and the GPU stalls waiting for weight loads
   rather than performing arithmetic.

2. At Qwen3-0.6B scale with ~300 output tokens on a 200-token input, approximately 13–14 s of
   the 14,000 ms total is decode-phase memory-bandwidth latency. Prefill on a 200-token input
   accounts for a few hundred milliseconds at most.

3. `merge_and_unload()` folds the LoRA A and B matrices into the base weights via
   W_merged = W_base + (α/r) × B·A, producing a merged weight matrix with the same shape as
   the base. The per-token memory-bandwidth load profile is therefore unchanged — the adapter
   adds no extra weight traffic per decode step after merge.

4. The 183 ms difference (+1.3%) is within normal run-to-run variance for a shared Colab T4
   (thermal throttling, shared GPU tenancy, HBM pressure from concurrent jobs) and is not
   attributable to adapter overhead.

A second commit (`docs: add single-measurement caveat to 183 ms latency claim`) added an
explicit caveat that each system was measured once — no mean ± std across runs. The variance
claim is an inference from known T4 noise characteristics, not a measured fact. A rigorous
comparison would require ≥5 runs per system. This gap was identified by Natnael's clarification
question #2 during the pair exchange.

## Why this improves the artifact

The original paragraph makes a claim the memo cannot substantiate. The rewritten paragraph
names the mechanism (memory-bandwidth bound decode, identical weight shape post-merge) in a
way that would survive a technical review challenge. The single-measurement caveat adds honesty
about the strength of the variance inference.

This is the gap identified in the Week 12 Day 1 question: the cost-Pareto section reported
numbers it could not explain. The two grounding commits close that gap.
