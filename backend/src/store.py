import json
from pathlib import Path

from schemas import Board


DEFAULT_PATH = Path(__file__).resolve().parent.parent / "store.json"


class Store:

    def save(self, board: Board) -> None:
        with open(DEFAULT_PATH, "w") as f:
            f.write(self._serialize_board(board))

    def load(self) -> Board:
        with open(DEFAULT_PATH, "r") as f:
            return self._deserialize_board(f.read())

    def _serialize_board(self, board: Board) -> str:
        return json.dumps(board)

    def _deserialize_board(self, s: str) -> Board:
        return json.loads(s)
