# Sources - Day 4
**Compiled by:** Nebiyou Abebe

---

## Papers

Zheng, L., Chiang, W.-L., Sheng, Y., Zhuang, S., Wu, Z., Zhuang, Y., Lin, Z., Li, Z., Li, D., Xing, E.P., Zhang, H., Gonzalez, J.E. and Stoica, I. (2023) 'Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena', *arXiv preprint arXiv:2306.05685*. Available at: https://arxiv.org/abs/2306.05685 (Accessed: 8 May 2026).

Wang, P., Li, L., Chen, L., Cai, Z., Zhu, D., Lin, B., Cao, Y., Liu, Q., Liu, T. and Sui, Z. (2023) 'Large Language Models are not Fair Evaluators', *arXiv preprint arXiv:2305.17926*. Available at: https://arxiv.org/abs/2305.17926 (Accessed: 8 May 2026).

Wataoka, K., Takahashi, T. and Ri, R. (2024) 'Self-Preference Bias in LLM-as-a-Judge', *arXiv preprint arXiv:2410.21819*. Available at: https://arxiv.org/abs/2410.21819 (Accessed: 8 May 2026).

Panickssery, A., Bowman, S.R. and Feng, S. (2024) 'LLM Evaluators Recognize and Favor Their Own Generations', *arXiv preprint arXiv:2404.13076*. Available at: https://arxiv.org/abs/2404.13076 (Accessed: 8 May 2026).

---

## Local Artifacts

Abebe, N. (2026) *Inter-Rater Agreement - Tenacious-Bench v0.1*. Local file: `D:\TRP-1\week-11\Sales Eval Bench\docs\inter_rater_agreement.md` (Accessed: 8 May 2026).

Abebe, N. (2026) *Ablation Summary 100*. Local file: `D:\TRP-1\week-11\Sales Eval Bench\reports\ablation_summary_100.json` (Accessed: 8 May 2026).

Abebe, N. (2026) *Judge Rotation and Preference Leakage*. Local file: `D:\TRP-1\week-11\Sales Eval Bench\docs\memos\judge_rotation_and_preference_leakage_v0.md` (Accessed: 8 May 2026).

---

## Experiments Implemented

`position_swap_live.py` implements a live 5-pair position-swap audit using `openai/gpt-4o-mini` as a comparative judge via OpenRouter. Each trained-vs-prompt-only pair is judged twice with candidate order reversed. Raw output is saved in `position_swap_results.json`. Result: 1/5 preferred-output flips, `slot_A_win_rate_order1=0.20`, `slot_A_win_rate_order2=0.60`, verdict ambiguous and requiring more pairs.

`experiment.py` implements the cheapest length-bias screen using existing Week 11 prediction artifacts. It scores each candidate with the local deterministic scorer, counts output words, and reports Pearson/Spearman correlations between length and score. This is not a substitute for a live LLM judge audit; it is a low-cost first diagnostic for whether the recorded result is obviously confounded by answer length.
