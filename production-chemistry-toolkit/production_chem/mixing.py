import math

from .brine import Brine, ION_DATA, molarities
from .scaling import DEFAULT_KSP_25C, MINERAL_IONS

MINERAL_MOLAR_MASS = {"BaSO4": 233.39, "SrSO4": 183.68, "CaSO4": 136.14, "CaCO3": 100.09}


def mix_brines(name: str, contributions: list) -> Brine:
    if not contributions:
        raise ValueError("at least one brine is required")
    total_fraction = sum(fraction for _, fraction in contributions)
    if total_fraction <= 0:
        raise ValueError("fractions must sum to a positive value")
    values = {key: 0.0 for key in ION_DATA}
    for brine, fraction in contributions:
        share = fraction / total_fraction
        for key in ION_DATA:
            values[key] += getattr(brine, key) * share
    return Brine(name=name, source="Mixture of " + ", ".join(brine.name for brine, _ in contributions), **values)


def precipitation_mg_l(brine: Brine, mineral: str, ksp: float = None) -> float:
    if mineral not in MINERAL_IONS:
        raise ValueError(f"unsupported mineral: {mineral}")
    ksp_value = DEFAULT_KSP_25C[mineral] if ksp is None else ksp
    cation_key, anion_key = MINERAL_IONS[mineral]
    moles = molarities(brine)
    cation = moles[cation_key]
    anion = moles[anion_key]
    if cation <= 0 or anion <= 0 or cation * anion <= ksp_value:
        return 0.0
    precipitated_mol_l = ((cation + anion) - math.sqrt((cation - anion) ** 2 + 4.0 * ksp_value)) / 2.0
    return precipitated_mol_l * MINERAL_MOLAR_MASS[mineral] * 1000.0


def remaining_ion_mg_l(brine: Brine, mineral: str, ion: str) -> float:
    if mineral not in MINERAL_IONS:
        raise ValueError(f"unsupported mineral: {mineral}")
    if ion not in MINERAL_IONS[mineral]:
        raise ValueError(f"{ion} is not part of {mineral}")
    ksp_value = DEFAULT_KSP_25C[mineral]
    cation_key, anion_key = MINERAL_IONS[mineral]
    moles = molarities(brine)
    cation = moles[cation_key]
    anion = moles[anion_key]
    if cation <= 0 or anion <= 0 or cation * anion <= ksp_value:
        return getattr(brine, ion)
    precipitated_mol_l = ((cation + anion) - math.sqrt((cation - anion) ** 2 + 4.0 * ksp_value)) / 2.0
    remaining_mol_l = moles[ion] - precipitated_mol_l
    return max(remaining_mol_l, 0.0) * ION_DATA[ion][0] * 1000.0
