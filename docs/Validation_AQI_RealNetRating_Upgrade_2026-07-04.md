# Validation: AQI Real-Net-Rating Upgrade (BPM proxy → NBA.com on-court NET_RATING)

**Date:** 2026-07-04 · **Desk:** Evidence → Canon candidate · **Status: `Evidence` (reproduced on-disk, robust)**
**Goal:** Close the #1 ironclad gap from the Framework Validity Ledger — AQI's flagship correlation was computed with **BPM as a net-rating *proxy*** (a labeled `Idea`, and the first thing any NBA quant flags). This test swaps in a **real measured on-court NET_RATING** and checks whether the championship signal holds at r ≥ 0.35.

## Result: it doesn't just hold — the upgrade makes AQI *stronger*.

Head-to-head, same team-season population, same champion labels, rotation filter GP≥40 & MPG≥20, seasons 1997–2023 (n = 802 team-seasons, 27 champions):

| AQI input | r(anchor AQI, is_champion) | Champion mean anchor | Non-champ mean | Champion anchor rank (within season) |
|---|---|---|---|---|
| **Real NET_RATING (upgrade)** | **0.365** ✅ | 3.617 | 0.952 | mean 2.33 · top-5 in **25/27** · top-3 in 21/27 |
| BPM proxy (status quo) | 0.266 ❌ | 2.544 | 1.175 | mean 4.19 · top-5 in 21/27 · top-3 in 13/27 |
| **Delta** | **+0.099** | | | materially better on every axis |

**The BPM proxy was *underselling* AQI.** The real on-court net rating separates champions from the field far more cleanly (champion anchors average 3.6 vs 0.95 for everyone else) and puts the champion's best player in the league's top 5 anchors in 25 of 27 seasons.

## Robustness — holds across every specification tested

| Filter / window | n | real-net r | BPM r | delta |
|---|---|---|---|---|
| GP≥40, MPG≥20, 1997–2023 | 802 | **0.365** | 0.266 | +0.099 |
| GP≥50, MPG≥24, 1997–2023 | 802 | **0.356** | 0.265 | +0.092 |
| GP≥40, MPG≥20, 2000–2023 | 715 | **0.370** | 0.261 | +0.109 |
| GP≥58, MPG≥28, 2000–2023 | 701 | **0.356** | 0.271 | +0.085 |

Real-net AQI stays in a tight 0.356–0.370 band (always ≥ 0.35, PASS); BPM stays 0.261–0.271 (always FAIL). The improvement is not a filter artifact.

## Method

AQI = net_rating_factor × usage × (TS / 0.550), per player-season (regular season). Team **anchor = AQI_top1** = the highest-AQI rotation player on a team-season. Target = `is_champion` (external binary — not tautological with the inputs). Real-net version uses NBA.com `NET_RATING`, `USG_PCT`, `TS_PCT` from `nbacom_advanced_rs_1996_2023.csv`; BPM version uses `bpm`, `usg_percent`, `ts_percent` from `bbref_advanced_1947_2024.csv`. Code: `_aqi_netrating_upgrade.py`, `_aqi_robust.py`.

## Two honest caveats (do not skip these when publishing)

1. **Scale shifted — the anchor floor must be recalibrated.** The familiar "1.75 anchor floor" and figures like Jaylen Brown's 1.245 were computed on the **BPM-based** scale. Under real net rating, champion anchors average **3.6**, so the floor and every published player AQI need re-derivation on the new scale before mixing the two. The *rank/correlation* conclusions are scale-invariant; the *absolute thresholds* are not.

2. **On-court NET_RATING carries team context.** It is a *real measured* quantity (points margin per 100 while the player is on the floor) — a genuine upgrade over BPM's box-score regression estimate — but it is lineup-dependent, so a star on a great team gets a contextual boost. That is arguably *appropriate* for a champion-anchor metric (you want the best player on an elite team to score high), but the purest individual isolation would be an **on/off differential**, which is the next refinement. NET_RATING is the strongest input available on-disk today; on/off is a future pull (nba_api, run locally).

## Anchor-floor recalibration (net-rating scale)

The old "1.75 anchor floor" was on the BPM scale. Recomputed on real net rating (anchor = top-1 AQI player per team-season, GP≥40 & MPG≥20):

| Threshold | Champions clearing (2000–2023) | Non-champions clearing | Reading |
|---|---|---|---|
| **1.73 — recalibrated floor** | **24/24 (100%)** | 168/691 (**24%**) | Necessary condition. Every champion clears it — but so does a quarter of the field. An **entry ticket, not proof.** |
| 2.50 — separator band | 23/24 (96%) | 77/691 (**11%**) | The discriminating threshold: keeps almost every champion, cuts non-champ clearers to ~1-in-9. |
| 3.00 | 17/24 (71%) | 41/691 (6%) | Too high — starts excluding real champions (the committee-anchor teams). |

Champion anchor distribution: **min 1.73, median 3.61, mean 3.62, max 5.65.**

**The floor barely moved (1.75 → 1.73) — but not by design.** It is bound by the same team on both scales: the **2004 Detroit Pistons**, the modern era's only no-superstar champion. Whatever the input, Detroit sets the minimum, so the floor value is stable. Everything *above* the floor shifted a lot (champion mean rose from 2.54 on BPM to 3.62 on net rating), so **individual player AQIs still must be republished on the new scale** — the floor coincidence does not carry to the rest of the distribution.

**Recalibrated canon:** anchor floor = **1.73 (net-rating scale), 100% of champions, ~24% specificity — a necessary entry condition, not a separator.** The operational separator is **≥2.50** (96% champions / 11% non-champions). Present the floor as a filter, never as a predictive hit rate.

**Anchor-identity quirk (honest flag):** on net rating the 2004 Pistons' top-AQI player reads as **Mehmet Okur**, not Chauncey Billups (Billups was the anchor on the BPM scale). On-court net rating rewards efficient role players in strong lineups — a direct symptom of the team-context caveat above, and the clearest argument for the on/off refinement.

**Not recalibrated yet:** current-player AQIs (e.g., Jaylen Brown's 1.245 in the Mirage article) were on the BPM scale and sit in the 2024–2026 seasons *not present* in `nbacom_advanced_rs_1996_2023.csv`. Republishing them on the net scale requires pulling 2024–26 NBA.com advanced data (nba_api, run locally).

## Verdict for the Ledger

AQI graduates from **Tier A "Strong"** to **Tier A-clean on the correlation axis**: the champion signal is now built on a real measured net rating, is robust across specifications, and *beats* the old proxy. Remaining to full ironclad: (a) recalibrate the anchor floor + republish player AQIs on the net-rating scale, (b) optionally swap on-court NET_RATING for on/off to isolate the individual, (c) commit the reproducible code to the public repo.

*Sources: `nbacom_advanced_rs_1996_2023.csv`, `bbref_advanced_1947_2024.csv`, `Framework_AQI_RQS_InteriorAnchor_Draymond_Backtest_2026-06-01.md` (prior team-season r=0.364), `DataDunkNBA_Formula_Registry.md`.*
