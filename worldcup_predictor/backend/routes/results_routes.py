from pathlib import Path
from fastapi import APIRouter, HTTPException
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = ROOT / "results"

router = APIRouter(prefix="", tags=["results"])


def read_records(path):
    df = pd.read_csv(path)
    return df.astype(object).where(pd.notna(df), None).to_dict(orient="records")


@router.get("/group-stage-results")
def group_stage_results():
    try:
        df = pd.read_csv(RESULTS_DIR / "tournament_predictions.csv")
        df = df[df["stage"] == "Group Stage"]
        return df.astype(object).where(pd.notna(df), None).to_dict(orient="records")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.get("/knockout-bracket")
def knockout_bracket():
    try:
        df = pd.read_csv(RESULTS_DIR / "tournament_predictions.csv")
        df = df[df["stage"] != "Group Stage"]
        return df.astype(object).where(pd.notna(df), None).to_dict(orient="records")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/group-standings")
def group_standings():
    try:
        return read_records(RESULTS_DIR / "group_standings.csv")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/best-third-teams")
def best_third_teams():
    try:
        return read_records(RESULTS_DIR / "best_third_teams.csv")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.get("/champion-odds")
def champion_odds():
    try:
        return read_records(RESULTS_DIR / "champion_odds.csv")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
