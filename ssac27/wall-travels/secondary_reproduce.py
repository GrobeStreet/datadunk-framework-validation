#!/usr/bin/env python3
import argparse, csv, json, math, random, statistics, hashlib
from pathlib import Path

ap=argparse.ArgumentParser()
ap.add_argument('--data-dir', type=Path, default=Path('data_derived'))
ap.add_argument('--out', type=Path, default=Path('results/secondary_receipt.json'))
args=ap.parse_args()
ROOT=args.data_dir
SEED=20260826
NPERM=20000

def read_csv(name):
    with (ROOT/name).open(encoding='utf-8-sig',newline='') as f:
        return list(csv.DictReader(f))

def f(x): return float(x)
def sha(p): return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def pearson(xs,ys):
    mx=statistics.fmean(xs); my=statistics.fmean(ys)
    num=sum((x-mx)*(y-my) for x,y in zip(xs,ys))
    den=math.sqrt(sum((x-mx)**2 for x in xs)*sum((y-my)**2 for y in ys))
    return num/den if den else float('nan')

def perm_p_corr(xs,ys,n=NPERM,seed=SEED):
    rng=random.Random(seed); obs=abs(pearson(xs,ys)); y=list(ys); ge=0
    for _ in range(n):
        rng.shuffle(y)
        ge += abs(pearson(xs,y)) >= obs
    return (ge+1)/(n+1)

def loo_corr(xs,ys):
    return [pearson(xs[:i]+xs[i+1:],ys[:i]+ys[i+1:]) for i in range(len(xs))]

def defender_spread(rows):
    # Historical-style label shuffle: shuffle defender labels across matchup rows
    # while keeping each row's observed shooter deviation and FGA weight fixed.
    labels=[r['DEF_PLAYER_ID'] for r in rows]
    weights=[f(r['MATCHUP_FGA']) for r in rows]
    values=[f(r['fg_vs_avg']) for r in rows]
    def calc(labs):
        groups={}
        for i,l in enumerate(labs): groups.setdefault(l,[]).append(i)
        means=[]
        for inds in groups.values():
            sw=sum(weights[i] for i in inds)
            means.append(sum(weights[i]*values[i] for i in inds)/sw)
        return statistics.pstdev(means)
    obs=calc(labels)
    rng=random.Random(SEED); null=[]; labs=labels[:]
    for _ in range(NPERM):
        rng.shuffle(labs); null.append(calc(labs))
    nm=statistics.fmean(null); ns=statistics.pstdev(null)
    z=(obs-nm)/ns if ns else float('nan')
    p=(sum(v>=obs for v in null)+1)/(NPERM+1)
    return {'defenders':len(set(labels)),'matchup_rows':len(rows),'matchup_fga':sum(weights),'observed_sd':obs,'null_mean':nm,'null_sd':ns,'z':z,'empirical_p_upper':p,'permutations':NPERM,'seed':SEED,
            'interpretation':'Curated 14-defender subset; null spread confirms range restriction. This is an independent rerun of the historical label-shuffle test, not the full 107-defender population test.'}

m=read_csv('matchup_grades.csv')
bridge=read_csv('micro_macro_bridge.csv')
det=read_csv('deterrence_team.csv')

bx=[f(r['team_rim_sup']) for r in bridge]; by=[f(r['opp_ppp']) for r in bridge]
bloo=loo_corr(bx,by)
dx=[f(r['team_sup']) for r in det]; dy=[f(r['rim_rate']) for r in det]
dloo=loo_corr(dx,dy)

out={
 'status':'REPRODUCED_FROM_FROZEN_DERIVED_INPUTS',
 'sources':{n:{'sha256':sha(n)} for n in ['matchup_grades.csv','micro_macro_bridge.csv','deterrence_team.csv']},
 'curated_matchup_range_restriction':defender_spread(m),
 'team_bridge_2024_25':{
   'n':len(bridge),'pearson_r_team_rim_supp_vs_opp_ppp':pearson(bx,by),'permutation_p_two_sided':perm_p_corr(bx,by),
   'leave_one_team_out_r_min':min(bloo),'leave_one_team_out_r_max':max(bloo),
   'claim_boundary':'One-season cross-sectional association; not causal identification.'
 },
 'team_deterrence_2024_25':{
   'n':len(det),'pearson_r_team_sup_vs_rim_attempt_rate':pearson(dx,dy),'permutation_p_two_sided':perm_p_corr(dx,dy,seed=SEED+1),
   'leave_one_team_out_r_min':min(dloo),'leave_one_team_out_r_max':max(dloo),
   'claim_boundary':'Team-level shot-frequency null; does not rule out player-level or scheme-conditional deterrence.'
 }
}
args.out.parent.mkdir(parents=True, exist_ok=True)
args.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps(out,indent=2,sort_keys=True))
