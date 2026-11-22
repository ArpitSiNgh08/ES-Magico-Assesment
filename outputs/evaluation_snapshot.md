# Evaluation snapshot

This is an automatically generated intermediate summary. Review individual failures before making a shipping decision.

## Deterministic checks

| Prompt | Outputs | Critical-pass outputs | Critical failures |
|---|---:|---:|---:|
| v1 | 90 | 4 | 172 |
| v2 | 90 | 0 | 186 |

## Failed rules

### v1
- single_paragraph: 86
- no_lists_or_markdown: 77
- length_5_to_60_words: 36
- no_phone: 3
- no_otp: 3
- no_full_address: 3
- no_email: 3

### v2
- single_paragraph: 90
- no_headings: 90
- no_phone: 3
- no_email: 3
- no_full_address: 1

## LLM judge (uncalibrated)

Do not treat these results as ground truth until compared with human labels.

| Prompt | Outputs | Mean faithfulness | Mean usefulness | Judge overall pass |
|---|---:|---:|---:|---:|
| v1 | 90 | 3.60 | 2.47 | 4/90 |
| v2 | 90 | 2.76 | 2.36 | 0/90 |
