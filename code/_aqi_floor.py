import csv, math
from collections import defaultdict
BASE="/sessions/vibrant-confident-faraday/mnt/Basketball Stats Book"
CHAMPS={1997:"CHI",1998:"CHI",1999:"SAS",2000:"LAL",2001:"LAL",2002:"LAL",2003:"SAS",2004:"DET",2005:"SAS",2006:"MIA",2007:"SAS",2008:"BOS",2009:"LAL",2010:"LAL",2011:"DAL",2012:"MIA",2013:"MIA",2014:"SAS",2015:"GSW",2016:"CLE",2017:"GSW",2018:"GSW",2019:"TOR",2020:"LAL",2021:"MIL",2022:"GSW",2023:"DEN"}
def endyear(s):a,b=s.split("-");return int(a)+1
# anchor (top1) with the player name, per team-season
team=defaultdict(list)  # (ey,tm)->[(aqi,player)]
with open(f"{BASE}/nbacom_advanced_rs_1996_2023.csv",newline='') as f:
    for row in csv.DictReader(f):
        try:
            if float(row["GP"])<40 or float(row["MIN"])<20:continue
            n=float(row["NET_RATING"]);u=float(row["USG_PCT"]);t=float(row["TS_PCT"])
        except:continue
        if u>1.5:u/=100
        ey=endyear(row["SEASON"])
        team[(ey,row["TEAM_ABBREVIATION"])].append((n*u*(t/0.55),row["PLAYER_NAME"]))
anchors=[]  # (ey,tm,aqi,player,is_champ)
for (ey,tm),lst in team.items():
    if ey not in CHAMPS:continue
    a,p=max(lst,key=lambda z:z[0])
    anchors.append((ey,tm,a,p,1 if CHAMPS[ey]==tm else 0))

def report(ymin,ymax,label):
    ch=[r for r in anchors if r[4]==1 and ymin<=r[0]<=ymax]
    non=[r for r in anchors if r[4]==0 and ymin<=r[0]<=ymax]
    ch_sorted=sorted(ch,key=lambda r:r[2])
    floor=ch_sorted[0][2]
    print(f"\n===== {label} ({len(ch)} champions, {len(non)} non-champ team-seasons) =====")
    print(f"Champion anchor AQI: min={floor:.3f}  median={ch_sorted[len(ch)//2][2]:.3f}  max={ch_sorted[-1][2]:.3f}  mean={sum(r[2] for r in ch)/len(ch):.3f}")
    print(f"FLOOR (min champion anchor) = {floor:.3f}  set by {ch_sorted[0][0]} {ch_sorted[0][1]} ({ch_sorted[0][3]})")
    print("3 lowest champion anchors (the stress tests):")
    for r in ch_sorted[:3]: print(f"   {r[0]} {r[1]:4s} {r[3]:22s} AQI={r[2]:.3f}")
    # specificity of the floor
    for thr,name in [(floor,"floor (min champ)"),(1.75,"old-scale 1.75"),(2.0,""),(2.5,""),(3.0,"")]:
        chn=sum(1 for r in ch if r[2]>=thr); nn=sum(1 for r in non if r[2]>=thr)
        print(f"   thr>={thr:.2f} {name:18s}: champs {chn}/{len(ch)} ({100*chn/len(ch):.0f}%) | non-champs clearing {nn}/{len(non)} ({100*nn/len(non):.0f}%)")

report(2000,2023,"2000-2023 (matches old 24/24 canon)")
report(1997,2023,"1997-2023 (full file)")
