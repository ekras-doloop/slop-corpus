# Community-contributed model runs

Model outputs contributed by others, kept **separate from the canonical `data/or_*.jsonl` spine on purpose.**
These rows are *contributor-attested*: we can't prove the model really produced them, so they're labeled
(`source":"community"`, `contributed_by`) and quarantined here for researchers to opt into knowingly.

Same prompts, same schema as the canonical data (plus the two required provenance fields). Add a file via PR -
see `../../CONTRIBUTING.md` - and run `python3 ../../validate.py your-file.jsonl` first.

Good reasons to contribute here: a local/open model, a fine-tune, an older release OpenRouter no longer serves,
or a provider doloop doesn't call. It widens the corpus at zero cost to the canonical run.
