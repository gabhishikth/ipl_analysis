"""Stage 5 - Analysis: pure functions that turn tidy tables into result tables."""
import pandas as pd

from ipl import config


def _decided(tm: pd.DataFrame) -> pd.DataFrame:
    return tm[~tm["is_no_result"]]


def team_summary(tm: pd.DataFrame) -> pd.DataFrame:
    d = _decided(tm)
    out = d.groupby("team").agg(matches=("won", "size"), wins=("won", "sum"),
                                seasons=("season", "nunique"))
    out["win_pct"] = (out["wins"] / out["matches"] * 100).round(1)
    titles = tm[tm["is_final"] & tm["won"]].groupby("team").size()
    out["titles"] = titles.reindex(out.index).fillna(0).astype(int)
    return out.sort_values("wins", ascending=False).reset_index()


def season_summary(m: pd.DataFrame) -> pd.DataFrame:
    g = m.groupby("season")
    out = g.agg(matches=("id", "size"), teams=("team1", "nunique"),
                no_results=("is_no_result", "sum"), close_matches=("is_close_match", "sum"))
    final = m[m["is_final"]].set_index("season")
    out["champion"] = final["winner"]
    out["runner_up"] = final.apply(
        lambda r: r["team2"] if r["winner"] == r["team1"] else r["team1"], axis=1)
    out["top_player_of_match"] = (
        m[m["player_of_match"] != "Not Awarded"].groupby("season")["player_of_match"]
        .agg(lambda s: s.value_counts().idxmax()))
    return out.reset_index()


def toss_impact(m: pd.DataFrame) -> dict[str, pd.DataFrame]:
    d = m[~m["is_no_result"]]
    overall = pd.DataFrame({
        "matches": [len(d)],
        "toss_winner_won": [int(d["toss_winner_won"].sum())],
        "pct": [round(d["toss_winner_won"].mean() * 100, 1)]})
    by_decision = (d.groupby("toss_decision")
                   .agg(matches=("id", "size"), toss_winner_won_pct=("toss_winner_won", "mean"))
                   .assign(toss_winner_won_pct=lambda x: (x.toss_winner_won_pct * 100).round(1))
                   .reset_index())
    by_season = (d.groupby("season")
                 .agg(toss_winner_won_pct=("toss_winner_won", "mean"),
                      chose_field_pct=("toss_decision", lambda s: (s == "field").mean()))
                 .mul(100).round(1).reset_index())
    return {"overall": overall, "by_decision": by_decision, "by_season": by_season}


def batting_first_vs_chasing(m: pd.DataFrame) -> pd.DataFrame:
    d = m[~m["is_no_result"]]
    out = (d.groupby("season")["batting_first_won"].mean().mul(100).round(1)
           .rename("bat_first_win_pct").reset_index())
    out["chasing_win_pct"] = (100 - out["bat_first_win_pct"]).round(1)
    return out


def venue_summary(m: pd.DataFrame, min_matches: int = config.MIN_VENUE_MATCHES) -> pd.DataFrame:
    d = m[~m["is_no_result"]]
    out = (d.groupby("venue")
           .agg(matches=("id", "size"), bat_first_win_pct=("batting_first_won", "mean"),
                toss_winner_won_pct=("toss_winner_won", "mean"),
                close_match_pct=("is_close_match", "mean"))
           .query("matches >= @min_matches"))
    pct_cols = ["bat_first_win_pct", "toss_winner_won_pct", "close_match_pct"]
    out[pct_cols] = (out[pct_cols] * 100).round(1)
    return out.sort_values("matches", ascending=False).reset_index()


def head_to_head(tm: pd.DataFrame) -> pd.DataFrame:
    """Matrix: rows = team, columns = opponent, value = wins of row-team."""
    d = _decided(tm)
    return d.pivot_table(index="team", columns="opponent", values="won",
                         aggfunc="sum", fill_value=0).astype(int)


def player_of_match_leaders(m: pd.DataFrame, top: int = 10) -> pd.DataFrame:
    s = m[m["player_of_match"] != "Not Awarded"]["player_of_match"].value_counts().head(top)
    return s.rename_axis("player").reset_index(name="awards")


def biggest_wins(m: pd.DataFrame, top: int = 10) -> pd.DataFrame:
    cols = ["season", "date", "winner", "team1", "team2", "win_type", "margin", "venue"]
    runs = m[m["win_type"] == "runs"].nlargest(top, "margin")[cols]
    return runs.reset_index(drop=True)


def team_season_wins(tm: pd.DataFrame) -> pd.DataFrame:
    d = _decided(tm)
    return d.pivot_table(index="season", columns="team", values="won",
                         aggfunc="sum", fill_value=0).astype(int)
