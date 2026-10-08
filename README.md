# IPL Matches Analysis (2008-2019)

A small, reproducible data-analysis project built on `matches.csv`
(756 matches, 12 seasons). Raw data goes in, cleaned data, result tables
and charts come out - with one command.

## Quick start
```bash
pip install -r requirements.txt
python scripts/run_pipeline.py        # runs all stages
python -m pytest -q                   # runs the tests
```

## Pipeline
```
data/raw/matches.csv
   |  1 ingest    src/ipl/ingest.py     load + schema check
   |  2 clean     src/ipl/clean.py      types, team/venue names, missing values
   |  3 validate  src/ipl/validate.py   data-quality gate (stops on critical failure)
   |  4 features  src/ipl/features.py   batting_first, win_type, margin, close match, final...
   |  5 analyse   src/ipl/analysis.py   result tables
   |  6 visualise src/ipl/visualize.py  PNG charts
   v
data/interim/ -> data/processed/ -> reports/tables + reports/figures
```
Every stage is a pure function (DataFrame in, DataFrame out). Only
`scripts/run_pipeline.py` touches the disk, so each piece is easy to test.

## Data issues handled
| Issue | Fix |
|---|---|
| `Season` is text like `IPL-2017` | converted to integer 2017 |
| `date` is dd-mm-yyyy text | parsed to datetime |
| Delhi Daredevils -> Delhi Capitals; Rising Pune Supergiant(s) | merged (see `config.py`) |
| Same stadium spelled several ways (Chinnaswamy, Chepauk, Mohali, Hyderabad...) | `VENUE_NAME_MAP` |
| `city` missing for 7 Dubai matches (2014) | filled from venue |
| 4 "no result" matches have no winner / player of match | flagged `is_no_result`, excluded from win stats |
| `umpire3` ~84% empty | dropped |

Decision to review: Deccan Chargers and Sunrisers Hyderabad are kept
separate (different franchises). Merge them in `config.TEAM_NAME_MAP`
if you prefer.

## Outputs
* `reports/tables/*.csv` - team, season, toss, venue, head-to-head, player tables
* `reports/figures/*.png` - 8 charts
* `reports/data_quality_report.json` - result of each validation check
* `data/processed/matches_features.csv` and `team_matches.csv` - analysis-ready data

## Notes on the data
* The final of each season is taken as the last match by date/id.
* The dataset has no ball-by-ball or score data, so first-innings totals
  and player batting/bowling stats are not possible (see ideas below).

## Ideas to take it further
1. Add `deliveries.csv` (ball-by-ball) -> batsman/bowler stats, powerplay & death-over analysis.
2. Predict match winner (logistic regression / random forest) with rolling team form.
3. Elo rating for teams across seasons.
4. Streamlit dashboard with season / team filters.
5. Statistical tests: is the toss advantage real? (chi-square / binomial test)
6. Update with the 2020+ seasons and add GitHub Actions to run tests on push.
