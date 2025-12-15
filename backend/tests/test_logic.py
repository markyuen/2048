from unittest.mock import patch, call

import logic


def test_init_board():
    board = logic.init_board()
    assert len(board) == 4
    for row in board:
        assert len(row) == 4
        for cell in row:
            assert cell in [0, 2]


def test_move_left():
    board = [
        [0, 8, 8, 8],
        [8, 0, 8, 8],
        [8, 8, 0, 8],
        [8, 8, 8, 0],
    ]
    expected = [
        [16, 8, 0, 0],
        [16, 8, 0, 0],
        [16, 8, 0, 0],
        [16, 8, 0, 0],
    ]
    assert logic.move_left(board) == expected


def test_move_left_no_change():
    board = [
        [8, 4, 0, 0],
        [4, 8, 0, 0],
        [0, 0, 0, 0],
        [2, 4, 8, 4],
    ]
    assert logic.move_left(board) == board


def test_move_right():
    board = [
        [0, 8, 2, 2],
        [4, 2, 0, 2],
        [2, 0, 2, 0],
        [8, 0, 2, 0],
    ]
    expected = [
        [0, 0, 8, 4],
        [0, 0, 4, 4],
        [0, 0, 0, 4],
        [0, 0, 8, 2]
    ]
    assert logic.move_right(board) == expected


def test_move_up():
    board = [
        [0, 0, 0, 8],
        [2, 0, 0, 0],
        [0, 4, 2, 0],
        [0, 4, 0, 0]
    ]
    expected = [
        [2, 8, 2, 8],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
    ]
    assert logic.move_up(board) == expected


def test_move_down():
    board = [
        [2, 4, 2, 0],
        [0, 0, 0, 0],
        [0, 2, 0, 0],
        [0, 0, 2, 0]
    ]
    expected = [
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 4, 0, 0],
        [2, 2, 4, 0]
    ]
    assert logic.move_down(board) == expected


def test_spawn_tile():
    board = [
        [2, 4, 8, 16],
        [32, 64, 0, 256],
        [512, 1024, 0, 0],
        [0, 4, 0, 8]
    ]
    expected = [
        [2, 4, 8, 16],
        [32, 64, 0, 256],
        [512, 1024, 0, 0],
        [2, 4, 0, 8]
    ]

    with patch("logic.random.choice") as mock_choice:
        mock_choice.side_effect = [(3, 0), 2]
        new_board = logic.spawn_tile(board)
        assert new_board == expected
        assert mock_choice.call_count == 2
        assert mock_choice.call_args_list == [
            call([(1, 2), (2, 2), (2, 3), (3, 0), (3, 2)]),
            call([2, 4]),
        ]


def test_is_win():
    board_win = [[2048, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    assert logic.is_win(board_win) is True
    board_no_win = [[1024, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    assert logic.is_win(board_no_win) is False


def test_is_lose():
    # Full board, no merges possible
    board_lose = [
        [2, 4, 2, 4],
        [4, 2, 4, 2],
        [2, 4, 2, 4],
        [4, 2, 4, 2]
    ]
    assert logic.is_lose(board_lose) is True

    # Full board, horizontal merge possible
    board_h = [
        [2, 2, 4, 8],
        [4, 8, 16, 32],
        [2, 4, 8, 16],
        [4, 8, 16, 32]
    ]
    assert logic.is_lose(board_h) is False

    # Full board, vertical merge possible
    board_v = [
        [2, 4, 2, 4],
        [2, 8, 16, 32],
        [2, 4, 8, 16],
        [4, 8, 16, 32]
    ]
    assert logic.is_lose(board_v) is False

    # Empty space exists
    board_empty = [
        [2, 4, 2, 4],
        [4, 2, 4, 2],
        [2, 4, 2, 4],
        [4, 2, 4, 0]
    ]
    assert logic.is_lose(board_empty) is False
