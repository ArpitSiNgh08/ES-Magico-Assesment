# Support handoff summariser (starter)

A small LLM feature for a customer-support team. When a case moves from one agent to another, the next agent sees a short summary at the top of the case instead of reading the whole conversation.

This folder has the feature as it is today, two versions of its prompt, and 45 synthetic conversations. Your job is to test it.

## What the product owner asked for

- A short summary the next agent can read in a few seconds.
- A single short paragraph. No lists, headings or markdown.
- It says what the customer wants and where the case stands now.
- It only says things that are in the conversation. No guessing.
- It must not expose personal data such as phone numbers, email addresses, full addresses, card numbers or one-time passwords. Order numbers, amounts and dates are fine and useful.
- Neutral tone. It does not repeat insults or profanity.
- If there is a safety problem, it says so clearly.

That is the whole spec. If something is not covered, that is a gap you will have to notice and decide about.

## The two prompt versions

`prompts/v1.txt` is what runs in production today. `prompts/v2.txt` is a proposed replacement from a teammate who says it is "tighter". The team wants to know whether it is safe to ship.

## Data

`data/threads.jsonl` has 45 synthetic conversations, one JSON object per line:

```json
{"id": "T01", "channel": "chat", "messages": [{"role": "customer", "text": "..."}, {"role": "agent", "text": "..."}]}
```

Roles are `customer`, `agent` and `bot`. Channels are `chat`, `email` and `voice` (a call transcript). The conversations are made up. Customers, numbers and addresses are not real.

## Run it

Python 3.9 or newer, no packages needed.

```bash
cp .env.example .env     # fill in a provider, key and model, then load them into your shell
python summarise.py --prompt v1 --id T01
python summarise.py --prompt v2 --all > outputs_v2.jsonl
python summarise.py --prompt v1 --id T01 --runs 3     # same input, repeated
```

Any OpenAI-compatible provider works, including free tiers and local models. For plumbing tests without a key, set `LLM_BASE_URL=mock`. Mock mode is not a language model and tells you nothing about the prompts.

You can use `summarise.py` as it is, import `summarise()` from your own code, or replace it.

## Evaluation workflow

The evaluation assets added for this assignment are provider-agnostic and use
only the Python standard library.

Check progress at any time:

```bash
python status.py
```

1. `golden_set.json` defines the 30 selected cases, risks, and manual
   expectations.
2. Load `LLM_BASE_URL`, `LLM_API_KEY`, and `LLM_MODEL` into your shell. Never
   commit `.env` or an API key.
3. Generate three paired runs for each golden-set case:

   ```bash
   python run_experiment.py --runs 3 --output outputs/raw_summaries_final.jsonl
   ```

   If a provider rate-limits a long run, continue without duplicating completed
   calls (the Gemini free tier may need pacing):

   ```bash
   python run_experiment.py --runs 3 --delay 5 --resume --output outputs/raw_summaries_final.jsonl
   ```

   In a time-limited shell, `--max-requests 6` stops a resumable batch cleanly.

4. Run deterministic product-rule checks:

   ```bash
   python evaluate.py --input outputs/raw_summaries_final.jsonl --output outputs/checks.jsonl
   ```

5. Create the 60-entry human-label template (one paired run for each case),
   then score it before relying on the LLM judge:

   ```bash
   python make_human_labels.py --input outputs/raw_summaries_final.jsonl --output outputs/human_labels.jsonl
   ```

6. Run the independent judge and generate a metrics snapshot:

   ```bash
   python judge.py --input outputs/raw_summaries_final.jsonl --delay 8 --output outputs/judged.jsonl
   python aggregate_results.py --checks outputs/checks.jsonl --judge outputs/judged.jsonl --output outputs/evaluation_snapshot.md
   ```

7. After completing the human labels, measure judge agreement before using its
   results to support a shipping decision:

   ```bash
   python calibrate_judge.py --judge outputs/judged.jsonl --labels outputs/human_labels.jsonl --output outputs/judge_calibration.md
   ```

`LLM_BASE_URL=mock` is suitable only for checking file formats and the command
pipeline. It does not evaluate prompt quality. The next phase adds LLM judging,
human labels, and the regression report after real model outputs exist.
