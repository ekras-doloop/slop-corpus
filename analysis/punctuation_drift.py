#!/usr/bin/env python3
"""Punctuation drift per lab, per snapshot: the numbers behind FINDINGS.md. Standard library only.

Unit: one generation (row). Rates are per 1,000 words, pooled over a lab's rows in one snapshot.
Only prompt_ids present in EVERY non-empty snapshot are counted, so growth of the prompt set cannot move them.
Usage: python3 analysis/punctuation_drift.py            (run from the repo root)"""
import glob, json, os, re
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARKS = {"em_dash": "—", "en_dash": "–", "colon": ":", "semicolon": ";"}

def words(t):
    return len(re.findall(r"[A-Za-z']+", t))

def main():
    files = sorted(f for f in glob.glob(os.path.join(ROOT, "data", "or_*.jsonl")) if os.path.getsize(f))
    snaps = {os.path.basename(f)[3:13]: [json.loads(l) for l in open(f) if l.strip()] for f in files}
    common = set.intersection(*[{r["prompt_id"] for r in rows} for rows in snaps.values()])
    print(f"{len(snaps)} non-empty snapshots; {len(common)} prompts common to all\n")
    print(f"{'date':<11}{'lab':<11}{'model':<26}{'rows':>5}{'rows_em':>8}" + "".join(f"{k:>11}" for k in MARKS))
    for d, rows in snaps.items():
        by = defaultdict(list)
        for r in rows:
            if r["prompt_id"] in common:
                by[r["model"].split("/")[0]].append(r)
        for lab in sorted(by):
            rs = by[lab]; w = sum(words(r["text"]) for r in rs) or 1
            models = sorted({r["model"].split("/")[1] for r in rs})
            rates = [round(sum(r["text"].count(ch) for r in rs) / w * 1000, 1) for ch in MARKS.values()]
            em_rows = sum(MARKS["em_dash"] in r["text"] for r in rs)
            print(f"{d:<11}{lab:<11}{','.join(models)[:25]:<26}{len(rs):>5}{em_rows:>8}" + "".join(f"{x:>11}" for x in rates))

if __name__ == "__main__":
    main()
