#!/usr/bin/env python3
"""doloop slop-corpus collector: ask the fixed situational prompts (prompts.json) to the LATEST models
via OpenRouter, save a dated snapshot to data/. Latest chat flagship per lab is auto-detected each run,
so the corpus tracks new releases automatically. OPENROUTER_API_KEY from env. Usage: collect.py <YYYY-MM-DD>"""
import urllib.request, json, os, sys, time, signal, hashlib
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
PARAMS={"temperature":0.7,"max_tokens":700,"reasoning_effort":"low"}   # recorded per row for reproducibility
def gen(k,model,text):
    body=json.dumps({"model":model,"messages":[{"role":"user","content":text}],"temperature":PARAMS["temperature"],"max_tokens":PARAMS["max_tokens"],"reasoning":{"effort":PARAMS["reasoning_effort"]}}).encode()
    req=urllib.request.Request(OR+"/chat/completions",body,{"Authorization":f"Bearer {k}","Content-Type":"application/json","HTTP-Referer":"https://doloop.io","X-Title":"doloop-slop-corpus"})
    for a in range(2):                                   # 2 tries; a dead/slow model costs ~2.5min not hours
        try:
            signal.alarm(75)                             # hard total deadline (beats urllib's per-read timeout)
            r=json.load(urllib.request.urlopen(req,timeout=60)); signal.alarm(0)
            ch=(r.get("choices") or [{}])[0]; c=ch.get("message",{}).get("content"); u=r.get("usage") or {}
            meta={"or_model":r.get("model"),"finish_reason":ch.get("finish_reason"),
                  "prompt_tokens":u.get("prompt_tokens"),"completion_tokens":u.get("completion_tokens"),"attempts":a+1}
            if c: return c, meta
        except urllib.error.HTTPError as e:
            signal.alarm(0); sys.stderr.write(f"[err {model} a{a}] HTTP {e.code}\n")
            if e.code in (400,404):break              # bad/unknown model id - not transient, don't retry
            time.sleep(4)
        except _Deadline: sys.stderr.write(f"[err {model} a{a}] deadline 75s\n"); time.sleep(2)
        except Exception as e: signal.alarm(0); sys.stderr.write(f"[err {model} a{a}] {e}\n"); time.sleep(4)
    signal.alarm(0); return None, None
def main(argv):
    date=argv[0] if argv else "undated"; k=key()
    backfill = len(argv)>1 and argv[1]=="backfill"
    os.makedirs(os.path.join(HERE,"data"),exist_ok=True)
    prompts_raw=open(os.path.join(HERE,"prompts.json"),"rb").read()
    prompts=json.loads(prompts_raw)["prompts"]
    pset_sha=hashlib.sha256(prompts_raw).hexdigest()[:16]   # which prompt version produced this snapshot
    models = HISTORICAL if backfill else latest()
    era = "backfill" if backfill else "latest"
    sys.stderr.write(f"{era} models: "+", ".join(models)+"\n")
    stem=f"{'backfill' if backfill else 'or'}_{date}"
    out=os.path.join(HERE,"data",stem+".jsonl"); n=0; served=set()
    with open(out,"w") as f:
        for model in models:
            for i,p in enumerate(prompts):
                t,meta=gen(k,model,p["text"])
                if t:
                    m=meta or {}
                    f.write(json.dumps({"date":date,"era":era,"model":model,"or_model":m.get("or_model"),
                        "prompt_id":p["id"],"situation":p["situation"],"voice":p.get("voice"),
                        "finish_reason":m.get("finish_reason"),"prompt_tokens":m.get("prompt_tokens"),
                        "completion_tokens":m.get("completion_tokens"),"params":PARAMS,"text":t})+"\n")
                    n+=1; served.add(model)
                elif i==0:                             # first prompt hard-failed -> model is down/retired; skip its rest
                    sys.stderr.write(f"[skip {model}] first call failed, skipping remaining {len(prompts)-1}\n"); break
    # per-snapshot manifest: everything needed to reproduce/interpret this file
    manifest={"date":date,"era":era,"schema":"doloop-slop-corpus/data/v2","params":PARAMS,
              "prompt_set_sha256_16":pset_sha,"n_prompts":len(prompts),"n_generations":n,
              "models_requested":models,"models_served":sorted(served)}
    json.dump(manifest,open(os.path.join(HERE,"data",stem+".manifest.json"),"w"),indent=1)
    print(f"{n} generations from {len(served)}/{len(models)} {era} models x {len(prompts)} situations -> {out}")
    return 0
if __name__=="__main__": sys.exit(main(sys.argv[1:]))
