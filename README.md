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

## Data
- `data/or_<YYYY-MM-DD>.jsonl` - ongoing snapshots. One JSON object per line:
  `{"date","era","model","prompt_id","situation","voice","text"}` (`era` = `latest`; `voice` is the
  requested persona for the 4 steered prompts, else `null`).
- `data/backfill_<YYYY-MM-DD>.jsonl` - **historical baseline** (`era` = `backfill`): the same prompts asked
  to notable *older, off-label* models (GPT-3.5, Claude 2, Llama-2, Mixtral, and the like). Drift needs an
  origin - you cannot measure a trend from today forward only. This anchors the timeline before the corpus began.
- `pulse.jsonl` - public interest history (see Sunset clause).
- `prompts.json` - the fixed situational prompt family (append-only; ids are stable).
- New snapshot roughly every two weeks (see `.github/workflows/collect.yml`).

## For researchers
Fixed prompts + many independent labs + dated snapshots + a historical baseline = a clean panel for
studying machine style. Concrete questions it supports: which phrases saturate into cliche and how fast;
whether independent houses *converge* on one register (they do - three frontier models unprompted all reach
for the same reassurance opening); how a single lab's voice moves release to release; and what a real human
baseline would have to beat. The voice-steered prompts add a sharper one: **does the house style survive an
explicit voice instruction?** Compare a situation's voiceless rows against its steered rows - if the slop
markers barely drop, the centroid is stickier than a persona prompt can fix. CC-BY-4.0 - cite it, fork it,
extend the prompt family.

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
