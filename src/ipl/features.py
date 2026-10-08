"""Stage 4 - Feature engineering: derive analysis-ready columns and tables."""
import numpy as np
import pandas as pd

from ipl import config


def add_match_features(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()

    # who batted first / chased
    other_team = np.where(d["toss_winner"] == d["team1"], d["team2"], d["team1"])
    d["batting_first"] = np.where(d["toss_decision"] == "bat", d["toss_winner"], other_team)
    d["chasing_team"] = np.where(d["toss_decision"] == "bat", other_team, d["toss_winner"])

    # outcome flags (only meaningful when is_no_result is False)
    d["toss_winner_won"] = d["toss_winner"] == d["winner"]
    d["batting_first_won"] = d["batting_first"] == d["winner"]

    # how the match was won + margin
    d["win_type"] = np.select(
        [d["is_no_result"], d["is_tie"], d["win_by_runs"] > 0, d["win_by_wickets"] > 0],
        ["no_result", "super_over", "runs", "wickets"],
        default="unknown",
    )
    d["margin"] = np.where(d["win_type"] == "runs", d["win_by_runs"],
                  np.where(d["win_type"] == "wickets", d["win_by_wickets"], 0))
    d["is_close_match"] = (
        ((d["win_type"] == "runs") & (d["win_by_runs"] <= config.CLOSE_RUNS_MARGIN))
        | ((d["win_type"] == "wickets") & (d["win_by_wickets"] <= config.CLOSE_WICKETS_MARGIN))
        | (d["win_type"] == "super_over")
    )

    # calendar features
    d["month"] = d["date"].dt.month
    d["weekday"] = d["date"].dt.day_name()
    # the final = last match of each season (data is sorted by date, id)
    d = d.sort_values(["date", "id"])
    d["is_final"] = d.groupby("season").cumcount(ascending=False).eq(0)
    d = d.sort_index()
    return d


def build_team_matches(d: pd.DataFrame) -> pd.DataFrame:
    """Long format: one row per team per match (the base for all team stats)."""
    side_a = d.assign(team=d["team1"], opponent=d["team2"])
    side_b = d.assign(team=d["team2"], opponent=d["team1"])
    tm = pd.concat([side_a, side_b], ignore_index=True)

    tm["won"] = tm["team"] == tm["winner"]
    tm["won_toss"] = tm["team"] == tm["toss_winner"]
    tm["batted_first"] = tm["team"] == tm["batting_first"]

    cols = ["id", "season", "date", "team", "opponent", "venue", "city", "won",
            "won_toss", "batted_first", "is_no_result", "is_final", "win_type", "margin"]
    return tm[cols].sort_values(["date", "id", "team"]).reset_index(drop=True)
