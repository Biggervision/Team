import json
d=json.load(open("src/words.json"))
W=[w for s in d["segs"] for w in s["words"]]
# keep intervals: cut gaps > 0.30s down to ~0.12s
PAD=0.06
keep=[[max(0,W[0]["s"]-0.08),None]]
for a,b in zip(W,W[1:]):
    if b["s"]-a["e"]>0.30:
        keep[-1][1]=a["e"]+PAD; keep.append([b["s"]-PAD,None])
keep[-1][1]=W[-1]["e"]+0.35
# map old->new
def m(t):
    acc=0
    for s,e in keep:
        if t<s: return acc
        if t<=e: return acc+t-s
        acc+=e-s
    return acc
for i,w in enumerate(W): w["ns"]=round(m(w["s"]),3); w["ne"]=round(m(w["e"]),3); w["i"]=i
json.dump({"keep":keep,"words":W},open("cut.json","w"))
print(len(keep),"segments; new dur",round(sum(e-s for s,e in keep),2))
print(" ".join(f'{w["i"]}:{w["w"].strip()}@{w["ns"]}' for w in W))
