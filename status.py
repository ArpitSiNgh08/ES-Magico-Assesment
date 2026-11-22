#!/usr/bin/env python3
"""Show progress for generation and LLM judging."""
import json
from pathlib import Path

ROOT = Path(__file__).parent
EXPECTED = 180  # 30 golden-set cases x 2 prompts x 3 runs


def unique_count(path):
    if not path.exists():
        return 0
    records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return len({(x["id"], x["prompt"], x["run"]) for x in records})


def show(name, path):
    completed = unique_count(path)
    state = "COMPLETE" if completed == EXPECTED else "IN PROGRESS"
    print(f"{name}: {completed}/{EXPECTED} ({state})")


show("Generation", ROOT / "outputs" / "raw_summaries_final.jsonl")
show("LLM judging", ROOT / "outputs" / "judged.jsonl")
