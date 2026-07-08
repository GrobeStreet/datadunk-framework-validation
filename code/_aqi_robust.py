import csv, math
from collections import defaultdict
BASE="/sessions/vibrant-confident-faraday/mnt/Basketball Stats Book"
CHAMPS={1997:"CHI",1998:"CHI",1999:"SAS",2000:"LAL",2001:"LAL",2002:"LAL",2003:"SAS",2004:"DET",2005:"SAS",2006:"MIA",2007:"SAS",2008:"BOS",2009:"LAL",2010:"LAL",2011:"DAL",2012:"MIA",2013:"MIA",2014:"SAS",2015:"GSW",2016:"CLE",2017:"GSW",2018:"GSW",2019:"TOR",2020:"LAL",2021:"MIL",2022:"GSW",2023:"DEN"}
def pearson(x,y):
    n=len(x);mx=sum(x)/n;my=sum(y)/n
    sxy=sum((a-mx)*(b-my) for a,b in zip(x,y));sxx=sum((a-mx)**2 for a in x);syy=sum((b-my)**2 for b in y)
    return sxy/math.sqrt(sxx*syy) if sxx and syy else float('nan')
def endyear(s):a,b=s.split("-");return int(a)+1
def run(gpmin,mpgmin,ymin,ymax):
    net=defaultdict(list);bpm=defaultdict(list)
    with open(f"{BASE}/nbacom_advanced_rs_1996_2023.csv",newline='') as f:
        for row in csv.DictReader(f):
            try:
                if float(row["GP"])<gpmin or float(row["MIN"])<mpgmin:continue
                n=float(row["NET_RATING"]);u=float(row["USG_PCT"]);t=float(row["TS_PCT"])
            except:continue
            if u>1.5:u/=100
            ey=endyear(row["SEASON"])
            if ey<ymin or ey>ymax:continue
            net[(ey,row["TEAM_ABBREVIATION"])].append(n*u*(t/0.55))
    with open(f"{BASE}/bbref_advanced_1947_2024.csv",newline='') as f:
        for row in csv.DictReader(f):
            try:
                ey=int(row["season"])
                if ey<ymin or ey>ymax:continue
                if row["tm"] in("TOT",""):continue
                g=float(row["g"]);mp=float(row["mp"] or 0)
                if g<gpmin or mp/g<mpgmin:continue
                b=float(row["bpm"]);u=float(row["usg_percent"]);t=float(row["ts_percent"])
            except:continue
            if u>1.5:u/=100
            bpm[(ey,row["tm"])].append(b*u*(t/0.55))
    def rc(d):
        rows=[(max(v),1 if CHAMPS[k[0]]==k[1] else 0) for k,v in d.items() if k[0] in CHAMPS]
        return pearson([r[0] for r in rows],[r[1] for r in rows]),len(rows)
    rn,n1=rc(net);rb,_=rc(bpm)
    print(f"filter GP>={gpmin} MPG>={mpgmin} yrs {ymin}-{ymax} (n={n1}): net r={rn:.3f}  bpm r={rb:.3f}  delta={rn-rb:+.3f}")
run(40,20,1997,2023)
run(50,24,1997,2023)   # stricter
run(40,20,2000,2023)   # match doc window
run(58,28,2000,2023)   # very strict (near-star only)
