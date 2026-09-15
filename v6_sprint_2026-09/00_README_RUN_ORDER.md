# v6 sprint reproduction run order

Status: 2026-09-15 canon sync.

These scripts restore the executable calculation layer referenced by the September 12 sprint results. They intentionally fail closed when the required source export is absent. Raw third-party source files are not redistributed in this repository.

## 1. CEV / close-game team-trait test

Input: a regular-season game-level CSV with one row per game and home/away teams and final scores, plus the canonical team-season panel containing W_PCT, NetRtg, champion label, OEV, DEV, and historical CEV/WEV fields.

Run:

```bash
python v6_sprint_2026-09/01_cev_rs_forecast_safe.py \
  --games /path/to/parquet_gamedata_with_lines.csv \
  --panel /path/to/team_seasons_full.csv
```

The September receipt used the warehouse game file covering 2008-2025. If a different source or date span is used, the result is a new receipt and must not be presented as the September reproduction.

## 2. RQS preseason-record test

Input: canonical team-season panel with Season, Abbrev, W_PCT, NetRtg, RQS, AQI2, and Floor Pct fields.

Run:

```bash
python v6_sprint_2026-09/02_rqs_preseason_record_model.py \
  --panel /path/to/team_seasons_full.csv
```

The script uses leave-one-target-season-out OOS linear regression on prior-season franchise features for 2001-2024. It includes franchise continuity mappings used in the September receipt.

## 3. Efficiency Tax on its own terms

Input: a frozen normalized team-season CSV with:

`season,team,w_pct,top3_salary_share,top3_availability,is_champion`

Run:

```bash
python v6_sprint_2026-09/03_efftax_on_its_own_terms.py \
  --input /path/to/efftax_team_seasons_2011_2026.csv
```

The September receipt came from a fresh Basketball-Reference salary + player-games pull for 2011-2026. That raw snapshot is not currently committed, so the exact September result is receipt-backed but not fully self-contained in GitHub. Do not call it independently reproduced from this repository until the frozen source export is added and hashed.

## Reproducibility boundary

- RQS calculation: executable from the canonical team-season export and independently re-run during the Sept. 15 sync.
- CEV: calculation script restored; exact September game source must be supplied.
- Efficiency Tax: calculation script restored; exact September normalized source must be frozen before full reproduction status.

The scripts compute; `SPRINT_RESULTS_2026-09-12.md` remains the human-readable receipt. New source snapshots require new hashes and a new result receipt.
