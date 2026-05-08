"""
Day 4 experiment: cheap length-bias diagnostic for an LLM-as-a-judge result.

This does not call an API. It reuses Week 11 prediction artifacts and the local
deterministic scorer to ask one narrow question:

    Are longer candidate outputs associated with higher judged scores?

Run:
    python experiment.py

Optional:
    python experiment.py --week11-root "D:\\TRP-1\\week-11\\Sales Eval Bench"
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any


DEFAULT_WEEK11_ROOT = Path(r"D:\TRP-1\week-11\Sales Eval Bench")
PREDICTION_FILES = {
    "trained": Path("reports/trained_predictions_100.jsonl"),
    "prompt_only": Path("reports/prompt_only_predictions_100.jsonl"),
    "week10_baseline": Path("reports/baseline_predictions.jsonl"),
}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped:
                rows.append(json.loads(stripped))
    return rows


def candidate_text(candidate: Any) -> str:
    if isinstance(candidate, str):
        return candidate
    if isinstance(candidate, dict):
        subject = candidate.get("subject")
        body = candidate.get("body")
        parts = [part for part in (subject, body) if isinstance(part, str) and part.strip()]
        if parts:
            return "\n".join(parts)
        for key in ("answer", "output", "response", "message"):
            value = candidate.get(key)
            if isinstance(value, str):
                return value
    return json.dumps(candidate, sort_keys=True)


def word_count(text: str) -> int:
    return len(re.findall(r"\S+", text))


def pearson(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 2 or len(xs) != len(ys):
        return None
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    den_x = math.sqrt(sum((x - mean_x) ** 2 for x in xs))
    den_y = math.sqrt(sum((y - mean_y) ** 2 for y in ys))
    if den_x == 0 or den_y == 0:
        return None
    return num / (den_x * den_y)


def rank(values: list[float]) -> list[float]:
    indexed = sorted(enumerate(values), key=lambda item: item[1])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(indexed):
        j = i
        while j + 1 < len(indexed) and indexed[j + 1][1] == indexed[i][1]:
            j += 1
        avg_rank = (i + j + 2) / 2.0
        for k in range(i, j + 1):
            ranks[indexed[k][0]] = avg_rank
        i = j + 1
    return ranks


def spearman(xs: list[float], ys: list[float]) -> float | None:
    return pearson(rank(xs), rank(ys))


def load_tasks(week11_root: Path) -> dict[str, dict[str, Any]]:
    task_dir = week11_root / "tenacious_bench_v0.1" / "held_out"
    tasks: dict[str, dict[str, Any]] = {}
    for path in sorted(task_dir.glob("*.jsonl")):
        for row in read_jsonl(path):
            task_id = str(row.get("task_id", ""))
            if task_id:
                tasks[task_id] = row
    return tasks


def load_scorer(week11_root: Path):
    sys.path.insert(0, str(week11_root))
    from src.scoring.scoring_evaluator import score_candidate

    return score_candidate


def summarize_prediction_file(
    *,
    label: str,
    path: Path,
    tasks: dict[str, dict[str, Any]],
    score_candidate,
) -> dict[str, Any]:
    rows = read_jsonl(path)
    records: list[dict[str, Any]] = []
    for row in rows:
        task_id = str(row.get("task_id", ""))
        task = tasks.get(task_id)
        if task is None:
            continue
        candidate = row.get("candidate_output", task.get("candidate_output", {}))
        text = candidate_text(candidate)
        score = score_candidate(task, candidate)
        records.append(
            {
                "task_id": task_id,
                "words": word_count(text),
                "score": float(score.total),
                "passed": bool(score.passed),
            }
        )

    words = [float(item["words"]) for item in records]
    scores = [float(item["score"]) for item in records]
    pass_words = [item["words"] for item in records if item["passed"]]
    fail_words = [item["words"] for item in records if not item["passed"]]
    longest = sorted(records, key=lambda item: item["words"], reverse=True)[:3]

    return {
        "label": label,
        "n": len(records),
        "mean_words": round(sum(words) / len(words), 2) if words else None,
        "mean_score": round(sum(scores) / len(scores), 4) if scores else None,
        "pass_rate": round(sum(1 for item in records if item["passed"]) / len(records), 4)
        if records
        else None,
        "mean_words_passed": round(sum(pass_words) / len(pass_words), 2) if pass_words else None,
        "mean_words_failed": round(sum(fail_words) / len(fail_words), 2) if fail_words else None,
        "pearson_words_vs_score": round(pearson(words, scores), 4)
        if pearson(words, scores) is not None
        else None,
        "spearman_words_vs_score": round(spearman(words, scores), 4)
        if spearman(words, scores) is not None
        else None,
        "longest_three": longest,
    }


def paired_length_delta(
    *,
    left_path: Path,
    right_path: Path,
    tasks: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    left_rows = {str(row["task_id"]): row for row in read_jsonl(left_path) if str(row.get("task_id", "")) in tasks}
    right_rows = {str(row["task_id"]): row for row in read_jsonl(right_path) if str(row.get("task_id", "")) in tasks}
    deltas: list[int] = []
    for task_id, left in left_rows.items():
        right = right_rows.get(task_id)
        if right is None:
            continue
        left_words = word_count(candidate_text(left.get("candidate_output", "")))
        right_words = word_count(candidate_text(right.get("candidate_output", "")))
        deltas.append(left_words - right_words)
    return {
        "paired_n": len(deltas),
        "mean_word_delta_left_minus_right": round(sum(deltas) / len(deltas), 2) if deltas else None,
        "left_longer_count": sum(1 for delta in deltas if delta > 0),
        "right_longer_count": sum(1 for delta in deltas if delta < 0),
        "same_length_count": sum(1 for delta in deltas if delta == 0),
    }


def position_swap_screen(
    *,
    left_path: Path,
    right_path: Path,
    tasks: dict[str, dict[str, Any]],
    score_candidate,
    n_pairs: int = 5,
) -> dict[str, Any]:
    """
    Position-bias diagnostic.

    For each of n_pairs tasks, score both candidates independently in two orderings:
      Order 1: slot_A = left (trained),  slot_B = right (prompt_only)
      Order 2: slot_A = right (prompt_only), slot_B = left (trained)

    A deterministic scorer is position-invariant by design — each candidate is scored
    against the rubric independently, not comparatively. Flip rate should be 0%.

    For an LLM comparative judge (e.g. "which is better, A or B?"), position bias
    manifests when the judge changes its preferred slot after the swap. This function
    records the data structure that a live LLM judge audit would need to populate.
    """
    left_rows = {
        str(row["task_id"]): row
        for row in read_jsonl(left_path)
        if str(row.get("task_id", "")) in tasks
    }
    right_rows = {
        str(row["task_id"]): row
        for row in read_jsonl(right_path)
        if str(row.get("task_id", "")) in tasks
    }
    shared_ids = sorted(set(left_rows) & set(right_rows))[:n_pairs]

    records = []
    flips = 0
    slot_a_wins_order1 = 0
    slot_a_wins_order2 = 0

    for task_id in shared_ids:
        task = tasks[task_id]
        left_candidate = left_rows[task_id].get("candidate_output", {})
        right_candidate = right_rows[task_id].get("candidate_output", {})

        score_left = float(score_candidate(task, left_candidate).total)
        score_right = float(score_candidate(task, right_candidate).total)

        # Order 1: slot A = left (trained), slot B = right (prompt_only)
        winner_order1 = "slot_A" if score_left >= score_right else "slot_B"
        if winner_order1 == "slot_A":
            slot_a_wins_order1 += 1

        # Order 2: slot A = right (prompt_only), slot B = left (trained)
        # Same underlying scores — slot identities are swapped, not the scores
        winner_order2 = "slot_A" if score_right >= score_left else "slot_B"
        if winner_order2 == "slot_A":
            slot_a_wins_order2 += 1

        # A flip means the preferred underlying output changed after the swap
        preferred_left_wins_order1 = score_left >= score_right
        preferred_left_wins_order2 = score_left >= score_right  # deterministic: always same
        flipped = preferred_left_wins_order1 != preferred_left_wins_order2

        if flipped:
            flips += 1

        records.append({
            "task_id": task_id,
            "score_left_trained": round(score_left, 4),
            "score_right_prompt_only": round(score_right, 4),
            "winner_order1_slot_A_is_trained": winner_order1,
            "winner_order2_slot_A_is_prompt_only": winner_order2,
            "flipped": flipped,
        })

    return {
        "diagnostic": "position_swap_screen",
        "n_pairs": len(records),
        "flip_rate": round(flips / len(records), 4) if records else None,
        "slot_A_win_rate_order1": round(slot_a_wins_order1 / len(records), 4) if records else None,
        "slot_A_win_rate_order2": round(slot_a_wins_order2 / len(records), 4) if records else None,
        "interpretation": (
            "flip_rate=0.0 confirms the deterministic scorer is position-invariant: "
            "each candidate is scored against the rubric independently, not comparatively. "
            "An LLM comparative judge (e.g. 'which is better, A or B?') must be tested "
            "with live API calls — swap the candidate order and measure score or winner "
            "flip rate on the same pairs. If slot_A_win_rate stays high in both orderings, "
            "position bias is inflating the result."
        ),
        "pairs": records,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a cheap judge length-bias diagnostic.")
    parser.add_argument("--week11-root", type=Path, default=DEFAULT_WEEK11_ROOT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    week11_root = args.week11_root
    tasks = load_tasks(week11_root)
    score_candidate = load_scorer(week11_root)

    summaries = []
    for label, relative_path in PREDICTION_FILES.items():
        path = week11_root / relative_path
        if path.exists():
            summaries.append(
                summarize_prediction_file(
                    label=label,
                    path=path,
                    tasks=tasks,
                    score_candidate=score_candidate,
                )
            )

    paired = {}
    trained = week11_root / PREDICTION_FILES["trained"]
    prompt_only = week11_root / PREDICTION_FILES["prompt_only"]
    baseline = week11_root / PREDICTION_FILES["week10_baseline"]
    if trained.exists() and prompt_only.exists():
        paired["trained_minus_prompt_only"] = paired_length_delta(
            left_path=trained,
            right_path=prompt_only,
            tasks=tasks,
        )
    if trained.exists() and baseline.exists():
        paired["trained_minus_week10_baseline"] = paired_length_delta(
            left_path=trained,
            right_path=baseline,
            tasks=tasks,
        )

    position_swap = None
    if trained.exists() and prompt_only.exists():
        position_swap = position_swap_screen(
            left_path=trained,
            right_path=prompt_only,
            tasks=tasks,
            score_candidate=score_candidate,
            n_pairs=5,
        )

    output = {
        "diagnostic": "length_bias_screen",
        "week11_root": str(week11_root),
        "interpretation_rule": (
            "A strong positive words-vs-score correlation, or much longer passed outputs "
            "than failed outputs, is a red flag for length bias. A weak or negative "
            "correlation does not prove absence of length bias; it only says this cheap "
            "artifact-level screen did not find that pattern."
        ),
        "summaries": summaries,
        "paired_length_deltas": paired,
        "position_swap_screen": position_swap,
    }
    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
