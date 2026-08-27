# The Wall Travels — SSAC27 hardening specification v2

**Status:** prespecified hardening plan before any v2 abstract update  
**Date:** 2026-08-26  
**Track:** Basketball  
**Question:** Does NBA rim suppression contain a portable player-specific component after accounting for scheme/context and measurement noise?

## Why v2 is necessary

The current reproduced lane establishes positive year-to-year persistence and positive persistence among team changers, but the original Substack framing is too strong for a conference paper. Two problems must be addressed before promotion:

1. Prior public work already asked whether rim protection travels across teams, so novelty cannot rest on asking that question first.
2. The current `reliability_floor` calculation subtracts a simple binomial noise bound from observed variance. Because NBA.com's `PLUSMINUS` is itself a difference between defended FG% and opponents' normal FG%, that calculation does not model every source of uncertainty and must not carry the main empirical claim.

The v2 paper therefore treats the existing receipt as a reproduced starting point, not as the final Sloan specification.

## Primary estimand

For defender `i` observed in seasons `t` and `t+1`, estimate portability with:

`suppression_{i,t+1} = alpha + beta*suppression_{i,t} + gamma*mover_i + delta*(suppression_{i,t}*mover_i) + controls + error_i`

where suppression is NBA.com `LeagueDashPtDefend` `PLUSMINUS` for `DefenseCategory=Less Than 6Ft`; lower is better. The key quantities are:

- `beta`: persistence among stayers;
- `beta + delta`: persistence among movers;
- `delta`: whether the persistence slope is detectably different after changing teams.

Movement is observational. This design tests **portability**, not causal treatment effects of changing teams.

## Data contract

Use NBA.com `LeagueDashPtDefend`, regular season, `DefenseCategory=Less Than 6Ft`, for 2023-24, 2024-25, and 2025-26.

Prefer `PerMode=Totals` for the v2 validation pull so defended-attempt exposure is observed directly rather than reconstructed from rounded per-game rates. Preserve the existing frozen `PerMode=PerGame` snapshots for exact v1 reproduction.

Required fields:

- `CLOSE_DEF_PERSON_ID`
- `PLAYER_NAME`
- `PLAYER_LAST_TEAM_ABBREVIATION`
- `PLAYER_POSITION`
- `AGE`
- `GP`
- `FGA_LT_06`
- `PLUSMINUS`

Any player with ambiguous multi-team attribution must be flagged. The last-team abbreviation is not automatically treated as a complete transaction history.

## Prespecified sensitivity grid

Run the full adjacent-season analysis at minimum defended-rim-attempt thresholds:

`50, 80, 100, 150`

The historical 80-attempt rule is retained because it reproduces the frozen July result, but it is explicitly post-hoc/reconstructed. No single threshold may be selected after looking at which produces the strongest result.

For each threshold report:

- n paired players;
- Pearson r;
- Spearman rho;
- mover n / stayer n;
- mover Pearson and Spearman;
- stayer Pearson and Spearman;
- bootstrap 95% intervals;
- mover-minus-stayer difference interval;
- interaction-regression coefficients and uncertainty.

## Exposure and role robustness

The mover/stayer comparison must address the possibility that changers differ systematically in opportunity or role.

At minimum run:

1. unweighted analysis;
2. exposure-weighted regression using a transparent function of defended rim attempts in both seasons;
3. position-stratified or position-controlled analysis;
4. age-controlled analysis when available;
5. a matched/reweighted mover-vs-stayer analysis using prior-season exposure and position if support is sufficient.

If overlap/support is poor, report the failure rather than extrapolate.

## Shrinkage / measurement-error robustness

Raw single-season percentages are noisy. Add a prespecified shrinkage analysis that pulls defender `PLUSMINUS` toward the league mean as a function of defended-rim exposure. The main conclusion must be compared across raw and shrunken estimates.

Do not describe the existing variance-subtraction statistic as a validated reliability floor unless a derivation explicitly accounts for the uncertainty in both components of `PLUSMINUS`.

## Negative-control / contrast test

If the same endpoint can be frozen reproducibly for a perimeter category, run the same persistence analysis there as a contrast. The purpose is not to manufacture significance; it is to test whether rim suppression is more portable than a shot-defense category known to be highly volatile.

If a clean perimeter category cannot be defined from the same source contract, omit this analysis and state why.

## Prior-work positioning

The paper must acknowledge that earlier public analyses already studied mover/stayer rim protection. In particular, a 2017 public analysis using opponent rim FG% reported approximately r=.54 for same-team centers and r=.20 for team changers and interpreted that gap as evidence for team-system influence.

The novelty claim for v2 is narrower:

- modern NBA.com shooter-baseline-adjusted `PLUSMINUS` rather than raw opponent rim FG%;
- three recent seasons;
- all qualifying defenders rather than a center-only anecdotal sample;
- explicit mover/stayer uncertainty and interaction testing;
- open-source reproduction with source hashes;
- willingness to retain the null if mover portability weakens under shrinkage/controls.

## Promotion gate

A v2 Sloan abstract may be written only after:

1. the Totals-source validation reproduces the v1 results within expected rounding tolerance;
2. the threshold grid is complete;
3. Pearson and Spearman point in the same qualitative direction;
4. the mover portability estimate remains positive across the reasonable sensitivity grid, or the abstract is rewritten to report that it does not;
5. interaction/matching results are reported regardless of direction;
6. every public number in the abstract is generated into a new machine-readable receipt.

## Allowed language before the gate passes

Allowed now: **“Three-season NBA.com data reproduce moderate year-to-year rim-suppression persistence, including positive raw persistence among team changers; a hardened portability analysis is in progress.”**

Not allowed now: “the wall travels,” “causal player trait,” “scheme does not matter,” “stable defender skill,” or a claim that mover persistence is statistically equal to stayer persistence.
