"""Central configuration: paths, constants and cleaning maps.

Everything that is a "decision" (which names to merge, what counts as a
close match) lives here, so the rest of the code has no magic values.
"""
from pathlib import Path

# ----------------------------------------------------------------- paths
ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
INTERIM_DIR = ROOT / "data" / "interim"
PROCESSED_DIR = ROOT / "data" / "processed"
FIG_DIR = ROOT / "reports" / "figures"
TABLE_DIR = ROOT / "reports" / "tables"
REPORT_DIR = ROOT / "reports"

RAW_MATCHES = RAW_DIR / "matches.csv"
CLEAN_MATCHES = INTERIM_DIR / "matches_clean.csv"
FEATURE_MATCHES = PROCESSED_DIR / "matches_features.csv"
TEAM_MATCHES = PROCESSED_DIR / "team_matches.csv"

# --------------------------------------------------------------- schema
REQUIRED_COLUMNS = [
    "id", "Season", "city", "date", "team1", "team2", "toss_winner",
    "toss_decision", "result", "dl_applied", "winner", "win_by_runs",
    "win_by_wickets", "player_of_match", "venue", "umpire1", "umpire2",
]
DATE_FORMAT = "%d-%m-%Y"
NO_RESULT_LABEL = "No Result"

# ------------------------------------------------------------- cleaning
# Same franchise, different spelling / rebranding.
# NOTE: Deccan Chargers and Sunrisers Hyderabad are different franchises
# (legally), so they are intentionally NOT merged.
TEAM_NAME_MAP = {
    "Rising Pune Supergiants": "Rising Pune Supergiant",
    "Delhi Daredevils": "Delhi Capitals",
}

VENUE_NAME_MAP = {
    "Feroz Shah Kotla Ground": "Feroz Shah Kotla",
    "M. Chinnaswamy Stadium": "M Chinnaswamy Stadium",
    "M. A. Chidambaram Stadium": "MA Chidambaram Stadium, Chepauk",
    "IS Bindra Stadium": "Punjab Cricket Association Stadium, Mohali",
    "Punjab Cricket Association IS Bindra Stadium, Mohali":
        "Punjab Cricket Association Stadium, Mohali",
    "Rajiv Gandhi Intl. Cricket Stadium":
        "Rajiv Gandhi International Stadium, Uppal",
    "ACA-VDCA Stadium":
        "Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium",
}

# Venues whose `city` is missing in the raw file.
VENUE_CITY_FILL = {
    "Dubai International Cricket Stadium": "Dubai",
}

COLUMNS_TO_DROP = ["umpire3"]  # ~84% null

# ------------------------------------------------------------- features
CLOSE_RUNS_MARGIN = 10      # won by <= 10 runs
CLOSE_WICKETS_MARGIN = 2    # won by <= 2 wickets
MIN_VENUE_MATCHES = 10      # ignore tiny-sample venues in venue ranking
