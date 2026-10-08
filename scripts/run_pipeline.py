#!/usr/bin/env python
"""Run the whole IPL pipeline end to end.

    python scripts/run_pipeline.py                # all stages
    python scripts/run_pipeline.py --skip-plots   # tables only
    python scripts/run_pipeline.py --input path/to/matches.csv

Stages:  ingest -> clean -> validate -> features -> analyse -> visualise
"""
import argparse
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ipl import analysis, clean, config, features, ingest, validate, visualize  # noqa: E402

log = logging.getLogger("pipeline")


def stage(name):
    """Tiny helper to time and log each stage."""
    class _Ctx:
        def __enter__(self):
            log.info(">>> %s", name)
            self.t = time.perf_counter()
        def __exit__(self, *exc):
            if exc[0] is None:
                log.info("<<< %s done (%.2fs)", name, time.perf_counter() - self.t)
    return _Ctx()


def save_table(df, name, index=False):
    config.TABLE_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(config.TABLE_DIR / f"{name}.csv", index=index)


def main(input_path: Path, skip_plots: bool) -> None:
    for d in (config.INTERIM_DIR, config.PROCESSED_DIR, config.TABLE_DIR, config.FIG_DIR):
        d.mkdir(parents=True, exist_ok=True)

    with stage("1. ingest"):
        raw = ingest.load_raw(input_path)

    with stage("2. clean"):
        clean_df = clean.clean_matches(raw)
        clean_df.to_csv(config.CLEAN_MATCHES, index=False)

    with stage("3. validate"):
        validate.validate(clean_df, config.REPORT_DIR / "data_quality_report.json")

    with stage("4. features"):
        matches = features.add_match_features(clean_df)
        team_matches = features.build_team_matches(matches)
        matches.to_csv(config.FEATURE_MATCHES, index=False)
        team_matches.to_csv(config.TEAM_MATCHES, index=False)

    with stage("5. analyse"):
        team_df = analysis.team_summary(team_matches)
        season_df = analysis.season_summary(matches)
        toss = analysis.toss_impact(matches)
        bat_chase = analysis.batting_first_vs_chasing(matches)
        venue_df = analysis.venue_summary(matches)
        h2h = analysis.head_to_head(team_matches)
        pom = analysis.player_of_match_leaders(matches)
        season_wins = analysis.team_season_wins(team_matches)

        save_table(team_df, "team_summary")
        save_table(season_df, "season_summary")
        save_table(toss["overall"], "toss_overall")
        save_table(toss["by_decision"], "toss_by_decision")
        save_table(toss["by_season"], "toss_by_season")
        save_table(bat_chase, "bat_first_vs_chase")
        save_table(venue_df, "venue_summary")
        save_table(h2h, "head_to_head", index=True)
        save_table(pom, "player_of_match_leaders")
        save_table(analysis.biggest_wins(matches), "biggest_wins")
        save_table(season_wins, "team_season_wins", index=True)

    if not skip_plots:
        with stage("6. visualise"):
            visualize.plot_matches_per_season(season_df)
            visualize.plot_team_wins(team_df)
            visualize.plot_toss_impact(toss)
            visualize.plot_bat_first_vs_chase(bat_chase)
            visualize.plot_head_to_head(h2h)
            visualize.plot_player_of_match(pom)
            visualize.plot_venues(venue_df)
            visualize.plot_season_wins_heatmap(season_wins)

    log.info("Pipeline finished. Tables -> %s | Figures -> %s", config.TABLE_DIR, config.FIG_DIR)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", type=Path, default=config.RAW_MATCHES)
    ap.add_argument("--skip-plots", action="store_true")
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-7s | %(message)s",
                        datefmt="%H:%M:%S")
    main(args.input, args.skip_plots)
