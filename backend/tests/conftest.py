import sys
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
SRC = (HERE / ".." / "src").resolve()
sys.path.insert(0, str(SRC))
