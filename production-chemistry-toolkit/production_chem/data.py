import csv
import json
from pathlib import Path

from .brine import Brine
from .treatment import WaterQuality

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def load_brines(path=DATA_DIR / "brines.csv"):
    with open(path, newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    brines = []
    for row in rows:
        values = {key: float(row[key]) for key in ["na", "k", "ca", "mg", "ba", "sr", "cl", "so4", "hco3", "co3", "fe"]}
        brines.append(Brine(name=row["name"], source=row["source"], **values))
    return brines


def load_ksp_data(path=DATA_DIR / "ksp.json"):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def load_treatment(path=DATA_DIR / "treatment.json"):
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    quality = WaterQuality(name="influent", **data["influent"])
    return quality, data["steps"]
