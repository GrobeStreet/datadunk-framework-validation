#!/usr/bin/env python3
"""Reproduce the Sept. 12, 2026 naive preseason RQS test.

Input: canonical team-season CSV with Season, franchise/team code, W_PCT,
NetRtg, RQS, AQI2, and Floor Pct. The model uses each franchise's prior
season features to predict current-season W_PCT and evaluates leave-one-target-
season-out OOS linear regression over 2001-2024.

This intentionally tests a naive lag, not a projected returning-roster model.
"""
from __future__ import annotations
import argparse, csv, math
import numpy as np

ALIASES = {
    "RQS": ["RQS", "RQS = AQI1×4 + AQI2×2 + anchor×3 + late_picks×1"],
    "AQI2": ["AQI2", "AQI #2 player"],
    "FLOOR": ["Floor Pct", "Floor%", "Floor Pct (% roster NR>2)"],
    "NET": ["NetRtg", "NET_RATING", "Net Rating"],
    "WPCT": ["W_PCT", "W%", "WIN_PCT"],
    "TEAM": ["Abbrev", "Team", "TEAM_ABBREVIATION"],
    "SEASON": ["Season", "season", "YEAR"],
}
FRANCHISE = {
    "NJN": "BKN", "BKN": "BKN", "NOH": "NOP", "NOK": "NOP", "NOP": "NOP",
    "CHH": "CHA", "CHA": "CHA", "CHO": "CHA", "SEA": "OKC", "OKC": "OKC",
    "VAN": "MEM", "MEM": "MEM",
}

def col(fieldnames, key):
    for c in ALIASES[key]:
        if c in fieldnames:
            return c
    raise SystemExit(f"Missing required column for {key}: tried {ALIASES[key]}")

def fnum(x):
    try:
        v=float(x)
        return v if math.isfinite(v) else None
    except Exception:
        return None

def canon_team(x):
    x=(x or "").strip().upper()
    return FRANCHISE.get(x,x)

def fit_predict(train_X, train_y, test_X):
    X=np.asarray(train_X,float); y=np.asarray(train_y,float); T=np.asarray(test_X,float)
    X=np.column_stack([np.ones(len(X)),X]); T=np.column_stack([np.ones(len(T)),T])
    beta=np.linalg.lstsq(X,y,rcond=None)[0]
    return T@beta

def score(y,p):
    y=np.asarray(y,float); p=np.asarray(p,float)
    sse=float(np.sum((y-p)**2)); sst=float(np.sum((y-y.mean())**2))
    return 1-sse/sst, float(np.mean(np.abs(y-p))*82)

def oos(rows, features):
    ys=[]; ps=[]
    for s in sorted(set(r["season"] for r in rows)):
        te=[r for r in rows if r["season"]==s]
        tr=[r for r in rows if r["season"]!=s]
        if not te or len(tr) <= len(features)+2:
            continue
        pred=fit_predict([[r[k] for k in features] for r in tr],[r["y"] for r in tr],[[r[k] for k in features] for r in te])
        ys.extend(r["y"] for r in te); ps.extend(pred.tolist())
    return len(ys), score(ys,ps)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--panel",required=True); args=ap.parse_args()
    with open(args.panel,newline="",encoding="utf-8-sig") as f:
        rd=csv.DictReader(f); fn=rd.fieldnames or []
        cS,cT,cW,cN,cR,cA,cF=(col(fn,k) for k in ["SEASON","TEAM","WPCT","NET","RQS","AQI2","FLOOR"])
        base=[]
        for z in rd:
            try: season=int(float(z[cS]))
            except: continue
            rec={"season":season,"team":canon_team(z[cT]),"y":fnum(z[cW]),"net":fnum(z[cN]),"rqs":fnum(z[cR]),"aqi2":fnum(z[cA]),"floor":fnum(z[cF])}
            if rec["y"] is not None: base.append(rec)
    idx={(r["team"],r["season"]):r for r in base}
    rows=[]
    for r in base:
        if not (2001 <= r["season"] <= 2024): continue
        p=idx.get((r["team"],r["season"]-1))
        if not p: continue
        rows.append({"season":r["season"],"y":r["y"],"prior_wpct":p["y"],"prior_net":p["net"],"prior_rqs":p["rqs"],"prior_aqi2":p["aqi2"],"prior_floor":p["floor"]})
    rows=[r for r in rows if all(r.get(k) is not None for k in ["prior_wpct","prior_net","prior_rqs","prior_aqi2","prior_floor"])]
    specs=[
        ("prior W%",["prior_wpct"]), ("prior NetRtg",["prior_net"]), ("prior RQS",["prior_rqs"]),
        ("prior AQI2",["prior_aqi2"]), ("prior Floor%",["prior_floor"]),
        ("NetRtg + RQS",["prior_net","prior_rqs"]),
        ("NetRtg + RQS + Floor%",["prior_net","prior_rqs","prior_floor"]),
    ]
    print(f"eligible franchise-season rows before feature filtering: {len(rows)}")
    print("spec\tn\tOOS_R2\tMAE_wins")
    for name,feat in specs:
        n,(r2,mae)=oos(rows,feat)
        print(f"{name}\t{n}\t{r2:.3f}\t{mae:.1f}")

if __name__=="__main__": main()
