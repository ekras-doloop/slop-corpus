#!/usr/bin/env python3
"""doloop slop-corpus collector: ask the fixed situational prompts (prompts.json) to the LATEST models
via OpenRouter, save a dated snapshot to data/. Latest chat flagship per lab is auto-detected each run,
so the corpus tracks new releases automatically. OPENROUTER_API_KEY from env. Usage: collect.py <YYYY-MM-DD>"""
import urllib.request, json, os, sys, time, signal
OR="https://openrouter.ai/api/v1"; HERE=os.path.dirname(os.path.abspath(__file__))
# BACKFILL roster: notable OFF-LABEL (older) models, kept as HISTORICAL baseline points so slop DRIFT has
# an origin - you can't measure a trend from today forward only. Best-effort: any 404 (retired) just skips.
# Run once via `collect.py <date> backfill`; output tagged era:backfill in data/backfill_<date>.jsonl.
HISTORICAL=["openai/gpt-3.5-turbo","openai/gpt-4-turbo","anthropic/claude-2.1","anthropic/claude-3-haiku",
    "google/gemini-flash-1.5","google/gemma-2-27b-it","meta-llama/llama-2-70b-chat","meta-llama/llama-3-70b-instruct",
    "mistralai/mistral-7b-instruct","mistralai/mixtral-8x7b-instruct","deepseek/deepseek-chat","qwen/qwen-2-72b-instruct"]
class _Deadline(Exception): pass
def _alarm(sig,frm): raise _Deadline()
signal.signal(signal.SIGALRM,_alarm)   # hard TOTAL cap per call: urllib timeout is per-read, a trickle can hang past it
LABS=("anthropic","openai","google","meta-llama","mistralai","x-ai","deepseek","qwen")
SKIP=("guard","vision","embed","tts","whisper","image","audio","ocr","moderation","-free")
def key():
    k=os.environ.get("OPENROUTER_API_KEY")
    if not k: raise SystemExit("set OPENROUTER_API_KEY")
    return k
def latest():
    d=json.load(urllib.request.urlopen(OR+"/models",timeout=30))["data"]; best={}
    for m in d:
        mid=m["id"]; lab=mid.split("/")[0]
        if lab not in LABS or any(s in mid.lower() for s in SKIP): continue
        if lab not in best or m.get("created",0)>best[lab]["created"]: best[lab]={"id":mid,"created":m.get("created",0)}
    return [best[l]["id"] for l in LABS if l in best]
def gen(k,model,text):
    body=json.dumps({"model":model,"messages":[{"role":"user","content":text}],"temperature":0.7,"max_tokens":700,"reasoning":{"effort":"low"}}).encode()
    req=urllib.request.Request(OR+"/chat/completions",body,{"Authorization":f"Bearer {k}","Content-Type":"application/json","HTTP-Referer":"https://doloop.io","X-Title":"doloop-slop-corpus"})
    for a in range(2):                                   # 2 tries; a dead/slow model costs ~2.5min not hours
        try:
            signal.alarm(75)                             # hard total deadline (beats urllib's per-read timeout)
            r=json.load(urllib.request.urlopen(req,timeout=60)); c=(r.get("choices") or [{}])[0].get("message",{}).get("content")
            signal.alarm(0)
            if c: return c
        except urllib.error.HTTPError as e:
            signal.alarm(0); sys.stderr.write(f"[err {model} a{a}] HTTP {e.code}\n")
            if e.code in (400,404):break              # bad/unknown model id - not transient, don't retry
            time.sleep(4)
        except _Deadline: sys.stderr.write(f"[err {model} a{a}] deadline 75s\n"); time.sleep(2)
        except Exception as e: signal.alarm(0); sys.stderr.write(f"[err {model} a{a}] {e}\n"); time.sleep(4)
    signal.alarm(0); return None
def main(argv):
    date=argv[0] if argv else "undated"; k=key()
    backfill = len(argv)>1 and argv[1]=="backfill"
    os.makedirs(os.path.join(HERE,"data"),exist_ok=True)
    prompts=json.load(open(os.path.join(HERE,"prompts.json")))["prompts"]
    models = HISTORICAL if backfill else latest()
    era = "backfill" if backfill else "latest"
    sys.stderr.write(f"{era} models: "+", ".join(models)+"\n")
    out=os.path.join(HERE,"data",f"{'backfill' if backfill else 'or'}_{date}.jsonl"); n=0
    with open(out,"w") as f:
        for model in models:
            for i,p in enumerate(prompts):
                t=gen(k,model,p["text"])
                if t: f.write(json.dumps({"date":date,"era":era,"model":model,"prompt_id":p["id"],"situation":p["situation"],"voice":p.get("voice"),"text":t})+"\n"); n+=1
                elif i==0:                             # first prompt hard-failed -> model is down/retired; skip its rest
                    sys.stderr.write(f"[skip {model}] first call failed, skipping remaining {len(prompts)-1}\n"); break
    print(f"{n} generations from {len(models)} {era} models x {len(prompts)} situations -> {out}")
    return 0
if __name__=="__main__": sys.exit(main(sys.argv[1:]))
