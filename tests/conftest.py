import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


@pytest.fixture
def raw_df():
    """Tiny hand-made dataset that contains every quirk of the real one."""
    return pd.DataFrame({
        "id": [1, 2, 3],
        "Season": ["IPL-2014", "IPL-2017", "IPL-2017"],
        "city": [None, "Pune", "Pune"],
        "date": ["10-04-2014", "05-04-2017", "07-04-2017"],
        "team1": ["Delhi Daredevils", "Rising Pune Supergiants", "Mumbai Indians"],
        "team2": ["Mumbai Indians", "Mumbai Indians", "Kolkata Knight Riders"],
        "toss_winner": ["Mumbai Indians", "Mumbai Indians", "Kolkata Knight Riders"],
        "toss_decision": ["field", "bat", "field"],
        "result": ["normal", "normal", "no result"],
        "dl_applied": [0, 0, 0],
        "winner": ["Mumbai Indians", "Rising Pune Supergiants", None],
        "win_by_runs": [0, 20, 0],
        "win_by_wickets": [5, 0, 0],
        "player_of_match": ["A", "B", None],
        "venue": ["Dubai International Cricket Stadium", "M. Chinnaswamy Stadium",
                  "Feroz Shah Kotla Ground"],
        "umpire1": ["x", "y", None],
        "umpire2": ["x", "y", "z"],
        "umpire3": [None, None, None],
    })
