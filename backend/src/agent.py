import os
from groq import Groq
from langchain_core.output_parsers import JsonOutputParser
from pydantic import ValidationError

from schemas import AgentResponse, AgentConfig, Move, Board
from store import Store


SYSTEM_PROMPT = """You are an expert 2048 game strategist. Your role is to analyze the current board state and recommend the best moves.

Rules of 2048:
- Tiles with numbers slide in the direction of movement
- When two tiles with the same number touch, they merge into one with the sum
- After each move, a new tile (2 or 4) appears randomly
- The goal is to create a tile with value 2048

Strategy Guidelines:
- Prioritize keeping the board organized and open
- Try to keep high-value tiles in corners
- Consider both immediate gains and long-term positioning

When analyzing the board:
1. Assess the current state (which tiles exist, their positions)
2. Evaluate each possible move (up, down, left, right)
3. Consider potential outcomes and strategic value
4. Rank moves by effectiveness

Respond with valid JSON only, following the exact format specified."""


class GameAgent:

    def __init__(self, config: AgentConfig, store: Store):
        key = os.getenv("GROQ_API_KEY")
        self._client = Groq(api_key=key) if key else None
        self._store = store
        self._config = config
        self._output_parser = JsonOutputParser(pydantic_object=AgentResponse)

    def invoke(self, num_suggestions: int) -> AgentResponse:
        user_prompt = self._build_prompt(num_suggestions)
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]
        chat_completion = self._client.chat.completions.create(
            messages=messages,
            model=self._config.model,
            temperature=self._config.temperature
        )
        content = chat_completion.choices[0].message.content

        try:
            parsed = self._output_parser.parse(content)
            return AgentResponse.model_validate(parsed)
        except ValidationError:
            return AgentResponse(
                recommended_moves=[
                    Move(
                        direction="UP",
                        reasoning="Default recommendation due to parsing error",
                        confidence=0.0
                    )
                ],
                game_analysis="Unable to analyze"
            )

    def _build_prompt(self, num_suggestions: int) -> str:
        board = self._store.load()
        board_analysis = self._format_board_for_analysis(board)
        metrics = self._calculate_board_metrics(board)

        return f"""Analyze the following 2048 game state and recommend moves:

{board_analysis}
Board Metrics:
- Empty spaces: {metrics['empty_spaces']}
- Highest tile: {metrics['max_tile']}
- Total value: {metrics['total_value']}

Provide exactly {num_suggestions} move recommendation(s).

Respond with the following JSON format (valid JSON only):
{{
  "recommended_moves": [
    {{
      "direction": "UP|DOWN|LEFT|RIGHT",
      "reasoning": "explanation",
      "confidence": 0.0-1.0
    }}
  ],
  "game_analysis": "overall assessment"
}}"""

    def _format_board_for_analysis(self, board: Board) -> str:
        board_str = "Current Board State:\n"
        for i, row in enumerate(board):
            board_str += f"Row {i}: {row}\n"
        return board_str

    def _calculate_board_metrics(self, board: Board) -> dict:
        flat = [val for row in board for val in row]
        return {
            "empty_spaces": sum(1 for val in flat if val == 0),
            "max_tile": max(flat),
            "total_value": sum(flat),
        }
