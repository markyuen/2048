from pydantic import BaseModel, Field
from enum import Enum


Board = list[list[int]]


class Status(str, Enum):
    WIN = "WIN"
    LOSE = "LOSE"
    NOOP = "NOOP"


class GameResponse(BaseModel):
    board: Board = Field(
        ...,
        description="4x4 game board state with tile values"
    )
    status: Status | None = Field(
        ...,
        description="Game status: 'WIN', 'LOSE', 'NOOP', or None if ongoing"
    )


class Direction(str, Enum):
    UP = "UP"
    DOWN = "DOWN"
    LEFT = "LEFT"
    RIGHT = "RIGHT"


class Move(BaseModel):
    direction: Direction = Field(
        ...,
        description="Direction to move: 'UP', 'DOWN', 'LEFT', 'RIGHT'"
    )
    reasoning: str = Field(
        ...,
        description="Explanation for this move"
    )
    confidence: float = Field(
        ...,
        ge=0,
        le=1,
        description="Confidence score between 0 and 1"
    )


class AgentResponse(BaseModel):
    recommended_moves: list[Move] = Field(
        ...,
        description="list of recommended moves ordered by preference"
    )
    game_analysis: str = Field(
        ...,
        description="High-level analysis of the current game state"
    )


class AgentConfig(BaseModel):
    model: str = Field(
        ...,
        description="LLM model to use"
    )
    temperature: float = Field(
        ...,
        ge=0,
        le=2,
        description="Temperature for LLM sampling"
    )
