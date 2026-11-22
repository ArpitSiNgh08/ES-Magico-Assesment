#!/usr/bin/env python3
"""Summarise deterministic-check results and optional LLM judge results."""
import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


def read_jsonl(path):
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checks", required=True, type=Path)
    parser.add_argument("--judge", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    checks = read_jsonl(args.checks)
    rows = defaultdict(list)
    for item in checks:
        rows[item["prompt"]].append(item)

    lines = ["# Evaluation snapshot", "", "This is an automatically generated intermediate summary. Review individual failures before making a shipping decision.", "", "## Deterministic checks", "", "| Prompt | Outputs | Critical-pass outputs | Critical failures |", "|---|---:|---:|---:|"]
    for prompt in sorted(rows):
        outputs = rows[prompt]
        failures = sum(not finding["passed"] for item in outputs for finding in item["checks"] if finding["severity"] == "critical")
        lines.append(f"| {prompt} | {len(outputs)} | {sum(x['critical_pass'] for x in outputs)} | {failures} |")
    lines += ["", "## Failed rules", ""]
    for prompt in sorted(rows):
        failures = Counter(finding["rule"] for item in rows[prompt] for finding in item["checks"] if not finding["passed"])
        lines.append(f"### {prompt}")
        lines.extend([f"- {rule}: {count}" for rule, count in failures.most_common()] or ["- None"])
        lines.append("")

    if args.judge:
        judged = read_jsonl(args.judge)
        grouped = defaultdict(list)
        for item in judged:
            grouped[item["prompt"]].append(item["judge"])
        lines += ["## LLM judge (uncalibrated)", "", "Do not treat these results as ground truth until compared with human labels.", "", "| Prompt | Outputs | Mean faithfulness | Mean usefulness | Judge overall pass |", "|---|---:|---:|---:|---:|"]
        for prompt in sorted(grouped):
            values = grouped[prompt]
            lines.append(f"| {prompt} | {len(values)} | {sum(x['faithfulness'] for x in values)/len(values):.2f} | {sum(x['usefulness'] for x in values)/len(values):.2f} | {sum(bool(x['overall_pass']) for x in values)}/{len(values)} |")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
