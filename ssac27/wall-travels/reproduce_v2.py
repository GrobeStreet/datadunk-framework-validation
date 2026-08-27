#!/usr/bin/env python3
"""SSAC27 Wall Travels v2 robustness harness.

This script is intentionally fail-closed. It reads NBA.com LeagueDashPtDefend
`Less Than 6Ft` CSV exports in Totals mode (preferred) or PerGame mode
(backward-compatible), runs a fixed threshold grid, raw and rank persistence,
mover/stayer bootstrap inference, and OLS portability interactions with role
controls. It never selects a threshold based on significance.

Expected filenames under --data-dir:
  2023-24.csv
  2024-25.csv
  2025-26.csv

Use --fetch to request fresh NBA.com Totals-mode exports. Cloud hosts may be
blocked; running locally is acceptable, but source hashes must be preserved.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
import statistics
import time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

SEASONS = ("2023-24", "2024-25", "2025-26")
THRESHOLDS = (50.0, 80.0, 100.0, 150.0)
ID = "CLOSE_DEF_PERSON_ID"
TEAM = "PLAYER_LAST_TEAM_ABBREVIATION"
NAME = "PLAYER_NAME"
POS = "PLAYER_POSITION"
AGE = "AGE"
GP = "GP"
FGA = "FGA_LT_06"
PM = "PLUSMINUS"


def fetch_season(season: str, out: Path) -> None:
    params = {
        "Conference": "", "DateFrom": "", "DateTo": "",
        "DefenseCategory": "Less Than 6Ft", "Division": "", "GameSegment": "",
        "LastNGames": 0, "LeagueID": "00", "Location": "", "Month": 0,
        "OpponentTeamID": 0, "Outcome": "", "PORound": 0, "PaceAdjust": "N",
        "PerMode": "Totals", "Period": 0, "PlayerExperience": "",
        "PlayerPosition": "", "PlusMinus": "N", "Rank": "N", "Season": season,
        "SeasonSegment": "", "SeasonType": "Regular Season", "StarterBench": "",
        "TeamID": 0, "VsConference": "", "VsDivision": "", "Weight": 0,
    }
    url = "https://stats.nba.com/stats/leaguedashptdefend?" + urlencode(params)
    req = Request(url, headers={
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.nba.com/",
        "Origin": "https://www.nba.com",
    })
    with urlopen(req, timeout=60) as r:
        payload = json.load(r)
    result = payload["resultSets"][0]
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(result["headers"])
        w.writerows(result["rowSet"])


def as_float(x, default=float("nan")):
    try:
        return float(x)
    except (TypeError, ValueError):
        return default


def read(path: Path):
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    required = {ID, TEAM, GP, FGA, PM}
    missing = required - set(rows[0].keys() if rows else [])
    if missing:
        raise ValueError(f"{path}: missing required columns {sorted(missing)}")

    # Totals mode returns integer-scale FGA; PerGame mode returns a small rate.
    # Infer mode conservatively from whether FGA is usually <= 20 despite long GP.
    fgas = [as_float(r.get(FGA)) for r in rows if math.isfinite(as_float(r.get(FGA)))]
    per_game = statistics.median(fgas) < 20 if fgas else False

    for r in rows:
        r[ID] = int(float(r[ID]))
        r[GP] = as_float(r.get(GP))
        r[FGA] = as_float(r.get(FGA))
        r[PM] = as_float(r.get(PM))
        r[AGE] = as_float(r.get(AGE))
        r["TOTAL_RIM_FGA"] = r[FGA] * r[GP] if per_game else r[FGA]
        r["SOURCE_MODE"] = "PerGame" if per_game else "Totals"
    return rows


def sha(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pearson(xs, ys):
    if len(xs) < 3:
        return float("nan")
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = math.sqrt(sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys))
    return num / den if den else float("nan")


def average_ranks(vals):
    order = sorted(range(len(vals)), key=lambda i: vals[i])
    ranks = [0.0] * len(vals)
    j = 0
    while j < len(order):
        k = j + 1
        while k < len(order) and vals[order[k]] == vals[order[j]]:
            k += 1
        avg = (j + 1 + k) / 2.0
        for q in range(j, k):
            ranks[order[q]] = avg
        j = k
    return ranks


def spearman(xs, ys):
    return pearson(average_ranks(xs), average_ranks(ys))


def paired(a, b, threshold):
    A = {r[ID]: r for r in a if r["TOTAL_RIM_FGA"] >= threshold and math.isfinite(r[PM])}
    B = {r[ID]: r for r in b if r["TOTAL_RIM_FGA"] >= threshold and math.isfinite(r[PM])}
    ids = sorted(A.keys() & B.keys())
    return ids, A, B


def corr_summary(A, B, ids):
    xs = [A[i][PM] for i in ids]
    ys = [B[i][PM] for i in ids]
    return {"n": len(ids), "pearson_r": pearson(xs, ys), "spearman_rho": spearman(xs, ys)}


def bootstrap_corr(A, B, ids, n=10000, seed=20260826, rank=False):
    if len(ids) < 3:
        return [float("nan"), float("nan")]
    rng = random.Random(seed)
    vals = []
    for _ in range(n):
        q = [ids[rng.randrange(len(ids))] for _ in ids]
        xs, ys = [A[i][PM] for i in q], [B[i][PM] for i in q]
        vals.append(spearman(xs, ys) if rank else pearson(xs, ys))
    vals = sorted(v for v in vals if math.isfinite(v))
    if not vals:
        return [float("nan"), float("nan")]
    return [vals[int(.025 * len(vals))], vals[max(0, int(.975 * len(vals)) - 1)]]


def bootstrap_diff(A, B, movers, stayers, n=10000, seed=20260827, rank=False):
    if min(len(movers), len(stayers)) < 3:
        return [float("nan"), float("nan")]
    rng = random.Random(seed)
    vals = []
    for _ in range(n):
        qm = [movers[rng.randrange(len(movers))] for _ in movers]
        qs = [stayers[rng.randrange(len(stayers))] for _ in stayers]
        fx = spearman if rank else pearson
        rm = fx([A[i][PM] for i in qm], [B[i][PM] for i in qm])
        rs = fx([A[i][PM] for i in qs], [B[i][PM] for i in qs])
        if math.isfinite(rm) and math.isfinite(rs):
            vals.append(rm - rs)
    vals.sort()
    return [vals[int(.025 * len(vals))], vals[max(0, int(.975 * len(vals)) - 1)]] if vals else [float("nan"), float("nan")]


def mat_inv(A):
    n = len(A)
    M = [list(map(float, A[i])) + [1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
    for c in range(n):
        pivot = max(range(c, n), key=lambda r: abs(M[r][c]))
        if abs(M[pivot][c]) < 1e-12:
            raise ValueError("singular design")
        M[c], M[pivot] = M[pivot], M[c]
        z = M[c][c]
        M[c] = [v / z for v in M[c]]
        for r in range(n):
            if r == c:
                continue
            z = M[r][c]
            M[r] = [M[r][j] - z * M[c][j] for j in range(2 * n)]
    return [row[n:] for row in M]


def ols(X, y, weights=None):
    p = len(X[0])
    XtWX = [[0.0] * p for _ in range(p)]
    XtWy = [0.0] * p
    for idx, row in enumerate(X):
        w = 1.0 if weights is None else weights[idx]
        for j in range(p):
            XtWy[j] += w * row[j] * y[idx]
            for k in range(p):
                XtWX[j][k] += w * row[j] * row[k]
    inv = mat_inv(XtWX)
    beta = [sum(inv[j][k] * XtWy[k] for k in range(p)) for j in range(p)]

    # HC1 sandwich robust SE; weighted residual contribution uses w*x*e.
    meat = [[0.0] * p for _ in range(p)]
    residuals = []
    for idx, row in enumerate(X):
        e = y[idx] - sum(row[j] * beta[j] for j in range(p))
        residuals.append(e)
        w = 1.0 if weights is None else weights[idx]
        for j in range(p):
            for k in range(p):
                meat[j][k] += (w * row[j] * e) * (w * row[k] * e)
    cov = [[sum(inv[j][a] * meat[a][b] * inv[b][k] for a in range(p) for b in range(p)) for k in range(p)] for j in range(p)]
    n = len(X)
    if n > p:
        scale = n / (n - p)
        cov = [[v * scale for v in row] for row in cov]
    se = [math.sqrt(max(0.0, cov[j][j])) for j in range(p)]
    return beta, se


def z_ci(b, se):
    return [b - 1.96 * se, b + 1.96 * se]


def position_bucket(pos):
    p = (pos or "").upper()
    if "C" in p:
        return "C"
    if "F" in p:
        return "F"
    if "G" in p:
        return "G"
    return "UNK"


def interaction_regression(A, B, ids, weighted=False):
    # Baseline: y ~ 1 + x + mover + x*mover + age + F + G
    # Center x/age/exposure for numerical readability.
    rows = []
    for i in ids:
        age = A[i].get(AGE, float("nan"))
        rows.append({
            "id": i,
            "x": A[i][PM],
            "y": B[i][PM],
            "m": 1.0 if A[i][TEAM] != B[i][TEAM] else 0.0,
            "age": age,
            "pos": position_bucket(A[i].get(POS, "")),
            "exp": min(A[i]["TOTAL_RIM_FGA"], B[i]["TOTAL_RIM_FGA"]),
        })
    ages = [r["age"] for r in rows if math.isfinite(r["age"])]
    age_mean = statistics.fmean(ages) if ages else 0.0
    x_mean = statistics.fmean(r["x"] for r in rows)
    X, y, W = [], [], []
    for r in rows:
        age = r["age"] if math.isfinite(r["age"]) else age_mean
        x = r["x"] - x_mean
        X.append([1.0, x, r["m"], x * r["m"], age - age_mean,
                  1.0 if r["pos"] == "F" else 0.0,
                  1.0 if r["pos"] == "G" else 0.0])
        y.append(r["y"])
        W.append(math.sqrt(max(r["exp"], 1.0)))
    names = ["intercept", "prior_suppression", "mover", "prior_x_mover", "age", "position_F", "position_G"]
    beta, se = ols(X, y, W if weighted else None)
    return {names[j]: {"coef": beta[j], "robust_se": se[j], "ci95": z_ci(beta[j], se[j])} for j in range(len(names))}


def threshold_analysis(a, b, threshold, seed_offset=0):
    ids, A, B = paired(a, b, threshold)
    movers = [i for i in ids if A[i][TEAM] != B[i][TEAM]]
    stayers = [i for i in ids if A[i][TEAM] == B[i][TEAM]]
    out = {
        "all": corr_summary(A, B, ids),
        "movers": corr_summary(A, B, movers),
        "stayers": corr_summary(A, B, stayers),
        "pearson_bootstrap95": {
            "movers": bootstrap_corr(A, B, movers, seed=20260826 + seed_offset),
            "stayers": bootstrap_corr(A, B, stayers, seed=20260828 + seed_offset),
            "mover_minus_stayer": bootstrap_diff(A, B, movers, stayers, seed=20260827 + seed_offset),
        },
        "spearman_bootstrap95": {
            "movers": bootstrap_corr(A, B, movers, seed=20260829 + seed_offset, rank=True),
            "stayers": bootstrap_corr(A, B, stayers, seed=20260830 + seed_offset, rank=True),
            "mover_minus_stayer": bootstrap_diff(A, B, movers, stayers, seed=20260831 + seed_offset, rank=True),
        },
    }
    try:
        out["interaction_ols_hc1"] = interaction_regression(A, B, ids, weighted=False)
        out["interaction_wls_hc1"] = interaction_regression(A, B, ids, weighted=True)
    except ValueError as e:
        out["regression_error"] = str(e)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", type=Path, default=Path("data_v2"))
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--out", type=Path, default=Path("results/receipt_v2.json"))
    args = ap.parse_args()

    paths = {s: args.data_dir / f"{s}.csv" for s in SEASONS}
    if args.fetch:
        for season, path in paths.items():
            fetch_season(season, path)
            time.sleep(2)
    missing = [str(p) for p in paths.values() if not p.exists()]
    if missing:
        raise SystemExit("Missing source files: " + ", ".join(missing) + ". Use --fetch locally or provide frozen CSVs.")

    D = {s: read(p) for s, p in paths.items()}
    result = {
        "status": "V2_ROBUSTNESS_RUN",
        "source_csv_sha256": {s: sha(p) for s, p in paths.items()},
        "source_mode": {s: D[s][0]["SOURCE_MODE"] if D[s] else None for s in SEASONS},
        "threshold_grid": list(THRESHOLDS),
        "adjacent_seasons": {},
        "claim_boundary": "Portability association, not causal identification. No threshold selected post hoc.",
    }
    pairs = (("2023-24", "2024-25"), ("2024-25", "2025-26"))
    for pair_idx, (s1, s2) in enumerate(pairs):
        key = f"{s1}_to_{s2}"
        result["adjacent_seasons"][key] = {
            str(int(t)): threshold_analysis(D[s1], D[s2], t, seed_offset=pair_idx * 100 + int(t))
            for t in THRESHOLDS
        }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=True))


if __name__ == "__main__":
    main()
