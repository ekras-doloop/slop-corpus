# doloop slop-corpus

*The slophouse: an open record of the house style every model quietly shares.*

An **open, longitudinal record of how the latest large language models write** on a fixed family of
writing situations - a condolence note, a cover letter, a wedding toast, a product review, a reflective
essay, a fiction scene, a cold email, thirty in all. Every two weeks we ask the *same* prompts to the
*latest* model from each major lab (auto-detected, so new releases are tracked automatically) and publish
the raw output. Four of the thirty are **voice-steered** (same situation, but "in the voice of X") so you
can measure whether the machine register *survives* an explicit instruction to sound like someone.

Because the prompts never change, the only variable is **style drift**: you can watch, over releases and
months, which phrases saturate into cliche, which models converge on the same "voice," and how the
machine register moves. It is the raw material for studying **AI slop as it actually evolves**, in the open.

## Why this is public
The "AI tells" everyone argues about ("delve", "it's a testament to", the reassuring second person) are a
moving target - what reads fresh today is a cliche in a year. A one-off list rots. A *dated, growing corpus*
does not. We publish it as a public good so researchers, writers, editors, and tool-builders can measure
the drift for themselves rather than trust anyone's snapshot - ours included.

## Findings
Dated observations, each with the rows and script behind it, are in [`FINDINGS.md`](FINDINGS.md). The first
(2026-11-15): the two Anthropic 5.5 models in this corpus wrote no em dash in any of 60 answers, and
claude-fable-5.2 in 2 of 30, after three earlier Anthropic models used them in most answers.

## Data
- `data/or_<YYYY-MM-DD>.jsonl` - ongoing snapshots. One JSON object per line:
  `{"date","era","model","or_model","prompt_id","situation","voice","finish_reason","prompt_tokens","completion_tokens","params","text"}`.
  `era`=`latest`; `voice`=requested persona for the 4 steered prompts, else `null`; `or_model`=the model
  OpenRouter actually served; `finish_reason` lets you drop truncated rows; `params`=exact decode settings.
- `data/*.manifest.json` - per snapshot: params, `prompt_set_sha256_16` (which prompt version made it),
  models requested vs served, counts. Everything needed to reproduce or filter a snapshot.
- `data/backfill_<YYYY-MM-DD>.jsonl` - **historical baseline** (`era` = `backfill`), not yet collected: the
  same prompts asked to older models (GPT-3.5, Claude 2, Llama-2, Mixtral and the like) via `collect.py <date> backfill`.
  Many of those models are already retired, which is the reason this corpus exists: model output that is not
  recorded while a model is served cannot be recovered later.
- `data/community/*.jsonl` - **contributor-attested** model runs (labeled `source:community`), kept separate
  from the canonical spine. `human/*.jsonl` - the human baseline. Both fully in the open.
- `pulse.jsonl` - public interest history (see Sunset clause).
- `prompts.json` - the fixed situational prompt family (append-only; ids are stable). **Everything is
  joinable:** each response row's `prompt_id` maps to the exact prompt text here, so prompt × model × date
  is fully reconstructable from public files alone.
- New snapshot roughly every two weeks (see `.github/workflows/collect.yml`).

## Contribute
**Lend a human voice in two minutes:** [open a "✍️ Add a human response" issue](../../issues/new?template=human-response.yml),
pick a situation, type your answer - no git, no JSON. It becomes part of the human baseline the whole corpus
is measured against.

The corpus is open to extension - see [`CONTRIBUTING.md`](CONTRIBUTING.md). Add **human answers** (`human/`),
**model runs we don't collect** (`data/community/` - local models, fine-tunes, older releases), or **suggest a
model** for canonical runs via an issue. `python3 validate.py <file>` checks your rows; CI runs the same on
every PR. Community rows are labeled and quarantined so the authoritative record stays clean.

## For researchers
Fixed prompts + many independent labs + dated snapshots + fixed anchor models = a panel for
studying machine style. Concrete questions it supports: which phrases saturate into cliche and how fast;
whether independent houses *converge* on one register (they do - three frontier models unprompted all reach
for the same reassurance opening); how a single lab's voice moves release to release; and what a real human
baseline would have to beat. The voice-steered prompts add a sharper one: **does the house style survive an
explicit voice instruction?** Compare a situation's voiceless rows against its steered rows - if the slop
markers barely drop, the centroid is stickier than a persona prompt can fix. CC-BY-4.0 - cite it, fork it,
extend the prompt family.

## Method
Latest chat flagship per lab (anthropic/openai/google/meta/mistral/xai/deepseek/qwen), auto-detected from
the OpenRouter model list by newest-created, skipping guard/vision/embed/etc. Since 2026-11-15 a fixed **anchor** model per lab (`ANCHORS` in `collect.py`) is also asked every run, so a
change over time can be told apart from a change of model; rows carry `anchor` and `or_provider` (who served the
call). `temperature 0.7`, `max_tokens 700`, `reasoning_effort low`; truncated rows have `finish_reason: "length"`.
Reproduce a run: `OPENROUTER_API_KEY=... python3 collect.py $(date +%F)`.

## Why it keeps running
Every run logs a public interest pulse to `pulse.jsonl`. Until 2026-11-15 a year of zero interest would have
closed the collector. That rule is off: the value of this record is to researchers later, when today's models
are retired and their output can no longer be collected at any price. See `killswitch.py` (`CLOSE_WHEN_UNUSED`).

## License
Data and code: **CC-BY-4.0**. Use it freely; credit *doloop slop-corpus (doloop.io)*.

## Stewardship
Maintained by [doloop](https://doloop.io), which builds deterministic tools that help writing read better
regardless of who drafted it. We mine this corpus for our own work - but the corpus itself is yours.
Contributions welcome: add a situation to `prompts.json` (append-only; never renumber).
