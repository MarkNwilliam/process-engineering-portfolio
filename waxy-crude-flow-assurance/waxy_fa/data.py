import json
from pathlib import Path

from .properties import WaxyCrude

DEFAULT_DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "fluids.json"


def _read_data(path=DEFAULT_DATA_PATH):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def load_fluids(path=DEFAULT_DATA_PATH):
    return [WaxyCrude(**row) for row in _read_data(path)["fluids"]]


def load_field_cases(path=DEFAULT_DATA_PATH):
    return _read_data(path)["field_cases"]


def load_additive_cases(path=DEFAULT_DATA_PATH):
    return _read_data(path)["additive_cases"]
