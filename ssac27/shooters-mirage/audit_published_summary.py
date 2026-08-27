#!/usr/bin/env python3
"""Audit only the aggregate counts reported in the June 2026 Shooter's Mirage study.

This is intentionally NOT a raw-data reproduction. It recomputes descriptive
uncertainty from published counts and uses two toy simulations to demonstrate
known design risks: regression to the mean after extreme-group selection and
conditioning on final margin.
"""
import json, math, random
from pathlib import Path
from statistics import NormalDist

ROOT=Path(__file__).resolve().parent
SRC=json.loads((ROOT/'published_summary.json').read_text())
N=NormalDist()

def wilson(k,n,z=1.959963984540054):
    p=k/n; den=1+z*z/n
    c=(p+z*z/(2*n))/den
    h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return [p,c-h,c+h]

def diff(p1,n1,p2,n2):
    d=p1-p2
    se=math.sqrt(p1*(1-p1)/n1 + p2*(1-p2)/n2)
    z=d/se
    p=2*(1-N.cdf(abs(z)))
    return {"diff":d,"se":se,"z":z,"p_two_sided":p,"ci95":[d-1.96*se,d+1.96*se]}

rs=SRC['wide_open']['regular_season']; po=SRC['wide_open']['playoffs']
rsd=diff(rs['elite_pct'],rs['elite_n'],rs['subavg_pct'],rs['subavg_n'])
pod=diff(po['elite_pct'],po['elite_n'],po['subavg_pct'],po['subavg_n'])
did=rsd['diff']-pod['diff']; sed=math.sqrt(rsd['se']**2+pod['se']**2); z=did/sed

# Toy diagnostic: classify extremes on noisy RS samples, then re-measure the
# same unchanged true skills. This is a design diagnostic, not NBA evidence.
def regression_to_mean_sim(seed=10, reps=800, players=554):
    rng=random.Random(seed)
    mean=.37; sd=.035; var=sd*sd; conc=mean*(1-mean)/var-1; aa=mean*conc; bb=(1-mean)*conc
    rs_gaps=[]; po_gaps=[]
    for _ in range(reps):
        elite_rs=[]; elite_po=[]; sub_rs=[]; sub_po=[]
        for __ in range(players):
            skill=rng.betavariate(aa,bb)
            nrs=rng.randint(100,500); npo=rng.randint(10,80)
            rs=sum(rng.random()<skill for ___ in range(nrs))/nrs
            po=sum(rng.random()<skill for ___ in range(npo))/npo
            if rs>=.40:
                elite_rs.append(rs); elite_po.append(po)
            elif rs<.35:
                sub_rs.append(rs); sub_po.append(po)
        if elite_rs and sub_rs:
            rs_gaps.append(sum(elite_rs)/len(elite_rs)-sum(sub_rs)/len(sub_rs))
            po_gaps.append(sum(elite_po)/len(elite_po)-sum(sub_po)/len(sub_po))
    rsg=sum(rs_gaps)/len(rs_gaps); pog=sum(po_gaps)/len(po_gaps)
    return {"assumptions":{"true_skill_mean":mean,"true_skill_sd":sd,"rs_attempt_range":[100,500],"playoff_attempt_range":[10,80],"no_true_playoff_compression":True},
            "mean_selected_rs_gap":rsg,"mean_remeasured_playoff_gap":pog,"apparent_gap_compression":1-pog/rsg,"reps":reps}

# Toy structural diagnostic: final-margin conditioning can attenuate a real
# shooting edge. This is not a reanalysis of NBA data.
def collider_sim(seed=7,Nsim=300000,n3=35,pA=.39,pB=.36,other_sd=10.0):
    rng=random.Random(seed)
    wins=0; close=0; closewins=0
    for _ in range(Nsim):
        a=sum(rng.random()<pA for __ in range(n3)); b=sum(rng.random()<pB for __ in range(n3))
        u1=max(rng.random(),1e-12); u2=rng.random()
        other=math.sqrt(-2*math.log(u1))*math.cos(2*math.pi*u2)*other_sd
        margin=3*(a-b)+other
        w=margin>0
        wins+=w
        if abs(margin)<6:
            close+=1; closewins+=w
    return {"assumptions":{"A_3p":pA,"B_3p":pB,"three_attempts_each":n3,"other_score_diff_sd":other_sd},
            "all_win_rate_A":wins/Nsim,"final_margin_lt6_win_rate_A":closewins/close,"close_n":close,"sim_n":Nsim}

out={
  "status":"AGGREGATE_AUDIT_ONLY_NOT_RAW_REPRODUCTION",
  "published_wide_open":{
     "rs_elite_minus_subavg":rsd,
     "playoff_elite_minus_subavg":pod,
     "naive_independent_shot_difference_in_differences":{
        "gap_reduction":did,"se":sed,"z":z,"p_two_sided":2*(1-N.cdf(abs(z))),"ci95":[did-1.96*sed,did+1.96*sed],
        "warning":"Shots are clustered within players/teams and tiers were defined using RS performance; this is a descriptive audit, not the final inferential test."
     }
  },
  "game_level_wilson95":{
      "all_422":wilson(238,422),
      "final_margin_lt6_100":wilson(50,100),
      "game7_16":wilson(8,16)
  },
  "structural_diagnostic":{
      "final_margin_collider_simulation":collider_sim(),
      "regression_to_mean_simulation":regression_to_mean_sim(),
      "warning":"Conditioning on final margin selects on an outcome affected by shooting. A real shooting advantage can look much smaller inside the post-outcome close-game subset."
  },
  "promotion_blockers":[
      "Original raw Mirage files of record were not found in Drive/File Library/GitHub during the 2026-08-26 audit.",
      "Shooter tiers use same-window RS shooting to define extremes, creating regression-to-the-mean risk.",
      "Primary close-game tables condition on final margin, a post-outcome/collider variable.",
      "Shot-level inference must cluster/hierarchically model repeated shooters rather than treat attempts as independent.",
      "Game 5+ is not equivalent to elimination pressure; series state must be reconstructed explicitly.",
      "The $430M payroll extrapolation and specialist-teardown claim are outside the validated empirical spine."
  ]
}
(ROOT/'results').mkdir(exist_ok=True)
(ROOT/'results'/'published_summary_audit.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps(out,indent=2,sort_keys=True))
