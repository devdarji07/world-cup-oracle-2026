from backend.services.tournament_service import simulator


def test_group_stage_and_standings():
    matches = simulator.simulate_group_stage()
    standings = simulator.calculate_group_standings(matches)
    assert len(matches) == 72
    assert len(standings) == 12
    assert all(len(table) == 4 for table in standings.values())
    assert all(sum(team["played"] for team in table) == 12 for table in standings.values())


def test_complete_tournament():
    result = simulator.simulate_worldcup()
    assert len(result["round_of_32"]) == 16
    assert len(result["round_of_16"]) == 8
    assert len(result["quarterfinals"]) == 4
    assert len(result["semifinals"]) == 2
    assert result["champion"] == result["final"]["winner"]
    assert len([team for team in result["best_third_teams"] if team["qualified"]]) == 8
