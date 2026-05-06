# Morning Call Summary — Day 2

**Partners:** Nebiyou Abebe & Addisu Taye  
**Topic:** Agent and tool-use internals

---

Addisu's original question focused on observable tool-selection failures in his Week 10 Conversion Engine: wrong tool calls, skipped tools, and cases where the agent continued in natural language even when a tool was available. During the call, we sharpened it toward the token-level mechanics of how a model transitions from normal text generation into a structured tool call, and how the prompt, tool name, description, schema, and conversation history influence that choice.

Nebiyou's original question about P24 was already grounded in a specific measured failure rate: 43.3% invalid JSON in tau2 thinking-model runs. Addisu asked for the concrete implementation details before answering it: the prompt instruction, the parser/validator logic, and examples of malformed outputs. After reviewing `agent/judgment/ai_maturity.py` and `agent/prompts/ai_maturity_rubric.md`, we found a key mixed signal: the prompt says "no markdown fencing," but the example immediately below uses a markdown-fenced JSON block.

Both final questions are now committed. Addisu's question asks how function-calling works at the token level when an agent chooses, skips, or misuses a tool. Nebiyou's question asks why prompt-instructed JSON was fragile in P24 and whether native `tool_use`, structured outputs, or constrained decoding would have mechanically prevented the failure or simply moved it to another layer.
