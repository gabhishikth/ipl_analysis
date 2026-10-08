"""Stage 2 - Clean: fix types, standardise names, handle missing values.

Pure function: raw DataFrame in -> clean DataFrame out (no file I/O).
"""
import logging

import pandas as pd

from ipl import config

log = logging.getLogger(__name__)

TEAM_COLS = ["team1", "team2", "toss_winner", "winner"]


def clean_matches(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.copy()

    # 1. consistent snake_case column names
    df.columns = [c.strip().lower() for c in df.columns]

    # 2. drop duplicate matches and mostly-empty columns
    before = len(df)
    df = df.drop_duplicates(subset="id")
    if len(df) != before:
        log.warning("Dropped %d duplicate match ids", before - len(df))
    df = df.drop(columns=[c for c in config.COLUMNS_TO_DROP if c in df.columns])

    # 3. trim whitespace in all text columns
    for col in df.select_dtypes(include=["object", "string"]).columns:
        df[col] = df[col].str.strip()

    # 4. types: "IPL-2017" -> 2017, "05-04-2017" -> datetime
    df["season"] = df["season"].astype(str).str.extract(r"(\d{4})")[0].astype(int)
    df["date"] = pd.to_datetime(df["date"], format=config.DATE_FORMAT)

    # 5. standardise franchise + venue names
    for col in TEAM_COLS:
        df[col] = df[col].replace(config.TEAM_NAME_MAP)
    df["venue"] = df["venue"].replace(config.VENUE_NAME_MAP)

    # 6. missing city (Dubai matches in 2014) -> fill from venue
    df["city"] = df["city"].fillna(df["venue"].map(config.VENUE_CITY_FILL))

    # 7. no-result matches have no winner / player of match
    df["is_no_result"] = df["result"].eq("no result")
    df["winner"] = df["winner"].fillna(config.NO_RESULT_LABEL)
    df["player_of_match"] = df["player_of_match"].fillna("Not Awarded")

    # 8. boolean flags + stable ordering
    df["dl_applied"] = df["dl_applied"].astype(bool)
    df["is_tie"] = df["result"].eq("tie")
    df = df.sort_values(["date", "id"]).reset_index(drop=True)

    log.info("Cleaned data: %d matches, %d teams", len(df), df["team1"].nunique())
    return df
