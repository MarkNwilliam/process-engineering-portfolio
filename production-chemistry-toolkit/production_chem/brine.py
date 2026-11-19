from dataclasses import dataclass

ION_DATA = {
    "na": (22.990, 1),
    "k": (39.098, 1),
    "ca": (40.078, 2),
    "mg": (24.305, 2),
    "ba": (137.327, 2),
    "sr": (87.620, 2),
    "cl": (35.450, -1),
    "so4": (96.060, -2),
    "hco3": (61.017, -1),
    "co3": (60.009, -2),
    "fe": (55.845, 2),
}


@dataclass(frozen=True)
class Brine:
    name: str
    source: str
    na: float = 0.0
    k: float = 0.0
    ca: float = 0.0
    mg: float = 0.0
    ba: float = 0.0
    sr: float = 0.0
    cl: float = 0.0
    so4: float = 0.0
    hco3: float = 0.0
    co3: float = 0.0
    fe: float = 0.0


def molarities(brine: Brine) -> dict:
    result = {}
    for key, (molar_mass, _) in ION_DATA.items():
        result[key] = getattr(brine, key) / (molar_mass * 1000.0)
    return result


def charge_balance_error_pct(brine: Brine) -> float:
    moles = molarities(brine)
    cations = sum(moles[key] * charge for key, (_, charge) in ION_DATA.items() if charge > 0)
    anions = -sum(moles[key] * charge for key, (_, charge) in ION_DATA.items() if charge < 0)
    denominator = (cations + anions) / 2.0
    if denominator == 0:
        return 0.0
    return 100.0 * (cations - anions) / denominator


def ionic_strength_m(brine: Brine) -> float:
    moles = molarities(brine)
    return 0.5 * sum(moles[key] * charge**2 for key, (_, charge) in ION_DATA.items())


def tds_mg_l(brine: Brine) -> float:
    return sum(getattr(brine, key) for key in ION_DATA)
