# Evening Call Summary — Day 2
**Partners:** Nebiyou Abebe & Addisu Taye
**Format:** Async exchange

---

Addisu's explainer identified that the P24 failure happened before parsing — the model never committed to structured output because prompt-only JSON generation leaves all tokens available, including prose, and thinking models are especially prone to deliberating in prose once they start generating. He traced the dominant cause to the contradiction in the rubric prompt: "no markdown fencing" as an instruction paired with a fenced example as a demonstration, a mixed signal that competing training patterns amplify. The load-bearing distinction is that prompting shifts probabilities while constrained decoding changes the allowed token set — mechanically different enforcement levels, not just stronger and weaker versions of the same thing. Both questions resolved at the same layer: the system expected deterministic machine-readable structure from an unconstrained probabilistic generator, and the fix is architectural — native structured outputs or constrained decoding upstream, with the parser as a fallback rather than the primary enforcement mechanism.
