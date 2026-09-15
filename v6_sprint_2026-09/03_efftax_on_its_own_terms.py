#!/usr/bin/env python3
"""Efficiency Tax reconstruction on its intended salary/availability target.

Required normalized columns:
season, team, w_pct, top3_salary_share, top3_availability, is_champion

fragility = top3_salary_share * (1 - top3_availability)

This script reports pooled correlations, per-season sign stability, champion-band
descriptives, and simple OLS R^2 decompositions. It does not claim causality and
it does not turn same-season availability into a forecast-safe variable.
"""
from __future__ import annotations
import argparse,csv,math
from collections import defaultdict
import numpy as np

def num(x):
    try:
        v=float(x); return v if math.isfinite(v) else None
    except:return None

def corr(a,b):
    a=np.asarray(a,float); b=np.asarray(b,float)
    return float(np.corrcoef(a,b)[0,1]) if len(a)>=3 and np.std(a)>0 and np.std(b)>0 else float('nan')

def ols_r2(rows, feats):
    X=np.array([[1]+[r[k] for k in feats] for r in rows],float); y=np.array([r['w_pct'] for r in rows],float)
    beta=np.linalg.lstsq(X,y,rcond=None)[0]; p=X@beta
    r2=1-float(np.sum((y-p)**2))/float(np.sum((y-y.mean())**2))
    return r2,beta[1:]

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--input',required=True); args=ap.parse_args()
    need=['season','team','w_pct','top3_salary_share','top3_availability','is_champion']
    rows=[]
    with open(args.input,newline='',encoding='utf-8-sig') as f:
        rd=csv.DictReader(f); miss=[x for x in need if x not in (rd.fieldnames or [])]
        if miss: raise SystemExit(f"Missing columns: {miss}")
        for z in rd:
            try:s=int(float(z['season']))
            except:continue
            r={'season':s,'team':z['team'],'w_pct':num(z['w_pct']),'share':num(z['top3_salary_share']),'avail':num(z['top3_availability']),'champ':num(z['is_champion'])}
            if None in [r['w_pct'],r['share'],r['avail'],r['champ']]: continue
            r['frag']=r['share']*(1-r['avail']); rows.append(r)
    print(f"team-seasons: {len(rows)}; champions: {sum(int(r['champ']) for r in rows)}")
    print(f"r(top3 salary share, W%) = {corr([r['share'] for r in rows],[r['w_pct'] for r in rows]):+.3f}")
    print(f"r(top3 availability, W%) = {corr([r['avail'] for r in rows],[r['w_pct'] for r in rows]):+.3f}")
    print(f"r(fragility, W%) = {corr([r['frag'] for r in rows],[r['w_pct'] for r in rows]):+.3f}")
    print(f"r(top3 share, champion) = {corr([r['share'] for r in rows],[r['champ'] for r in rows]):+.3f}")
    print(f"r(fragility, champion) = {corr([r['frag'] for r in rows],[r['champ'] for r in rows]):+.3f}")
    by=defaultdict(list)
    for r in rows: by[r['season']].append(r)
    rs=[]
    print("season\tr_frag\tr_share\tr_avail")
    for s in sorted(by):
        q=by[s]; rf=corr([r['frag'] for r in q],[r['w_pct'] for r in q]); rs.append(rf)
        print(f"{s}\t{rf:+.3f}\t{corr([r['share'] for r in q],[r['w_pct'] for r in q]):+.3f}\t{corr([r['avail'] for r in q],[r['w_pct'] for r in q]):+.3f}")
    finite=[x for x in rs if math.isfinite(x)]
    print(f"negative seasons: {sum(x<0 for x in finite)}/{len(finite)}; median r_frag = {np.median(finite):+.3f}")
    champs=[r for r in rows if r['champ']>=0.5]; field=[r for r in rows if r['champ']<0.5]
    if champs:
        band=lambda rr: sum(.55<=r['share']<=.70 for r in rr)/len(rr)
        print(f"champions in 55-70% salary band = {band(champs):.1%}; field = {band(field):.1%}")
        print(f"mean champion share={np.mean([r['share'] for r in champs]):.3f}; availability={np.mean([r['avail'] for r in champs]):.3f}; fragility={np.mean([r['frag'] for r in champs]):.4f}")
        print(f"mean field share={np.mean([r['share'] for r in field]):.3f}; availability={np.mean([r['avail'] for r in field]):.3f}; fragility={np.mean([r['frag'] for r in field]):.4f}")
    for label,feats in [('availability',['avail']),('salary share',['share']),('availability + share',['avail','share']),('fragility',['frag']),('availability + fragility',['avail','frag'])]:
        r2,b=ols_r2(rows,feats); print(f"R2 W% ~ {label} = {r2:.3f}; coefs={[round(float(x),3) for x in b]}")

if __name__=='__main__': main()
