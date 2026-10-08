import pytest

from ipl import analysis, clean, features, validate


def test_clean_standardises_names_and_types(raw_df):
    df = clean.clean_matches(raw_df)
    assert "Delhi Capitals" in set(df["team1"])
    assert "Rising Pune Supergiant" in set(df["team1"])
    assert df["season"].tolist() == [2014, 2017, 2017]
    assert str(df["date"].dtype).startswith("datetime64")
    assert "umpire3" not in df.columns
    assert "M Chinnaswamy Stadium" in set(df["venue"])


def test_clean_fills_missing_city_and_no_result(raw_df):
    df = clean.clean_matches(raw_df)
    assert df.loc[df["venue"].str.contains("Dubai"), "city"].iloc[0] == "Dubai"
    nr = df[df["is_no_result"]].iloc[0]
    assert nr["winner"] == "No Result" and nr["player_of_match"] == "Not Awarded"


def test_features_batting_first_logic(raw_df):
    m = features.add_match_features(clean.clean_matches(raw_df))
    row_field = m[m["id"] == 1].iloc[0]   # MI won toss, chose field -> DC bats first
    assert row_field["batting_first"] == "Delhi Capitals"
    assert row_field["toss_winner_won"] is True or row_field["toss_winner_won"]
    row_bat = m[m["id"] == 2].iloc[0]     # MI won toss, chose bat
    assert row_bat["batting_first"] == "Mumbai Indians"
    assert row_bat["win_type"] == "runs" and row_bat["margin"] == 20


def test_team_matches_has_two_rows_per_match(raw_df):
    m = features.add_match_features(clean.clean_matches(raw_df))
    tm = features.build_team_matches(m)
    assert len(tm) == 2 * len(m)
    assert tm.groupby("id")["won"].sum().max() == 1   # at most one winner


def test_validation_passes_on_clean_data_and_fails_on_bad(raw_df):
    df = features.add_match_features(clean.clean_matches(raw_df))
    validate.validate(df)  # should not raise
    bad = df.copy()
    bad.loc[0, "toss_winner"] = "Some Other Team"
    with pytest.raises(ValueError):
        validate.validate(bad)


def test_team_summary_win_pct(raw_df):
    m = features.add_match_features(clean.clean_matches(raw_df))
    tm = features.build_team_matches(m)
    ts = analysis.team_summary(tm).set_index("team")
    assert ts.loc["Mumbai Indians", "wins"] == 1
    assert ts.loc["Mumbai Indians", "matches"] == 2   # no-result match excluded
