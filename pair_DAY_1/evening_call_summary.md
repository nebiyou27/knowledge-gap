# Evening Call Summary — Day 1
**Partners:** Natnael Alemseged & Nebiyou Abebe
**Format:** Async exchange

---

Natnael's explainer introduced the 3-way benchmark design (base vs unmerged vs merged) with repeated runs, which is the experiment that would confirm the mechanism rather than just explain it — the Week 11 ablation used only one run per system, so the 183 ms gap cannot be separated from noise without it. Working through Natnael's question forced precise thinking about provider availability: the first diagnostic for any caching question is whether the provider exposes caching for that specific model, not prefix structure or token count. For Natnael's stack (OpenRouter → Qwen3), caching is not available at all, which made the CFO memo claim unsubstantiated and removed any redesign path through prompt engineering. Both questions resolved at the same layer: prompt caching reduces prefill cost, merged LoRA does not change decode cost, and the real bottleneck in both systems is the decode phase — the part neither optimization touches.
