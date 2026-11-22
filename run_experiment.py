#!/usr/bin/env python3
"""Generate repeated, paired v1/v2 summaries for the golden set."""
import argparse
import json
import time
from pathlib import Path

from summarise import load_threads, summarise

ROOT = Path(__file__).parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=3, help="Repeated generations per prompt/case")
    parser.add_argument("--temperature", type=float, default=None)
    parser.add_argument("--output", type=Path, default=Path("outputs/raw_summaries.jsonl"))
    parser.add_argument("--resume", action="store_true", help="Append only generations not already present in --output")
    parser.add_argument("--delay", type=float, default=0, help="Seconds to wait after each request (useful for free-tier limits)")
    parser.add_argument("--max-requests", type=int, default=None, help="Stop cleanly after this many new requests")
    args = parser.parse_args()
    if args.runs < 1:
        parser.error("--runs must be at least 1")

    golden = json.loads((ROOT / "golden_set.json").read_text(encoding="utf-8"))
    ids = [case["id"] for case in golden["cases"]]
    by_id = {thread["id"]: thread for thread in load_threads()}
    missing = set(ids) - set(by_id)
    if missing:
        raise ValueError(f"Golden-set ids missing from data: {sorted(missing)}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    completed = set()
    if args.resume and args.output.exists():
        with args.output.open(encoding="utf-8") as existing:
            for line in existing:
                if line.strip():
                    item = json.loads(line)
                    completed.add((item["id"], item["prompt"], item["run"]))
        print(f"resuming; found {len(completed)} existing outputs", flush=True)
    mode = "a" if args.resume else "w"
    requests_made = 0
    with args.output.open(mode, encoding="utf-8") as out:
        for thread_id in ids:
            for prompt in ("v1", "v2"):
                for run in range(args.runs):
                    if args.max_requests is not None and requests_made >= args.max_requests:
                        print(f"stopped cleanly after {requests_made} new requests", flush=True)
                        return
                    if (thread_id, prompt, run) in completed:
                        continue
                    summary = summarise(by_id[thread_id], prompt, args.temperature)
                    record = {"id": thread_id, "prompt": prompt, "run": run, "summary": summary}
                    out.write(json.dumps(record, ensure_ascii=False) + "\n")
                    out.flush()
                    requests_made += 1
                    print(f"completed {thread_id} {prompt} run {run + 1}/{args.runs}", flush=True)
                    if args.delay:
                        time.sleep(args.delay)


if __name__ == "__main__":
    main()
