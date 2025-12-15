from unittest.mock import patch, mock_open, ANY
import pytest

from store import Store


board = [[1, 2], [3, 4]]
serialized = "[[1, 2], [3, 4]]"


@pytest.fixture
def store():
    return Store()


def test_save(store):
    with patch("builtins.open", mock_open()) as m:
        store.save(board)
        m.assert_called_once_with(ANY, "w")
        handle = m.return_value
        handle.write.assert_called_once_with(serialized)


def test_load(store):
    with patch("builtins.open", mock_open(read_data=serialized)) as m:
        assert store.load() == board
        m.assert_called_once_with(ANY, "r")
