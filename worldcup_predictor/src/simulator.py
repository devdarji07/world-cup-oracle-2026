from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from src.predictor import MatchPredictor

ROOT = Path(__file__).resolve().parents[1]


def normalize_value(value: float, default: float = 0.0) -> float:
    return default if value is None or pd.isna(value) else float(value)


class TournamentSimulator:
    def __init__(
        self,
        fixtures_df: pd.DataFrame,
        predictor: MatchPredictor,
        rankings_df: pd.DataFrame,
        markets_df: pd.DataFrame,
        seed: Optional[int] = None,
    ):
        self.fixtures_df = fixtures_df.copy()
        self.predictor = predictor
        self.rankings_df = rankings_df.copy()
        self.markets_df = markets_df.copy()
        self.rng = np.random.default_rng(seed)
        self._prediction_cache: Dict[tuple[str, str], Dict[str, Any]] = {}

    def get_team_stat(self, team: str, column: str, default: float) -> float:
        source = self.rankings_df if column == "rank" else self.markets_df
        if column not in source.columns:
            return default
        row = source.loc[source["team"].astype(str).str.strip() == str(team).strip()]
        return normalize_value(row.iloc[0][column], default) if not row.empty else default

    def build_match_input(self, home_team: str, away_team: str) -> pd.DataFrame:
        home_rank = self.get_team_stat(home_team, "rank", 120)
        away_rank = self.get_team_stat(away_team, "rank", 120)
        home_value = self.get_team_stat(home_team, "market_value_eur", 100_000_000)
        away_value = self.get_team_stat(away_team, "market_value_eur", 100_000_000)
        rank_edge = away_rank - home_rank
        return pd.DataFrame([{
            "teamA_rank": home_rank, "teamB_rank": away_rank,
            "rank_difference": home_rank - away_rank,
            "teamA_market_value": home_value, "teamB_market_value": away_value,
            "market_value_difference": home_value - away_value,
            "teamA_last5_form": np.clip(50 + rank_edge / 4, 0, 100),
            "teamB_last5_form": np.clip(50 - rank_edge / 4, 0, 100),
            "teamA_last10_winrate": np.clip(0.5 + rank_edge / 300, 0, 1),
            "teamB_last10_winrate": np.clip(0.5 - rank_edge / 300, 0, 1),
            "teamA_avg_goals_scored": np.clip(1.35 + rank_edge / 100, 0.3, 3.2),
            "teamB_avg_goals_scored": np.clip(1.35 - rank_edge / 100, 0.3, 3.2),
            "teamA_avg_goals_conceded": np.clip(1.1 - rank_edge / 180, 0.2, 2.5),
            "teamB_avg_goals_conceded": np.clip(1.1 + rank_edge / 180, 0.2, 2.5),
            "head_to_head_wins": 0, "head_to_head_draws": 0,
        }])

    def simulate_match(
        self, home_team: str, away_team: str, match_id: str = "", stage: str = "",
        group: str = "", stochastic: bool = False, knockout: bool = False,
    ) -> Dict[str, Any]:
        cache_key = (home_team, away_team)
        if cache_key not in self._prediction_cache:
            self._prediction_cache[cache_key] = self.predictor.predict_match(self.build_match_input(home_team, away_team))
        prediction = self._prediction_cache[cache_key].copy()
        home_score, away_score = map(int, prediction["predicted_score"].split("-"))
        if stochastic:
            probabilities = np.array([
                prediction["home_win_probability"], prediction["draw_probability"],
                prediction["away_win_probability"],
            ], dtype=float)
            probabilities = probabilities / probabilities.sum()
            outcome = int(self.rng.choice(3, p=probabilities))
            base_home = max(0.2, home_score + 0.35)
            base_away = max(0.2, away_score + 0.35)
            home_score, away_score = int(self.rng.poisson(base_home)), int(self.rng.poisson(base_away))
            if outcome == 0 and home_score <= away_score:
                home_score = away_score + 1
            elif outcome == 2 and away_score <= home_score:
                away_score = home_score + 1
            elif outcome == 1:
                away_score = home_score

        winner = None
        decided_by = "regulation"
        if home_score > away_score:
            winner = home_team
        elif away_score > home_score:
            winner = away_team
        elif knockout:
            home_probability = prediction["home_win_probability"]
            away_probability = prediction["away_win_probability"]
            winner = str(self.rng.choice(
                [home_team, away_team],
                p=np.array([home_probability, away_probability]) / (home_probability + away_probability),
            ))
            decided_by = "penalties"

        return {
            "match_id": match_id, "stage": stage, "group": group,
            "home_team": home_team, "away_team": away_team,
            **prediction, "predicted_score": f"{home_score}-{away_score}",
            "home_score": home_score, "away_score": away_score,
            "winner": winner, "decided_by": decided_by,
        }

    def simulate_group_stage(self, stochastic: bool = False) -> List[Dict[str, Any]]:
        fixtures = self.fixtures_df[self.fixtures_df["stage"] == "Group Stage"]
        return [
            self.simulate_match(
                row["team_slot_1"], row["team_slot_2"], row["match_id"],
                "Group Stage", row["group"], stochastic,
            )
            for _, row in fixtures.iterrows()
        ]

    def calculate_group_standings(self, matches: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        standings: Dict[str, Dict[str, Dict[str, Any]]] = {}
        for match in matches:
            group = match["group"]
            table = standings.setdefault(group, {})
            for team in (match["home_team"], match["away_team"]):
                table.setdefault(team, {
                    "team": team, "group": group, "played": 0, "wins": 0, "draws": 0,
                    "losses": 0, "goals_for": 0, "goals_against": 0, "goal_difference": 0,
                    "points": 0,
                })
            home, away = table[match["home_team"]], table[match["away_team"]]
            hs, aws = match["home_score"], match["away_score"]
            home["played"] += 1; away["played"] += 1
            home["goals_for"] += hs; home["goals_against"] += aws
            away["goals_for"] += aws; away["goals_against"] += hs
            if hs > aws:
                home["wins"] += 1; home["points"] += 3; away["losses"] += 1
            elif hs < aws:
                away["wins"] += 1; away["points"] += 3; home["losses"] += 1
            else:
                home["draws"] += 1; away["draws"] += 1; home["points"] += 1; away["points"] += 1
        result = {}
        for group, table in standings.items():
            for team in table.values():
                team["goal_difference"] = team["goals_for"] - team["goals_against"]
            ranked = sorted(
                table.values(),
                key=lambda team: (team["points"], team["goal_difference"], team["goals_for"], -self.get_team_stat(team["team"], "rank", 120)),
                reverse=True,
            )
            for position, team in enumerate(ranked, 1):
                team["position"] = position
            result[group] = ranked
        return result

    def determine_best_third_placed_teams(self, standings: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        thirds = [table[2].copy() for table in standings.values()]
        ranked = sorted(
            thirds,
            key=lambda team: (team["points"], team["goal_difference"], team["goals_for"], -self.get_team_stat(team["team"], "rank", 120)),
            reverse=True,
        )
        for index, team in enumerate(ranked, 1):
            team["third_place_rank"] = index
            team["qualified"] = index <= 8
        return ranked

    def generate_round_of_32(
        self, standings: Dict[str, List[Dict[str, Any]]], best_thirds: List[Dict[str, Any]],
    ) -> List[Dict[str, str]]:
        slots = {f"1{group}": table[0]["team"] for group, table in standings.items()}
        slots.update({f"2{group}": table[1]["team"] for group, table in standings.items()})
        available_thirds = {team["group"]: team["team"] for team in best_thirds if team["qualified"]}
        templates = self.fixtures_df[self.fixtures_df["stage"] == "Round of 32 Template"]
        matches = []
        used_thirds = set()
        for _, row in templates.iterrows():
            opponent_slot = row["team_slot_2"]
            if str(opponent_slot).startswith("3"):
                allowed = [group for group in str(opponent_slot)[1:] if group in available_thirds and group not in used_thirds]
                if not allowed:
                    allowed = [group for group in available_thirds if group not in used_thirds]
                group = allowed[0]
                away_team = available_thirds[group]
                used_thirds.add(group)
            else:
                away_team = slots[opponent_slot]
            matches.append({"match_id": row["match_id"], "home_team": slots[row["team_slot_1"]], "away_team": away_team})
        return matches

    def simulate_knockout_round(
        self, pairings: List[Dict[str, str]], stage: str, stochastic: bool,
    ) -> List[Dict[str, Any]]:
        return [
            self.simulate_match(
                pairing["home_team"], pairing["away_team"],
                pairing.get("match_id", f"{stage[:3].upper()}-{index}"), stage=stage,
                stochastic=stochastic, knockout=True,
            )
            for index, pairing in enumerate(pairings, 1)
        ]

    @staticmethod
    def pair_winners(matches: List[Dict[str, Any]], prefix: str) -> List[Dict[str, str]]:
        winners = [match["winner"] for match in matches]
        return [
            {"match_id": f"{prefix}-{index // 2 + 1}", "home_team": winners[index], "away_team": winners[index + 1]}
            for index in range(0, len(winners), 2)
        ]

    def simulate_worldcup(self, stochastic: bool = False) -> Dict[str, Any]:
        group_stage = self.simulate_group_stage(stochastic)
        standings = self.calculate_group_standings(group_stage)
        best_thirds = self.determine_best_third_placed_teams(standings)
        round_of_32 = self.simulate_knockout_round(self.generate_round_of_32(standings, best_thirds), "Round of 32", stochastic)
        round_of_16 = self.simulate_knockout_round(self.pair_winners(round_of_32, "R16"), "Round of 16", stochastic)
        quarterfinals = self.simulate_knockout_round(self.pair_winners(round_of_16, "QF"), "Quarterfinal", stochastic)
        semifinals = self.simulate_knockout_round(self.pair_winners(quarterfinals, "SF"), "Semifinal", stochastic)
        final = self.simulate_knockout_round(self.pair_winners(semifinals, "F"), "Final", stochastic)[0]
        losers = [match["away_team"] if match["winner"] == match["home_team"] else match["home_team"] for match in semifinals]
        third_place = self.simulate_match(losers[0], losers[1], "3P-1", "Third Place", stochastic=stochastic, knockout=True)
        return {
            "group_stage": group_stage, "standings": standings, "best_third_teams": best_thirds,
            "round_of_32": round_of_32, "round_of_16": round_of_16,
            "quarterfinals": quarterfinals, "semifinals": semifinals,
            "third_place": third_place, "final": final, "champion": final["winner"],
        }

    @staticmethod
    def save_tournament(result: Dict[str, Any], results_dir: Path) -> None:
        results_dir.mkdir(parents=True, exist_ok=True)
        stages = ["group_stage", "round_of_32", "round_of_16", "quarterfinals", "semifinals"]
        matches = [match for stage in stages for match in result[stage]]
        matches.extend([result["third_place"], result["final"]])
        pd.DataFrame(matches).to_csv(results_dir / "tournament_predictions.csv", index=False)
        standings = [team for table in result["standings"].values() for team in table]
        pd.DataFrame(standings).to_csv(results_dir / "group_standings.csv", index=False)
        pd.DataFrame(result["best_third_teams"]).to_csv(results_dir / "best_third_teams.csv", index=False)
