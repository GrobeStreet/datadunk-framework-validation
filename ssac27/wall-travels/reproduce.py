#!/usr/bin/env python3
"""SSAC27 Wall Travels: reproduce the three-season rim-suppression results.

By default reads data/{season}.csv. Use --fetch to regenerate those CSVs from
NBA.com's LeagueDashPtDefend endpoint (cloud hosts may be blocked by NBA.com).
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
ID = "CLOSE_DEF_PERSON_ID"
TEAM = "PLAYER_LAST_TEAM_ABBREVIATION"
GP = "GP"
FGA = "FGA_LT_06"
PM = "PLUSMINUS"
SIGNAL_MIN = 100.0
PERSIST_MIN = 80.0


def fetch_season(season: str, out: Path) -> None:
    params = {
        "Conference": "", "DateFrom": "", "DateTo": "",
        "DefenseCategory": "Less Than 6Ft", "Division": "", "GameSegment": "",
        "LastNGames": 0, "LeagueID": "00", "Location": "", "Month": 0,
        "OpponentTeamID": 0, "Outcome": "", "PORound": 0, "PaceAdjust": "N",
        "PerMode": "PerGame", "Period": 0, "PlayerExperience": "",
        "PlayerPosition": "", "PlusMinus": "N", "Rank": "N", "Season": season,
        "SeasonSegment": "", "SeasonType": "Regular Season", "StarterBench": "",
        "TeamID": 0, "VsConference": "", "VsDivision": "", "Weight": 0,
    }
    url = "https://stats.nba.com/stats/leaguedashptdefend?" + urlencode(params)
    req = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://www.nba.com/",
            "Origin": "https://www.nba.com",
        },
    )
    with urlopen(req, timeout=60) as r:
        payload = json.load(r)
    result = payload["resultSets"][0]
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(result["headers"])
        w.writerows(result["rowSet"])


def read(path: Path):
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r[ID] = int(float(r[ID]))
        r[GP] = float(r[GP])
        r[FGA] = float(r[FGA])
        r[PM] = float(r[PM])
        r["TOTAL_RIM_FGA"] = r[GP] * r[FGA]
    return rows


def pearson(xs, ys):
    mx = statistics.fmean(xs)
    my = statistics.fmean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = math.sqrt(
        sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys)
    )
    return num / den


def signal(rows):
    z = [r for r in rows if r["TOTAL_RIM_FGA"] >= SIGNAL_MIN]
    vals = [r[PM] for r in z]
    observed_var = statistics.variance(vals)
    noise_bound = statistics.fmean(0.25 / r["TOTAL_RIM_FGA"] for r in z)
    true_var_floor = max(0.0, observed_var - noise_bound)
    suppression = sorted((max(0.0, -v) for v in vals), reverse=True)
    return {
        "n": len(z),
        "observed_sd": math.sqrt(observed_var),
        "true_signal_sd_floor": math.sqrt(true_var_floor),
        "reliability_floor": true_var_floor / observed_var,
        "top3_mass": sum(suppression[:3]) / sum(suppression),
    }


def pair(a, b):
    A = {r[ID]: r for r in a if r["TOTAL_RIM_FGA"] >= PERSIST_MIN}
    B = {r[ID]: r for r in b if r["TOTAL_RIM_FGA"] >= PERSIST_MIN}
    ids = sorted(A.keys() & B.keys())
    return ids, A, B, pearson([A[i][PM] for i in ids], [B[i][PM] for i in ids])


def bootstrap_corr(A, B, ids, n=10000, seed=20260826):
    rng = random.Random(seed)
    vals = []
    N = len(ids)
    for _ in range(n):
        q = [ids[rng.randrange(N)] for _ in range(N)]
        vals.append(pearson([A[i][PM] for i in q], [B[i][PM] for i in q]))
    vals.sort()
    return [vals[int(0.025 * n)], vals[int(0.975 * n) - 1]]


def bootstrap_corr_diff(A, B, movers, stayers, n=10000, seed=20260827):
    rng = random.Random(seed)
    vals = []
    for _ in range(n):
        qm = [movers[rng.randrange(len(movers))] for _ in movers]
        qs = [stayers[rng.randrange(len(stayers))] for _ in stayers]
        rm = pearson([A[i][PM] for i in qm], [B[i][PM] for i in qm])
        rs = pearson([A[i][PM] for i in qs], [B[i][PM] for i in qs])
        vals.append(rm - rs)
    vals.sort()
    return [vals[int(0.025 * n)], vals[int(0.975 * n) - 1]]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", type=Path, default=Path("data"))
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--out", type=Path, default=Path("results/receipt.json"))
    args = ap.parse_args()

    paths = {s: args.data_dir / f"{s}.csv" for s in SEASONS}
    if args.fetch:
        for season, path in paths.items():
            fetch_season(season, path)
            time.sleep(2)

    D = {s: read(path) for s, path in paths.items()}
    p12 = pair(D["2023-24"], D["2024-25"])
    p23 = pair(D["2024-25"], D["2025-26"])
    p13 = pair(D["2023-24"], D["2025-26"])

    ids, A, B, _ = p23
    movers = [i for i in ids if A[i][TEAM] != B[i][TEAM]]
    stayers = [i for i in ids if A[i][TEAM] == B[i][TEAM]]

    result = {
        "status": "REPRODUCED",
        "thresholds": {
            "signal_total_rim_fga": 100,
            "persistence_total_rim_fga_each_season": 80,
        },
        "source_csv_sha256": {s: sha(path) for s, path in paths.items()},
        "signal": {s: signal(D[s]) for s in SEASONS},
        "persistence": {
            "2023-24_to_2024-25": {"n": len(p12[0]), "r": p12[3]},
            "2024-25_to_2025-26": {"n": len(p23[0]), "r": p23[3]},
            "2023-24_to_2025-26": {"n": len(p13[0]), "r": p13[3]},
        },
        "movement_2024-25_to_2025-26": {
            "movers": {
                "n": len(movers),
                "r": pearson([A[i][PM] for i in movers], [B[i][PM] for i in movers]),
                "bootstrap95": bootstrap_corr(A, B, movers),
            },
            "stayers": {
                "n": len(stayers),
                "r": pearson([A[i][PM] for i in stayers], [B[i][PM] for i in stayers]),
                "bootstrap95": bootstrap_corr(A, B, stayers, seed=20260828),
            },
            "mover_minus_stayer_r_bootstrap95": bootstrap_corr_diff(A, B, movers, stayers),
        },
        "claim_boundary": (
            "Associational player persistence; movement is not randomized causal identification."
        ),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
