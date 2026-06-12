from pydantic import BaseModel
from typing import Any, Dict, List


class WorldcupSimulationResponse(BaseModel):
    group_stage: List[Dict[str, Any]]
    standings: Dict[str, Any]
    best_third_teams: List[Dict[str, Any]]
    round_of_32: List[Dict[str, Any]]
    round_of_16: List[Dict[str, Any]]
    quarterfinals: List[Dict[str, Any]]
    semifinals: List[Dict[str, Any]]
    third_place: Dict[str, Any]
    final: Dict[str, Any]
    champion: str
