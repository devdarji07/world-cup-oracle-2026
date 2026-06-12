import joblib
import numpy as np
import pandas as pd
from typing import Any, Dict


MODEL_FEATURES = [
    "teamA_rank", "teamB_rank", "rank_difference",
    "teamA_market_value", "teamB_market_value", "market_value_difference",
    "teamA_last5_form", "teamB_last5_form",
    "teamA_last10_winrate", "teamB_last10_winrate",
    "teamA_avg_goals_scored", "teamB_avg_goals_scored",
    "teamA_avg_goals_conceded", "teamB_avg_goals_conceded",
    "head_to_head_wins", "head_to_head_draws",
]


class MatchPredictor:
    def __init__(self, outcome_model_path: str, score_model_path: str):
        self.outcome_model = joblib.load(outcome_model_path)
        self.score_model = joblib.load(score_model_path)

    def predict_match(self, input_features: pd.DataFrame) -> Dict[str, Any]:
        missing = [column for column in MODEL_FEATURES if column not in input_features]
        if missing:
            raise ValueError(f"Missing model features: {', '.join(missing)}")
        features = input_features[MODEL_FEATURES]
        probability = self.outcome_model.predict_proba(features)[0]
        raw_score = np.asarray(self.score_model.predict(features)[0]).reshape(-1)
        if raw_score.size < 2:
            raise ValueError("Score model must predict home and away goals")
        home_score = int(np.clip(round(raw_score[0]), 0, 10))
        away_score = int(np.clip(round(raw_score[1]), 0, 10))
        return {
            "home_win_probability": float(round(probability[0] * 100, 1)),
            "draw_probability": float(round(probability[1] * 100, 1)),
            "away_win_probability": float(round(probability[2] * 100, 1)),
            "predicted_score": f"{home_score}-{away_score}",
        }
