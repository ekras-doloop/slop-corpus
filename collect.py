#!/usr/bin/env python3
"""doloop slop-corpus collector: ask the fixed situational prompts (prompts.json) to the LATEST models
via OpenRouter, save a dated snapshot to data/. Latest chat flagship per lab is auto-detected each run,
so the corpus tracks new releases automatically. OPENROUTER_API_KEY from env. Usage: collect.py <YYYY-MM-DD>"""
import urllib.request, json, os, sys, time
OR="https://openrouter.ai/api/v1"; HERE=os.path.dirname(os.path.abspath(__file__))
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
        if lab not in best or m.get("created",0)>best[lab]["created"]: best[lab]={"id":mid,"c":m.get("created",0)}
    return [best[l]["id"] for l in LABS if l in best]
def gen(k,model,text):
    body=json.dumps({"model":model,"messages":[{"role":"user","content":text}],"temperature":0.7,"max_tokens":1200,"reasoning":{"effort":"low"}}).encode()
    req=urllib.request.Request(OR+"/chat/completions",body,{"Authorization":f"Bearer {k}","Content-Type":"application/json","HTTP-Referer":"https://doloop.io","X-Title":"doloop-slop-corpus"})
    for a in range(3):
        try:
            r=json.load(urllib.request.urlopen(req,timeout=90)); c=(r.get("choices") or [{}])[0].get("message",{}).get("content")
            if c: return c
        except Exception as e: sys.stderr.write(f"[err {model} a{a}] {e}\n"); time.sleep(4)
    return None
def main(argv):
    date=argv[0] if argv else "undated"; k=key()
    prompts=json.load(open(os.path.join(HERE,"prompts.json")))["prompts"]; models=latest()
    sys.stderr.write("latest models: "+", ".join(models)+"\n")
    out=os.path.join(HERE,"data",f"or_{date}.jsonl"); n=0
    with open(out,"w") as f:
        for model in models:
            for p in prompts:
                t=gen(k,model,p["text"])
                if t: f.write(json.dumps({"date":date,"model":model,"prompt_id":p["id"],"situation":p["situation"],"text":t})+"\n"); n+=1
    print(f"{n} generations from {len(models)} latest models x {len(prompts)} situations -> {out}")
    return 0
if __name__=="__main__": sys.exit(main(sys.argv[1:]))
