#!/usr/bin/env python3
"""Forecast-safe team clutch / CEV test used by the Sept. 2026 sprint.

Inputs
------
--games : one row per regular-season game with season, home team, away team,
          home points, away points. Common aliases are auto-detected.
--panel : canonical team-season panel with Season, team code, W_PCT, NetRtg,
          champion label, and optionally OEV/DEV/WEV v3.

The script defines a close game as final margin <= 5, builds close-game W% and
close residual = close W% - overall W%, tests championship association and
persistence, and evaluates next-season W% prediction from prior NetRtg with and
without prior clutch residual. It answers only the team-trait question.
"""
from __future__ import annotations
import argparse, csv, math
from collections import defaultdict
import numpy as np

ALIASES={
 "season":["Season","season","SEASON","YEAR"],
 "home":["HOME_TEAM_ABBREVIATION","home_team","HomeTeam","HOME","home"],
 "away":["AWAY_TEAM_ABBREVIATION","away_team","AwayTeam","AWAY","away"],
 "hp":["PTS_HOME","home_pts","HomePts","HOME_PTS","home_score"],
 "ap":["PTS_AWAY","away_pts","AwayPts","AWAY_PTS","away_score"],
}
PANEL={
 "season":["Season","season"],"team":["Abbrev","Team","TEAM_ABBREVIATION"],
 "wpct":["W_PCT","W%","WIN_PCT"],"net":["NetRtg","NET_RATING","Net Rating"],
 "champ":["is_champion","Champion","champion"],"oev":["OEV"],"dev":["DEV"],
 "wev":["WEV v3 (OEV×0.30 + DEV×0.60 + CEV×0.10)","WEV_v3"]
}
FRANCHISE={"NJN":"BKN","BKN":"BKN","NOH":"NOP","NOK":"NOP","NOP":"NOP","CHH":"CHA","CHO":"CHA","CHA":"CHA","SEA":"OKC","OKC":"OKC","VAN":"MEM","MEM":"MEM"}

def pick(fields, aliases, required=True):
    for x in aliases:
        if x in fields: return x
    if required: raise SystemExit(f"Missing column; tried {aliases}")
    return None

def num(x):
    try:
        v=float(x); return v if math.isfinite(v) else None
    except: return None

def team(x):
    x=(x or "").strip().upper(); return FRANCHISE.get(x,x)

def corr(a,b):
    a=np.asarray(a,float); b=np.asarray(b,float)
    return float(np.corrcoef(a,b)[0,1]) if len(a)>=3 and np.std(a)>0 and np.std(b)>0 else float('nan')

def linpred(train, test, feats):
    X=np.array([[1]+[r[k] for k in feats] for r in train],float); y=np.array([r['y'] for r in train],float)
    T=np.array([[1]+[r[k] for k in feats] for r in test],float)
    beta=np.linalg.lstsq(X,y,rcond=None)[0]; return T@beta

def oos_r2(rows, feats):
    ys=[]; ps=[]
    for s in sorted(set(r['season'] for r in rows)):
        te=[r for r in rows if r['season']==s and all(r.get(k) is not None for k in feats)]
        tr=[r for r in rows if r['season']!=s and all(r.get(k) is not None for k in feats)]
        if not te or len(tr)<=len(feats)+2: continue
        pr=linpred(tr,te,feats); ys += [r['y'] for r in te]; ps += pr.tolist()
    y=np.array(ys); p=np.array(ps)
    return len(y), 1-float(np.sum((y-p)**2))/float(np.sum((y-y.mean())**2))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--games',required=True); ap.add_argument('--panel',required=True); args=ap.parse_args()
    with open(args.games,newline='',encoding='utf-8-sig') as f:
        rd=csv.DictReader(f); fields=rd.fieldnames or []
        cs,ch,ca,cp_h,cp_a=[pick(fields,ALIASES[k]) for k in ['season','home','away','hp','ap']]
        agg=defaultdict(lambda:{'w':0,'g':0,'cw':0,'cg':0})
        for z in rd:
            try: s=int(float(z[cs]))
            except: continue
            hp,apts=num(z[cp_h]),num(z[cp_a]); h,a=team(z[ch]),team(z[ca])
            if hp is None or apts is None or not h or not a: continue
            hw=hp>apts; close=abs(hp-apts)<=5
            for t,w in [(h,hw),(a,not hw)]:
                q=agg[(t,s)]; q['g']+=1; q['w']+=int(w)
                if close: q['cg']+=1; q['cw']+=int(w)
    clutch={}
    for k,q in agg.items():
        if q['g'] and q['cg']:
            ow=q['w']/q['g']; cw=q['cw']/q['cg']; clutch[k]={'overall':ow,'close':cw,'resid':cw-ow,'close_n':q['cg']}

    with open(args.panel,newline='',encoding='utf-8-sig') as f:
        rd=csv.DictReader(f); fields=rd.fieldnames or []
        c={k:pick(fields,v,required=(k in ['season','team','wpct','net','champ'])) for k,v in PANEL.items()}
        rows=[]
        for z in rd:
            try:s=int(float(z[c['season']]))
            except:continue
            t=team(z[c['team']]); cc=clutch.get((t,s))
            if not cc: continue
            r={'season':s,'team':t,'wpct':num(z[c['wpct']]),'net':num(z[c['net']]),'champ':num(z[c['champ']]),**cc}
            for k in ['oev','dev','wev']: r[k]=num(z[c[k]]) if c[k] else None
            if r['wpct'] is not None and r['net'] is not None and r['champ'] is not None: rows.append(r)

    print(f"matched team-seasons: {len(rows)}")
    print(f"corr(close W%, champion) = {corr([r['close'] for r in rows],[r['champ'] for r in rows]):+.3f}")
    print(f"corr(clutch residual, champion) = {corr([r['resid'] for r in rows],[r['champ'] for r in rows]):+.3f}")
    by={(r['team'],r['season']):r for r in rows}; pairs=[]
    for r in rows:
        p=by.get((r['team'],r['season']-1))
        if p: pairs.append((p,r))
    print(f"year-to-year pairs: {len(pairs)}")
    print(f"persistence close W% = {corr([p['close'] for p,r in pairs],[r['close'] for p,r in pairs]):+.3f}")
    print(f"persistence residual = {corr([p['resid'] for p,r in pairs],[r['resid'] for p,r in pairs]):+.3f}")
    print(f"persistence NetRtg = {corr([p['net'] for p,r in pairs],[r['net'] for p,r in pairs]):+.3f}")
    pred=[{'season':r['season'],'y':r['wpct'],'prior_net':p['net'],'prior_resid':p['resid']} for p,r in pairs]
    n0,r20=oos_r2(pred,['prior_net']); n1,r21=oos_r2(pred,['prior_net','prior_resid'])
    print(f"next-season OOS R2 prior NetRtg = {r20:.3f} (n={n0})")
    print(f"next-season OOS R2 prior NetRtg + clutch residual = {r21:.3f} (n={n1})")
    usable=[r for r in rows if r['oev'] is not None and r['dev'] is not None]
    if usable:
        for r in usable: r['wev_nocev']=(0.30*r['oev']+0.60*r['dev'])/0.90
        print(f"corr(WEV_noCEV, champion) = {corr([r['wev_nocev'] for r in usable],[r['champ'] for r in usable]):+.3f}")
        have=[r for r in usable if r['wev'] is not None]
        if have: print(f"corr(legacy WEV v3, champion) = {corr([r['wev'] for r in have],[r['champ'] for r in have]):+.3f}")

if __name__=='__main__': main()
