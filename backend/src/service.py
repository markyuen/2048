import logic
from schemas import Board, Direction, Status
from store import Store


class Service:

    def __init__(self, store: Store):
        self._store = store

    def restart_game(self) -> Board:
        board = logic.init_board()
        self._store.save(board)
        return board

    def make_move(self, direction: Direction) -> tuple[Board, Status | None]:
        board = self._store.load()
        after_move = self._move(board, direction)
        if after_move == board:
            return board, Status.NOOP

        after_tile = logic.spawn_tile(after_move)
        if logic.is_win(after_tile):
            return after_tile, Status.WIN
        if logic.is_lose(after_tile):
            return after_tile, Status.LOSE

        self._store.save(after_tile)
        return after_tile, None

    def _move(self, board: Board, direction: Direction) -> Board:
        if direction == Direction.UP:
            board = logic.move_up(board)
        elif direction == Direction.DOWN:
            board = logic.move_down(board)
        elif direction == Direction.LEFT:
            board = logic.move_left(board)
        else:
            board = logic.move_right(board)
        return board
