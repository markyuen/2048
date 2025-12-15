from unittest.mock import patch
from fastapi.testclient import TestClient
import pytest

from api import app
from schemas import Direction, Status, AgentResponse

client = TestClient(app)


@pytest.fixture
def mock_service():
    with patch("api.service") as mock:
        yield mock


@pytest.fixture
def mock_agent():
    with patch("api.agent") as mock:
        yield mock


def test_restart(mock_service):
    expected_board = [[0]*4]*4
    mock_service.restart_game.return_value = expected_board

    response = client.patch("/api/restart")
    assert response.status_code == 200
    data = response.json()
    assert data["board"] == expected_board
    assert data["status"] is None
    mock_service.restart_game.assert_called_once()


@pytest.mark.parametrize(
    "direction, status",
    [
        (Direction.UP, None),
        (Direction.DOWN, Status.WIN),
        (Direction.LEFT, Status.LOSE),
        (Direction.RIGHT, Status.NOOP),
    ],
)
def test_move(mock_service, direction, status):
    expected_board = [[0]*4]*4
    mock_service.make_move.return_value = (expected_board, status)
    response = client.patch(f"/api/move/{direction.value}")
    assert response.status_code == 200
    data = response.json()
    assert data["board"] == expected_board
    assert data["status"] == status
    mock_service.make_move.assert_called_once_with(direction)


def test_move_invalid_direction():
    response = client.patch("/api/move/hi")
    assert response.status_code == 422


def test_suggest_success(mock_agent):
    mock_output = {
        "recommended_moves": [
            {"direction": "UP", "reasoning": "Test", "confidence": 0.9}
        ],
        "game_analysis": "Analysis"
    }
    mock_agent.invoke.return_value = AgentResponse(**mock_output)

    response = client.post("/api/suggest/3")

    assert response.status_code == 200
    assert response.json() == mock_output
    mock_agent.invoke.assert_called_once_with(3)


def test_suggest_agent_error(mock_agent):
    mock_agent.invoke.side_effect = Exception("Agent error")
    response = client.post("/api/suggest/3")
    assert response.status_code == 500
    assert response.json()["detail"] == "Agent invocation failed"


def test_suggest_input_error():
    response = client.post("/api/suggest/hi")
    assert response.status_code == 422
