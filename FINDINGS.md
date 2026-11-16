# Findings

Dated observations from this corpus. Each one names its rows, its snapshots and the script that reproduces it.
Numbers are per 1,000 words, pooled over one lab's rows in one snapshot, counting only the 20 prompts that
appear in every non-empty snapshot. Reproduce with `python3 analysis/punctuation_drift.py`.

## 2026-11-15: Anthropic's newest models almost stopped writing em dashes

Across three Anthropic models from August to mid-September, most answers contained at least one em dash.
The two Anthropic 5.5 models in our runs contained none, and claude-fable-5.2 contained one in 2 of 30 answers.

| Snapshot | Model | Rows with an em dash | Em dashes per 1k words | Colons per 1k words |
|---|---|---|---|---|
| 2026-08-13 | claude-opus-5-fast | 16 of 20 | 9.9 | 6.0 |
| 2026-08-15 | claude-opus-5-fast | 16 of 20 | 10.7 | 5.7 |
| 2026-09-01 | claude-opus-5 | 15 of 20 | 7.0 | 7.0 |
| 2026-09-15 | claude-fable-5.1 | 11 of 20 | 6.2 | 7.8 |
| 2026-10-01 | claude-sonnet-5.5 | 0 of 20 | 0.0 | 8.4 |
| 2026-10-15 | claude-haiku-5.5 | 0 of 20 | 0.0 | 3.6 |
| 2026-11-15 | claude-fable-5.2 | 1 of 20 | 0.3 | 4.7 |

Over all 30 prompts the 5.5 models are 0 of 60 rows, and claude-fable-5.2 is 2 of 30. The latest models from deepseek, google, openai, qwen and x-ai kept using em dashes in every snapshot
(1.1 to 6.7 per 1k words through 2026-10-15; on 2026-11-15, 1.3 to 6.1).

What this does and does not show:
- It is three recent models, on these prompts, at temperature 0.7. It does not show that every Anthropic
  model, or every surface, has stopped.
- The em dash is the most common single marker in public lists of "AI tells". A detector that leans on it
  will score these models as human-like.

## 2026-11-15: a model changed without changing its name

`meta-llama/llama-4-maverick` is the one model asked in every snapshot. For five snapshots none of its
answers contained an em dash (0 of 140 rows over all prompts). On 2026-10-15, 9 of 30 did, its colon rate
went from 2 to 3 per 1k words to 10.9, and semicolons appeared. On 2026-11-15 it was back: 0 of 30 rows with an
em dash, colons at 2.5. The model id and decode settings never changed. A change that comes and goes points to
which provider served the calls more than to a new version of the model.

We cannot say why: the rows did not record which provider served the call. From 2026-11-15 every row records
`or_provider`, and a fixed set of anchor models is asked every run (see Method), so a change like this can be
traced to a provider or to time.

## Gaps

- **2026-11-01:** no data. The API key was rejected (HTTP 401) for every call, and the collector wrote empty files
  that were published. They were removed on 2026-11-15, and the collector now fails the run instead of publishing
  an empty snapshot. The 2026-11-15 run failed the same way and was rerun the same day with a new key.
- **Partial labs:** google answered 13 of 30 prompts on 2026-11-15 and mistralai 2 to 16 in each snapshot where it appears.
- **Truncation:** `max_tokens` is 700 and is kept for comparability. Some answers stop mid-thought
  (google 17 rows, mistralai 9, deepseek 6, on the 20 common prompts over the six snapshots). Filter on `finish_reason == "length"`.
