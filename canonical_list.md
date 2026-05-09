# Canonical Reading List — Week 12 Knowledge Gap
**Author:** Nebiyou Abebe
**Audience:** FDEs and ML practitioners working on LLM evaluation, training, and inference

---

## Papers

### Inference and caching

**Vaswani et al. (2017). Attention Is All You Need.**
arxiv.org/abs/1706.03762

The architectural foundation. Read sections 3.2 (scaled dot-product attention) and 3.3
(multi-head attention) to understand why KV caching is possible: the K and V matrices for a
fixed prefix can be computed once and reused. Everything about prompt caching, paged attention,
and decode-phase bottlenecks follows from this.

**Kwon et al. (2023). Efficient Memory Management for Large Language Model Serving with
PagedAttention.**
arxiv.org/abs/2309.06180

Explains the decode bottleneck mechanistically. Memory-bandwidth bound decode is why a
merged LoRA model runs at the same latency as the base model: once weights are in memory,
compute is not the ceiling — memory bandwidth is. Required reading before optimizing inference.

---

### Fine-tuning and adaptation

**Hu et al. (2022). LoRA: Low-Rank Adaptation of Large Language Models.**
arxiv.org/abs/2106.09685

The LoRA paper. Section 4 (method) and section 7 (why low-rank decomposition works) are
the core. The key result for practitioners: after `merge_and_unload()`, the forward pass is
identical to a standard dense forward pass. There is no adapter overhead at inference time.

**Hong et al. (2024). ORPO: Monolithic Preference Optimization without Reference Model.**
arxiv.org/abs/2403.07691

The training objective used in Week 11. The critical insight is in section 3: SFT's
cross-entropy loss raises log-probabilities of chosen outputs but simultaneously raises
log-probabilities of rejected outputs too (Figure 2 in the paper). This is the mechanism
behind LoRA behavioral asymmetry — behaviors that require penalizing rejected tokens
(banned-phrase suppression) cannot be learned by positive-only imitation.

**Welleck et al. (2019). Neural Text Generation with Unlikelihood Training.**
arxiv.org/abs/1908.04319

Complementary to ORPO. Explains the theoretical gap in MLE/cross-entropy: because the loss
maximizes log P(chosen), it implicitly allows P(rejected) to remain high. Unlikelihood
training adds an explicit penalty term. Read alongside ORPO to understand why preference
learning requires a negative signal component.

---

### Constrained decoding

**Willard & Louf (2023). Efficient Guided Generation for Large Language Models.**
arxiv.org/abs/2307.09702

The theoretical foundation for grammar-constrained decoding. Shows how a finite-state
machine over a JSON/regex grammar can be applied at each decode step to mask logits for
illegal next tokens — guaranteeing valid output regardless of what the model's raw
distribution would have produced. The basis for tools like Outlines and Guidance.

**Geng et al. (2023). Grammar-Constrained Decoding for Structured NLP Tasks without
Finetuning.**
EMNLP 2023. github.com/epfl-dlab/GCD

Applied counterpart to Willard & Louf. Shows constrained decoding producing valid structured
outputs on models that would otherwise hallucinate invalid syntax. Relevant when working at
enforcement layer 3 — constrained decoding is the only layer that guarantees valid output.

---

### Evaluation methodology

**Zheng et al. (2023). Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena.**
arxiv.org/abs/2306.05685

The most-cited LLM judge paper. Section 6 explicitly lists the limitations the paper's own
judge exhibits: position bias, verbosity bias, self-enhancement bias. 80%+ agreement with
humans is the headline result; the bias limitations are in the limitations section and are
often overlooked. Read both.

**Wang et al. (2023). Large Language Models are not Fair Evaluators.**
arxiv.org/abs/2305.17926

Documents position bias at scale: GPT-4 preferred the first response in 60%+ of cases in
some test conditions even when content was equivalent. Proposes calibration via multiple
position orderings. The minimum audit standard — position-swap on a sample of pairs — comes
from this work.

**Voorhees (2002). The Philosophy of Information Retrieval Evaluation.**
NIST. nist.gov/publications/philosophy-information-retrieval-evaluation

The Cranfield/TREC evaluation standard: relevance judgments must be independent of the
retrieval system being evaluated. Applies directly to any LLM pipeline that uses the same
knowledge structure to both organize content and generate evaluation labels. The independence
principle is what makes a held-out human-labeled query set the minimum fair fix for
evaluation coupling.

---

## Tools

**Unsloth + HuggingFace TRL**
unsloth.ai / huggingface.co/docs/trl

The training stack used in Week 11. Unsloth provides memory-efficient PEFT kernels; TRL
provides the SFT and ORPO trainers. On a T4 (16 GB VRAM), Qwen3-0.6B with LoRA r=8 fits
comfortably. Qwen3-1.7B is borderline — enable gradient checkpointing and use batch size 1.

**Outlines / Guidance**
github.com/outlines-dev/outlines / github.com/guidance-ai/guidance

Constrained decoding libraries. Outlines (Python) uses the FSM-masking approach from
Willard & Louf. Guidance allows interleaved control flow. Both guarantee valid JSON/schema
output from any model that allows logit access. Not available through standard OpenRouter
API calls — requires local inference or a compatible endpoint.

**OpenRouter**
openrouter.ai

Multi-model API gateway. Note: provider-side KV caching is only exposed for Anthropic and
OpenAI models routed through OpenRouter. For Qwen3, DeepSeek, Llama, and other open models,
there is no caching — each call pays full prefill cost. Check the model card on OpenRouter
before designing any caching-dependent architecture.

---

## Patterns worth keeping

**Static-before-dynamic prefix structure**
All cacheable static content (system prompt, knowledge base, rubric) must appear before
the cache breakpoint annotation (`"cache_control": {"type": "ephemeral"}`). Dynamic
fields (company name, user message, task ID) go after. This is the only structure that
enables provider-side KV cache hits.

**Three-layer enforcement taxonomy**
When debugging an LLM compliance failure (wrong format, banned token present, wrong structure):
1. Prompt instruction — probabilistic. Sends signal but cannot guarantee output.
2. Native tool_use / structured output — requires model and provider support. Check the model
   card before assuming this is available.
3. Constrained decoding — guaranteed valid output. Requires logit access and a local or
   compatible inference framework.
Identify which layer you are on before writing any fix.

**Power analysis before training diagnosis**
For any evaluation result with p > 0.05: compute Cohen's h (for proportions) or Cohen's d
(for means), look up the required n for 80% power, compare to your eval size. If underpowered,
rerun with a larger sample before investigating the training setup. The correct diagnostic
order is: rule out evaluation first, then model.

**Position-swap audit before publishing judge scores**
Run at minimum 10–20 output pairs through the judge twice — once in original order, once with
positions swapped. Compute flip_rate and slot_A_win_rate. A flip_rate above 0.10 or a
slot_A_win_rate above 0.60 indicates position bias that should be disclosed. This is a
30-minute audit that can save a result from being challenged at review.

**Evaluation coupling check**
Before publishing any retrieval or generation benchmark result: verify that the evaluation
labels (queries, relevance judgments, reference outputs) were generated independently of the
system being evaluated. If they share a source structure (same knowledge base, same model
family, same author), the benchmark may measure alignment rather than quality. The fix is
always some form of independent ground truth.
