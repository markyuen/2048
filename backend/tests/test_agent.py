import os
from unittest.mock import MagicMock, patch
import pytest

from schemas import AgentConfig, AgentResponse, Move
from agent import GameAgent, SYSTEM_PROMPT


@pytest.fixture
def mock_store():
    return MagicMock()


@pytest.fixture
def mock_groq():
    with patch("agent.Groq") as mock:
        yield mock


@pytest.fixture
def agent(mock_store, mock_groq):
    with patch.dict(os.environ, {"GROQ_API_KEY": "fake_key"}):
        config = AgentConfig(model="a", temperature=0)
        return GameAgent(config, mock_store)


def test_invoke_success(agent, mock_store, mock_groq):
    mock_store.load.return_value = [
        [2, 4, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [8, 0, 0, 0]
    ]

    expected_prompt = """Analyze the following 2048 game state and recommend moves:

Current Board State:
Row 0: [2, 4, 0, 0]
Row 1: [0, 0, 0, 0]
Row 2: [0, 0, 0, 0]
Row 3: [8, 0, 0, 0]

Board Metrics:
- Empty spaces: 13
- Highest tile: 8
- Total value: 14

Provide exactly 1 move recommendation(s).

Respond with the following JSON format (valid JSON only):
{
  "recommended_moves": [
    {
      "direction": "UP|DOWN|LEFT|RIGHT",
      "reasoning": "explanation",
      "confidence": 0.0-1.0
    }
  ],
  "game_analysis": "overall assessment"
}"""
    expected_messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": expected_prompt},
    ]
    mock_response_content = """{
        "recommended_moves": [
            {
                "direction": "UP",
                "reasoning": "test",
                "confidence": 0.8
            }
        ],
        "game_analysis": "test"
    }"""

    mock_client_instance = mock_groq.return_value
    mock_chat_completion = MagicMock()
    mock_chat_completion.choices[0].message.content = mock_response_content
    mock_client_instance.chat.completions.create.return_value = mock_chat_completion

    expected_response = AgentResponse(
        recommended_moves=[
            Move(direction="UP", reasoning="test", confidence=0.8)
        ],
        game_analysis="test"
    )

    assert agent.invoke(1) == expected_response
    mock_store.load.assert_called_once()
    mock_client_instance.chat.completions.create.assert_called_once_with(
        messages=expected_messages, model="a", temperature=0)


def test_invoke_validation_error(agent, mock_store, mock_groq):
    mock_store.load.return_value = [[0]*4]*4

    mock_chat_completion = MagicMock()
    mock_chat_completion.choices[0].message.content = '{"missing": "stuff!"}'
    mock_groq.return_value.chat.completions.create.return_value = mock_chat_completion

    response = agent.invoke(1)
    assert len(response.recommended_moves) == 1
    assert response.recommended_moves[0].reasoning == "Default recommendation due to parsing error"
