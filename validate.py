#!/usr/bin/env python3
"""Validate a contributed jsonl against the corpus schema. Contributors run it before a PR; CI runs it on PRs.

Trust boundary: doloop-collected rows in data/or_*.jsonl and data/backfill_*.jsonl are the authoritative spine.
COMMUNITY contributions live in data/community/ and must be self-labeled (source=community, contributed_by) so a
researcher can always separate attested-by-a-stranger rows from the canonical longitudinal record. This script
can't prove someone really ran a model - it enforces that every row is well-formed, on-schema, and honestly labeled.

  python3 validate.py <file.jsonl> [<file2.jsonl> ...]     # exit 0 = all valid, 1 = problems (with line-level errors)
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SITUATIONS = {p["situation"] for p in json.load(open(os.path.join(HERE, "prompts.json")))["prompts"]}
PROMPT_IDS = {p["id"] for p in json.load(open(os.path.join(HERE, "prompts.json")))["prompts"]}

def _kind(path):
    p = path.replace("\\", "/"); base = os.path.basename(p).lower()
    if "/human/" in p or p.startswith("human/") or base.startswith("human"): return "human"
    if "data/community/" in p: return "community"
    return "canonical"

def validate_row(row, kind, ln, errs):
    def need(field):
        if not row.get(field): errs.append(f"L{ln}: missing/empty '{field}'")
    need("text")
    if row.get("text") and "REPLACE ME" in row["text"]: errs.append(f"L{ln}: template placeholder text not replaced")
    if kind == "human":
        need("situation")
        if row.get("situation") and row["situation"] not in SITUATIONS:
            errs.append(f"L{ln}: situation '{row['situation']}' not in prompts.json ({len(SITUATIONS)} known)")
        if row.get("source") and row["source"] == "community":
            errs.append(f"L{ln}: human rows use source!='community'")
        return
    # model data (canonical or community)
    need("model"); need("situation"); need("prompt_id")
    if row.get("situation") and row["situation"] not in SITUATIONS:
        errs.append(f"L{ln}: situation '{row['situation']}' not a known situation")
    if row.get("prompt_id") and row["prompt_id"] not in PROMPT_IDS:
        errs.append(f"L{ln}: prompt_id '{row['prompt_id']}' not in prompts.json (use the SAME prompts so rows are comparable)")
    if kind == "community":                                  # stricter: must be honestly self-labeled
        if row.get("source") != "community": errs.append(f"L{ln}: community rows must set \"source\":\"community\"")
        if not row.get("contributed_by"): errs.append(f"L{ln}: community rows must set \"contributed_by\" (handle/org, no PII needed)")
        if not row.get("date"): errs.append(f"L{ln}: community rows must set \"date\" (YYYY-MM-DD)")

def validate_file(path):
    kind = _kind(path); errs = []
    try:
        lines = [l for l in open(path) if l.strip()]
    except FileNotFoundError:
        return [f"{path}: not found"]
    if not lines: errs.append("empty file")
    for i, l in enumerate(lines, 1):
        try:
            row = json.loads(l)
        except json.JSONDecodeError as e:
            errs.append(f"L{i}: invalid JSON ({e})"); continue
        validate_row(row, kind, i, errs)
    return [f"{path} [{kind}]: {e}" for e in errs]

def main(argv):
    if not argv: raise SystemExit("usage: validate.py <file.jsonl> ...")
    allerr = []
    for path in argv:
        if os.path.basename(path).upper().startswith("TEMPLATE"):   # example scaffold, not data
            print(f"skip  {path}  (template)"); continue
        e = validate_file(path); allerr += e
        print(f"{'FAIL' if e else 'ok  '}  {path}  ({_kind(path)})")
        for msg in e[:20]: print(f"       {msg.split(': ',1)[-1]}")
    if allerr:
        print(f"\n{len(allerr)} problem(s). See github.com/ekras-doloop/slop-corpus/blob/main/CONTRIBUTING.md")
        return 1
    print("\nall valid.")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
