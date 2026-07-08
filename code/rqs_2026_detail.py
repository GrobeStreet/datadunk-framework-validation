import csv
from collections import defaultdict
pick={}
with open("/tmp/draft.csv",newline='') as f:
    for r in csv.DictReader(f):
        try: pick[r["PERSON_ID"]]=int(float(r["OVERALL_PICK"]))
        except: pass
# playoff field 2026: 6 auto per conf + play-in. Use actual 16 (seeds 1-6 + play-in winners).
# Auto (clinched top-6): 
auto={"DET","BOS","NYK","CLE","TOR","ATL","OKC","SAS","DEN","LAL","HOU","MIN"}
# play-in seeds 7-10 East: PHI ORL CHA MIA ; West: PHX POR LAC GSW
playin={"PHI","ORL","CHA","MIA","PHX","POR","LAC","GSW"}
teams=defaultdict(list)
with open("/tmp/adv_2025-26.csv",newline='') as f:
    for r in csv.DictReader(f):
        try:
            gp=float(r["GP"]);mpg=float(r["MIN"]);net=float(r["NET_RATING"])
            usg=float(r["USG_PCT"]);ts=float(r["TS_PCT"]);dreb=float(r["DREB_PCT"])
        except: continue
        teams[r["TEAM_ABBREVIATION"]].append(dict(pid=r["PLAYER_ID"],nm=r["PLAYER_NAME"],gp=gp,mpg=mpg,net=net,aqi=net*usg*(ts/0.55),dreb=dreb))
def comp(pl):
    rot=[p for p in pl if p["gp"]>=40 and p["mpg"]>=20]
    a=sorted(rot,key=lambda p:-p["aqi"])
    aqi1=a[0]["aqi"] if a else 0; aqi2=a[1]["aqi"] if len(a)>1 else 0
    anchor=1 if any(p["dreb"]>0.18 and p["net"]>3 and p["gp"]>=20 for p in pl) else 0
    late=min(sum(1 for p in pl if p["gp"]>=20 and p["net"]>3 and pick.get(p["pid"],99)>=20),3)
    return aqi1,aqi2,anchor,late,aqi1*4+aqi2*2+anchor*3+late,(a[0]["nm"] if a else"-"),(a[1]["nm"] if len(a)>1 else"-")
rows=[]
for tm,pl in teams.items():
    aqi1,aqi2,anc,late,rqs,n1,n2=comp(pl)
    rows.append((tm,rqs,aqi1,aqi2,anc,late,n1,n2))
rows.sort(key=lambda r:-r[1])
print("2026 RQS ranking (all 30) — PO=auto/play-in/miss")
for i,(tm,rqs,a1,a2,anc,late,n1,n2) in enumerate(rows,1):
    po="AUTO" if tm in auto else ("play-in" if tm in playin else "MISS")
    star="  <== NYK CHAMPION" if tm=="NYK" else ""
    print(f"{i:2d}. {tm:3s} RQS={rqs:5.1f} [{po:7s}] AQI1={a1:4.1f}({n1}) AQI2={a2:4.1f}({n2}) anc={anc} late={late}{star}")
# rank among playoff-relevant teams (auto + play-in field = 20; and among strict 16 auto+bracket)
field=[r for r in rows if r[0] in auto or r[0] in playin]
rank_field=[i for i,r in enumerate(field,1) if r[0]=="NYK"][0]
auto_only=[r for r in rows if r[0] in auto]
rank_auto=[i for i,r in enumerate(auto_only,1) if r[0]=="NYK"][0]
print(f"\nNYK RQS rank among AUTO playoff teams (12): {rank_auto}")
print(f"NYK RQS rank among full playoff field auto+playin (20): {rank_field}")
