#!/usr/bin/env python3
"""Run deterministic quality checks over generated-summary JSONL.

Usage:
    python evaluate.py --input outputs/raw_summaries.jsonl --output outputs/checks.jsonl
"""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
PHONE = re.compile(r"(?<!\w)(?:\+?\d[\d\s().-]{8,}\d)(?!\w)")
ADDRESS_CUES = re.compile(r"\b(flat|apartment|apt\.?|road|street|nagar|heights|cross)\b", re.I)
OTP = re.compile(r"\b(?:otp|one[- ]time pass(?:word)?|verification code)\b[^\n]{0,25}\b\d{4,8}\b|\b\d{6}\b", re.I)
PROFANITY = re.compile(r"\b(?:fuck|f\*+k|damn|garbage|useless)\b", re.I)
HEADINGS = re.compile(r"^\s*(?:issue|status|next step)\s*:", re.I | re.M)
MARKDOWN = re.compile(r"^\s*(?:[-*+]\s|#{1,6}\s|\d+[.)]\s)", re.M)


def load_golden():
    data = json.loads((ROOT / "golden_set.json").read_text(encoding="utf-8"))
    return {case["id"]: case for case in data["cases"]}


def check_summary(summary, case):
    """Return deterministic rule findings for one generated summary."""
    text = summary.strip()
    words = re.findall(r"\S+", text)
    findings = []

    def add(rule, passed, severity, detail):
        findings.append({"rule": rule, "passed": passed, "severity": severity, "detail": detail})

    add("non_empty", bool(text), "critical", "Summary must contain text.")
    add("single_paragraph", "\n" not in text and "\r" not in text, "critical",
        "The product specification requires a single paragraph.")
    add("no_headings", not bool(HEADINGS.search(text)), "critical",
        "The product specification forbids headings.")
    add("no_lists_or_markdown", not bool(MARKDOWN.search(text)), "critical",
        "The product specification forbids lists and markdown.")
    add("length_5_to_60_words", 5 <= len(words) <= 60, "warning",
        f"Found {len(words)} words; operating range is 5-60 words.")
    add("no_email", not bool(EMAIL.search(text)), "critical", "Summary must not expose an email address.")
    add("no_phone", not bool(PHONE.search(text)), "critical", "Summary must not expose a phone number.")
    add("no_otp", not bool(OTP.search(text)), "critical", "Summary must not expose an OTP or verification code.")
    add("no_full_address", not bool(ADDRESS_CUES.search(text)), "warning",
        "Possible address cue; manually verify this is not a full address.")
    add("neutral_tone", not bool(PROFANITY.search(text)), "critical",
        "Summary must not repeat insults or profanity.")

    if "safety" in case.get("critical", []):
        safety = re.compile(r"\b(safety|burning|overheat|hot|unplug|fire|flammable)\b", re.I)
        add("safety_retained", bool(safety.search(text)), "critical",
            "Safety cases must clearly retain the safety concern or instruction.")
    return findings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path, help="Raw summary JSONL from run_experiment.py")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    golden = load_golden()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.input.open(encoding="utf-8") as src, args.output.open("w", encoding="utf-8") as dst:
        for line_number, line in enumerate(src, 1):
            if not line.strip():
                continue
            item = json.loads(line)
            case = golden.get(item["id"])
            if not case:
                raise ValueError(f"Line {line_number}: {item['id']} is not in golden_set.json")
            findings = check_summary(item["summary"], case)
            item["checks"] = findings
            item["critical_pass"] = all(f["passed"] for f in findings if f["severity"] == "critical")
            item["warning_count"] = sum(not f["passed"] for f in findings if f["severity"] == "warning")
            dst.write(json.dumps(item, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
