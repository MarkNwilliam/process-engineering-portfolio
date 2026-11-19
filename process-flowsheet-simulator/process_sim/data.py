import json
from pathlib import Path

from .stream import Stream

DEFAULT_DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "feed.json"


def _read_data(path=DEFAULT_DATA_PATH):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def load_feed(path=DEFAULT_DATA_PATH):
    return _read_data(path)["feed"]


def load_settings(path=DEFAULT_DATA_PATH):
    return _read_data(path)["settings"]


def load_wash_water(path=DEFAULT_DATA_PATH, name="wash_water"):
    data = _read_data(path)
    return Stream(
        name=name,
        water_kg_s=data["wash_water_kg_s"],
        temperature_c=data["feed"]["temperature_c"],
        pressure_bar=data["settings"]["pump_discharge_bar"],
    )
