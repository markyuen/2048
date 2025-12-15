import random
from schemas import Board


def init_board() -> Board:
    return [[random.choice([0, 2]) for _ in range(4)] for _ in range(4)]


def _compress_line_left(line: list[int]) -> list[int]:
    non_empty = [v for v in line if v != 0]
    merged = []
    i = 0
    while i < len(non_empty):
        if i + 1 >= len(non_empty):
            merged.append(non_empty[i])
            break
        if non_empty[i] == non_empty[i + 1]:
            merged.append(non_empty[i] * 2)
            i += 2
        else:
            merged.append(non_empty[i])
            i += 1
    return merged + [0 for _ in range(4-len(merged))]


def _rotate_board_clockwise(board: Board) -> Board:
    return [[board[3-c][r] for c in range(4)] for r in range(4)]


def move_left(board: Board) -> Board:
    return [_compress_line_left(board[r]) for r in range(4)]


def move_down(board: Board) -> Board:
    board = _rotate_board_clockwise(board)
    board = move_left(board)
    board = _rotate_board_clockwise(board)
    board = _rotate_board_clockwise(board)
    return _rotate_board_clockwise(board)


def move_right(board: Board) -> Board:
    board = _rotate_board_clockwise(board)
    board = _rotate_board_clockwise(board)
    board = move_left(board)
    board = _rotate_board_clockwise(board)
    return _rotate_board_clockwise(board)


def move_up(board: Board) -> Board:
    board = _rotate_board_clockwise(board)
    board = _rotate_board_clockwise(board)
    board = _rotate_board_clockwise(board)
    board = move_left(board)
    return _rotate_board_clockwise(board)


def spawn_tile(board: Board) -> Board:
    empty = [(r, c) for r in range(4) for c in range(4) if board[r][c] == 0]
    r, c = random.choice(empty)
    board[r][c] = random.choice([2, 4])
    return board


def is_win(board: Board) -> bool:
    return any(board[r][c] == 2048 for r in range(4) for c in range(4))


def is_lose(board: Board) -> bool:
    return all(
        new_board == board for new_board in [
            move_left(board),
            move_right(board),
            move_up(board),
            move_down(board),
        ]
    )
