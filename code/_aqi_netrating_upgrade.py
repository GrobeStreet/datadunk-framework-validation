#!/usr/bin/env python3
"""
AQI real-net-rating upgrade + head-to-head vs BPM proxy.

AQI = net_rating_factor * usage * (TS / 0.550), per player-season (regular season).
Team anchor = AQI_top1 = highest-AQI rotation player on a team-season.
Target = is_champion (external binary).

Two versions on the SAME team-season population + same champion labels:
  - AQI_bpm : uses Basketball-Reference BPM as the net-rating proxy (status quo)
  - AQI_net : uses NBA.com real on-court NET_RATING (the upgrade)

Rotation filter: GP >= 40 and MPG >= 20.
"""
import csv, math
from collections import defaultdict

BASE = "/sessions/vibrant-confident-faraday/mnt/Basketball Stats Book"

# Champions by season END year -> team abbr (standard). File coverage: 1997-2023.
CHAMPS = {
    1997:"CHI",1998:"CHI",1999:"SAS",2000:"LAL",2001:"LAL",2002:"LAL",2003:"SAS",
    2004:"DET",2005:"SAS",2006:"MIA",2007:"SAS",2008:"BOS",2009:"LAL",2010:"LAL",
    2011:"DAL",2012:"MIA",2013:"MIA",2014:"SAS",2015:"GSW",2016:"CLE",2017:"GSW",
    2018:"GSW",2019:"TOR",2020:"LAL",2021:"MIL",2022:"GSW",2023:"DEN",
}

def pearson(x, y):
    n=len(x); mx=sum(x)/n; my=sum(y)/n
    sxy=sum((a-mx)*(b-my) for a,b in zip(x,y))
    sxx=sum((a-mx)**2 for a in x); syy=sum((b-my)**2 for b in y)
    if sxx==0 or syy==0: return float('nan')
    return sxy/math.sqrt(sxx*syy)

def season_endyear_nbacom(s):   # "1996-97" -> 1997
    a,b=s.split("-"); return int(a[:2]+b) if int(b)>50 else int(str(int(a)+1))
def endyear_nbacom(s):
    a,b=s.split("-"); yr=int(a); return yr+1  # 1996-97 -> 1997

# ---------- Build AQI_net from NBA.com advanced ----------
net_team = defaultdict(list)   # (endyear, team) -> [aqi,...]
with open(f"{BASE}/nbacom_advanced_rs_1996_2023.csv", newline='') as f:
    r=csv.DictReader(f)
    for row in r:
        try:
            gp=float(row["GP"]); mpg=float(row["MIN"])
            if gp<40 or mpg<20: continue
            net=float(row["NET_RATING"]); usg=float(row["USG_PCT"]); ts=float(row["TS_PCT"])
        except: continue
        if usg>1.5: usg=usg/100.0   # normalize if percent-scaled
        aqi = net * usg * (ts/0.550)
        ey = endyear_nbacom(row["SEASON"])
        net_team[(ey,row["TEAM_ABBREVIATION"])].append(aqi)

# ---------- Build AQI_bpm from Basketball-Reference advanced ----------
bpm_team = defaultdict(list)
with open(f"{BASE}/bbref_advanced_1947_2024.csv", newline='') as f:
    r=csv.DictReader(f)
    for row in r:
        try:
            ey=int(row["season"])
            if ey<1997 or ey>2023: continue
            tm=row["tm"]
            if tm in ("TOT",""): continue
            g=float(row["g"]); mp=float(row["mp"] or 0)
            if g<40 or (mp/g)<20: continue
            bpm=float(row["bpm"]); usg=float(row["usg_percent"]); ts=float(row["ts_percent"])
        except: continue
        if usg>1.5: usg=usg/100.0
        aqi = bpm * usg * (ts/0.550)
        bpm_team[(ey,tm)].append(aqi)

def anchor_panel(team_dict):
    rows=[]  # (endyear, team, aqi_top1, is_champ)
    for (ey,tm),vals in team_dict.items():
        if ey not in CHAMPS: continue
        top1=max(vals)
        is_ch = 1 if CHAMPS[ey]==tm else 0
        rows.append((ey,tm,top1,is_ch))
    return rows

def analyze(name, rows):
    x=[r[2] for r in rows]; y=[r[3] for r in rows]
    r_champ=pearson(x,y)
    champs=[r for r in rows if r[3]==1]
    noch=[r for r in rows if r[3]==0]
    mc=sum(c[2] for c in champs)/len(champs)
    mn=sum(c[2] for c in noch)/len(noch)
    # rank check: for each champ season, rank champion anchor among that season's teams
    by_season=defaultdict(list)
    for r in rows: by_season[r[0]].append(r)
    top5=0; top3=0; top1c=0; ranks=[]
    for ey,ch_tm in CHAMPS.items():
        srows=by_season.get(ey,[])
        if not srows: continue
        srows_sorted=sorted(srows,key=lambda r:-r[2])
        for i,r in enumerate(srows_sorted,1):
            if r[3]==1:
                ranks.append(i)
                if i<=5: top5+=1
                if i<=3: top3+=1
                if i==1: top1c+=1
                break
    nch=len(ranks)
    print(f"\n===== {name} =====")
    print(f"team-seasons: {len(rows)}  | champion rows: {len(champs)}")
    print(f"r(anchor AQI, is_champion) = {r_champ:.3f}")
    print(f"champion mean anchor AQI = {mc:.3f} | non-champ mean = {mn:.3f} | gap = {mc-mn:.3f}")
    print(f"champion anchor rank within season: mean={sum(ranks)/nch:.2f}  top1={top1c}/{nch}  top3={top3}/{nch}  top5={top5}/{nch}")
    return r_champ

rows_net=anchor_panel(net_team)
rows_bpm=anchor_panel(bpm_team)
r_net=analyze("AQI_net (real NBA.com on-court NET_RATING)  [UPGRADE]", rows_net)
r_bpm=analyze("AQI_bpm (Basketball-Reference BPM proxy)     [STATUS QUO]", rows_bpm)

print("\n===== HEAD-TO-HEAD =====")
print(f"r_champ  real-net = {r_net:.3f}   vs   BPM-proxy = {r_bpm:.3f}   (delta {r_net-r_bpm:+.3f})")
print(f"IRONCLAD BAR r>=0.35 : real-net {'PASS' if r_net>=0.35 else 'FAIL'} | bpm {'PASS' if r_bpm>=0.35 else 'FAIL'}")
