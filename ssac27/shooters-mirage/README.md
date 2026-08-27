# The Shooter's Mirage - SSAC27 research lane

**Candidate title:** *The Shooter's Mirage: Does Prior Three-Point Skill Compress in the NBA Playoffs?*  
**Track:** Basketball  
**Status:** BLOCKED / RETEST REQUIRED - not submission-ready  
**Author:** Robert Morong (DataDunkNBA)

This lane preserves the June 2026 exploratory result while preventing the original article's strongest claims from being promoted into a conference submission without a clean retest.

The source article documented 422 playoff games and a shot-tracking analysis in which the wide-open Elite-minus-Sub-Avg 3P% gap was 10.6 percentage points in the regular season and 1.7 in the playoffs. The old raw files were recorded as temporary `/tmp/` paths and were not recovered in the August 26 audit. The published aggregate result is therefore **documented but not raw-data reproduced**.

`audit_published_summary.py` rechecks only the arithmetic/uncertainty available from the published aggregate counts and runs design-diagnostic simulations. It is explicitly not a substitute for the raw-data retest.

The hardened study is specified in `HARDENING_SPEC_v1.md`. The key changes are prior-only shooter skill, continuous rather than extreme-tier effects, player-clustered/hierarchical inference, and game-level analysis that never conditions on final margin.
