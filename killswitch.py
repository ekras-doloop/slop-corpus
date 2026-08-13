#!/usr/bin/env python3
"""Dead-man's kill switch for the public slop-corpus cron.

A public good that spends tokens on a schedule should not run forever if nobody uses it.
Rule (GR, 2026-08-12): if a full YEAR passes with NO external pull/interest, auto-close it.

What counts as "interest" = signals this Action does NOT generate itself:
  stars, forks, watchers (subscribers beyond the owner), and issues.
  (Deliberately NOT git-clone traffic: every scheduled run does actions/checkout, which GitHub
   counts as a clone - so clones can never fall to zero and would defeat the switch. We log clone
   traffic to pulse.jsonl for transparency, but never gate on it.)

Each run appends a dated pulse to pulse.jsonl (committed), so the interest history is public.
If the repo is older than 365 days AND every interest signal is still zero, the switch:
  1. disables this workflow via the API (no future runs fire), and
  2. writes DORMANT.md and emits dormant=true so the collect/publish steps skip.
Re-enabling is one click in the Actions tab - the switch is a sunset, not a delete.

  env: GH_TOKEN (Actions token, needs actions:write), GITHUB_REPOSITORY (owner/repo)
  python3 killswitch.py            # prints dormant=true/false to $GITHUB_OUTPUT
"""
import urllib.request, json, os, sys
from datetime import datetime, timezone

API = "https://api.github.com"
WORKFLOW_FILE = "collect.yml"
GRACE_DAYS = 365

def _get(path, token):
    req = urllib.request.Request(API + path,
        headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json",
                 "User-Agent": "doloop-slop-killswitch"})
    return json.load(urllib.request.urlopen(req, timeout=30))

def _clones_14d(repo, token):
    try:
        return _get(f"/repos/{repo}/traffic/clones", token).get("uniques", 0)   # CI-polluted; log only
    except Exception:
        return None

def main():
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")
    if not token or not repo:
        # no token/repo (e.g. local run) -> never kill; just report alive so generation proceeds
        return _emit(False, note="no GH_TOKEN/GITHUB_REPOSITORY - kill switch inert")

    r = _get(f"/repos/{repo}", token)
    created = datetime.fromisoformat(r["created_at"].replace("Z", "+00:00"))
    age_days = (datetime.now(timezone.utc) - created).days
    stars = r.get("stargazers_count", 0)
    forks = r.get("forks_count", 0)
    subs  = r.get("subscribers_count", 0)          # watchers; includes the owner
    issues = r.get("open_issues_count", 0)         # issues + PRs
    interest = stars + forks + max(0, subs - 1) + issues   # owner's own watch does not count
    clones = _clones_14d(repo, token)

    # public interest history (committed by the Publish step)
    pulse = {"date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
             "age_days": age_days, "stars": stars, "forks": forks,
             "watchers_ext": max(0, subs - 1), "issues": issues, "clones_14d": clones}
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "pulse.jsonl"), "a") as f:
        f.write(json.dumps(pulse) + "\n")

    sys.stderr.write(f"pulse: age={age_days}d interest={interest} "
                     f"(stars={stars} forks={forks} watchers_ext={max(0,subs-1)} issues={issues}) clones14d={clones}\n")

    if age_days > GRACE_DAYS and interest == 0:
        sys.stderr.write(f"KILL SWITCH: {age_days}d old, zero external interest for a full year -> closing.\n")
        _disable(repo, token)
        _write_dormant(age_days)
        return _emit(True, note=f"dormant after {age_days}d unused")
    return _emit(False, note=f"alive: interest={interest}, age={age_days}d")

def _disable(repo, token):
    req = urllib.request.Request(f"{API}/repos/{repo}/actions/workflows/{WORKFLOW_FILE}/disable",
        method="PUT", headers={"Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json", "User-Agent": "doloop-slop-killswitch"})
    try:
        urllib.request.urlopen(req, timeout=30)
        sys.stderr.write("workflow disabled via API (no future runs will fire).\n")
    except Exception as e:
        sys.stderr.write(f"[warn] could not self-disable workflow: {e}\n")   # DORMANT.md + skip still apply

def _write_dormant(age_days):
    open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "DORMANT.md"), "w").write(
        f"# Dormant\n\nThis corpus auto-closed after {age_days} days with no external interest "
        f"(no stars, forks, watchers, or issues) - the kill switch in `killswitch.py`.\n\n"
        f"The data already collected stays public. To resume, re-enable the **slop-corpus-collect** "
        f"workflow in the Actions tab; the next scheduled run picks up where it left off.\n")

def _emit(dormant, note=""):
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a") as f:
            f.write(f"dormant={'true' if dormant else 'false'}\n")
    print(f"dormant={'true' if dormant else 'false'}  ({note})")
    return 0

if __name__ == "__main__":
    sys.exit(main())
