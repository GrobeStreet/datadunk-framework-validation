# Validation: RQS "100% Top-5" — Out-of-Sample Test (held-out champions 2024–2026)

**Date:** 2026-07-04 · **Desk:** Evidence → Canon correction · **Status: `Evidence` — the universal claim is FALSIFIED**
**Goal:** Ledger's last untested Tier-B claim. RQS's weights/thresholds were built on 2000–2023 champions, so "every champion finished top-5 in RQS" is in-sample. The true test: does the top-5 filter hold on the **2024, 2025, 2026 champions it was never tuned on** (the June 1 backtest explicitly excluded 2024–26 for lack of data)? Data pulled live via `nba_api` (real on-court NET_RATING, consistent with the upgraded AQI). Code: `/tmp/rqs_oos.py`, `/tmp/rqs_2026_detail.py`.

## Verdict: FAILS out-of-sample. The 2026 Knicks are the counterexample.

RQS = AQI1×4 + AQI2×2 + interior_anchor×3 + late_draft_elite×1, ranked within season:

| Season | Champion | Kind | RQS rank (of 30) | Top-5? | Note |
|---|---|---|---|---|---|
| 2023 | Denver | in-sample **control** | **#1** | ✅ | pipeline reproduces the known result |
| 2024 | Boston | held out | **#2** | ✅ | passes |
| 2025 | Oklahoma City | held out | **#1** | ✅ | passes |
| **2026** | **New York** | **held out** | **#8** | ❌ | **breaks the claim** |

Held-out record: **2 of 3 champions in the top 5.** One clean counterexample falsifies a "100% / universal" claim. And 2026 isn't a near-miss — the Knicks are **#8 of 30, #7 among the 12 auto-clinched playoff teams, #8 among the full 20-team playoff field.** No slicing of the playoff field puts them in the top 5: six auto-playoff teams (OKC, SAS, DET, DEN, BOS, CLE) outrank the actual champion.

## Why: the Knicks are a flat, clutch champion with no dominant AQI star

NYK's top three by AQI are nearly identical and all modest — none near the ~3.6 champion-anchor norm:

| NYK player | GP | MPG | NET | USG | TS | AQI |
|---|---|---|---|---|---|---|
| OG Anunoby | 67 | 33.2 | +9.2 | .194 | .620 | 2.01 (AQI1) |
| Karl-Anthony Towns | 75 | 31.0 | +7.0 | .251 | .619 | 1.98 (AQI2) |
| **Jalen Brunson (Finals MVP)** | 74 | 35.0 | +6.1 | **.296** | .580 | **1.90** |

RQS = 2.01×4 + 1.98×2 + 1(anchor) ×3 + 3(late) = **18.0**, vs OKC 39.6, SAS 35.5. Brunson — the Finals MVP, 45 points in the clinching game — is a **high-usage (29.6%), good-not-elite-efficiency (.580 TS), moderate-net guard**: the "Ghost Points" profile. The 2026 Knicks won on clutch execution (four Finals games decided by ~4, "historically clutch"), not regular-season net-rating dominance. RQS, a roster-star-quality index, structurally underrates that kind of champion.

**This is the same failure mode as the AQI floor's binding case (2004 Detroit).** Balanced, defense/clutch champions without a separated top-2 AQI punish roster-quality metrics. 2004 Detroit and 2026 New York are the two archetypes RQS cannot see.

## Robustness

- **Pipeline control passes:** 2023 Denver reproduces at #1, confirming the computation is sound before trusting the held-out years.
- **NYK is not a filter artifact:** Brunson clears the rotation filter (74 GP, 35 MPG); his AQI is genuinely third, not excluded. The result survives inspection.
- **Not a playoff-field definition issue:** NYK is outside the top 5 under all three definitions (all-30, auto-12, field-20).
- **Small n (3 held-out champions)** — but one unambiguous counterexample is sufficient to falsify a universal ("100%") claim, which is what was asserted.

## Verdict for the canon

**Retire the "RQS 100% top-5" claim.** RQS remains a *reasonable roster-star-quality index* — champions usually rank well (DEN #1, BOS #2, OKC #1) — but it is **not a universal champion filter.** On the only true out-of-sample test available, it caught 2 of 3 and missed the actual 2026 champion by a wide margin. Downgrade RQS from "strongest single predictive filter" to **descriptive roster-quality index (in-sample r≈0.36; OOS top-5 hit 2/3)**, and never publish "100%." The honest headline is sharper anyway: *the two champions our roster-quality metric can't see are the 2004 Pistons and the 2026 Knicks — the defense-and-clutch archetype.*

*Sources: `nba_api` LeagueDashPlayerStats (Advanced) 2022-23 … 2025-26 + DraftHistory + LeagueStandingsV3; `DataDunkNBA_Formula_Registry.md`; `Framework_Validity_Ledger_2026-07-04.md`. 2026 champion (NYK over SAS 4–1, Brunson Finals MVP) web-verified via NBA.com/ESPN.*
