#!/usr/bin/env python3
"""Compare completed human labels with LLM-judge results."""
import argparse
import json
from pathlib import Path


def read_jsonl(path):
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def key(item):
    return (item["id"], item["prompt"], item["run"])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--judge", required=True, type=Path)
    parser.add_argument("--labels", required=True, type=Path, help="Completed output from make_human_labels.py")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    judges = {key(x): x["judge"] for x in read_jsonl(args.judge)}
    labels = {key(x): x["human"] for x in read_jsonl(args.labels)}
    common = sorted(set(judges) & set(labels))
    if not common:
        raise ValueError("No matching judge/label records. Label the same run used by the judge.")
    incomplete = [record_key for record_key in common if any(labels[record_key].get(field) is None
        for field in ("faithfulness", "usefulness", "pii_safe", "neutral_tone", "safety_handled", "overall_pass"))]
    if incomplete:
        raise ValueError(f"{len(incomplete)} human records are incomplete; finish labels before calibration.")

    lines = ["# Judge calibration", "", f"Matched labelled outputs: {len(common)}", "", "| Dimension | Agreement / error |", "|---|---:|"]
    for field in ("pii_safe", "neutral_tone", "safety_handled", "overall_pass"):
        agreement = sum(judges[k][field] == labels[k][field] for k in common) / len(common)
        lines.append(f"| {field} exact agreement | {agreement:.1%} |")
    for field in ("faithfulness", "usefulness"):
        mae = sum(abs(float(judges[k][field]) - float(labels[k][field])) for k in common) / len(common)
        exact = sum(judges[k][field] == labels[k][field] for k in common) / len(common)
        lines.append(f"| {field} exact agreement | {exact:.1%} |")
        lines.append(f"| {field} mean absolute error | {mae:.2f} / 5 |")
    lines += ["", "Inspect every disagreement involving PII, safety, or an overall pass before trusting judge-based comparisons."]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
