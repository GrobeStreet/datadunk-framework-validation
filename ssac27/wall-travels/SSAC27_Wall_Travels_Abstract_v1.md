# The Wall Travels: Separating Player Signal from Team Scheme in NBA Rim Suppression

**Author:** Robert Morong (DataDunkNBA)  
**Track:** Basketball  
**Status:** submission candidate v1 — not yet submitted

## Introduction

Public defensive metrics are entangled with team scheme: a rim defender may look effective because of his own contests, the teammates around him, or the shots the system concedes. We test whether opponent shooting suppression at the rim contains a repeatable player component and, more stringently, whether that component persists when defenders change teams.

## Methods

We use NBA.com LeagueDashPtDefend tracking for the 2023-24, 2024-25, and 2025-26 regular seasons. Rim suppression is the closest defender's opponent field-goal percentage within six feet minus those opponents' normal percentage in that zone; lower values indicate greater suppression. For defenders with at least 100 defended rim attempts, we subtract a conservative binomial sampling-noise bound from observed between-player variance. For persistence, players must have at least 80 defended rim attempts in both compared seasons. We calculate adjacent- and two-year correlations, then compare 2024-25 to 2025-26 players who changed teams with players who stayed. Player bootstrap intervals quantify correlation uncertainty, including the difference between mover and stayer persistence.

## Results

The signal survives the noise correction in all three seasons: the estimated true-signal standard-deviation floor is 6.8 percentage points in 2023-24 (n=492), 3.5 in 2024-25 (n=334), and 6.4 in 2025-26 (n=509), with reliability floors of .96, .50, and .96. Suppression persists year to year but is not fixed: r=.423 (n=324) from 2023-24 to 2024-25, r=.400 (n=329) from 2024-25 to 2025-26, and r=.272 over two years. Among 111 team changers, persistence remains positive at r=.337 (95% player-bootstrap CI .165-.480); among 218 stayers it is r=.450 (.326-.559). The mover-minus-stayer difference is not statistically resolved (bootstrap 95% CI for the correlation difference, -.32 to .08).

## Conclusion

NBA rim suppression contains a meaningful player-specific signal, but it evolves substantially across seasons. Most importantly, positive persistence survives team changes, while the data do not support a claim that movers lose the relationship entirely. Front offices should therefore treat rim defense as a portable but noisy player attribute embedded in scheme, not as either a pure team effect or a fixed individual constant. The result provides an open-source framework for separating defensive personnel signal from context without claiming that observational team movement identifies causality.

**Word count:** approximately 375 words including title; safely below the SSAC27 500-word maximum.  
**Open source:** `github.com/GrobeStreet/datadunk-framework-validation/tree/main/ssac27/wall-travels`
