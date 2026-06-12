from collections import Counter
import math
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from src.simulator import TournamentSimulator


class MonteCarloEngine:
    def __init__(self, simulator: TournamentSimulator):
        self.simulator = simulator

    def run(self, simulations: int = 10_000) -> List[Dict[str, Any]]:
        if simulations < 1 or simulations > 100_000:
            raise ValueError("simulations must be between 1 and 100000")
        baseline = self.simulator.simulate_worldcup(stochastic=False)
        field = [
            team
            for match in baseline["round_of_32"]
            for team in (match["home_team"], match["away_team"])
        ]
        strengths = {team: self._team_strength(team) for team in field}
        champions, finalists, semifinalists = Counter(), Counter(), Counter()
        for _ in range(simulations):
            remaining = field.copy()
            self.simulator.rng.shuffle(remaining)
            while len(remaining) > 4:
                remaining = self._play_round(remaining, strengths)
            for team in remaining:
                semifinalists[team] += 1
            finalists_in_run = self._play_round(remaining, strengths)
            for team in finalists_in_run:
                finalists[team] += 1
            champion = self._play_round(finalists_in_run, strengths)[0]
            champions[champion] += 1
        teams = set(champions) | set(finalists) | set(semifinalists)
        return sorted([{
            "team": team,
            "champion_probability": round(champions[team] / simulations * 100, 2),
            "final_probability": round(finalists[team] / simulations * 100, 2),
            "semifinal_probability": round(semifinalists[team] / simulations * 100, 2),
        } for team in teams], key=lambda row: row["champion_probability"], reverse=True)

    def _team_strength(self, team: str) -> float:
        rank = self.simulator.get_team_stat(team, "rank", 120)
        market = self.simulator.get_team_stat(team, "market_value_eur", 100_000_000)
        return max(0.05, (130 - rank) / 130 + math.log10(max(market, 1)) / 20)

    def _play_round(self, teams: List[str], strengths: Dict[str, float]) -> List[str]:
        winners = []
        for index in range(0, len(teams), 2):
            home, away = teams[index], teams[index + 1]
            home_probability = strengths[home] / (strengths[home] + strengths[away])
            winners.append(home if self.simulator.rng.random() < home_probability else away)
        return winners

    @staticmethod
    def save_odds(output_path: Path, odds: List[Dict[str, Any]]) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(odds).to_csv(output_path, index=False)
