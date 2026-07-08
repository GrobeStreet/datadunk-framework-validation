import csv, numpy as np
from collections import defaultdict
rows=[]
with open("/tmp/ts.csv",newline='') as f:
    r=csv.DictReader(f); H=r.fieldnames
    wev3=[c for c in H if c.startswith("WEV v3")][0]
    for d in r:
        try:
            yr=int(d["Season"])
            if yr<2000 or yr>2023: continue
            rows.append({"yr":yr,"champ":int(d["is_champion"]),
              "WEV_v3":float(d[wev3]),"CPV":float(d["CPV"]),
              "NetRtg":float(d["NetRtg"]),"SRS":float(d["SRS"]),"WPCT":float(d["W_PCT"])})
        except: pass
TEST=set(range(2016,2024)); te=[x for x in rows if x["yr"] in TEST]
def stats(data,key):
    by=defaultdict(list)
    for x in data: by[x["yr"]].append(x)
    ranks=[]
    for yr,lst in by.items():
        s=sorted(lst,key=lambda z:-z[key])
        for i,x in enumerate(s,1):
            if x["champ"]==1: ranks.append(i);break
    ranks=np.array(ranks)
    v=np.array([x[key] for x in data]);c=np.array([x["champ"] for x in data],float)
    r=np.corrcoef(v,c)[0,1]
    return ranks.mean(),(ranks<=1).sum(),(ranks<=3).sum(),(ranks<=5).sum(),r,len(ranks)
print("OOS 2016-2023 (held-out era) — does the composite beat the trivial baseline?")
print(f"{'metric':8s} | meanRank | top1 | top3 | top5 | r(champ)")
for k in ["WEV_v3","CPV","NetRtg","SRS","WPCT"]:
    mr,t1,t3,t5,r,n=stats(te,k)
    print(f"{k:8s} | {mr:7.2f}  | {t1}/{n}  | {t3}/{n}  | {t5}/{n}  | {r:+.3f}")
