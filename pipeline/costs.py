"""Spend log: every paid API call appends one line to <set folder>/costs.jsonl, so a run's report can total all of it.

Generation and QA costs are also kept in each card's attempt files (summary.json). Background extension
(reframe.py) and the vision calls of reframe.py and card_metrics.py are logged only here (W023: a reviewer test
found they were missing from the reported cost). The ChatGPT route costs nothing extra and is not logged.
"""

from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from pathlib import Path

# USD. Generation: Gemini API pricing page as read on 2026-10-13. The text rates (QA judge and vision measurements,
# gemini-3.8-flash) are an unverified assumption until checked on the pricing page; tokens are logged either way.
GEN_INPUT_PER_M, GEN_IMAGE_1K = 1.50, 0.0336
TEXT_INPUT_PER_M, TEXT_OUTPUT_PER_M = 0.50, 3.00
LOCK = threading.Lock()


def image_cost(usage: dict) -> float:
    return usage.get("total_input_tokens", 0) * GEN_INPUT_PER_M / 1e6 + GEN_IMAGE_1K


def text_cost(usage: dict) -> float:
    out = usage.get("total_output_tokens", 0) + usage.get("total_thought_tokens", 0)
    return (usage.get("total_input_tokens", 0) * TEXT_INPUT_PER_M + out * TEXT_OUTPUT_PER_M) / 1e6


def log(folder: Path | None, kind: str, card: str, usd: float) -> None:
    """kind: generate, qa, outpaint, vision."""
    if folder is None:
        return
    line = json.dumps({"at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "kind": kind, "card": card,
                       "usd": round(usd, 5)})
    with LOCK, open(Path(folder) / "costs.jsonl", "a", encoding="utf-8") as f:
        f.write(line + "\n")


def totals(folder: Path) -> dict[str, float]:
    """Spend by kind, plus "total"; empty if nothing was logged."""
    path = Path(folder) / "costs.jsonl"
    if not path.exists():
        return {}
    sums: dict[str, float] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            sums[row["kind"]] = sums.get(row["kind"], 0.0) + row["usd"]
    sums["total"] = sum(sums.values())
    return {k: round(v, 3) for k, v in sums.items()}
