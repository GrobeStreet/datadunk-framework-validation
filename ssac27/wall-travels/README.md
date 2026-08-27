# The Wall Travels — SSAC27 research lane

**Candidate title:** *The Wall Travels: Separating Player Signal from Team Scheme in NBA Rim Suppression*  
**Track:** Basketball  
**Status:** reproduced / submission candidate; not yet submitted  
**Author:** Robert Morong (DataDunkNBA)

## Question

Public defensive metrics are entangled with team scheme. This study asks whether opponent shooting suppression at the rim contains a repeatable player component, and whether that component survives when the defender changes teams.

## Data

The source is NBA.com `LeagueDashPtDefend`, `DefenseCategory=Less Than 6Ft`, regular season, `PerMode=PerGame`, for:

- 2023-24
- 2024-25
- 2025-26

The historical raw Parquet snapshots were byte-frozen in the controlled research store. They are not redistributed here; `reproduce.py --fetch` can regenerate public-source CSVs from NBA.com, and `source_manifest.json` records the hashes of the frozen source snapshots used for the receipt.

`FGA_LT_06` is returned in per-game units. Total defended rim attempts are therefore reconstructed as:

```text
TOTAL_RIM_FGA = FGA_LT_06 * GP
```

## Primary measurement

NBA.com's `PLUSMINUS` for this endpoint is the defender's opponent FG% within six feet minus the opponents' normal FG% in that zone. Lower values indicate more shooting suppression relative to shooter baseline.

Two historical eligibility rules are used:

- **Signal/noise:** at least 100 total defended rim FGA in the season.
- **Persistence/movement:** at least 80 total defended rim FGA in each compared season.

The 80-attempt persistence rule was reconstructed from the frozen July result because it exactly regenerates the documented sample sizes and correlations. It is **not** represented as independently preregistered.

## Reproduced results

| Test | Result |
|---|---:|
| 2023-24 true-signal SD floor | 0.0683 (n=492; reliability floor .958) |
| 2024-25 true-signal SD floor | 0.0349 (n=334; reliability floor .500) |
| 2025-26 true-signal SD floor | 0.0637 (n=509; reliability floor .961) |
| 2023-24 -> 2024-25 persistence | r=.4227 (n=324) |
| 2024-25 -> 2025-26 persistence | r=.4001 (n=329) |
| 2023-24 -> 2025-26 persistence | r=.2723 (n=340) |
| 2024-25 -> 2025-26 movers | r=.3368 (n=111; bootstrap 95% CI .165-.480) |
| 2024-25 -> 2025-26 stayers | r=.4499 (n=218; bootstrap 95% CI .326-.559) |
| mover minus stayer correlation | bootstrap 95% CI -.316 to +.078 |

The strongest defensible interpretation is narrower than the original Substack headline: **rim suppression has a repeatable player component that remains positively associated across team changes, but it is not a fixed trait and observational movement does not identify causality.**

## Reproduce

With previously fetched CSVs:

```bash
python reproduce.py --data-dir data --out results/receipt.json
```

Or attempt a fresh public-source pull:

```bash
python reproduce.py --fetch --data-dir data --out results/receipt.json
```

NBA.com blocks some cloud hosts, so the fetch step may need to run from a local connection.

## Claim boundaries

This lane does **not** claim:

- that team changes are randomized natural experiments;
- that the player is more important than scheme in a causal sense;
- that rim suppression is a fixed stable trait;
- that the result predicts championships;
- that a same-season matchup regression is causal without cross-fitting.

The player-movement result is an associational portability test. That limitation is part of the paper, not a footnote.
