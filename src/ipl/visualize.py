"""Stage 6 - Visualise: every function saves one PNG and returns its path."""
import matplotlib

matplotlib.use("Agg")  # headless-safe
import matplotlib.pyplot as plt
import seaborn as sns

from ipl import config

sns.set_theme(style="whitegrid", context="notebook")


def _save(fig, name):
    config.FIG_DIR.mkdir(parents=True, exist_ok=True)
    path = config.FIG_DIR / f"{name}.png"
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def plot_matches_per_season(season_df):
    fig, ax = plt.subplots(figsize=(9, 4.5))
    sns.barplot(data=season_df, x="season", y="matches", color="#4C78A8", ax=ax)
    ax.set(title="Matches played per season", xlabel="Season", ylabel="Matches")
    return _save(fig, "01_matches_per_season")


def plot_team_wins(team_df):
    fig, ax = plt.subplots(figsize=(9, 6))
    sns.barplot(data=team_df, y="team", x="wins", color="#59A14F", ax=ax)
    for i, (w, p) in enumerate(zip(team_df["wins"], team_df["win_pct"])):
        ax.text(w + 1, i, f"{p}%", va="center", fontsize=8)
    ax.set(title="Total wins by team (label = win %)", xlabel="Wins", ylabel="")
    return _save(fig, "02_team_wins")


def plot_toss_impact(toss):
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    by_dec = toss["by_decision"]
    sns.barplot(data=by_dec, x="toss_decision", y="toss_winner_won_pct",
                color="#F28E2B", ax=axes[0])
    axes[0].axhline(50, ls="--", c="grey")
    axes[0].set(title="Toss winner's match win % by decision", ylim=(0, 100),
                xlabel="Toss decision", ylabel="% matches won")
    by_season = toss["by_season"]
    axes[1].plot(by_season["season"], by_season["chose_field_pct"], marker="o", label="Chose to field %")
    axes[1].plot(by_season["season"], by_season["toss_winner_won_pct"], marker="s", label="Toss winner won %")
    axes[1].axhline(50, ls="--", c="grey")
    axes[1].set(title="Toss trends over seasons", xlabel="Season", ylabel="%")
    axes[1].legend()
    return _save(fig, "03_toss_impact")


def plot_bat_first_vs_chase(bf):
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(bf["season"], bf["bat_first_win_pct"], marker="o", label="Batting first")
    ax.plot(bf["season"], bf["chasing_win_pct"], marker="o", label="Chasing")
    ax.axhline(50, ls="--", c="grey")
    ax.set(title="Win % : batting first vs chasing", xlabel="Season", ylabel="Win %")
    ax.legend()
    return _save(fig, "04_bat_first_vs_chase")


def plot_head_to_head(h2h):
    fig, ax = plt.subplots(figsize=(11, 9))
    sns.heatmap(h2h, annot=True, fmt="d", cmap="YlGnBu", cbar=False, ax=ax)
    ax.set(title="Head-to-head wins (row team beat column team)", xlabel="Opponent", ylabel="")
    return _save(fig, "05_head_to_head")


def plot_player_of_match(pom):
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(data=pom, y="player", x="awards", color="#E15759", ax=ax)
    ax.set(title="Most Player-of-the-Match awards", xlabel="Awards", ylabel="")
    return _save(fig, "06_player_of_match")


def plot_venues(venue_df, top=10):
    d = venue_df.head(top)
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.barplot(data=d, y="venue", x="matches", color="#76B7B2", ax=ax)
    for i, p in enumerate(d["bat_first_win_pct"]):
        ax.text(d["matches"].iloc[i] + 0.3, i, f"bat-first win {p}%", va="center", fontsize=8)
    ax.set(title=f"Top {top} venues by matches hosted", xlabel="Matches", ylabel="")
    return _save(fig, "07_venues")


def plot_season_wins_heatmap(season_wins):
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.heatmap(season_wins, annot=True, fmt="d", cmap="Blues", cbar=False, ax=ax)
    ax.set(title="Wins per team per season", xlabel="", ylabel="Season")
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    return _save(fig, "08_season_wins_heatmap")
