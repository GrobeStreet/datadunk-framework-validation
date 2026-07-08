# DataDunkNBA — Framework Validation (Phase 1, July 2026)

Reproducible out-of-sample (OOS) validation of the DataDunkNBA metric stack. Every claim here is graded on a strict OOS standard: a metric counts only if it predicts on data it was **not** built on. Several metrics were downgraded or retired in this pass — that is the point.

## Headline results

| Metric | Test | Verdict |
|---|---|---|
| **AQI** | Rebuilt on real NBA.com on-court NET_RATING (vs BPM proxy); champion correlation | ✅ r=+0.365 (802 team-seasons), robust 0.356–0.370, **beats BPM proxy (0.266)**. Floor recalibrated to 1.73. |
| **WEV_v3 / CPV** | Temporal hold-out: fit 2000–2015, test 2016–2023 | ✅ Generalizes (WEV_v3 r 0.354→0.320; CPV 0.327→0.348); **beats raw NetRtg/SRS/W%**; DEV≈0.58 weight independently re-derived. Top-5 filter, not a picker. |
| **RQS** | OOS test on held-out champions 2024–2026 | ❌ "100% top-5" **FALSIFIED** — 2026 NYK finished #8; caught 2/3. Demoted to descriptive index. |
| **EffTax** | Historical widening (745 team-seasons) | ❌ Multiplier **FAILED OOS** (r≈0.003 vs the one-season r=−0.639). Retired. |

Full grading in `docs/Framework_Validity_Ledger_2026-07-04.md`.

## Layout

```
code/   validation scripts (stdlib + numpy only)
  _aqi_netrating_upgrade.py   AQI: real NET_RATING vs BPM proxy, champion correlation head-to-head
  _aqi_robust.py              AQI: robustness across minutes filters + year windows
  _aqi_floor.py               AQI: anchor-floor recalibration on the net-rating scale
  wev_holdout.py              WEV_v3/CPV: fit-2000-15 / test-2016-23 hold-out + weight refit
  wev_baseline.py             WEV_v3/CPV vs raw NetRtg/SRS/W% baseline (OOS)
  rqs_oos.py                  RQS: held-out champions 2024-2026 top-5 test (+ 2023 control)
  rqs_2026_detail.py          RQS: 2026 full ranking + NYK component breakdown
docs/   validation write-ups + the Framework Validity Ledger
```

## Data sources (not committed — regenerate)

Raw data is third-party and not redistributed here. To reproduce:

- **Historical player advanced (1996–2023):** NBA.com advanced player stats → `nbacom_advanced_rs_1996_2023.csv` (cols incl. `NET_RATING`, `USG_PCT`, `TS_PCT`).
- **Historical player advanced (BPM, 1947–2024):** Basketball-Reference → `bbref_advanced_1947_2024.csv` (cols incl. `bpm`, `usg_percent`, `ts_percent`).
- **Team-season composites panel:** `proof_outputs/team_seasons_full.csv` (WEV_v2/v3, OEV/DEV/CEV, CPV, NetRtg, SRS, is_champion — 805 team-seasons 2000–2026).
- **Held-out seasons 2022-23 … 2025-26:** pulled live via [`nba_api`](https://github.com/swar/nba_api) `LeagueDashPlayerStats(measure_type="Advanced")` + `DraftHistory` + `LeagueStandingsV3`. Run locally (stats.nba.com blocks some cloud hosts).

Champion labels are external (NBA Finals results). Champion correlation targets `is_champion`, which is independent of every metric input (not tautological).

## Method notes

- **AQI** = `net_rating × usg × (TS / 0.550)` per player-season. Team anchor = highest-AQI rotation player (GP≥40 & MPG≥20). The upgrade swaps BPM (a box-score regression *estimate*) for NBA.com on-court NET_RATING (a *measured* quantity). On-court NET_RATING carries team context; an on/off differential would isolate the individual further (future refinement).
- **RQS** = `AQI1×4 + AQI2×2 + interior_anchor×3 + late_draft_elite×1`.
- **Honest limits** are stated in each doc: modest predictors (r²≈0.10), small held-out champion counts, and team-context effects. These are filters and descriptors, not oracles.

*Generated 2026-07-04. Companion to the SSAC27 PASV and NPSS papers (separate repo).*
