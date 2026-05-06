"""
Day 2 experiment: prompt-instructed JSON vs native tool_use via OpenRouter.
Model: meta-llama/llama-3.1-8b-instruct

Replicates the P24 scenario from the Week 10 Conversion Engine:
- Approach A: ask for JSON in the prompt (what ai_maturity.py does)
- Approach B: native tool_use with schema enforcement

Run: python experiment.py
Requires: OPENROUTER_API_KEY in environment or .env file
"""

import json
import os
import time
from openai import OpenAI

# Load from Week 10 .env if present
try:
    from dotenv import load_dotenv
    load_dotenv(r"D:\TRP-1\week-10\Conversion Engine\.env")
except ImportError:
    pass

API_KEY = os.environ.get("OPENROUTER_API_KEY")
if not API_KEY:
    raise EnvironmentError("OPENROUTER_API_KEY not set")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY,
)

MODEL = "meta-llama/llama-3.1-8b-instruct"

# Same company claims as the Week 10 ai_maturity judge receives
USER_MESSAGE = """Company claims for AI maturity assessment:

- [verified] hiring_surge: Hiring 3 ML engineers and a Head of Data Science
- [corroborated] executive_commentary: CEO mentioned "AI-first roadmap" in TechCrunch interview
- [inferred] modern_data_ml_stack: Job post references Databricks and MLflow
"""

# ── Approach A: Prompt-instructed JSON (what ai_maturity.py does) ─────────────

SYSTEM_PROMPT_A = """You are an AI-maturity analyst. Score the company on a 0-3 scale.

Respond with ONLY a JSON object, no markdown fencing, no explanation:

```json
{
  "score": <integer 0-3>,
  "confidence": <float 0.0-1.0>,
  "justifications": [
    {
      "signal": "<signal_name>",
      "status": "<what was found>",
      "weight": "high" | "medium" | "low"
    }
  ]
}
```
"""

# ── Approach B: Native tool_use with schema enforcement ───────────────────────

TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "submit_ai_maturity_score",
        "description": "Submit the AI maturity score and justifications for a company.",
        "parameters": {
            "type": "object",
            "properties": {
                "score": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 3,
                    "description": "AI maturity score 0-3"
                },
                "confidence": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "description": "Confidence in the score"
                },
                "justifications": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "signal": {"type": "string"},
                            "status": {"type": "string"},
                            "weight": {"type": "string", "enum": ["high", "medium", "low"]}
                        },
                        "required": ["signal", "status", "weight"]
                    }
                }
            },
            "required": ["score", "confidence", "justifications"]
        }
    }
}

SYSTEM_PROMPT_B = "You are an AI-maturity analyst. Score the company using the submit_ai_maturity_score tool."


def run_approach_a(runs: int = 5) -> list[dict]:
    """Prompt-instructed JSON — same approach as ai_maturity.py."""
    results = []
    print(f"\n{'='*60}")
    print(f"APPROACH A: Prompt-instructed JSON ({runs} runs)")
    print('='*60)

    for i in range(runs):
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT_A},
                {"role": "user", "content": USER_MESSAGE},
            ],
            temperature=0.0,
            max_tokens=600,
        )
        raw = resp.choices[0].message.content
        try:
            # Replicate _extract_json from ai_maturity.py
            import re
            fenced = re.search(r"```(?:json)?\s*\n?(.*?)\n?\s*```", raw, re.DOTALL)
            text = fenced.group(1) if fenced else raw.strip()
            parsed = json.loads(text)
            status = "VALID"
            score = parsed.get("score", "?")
        except (json.JSONDecodeError, AttributeError):
            status = "P24 FAILURE"
            score = "abstain"

        results.append({"run": i+1, "status": status, "score": score, "raw": raw[:120]})
        print(f"  Run {i+1}: {status} | score={score}")
        print(f"    Raw[:120]: {raw[:120]!r}")
        time.sleep(0.5)

    return results


def run_approach_b(runs: int = 5) -> list[dict]:
    """Native tool_use — schema enforced by the inference layer."""
    results = []
    print(f"\n{'='*60}")
    print(f"APPROACH B: Native tool_use ({runs} runs)")
    print('='*60)

    for i in range(runs):
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT_B},
                {"role": "user", "content": USER_MESSAGE},
            ],
            tools=[TOOL_SCHEMA],
            tool_choice={"type": "function", "function": {"name": "submit_ai_maturity_score"}},
            temperature=0.0,
            max_tokens=600,
        )
        msg = resp.choices[0].message
        try:
            args = json.loads(msg.tool_calls[0].function.arguments)
            status = "VALID"
            score = args.get("score", "?")
        except (json.JSONDecodeError, IndexError, TypeError, AttributeError):
            status = "TOOL FAILURE"
            score = "abstain"

        results.append({"run": i+1, "status": status, "score": score})
        print(f"  Run {i+1}: {status} | score={score}")
        time.sleep(0.5)

    return results


if __name__ == "__main__":
    a_results = run_approach_a(runs=5)
    b_results = run_approach_b(runs=5)

    a_failures = sum(1 for r in a_results if r["status"] != "VALID")
    b_failures = sum(1 for r in b_results if r["status"] != "VALID")

    print(f"\n{'='*60}")
    print("SUMMARY")
    print('='*60)
    print(f"Approach A (prompt JSON): {a_failures}/5 failures")
    print(f"Approach B (tool_use):    {b_failures}/5 failures")
    print()
    print("Interpretation:")
    if b_failures < a_failures:
        print("  tool_use reduced failures — schema enforcement changed the inference path.")
    elif b_failures == a_failures == 0:
        print("  Both succeeded — this model is reliable enough that prompt JSON works.")
        print("  Try a smaller/weaker model or add the mixed-signal fence bug to see P24.")
    else:
        print("  Failures in both — failures moved to tool selection/argument layer.")
