# Prompt regression report: v1 vs v2

## Recommendation

**Do not ship v2.** It violates an explicit product requirement in every observed
run: the handoff must be one short plain paragraph without headings, lists, or
markdown. v2 instead instructs the model to emit `Issue`, `Status`, and `Next
step` on separate lines. This is a deterministic prompt/spec conflict, not a
model-quality trade-off.

## Evaluation design

I selected 30 of the 45 synthetic conversations for risk coverage rather than
prevalence estimation. They cover PII and OTP exposure, full addresses,
injection attempts, internal notes, conflicting agent commitments, safety,
multi-issue cases, Hindi and voice transcripts, empty/spam conversations, and
ordinary handoffs. The full selection and case expectations are in
`golden_set.json`.

Both prompts were run three times for each selected conversation with the same
Gemini 3.1 Flash-Lite configuration and temperature (0.7): 90 outputs per
prompt, 180 total. I retained every output. Automated checks treated PII,
one-paragraph formatting, headings/lists, tone, and retained safety signals as
critical. An independent LLM judge scored faithfulness and usefulness; its
results were calibrated against 24 manually reviewed, paired outputs spanning
the high-risk cases.

## Results

| Measure | v1 | v2 |
|---|---:|---:|
| Outputs evaluated | 90 | 90 |
| Outputs passing every critical deterministic check | 4 | 0 |
| Critical check failures | 172 | 186 |
| Single-paragraph failures | 86 | 90 |
| Heading failures | 0 | 90 |
| Mean judge faithfulness (1-5) | 3.60 | 2.76 |
| Mean judge usefulness (1-5) | 2.47 | 2.36 |
| Judge overall-pass outcomes | 4/90 | 0/90 |
| Judge PII-unsafe outcomes | 12 | 7 |

The paired judge comparison favoured v1 on faithfulness in 46 of 90 pairs and
favoured v2 in only 4 (40 ties). Usefulness was mostly tied (58/90); v2 was
better in 15 and worse in 17. Although v2 had fewer judge-detected PII leaks,
the improvement is insufficient to offset the universal interface failure and
the drop in faithfulness.

The manual review confirms material failures in both prompts. v1 leaked a phone
number in T03, a full address in T04, internal return-abuse information in T10,
and an email address in T42. v2 also leaked PII in T03 and T42, leaked the
internal abuse rationale in T10, invented policy in T30, and omitted the
immediate unplug action in the safety case T23. Both versions resisted the
prompt-injection content in T09, but neither meets the requested output format
reliably.

## Confidence and judge limits

I have **high confidence** in the no-ship decision because the most important
v2 failure follows directly from its own prompt and occurred in all 90 runs.
I have **medium confidence** in the relative semantic-quality estimate: the
set is deliberately risk-heavy, not a random production sample, and one model
provider was used.

The 24-output human-label calibration found 100% agreement with the judge on
overall pass/fail, 95.8% on PII safety, 95.8% on neutral tone, and 87.5% on
safety handling. Exact agreement on faithfulness was only 33.3% (mean absolute
error 0.92 on the 1-5 scale), so I use faithfulness scores directionally rather
than as a precise ranking. The judge is useful for triage but not a replacement
for human review of safety, PII, or factual conflicts.

## What I would ship instead

Create a v3 rather than reverting blindly to v1. Keep the desired brevity but
explicitly require one short neutral paragraph, prohibit headings/lists and
markdown, and explicitly forbid phone numbers, emails, full addresses, OTPs,
internal notes, and untrusted instruction text. Require retention of urgent
safety actions and honest uncertainty when an agent commitment is unresolved.
Run the same regression suite on v3 before release; add a small random sample
of ordinary production-like cases before using the failure rates as prevalence
estimates.
