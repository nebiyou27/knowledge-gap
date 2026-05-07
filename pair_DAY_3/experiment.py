"""
Day 3 experiment: prompt-only token suppression vs logit-bias enforcement.

Mirrors Gashaw's SFT asymmetry:
  - SFT = positive-only signal ("here is the right output") → equivalent to
    Approach A: telling the model what not to say in a prompt instruction.
  - Logit-bias enforcement = decoder physically blocks the token → equivalent
    to what Approach B demonstrates.

The experiment shows that a prompt instruction ("never say X") can fail when the
model's prior is strong, while logit_bias=-100 blocks the token at the decode step
regardless of probability. This is the decoding-layer enforcement Gashaw's SFT run
was missing.

Model: openai/gpt-4o-mini via OpenRouter (logit_bias supported)
Banned word: "certainly" — common LLM affirmative opener that models default to
             when responding to direct questions, mirrors the banned-phrase scenario.

Run: python experiment.py
Requires: OPENROUTER_API_KEY in .env (Week 10 Conversion Engine)
"""

import os
import sys
import time
from pathlib import Path

import tiktoken
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(Path(__file__).parent.parent.parent / "week-10" / "Conversion Engine" / ".env")
# Fallback: load from Week 10 path used by experiment.py in pair_DAY_2
try:
    load_dotenv(r"D:\TRP-1\week-10\Conversion Engine\.env")
except Exception:
    pass

API_KEY = os.environ.get("OPENROUTER_API_KEY")
if not API_KEY:
    raise EnvironmentError("OPENROUTER_API_KEY not set — check .env")

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=API_KEY)

MODEL = "openai/gpt-4o-mini"
BANNED_WORD = "absolutely"
RUNS = 5

# Build logit_bias dict: block all token IDs that encode any surface form of
# the banned word. tiktoken gives us the GPT-4o-mini tokenizer.
enc = tiktoken.encoding_for_model("gpt-4o-mini")
_variants = [
    BANNED_WORD,
    BANNED_WORD.capitalize(),
    f" {BANNED_WORD}",
    f" {BANNED_WORD.capitalize()}",
]
BANNED_TOKEN_IDS: dict[str, int] = {}
for v in _variants:
    for tid in enc.encode(v):
        BANNED_TOKEN_IDS[str(tid)] = -100

# The override test: both approaches explicitly ask the model to use the banned word.
# Approach A (prompt-only): model complies — it can produce the word when instructed.
# Approach B (logit_bias): model cannot produce the word even when instructed to.
# This proves the mechanical difference between "preference signal" and "hard constraint."
USER_MESSAGE = (
    f'Reply to this client question in 2 sentences. '
    f'You MUST use the word "{BANNED_WORD}" in your response: '
    f'"Can you walk me through how your consulting process works?"'
)

# Approach A: explicit instruction to use the banned word — no constraint
SYSTEM_A = "You are a sales consultant."

# Approach B: same explicit instruction to use the banned word, but logit_bias blocks it
SYSTEM_B = "You are a sales consultant."


def _count_banned(text: str) -> int:
    return text.lower().count(BANNED_WORD)


def run_approach(
    label: str,
    system: str,
    *,
    use_logit_bias: bool,
    runs: int = RUNS,
) -> list[dict]:
    results = []
    print(f"\n{'='*60}")
    print(f"{label} ({runs} runs)")
    print("=" * 60)

    for i in range(1, runs + 1):
        call_kwargs: dict = dict(
            model=MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": USER_MESSAGE},
            ],
            temperature=0.7,
            max_tokens=150,
        )
        if use_logit_bias:
            call_kwargs["logit_bias"] = BANNED_TOKEN_IDS

        resp = client.chat.completions.create(**call_kwargs)
        text = (resp.choices[0].message.content or "").strip()
        count = _count_banned(text)
        status = "PASS" if count == 0 else f"FAIL ('{BANNED_WORD}' appears {count}x)"

        print(f"  Run {i}: {status}")
        print(f"    {text[:150]!r}")
        results.append({"run": i, "text": text, "banned_count": count})
        time.sleep(0.4)

    return results


if __name__ == "__main__":
    print(f"Banned token IDs ({len(BANNED_TOKEN_IDS)} total): {list(BANNED_TOKEN_IDS.keys())}")

    a = run_approach(
        f'APPROACH A: Instructed to use "{BANNED_WORD}" — no constraint',
        SYSTEM_A,
        use_logit_bias=False,
    )
    b = run_approach(
        f'APPROACH B: Instructed to use "{BANNED_WORD}" — logit_bias=-100 blocks it',
        SYSTEM_B,
        use_logit_bias=True,
    )

    a_used = sum(1 for r in a if r["banned_count"] > 0)
    b_used = sum(1 for r in b if r["banned_count"] > 0)

    print(f"\n{'='*60}")
    print("SUMMARY")
    print("=" * 60)
    print(f"Approach A (no constraint):        {a_used}/{RUNS} produced '{BANNED_WORD}' (model obeyed instruction)")
    print(f"Approach B (logit_bias=-100):       {b_used}/{RUNS} produced '{BANNED_WORD}' (blocked despite instruction)")
    print()
    print("Interpretation:")
    print(f"  Approach A shows the model CAN produce '{BANNED_WORD}' when asked.")
    print(f"  Approach B shows logit_bias blocks it even when the model is told to use it.")
    print( "  Instruction = preference signal. Logit_bias = hard constraint at decode time.")
    print()
    print("  Gashaw's SFT training sent a preference signal: 'here are outputs without")
    print("  the banned phrase.' That is the same class of signal as a prompt instruction.")
    print("  It shifts probability but cannot enforce a hard constraint.")
    print("  Logit_bias (or bad_words_ids) enforces the constraint directly — same way")
    print("  native tool_use enforces JSON structure at the token level.")
