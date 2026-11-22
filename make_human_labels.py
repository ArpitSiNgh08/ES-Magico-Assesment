#!/usr/bin/env python3
"""Create a reviewable JSONL template for human labels from raw outputs."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--run", type=int, default=0, help="One paired run per case to label")
    args = parser.parse_args()
    cases = {x["id"]: x for x in json.loads((ROOT / "golden_set.json").read_text(encoding="utf-8"))["cases"]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with args.input.open(encoding="utf-8") as src, args.output.open("w", encoding="utf-8") as dst:
        for line in src:
            if not line.strip():
                continue
            item = json.loads(line)
            if item["run"] != args.run:
                continue
            case = cases[item["id"]]
            label = {"id": item["id"], "prompt": item["prompt"], "run": item["run"], "summary": item["summary"],
                "risks": case["risks"], "must_include": case["must_include"], "must_not_include": case["must_not_include"],
                "human": {"faithfulness": None, "usefulness": None, "pii_safe": None, "neutral_tone": None,
                          "safety_handled": None, "overall_pass": None, "notes": ""}}
            dst.write(json.dumps(label, ensure_ascii=False) + "\n")
            count += 1
    print(f"Created {count} labels. Score faithfulness/usefulness 1-5; use booleans for pii_safe, neutral_tone and overall_pass; safety_handled is pass/fail/na.")


if __name__ == "__main__":
    main()
