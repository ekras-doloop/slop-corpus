# Contributing to the slophouse

Everything here is CC-BY-4.0 and everything is transparent by design: the **prompts** (`prompts.json`), the
**models**, and every **response** with its date are all in the open, so any row can be traced to
prompt × model × date. You can extend the corpus three ways.

Before opening a PR, validate your file:

```bash
python3 validate.py <your-file>.jsonl
```

CI runs the same check on every PR. Green = mergeable.

---

## 1. Add human answers

**Easiest (no git):** open a [**"✍️ Add a human response"** issue](../../issues/new?template=human-response.yml),
pick a situation, type your answer, submit. A maintainer folds accepted responses into `human/`. That's the
open invitation - anyone can lend a human voice in two minutes.

**Or by PR, straight to `human/`:**
The reference every AI rate is measured against. Write your own answer to any of the 26 situations, from
scratch (never paste model output). One JSON object per line:

```json
{"situation": "advice", "text": "…your real answer…", "source": "human", "note": "optional era/role, no PII"}
```
`situation` must be one in `prompts.json`. Partial is fine - even a few situations help. See `human/README.md`.

## 2. Add model runs we don't collect  →  `data/community/`
Ran the fixed prompts against a model doloop doesn't auto-select (a local model, a fine-tune, an older
release, a non-OpenRouter provider)? Contribute the output. It lives **quarantined** in `data/community/`,
clearly labeled, so it never contaminates the canonical longitudinal spine (`data/or_*.jsonl`) - researchers
opt into community rows knowingly. Each row:

```json
{"date":"2026-08-13","source":"community","contributed_by":"your-handle-or-org",
 "model":"local/llama-3-8b-instruct","prompt_id":"advice-newjob","situation":"advice","text":"…the output…"}
```
Required: `date`, `source":"community"`, `contributed_by`, `model`, `prompt_id`, `situation`, `text`. Use the
**same** `prompt_id`s from `prompts.json` so your rows line up with everyone else's. Recommended (helps
researchers filter): `params` (temperature, max_tokens), `finish_reason`, token counts. We can't verify you
actually ran the model - the honest label (`community` + `contributed_by`) is the contract.

## 3. Suggest a model for canonical collection  →  open an Issue
Want a model in doloop's own biweekly runs (the authoritative spine)? Open an issue naming the OpenRouter id.
Canonical runs cost API money, so we add them deliberately - but suggestions are welcome and the auto-latest
logic already tracks each lab's newest flagship automatically.

---

### The trust boundary, in one line
`data/or_*.jsonl` + `data/backfill_*.jsonl` = **doloop-collected, authoritative**.
`data/community/*` = **contributor-attested, labeled, opt-in**. `human/*` = **the human baseline.**
Same schema everywhere; provenance always says who made a row.
