from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_health_and_prediction():
    assert client.get("/health").json()["models_loaded"] is True
    response = client.get("/predict-match/France/Argentina")
    assert response.status_code == 200
    assert response.json()["home_team"] == "France"


def test_tournament_endpoint():
    response = client.post("/simulate-tournament")
    assert response.status_code == 200
    assert response.json()["champion"]
    assert len(client.get("/group-stage-results").json()) == 72
    assert len(client.get("/knockout-bracket").json()) == 32


def test_monte_carlo_endpoint():
    response = client.post("/run-monte-carlo?simulations=100")
    assert response.status_code == 200
    odds = response.json()["champion_odds"]
    assert round(sum(team["champion_probability"] for team in odds), 2) == 100
