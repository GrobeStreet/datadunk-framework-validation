# DataDunkNBA — Framework Validity Ledger

**Date:** 2026-07-04 · **Purpose:** The single honest source of truth on what is *ironclad* vs. *not-yet* across the whole metric stack, graded on an **out-of-sample (OOS)** standard — not the in-sample "hard validated" labels in the registry. This is the spine of the ironclad → authorize → leverage plan, and the exact document to hand a skeptical NBA analytics director.

> **The standard.** A metric is *ironclad* only if it (1) predicts on data it was **not** built on (held-out or genuinely cross-sectional), (2) is **pre-registered or reproducible**, and (3) states its own failure modes. A 100% hit rate on the same sample used to define the rule is **not** validation — it's a description of the training set. This ledger re-grades every metric on that bar. Several registry "✅ Hard validated" labels are downgraded here on purpose; that honesty is the product.

---

## TIER A — Ironclad-track (real, OOS-defensible). Lead with these.

| Metric | Best honest evidence | OOS status | What makes it ironclad (the gap to close) |
|---|---|---|---|
| **AQI** (Anchor Quality Index) | **UPGRADED 2026-07-04:** rebuilt on real NBA.com on-court NET_RATING (not BPM proxy). r = **+0.365** to championships (802 team-seasons, 1997–2023), robust 0.356–0.370 across specs. Champion anchor is a top-5 anchor in **25/27** seasons. Beats the old BPM-proxy version (r=0.266) by +0.10. | **CLEAN (correlation axis)** ✅ — real measured net rating, robust, external target, *beats* the proxy. See `Validation_AQI_RealNetRating_Upgrade_2026-07-04.md`. | (a) ✅ **Floor recalibrated 2026-07-04: 1.73 net-rating scale (100% champions, ~24% specificity — a necessary entry condition; separator ≥2.50 = 96%/11%).** Still pending: republish *current-player* AQIs on the new scale (needs 2024–26 NBA.com advanced pull). (b) Optionally swap on-court NET_RATING → on/off differential to isolate the individual. (c) Publish the reproducible code to the repo. |
| **NPSS** (schemable-big playoff collapse) | Held-out temporal test THIS session: schemable-big RS→PO AQI drop **−0.19 on unseen 2023–25**, matching train (−0.20); 100% recall of held-out star collapses | **OOS-VALIDATED** ✅ (the cleanest in the stack) | Already hold-out validated + public repo (github/GrobeStreet/pasv/npss). Ironclad on the schemable-big effect. Bound the star-tier multiplier honestly (n=71). Submitted to SSAC27. |
| **DTI** (Defender Targeting Index) | Multi-season lineup-aware falsifying regression: **66,006 playoff possessions, β₂=0.945, p=0.010**; matchup-blind v1 collapses (p=0.78) | **Validated** ✅ (multi-season, out-of-sample of the single-season pilot) | Public repo done. Push β₂ to p<0.001 with the full 5-playoff pool; it's the empirical spine of the PASV paper. |
| **PASV** (Possibility-Adjusted Shot Value) | First per-shot validation on public data: **beats the Skinner 2012 MDP baseline** within-player (held-out 2024-25 playoffs, 14,377 attempts) | **Partial** — beats Skinner (real); **ties raw xPTS** (honest null). Robust across 5 estimators. | Honest as-is. The frontier: a tracking-grade V\* to separate from shot quality. Submitted to SSAC27. Don't overclaim beyond "beats Skinner + formalizes possibility cost." |
| **WEV_v3 / CPV** (team composites) | **HOLD-OUT PASSED 2026-07-04:** frozen canon predicts held-out 2016–23 champions as well as in-sample (WEV_v3 r 0.354→0.320; CPV 0.327→**0.348**); champion in top-5 ~88% of held-out yrs; **beats raw NetRtg (0.25)/SRS/W%**; refit independently re-derives DEV≈0.58 (canon 0.60). | **OOS-GENERALIZING** ✅ — prediction, not description; beats trivial baseline. See `Validation_WEV_CPV_TemporalHoldout_2026-07-04.md`. CPV marginally strongest composite in stack. | Honest limits: modest predictor (r²≈0.10, a top-5 *filter* not a picker); OEV/CEV split weakly identified; n=8 held-out champs. To finish: commit code to repo; backfill 2024–26 champions. |

## TIER B — In-sample fits. Impressive-looking, NOT predictive. Reframe or a reviewer buries you.

| Metric | The claim | The problem | Correct framing |
|---|---|---|---|
| **RQS** "100% top-5" | Every champion 2000–23 finished top-5 in RQS | **FALSIFIED OOS (Jul 4 2026):** on the 3 held-out champions it caught 2/3 — **2026 NYK finished #8**. The 100% was an in-sample fit. | **RETIRED as a filter.** RQS is a *descriptive roster-quality index* (champions usually rank well: DEN #1, BOS #2, OKC #1) but NOT a universal champion filter. Never publish "100%." Ref: `Validation_RQS_OutOfSample_Test_2026-07-04.md`. |
| **Interior Anchor Rule** "24/24" | Every champ had a player with dreb%>18 & net>+3 | Same in-sample issue; it's a description of 24 rosters. | Frame as a **structural regularity / entry condition**, with the honest note that near-100% of *all* deep playoff teams also pass it (low specificity). |
| **Draymond Effect** "22/24" | 92% of champs had a late-pick (≥20) plus rotation player | In-sample; also likely true of most good teams (low discriminating power). | Same reframe. Interesting narrative, weak filter. |

## TIER C — Directional / operational (honest, unvalidated). Keep as `Idea`, don't lead with.

PDR (playoff decay — directional, the two-way-wing rejection is the validated piece), SSR (86 arcs, directional), SLS (n=14 supermax, too small), GPI (role-player r=−0.656 to win% is real; star-tier use is not), CSG (dead-cap accounting, no correlation), LES (star-quality proxy), PEI (first per-defender PDR, evidence-grade), CPS (composite, operational). **Action: each needs its own hold-out before promotion; until then labeled `Idea`/`Operational` and never sold as proven.**

## TIER D — Failed / weak / retired. Say so out loud (this is what earns trust).

| Metric | Verdict |
|---|---|
| **EffTax multiplier** (r=−0.639) | **FAILED OOS.** The −0.639 was a single 2025-26 cross-section; across 745 team-seasons the concentration×fragility signal → ~0 (r=0.003). Retire the multiplier claim; keep only the descriptive "champions cluster in a 55–70% concentration band." |
| **Clutch Paradox** | Blocked (v0.1, never validated). |
| **OEV as champion selector** | Dead (r=0.090, weaker than Age). Only defensible as a post-2017 floor. |
| **CIS as champion predictor** | Dead (r=0.039). Real only as an era-trend diagnostic (era r=0.966). |
| **Betting/market edge** | No blind edge; closing lines price the net-rating signal. Explanatory only (canon). |
| **Pace / 3PA-rate** | Noise (r≈0.0–0.04). |

---

## What this means for the three goals

**Ironclad (Goal 1):** The honest core is **five Tier-A metrics** — AQI, NPSS, DTI, PASV, WEV/CPV. That's more than enough for a serious system; you don't need 18. The work now is (a) close each Tier-A gap (real net rating for AQI; temporal hold-outs for WEV/CPV; push DTI to p<0.001), and (b) publicly downgrade Tier B/D so the whole system reads as self-policing. **Fewer, bulletproof metrics beat a long list with soft ones.**

**Authorize (Goal 2):** Lead the Sloan papers, arXiv, journals, and the front-office pitch with **Tier A only.** The Tier-D honesty ("we killed EffTax, here's the OOS proof") is a *credibility multiplier* with quants — it signals you test yourself harder than they will.

**Leverage (Goal 3):** The consultant pitch = the Tier-A five + the two Sloan papers + the reproducible repo + the dashboard. A front office can verify every claim. That verifiability is the hire signal.

## Next actions (Phase 1 hardening — priority order)
1. ~~**AQI real-net-rating upgrade**~~ — ✅ DONE 2026-07-04. r=0.365 on real net rating, beats BPM proxy (+0.10), robust. Follow-up: recalibrate the anchor floor + republish player AQIs on the new scale.
2. ~~**WEV/CPV temporal hold-out**~~ — ✅ DONE 2026-07-04. Passed: predicts held-out 2016–23 champions (r 0.32–0.35), beats raw NetRtg, defense weighting independently confirmed. CPV strongest.
3. **DTI to p<0.001** — full 5-playoff lineup pool (the ingest is scoped).
4. **Registry correction pass** — reclassify RQS/Interior Anchor/Draymond as in-sample filters and EffTax as failed, so the canon itself is honest.
5. ~~**RQS OOS test**~~ — ✅ DONE 2026-07-04. FAILED: caught 2/3 held-out champions; 2026 NYK #8. "100% top-5" retired; RQS demoted to descriptive index.

---
*Grades per CLAUDE.md discipline. This ledger supersedes the registry's in-sample "hard validated" labels wherever they conflict, for the purpose of external (Sloan/journal/front-office) claims. Sources: `DataDunkNBA_Formula_Registry.md` (Master Validity Table), `Validation_EffTax_Historical_Test_2026-06-29.md`, `Validation_NPSS_HeldOut_2026-06-29.md`, `DTI_v0.2_MULTISEASON_CANON_2026-06-15.md`, `pasv-sloan-repo/results/Study1_FINAL_Verdict_2026-06-25.md`.*
