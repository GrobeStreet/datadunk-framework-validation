# v6 Sprint — Results (2026-09-12)

**Desk:** Evidence · **Status:** three pre-registered tests run; two on the Mac warehouse, one from a fresh Basketball-Reference pull. Gates were written before the numbers were seen (see `00_README_RUN_ORDER.md`).

| # | Test | Gate | Result | Verdict |
|---|---|---|---|---|
| 1 | **CEV_close** — forecast-safe clutch from close-game results | r(champ) ≥ 0.25 AND persistence ≥ 0.40 | r(champ) = **+0.19** (raw close W%) / **−0.16** (clutch residual); persistence **0.16–0.22** (NetRtg: 0.60) | **Fails both.** Team-level clutch, measured by outcomes, is noise. The Clutch Paradox stays open only as a *player-process* question. |
| 2 | **RQS as a preseason predictor** | +0.02 OOS R² over prior-season NetRtg | prior RQS alone R² 0.346 vs NetRtg 0.388; NetRtg + RQS **+0.004** | **Fails.** RQS is a same-season descriptor (R² 0.76), not a forecaster — at least as naively lagged. |
| 3 | **Efficiency Tax on its own terms** — salary concentration × availability vs RS win% | pooled r ≤ −0.15, sign stable ≥ 10/15 seasons | pooled r = **−0.394**; negative in **16/16** seasons (median −0.41); 2025-26 alone −0.578 | **PASSES.** The June 29 burial tested the wrong design. The construct is back — with a corrected mechanism (below). |

---

## 1. CEV_close — clutch is not a team trait (`Evidence`)

NBA.com's clutch endpoint is unreachable from both environments, so the test used what the warehouse has: every regular-season game 2008–2025 (`parquet_gamedata_with_lines.csv`), close game = final margin ≤ 5. Two measures per team-season: raw close-game W%, and the *clutch residual* (close W% − overall W%), each z-scored within season. 500 team-seasons matched to the panel (game-file W% vs panel W% r = 0.98).

- **Raw close-game W%** ↔ champion: r = 0.186; champion top-5 8/17. Weak.
- **Clutch residual** ↔ champion: r = **−0.158**; champions average **−0.113** (they win their close games *less* often than their overall record, because elite teams' overall record is built on blowouts and close games are coin-flips). Same-season r with W% = −0.62 — pure mean reversion.
- **Persistence:** close-game W% year-to-year r = **0.158**; residual 0.215; NetRtg 0.603 for scale. It doesn't carry over.
- **Forecast value:** next-season W% ~ prior NetRtg R² 0.390; adding the clutch residual → 0.395. Nothing.
- **Swapping CEV_close into WEV:** r(champ) 0.366 → 0.379, hit-rates unchanged — within noise.

**Read:** the leaky CEV_partial (r = 0.389 here) was "the strongest signal in the stack" only because it contains the playoff result. A forecast-safe clutch measure built from outcomes has no title signal and no persistence. This answers the *team-level* Clutch Paradox: no. What it does **not** test is the *player-process* version (clutch TS% vs regulation TS% for a specific creator) — that still needs NBA.com clutch splits or the possession parquet, and stays `Idea`.

**Canon action:** WEV v3 keeps its 0.10 CEV weight only as legacy; the honest operational form is `WEV_noCEV = (0.30·OEV + 0.60·DEV)/0.90`, which the hold-out shows is indistinguishable. Strike "CEV Elite tier" and the 0.20 proposal.

## 2. RQS — a descriptor, not a forecaster (`Evidence`)

Leave-one-season-out, 677 team-seasons 2001–2024, every feature from the *prior* season of the same franchise, target = current W%.

| Spec | OOS R² | MAE (wins) | Δ vs prior NetRtg |
|---|---|---|---|
| prior W% | 0.379 | 7.7 | −0.009 |
| **prior NetRtg** | **0.388** | 7.6 | — |
| prior RQS | 0.346 | 7.9 | −0.042 |
| prior AQI2 | 0.332 | 8.0 | −0.056 |
| prior Floor% | 0.330 | 8.0 | −0.058 |
| NetRtg + RQS | 0.392 | 7.6 | **+0.004** |
| NetRtg + RQS + Floor% | 0.391 | 7.6 | +0.003 |

Same-season RQS R² with W% = 0.764. Lagged one year it's 0.348 and adds nothing over last year's point differential.

**Read:** RQS describes a roster's quality *once the season has revealed it* — a fine lens for "why did this team win," not for "who will win." It stays a full member of the stack as a descriptor. **The honest v2 test** is projected AQI from *returning* players only (roster turnover is unmodeled here); that's the next expound, not a burial.

## 3. Efficiency Tax — the burial was wrong; the mechanism was misnamed (`Evidence`, restored)

Fresh pull: Basketball-Reference salary tables + player games for all 30 teams, 2011–2026 (480 team-seasons, 16 champions). Rebuilt *exactly* the Registry definition: `fragility = top-3 salary share × (1 − top-3 availability)`, against regular-season W%.

| Relationship | r |
|---|---|
| top-3 **salary share** ↔ W% | **+0.279** |
| top-3 **availability** (games/82) ↔ W% | **+0.472** |
| **fragility** (share × (1−avail)) ↔ W% | **−0.394** |
| fragility ↔ is_champion | −0.078 |

Per-season: r(fragility, W%) negative in **16 of 16** seasons, range −0.15 to −0.62, median −0.41. The original −0.639 (2025-26, n=30) reproduces here at −0.578 and is an ordinary year, not a fluke.

Band check: champions in the 55–70% *salary* band **69%** vs field 41% (mean champion share 0.582 vs 0.534).

**But the decomposition changes what the framework means:**

| Model | R² |
|---|---|
| W% ~ availability | 0.223 |
| W% ~ salary share | 0.077 |
| W% ~ availability + share (additive) | **0.276** |
| W% ~ fragility (the multiplier) | 0.155 |

The multiplier form is *worse* than its two components added. And concentration's sign is **positive** — teams that concentrate payroll win *more*, because good teams pay their stars (selection, not causation). The negative "tax" is entirely **top-earner availability**: whether the three players you're paying actually play.

**Canon action:** Efficiency Tax returns as `Evidence` with a corrected statement — *the tax is paid in games missed by the players you've concentrated payroll in; concentration itself is not the risk, unavailability of the concentrated dollars is.* The multiplier is retired **as a functional form** (not as a claim of no signal); the operational measure is the additive pair, which is what CSG (Cap Space Ghost) already computes per player. Caveat that stays in every citation: same-season availability ↔ same-season wins is partly mechanical; the forecast-time version (projected availability from injury history) is the next test.

---

## What changed in the canon

- **CEV:** outcome-based clutch fails as a trait → WEV_noCEV is the honest operational form; Clutch Paradox narrows to a player-process question.
- **RQS:** descriptor confirmed, forecaster refuted (as lagged) → v2 test = projected-returning-roster AQI.
- **Efficiency Tax:** June 29 burial overturned on the right design (r −0.39, 16/16 seasons); mechanism corrected to top-earner availability; multiplier retired as form; merge with CSG.
- **New headstone:** "Efficiency Tax has no signal (r ≈ 0.003)" — that claim was itself an artifact of testing Win Shares against titles.
- **Reinforced:** the feature-provenance step. Two of three sprint results turned on *what was actually being measured*, not on statistics.

## Files in this folder

- `01_cev_rs_forecast_safe.py` — NBA.com clutch-split version (needs `nba_api`; kept for when that access returns)
- `02_rqs_preseason_record_model.py`
- `03_efftax_on_its_own_terms.py` → `efftax_results.md`
