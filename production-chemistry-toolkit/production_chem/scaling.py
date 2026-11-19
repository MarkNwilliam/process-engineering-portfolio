import math
from dataclasses import dataclass

from .brine import Brine, ionic_strength_m, molarities

DEFAULT_KSP_25C = {
    "BaSO4": 1.1e-10,
    "SrSO4": 3.2e-7,
    "CaSO4": 2.4e-5,
    "CaCO3": 3.3e-9,
}

MINERAL_IONS = {
    "BaSO4": ("ba", "so4"),
    "SrSO4": ("sr", "so4"),
    "CaSO4": ("ca", "so4"),
}


@dataclass(frozen=True)
class ScalingResult:
    mineral: str
    saturation_ratio: float
    ion_activity_product: float
    ionic_strength_m: float
    activity_correction_used: bool


def davies_gamma(charge: int, strength: float) -> float:
    if strength > 0.5:
        raise ValueError("Davies equation is not valid above 0.5 M")
    root = math.sqrt(max(strength, 0.0))
    log_gamma = -0.509 * charge**2 * (root / (1.0 + root) - 0.3 * strength)
    return 10.0**log_gamma


def saturation_ratio(brine: Brine, mineral: str, ksp: float = None, use_activity: bool = True) -> ScalingResult:
    if mineral not in MINERAL_IONS:
        raise ValueError(f"unsupported mineral: {mineral}")
    ksp_value = DEFAULT_KSP_25C[mineral] if ksp is None else ksp
    cation_key, anion_key = MINERAL_IONS[mineral]
    moles = molarities(brine)
    strength = ionic_strength_m(brine)
    corrected = use_activity and strength <= 0.5
    if corrected:
        cation_activity = moles[cation_key] * davies_gamma(2, strength)
        anion_activity = moles[anion_key] * davies_gamma(-2, strength)
    else:
        cation_activity = moles[cation_key]
        anion_activity = moles[anion_key]
    product = cation_activity * anion_activity
    return ScalingResult(
        mineral=mineral,
        saturation_ratio=product / ksp_value,
        ion_activity_product=product,
        ionic_strength_m=strength,
        activity_correction_used=corrected,
    )


def lsi(brine: Brine, ph: float = 7.0, pka2: float = 10.33, ksp_calcite: float = DEFAULT_KSP_25C["CaCO3"]) -> float:
    moles = molarities(brine)
    calcium = moles["ca"]
    carbonate_from_bicarbonate = moles["hco3"] * 10.0 ** (ph - pka2)
    carbonate = moles["co3"] + carbonate_from_bicarbonate
    if calcium <= 0 or carbonate <= 0:
        return float("-inf")
    return math.log10(calcium * carbonate / ksp_calcite)
