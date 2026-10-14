import json
d=json.load(open("src/words.json")); e=json.load(open("src/end_words.json"))
W=[w for s in d["segs"] for w in s["words"]]
fi=[i for i,w in enumerate(W) if w["w"].strip().lower().startswith("follow")][0]
W=W[:fi]                      # main video up to its own CTA (replaced by the ending clip)
E=[w for s in e["segs"] for w in s["words"]]
PAD=0.06
keep=[["main",max(0,W[0]["s"]-0.08),None]]
for a,b in zip(W,W[1:]):
    if b["s"]-a["e"]>0.30:
        keep[-1][2]=a["e"]+PAD; keep.append(["main",b["s"]-PAD,None])
keep[-1][2]=W[-1]["e"]+0.18
keep.append(["end",max(0,E[0]["s"]-0.05),min(4.43,E[-1]["e"]+0.35)])
def m(src,t):
    acc=0
    for k,s,e_ in keep:
        if k==src and s<=t<=e_: return acc+t-s
        if k==src and t<s: return acc
        acc+=e_-s
    return acc
out=[]
for w in W: out.append({"w":w["w"],"ns":round(m("main",w["s"]),3),"ne":round(m("main",w["e"]),3)})
for w in E: out.append({"w":w["w"],"ns":round(m("end",w["s"]),3),"ne":round(m("end",w["e"]),3)})
for i,w in enumerate(out): w["i"]=i
json.dump({"keep":[[s,e_] for _,s,e_ in keep],"src":keep,"words":out},open("cut.json","w"))
print(len(keep),"segs; dur",round(sum(e_-s for _,s,e_ in keep),2))
print(" ".join(f'{w["i"]}:{w["w"].strip()}@{w["ns"]}' for w in out))
