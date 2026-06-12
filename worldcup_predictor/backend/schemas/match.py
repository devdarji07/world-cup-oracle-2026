from pydantic import BaseModel


class MatchPredictionRequest(BaseModel):
    home_team: str
    away_team: str
    teamA_rank: float
    teamB_rank: float
    rank_difference: float
    teamA_market_value: float
    teamB_market_value: float
    market_value_difference: float
    teamA_last5_form: float
    teamB_last5_form: float
    teamA_last10_winrate: float
    teamB_last10_winrate: float
    teamA_avg_goals_scored: float
    teamB_avg_goals_scored: float
    teamA_avg_goals_conceded: float
    teamB_avg_goals_conceded: float
    head_to_head_wins: int
    head_to_head_draws: int


class MatchPredictionResponse(BaseModel):
    home_team: str
    away_team: str
    home_win_probability: float
    draw_probability: float
    away_win_probability: float
    predicted_score: str
