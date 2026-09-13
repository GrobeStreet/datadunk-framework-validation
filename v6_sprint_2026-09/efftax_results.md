# Efficiency Tax — tested as originally designed (SALARY concentration × availability vs RS win%)

Source: Basketball-Reference team pages, salaries + totals tables, pulled 2026-09-12. Team-seasons: 480 (2011–2026), champions 16.

| Relationship | r |
|---|---|
| top-3 SALARY share vs W% | 0.279 |
| top-3 availability (games/82) vs W% | 0.472 |
| fragility = share × (1 − avail) vs W% | -0.394 |
| top-3 share vs is_champion | 0.102 |
| fragility vs is_champion | -0.078 |

Champions in the 55–70% SALARY band: 69% · field: 41%
Mean top-3 salary share — champions 0.582 vs field 0.534
Mean top-3 availability — champions 0.800 vs field 0.698
Mean fragility — champions 0.1179 vs field 0.1602

Per-season cross-sections (the original −0.639 was ONE of these, 2025-26):

| Season | r_frag | r_share | r_avail |
|---|---|---|---|
| 2011 | -0.406 | 0.320 | 0.456 |
| 2012 | -0.421 | 0.415 | 0.633 |
| 2013 | -0.359 | 0.595 | 0.481 |
| 2014 | -0.342 | 0.351 | 0.416 |
| 2015 | -0.621 | 0.059 | 0.607 |
| 2016 | -0.454 | -0.087 | 0.438 |
| 2017 | -0.288 | 0.369 | 0.359 |
| 2018 | -0.292 | 0.397 | 0.367 |
| 2019 | -0.566 | 0.361 | 0.601 |
| 2020 | -0.476 | 0.264 | 0.567 |
| 2021 | -0.482 | 0.236 | 0.566 |
| 2022 | -0.369 | 0.182 | 0.434 |
| 2023 | -0.147 | 0.529 | 0.399 |
| 2024 | -0.291 | 0.648 | 0.437 |
| 2025 | -0.595 | 0.040 | 0.696 |
| 2026 | -0.578 | 0.033 | 0.635 |

Seasons with r(fragility,W%) < 0: 16/16; median -0.413

| Model | R² | coefs |
|---|---|---|
| W% ~ top3_avail | 0.223 | [0.397] |
| W% ~ top3_share | 0.077 | [0.499] |
| W% ~ top3_avail + top3_share | 0.276 | [0.376, 0.414] |
| W% ~ fragility | 0.155 | [-0.608] |
| W% ~ top3_avail + fragility | 0.248 | [0.771, 0.729] |

Pre-registered gate: pooled r(fragility, W%) ≤ −0.15 with sign stable in ≥10/15 seasons → multiplier back as `Evidence`; |r| < 0.10 → burial stands on the right design.

**Verdict:** PASSES. Mechanism corrected: the tax is paid in games missed by the players payroll is concentrated in; concentration itself is positively associated with winning (selection). Multiplier retired as a functional form; operational measure is the additive pair (availability + share). Script: `03_efftax_on_its_own_terms.py`.
