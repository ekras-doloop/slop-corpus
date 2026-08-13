# doloop slop-corpus

An **open, longitudinal record of how the latest large language models write** on a fixed family of
everyday writing situations - a condolence note, a cover letter, a wedding toast, a product review,
a reflective essay, twenty in all. Every two weeks we ask the *same* prompts to the *latest* model
from each major lab (auto-detected, so new releases are tracked automatically) and publish the raw output.

Because the prompts never change, the only variable is **style drift**: you can watch, over releases and
months, which phrases saturate into cliche, which models converge on the same "voice," and how the
machine register moves. It is the raw material for studying **AI slop as it actually evolves**, in the open.

## Why this is public
The "AI tells" everyone argues about ("delve", "it's a testament to", the reassuring second person) are a
moving target - what reads fresh today is a cliche in a year. A one-off list rots. A *dated, growing corpus*
does not. We publish it as a public good so researchers, writers, editors, and tool-builders can measure
the drift for themselves rather than trust anyone's snapshot - ours included.

## Data
- `data/or_<YYYY-MM-DD>.jsonl` - one JSON object per line:
  `{"date","model","prompt_id","situation","text"}`
- `prompts.json` - the fixed situational prompt family (append-only; ids are stable).
- New snapshot roughly every two weeks (see `.github/workflows/collect.yml`).

## Method
Latest chat flagship per lab (anthropic/openai/google/meta/mistral/xai/deepseek/qwen), auto-detected from
the OpenRouter model list by newest-created, skipping guard/vision/embed/etc. `temperature 0.7`, ~1200 tokens.
Reproduce a run: `OPENROUTER_API_KEY=... python3 collect.py $(date +%F)`.

## Sunset clause
This corpus is a public good with a dead-man's switch. Every run logs a public interest pulse to
`pulse.jsonl` (stars, forks, watchers, issues - the signals CI doesn't generate itself). If a full
year passes with **zero** external interest, the collector auto-closes: the cron disables itself and a
`DORMANT.md` appears. Already-collected data stays public forever; re-enabling the workflow is one click.
No point spending tokens on a corpus nobody pulls. See `killswitch.py`.

## License
Data and code: **CC-BY-4.0**. Use it freely; credit *doloop slop-corpus (doloop.io)*.

## Stewardship
Maintained by [doloop](https://doloop.io), which builds deterministic tools that help writing read better
regardless of who drafted it. We mine this corpus for our own work - but the corpus itself is yours.
Contributions welcome: add a situation to `prompts.json` (append-only; never renumber).
