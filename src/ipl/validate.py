"""Stage 3 - Validate: data-quality gate between cleaning and analysis.

Each check returns (name, passed, detail). Critical failures stop the
pipeline; warnings are only written to the quality report.
"""
import json
import logging
from pathlib import Path

import pandas as pd

from ipl import config

log = logging.getLogger(__name__)


def run_checks(df: pd.DataFrame) -> list[dict]:
    decided = df[~df["is_no_result"]]
    teams = set(df["team1"]) | set(df["team2"])

    checks = [
        ("unique_match_id", df["id"].is_unique, "critical", ""),
        ("no_nulls_in_core_columns",
         not df[["season", "date", "team1", "team2", "toss_winner",
                 "toss_decision", "winner", "venue", "city"]].isna().any().any(),
         "critical", ""),
        ("team1_differs_from_team2", bool((df["team1"] != df["team2"]).all()),
         "critical", ""),
        ("toss_winner_is_a_participant",
         bool(((df["toss_winner"] == df["team1"]) | (df["toss_winner"] == df["team2"])).all()),
         "critical", ""),
        ("winner_is_a_participant",
         bool(((decided["winner"] == decided["team1"]) | (decided["winner"] == decided["team2"])).all()),
         "critical", ""),
        ("toss_decision_valid", bool(df["toss_decision"].isin(["bat", "field"]).all()),
         "critical", ""),
        ("no_negative_margins",
         bool(((df["win_by_runs"] >= 0) & (df["win_by_wickets"] >= 0)).all()),
         "critical", ""),
        ("one_margin_type_per_normal_match",
         bool((((decided["win_by_runs"] > 0) ^ (decided["win_by_wickets"] > 0))
               | decided["is_tie"]).all()),
         "warning", "super-over / D/L edge cases can break this"),
        ("team_count_reasonable", len(teams) <= 15, "warning", f"{len(teams)} teams"),
    ]
    return [{"check": n, "passed": bool(p), "severity": s, "detail": d}
            for n, p, s, d in checks]


def validate(df: pd.DataFrame, report_path: Path | None = None) -> list[dict]:
    results = run_checks(df)
    failed_critical = [r for r in results if not r["passed"] and r["severity"] == "critical"]
    for r in results:
        level = logging.INFO if r["passed"] else logging.WARNING
        log.log(level, "[%s] %s", "PASS" if r["passed"] else "FAIL", r["check"])

    if report_path:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(results, indent=2))

    if failed_critical:
        raise ValueError(f"Critical data-quality failures: "
                         f"{[r['check'] for r in failed_critical]}")
    return results
