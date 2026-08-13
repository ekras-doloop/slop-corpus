#!/usr/bin/env python3
"""Maintainer tool: turn submitted 'human-response' issues into human/ rows.

Humans contribute via the issue form (.github/ISSUE_TEMPLATE/human-response.yml) - no git needed. This reads
those issues, parses the form sections, maps the chosen prompt back to its situation, and writes validated
human rows. A maintainer reviews (the form has an 'I wrote this myself' attestation) then commits the output.

  gh must be authenticated. Usage:
    python3 harvest.py                       # -> writes human/from-issues.jsonl (dedup by issue number)
    python3 harvest.py --repo owner/name
"""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ID2SIT = {p["id"]: p["situation"] for p in json.load(open(os.path.join(HERE, "prompts.json")))["prompts"]}

def _section(body, label):
    """Issue forms render as '### <label>\\n\\n<value>' blocks. Return the value under `label`, or ''."""
    m = re.search(r"###\s*" + re.escape(label) + r"\s*\n+(.*?)(?:\n###\s|\Z)", body, re.S)
    v = (m.group(1).strip() if m else "")
    return "" if v in ("_No response_", "None") else v

def harvest(repo):
    raw = subprocess.run(["gh", "issue", "list", "--repo", repo, "--label", "human-response",
        "--state", "all", "--limit", "500", "--json", "number,author,body"],
        capture_output=True, text=True)
    if raw.returncode: raise SystemExit(f"gh error: {raw.stderr.strip()}")
    issues = json.loads(raw.stdout or "[]")
    rows, skipped = [], 0
    for it in issues:
        body = it.get("body") or ""
        text = _section(body, "Your response")
        sit_line = _section(body, "Which situation?")
        m = re.search(r"\[([a-z0-9-]+)\]", sit_line)
        pid = m.group(1) if m else None
        if not text or not pid or pid not in ID2SIT:
            skipped += 1; sys.stderr.write(f"  skip issue #{it['number']} (no text / unknown prompt)\n"); continue
        note = _section(body, "Optional context (no personal info)")
        row = {"situation": ID2SIT[pid], "source": "human", "text": text,
               "contributed_by": (it.get("author") or {}).get("login", "anon"), "issue": it["number"]}
        if note: row["note"] = note
        rows.append(row)
    return rows, skipped

def main(argv):
    repo = "ekras-doloop/slop-corpus"
    if "--repo" in argv: repo = argv[argv.index("--repo") + 1]
    rows, skipped = harvest(repo)
    out = os.path.join(HERE, "human", "from-issues.jsonl")
    with open(out, "w") as f:
        for r in sorted(rows, key=lambda r: r["issue"]): f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"harvested {len(rows)} human rows -> {out}  ({skipped} skipped)")
    print("review, then: python3 validate.py human/from-issues.jsonl && git add human/from-issues.jsonl && commit")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
