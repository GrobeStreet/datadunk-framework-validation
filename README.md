# DataDunkNBA — Framework Validation

Reproducible out-of-sample validation of the DataDunkNBA metric stack. Every claim is graded at the level of the exact rule, target, formula, or predictive use being tested. **Frameworks live; claims die.** A failed title rule does not automatically erase a useful descriptor or mechanism.

## Headline results

| Metric | Test | Verdict |
|---|---|---|
| **AQI** | Rebuilt on real NBA.com on-court NET_RATING; champion correlation | ✅ r=+0.365 (802 team-seasons), robust 0.356–0.370; floor recalibrated to 1.73. |
| **WEV_v3 / CPV** | Temporal hold-out: fit 2000–2015, test 2016–2023 | ✅ Generalizes (WEV_v3 r 0.354→0.320; CPV 0.327→0.348); DEV≈0.58 weight independently re-derived. Team-quality filters, not oracles. |
| **RQS** | Held-out title rule + Sept. 12 preseason-record test | ⚠️ Universal top-5 title rule **falsified**; same-season descriptor survives. Naive prior RQS OOS R² 0.346 vs prior NetRtg 0.388; NetRtg+RQS adds only +0.004. |
| **Efficiency Tax** | Sept. 12 salary concentration × availability reconstruction, 2011–2026 | ✅ Construct restored as an **availability mechanism**: concentrated-dollar fragility r≈−0.394 with win%, negative in 16/16 seasons. The old multiplier remains non-canonical as a production form. |
| **CEV / team clutch** | Forecast-safe close-game outcome test | ❌ Team-trait version fails: weak title association, low year-to-year persistence, and essentially no forecast lift beyond prior NetRtg. Player-process clutch remains open. |

Full historical grading remains in `docs/Framework_Validity_Ledger_2026-07-04.md`; September sprint results are in `v6_sprint_2026-09/SPRINT_RESULTS_2026-09-12.md`.

**Release note:** the September research canon is newer than the currently verified public Bible deployment. `https://datadunknba-master-bible.netlify.app` is still the Aug. 13 v5 production deploy until a new Netlify production deploy is verified. Do not describe the live site as v6 yet.

## SSAC27 research lanes

The conference work is fail-closed: a provocative Substack result is not automatically a submission result.

| Lane | Current status | Public path |
|---|---|---|
| **PASV** | Submitted; current v4 framing is maintained in the dedicated PASV repository | `GrobeStreet/pasv` |
| **The Wall Travels / rim-suppression portability** | v1 reproduced; v2 robustness specification + harness frozen; **HOLD** until the v2 receipt is generated | `ssac27/wall-travels/` |
| **The Shooter's Mirage / playoff 3P translation** | Historical aggregate result audited; original raw `/tmp/` files not recovered; **BLOCKED / RETEST REQUIRED** under prior-only skill and no-final-margin-conditioning design | `ssac27/shooters-mirage/` |

For Wall Travels, the reproduced result is moderate positive year-to-year rim-suppression persistence, including positive raw persistence among team changers. Movement is observational, not causal identification. For Shooter's Mirage, the published 10.6-point regular-season wide-open elite/sub-average gap and 1.7-point playoff gap remain documented exploratory evidence; the current lane explicitly tests regression-to-the-mean and post-outcome selection risks before any Sloan promotion.

## Layout

```text
code/   framework validation scripts
  _aqi_netrating_upgrade.py
  _aqi_robust.py
  _aqi_floor.py
  wev_holdout.py
  wev_baseline.py
  rqs_oos.py
  rqs_2026_detail.py
docs/   validation write-ups + the Framework Validity Ledger
ssac27/ conference research lanes with frozen specs, code, and machine-readable receipts
v6_sprint_2026-09/
  00_README_RUN_ORDER.md
  01_cev_rs_forecast_safe.py
  02_rqs_preseason_record_model.py
  03_efftax_on_its_own_terms.py
  SPRINT_RESULTS_2026-09-12.md
  efftax_results.md
```

## September sprint reproducibility boundary

- **RQS:** executable from the canonical team-season export. During the Sept. 15 sync, the restored script independently reproduced the reported common-panel results: n=677; prior NetRtg OOS R² 0.388; prior RQS 0.346; NetRtg+RQS 0.392; NetRtg+RQS+Floor 0.391.
- **CEV / team clutch:** calculation script is restored, but the exact September warehouse game-level source export is not committed here. A rerun requires that frozen source.
- **Efficiency Tax:** calculation script is restored, but the exact Sept. 12 normalized salary/availability source snapshot is not committed here. The existing result is receipt-backed, not independently self-contained from GitHub alone.

See `v6_sprint_2026-09/00_README_RUN_ORDER.md` before calling any new run a reproduction of the September receipt.

## Data sources

Raw third-party data are not redistributed unless permitted. Current reproducibility therefore distinguishes between a frozen receipt and a self-contained rerun.

- **Historical player advanced (1996–2023):** NBA.com advanced player stats.
- **Historical player advanced (BPM, 1947–2024):** Basketball-Reference.
- **Team-season composites panel:** canonical `team_seasons_full.csv` export with WEV/OEV/DEV/CEV/CPV/NetRtg/SRS/champion labels and roster-quality fields.
- **Held-out seasons 2022-23 … 2025-26:** NBA.com pulls via `nba_api` where access is available.
- **Efficiency Tax Sept. 12 test:** Basketball-Reference salary tables + player games, normalized to a 480 team-season panel for 2011–2026.

## Method notes

- **AQI** = `net_rating × usg × (TS / 0.550)` per player-season. Team anchor = highest-AQI rotation player subject to eligibility rules.
- **RQS** = `AQI1×4 + AQI2×2 + interior_anchor×3 + late_draft_elite×1`; the September result limits forecast use but does not erase descriptive use.
- **Efficiency Tax:** the September mechanism is concentrated payroll in players who miss games; concentration itself is positively associated with winning, so the old “concentration is the tax” reading is wrong.
- **CEV / clutch:** outcome-based team clutch is not a stable trait in the Sept. 12 test; a separate player-process question remains open.

*Original Phase 1 generated 2026-07-04; SSAC27 lanes added 2026-08-26; September sprint evidence added 2026-09-13; reproducibility/release-state sync updated 2026-09-15.*
