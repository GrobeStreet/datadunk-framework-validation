# The Shooter's Mirage - SSAC27 hardening specification v1

**Status:** BLOCKED pending raw-data regeneration / clean retest  
**Date:** 2026-08-26  
**Track:** Basketball  
**Question:** Does prior three-point shooting skill retain the same relationship to shot conversion and team outcomes in the NBA playoffs as it does in the regular season?

## Why the published study cannot be submitted unchanged

The June 17 exploratory study produced a provocative pattern: the published wide-open elite-vs-sub-average gap was 10.6 percentage points in the regular season and 1.7 points in the playoffs, while the higher-regular-season-3P% team won 56.4% of all 422 playoff games but 50.0% of the 100 games that finished within six points. Those are descriptive findings worth retesting. They are not yet a Sloan-grade causal or predictive result.

Five design problems are now frozen before any new result is viewed:

1. **Regression to the mean:** shooter tiers were defined from the same regular-season shooting measurements later contrasted with playoff measurements. Extreme observed RS groups are expected to move toward the center on remeasurement even if true shooting skill does not change.
2. **Post-outcome conditioning:** "close games" were defined by final margin. Final margin is partly caused by shooting performance, so conditioning on it can attenuate or distort the very shooting effect being tested.
3. **Repeated-shot dependence:** thousands of attempts are clustered within shooters, teams, series, and seasons. Attempt-level uncertainty must not treat every shot as independent.
4. **Selection into shot quality:** a 6+ foot nearest-defender bucket does not make shots exchangeable. Shooter role, location, action type, lineup, and defense selection can differ by shooting reputation.
5. **Leverage-label error:** "Game 5+" is not synonymous with elimination pressure. A Game 5 at 2-2 is not an elimination game. Series state must be reconstructed explicitly.

The payroll extrapolation and the claim that teams should tear down the specialist archetype are outside this validation lane.

## Primary estimand: prior skill x postseason interaction

The primary player-shot model must define shooting skill using **information available before the evaluation regular season/playoffs**. No player may be classified as elite using the same RS sample whose playoff translation is being tested.

Preferred specification for evaluation season `t`:

`logit(P(make)) = alpha + beta*prior_3P_skill_z + gamma*playoffs + delta*(prior_3P_skill_z*playoffs) + shot_context + season_FE + player_effect`

The target is `delta`: whether the slope linking prior shooting skill to conversion changes in the playoffs. The paper should report the continuous slope, not rely on extreme tier cutoffs.

### Prior-skill construction

- Build prior 3P skill from seasons strictly before `t`.
- Minimum prior exposure must be prespecified and sensitivity-tested (for example 200 / 400 / 600 3PA).
- Use shrinkage toward league average so a 40% label is not driven by a small prior sample.
- Freeze one primary prior window (recommended: trailing two regular seasons) before running the outcome model.

### Shot context

At minimum condition/stratify on:

- closest-defender distance bucket;
- corner vs above-break three when available;
- season;
- team / lineup or role proxy when available.

Primary reporting should include all 3PA plus a prespecified open/wide-open subgroup. The subgroup is secondary, not selected because it gives the largest compression.

### Inference

Use player-clustered uncertainty or a hierarchical binomial/logistic model with repeated player observations. If team/series clustering materially changes uncertainty, report it.

## Secondary estimand: team-level playoff translation

Do **not** define leverage by final game margin.

For each playoff game, construct before-tip predictors:

- difference in prior/regular-season team 3P skill;
- team strength controls (at minimum W%, Net Rating or SRS);
- home court;
- series state known before the game;
- season fixed effects.

Estimate whether team shooting skill adds held-out win-probability information beyond baseline team strength. Report log loss/Brier/AUC or an equivalent prespecified predictive score, not only winner percentages.

### High-leverage subgroups

Allowed high-leverage definitions must be knowable **before the outcome**:

- true elimination game from reconstructed series score;
- Game 7;
- optionally pregame expected closeness if a frozen betting-line source is available.

A fourth-quarter state analysis is allowed only if the state is defined at a fixed time (for example 5:00 remaining) before the final outcome.

## Temporal validation

Preferred design:

- discovery / model-development window: 2023-24 and 2024-25 tracking if required;
- held-out confirmation: 2025-26, with all definitions frozen before reading the confirmation result.

If historical tracking coverage permits a longer rolling evaluation, use expanding-window or leave-one-season-out validation instead and preserve a final untouched season.

## Falsification / sensitivity tests

1. continuous prior-skill slope rather than only elite/sub-average bins;
2. prior-exposure thresholds 200 / 400 / 600;
3. trailing-one-year vs trailing-two-year skill estimates;
4. all threes vs open/wide-open threes;
5. player-clustered vs player+team/series robust uncertainty;
6. remove each season in turn;
7. no final-margin conditioning anywhere in the primary analysis;
8. negative-control simulation demonstrating how much apparent compression can arise from extreme-group selection under no true playoff compression.

## Raw-data recovery / regeneration contract

The June study listed four `/tmp/` files as files of record, but the 2026-08-26 audit did not locate those raw files in Google Drive, File Library, or the GitHub repositories searched:

- `league_3pt_by_defender_dist.csv`
- `po_5seasons.csv`
- `rs_team_5seasons.csv`
- `playoff_games_5seasons_with_3pt.csv`

Therefore the old numerical tables are treated as **documented, not reproduced** until those exact files are recovered or regenerated from source. New raw pulls get hashes and a manifest before analysis.

## Promotion gate

A Sloan abstract can be promoted only after:

1. raw source snapshots are frozen and hashed;
2. the prior-only player-skill definition is frozen;
3. clustered/hierarchical player-shot inference is complete;
4. the game-level model uses no final-margin selection;
5. true elimination states are reconstructed;
6. at least one time-respecting held-out test is complete;
7. the abstract reports the result even if the compression disappears.

## Allowed language now

Allowed: **"An exploratory 2020-25 study found striking regular-season-to-playoff compression in wide-open three-point shooting and little close-game separation by regular-season 3P%, but a clean retest is required because the original design used extreme-group selection and final-margin conditioning."**

Not allowed now: "shooting talent does not decide playoff games," "$430M is mispriced," "variance rather than skill decides series," or "specialists have no playoff value."
