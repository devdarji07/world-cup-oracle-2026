import pandas as pd
import numpy as np
from typing import List, Tuple


def load_data(matches_path: str, rankings_path: str, market_path: str, groups_path: str) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    matches = pd.read_csv(matches_path, parse_dates=["date"], dayfirst=True)
    rankings = pd.read_csv(rankings_path)
    markets = pd.read_csv(market_path)
    groups = pd.read_csv(groups_path)
    return matches, rankings, markets, groups


def normalize_team_name(name: str) -> str:
    return name.strip().replace("&", "and").replace("United States", "USA").replace("South Korea", "Korea Republic").replace("USA", "United States")


def prepare_rankings(rankings: pd.DataFrame) -> pd.DataFrame:
    if "team" not in rankings.columns:
        rankings = rankings.rename(columns={"Country": "team", "Team": "team"})
    columns = [c for c in ["team", "rank", "points"] if c in rankings.columns]
    return rankings[columns].copy()


def prepare_markets(markets: pd.DataFrame) -> pd.DataFrame:
    if "team" not in markets.columns:
        markets = markets.rename(columns={"Team": "team"})
    columns = [c for c in ["team", "market_value_eur"] if c in markets.columns]
    return markets[columns].copy()


def build_match_features(matches: pd.DataFrame, rankings: pd.DataFrame, markets: pd.DataFrame) -> pd.DataFrame:
    matches = matches.copy()
    matches["home_team"] = matches["home_team"].map(lambda x: normalize_team_name(str(x)))
    matches["away_team"] = matches["away_team"].map(lambda x: normalize_team_name(str(x)))
    matches = matches.dropna(subset=["home_score", "away_score"])
    matches["result"] = matches.apply(lambda row: 0 if row["home_score"] > row["away_score"] else 1 if row["home_score"] == row["away_score"] else 2, axis=1)
    matches["goal_diff"] = matches["home_score"] - matches["away_score"]
    rankings = rankings.copy()
    rankings["team"] = rankings["team"].map(lambda x: normalize_team_name(str(x)))
    markets = markets.copy()
    markets["team"] = markets["team"].map(lambda x: normalize_team_name(str(x)))
    merged = matches.merge(rankings.rename(columns={"rank": "teamA_rank", "team": "home_team"}), on="home_team", how="left")
    merged = merged.merge(rankings.rename(columns={"rank": "teamB_rank", "team": "away_team"}), on="away_team", how="left")
    merged = merged.merge(markets.rename(columns={"market_value_eur": "teamA_market_value", "team": "home_team"}), on="home_team", how="left")
    merged = merged.merge(markets.rename(columns={"market_value_eur": "teamB_market_value", "team": "away_team"}), on="away_team", how="left")
    merged["rank_difference"] = merged["teamA_rank"] - merged["teamB_rank"]
    merged["market_value_difference"] = merged["teamA_market_value"] - merged["teamB_market_value"]
    merged = merged.sort_values("date").reset_index(drop=True)
    merged = add_form_and_aggregate_features(merged)
    return merged


def add_form_and_aggregate_features(matches: pd.DataFrame) -> pd.DataFrame:
    matches = matches.copy()
    matches["teamA_last5_form"] = 0.0
    matches["teamB_last5_form"] = 0.0
    matches["teamA_last10_winrate"] = 0.0
    matches["teamB_last10_winrate"] = 0.0
    matches["teamA_avg_goals_scored"] = 0.0
    matches["teamB_avg_goals_scored"] = 0.0
    matches["teamA_avg_goals_conceded"] = 0.0
    matches["teamB_avg_goals_conceded"] = 0.0
    matches["head_to_head_wins"] = 0
    matches["head_to_head_draws"] = 0

    for idx, row in matches.iterrows():
        teamA = row["home_team"]
        teamB = row["away_team"]
        prior = matches.iloc[:idx]
        teamA_matches = prior[(prior["home_team"] == teamA) | (prior["away_team"] == teamA)]
        teamB_matches = prior[(prior["home_team"] == teamB) | (prior["away_team"] == teamB)]
        h2h = prior[((prior["home_team"] == teamA) & (prior["away_team"] == teamB)) | ((prior["home_team"] == teamB) & (prior["away_team"] == teamA))]
        matches.at[idx, "teamA_last5_form"] = compute_form(teamA_matches, teamA)
        matches.at[idx, "teamB_last5_form"] = compute_form(teamB_matches, teamB)
        matches.at[idx, "teamA_last10_winrate"] = compute_winrate(teamA_matches, teamA, 10)
        matches.at[idx, "teamB_last10_winrate"] = compute_winrate(teamB_matches, teamB, 10)
        matches.at[idx, "teamA_avg_goals_scored"] = compute_avg_goals(teamA_matches, teamA, scored=True)
        matches.at[idx, "teamB_avg_goals_scored"] = compute_avg_goals(teamB_matches, teamB, scored=True)
        matches.at[idx, "teamA_avg_goals_conceded"] = compute_avg_goals(teamA_matches, teamA, scored=False)
        matches.at[idx, "teamB_avg_goals_conceded"] = compute_avg_goals(teamB_matches, teamB, scored=False)
        matches.at[idx, "head_to_head_wins"], matches.at[idx, "head_to_head_draws"] = compute_head_to_head(h2h, teamA, teamB)
    return matches


def compute_form(matches: pd.DataFrame, team: str) -> float:
    if matches.empty:
        return 0.0
    last5 = matches.tail(5)
    score = 0
    for _, row in last5.iterrows():
        if row["home_team"] == team:
            score += 3 if row["home_score"] > row["away_score"] else 1 if row["home_score"] == row["away_score"] else 0
        else:
            score += 3 if row["away_score"] > row["home_score"] else 1 if row["away_score"] == row["home_score"] else 0
    return score / 15.0 * 100.0


def compute_winrate(matches: pd.DataFrame, team: str, length: int) -> float:
    if matches.empty:
        return 0.0
    last = matches.tail(length)
    wins = 0
    for _, row in last.iterrows():
        if row["home_team"] == team:
            wins += 1 if row["home_score"] > row["away_score"] else 0
        else:
            wins += 1 if row["away_score"] > row["home_score"] else 0
    return wins / len(last)


def compute_avg_goals(matches: pd.DataFrame, team: str, scored: bool) -> float:
    if matches.empty:
        return 0.0
    goals = []
    for _, row in matches.iterrows():
        if row["home_team"] == team:
            goals.append(row["home_score"] if scored else row["away_score"])
        else:
            goals.append(row["away_score"] if scored else row["home_score"])
    return float(np.mean(goals)) if goals else 0.0


def compute_head_to_head(h2h: pd.DataFrame, teamA: str, teamB: str) -> Tuple[int, int]:
    wins = 0
    draws = 0
    for _, row in h2h.iterrows():
        if row["home_score"] == row["away_score"]:
            draws += 1
        elif (row["home_team"] == teamA and row["home_score"] > row["away_score"]) or (row["away_team"] == teamA and row["away_score"] > row["home_score"]):
            wins += 1
    return wins, draws


def export_features(feature_df: pd.DataFrame, output_path: str) -> None:
    feature_df.to_csv(output_path, index=False)
