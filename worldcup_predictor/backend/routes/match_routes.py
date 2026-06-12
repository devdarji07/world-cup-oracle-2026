from fastapi import APIRouter, HTTPException
from ..schemas.match import MatchPredictionRequest, MatchPredictionResponse
from ..services.tournament_service import predictor, simulator
import pandas as pd

router = APIRouter(prefix="", tags=["matches"])

@router.post("/predict-match", response_model=MatchPredictionResponse)
def predict_match(request: MatchPredictionRequest):
    try:
        feature_df = pd.DataFrame([request.dict()])
        prediction = predictor.predict_match(feature_df)
        return {
            "home_team": request.home_team,
            "away_team": request.away_team,
            **prediction,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/predict-match/{home_team}/{away_team}", response_model=MatchPredictionResponse)
def predict_teams(home_team: str, away_team: str):
    try:
        return simulator.simulate_match(home_team, away_team)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
