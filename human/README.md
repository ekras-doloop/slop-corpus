# Human baseline

The corpus records how *models* write. This folder is where the **human answers to the same situations**
live - the reference every AI slop rate is measured against. Without it, "gemini 13.7 markers/1k" floats;
with it, that becomes "13.7 vs a human 2.1," and the corpus turns from a curiosity into a benchmark.

## Format
One JSON object per line, in `human/*.jsonl`. Match a prompt's `situation` so it joins to the AI rows:

```json
{"situation": "advice", "text": "…a real person's answer to the same task…", "source": "human", "note": "optional: rough era/role, anon is fine"}
```

- **`situation`** must be one of the 26 in `prompts.json` (advice, condolence, review, fiction, …).
- **`text`** is the human-written response. Write it how *you* would - the point is a real voice, not a polished one.
- **`source`** = `human` (reserved for later: `human-pre-2022`, `human-edited`, etc.).
- **`note`** optional, no PII. Era and role help ("2019 blog", "nurse"); a name is not needed and not wanted.

## How to contribute
Open a PR adding a `human/<yourhandle-or-anon>.jsonl`. Even a handful of situations helps - partial is fine,
the miner joins on whatever situations are present. **Write from scratch; do not paste model output.**
CC-BY-4.0, same as the rest of the corpus.

## Why humans are the one source we don't pay for
Every model row costs an API call. Human rows cost nothing but a person choosing to write one. That makes
this the highest-leverage, lowest-cost expansion of the whole corpus - and the only one that makes the AI
numbers *mean* something.
