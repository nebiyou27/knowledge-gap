# Sources — Day 3
**Compiled by:** Nebiyou Abebe

---

## Papers

Hu, E.J., Shen, Y., Wallis, P., Allen-Zhu, Z., Li, Y., Wang, S., Wang, L. and Chen, W. (2021) 'LoRA: Low-rank adaptation of large language models', *arXiv preprint arXiv:2106.09685*. Available at: https://arxiv.org/abs/2106.09685 (Accessed: 7 May 2026).

Hong, J., Lee, N. and Thorne, J. (2024) 'ORPO: Monolithic preference optimization without reference model', *arXiv preprint arXiv:2403.07691*. Available at: https://arxiv.org/abs/2403.07691 (Accessed: 7 May 2026).

Welleck, S., Kulikov, I., Roller, S., Dinan, E., Cho, K. and Weston, J. (2019) 'Neural text generation with unlikelihood training', *arXiv preprint arXiv:1908.04319*. Available at: https://arxiv.org/abs/1908.04319 (Accessed: 7 May 2026).

---

## Primary Documentation

Hugging Face (2026) *Generation utilities — logits processors*. Hugging Face Documentation. Available at: https://huggingface.co/docs/transformers/internal/generation_utils (Accessed: 7 May 2026).

OpenAI (2026) *Create chat completion — logit_bias*. OpenAI Platform Documentation. Available at: https://platform.openai.com/docs/api-reference/chat/create (Accessed: 7 May 2026).

---

## Tool or Engineering Pattern Used

OpenRouter API (2026) *openai/gpt-4o-mini via OpenRouter gateway*. Available at: https://openrouter.ai (Accessed: 7 May 2026).

Five-trial override test comparing no-constraint generation (Approach A) versus logit_bias=−100 enforcement (Approach B) on a token suppression task. Both approaches used an identical user message explicitly instructing the model to produce the banned word "absolutely." Approach A: 5/5 produced the banned word (model obeyed the instruction). Approach B: 0/5 produced the banned word (token blocked at the decode step despite the instruction). Token IDs obtained via tiktoken for the gpt-4o-mini tokenizer, blocking all surface forms: "absolutely", "Absolutely", " absolutely", " Absolutely".
