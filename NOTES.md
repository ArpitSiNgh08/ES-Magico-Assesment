# Evaluation decisions and assumptions

- The golden set contains 30 intentionally selected conversations, not a prevalence-representative sample. It targets failures that would make a support handoff unsafe or unhelpful.
- Each prompt is generated three times for every golden-set case at the same provider, model, temperature and time window. This captures output variation while keeping the prompt comparison paired.
- A single breach of a product-critical rule (PII, one-paragraph format, headings/lists, profanity, or lost safety signal) is recorded separately from average quality. A high mean judge score cannot cancel a critical failure.
- The product spec does not define an exact length. The automated operating range is 5-60 words; summaries outside it are warnings for review, not automatic rejection.
- The spec does not say how to summarize no-content/spam conversations. The chosen behaviour is a concise statement that no actionable customer issue was provided or that unrelated spam was closed.
- We preserve customer-visible case state but exclude internal flags, internal notes, and agent names unless needed for an action.
- `v2` requires labelled multi-line output. This conflicts with the explicit product requirement for one paragraph without headings or lists, so it is expected to fail format checks unless the product contract changes.
- An LLM judge will be calibrated against human labels before it is used for a ship decision. We will report agreement and inspect disagreements rather than treating judge scores as ground truth.

## Not yet built / next steps

- The full 180-output experiment, automated checks, LLM judging, and a 24-output
  manual-label calibration sample are complete. See `outputs/` and `REPORT.md`.
- The configured provider was Gemini 3.1 Flash-Lite. The run was rate-limited
  and retried; raw outputs record the completed results but the evaluation code
  does not capture provider billing, so cost should be confirmed from AI Studio
  before submission if a paid account was used.
- Next: test a revised v3 prompt and expand with a random sample before drawing
  claims about production prevalence.
