"""
Live position-swap audit — LLM comparative judge.

Presents two candidate sales emails to gpt-4o-mini as a comparative judge.
Runs each pair twice (order swapped) and measures flip rate.

A flip = the judge changes its preferred output after the swap.
High flip_rate or persistently high slot_A_win_rate = position bias signal.

Run:
    python position_swap_live.py

Requires: OPENROUTER_API_KEY in D:\\TRP-1\\week-10\\Conversion Engine\\.env
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(Path(r"D:\TRP-1\week-10\Conversion Engine\.env"))

API_KEY = os.environ.get("OPENROUTER_API_KEY")
if not API_KEY:
    raise EnvironmentError("OPENROUTER_API_KEY not set — check .env")

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=API_KEY)
MODEL = "openai/gpt-4o-mini"

WEEK11_ROOT = Path(r"D:\TRP-1\week-11\Sales Eval Bench")
TRAINED_PATH = WEEK11_ROOT / "reports" / "trained_predictions_100.jsonl"
PROMPT_ONLY_PATH = WEEK11_ROOT / "reports" / "prompt_only_predictions_100.jsonl"
N_PAIRS = 5


def read_jsonl(path: Path) -> dict[str, dict]:
    rows = {}
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                row = json.loads(line)
                rows[row["task_id"]] = row
    return rows


def format_email(candidate: dict) -> str:
    subject = candidate.get("subject", "").strip()
    body = candidate.get("body", "").strip()
    if subject:
        return f"Subject: {subject}\n\n{body}"
    return body


def judge_prompt(email_a: str, email_b: str) -> str:
    return (
        "You are evaluating two sales email candidates. "
        "Judge which is better based on: professionalism, clarity, "
        "grounded claims, and a single clear next step. "
        "Reply with ONLY 'A' or 'B' — nothing else.\n\n"
        f"=== Candidate A ===\n{email_a}\n\n"
        f"=== Candidate B ===\n{email_b}\n\n"
        "Which is better? Reply A or B only:"
    )


def call_judge(email_a: str, email_b: str) -> str:
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": judge_prompt(email_a, email_b)}],
        temperature=0,
        max_tokens=5,
    )
    raw = (resp.choices[0].message.content or "").strip().upper()
    if "A" in raw:
        return "A"
    if "B" in raw:
        return "B"
    return "?"


def main() -> None:
    trained = read_jsonl(TRAINED_PATH)
    prompt_only = read_jsonl(PROMPT_ONLY_PATH)

    shared_ids = sorted(set(trained) & set(prompt_only))[:N_PAIRS]
    print(f"Running position-swap audit on {len(shared_ids)} pairs via {MODEL}\n")

    results = []
    flips = 0
    slot_a_wins_order1 = 0
    slot_a_wins_order2 = 0

    for task_id in shared_ids:
        t_email = format_email(trained[task_id]["candidate_output"])
        p_email = format_email(prompt_only[task_id]["candidate_output"])

        # Order 1: trained = A, prompt_only = B
        winner1 = call_judge(t_email, p_email)
        time.sleep(0.5)

        # Order 2: prompt_only = A, trained = B
        winner2 = call_judge(p_email, t_email)
        time.sleep(0.5)

        # Translate slot winners to underlying output winners
        # Order 1: A=trained, B=prompt_only
        preferred_order1 = "trained" if winner1 == "A" else "prompt_only"
        # Order 2: A=prompt_only, B=trained
        preferred_order2 = "prompt_only" if winner2 == "A" else "trained"

        flipped = preferred_order1 != preferred_order2
        if flipped:
            flips += 1
        if winner1 == "A":
            slot_a_wins_order1 += 1
        if winner2 == "A":
            slot_a_wins_order2 += 1

        print(f"  {task_id[:55]}")
        print(f"    Order1 (trained=A): judge picked {winner1} ->preferred={preferred_order1}")
        print(f"    Order2 (prompt_only=A): judge picked {winner2} ->preferred={preferred_order2}")
        print(f"    Flipped: {flipped}\n")

        results.append({
            "task_id": task_id,
            "order1_winner_slot": winner1,
            "order2_winner_slot": winner2,
            "preferred_order1": preferred_order1,
            "preferred_order2": preferred_order2,
            "flipped": flipped,
        })

    n = len(results)
    flip_rate = flips / n
    slot_a_rate1 = slot_a_wins_order1 / n
    slot_a_rate2 = slot_a_wins_order2 / n

    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  pairs tested:          {n}")
    print(f"  flips:                 {flips}")
    print(f"  flip_rate:             {flip_rate:.2f}")
    print(f"  slot_A_win_rate_order1 (trained=A):     {slot_a_rate1:.2f}")
    print(f"  slot_A_win_rate_order2 (prompt_only=A): {slot_a_rate2:.2f}")
    print()
    if flip_rate >= 0.4:
        verdict = "HIGH position bias signal — judge is changing preferred output based on slot."
    elif slot_a_rate1 > 0.7 and slot_a_rate2 > 0.7:
        verdict = "POSITION BIAS — judge consistently picks slot A regardless of content."
    elif flip_rate <= 0.2 and abs(slot_a_rate1 - slot_a_rate2) < 0.3:
        verdict = "Initial green flag — low flip rate and balanced slot preferences. Not a full clearance."
    else:
        verdict = "Ambiguous — run more pairs to confirm."
    print(f"  Verdict: {verdict}")

    output_path = Path(__file__).parent / "position_swap_results.json"
    with output_path.open("w", encoding="utf-8") as f:
        json.dump({
            "model": MODEL,
            "n_pairs": n,
            "flip_rate": round(flip_rate, 4),
            "slot_A_win_rate_order1_trained_as_A": round(slot_a_rate1, 4),
            "slot_A_win_rate_order2_prompt_only_as_A": round(slot_a_rate2, 4),
            "verdict": verdict,
            "pairs": results,
        }, f, indent=2)
    print(f"\n  Results saved to {output_path}")


if __name__ == "__main__":
    main()
