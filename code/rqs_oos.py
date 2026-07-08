import csv
from collections import defaultdict
# draft map: person_id -> overall pick
pick={}
with open("/tmp/draft.csv",newline='') as f:
    for r in csv.DictReader(f):
        try: pick[r["PERSON_ID"]]=int(float(r["OVERALL_PICK"]))
        except: pass
SEASONS={"2022-23":(2023,"DEN","in-sample control"),
         "2023-24":(2024,"BOS","HELD OUT"),
         "2024-25":(2025,"OKC","HELD OUT"),
         "2025-26":(2026,"NYK","HELD OUT")}
def compute(season):
    teams=defaultdict(list)
    with open(f"/tmp/adv_{season}.csv",newline='') as f:
        for r in csv.DictReader(f):
            try:
                gp=float(r["GP"]);mpg=float(r["MIN"]);net=float(r["NET_RATING"])
                usg=float(r["USG_PCT"]);ts=float(r["TS_PCT"]);dreb=float(r["DREB_PCT"])
            except: continue
            aqi=net*usg*(ts/0.55)
            teams[r["TEAM_ABBREVIATION"]].append(dict(pid=r["PLAYER_ID"],gp=gp,mpg=mpg,net=net,aqi=aqi,dreb=dreb))
    rqs={}
    for tm,pl in teams.items():
        rot=[p for p in pl if p["gp"]>=40 and p["mpg"]>=20]
        aqis=sorted([p["aqi"] for p in rot],reverse=True)
        aqi1=aqis[0] if aqis else 0; aqi2=aqis[1] if len(aqis)>1 else 0
        anchor=1 if any(p["dreb"]>0.18 and p["net"]>3 and p["gp"]>=20 for p in pl) else 0
        late=sum(1 for p in pl if p["gp"]>=20 and p["net"]>3 and (pick.get(p["pid"],99)>=20))
        late=min(late,3)
        rqs[tm]=aqi1*4+aqi2*2+anchor*3+late*1
    return rqs
print(f"{'season':7s} {'champ':4s} {'kind':18s} | champ RQS rank (of 30) | top-5? | champ RQS | RQS #1 team")
for season,(ey,champ,kind) in SEASONS.items():
    rqs=compute(season)
    ranked=sorted(rqs.items(),key=lambda kv:-kv[1])
    rank=[i for i,(tm,_) in enumerate(ranked,1) if tm==champ][0]
    top1=ranked[0]
    print(f"{ey:<7d} {champ:4s} {kind:18s} | {rank:^20d} | {'YES' if rank<=5 else 'NO':^6s} | {rqs[champ]:8.2f} | {top1[0]} ({top1[1]:.1f})")
    top5=", ".join(f"{tm}:{v:.1f}" for tm,v in ranked[:5])
    print(f"        top-5 RQS: {top5}")
