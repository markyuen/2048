from unittest.mock import MagicMock, patch
import pytest

from schemas import Direction, Status
from service import Service


@pytest.fixture
def mock_store():
    return MagicMock()


@pytest.fixture
def service(mock_store):
    return Service(mock_store)


@pytest.fixture
def mock_logic():
    with patch("service.logic") as mock:
        yield mock


def test_restart_game(service, mock_store, mock_logic):
    expected_board = [[0]*4]*4
    mock_logic.init_board.return_value = expected_board
    board = service.restart_game()
    assert board == expected_board
    mock_logic.init_board.assert_called_once()
    mock_store.save.assert_called_once_with(expected_board)


def test_make_move_noop(service, mock_store, mock_logic):
    initial_board = [[0]*4]*4
    mock_store.load.return_value = initial_board
    mock_logic.move_up.return_value = initial_board
    board, status = service.make_move(Direction.UP)
    assert board == initial_board
    assert status == Status.NOOP
    mock_logic.move_up.assert_called_once_with(initial_board)
    mock_store.save.assert_not_called()


def test_make_move_success(service, mock_store, mock_logic):
    initial_board = [[0]*4]*4
    intermediate_board = [[4]*4]*4
    expected_board = [[2]*4]*4
    mock_store.load.return_value = initial_board
    mock_logic.move_down.return_value = intermediate_board
    mock_logic.spawn_tile.return_value = expected_board
    mock_logic.is_win.return_value = False
    mock_logic.is_lose.return_value = False

    board, status = service.make_move(Direction.DOWN)
    assert board == expected_board
    assert status is None
    mock_logic.move_down.assert_called_once_with(initial_board)
    mock_logic.spawn_tile.assert_called_once_with(intermediate_board)
    mock_store.save.assert_called_once_with(expected_board)


def test_make_move_win(service, mock_store, mock_logic):
    initial_board = [[0]*4]*4
    intermediate_board = [[4]*4]*4
    expected_board = [[2]*4]*4
    mock_store.load.return_value = initial_board
    mock_logic.move_left.return_value = intermediate_board
    mock_logic.spawn_tile.return_value = expected_board
    mock_logic.is_win.return_value = True

    board, status = service.make_move(Direction.LEFT)
    assert board == expected_board
    assert status == Status.WIN
    mock_logic.move_left.assert_called_once_with(initial_board)
    mock_logic.spawn_tile.assert_called_once_with(intermediate_board)
    mock_store.save.assert_not_called()


def test_make_move_lose(service, mock_store, mock_logic):
    initial_board = [[0]*4]*4
    intermediate_board = [[4]*4]*4
    expected_board = [[2]*4]*4
    mock_store.load.return_value = initial_board
    mock_logic.move_right.return_value = intermediate_board
    mock_logic.spawn_tile.return_value = expected_board
    mock_logic.is_win.return_value = False
    mock_logic.is_lose.return_value = True

    board, status = service.make_move(Direction.RIGHT)
    assert board == expected_board
    assert status == Status.LOSE
    mock_logic.move_right.assert_called_once_with(initial_board)
    mock_logic.spawn_tile.assert_called_once_with(intermediate_board)
    mock_store.save.assert_not_called()
