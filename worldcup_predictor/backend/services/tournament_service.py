from pathlib import Path

import pandas as pd

from src.monte_carlo import MonteCarloEngine
from src.predictor import MatchPredictor
from src.simulator import TournamentSimulator

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
MODELS_DIR = ROOT / "models"
RESULTS_DIR = ROOT / "results"

predictor = MatchPredictor(
    MODELS_DIR / "match_outcome_model.pkl",
    MODELS_DIR / "score_prediction_model.pkl",
)
simulator = TournamentSimulator(
    pd.read_csv(DATA_DIR / "worldcup_groups.csv"),
    predictor,
    pd.read_csv(DATA_DIR / "fifa_rankings.csv"),
    pd.read_csv(DATA_DIR / "squad_market_values.csv"),
)
monte_carlo = MonteCarloEngine(simulator)


def run_and_save_tournament():
    result = simulator.simulate_worldcup()
    simulator.save_tournament(result, RESULTS_DIR)
    return result
