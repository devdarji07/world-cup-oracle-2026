from fastapi import APIRouter, HTTPException
from ..schemas.simulation import WorldcupSimulationResponse
from ..services.tournament_service import RESULTS_DIR, monte_carlo, run_and_save_tournament, simulator

router = APIRouter(prefix="", tags=["simulations"])

@router.post("/simulate-group-stage", response_model=list)
def simulate_group_stage():
    try:
        return simulator.simulate_group_stage()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.post("/simulate-tournament", response_model=WorldcupSimulationResponse)
def simulate_tournament():
    try:
        return run_and_save_tournament()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.post("/run-monte-carlo")
def run_monte_carlo(simulations: int = 10000):
    try:
        odds = monte_carlo.run(simulations)
        monte_carlo.save_odds(RESULTS_DIR / "champion_odds.csv", odds)
        return {"champion_odds": odds}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
