# Wall Travels SSAC27 v2 status

**Date:** 2026-08-26  
**Status:** HOLD - v1 is reproduced; v2 promotion gate is not yet passed.

## What is already reproduced

The frozen v1 receipt regenerates the three-season NBA.com `LeagueDashPtDefend` rim-suppression persistence result from the canonical CSV exports:

- 2023-24 -> 2024-25: Pearson r = 0.4227357527, n = 324.
- 2024-25 -> 2025-26: Pearson r = 0.4000830812, n = 329.
- 2023-24 -> 2025-26: Pearson r = 0.2722534317, n = 340.
- 2024-25 -> 2025-26 movers: r = 0.3368138812, n = 111, bootstrap 95% [0.1652608907, 0.4795431177].
- Stayers: r = 0.4499101223, n = 218, bootstrap 95% [0.3259682312, 0.5593064012].
- Mover-minus-stayer r difference bootstrap 95% [-0.3160765486, 0.0775134048].

These are **portability associations**, not randomized evidence that team changes do or do not cause defensive performance.

The raw adjacent-season persistence also failed the previously stated `r >= .50` stability target. That miss remains part of the paper.

## What was hardened after the v1 reproduction

`HARDENING_SPEC_v2.md` freezes the conference-grade question and sensitivity plan. `reproduce_v2.py` implements a fail-closed threshold grid (50/80/100/150 defended rim attempts), Pearson/Spearman estimates, mover/stayer bootstrap intervals, and unweighted/exposure-weighted interaction regressions with age and position controls.

The stronger novelty claim is not simply that defenders who move teams retain some signal; earlier public work asked related questions. The v2 contribution must be the modern shooter-baseline-adjusted NBA.com measure, explicit uncertainty, open-source receipts, and a willingness to retain a weak/zero mover interaction if that is what the robust test shows.

## Current blocker

The v2 harness requires fresh/frozen `PerMode=Totals` source CSVs for 2023-24, 2024-25, and 2025-26. This execution environment cannot complete the NBA.com pull, and those three Totals-mode source files are not currently committed to the repository. Therefore `results/receipt_v2.json` does not exist and the v2 promotion gate has **not** passed.

The original v1 sources remain fingerprinted in `source_manifest.json`; raw NBA.com data are not redistributed there.

## Submission rule

Do not submit a new Wall Travels abstract as if v2 is validated until the full v2 receipt is generated. The strongest allowed language in the meantime is:

> Three-season NBA.com data reproduce moderate year-to-year rim-suppression persistence, including positive raw persistence among team changers; a hardened portability analysis is in progress.

Forbidden until the v2 gate passes: `causal player trait`, `scheme does not matter`, `stable defender skill`, or treating the title phrase **The Wall Travels** as a proven causal law.
