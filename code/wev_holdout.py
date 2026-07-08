import csv, numpy as np
from collections import defaultdict

rows=[]
with open("/tmp/ts.csv", newline='') as f:
    r=csv.DictReader(f)
    H=r.fieldnames
    wev3_col=[c for c in H if c.startswith("WEV v3")][0]
    for d in r:
        try:
            yr=int(d["Season"])
            if yr<2000 or yr>2023: continue
            rows.append({
                "yr":yr,"tm":d["Abbrev"],
                "champ":int(d["is_champion"]),
                "OEV":float(d["OEV"]),"DEV":float(d["DEV"]),"CEV":float(d["CEV_partial"]),
                "CPV":float(d["CPV"]),"WEV_v2":float(d["WEV_v2"]),
                "WEV_v3":float(d[wev3_col]),
            })
        except: pass

TRAIN=set(range(2000,2016)); TEST=set(range(2016,2024))
def split(era): return [x for x in rows if x["yr"] in era]

def champ_rank_stats(data, key):
    by=defaultdict(list)
    for x in data: by[x["yr"]].append(x)
    ranks=[]
    for yr,lst in by.items():
        s=sorted(lst,key=lambda z:-z[key])
        for i,x in enumerate(s,1):
            if x["champ"]==1: ranks.append(i); break
    ranks=np.array(ranks)
    return len(ranks),ranks.mean(),(ranks<=1).sum(),(ranks<=3).sum(),(ranks<=5).sum()

def pb_r(data,key):
    v=np.array([x[key] for x in data]); c=np.array([x["champ"] for x in data],float)
    if v.std()==0 or c.std()==0: return float('nan')
    return np.corrcoef(v,c)[0,1]

print("="*74)
print("TEST 1 — FROZEN CANON METRICS: does champion identification hold OOS?")
print("="*74)
tr=split(TRAIN); te=split(TEST)
print(f"{'metric':10s} | {'era':5s} | nCh | meanRank | top1 | top3 | top5 | r(champ)")
for key in ["WEV_v3","CPV","WEV_v2"]:
    for era,name in [(tr,"train"),(te,"TEST")]:
        n,mr,t1,t3,t5=champ_rank_stats(era,key)
        print(f"{key:10s} | {name:5s} | {n:3d} | {mr:7.2f}  | {t1:3d}/{n} | {t3:3d}/{n} | {t5:3d}/{n} | {pb_r(era,key):+.3f}")
    print("-"*74)

print()
print("="*74)
print("TEST 2 — REFIT WEIGHTS ON 2000-2015, FREEZE, APPLY TO 2016-2023")
print("="*74)
# standardize OEV/DEV/CEV using TRAIN scaler (frozen)
feats=["OEV","DEV","CEV"]
Xtr=np.array([[x[f] for f in feats] for x in tr]); ytr=np.array([x["champ"] for x in tr],float)
mu=Xtr.mean(0); sd=Xtr.std(0)
Ztr=(Xtr-mu)/sd
# logistic regression via gradient descent (L2)
w=np.zeros(3); b=0.0; lr=0.1; lam=1e-3
for it in range(20000):
    z=Ztr@w+b; p=1/(1+np.exp(-z)); g=p-ytr
    gw=Ztr.T@g/len(ytr)+lam*w; gb=g.mean()
    w-=lr*gw; b-=lr*gb
absw=np.abs(w); norm=absw/absw.sum()
print(f"Fitted logistic coefs (standardized): OEV={w[0]:+.3f} DEV={w[1]:+.3f} CEV={w[2]:+.3f}")
print(f"Implied |weight| share:  OEV={norm[0]:.2f}  DEV={norm[1]:.2f}  CEV={norm[2]:.2f}")
print(f"Canon WEV_v3 weights:    OEV=0.30  DEV=0.60  CEV=0.10")
# apply frozen scaler+weights to TEST
Xte=np.array([[x[f] for f in feats] for x in te])
Zte=(Xte-mu)/sd
score_te=Zte@w+b
for x,s in zip(te,score_te): x["FIT"]=s
# also score train for reference
for x,s in zip(tr,Ztr@w+b): x["FIT"]=s
print()
print(f"{'model':16s} | era  | nCh | meanRank | top1 | top3 | top5")
for key,label in [("FIT","refit-logistic"),("WEV_v3","canon WEV_v3")]:
    for era,name in [(tr,"train"),(te,"TEST")]:
        n,mr,t1,t3,t5=champ_rank_stats(era,key)
        print(f"{label:16s} | {name:5s}| {n:3d} | {mr:7.2f}  | {t1:3d}/{n} | {t3:3d}/{n} | {t5:3d}/{n}")
    print("-"*66)
